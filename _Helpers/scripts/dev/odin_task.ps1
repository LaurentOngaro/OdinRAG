[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)] [string] $WorkspaceFolder,
  [Parameter(Mandatory = $false)] [string] $ActiveFile,
  [Parameter(Mandatory = $true)]
  [ValidateSet('build-debug', 'build-release', 'build-dll', 'run-debug', 'run-release', 'check', 'build-raddebug')]
  [string] $Mode,
  [string] $OdinExe = 'odin'
)

$ErrorActionPreference = 'Stop'

function Resolve-ProjectContext {
  param([string] $Ws, [string] $File, [string] $Mode)

  if ([string]::IsNullOrWhiteSpace($File)) {
    throw 'No active file. Open a file under code/projects/<project>/src/ or source/ first, or pass -ActiveFile explicitly.'
  }
  if (-not $File.StartsWith($Ws, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Active file '$File' is not inside workspace '$Ws'."
  }
  $rel = $File.Substring($Ws.Length).TrimStart('\', '/')
  if ($rel -notmatch '^code[\\/]projects[\\/]([^\\/]+)[\\/]') {
    throw "Active file is not under code/projects/<project>/. Path was: $File"
  }
  $projectName = $Matches[1]
  $projectRoot = Join-Path $Ws "code/projects/$projectName"
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

$ctx = Resolve-ProjectContext -Ws $WorkspaceFolder -File $ActiveFile -Mode $Mode
Write-Host "[odin_task] project: $($ctx.ProjectName)"
Write-Host "[odin_task] src    : $($ctx.Src) (mode=$Mode)"

# Ensure build/debug, build/release and build/dll exist.
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

switch ($Mode) {
  'build-debug' {
    & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
  }
  'build-release' {
    & $OdinExe build $ctx.Src -out:$releaseExe -o:speed -no-bounds-check
  }
  'build-dll' {
    & $OdinExe build $ctx.Src -build-mode:dll -out:$dllOut -debug -vet
  }
  'run-debug' {
    & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
    & $debugExe
  }
  'run-release' {
    & $OdinExe build $ctx.Src -out:$releaseExe -o:speed -no-bounds-check
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
    & $releaseExe
  }
  'check' {
    & $OdinExe check $ctx.Src -vet -strict-style
  }
  'build-raddebug' {
    # Builds the debug binary AND launches RAD Debugger (raddbg.exe) on it.
    # raddbg.exe is from EpicGames/raddebugger (see KB: odin-knowledge-base/
    #   docs/karl_zylinski/hot-reload-gameplay-code.md, section "RAD Debugger").
    & $OdinExe build $ctx.Src -out:$debugExe -debug -vet -strict-style
    if ($LASTEXITCODE -ne 0) {
      exit $LASTEXITCODE
    }
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
