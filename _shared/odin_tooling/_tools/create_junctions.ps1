<#
.SYNOPSIS
    Creates junctions from "E:\Apps\_odin\examples", "E:\Apps\_odin\core" and "E:\Apps\_odin\vendor" to "examples", "core" and "vendor" inside the "_refs" folder.

.DESCRIPTION
    This script creates junction points from the specified source directories to the target directories.

.PARAMETER examplesSource
    The source directory for the examples junction. Default is "E:\Apps\_odin\examples".

.PARAMETER examplesTarget
    The target directory where the examples junction will be created. Default is "_refs\examples".

.PARAMETER coreSource
    The source directory for the core junction. Default is "E:\Apps\_odin\core".

.PARAMETER coreTarget
    The target directory where the core junction will be created. Default is "_refs\core".

.PARAMETER vendorSource
    The source directory for the vendor junction. Default is "E:\Apps\_odin\vendor".

.PARAMETER vendorTarget
    The target directory where the vendor junction will be created. Default is "_refs\vendor".

.EXAMPLE
    .\create_junctions.ps1 -coreSource "E:\Apps\_odin\core" -coreTarget "../_refs\core" -vendorSource "E:\Apps\_odin\vendor" -vendorTarget "../_refs\vendor"
#>


param (
  [string]$examplesSource = "$env:FLD_APPS\_odin\examples",
  [string]$examplesTarget = '',
  [string]$coreSource = "$env:FLD_APPS\_odin\core",
  [string]$coreTarget = '',
  [string]$vendorSource = "$env:FLD_APPS\_odin\vendor",
  [string]$vendorTarget = ''
)

$refFolder = '..\_refs'

if ($examplesTarget -eq '') {
  $examplesTarget = "$refFolder\examples"
}
if ($coreTarget -eq '') {
  $coreTarget = "$refFolder\core"
}
if ($vendorTarget -eq '') {
  $vendorTarget = "$refFolder\vendor"
}

# Ensure the $refFolder directories exist
if (!(Test-Path $refFolder)) {
  Write-Host "This script must be run inside the ""_tools"" and the ""$refFolder"" folder must exists" -ForegroundColor Red
  Exit 1
}

# Ensure the target directories exist
$examplesTargetDir = Split-Path -Path $examplesTarget -Parent
if (!(Test-Path $examplesTargetDir)) {
  New-Item -Path $examplesTargetDir -ItemType Directory -Force
}
$coreTargetDir = Split-Path -Path $coreTarget -Parent
if (!(Test-Path $coreTargetDir)) {
  New-Item -Path $coreTargetDir -ItemType Directory -Force
}
$vendorTargetDir = Split-Path -Path $vendorTarget -Parent
if (!(Test-Path $vendorTargetDir)) {
  New-Item -Path $vendorTargetDir -ItemType Directory -Force
}

# Validate a junction: returns $true only if the path is a reparse point
# pointing to the expected target. Broken junctions or plain directories
# are reported as invalid so they get recreated.
function Test-JunctionValid {
  param([string]$Path, [string]$Target)
  if (-not (Test-Path -LiteralPath $Path)) { return $false }
  $item = Get-Item -LiteralPath $Path -Force
  $isReparse = bool ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
  if (-not $isReparse) { return $false }
  return ($item.Target -eq $Target)
}

function New-Or-Repair-Junction {
  param([string]$Link, [string]$Target)
  if (Test-JunctionValid -Path $Link -Target $Target) {
    Write-Host "Junction already valid at $Link -> $Target" -ForegroundColor Yellow
    return
  }
  if (Test-Path -LiteralPath $Link) {
    Write-Host "Removing stale entry at $Link" -ForegroundColor DarkYellow
    Remove-Item -LiteralPath $Link -Force
  }
  New-Item -Path $Link -ItemType Junction -Value $Target | Out-Null
  Write-Host "Junction created from $Target to $Link" -ForegroundColor Green
}

# Create the junctions
New-Or-Repair-Junction -Link $examplesTarget -Target $examplesSource
New-Or-Repair-Junction -Link $coreTarget     -Target $coreSource
New-Or-Repair-Junction -Link $vendorTarget   -Target $vendorSource