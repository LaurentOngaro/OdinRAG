# TODO

Track open bugs, improvements, and active tickets.

## priorities

_Define your top priorities here, in execution order. Leave blank if undecided._

## Project Improvements

### Bugs (last: BUG01)

_None for now._

### Documentation (last: DOC01)

_None for now._

### Display (last: DISP01)

_None for now._

### Features (last: FEAT01)

_None for now._

### Publish (last: PUB01)

_None for now._

### Refactoring (last: REF02)

- [ ] REF02 - `_tools/jetbrains_configurations/` is currently NOT synced (per-project IDE files).
  - If we want to mutualise them, add a recursive copy step in `sync-tooling.ps1` and a `_tools/jetbrains_configurations/TPL_/` directory.

### Security (last: SEC01)

_None for now._

## Recurring tasks (last: REC01)

- [ ] REC01: **Quarterly check KB + Space** - run the following scripts to ensure the knowledge base and Space are up-to-date and consistent.

  ```bash
  python _Helpers/scripts/scrapers/build_gitingest.py --check
  python _Helpers/scripts/scrapers/scrape_odin_changelog.py --check
  python _Helpers/scripts/scrapers/scrape_raylib_changelog.py --check
  python _Helpers/scripts/diagnostic/audit_public_safety.py
  ```

## Roadmap / Ideas to Investigate (last: IDEA01)

Next up:

_None for now._

Backlog (value to confirm):

- [ ] **`scrape_odin_discussions.py`** - postponed .
- [ ] **`scrape_raylib_odin_bindings.py`** - unplanned.
- [ ] **(Optional)** Upload the TerraBloom synthesis if pair-coding TerraBloom-like.

## Completed

- REF01: mutualise `_tools/install_full_env.ps1` (2026-07-26)
  - 3 versions analysed across projects (Skeleton/PVG02/PVG03/PVG00_Pong); only PVG00_Pong had a complete Odin download/unpack path
  - merged with the `<#...#>` documentation block from PVG03_RPG
  - stored as `templates/_tools/TPL_install_full_env.ps1` in `_shared/odin_tooling/`
  - `sync-tooling.ps1` now seeds it (NOT overwrites) on first sync of a new project
- DOC02: tasks/launch wiring refactor (2026-07-26)
  - migrated binaries from `build/<Proj>_debug.exe` to `build/debug/<Proj>.exe` (and `build/release/`)
  - split tasks into Family A (project auto-detected from `${file}`) and Family B (project-specific via `${input:pvProjectDir}`)
  - added `-Exec` flag in `odin_task.ps1`, sub-project routing via cwd
  - archived `_tools/build_and_run_OdinRAG.bat` to `_Private/archives/` (no longer needed)
  - documented in `_Helpers/docs/008_tasks_and_launch_wiring.md` (v2.3.0 -> v2.4.0)
- DOC01: normalization (2026-07-01)
  - restructured docs into `_Helpers/docs/` (renamed to NNN_*.md) and `odin-knowledge-base/docs/` (scraped sources)
  - normalized frontmatter (title, date, tags, type, status, version, lastUpdated, updatedBy) per [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](_Helpers/docs/003_yaml_frontmatter_conventions.md)
  - moved MIXING_PUBLIC_AND_PRIVATE_HISTORY.md to `_Helpers/docs/007_mixing_public_and_private_history.md`
