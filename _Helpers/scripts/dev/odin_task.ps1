[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $WorkspaceFolder,
  [Parameter(Mandatory = $false)] [string] $ActiveFile,
  [Parameter(Mandatory = $true)]
  [ValidateSet('build-debug', 'build-release', 'build-dll', 'run-debug', 'run-release', 'check', 'build-raddebug')]
  [string] $Mode,
  [string] $OdinExe = 'odin',
  [switch] $Exec,
  # Explicit project root, set by the launch config (Family B) via
  # `${input:pvProjectDir}`. Takes priority over the (Get-Location) detection.
  [Parameter(Mandatory = $false)] [string] $Cwd
)

$ErrorActionPreference = 'Stop'

function Resolve-ProjectContext {
  param([string] $Ws, [string] $File, [string] $Mode)

  # Project resolution order (highest priority first):
  #   1. cwd under code/projects/<X>/          -> <X>   (Family B launch configs set this)
  #   2. Active file under code/projects/<X>/  -> <X>   (Family A: project detected from ${file})
  #   3. else: fail with a message that says what to do
  #
  # The cwd check goes FIRST on purpose: a Family B launch config sets `cwd`
  # explicitly to the sub-project folder, which is the user's strongest intent
  # signal. The ActiveFile hint is only used when cwd does not pin a project
  # (i.e. when invoked from the root workspace).
  $projectName = $null
  $projectRoot = $null

  $cwd = if (-not [string]::IsNullOrWhiteSpace($Cwd)) {
    # -Cwd was passed (e.g. via launch.json's ${input:pvProjectDir}). Trust it
    # over the current shell's cwd - the launch config is the authoritative
    # source of intent for Family B.
    (Resolve-Path -LiteralPath $Cwd).ProviderPath
  } else {
    (Get-Location).ProviderPath
  }
  if ($cwd.StartsWith($Ws, [System.StringComparison]::OrdinalIgnoreCase)) {
    $relCwd = $cwd.Substring($Ws.Length).TrimStart('\', '/')
    if ($relCwd -match '^code[\\/]projects[\\/]([^\\/]+)([\\/]|$)') {
      $projectName = $Matches[1]
      $projectRoot = Join-Path $Ws "code/projects/$projectName"
    }
  }

  if (-not $projectName -and -not [string]::IsNullOrWhiteSpace($File)) {
    if (-not $File.StartsWith($Ws, [System.StringComparison]::OrdinalIgnoreCase)) {
      throw "Active file '$File' is not inside workspace '$Ws'."
    }
    $rel = $File.Substring($Ws.Length).TrimStart('\', '/')
    if ($rel -match '^code[\\/]projects[\\/]([^\\/]+)([\\/]|$)') {
      $projectName = $Matches[1]
      $projectRoot = Join-Path $Ws "code/projects/$projectName"
    }
  }

  if (-not $projectName) {
    throw @"
Cannot resolve a sub-project from the current context:
  -ActiveFile: '$File'
  cwd        : '$cwd'
  workspace  : '$Ws'

The script needs either:
  - a cwd inside code/projects/<project>/ (set by Family B launch configs), or
  - an active file under code/projects/<project>/ (Family A).
"@
  }
  if (-not (Test-Path -LiteralPath $projectRoot -PathType Container)) {
    throw "Project folder not found: $projectRoot"
  }

  $hasSource = Test-Path -LiteralPath (Join-Path $projectRoot 'source') -PathType Container
  $hasSrc = Test-Path -LiteralPath (Join-Path $projectRoot 'src') -PathType Container
  if (-not ($hasSource -or $hasSrc)) {
    throw "Neither source/ nor src/ exists in $projectRoot"
  }

  $src = if ($Mode -eq 'build-dll') {
    if ($hasSource) {
      Join-Path $projectRoot 'source'
    } else {
      Join-Path $projectRoot 'src'
    }
  } else {
    if ($hasSrc) {
      Join-Path $projectRoot 'src'
    } else {
      Join-Path $projectRoot 'source'
    }
  }

  return [pscustomobject]@{
    ProjectName = $projectName
    ProjectRoot = $projectRoot
    Src         = $src
    BuildDir    = (Join-Path $projectRoot 'build')
    DebugDir    = (Join-Path $projectRoot 'build\debug')
    ReleaseDir  = (Join-Path $projectRoot 'build\release')
    DllDir      = (Join-Path $projectRoot 'build\dll')
  }
}

# If a sub-project's _tools/build_and_run.bat exists, prefer it over the
# generic `odin build` invocation. Triggered when the current working directory
# is inside code/projects/<project>/ (e.g. when the launch config hardcodes
# `cwd` to that project). Mirrors the convention used by the standalone
# project workspace.
function Resolve-SubprojectBat {
  param([string] $ProjectRoot)
  $bat = Join-Path $ProjectRoot '_tools\build_and_run.bat'
  if (Test-Path -LiteralPath $bat -PathType Leaf) { return $bat }
  return $null
}

$ctx = Resolve-ProjectContext -Ws $WorkspaceFolder -File $ActiveFile -Mode $Mode
Write-Host "[odin_task] project: $($ctx.ProjectName)"
Write-Host "[odin_task] src    : $($ctx.Src) (mode=$Mode, exec=$Exec)"

# Detect subproject mode from the current working directory: if cwd is inside
# the project, route through the project's _tools\build_and_run.bat for
# build/run modes. The .bat is the canonical pipeline used by the standalone
# workspace, so this keeps the root workspace behavior identical when the
# user opens it from anywhere.
$subprojectBat = $null
if ($Mode -in @('build-debug', 'build-release', 'run-debug', 'run-release')) {
  $subprojectBat = Resolve-SubprojectBat -ProjectRoot $ctx.ProjectRoot
  if ($subprojectBat) {
    Write-Host "[odin_task] routing via sub-project bat: $subprojectBat"
  }
}

# Ensure build/debug, build/release and build/dll exist (generic fallback path).
foreach ($d in @($ctx.DebugDir, $ctx.ReleaseDir, $ctx.DllDir)) {
  if (-not (Test-Path -LiteralPath $d)) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
  }
}

# Convention: build artifacts live under build/<mode>/<ProjectName>.<ext>.
# No more _debug / _release suffixes on the binary names - the sub-folder
# disambiguates them. Matches the KB convention (karl_zylinski hot-reload
# template: OUT_DIR=build/debug, OUT_DIR=build/release).
$exeBaseName = "$($ctx.ProjectName).exe"
$dllBaseName = "$($ctx.ProjectName).dll"
$debugExe   = Join-Path $ctx.DebugDir   $exeBaseName
$releaseExe = Join-Path $ctx.ReleaseDir $exeBaseName
$dllOut     = Join-Path $ctx.DllDir     $dllBaseName

# Helper: invoke the sub-project's build_and_run.bat with consistent flags.
function Invoke-SubprojectBuild {
  param([string] $Bat, [string] $Src, [string] $Out, [bool] $IsDebug, [bool] $DoExec)

  $args = @('build', '--src', $Src, '--out', $Out)
  if ($IsDebug) {
    $args += '--debug'
  }
  if ($DoExec) {
    $args += '--exec'
  }
  Write-Host "[odin_task] cmd /c `"$Bat`" $($args -join ' ')"
  & cmd /c "`"$Bat`"" $args
  return $LASTEXITCODE
}

switch ($Mode) {
  'build-debug' {
    if ($subprojectBat) {
      $code = Invoke-SubprojectBuild -Bat $subprojectBat -Src $ctx.Src -Out $debugExe -IsDebug $true -DoExec $Exec
      if ($code -ne 0) { exit $code }
    } else {
      & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
      if ($Exec) { & $debugExe }
    }
  }
  'build-release' {
    if ($subprojectBat) {
      $code = Invoke-SubprojectBuild -Bat $subprojectBat -Src $ctx.Src -Out $releaseExe -IsDebug $false -DoExec $Exec
      if ($code -ne 0) { exit $code }
    } else {
      & $OdinExe build $ctx.Src -out:$releaseExe -o:speed -no-bounds-check
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
      if ($Exec) { & $releaseExe }
    }
  }
  'build-dll' {
    # DLL is always generic - the sub-project .bat does not have a build-dll mode.
    & $OdinExe build $ctx.Src -build-mode:dll -out:$dllOut -debug -vet
  }
  'run-debug' {
    # Kept for back-compat with [BUILD+RUN] odin_task (debug). Equivalent to
    # build-debug + Exec, but routed through the .bat if available for parity.
    if ($subprojectBat) {
      $code = Invoke-SubprojectBuild -Bat $subprojectBat -Src $ctx.Src -Out $debugExe -IsDebug $true -DoExec $true
      if ($code -ne 0) { exit $code }
    } else {
      & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
      & $debugExe
    }
  }
  'run-release' {
    if ($subprojectBat) {
      $code = Invoke-SubprojectBuild -Bat $subprojectBat -Src $ctx.Src -Out $releaseExe -IsDebug $false -DoExec $true
      if ($code -ne 0) { exit $code }
    } else {
      & $OdinExe build $ctx.Src -out:$releaseExe -o:speed -no-bounds-check
      if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
      & $releaseExe
    }
  }
  'check' {
    # check is always generic - keeps the smoke-test fast and isolated from
    # any project-specific .bat side effects.
    & $OdinExe check $ctx.Src -vet -strict-style
  }
  'build-raddebug' {
    # Builds the debug binary AND launches RAD Debugger (raddbg.exe) on it.
    # raddbg.exe is from EpicGames/raddebugger (see KB: odin-knowledge-base/
    #   docs/karl_zylinski/hot-reload-gameplay-code.md, section "RAD Debugger").
    & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $raddbg = Get-Command raddbg.exe -ErrorAction SilentlyContinue
    if ($raddbg) {
      Write-Host "[odin_task] launching raddbg.exe on $debugExe"
      & raddbg.exe -g "$debugExe" --PID 0 | Out-Null
    } else {
      Write-Host '[odin_task] raddbg.exe not found in PATH (skip Raddebugger attach)'
      Write-Host "[odin_task] binary ready: $debugExe"
    }
  }
}
