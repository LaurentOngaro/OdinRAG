---
title: "README - diagnostic"
date: "2026-07-02"
tags: [OdinRAG, reference, scripts, diagnostic]
type: reference
status: active
version: 1.1.0
lastUpdated: "2026-07-02"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# README - diagnostic

## Purpose

Diagnostic and audit scripts. These are the manual pre-push checks that mirror what the GitHub Action runs automatically (see `.github/workflows/`).

## Scripts

| Script                     | Purpose                                                                                                                          | Exit codes                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `audit_public_safety.py`   | Verify forbidden paths are absent from the working tree AND/OR the local `public` branch. Called by the pre-push hook and by CI. | 0 = clean, 1 = violations, 2 = error             |
| `auditReadmeCoherence.py`  | Verify per-folder READMEs reflect their host directory (wikilinks resolve, no missing files).                                    | 0 = clean, 1 = issues found                      |
| `refresh_public_branch.py` | Regenerate the local `public` branch from `main` using `git filter-branch --index-filter`. Idempotent.                           | 0 = OK / no-change, 1 = error, 2 = verify failed |

## `audit_public_safety.py`

The script enforces the public/private split. After the 2026-07-02 refactor,it has TWO scopes:

- `--scope tree` (default `tree` only): the working tree's committed state. Will fail on `main` because the workflow intentionally tracks personal content on main. Useful for diagnosing ignore-config hygiene, NOT for the publish flow.
- `--scope branch` (default): the local `refs/heads/public` branch's tree. This is the tree that will be pushed to GitHub. Should always be clean before push.
- `--scope both`: paranoid double check (combines the two above).

Example before publishing:

```bash
python _Helpers/scripts/diagnostic/audit_public_safety.py           # default = branch scope
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose # list every file examined
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope both --verbose
```

## `refresh_public_branch.py`

Wrapper around `git filter-branch --index-filter --prune-empty` that strips personal paths from the `public` branch.
Required because `git subtree split --prefix=.` does not work at the repo root (see doc 007 for why).

```bash
python refresh_public_branch.py             # refresh if needed (idempotent)
python refresh_public_branch.py --check     # show what would happen, no changes
python refresh_public_branch.py --verify    # refresh + audit afterwards
python refresh_public_branch.py --force     # bypass idempotence check
```

Filter-branch refuses to run against a dirty working tree. If you have unstaged changes, the script will tell you to `git stash push` first and `git stash pop` after.

## `auditReadmeCoherence.py`

`auditReadmeCoherence.py [--scope <path>] [--quiet] [--fail-on-error]`

Walks the repo, reads each `README*.md`, and validates that:

- The referenced folder structure is real (no `[[wikilinks]]` to non-existent files)
- Wikilinks resolve to existing files (no 404s in rendered KB)
- Aspirational READMEs (describing future content) are explicitly marked as such

## For the public release checklist

See [`_Helpers/docs/005_public_release_checklist.md`](../../docs/005_public_release_checklist.md) for the full pre-push procedure that uses these scripts.
