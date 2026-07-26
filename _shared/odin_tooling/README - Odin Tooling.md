# Odin Tooling - Canonical Source

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

`_shared/odin_tooling/` is the **canonical mirror** for **all** tooling that should be identical across projects (JSON configs, build scripts, raddbg init file).
The Odin Skeleton is now a consumer, not a source. Editing a file here and running `sync-tooling.ps1` propagates it everywhere.

## Files in this directory

| File                                       | Role                                                  | Sync target          |
| ------------------------------------------ | ----------------------------------------------------- | -------------------- |
| `odinfmt.json`                             | Formatter config (odinfmt)                            | project root         |
| `ols.json`                                 | LSP config (ols) + lint rules                         | project root         |
| `tasks.json.template`                      | VS Code tasks (use `${workspaceFolder}`)              | `.vscode/tasks.json` |
| `_tools/build_and_run.bat`                 | build + run + raddebugger wrapper                     | `_tools/`            |
| `_tools/check_and_format.bat`              | CI pipeline: `odinfmt -w` + `odin check`              | `_tools/`            |
| `_tools/create_junctions.ps1`              | Creates `_refs/` junctions to Odin SDK                | `_tools/`            |
| `_tools/project.raddbg_project`            | RadDebugger initial project config                    | `_tools/`            |
| `templates/_tools/install_full_env.ps1.template`  | Odin + BuildTools env installer (merged PVG00)   | `_tools/` (seed)     |
| `templates/_tools/project.raddbg_user.template`    | raddbg user config (default)                     | `_tools/` (seed)     |
| `templates/_tools/README.md.template`             | tools folder README                              | `_tools/` (seed)     |
| `sync-tooling.ps1`                         | One-way sync to all known projects                    | (this dir)           |
| `README - Odin Tooling.md`                  | This documentation                                    | n/a                  |

## Sync semantics

`sync-tooling.ps1` distinguishes two kinds of files:

- **Canonical** (`Copy-Item -Force`, always overwritten): files that must stay identical across all projects. Edited in `_shared/odin_tooling/` and propagated on the next sync.
- **Templates** (seeded ONLY if missing): files that have a sensible default but should be customised per project or per user. The first sync seeds them; subsequent syncs leave them alone to preserve local customisations.

## Files seeded as templates (NOT overwritten)

These come from `templates/_tools/*.template`. They are copied only if the destination does not exist locally:

| Destination                          | Why seeded-only (not canonical)                           |
| ------------------------------------ | --------------------------------------------------------- |
| `_tools/install_full_env.ps1`         | Script to bootstrap Odin + BuildTools on a new dev machine |
| `_tools/project.raddbg_user`          | Per-user RadDebugger config (custom breakpoints, layout)  |
| `_tools/README.md`                    | Short project-specific tools-folder documentation         |

## Portability

All paths in the synced files use either:

- **`${workspaceFolder}`** (in `tasks.json.template`) - resolves to the VS Code workspace root.
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
- Seed template files (install_full_env.ps1, project.raddbg_user, README.md) since the destination does not exist.

For existing projects, only the canonical files are overwritten; templates are skipped (local customisations preserved).

## Deferred work

- `_tools/jetbrains_configurations/` is currently NOT synced (per-project IDE files). If we want to mutualise them, add a recursive copy step in `sync-tooling.ps1` and a `_tools/jetbrains_configurations/.template/` directory.
