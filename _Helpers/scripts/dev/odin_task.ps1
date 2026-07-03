[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $WorkspaceFolder,
    [Parameter(Mandatory = $false)] [string] $ActiveFile,
    [Parameter(Mandatory = $true)]
    [ValidateSet('build-debug', 'build-release', 'build-dll', 'run-debug', 'check')]
    [string] $Mode,
    [string] $OdinExe = 'odin'
)

$ErrorActionPreference = 'Stop'

function Resolve-ProjectContext {
    param([string] $Ws, [string] $File, [string] $Mode)

    if ([string]::IsNullOrWhiteSpace($File)) {
        throw "No active file. Open a file under code/projects/<project>/src/ or source/ first, or pass -ActiveFile explicitly."
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
    $hasSrc    = Test-Path -LiteralPath (Join-Path $projectRoot 'src') -PathType Container
    if (-not ($hasSource -or $hasSrc)) {
        throw "Neither source/ nor src/ exists in $projectRoot"
    }

    $src = if ($Mode -eq 'build-dll') {
        if ($hasSource) { Join-Path $projectRoot 'source' } else { Join-Path $projectRoot 'src' }
    } else {
        if ($hasSrc) { Join-Path $projectRoot 'src' } else { Join-Path $projectRoot 'source' }
    }

    return [pscustomobject]@{
        ProjectName = $projectName
        ProjectRoot = $projectRoot
        Src         = $src
        BuildDir    = (Join-Path $projectRoot 'build')
    }
}

$ctx = Resolve-ProjectContext -Ws $WorkspaceFolder -File $ActiveFile -Mode $Mode
Write-Host "[odin_task] project: $($ctx.ProjectName)"
Write-Host "[odin_task] src    : $($ctx.Src) (mode=$Mode)"

if (-not (Test-Path -LiteralPath $ctx.BuildDir)) {
    New-Item -ItemType Directory -Path $ctx.BuildDir -Force | Out-Null
}

$exeName = "$($ctx.ProjectName)_debug.exe"
$relName = "$($ctx.ProjectName).exe"
$dllName = "$($ctx.ProjectName).dll"
$exePath = Join-Path $ctx.BuildDir $exeName
$relPath = Join-Path $ctx.BuildDir $relName
$dllPath = Join-Path $ctx.BuildDir $dllName

switch ($Mode) {
    'build-debug'   { & $OdinExe build $ctx.Src -out:$exePath -debug -vet -strict-style }
    'build-release' { & $OdinExe build $ctx.Src -out:$relPath -o:speed -no-bounds-check }
    'build-dll'     { & $OdinExe build $ctx.Src -build-mode:dll -out:$dllPath -debug -vet }
    'run-debug' {
        & $OdinExe build $ctx.Src -out:$exePath -debug -vet -strict-style
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $exePath
    }
    'check'         { & $OdinExe check $ctx.Src -vet -strict-style }
}