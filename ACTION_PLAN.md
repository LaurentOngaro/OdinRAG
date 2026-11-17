# ACTION_PLAN - Remaining Steps (OdinRAG)

> This file lists only the **remaining** multi-step work, the kind that does not fit in a single line.
> Short tasks live in [`TODO.md`](TODO.md). Rule of thumb: if a task cannot be written in one line in `TODO.md`, it belongs here.
>
> The AI session is not shared between machines nor between repositories. Anything that is not written in `TODO.md` or in this file is lost.

---

## 0. Repository audit 005 (2026-11-17)

The full findings and the prioritized plan live in the private audit `_Private/docs/audits/005_audit_odinrag_repository.md`. Implementation status:

- [x] **Anti-leak guards & `_Archives/` isolation**: centralized private rules in `_Helpers/config/private_paths.jsonc`, added `_Archives/` and nested `_Private/`/`_Archives/` matching in `publish_public.py`, `audit_public_safety.py`, and `pre-push`, and added automated tests under `_Helpers/tests/` (audit 005: C1, L1, L2).
- [x] **Hook path & clone hygiene**: configured `core.hooksPath _Helpers/scripts/dev/hooks`, set executable bit on `pre-push`, pruned stale `pine-painter` worktree, cleaned `.git/info/exclude`, removed empty `metroidvania-10-testing-ignore`, and added course exclusion in `scrape_skool.py` (H2, H3, L5, M6).
- [x] **KB index, reflow, frontmatter, and docs**: fixed `build_kb_index.py --check` exit code and idempotence, added `add_kb_frontmatter.py` + native frontmatter on scrape, excluded `_Archives` in `reflow_md.py`, wrote `ADR-003` and aligned `AGENTS.md` / `001_folder_structure.md` / `007` (M1-M5, L3, L4, L6).
- [ ] **Commit and publish (requires explicit user validation)**: commit local changes on `main`, push `main` to `private`, then run `python _Helpers/scripts/diagnostic/publish_public.py` (H1).

---

## 1. Cross-OS and cross-repo operations (Windows 11 <-> Fedora Linux)

### 1.1 Prepare a new clone or a switch to the Fedora machine

The workspace relies on local machine settings: Git line-ending policy, hooks path, and workspace links.

- [ ] **Configure the clone** (once per clone, local settings, never versioned):

  ```bash
  git config core.autocrlf false
  git config core.hooksPath _Helpers/scripts/dev/hooks
  ```

- [ ] **Normalize the line endings** (one-off, the index is already in LF, the working tree may not be):

  ```bash
  python _Helpers/scripts/dev/normalize_eol.py --apply
  ```

- [ ] **Generate the links for the current OS** (NTFS junction on Windows, symbolic link on Linux):

  ```bash
  python _Helpers/scripts/dev/sync_links.py --apply
  ```

- [ ] **Verify** that the project folders resolve and that the repositories are consistent:

  ```bash
  python _Helpers/scripts/dev/sync_links.py --check
  python _Helpers/scripts/dev/normalize_eol.py --check
  git status   # must be clean
  ```

  - Expected result on Fedora: `code/projects/PVG03_RPG/AGENTS.md` is readable, `git ls-files --eol` reports `i/lf w/lf` everywhere except the Windows scripts (`.bat`, `.cmd`, `.ps1`).

### 1.2 Publish the pending commits

- [ ] **Push the private branch** (`main` carries the full content, the `public` branch is a filtered rewrite):

  ```bash
  git push private main
  python _Helpers/scripts/diagnostic/publish_public.py
  ```

- [ ] **Audit before publishing** (must exit 0):

  ```bash
  python _Helpers/scripts/diagnostic/audit_public_safety.py
  ```

### 1.3 Same operations for the sibling repository

- [ ] Apply steps 1.1 and 1.2 to the sibling `GodotRAG` repository (same tools, same manifest format). The detailed checklist lives in `GodotRAG`'s `ACTION_PLAN.md`.

---

## 2. Knowledge base and tooling

### 2.1 Keep the line endings clean after the scrapers

- [ ] Run `python _Helpers/scripts/dev/normalize_eol.py --check` after every scrape batch: some scrapers write CRLF, and the working tree must stay LF. This is also listed as a recurring task in `TODO.md` (REC02).

### 2.2 Scrape the remaining sources

- [ ] `scrape_odin_discussions.py` (postponed, see `TODO.md`).
- [ ] `scrape_raylib_odin_bindings.py` (unplanned, see `TODO.md`).

---

## 3. Repository hygiene

- [ ] **Audit the README coherence** after adding or renaming files (the audit script does not run in CI yet):

  ```bash
  python _Helpers/scripts/diagnostic/auditReadmeCoherence.py
  ```

- [ ] **Decide the fate of the `REF02` item** (jetbrains configurations, see `TODO.md`): either mutualize `_tools/jetbrains_configurations/` in `sync-tooling.ps1` or close the ticket.
