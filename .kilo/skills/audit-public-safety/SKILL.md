---
name: audit-public-safety
description: "Run the public-safety audit before pushing to github.com/LaurentOngaro/OdinRAG. Verifies the public branch contains no leaked personal content (private planning, paywalled scraped KB, secrets). Use when the user says 'push', 'publish', 'release', 'audit', 'public safety', 'leak check', or any pre-push workflow."
---

# Public safety audit

Pre-push audit for the `public` branch of OdinRAG. The repo uses a **single-repo / two-branch / two-remote workflow** (see [`_Helpers/docs/007_mixing_public_and_private_history.md`](../../_Helpers/docs/007_mixing_public_and_private_history.md)): `main` carries everything, `public` carries only the public subset, and the pre-push hook blocks leaks before they leave the machine. The GitHub Action `.github/workflows/public_safety.yml` re-runs the audit on every push to `main` and every PR.

> **This skill is NOT optional.** Push without running the audit = potential leak of copyrighted scraped content, secrets, or personal planning into the public repo. See [`_Helpers/docs/005_public_release_checklist.md`](../../_Helpers/docs/005_public_release_checklist.md) for the full procedure.

## When to invoke

- **Before any push** to the `public` remote (`git push public public`).
- Before sharing a `git bundle` of the local repo.
- Before mirroring on another platform (GitLab, Codeberg, etc.).
- After adding a **new scraping source** (update `SOURCES.md`, `.gitignore`, `.git/info/exclude`, `audit_public_safety.py` `FORBIDDEN_PATTERNS`, and `refresh_public_branch.py` `STRIP_RULES`).
- After adding a **new personal project folder** under `code/projects/` (update `.git/info/exclude` and the two scripts above).

## The 3 MUST-PASS conditions

1. `python _Helpers/scripts/diagnostic/audit_public_safety.py` → **must exit 0**.
2. `.gitignore` `COPYRIGHTED SCRAPED CONTENT` section is intact.
3. No `_Private/planning/daily/`, `_Private/raw/`, or `_Private/docs/` files are staged.

## Quick audit

```bash
# Default: audit the local refs/heads/public branch (the tree that will be pushed)
python _Helpers/scripts/diagnostic/audit_public_safety.py

# Paranoid double check (working tree + branch)
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope both

# See every file examined + every violation
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose
```

Expected output: `[OK] Public safety audit (branch): clean`.

| Exit | Meaning       | Action                                              |
| ---- | ------------- | --------------------------------------------------- |
| 0    | Clean         | Safe to push                                        |
| 1    | Leak detected | Fix the leak (see "Common leaks" below)             |
| 2    | Tool error    | git missing, branch absent, etc. - read the message |

## Refresh the public branch first

The audit checks `refs/heads/public`, which is a filtered view of `main`. If you added new personal content since the last refresh, regenerate the branch first:

```bash
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
# --verify also re-runs the audit immediately after
```

`filter-branch` refuses a dirty working tree. If needed:

```bash
git stash push -u -m "wip-refresh"
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
git stash pop
```

## Common leaks and fixes

| Leak                                                | Cause                                | Fix                                                                |
| --------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------ |
| `_Private/planning/daily/J_2026-XX-XX.md`           | Not in `.git/info/exclude`           | Add to `.git/info/exclude` + re-run `refresh_public_branch.py`     |
| `odin-knowledge-base/courses/programvideogames/...` | Paywalled content                    | Already gitignored by design, but `audit` re-checks                |
| `_Private/.config/skool_credentials.txt`            | Credentials file accidentally staged | `git rm --cached` + verify `/_Private/.config/` is in `.gitignore` |
| `code/projects/PVG03_RPG/`                          | Personal project folder              | Add to `.git/info/exclude` + update `STRIP_RULES`                  |
| `odin-knowledge-base/docs/karl_zylinski/odin-book/` | Paywalled book chapters              | Already gitignored; verify with `--verbose`                        |

## NEVER

- **Push `main` to the `public` remote.** The hook refuses it; bypassing the hook leaks history.
- **Push without running `audit_public_safety.py --scope branch` first.**
- **Share a `git bundle`** of the local repo without purging - the bundle contains the full history including personal content.
- **Include long excerpts (> 200 words) of Skool lessons** in public posts: fair use does not cover full republication.
- **Disable or skip the pre-push hook.** It is the last line of defense.

## Post-push verification

After the push succeeds, verify the live GitHub repo:

```bash
curl -s https://api.github.com/repos/LaurentOngaro/OdinRAG/contents/ | python -c "import json,sys; data=json.load(sys.stdin); print(f'{len(data)} top-level items')"
```

Expected: ~ 8-10 top-level items (`_Helpers/`, `.kilo/`, `docs/`, `code/`, `odinfmt.json`, `AGENTS.md`, `README.md`, `LICENSE`...). Manually browse the `Code` tab to confirm the absence of `code/projects/PVG03_RPG/`, `_Private/`, `odin-knowledge-base/courses/`, and non-README files under `odin-knowledge-base/docs/karl_zylinski/`.

## If the CI audit fails

Treat the `public` remote as **compromised**:

1. Rotate the secrets in `_Private/.config/skool_credentials.txt` and `cookies.txt`.
2. Pull the leak back into `main`.
3. Force-push a re-filtered `public` branch.
4. Document the incident in the daily.

## Reference

- Full procedure (canonical): [`_Helpers/docs/005_public_release_checklist.md`](../../_Helpers/docs/005_public_release_checklist.md) - 111 lines, covers every edge case.
- Workflow file (re-runs the audit in CI): `.github/workflows/public_safety.yml`.
- Underlying two-branch rationale: [`_Helpers/docs/007_mixing_public_and_private_history.md`](../../_Helpers/docs/007_mixing_public_and_private_history.md).

## Anti-patterns

- **Never** declare a push safe without running the script (exit 0 is the only valid signal).
- **Never** edit `audit_public_safety.py` `FORBIDDEN_PATTERNS` to silence a real leak - that hides the problem, it doesn't fix it.
- **Never** assume the working tree is clean because `git status` is empty - the audit checks `refs/heads/public`, not `main` directly.
