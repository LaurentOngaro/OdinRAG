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
        - .vscode/tasks.json (from tasks.json.template)

      _tools/ (mutualised):
        - build_and_run.bat
        - check_and_format.bat
        - create_junctions.ps1
        - project.raddbg_project  (skip if .raddbg_user exists and is customised)

  - **Templates (copied ONLY if missing)**: files that have a sensible default
    but should be customised per-user/per-project. `sync-tooling.ps1` only
    seeds them - it never overwrites an existing local copy.

      _tools/ (seeded only if missing):
        - install_full_env.ps1   (from templates/_tools/install_full_env.ps1.template)
        - project.raddbg_user    (from templates/_tools/project.raddbg_user.template)
        - README.md              (from templates/_tools/README.md.template)

  Files that are INTENTIONALLY left local (never synced):
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
#>
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [string[]]$Targets = @(
        "D:\Projets\Odin\Falconerd\PVG02_Metroidvania",
        "D:\Projets_Perso\00a_Skeletons\Odin_Skel\Odin_Skeleton",
        "D:\Projets_Perso\03_Code\Odin\OdinRAG\code\projects\PVG03_RPG"
    ),
    [string]$Source = $PSScriptRoot,
    [switch]$SkipTemplates
)

$ErrorActionPreference = "Stop"

# =============================================================================
# Canonical files (always copied, overwriting any local copy).
# rel-path inside the project -> absolute source inside _shared/
# =============================================================================
$canonical = @{
    "odinfmt.json"                       = Join-Path $Source "odinfmt.json"
    "ols.json"                           = Join-Path $Source "ols.json"
    ".vscode\tasks.json"                 = Join-Path $Source "tasks.json.template"
    "_tools\build_and_run.bat"           = Join-Path $Source "_tools\build_and_run.bat"
    "_tools\check_and_format.bat"        = Join-Path $Source "_tools\check_and_format.bat"
    "_tools\create_junctions.ps1"        = Join-Path $Source "_tools\create_junctions.ps1"
    "_tools\project.raddbg_project"      = Join-Path $Source "_tools\project.raddbg_project"
}

# =============================================================================
# Template files (seeded ONLY if missing locally).
# rel-path inside the project -> absolute source inside templates/
# These are customised per user/project (e.g. project.raddbg_user), so we
# never overwrite - the first sync seeds them, subsequent syncs leave them alone.
# =============================================================================
$templates = @{
    "_tools\install_full_env.ps1"  = Join-Path $Source "templates\_tools\install_full_env.ps1.template"
    "_tools\project.raddbg_user"    = Join-Path $Source "templates\_tools\project.raddbg_user.template"
    "_tools\README.md"             = Join-Path $Source "templates\_tools\README.md.template"
}

# Sanity check: every source path must exist before we attempt anything.
Write-Host ""
Write-Host "=== Odin Tooling Sync ===" -ForegroundColor Cyan
Write-Host "Source (canonical): $Source"

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
    copied  = 0
    seeded  = 0
    skipped = 0
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

    # 2) Template files - copy ONLY if destination is missing.
    if (-not $SkipTemplates) {
        foreach ($rel in $templates.Keys) {
            $src = $templates[$rel]
            if (-not (Test-Path $src)) { continue }  # skip silently if source missing
            $dst = Join-Path $target $rel
            if (Test-Path $dst) {
                # Local file already exists - never overwrite.
                Write-Host "    . $rel (exists, skipped)" -ForegroundColor DarkGray
                $stats.skipped++
                continue
            }
            $dstDir = Split-Path $dst -Parent
            if (-not (Test-Path $dstDir)) {
                if ($PSCmdlet.ShouldProcess($dstDir, "Create directory")) {
                    New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
                }
            }
            if ($PSCmdlet.ShouldProcess($dst, "Seed from $src")) {
                Copy-Item -Path $src -Destination $dst -Force
                Write-Host "    * $rel (seeded)" -ForegroundColor Cyan
                $stats.seeded++
            }
        }
    }
    Write-Host ""
}

Write-Host "=== Sync complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host ("  Canonical copied : {0}" -f $stats.copied) -ForegroundColor Green
Write-Host ("  Templates seeded : {0}" -f $stats.seeded) -ForegroundColor Cyan
Write-Host ("  Templates skipped: {0} (already exists locally)" -f $stats.skipped) -ForegroundColor DarkGray
Write-Host ""
Write-Host "Tip: review the diff in each project before committing." -ForegroundColor Yellow