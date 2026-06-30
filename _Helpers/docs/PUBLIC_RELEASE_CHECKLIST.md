# Public release checklist - OdinRAG repo

## Why this document exists

The repo contains scraped content (Skool paywall, Karl Zylinski blog) that **must never** be published. This checklist is the only authorised procedure to make the repo public.

## Steps

### 1. Local side - `.gitignore`

The `COPYRIGHTED SCRAPED CONTENT` section of `.gitignore` is the source of truth. Verify it contains:

- `odin-knowledge-base/courses/`
- `courses/`
- `/docs/karl_zylinski/*.md` + `/docs/karl_zylinski/odin-book/*.md` + `!/docs/karl_zylinski/README.md`
- `/docs/newsletters/*.md` + `!/docs/newsletters/README.md`
- `/planning/daily/`

### 2. Automatic audit

```bash
python _Helpers/audit_public_safety.py --verbose
```

Expected output: `[OK] Public safety audit: clean`.

Exit code `0` -> you can push.
Exit code `1` -> fix `.gitignore` or a residual tracker.

### 3. Post-push verification

```bash
curl -s https://api.github.com/repos/LaurentOngaro/OdinRAG/contents/ | python -c "import json,sys; data=json.load(sys.stdin); print(f'{len(data)} top-level items')"
```

Compare the output to the expected count (~ 8-10 top-level items: `_Helpers/`, `.kilo/`, `docs/`, `code/`, `odinfmt.json`, `AGENTS.md`, `README.md`, `LICENSE`...).

Browse the `Code` tab on GitHub manually to confirm the absence of:

- `odin-knowledge-base/courses/`
- `/docs/karl_zylinski/*.md` (other than README)

## NEVER

- Push without having run `audit_public_safety.py` first.
- Share a `git bundle` of the local repo without having done the purge - it contains the entire history.
- Include long excerpts (> 200 words) of Skool lessons in public posts: fair use does not cover full republication.

## When to re-run this checklist

- Before any private -> public transition.
- Before sharing the repo with a third party (colleague, mentor).
- Before mirroring on another platform (GitLab, Codeberg, etc.).
- After adding a new scraping source (`SOURCES.md` -> if a new source is added, update `.gitignore` AND `_Helpers/audit_public_safety.py`).
