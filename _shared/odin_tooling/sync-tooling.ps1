<#
.SYNOPSIS
  One-way sync of canonical Odin tooling files to a list of target projects.

.DESCRIPTION
  Copies the canonical tooling files from this directory (the source of truth)
  to each project listed in -Targets.

  Two kinds of files are synced:

  - **Canonical (always copied)**: files that should be IDENTICAL across all
    projects. `Copy-Item -Force` overwrites any local copy.

      Project root:
        - odinfmt.json
        - ols.json

      _tools/ (mutualised):
        - build_and_run.bat
        - check_and_format.bat
        - create_junctions.ps1

  - **Templates (copied ONLY if missing by default)**: files that have a sensible
    default but should be customised per-user/per-project. With -Force, they
    are overwritten (with a per-file warning so you don't silently nuke
    project-local customisations.

      .vscode/ (seeded only if missing, or always with -Force):
        - tasks.json             (from templates/TPL_tasks.json)

      _tools/ (seeded only if missing, or always with -Force):
        - install_full_env.ps1   (from templates/TPL_install_full_env.ps1)
        - README.md              (from templates/TPL_README.md)

  Files that are INTENTIONALLY left local (never synced, even with -Force):
    - (none - templates cover the previous "left local" list)

  Usage (interactive, default targets):
    pwsh -File .\sync-tooling.ps1

  Usage (with explicit targets):
    pwsh -File .\sync-tooling.ps1 -Targets @(
        "D:\Projets\Odin\Falconerd\PVG02_Metroidvania",
        "D:\Projets_Perso\00a_Skeletons\Odin_Skel\Odin_Skeleton"
    )

.PARAMETER Targets
  List of project root paths. Defaults to the 3 known projects.

.PARAMETER Source
  The canonical shared tooling directory. Defaults to the script's folder.

.PARAMETER WhatIf
  If set, only prints what would be done without modifying files.

.PARAMETER SkipTemplates
  If set, do not seed the template files (canonical-only sync).

.PARAMETER Force
  Overwrite existing template files at the destination (canonical files are
  always overwritten, this flag only changes template behaviour). For each
  template file that already exists locally, a warning is printed before
  overwriting so you can spot project-local customisations being clobbered.
#>
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [string[]]$Targets = @(
        "D:\Projets\Odin\Falconerd\PVG02_Metroidvania",
        "D:\Projets_Perso\00a_Skeletons\Odin_Skel\Odin_Skeleton",
        "D:\Projets_Perso\03_Code\Odin\OdinRAG\code\projects\PVG03_RPG"
    ),
    [string]$Source = $PSScriptRoot,
    [switch]$SkipTemplates,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# =============================================================================
# Canonical files (always copied, overwriting any local copy).
# rel-path inside the project -> absolute source inside _shared/
# =============================================================================
$canonical = @{
    "odinfmt.json"                       = Join-Path $Source "odinfmt.json"
    "ols.json"                           = Join-Path $Source "ols.json"
    "_tools\build_and_run.bat"           = Join-Path $Source "_tools\build_and_run.bat"
    "_tools\check_and_format.bat"        = Join-Path $Source "_tools\check_and_format.bat"
    "_tools\create_junctions.ps1"        = Join-Path $Source "_tools\create_junctions.ps1"
}

# =============================================================================
# Template files (seeded ONLY if missing locally; -Force overrides with warning).
# rel-path inside the project -> absolute source inside templates/
# Convention: files use the TPL_ prefix (e.g. TPL_project.raddbg_user) so the
# extension remains native (raddbg_user, README.md, .ps1, .json) and linters/
# editors recognise them. All templates live directly in templates/ (no nested
# subfolders - the prefix + extension is enough to identify the target type).
# =============================================================================
$templates = @{
    ".vscode\tasks.json"                 = Join-Path $Source "templates\TPL_tasks.json"
    "_tools\install_full_env.ps1"        = Join-Path $Source "templates\TPL_install_full_env.ps1"
    "_tools\README.md"                   = Join-Path $Source "templates\TPL_README.md"
}

# Sanity check: every source path must exist before we attempt anything.
Write-Host ""
Write-Host "=== Odin Tooling Sync ===" -ForegroundColor Cyan
Write-Host "Source (canonical): $Source"
if ($Force) {
    Write-Host "Mode: FORCE (templates will overwrite existing files with warning)" -ForegroundColor Yellow
} else {
    Write-Host "Mode: default (templates only seed missing files)"
}

$missing = @()
foreach ($rel in $canonical.Keys) {
    if (-not (Test-Path $canonical[$rel])) {
        $missing += $canonical[$rel]
    }
}
foreach ($rel in $templates.Keys) {
    if (-not (Test-Path $templates[$rel])) {
        $missing += $templates[$rel]
    }
}
if ($missing.Count -gt 0) {
    Write-Warning "Some source files are missing in canonical directory:"
    foreach ($m in $missing) { Write-Warning "  ! $m" }
    Write-Warning "These will be skipped."
}
Write-Host "Targets:" -ForegroundColor Cyan
foreach ($t in $Targets) { Write-Host "  - $t" }
Write-Host ""

# Statistics
$stats = @{
    copied        = 0
    seeded        = 0
    skipped       = 0
    forceOverwrite = 0
}

foreach ($target in $Targets) {
    if (-not (Test-Path $target)) {
        Write-Warning "Target does not exist: $target  (skipping)"
        continue
    }

    Write-Host "--- Syncing to: $target ---" -ForegroundColor Yellow

    # 1) Canonical files - always copy (overwrites).
    foreach ($rel in $canonical.Keys) {
        $src = $canonical[$rel]
        if (-not (Test-Path $src)) { continue }  # skip silently if source missing
        $dst = Join-Path $target $rel
        $dstDir = Split-Path $dst -Parent
        if (-not (Test-Path $dstDir)) {
            if ($PSCmdlet.ShouldProcess($dstDir, "Create directory")) {
                New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
            }
        }
        if ($PSCmdlet.ShouldProcess($dst, "Copy from $src")) {
            Copy-Item -Path $src -Destination $dst -Force
            Write-Host "    + $rel" -ForegroundColor Green
            $stats.copied++
        }
    }

    # 2) Template files - copy ONLY if destination is missing (or always with -Force).
    if (-not $SkipTemplates) {
        foreach ($rel in $templates.Keys) {
            $src = $templates[$rel]
            if (-not (Test-Path $src)) { continue }  # skip silently if source missing
            $dst = Join-Path $target $rel
            $exists = Test-Path $dst
            if ($exists -and -not $Force) {
                # Local file already exists - never overwrite.
                Write-Host "    . $rel (exists, skipped)" -ForegroundColor DarkGray
                $stats.skipped++
                continue
            }
            if ($exists -and $Force) {
                # Force mode: warn BEFORE overwriting so the user can spot
                # project-local customisations being clobbered.
                Write-Warning ("  ! FORCE: overwriting existing {0} - any project-local customisation will be LOST" -f $rel)
                $stats.forceOverwrite++
            }
            $dstDir = Split-Path $dst -Parent
            if (-not (Test-Path $dstDir)) {
                if ($PSCmdlet.ShouldProcess($dstDir, "Create directory")) {
                    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
                }
            }
            if ($PSCmdlet.ShouldProcess($dst, "Seed from $src")) {
                Copy-Item -Path $src -Destination $dst -Force
                if ($exists) {
                    Write-Host "    ! $rel (force-overwritten)" -ForegroundColor Yellow
                } else {
                    Write-Host "    * $rel (seeded)" -ForegroundColor Cyan
                    $stats.seeded++
                }
            }
        }
    }
    Write-Host ""
}

Write-Host "=== Sync complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host ("  Canonical copied   : {0}" -f $stats.copied) -ForegroundColor Green
Write-Host ("  Templates seeded   : {0}" -f $stats.seeded) -ForegroundColor Cyan
Write-Host ("  Templates skipped  : {0} (already exists locally)" -f $stats.skipped) -ForegroundColor DarkGray
if ($Force) {
    Write-Host ("  Force-overwritten  : {0}" -f $stats.forceOverwrite) -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Tip: review the diff in each project before committing." -ForegroundColor Yellow