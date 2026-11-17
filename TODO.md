# TODO

Track open bugs, improvements, and active tickets.

## priorities

_Define your top priorities here, in execution order. Leave blank if undecided._

## Project Improvements

### Bugs (next: BUG01)

_None for now._

### Documentation (next: DOC03)

_None for now._

### Display (next: DISP01)

_None for now._

### Features (next: FEAT01)

_None for now._

### Publish (next: PUB01)

_None for now._

### Refactoring (next: REF03)

#### REF02 - jetbrains configurations

`_tools/jetbrains_configurations/` is currently NOT synced (per-project IDE files).

- If we want to mutualise them, add a recursive copy step in `sync-tooling.ps1` and a `_tools/jetbrains_configurations/TPL_/` directory.

### Security (next: SEC01)

_None for now._

## Recurring tasks (next: REC03)

### REC01 : Quarterly check KB + Space

run the following scripts to ensure the knowledge base and Space are up-to-date and consistent.

```bash
python _Helpers/scripts/scrapers/build_gitingest.py --check
python _Helpers/scripts/scrapers/scrape_odin_changelog.py --check
python _Helpers/scripts/scrapers/scrape_raylib_changelog.py --check
python _Helpers/scripts/dev/sync_links.py --check
python _Helpers/scripts/diagnostic/audit_public_safety.py
```

### REC02 : After each scrape or external rewrite

Some scrapers and external tools write CRLF. The working tree must stay LF on both OS, and the workspace links must match the current OS.

```bash
python _Helpers/scripts/fixes/add_kb_frontmatter.py --check
python _Helpers/scripts/fixes/format_kb_md.py --check
python _Helpers/scripts/dev/normalize_eol.py --check
python _Helpers/scripts/dev/sync_links.py --check
```

### REC03 : On every new clone (Windows 11 or Fedora Linux)

Local setup, run once per clone. Details in [`ACTION_PLAN.md`](ACTION_PLAN.md).

```bash
git config core.autocrlf false
git config core.hooksPath _Helpers/scripts/dev/hooks
python _Helpers/scripts/dev/normalize_eol.py --apply
python _Helpers/scripts/dev/sync_links.py --apply
```

## Cross-repo (OdinRAG <-> GodotRAG)

- [ ] Push the pending commits of both repositories (OdinRAG: 3 commits, GodotRAG: 2 commits) to their remotes.
- [ ] Decide what to do with the TerraBloom design docs, now that the project is a link and its content is not duplicated in the repositories (tracked in GodotRAG's `ACTION_PLAN.md`).
- [ ] Apply the same cross-OS setup (REC03) to the GodotRAG clone on the Fedora machine.

## Roadmap / Ideas to Investigate (next: IDEA01)

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
