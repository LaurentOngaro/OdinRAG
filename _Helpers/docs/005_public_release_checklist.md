---
title: "Public release checklist"
date: 2026-06-29
tags: [OdinRAG, reference, release, audit]
type: reference
status: active
version: 2.0.0
lastUpdated: "2026-07-02"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# 005_public_release_checklist

## Why this document exists

The repo uses a **single-repo / two-branch / two-remote workflow** (see [`_Helpers/docs/007_mixing_public_and_private_history.md`](007_mixing_public_and_private_history.md)):

- `main` (local) carries everything, including personal content
- `public` (local, filter-branch output) carries only the public subset
- the pre-push hook blocks leaks before they leave the machine
- a GitHub Action (`public_safety.yml`) re-runs the audit on every push to `main`

This checklist is the only authorized procedure to make the repo public.

## Steps

### 1. Local side - `.gitignore` + `.git/info/exclude`

The exclusion patterns are split between two files:

- `.gitignore` (tracked, present in public clones): only `/_Private/.config/` (defense in depth for credentials) and build / IDE artifacts.
- `.git/info/exclude` (local only, never pushed): the per-developer ignores (`/_Private/planning/`, `/_Private/raw/`, `/_Private/docs/`, etc.) so personal content stays untracked by default.

Verify they jointly cover:

- `code/projects/PVG03_RPG/`
- `_Private/` (whole folder, except the README captured by the strategy doc)
- `odin-knowledge-base/courses/`
- `odin-knowledge-base/docs/karl_zylinski/odin-book/`

### 2. Refresh the `public` branch from `main`

```bash
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
```

This regenerates `refs/heads/public` from the current tip of `main`, stripping the personal paths above via `git filter-branch --index-filter --prune-empty`.
The `--verify` flag also runs the audit immediately afterwards. Idempotent: if the public branch already represents a clean view of main, the script exits without changes.

Filter-branch refuses to run on a dirty working tree. If you have unstaged changes:

```bash
git stash push -u -m "wip-refresh"
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
git stash pop
```

### 3. Automatic audit

```bash
python _Helpers/scripts/diagnostic/audit_public_safety.py                # default = branch scope
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope both    # paranoid double check
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose       # list every file examined
```

Expected output: `[OK] Public safety audit (branch): clean`.

- Exit code `0` -> you can push.
- Exit code `1` -> fix the leak (re-run `refresh_public_branch.py --verify` if it's a branch issue, or update ignore patterns if it's a tree issue).
- Exit code `2` -> error (git missing, branch absent, ...).

### 4. Push

```bash
git push public public    # NEVER `git push public main` - the hook refuses it anyway
```

### 5. CI double-check

The `.github/workflows/public_safety.yml` workflow re-runs the same filter + audit on every push to `main` and every pull request. If it ever fails, treat the `public` remote as compromised: rotate the secrets in `_Private/.config/skool_credentials.txt` and `cookies.txt`, force-push a re-filtered `public` branch (after pulling the leak back), and document the incident in the daily.

### 6. Post-push verification

```bash
curl -s https://api.github.com/repos/LaurentOngaro/OdinRAG/contents/ | python -c "import json,sys; data=json.load(sys.stdin); print(f'{len(data)} top-level items')"
```

Compare the output to the expected count (~ 8-10 top-level items: `_Helpers/`, `.kilo/`, `docs/`, `code/`, `odinfmt.json`, `AGENTS.md`, `README.md`, `LICENSE`...).

Browse the `Code` tab on GitHub manually to confirm the absence of:

- `code/projects/PVG03_RPG/`
- `_Private/`
- `odin-knowledge-base/courses/`
- `odin-knowledge-base/docs/karl_zylinski/*.md` (other than README)

## NEVER

- Push `main` to the `public` remote (the hook refuses it; bypassing the hook means leaking history).
- Push without having run `audit_public_safety.py --scope branch` first.
- Share a `git bundle` of the local repo without having done the purge - it contains the entire history including personal content.
- Include long excerpts (> 200 words) of Skool lessons in public posts: fair use does not cover full republication.

## When to re-run this checklist

- Before any private -> public transition.
- Before sharing the repo with a third party (colleague, mentor).
- Before mirroring on another platform (GitLab, Codeberg, etc.).
- After adding a new scraping source: update `SOURCES.md`, AND update `.gitignore` (and the per-developer `.git/info/exclude` if relevant), AND `_Helpers/scripts/diagnostic/audit_public_safety.py` (`FORBIDDEN_PATTERNS`), AND `_Helpers/scripts/diagnostic/refresh_public_branch.py` (`STRIP_RULES`).
- After adding a new personal project folder: update `.git/info/exclude` and the two scripts above.
