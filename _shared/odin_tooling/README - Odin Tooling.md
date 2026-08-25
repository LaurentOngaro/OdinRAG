# README - Odin Tooling

This directory is the **single source of truth** for Odin project tooling used across all projects in the OdinRAG workspace and its sibling Odin projects.

## Hierarchy

```
        _shared/odin_tooling/             <-- canonical mirror (this dir)
                       |
        +--------------+--------------+
        |              |              |
        v              v              v
    PVG02_RPG    PVG03_RPG      (future projects)
        ^              ^
        |              |
    Odin_Skeleton   (still consumes from _shared/,
                     no longer acts as a source)
```

`_shared/odin_tooling/` is the **canonical mirror** for **all** tooling that should be identical across projects (JSON configs, build scripts). The Odin Skeleton is now a consumer, not a source. Editing a file here and running `sync-tooling.ps1` propagates it everywhere.

## Files in this directory

| File                                 | Role                                           | Sync target                 |
| ------------------------------------ | ---------------------------------------------- | --------------------------- |
| `CODING_STYLE.md`                    | Coding conventions & style guide               | (reference)                 |
| `odinfmt.json`                       | Formatter config (odinfmt)                     | project root                |
| `ols.json`                           | LSP config (ols) + lint rules                  | project root                |
| `_tools/build_and_run.bat`           | build + run + raddebugger wrapper              | `_tools/`                   |
| `_tools/check_and_format.bat`        | CI pipeline: `odinfmt -w` + `odin check`       | `_tools/`                   |
| `_tools/create_junctions.ps1`        | Creates `_refs/` junctions to Odin SDK         | `_tools/`                   |
| `templates/`                         | Project template files                         | (see templates below)       |
| `templates/TPL_tasks.json`           | VS Code tasks (use `${workspaceFolder}`)       | `.vscode/tasks.json` (seed) |
| `templates/TPL_install_full_env.ps1` | Odin + BuildTools env installer (merged PVG00) | `_tools/` (seed)            |
| `templates/TPL_README.md`            | tools folder README                            | `_tools/` (seed)            |
| `sync-tooling.ps1`                   | One-way sync to all known projects             | (this dir)                  |
| `README - Odin Tooling.md`           | This documentation                             | n/a                         |

### Template naming convention

Template files use the `TPL_` prefix instead of a `.template` extension. This keeps the original extension visible so editors and linters recognise the file type (e.g. `TPL_tasks.json` is still parsed as JSON, `TPL_README.md` as Markdown, `TPL_install_full_env.ps1` as PowerShell).

## Sync semantics

`sync-tooling.ps1` distinguishes two kinds of files:

- **Canonical** (`Copy-Item -Force`, always overwritten): files that must stay identical across all projects. Edited in `_shared/odin_tooling/` and propagated on the next sync.
- **Templates** (seeded ONLY if missing): files that have a sensible default but should be customised per project or per user. The first sync seeds them; subsequent syncs leave them alone to preserve local customisations.

## Files seeded as templates (NOT overwritten by default)

These come from `templates/TPL_*`. They are copied only if the destination does not exist locally. Use `-Force` to overwrite (with a per-file warning) - local customisations may be clobbered.

| Source                               | Destination                   | Why seeded-only (not canonical)                            |
| ------------------------------------ | ----------------------------- | ---------------------------------------------------------- |
| `templates/TPL_tasks.json`           | `.vscode/tasks.json`          | VS Code tasks (per-project customisations possible)        |
| `templates/TPL_install_full_env.ps1` | `_tools/install_full_env.ps1` | Script to bootstrap Odin + BuildTools on a new dev machine |
| `templates/TPL_README.md`            | `_tools/README.md`            | Short project-specific tools-folder documentation          |

### Force mode

`sync-tooling.ps1 -Force` overwrites template files at the destination (canonical files are always overwritten, regardless of `-Force`). For each template file that already exists locally, a warning is printed **before** overwriting so you can spot project-local customisations being clobbered. Example output:

