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

### Refactoring (last: REFA01)

_None for now._

### Security (last: SEC01)

_None for now._

## Recurring tasks (last: REC01)

- [ ] REC01: **Quarterly check KB + Space** - run the following scripts to ensure the knowledge base and Space are up-to-date and consistent.

  ```bash
  python _Helpers/scripts/scrapers/build_gitingest.py --check
  python _Helpers/scripts/scrappers/scrape_odin_changelog.py --check
  python _Helpers/scripts/scrappers/scrape_raylib_changelog.py --check
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

- [x] DOC01: normalization (2026-07-01)
  - restructured docs into `_Helpers/docs/` (renamed to NNN_*.md) and `odin-knowledge-base/docs/` (scraped sources)
  - normalized frontmatter (title, date, tags, type, status, version, lastUpdated, updatedBy) per [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](_Helpers/docs/003_yaml_frontmatter_conventions.md)
  - moved MIXING_PUBLIC_AND_PRIVATE_HISTORY.md to `_Helpers/docs/007_mixing_public_and_private_history.md`
