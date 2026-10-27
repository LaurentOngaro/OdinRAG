# ACTION_PLAN - Remaining Steps (OdinRAG)

> This file lists only the **remaining** multi-step work, the kind that does not fit in a single line.
> Short tasks live in [`TODO.md`](TODO.md). Rule of thumb: if a task cannot be written in one line in `TODO.md`, it belongs here.
>
> The AI session is not shared between machines nor between repositories. Anything that is not written in `TODO.md` or in this file is lost.

---

## 1. Cross-OS and cross-repo operations (Windows 11 <-> Fedora Linux)

### 1.1 Prepare a new clone or a switch to the Fedora machine

The workspace relies on two mechanisms that are local to each machine: the Git line-ending policy and the workspace links.

- [ ] **Configure the clone** (once per clone, local settings, never versioned):

  ```bash
  git config core.autocrlf false
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

- [ ] Apply steps 1.1 and 1.2 to `D:/Projets_Perso/03_Code/Godot/GodotRAG` (same tools, same manifest format). The detailed checklist lives in that repository's `ACTION_PLAN.md`.

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