```
! FORCE: overwriting existing _tools\install_full_env.ps1 - any project-local customisation will be LOST
```

Use with care.

## Portability

All paths in the synced files use either:

- **`${workspaceFolder}`** (in `TPL_tasks.json`) - resolves to the VS Code workspace root.
- **Relative paths** (`_refs\core`, `_refs\vendor`) - in `ols.json`. Resolves relative to the `ols.json` location, which must be at the project root.
- **`%~dp0..\source`** (in `check_and_format.bat`) - relative to the script. Pass an explicit path as first arg to override.
- **`$env:FLD_APPS`** (in `create_junctions.ps1`) - user-defined env var pointing to `<parent of _odin install dir>`.

No absolute Windows paths are baked into the synced files.

## How to propagate a change

1. Edit the file in `_shared/odin_tooling/`.
2. Run the sync script:

   ```powershell
   # Dry-run first
   pwsh -File D:\Projets_Perso\03_Code\Odin\OdinRAG\_shared\odin_tooling\sync-tooling.ps1 -WhatIf
   # Apply
   pwsh -File D:\Projets_Perso\03_Code\Odin\OdinRAG\_shared\odin_tooling\sync-tooling.ps1
   ```

3. Review the diff in each project (via `git diff` or VS Code source control).
4. Commit the changes in each project.

## Onboarding a new Odin project

1. Add the new project path to `-Targets` in `sync-tooling.ps1`.
2. Run `sync-tooling.ps1 -WhatIf` to verify which files would be copied / seeded.
3. Run `sync-tooling.ps1` to apply.
4. Review the diff in each project (via `git diff` or VS Code source control).
5. Commit the changes in each project.

For brand-new projects (no `_tools/` yet), the first sync will:

- Seed canonical files (odinfmt.json, ols.json, tasks.json, the 4 mutualised `_tools/` files).
- Seed template files (install_full_env.ps1, README.md) since the destination does not exist.

For existing projects, only the canonical files are overwritten; templates are skipped (local customisations preserved).

## Deferred work

- `_tools/jetbrains_configurations/` is currently NOT synced (per-project IDE files). If we want to mutualise them, add a recursive copy step in `sync-tooling.ps1` and a `_tools/jetbrains_configurations/TPL_/` directory.

## Supported Odin flags (verified list)

The flags used in `build_and_run.bat`, `check_and_format.bat`, `ols.json` and `tasks.json` are restricted to the **real, supported** flags exposed by `odin check -help` (verified against `dev-2026-06:48a95d798` and the upstream `odin-lang/Odin` repo).

| Flag                    | Purpose                                                    |
| ----------------------- | ---------------------------------------------------------- |
| `-vet-unused`           | Checks for unused declarations (variables and imports)     |
| `-vet-unused-variables` | Checks for unused variable declarations                    |
| `-vet-unused-imports`   | Checks for unused import declarations                      |
| `-vet-shadowing`        | Checks for variable shadowing within procedures            |
| `-vet-style`            | Errs on missing trailing commas followed by a newline      |
| `-vet-semicolon`        | Errs on unneeded semicolons                                |
| `-vet-cast`             | Errs on casting a value to its own type or bad `transmute` |
| `-strict-style`         | Alias: enables a stricter subset of `-vet-*` checks        |

### Flags that do NOT exist (do not add)

The following flags have been proposed in community discussions but **do not exist** in Odin as of `dev-2026-06` and are NOT used in the canonical tooling:

- `-missing-blank-lines-between-procs` - does not exist. Style guide for blank lines is enforced by convention, not by tooling.

If a future Odin version adds such a flag, update `_shared/odin_tooling/` first and re-run `sync-tooling.ps1`.

### Style guide: blank lines between procedures

See [`CODING_STYLE.md`](CODING_STYLE.md) §6 for the canonical convention. (This file is read by both humans and AI agents.)
