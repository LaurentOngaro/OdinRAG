---
title: "Mixing public and private history in a single repo"
date: 2026-07-01
tags: [OdinRAG, reference, git, workflow]
type: how-to
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# 007_mixing_public_and_private_history

## The problem

You maintain a repo whose public remote must stay clean of personal content (for example an open-source knowledge base or a curated RAG scaffold), yet you also want full local git history for:

- per-project code and devlogs in `code/projects/<your-project>/`
- personal daily notes in `_Private/planning/daily/`
- one-shot raw research in `_Private/raw/`
- scraped content under fair-use restrictions in `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/`

The repo currently keeps those paths out of `.gitignore`, so they never reach history at all. This guide documents the **single-repo / two-branch / two-remote** strategy that keeps everything versioned locally while keeping the public remote clean.

## The strategy in one diagram

```text
working tree (single folder, one .git/)
        |
        | git commit  (always lands on local main)
        v
+----------------+        push private main       +--------------------+
|  local main    | -----------------------------> |  private remote    |
| (full history) |                                | (your own server)  |
+----------------+                                +--------------------+
        |
        | git subtree split  (or manual mirror)
        v
+----------------+        push public public      +--------------------+
|  local public  | -----------------------------> |  public remote     |
| (public only)  |                                | (github.com etc.)  |
+----------------+                                +--------------------+
```

A `pre-push` hook is the only thing standing between a wrong `git push` and a leaked history. The hook refuses to push `main` to the public remote. The audit script `_Helpers/scripts/diagnostic/audit_public_safety.py` is extended to scan the `public` branch's tree, not just the working tree.

## Why not the alternatives

Two clones side by side lose unified history and break AI tooling that expects a single working tree (the `kb-navigator` and `odin-pattern-finder` skills assume one workspace). A submodule breaks the same tooling, with the added friction of branch juggling. One repo, one working tree, two branches, two remotes gives you all of: local history, single editor context, public isolation.

## Prerequisites

- `git` 2.30 or newer (for modern `subtree split` and refspec syntax).
- A private remote you control (a private repo on a forge you trust, self-hosted Gitea, a `git` daemon over SSH, ...). The URL only lives in your local git config, never in any tracked file.
- A public remote you already push to. This guide assumes it gets renamed to `public` in step 1; pick any consistent names.
- The audit script `_Helpers/scripts/diagnostic/audit_public_safety.py` already present and passing on the current working tree.

## Step 1 - rename and add the private remote

This guide renames the public remote to `public` and adds a second remote named `private`. The rename is purely cosmetic: stay consistent.

```bash
git remote rename origin public
git remote add private <URL_OF_YOUR_PRIVATE_REMOTE>
git remote -v
```

Expected output: two remotes listed, `public` and `private`. Nothing is pushed yet, and no commit history has changed.

## Step 2 - move personal paths out of `.gitignore`

Tracked `.gitignore` must stay strict for collaborators cloning the repo, who should never see your personal content. Override it for yourself only.

In `.gitignore`, **remove** the following lines (or move them verbatim into `.git/info/exclude`, which is local and not version-controlled):

```gitignore
/code/projects/PVG03_RPG/   # personal Odin project
/_Private/planning/daily/
/_Private/raw/
/odin-knowledge-base/courses/
/odin-knowledge-base/docs/karl_zylinski/odin-book/**/*.md
```

Replace them with a single pointer comment so future readers know where to look:

```gitignore
# Personal paths are NOT ignored at the repo level: see _Helpers/docs/007_mixing_public_and_private_history.md
# Collaborators who want to ignore them locally should copy the patterns above into .git/info/exclude.
```

The patterns above match the ones already enforced by `_Helpers/scripts/diagnostic/audit_public_safety.py`. Keep both in sync.

## Step 3 - commit personal content under the override

The `-f` flag bypasses the local exclusion rules (if any remain) so the personal files can be staged.

```bash
git add -f code/projects/ _Private/planning/daily/ _Private/raw/ odin-knowledge-base/courses/ odin-knowledge-base/docs/karl_zylinski/odin-book/
git status
git commit -m "chore: import personal history into private main"
```

After this, `git log -- code/projects/<your-project>/` shows your full project history locally. The public remote has not been touched.

## Step 4 - create the public branch

Two approaches, in order of preference.

### 4a. `git subtree split` (recommended for automation)

This produces a `public` branch that contains only the public subset of `main`, preserving history for the files that exist in both branches. The trick is an `--onto` orphan target so the public branch starts clean and is rebuilt from scratch on every refresh.

```bash
# Create an empty orphan once
git checkout --orphan public-orphan
git rm -rf . 2>/dev/null || true
git commit --allow-empty -m "chore: public branch anchor"
git checkout main

# Public paths = everything EXCEPT the personal paths.
# The exclude regex matches code/projects/PVG03_RPG/ (the personal project).
git config split.public.path .
git config split.public.exclude 'code/projects/PVG03_RPG/|_Private/planning/daily|_Private/raw|odin-knowledge-base/courses|odin-knowledge-base/docs/karl_zylinski/odin-book'
git subtree split --prefix=. -b public --onto public-orphan
```

If your personal paths differ, edit the `exclude` value. The format is one extended-regex per personal prefix, anchored implicitly to the repo root.

### 4b. hand-maintained mirror

Use a worktree to keep `public` clean by hand. Slower but easier to debug:

```bash
git worktree add ../odinrag-public public-orphan
# In the new worktree: delete the personal paths, then commit.
```

Whichever approach you choose, push the resulting `public` branch once to the public remote to create it, then continue:

```bash
git push -u public public
```

## Step 5 - install the pre-push hook

Save the following as `.git/hooks/pre-push`. On git for Windows the executable bit is set automatically when the file has a shebang; on Unix run `chmod +x .git/hooks/pre-push`.

```bash
#!/usr/bin/env bash
set -euo pipefail

remote="$1"
if [ "$remote" != "public" ]; then
  exit 0
fi

# Personal paths that must never reach the public remote.
# Anchored at repo root. Excludes code/projects/PVG03_RPG/ (the personal Odin project).
personal_pattern='^(code/projects/PVG03_RPG/|_Private/planning/daily|_Private/raw|odin-knowledge-base/courses|odin-knowledge-base/docs/karl_zylinski/odin-book)/'

while read -r local_ref _remote_ref; do
  if [ -z "$local_ref" ]; then
    continue
  fi
  diff_output="$(git diff --name-only "public-orphan..$local_ref" 2>/dev/null || true)"
  if echo "$diff_output" | grep -qE "$personal_pattern"; then
    echo "Refusing push to public remote: personal paths detected in $local_ref." >&2
    echo "Push that branch to the 'private' remote, not 'public'." >&2
    exit 1
  fi
done

exit 0
```

To test the hook without risking a real push:

```bash
git push public main --dry-run
```

Expected: the hook refuses with the message above. A successful push would be `git push public public`, not `git push public main`.

## Step 6 - extend `_Helpers/scripts/diagnostic/audit_public_safety.py`

The audit script currently walks the working tree via `git ls-files`. After this guide, it must also walk the `public` branch's tree, since that is what the public remote will receive.

Add the following helper near the top of the file, alongside `git_ls_files()`:

```python
def git_ls_branch(branch: str = "public") -> list[str]:
    """Return the list of file paths present in the given branch's tree."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", branch],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.splitlines() if f]
```

In `audit()`, add a second pass after the working-tree scan: iterate `git_ls_branch("public")` against the same `FORBIDDEN_PATTERNS` list and append any violation. The patterns already in the script match the regex used by the hook, so the two checks stay aligned automatically.

Run it before any push:

```bash
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose
```

Exit code `0` means the `public` branch is safe to push to the public remote.

## Daily workflow

```bash
# Commit anywhere, on any branch (always lands on local main).
git add -A
git commit -m "..."

# Push personal work to the private remote.
git push private main

# Refresh the public branch from main, then push it.
git subtree split --prefix=. -b public --onto public-orphan
git push public public

# Or, if you hand-maintain public: rebase / re-mirror, then push.
git push public public
```

The public branch can lag behind main by hours, days, or weeks. That lag is a feature, not a bug: it gives you time to review what becomes public.

## Recovery procedures

### Lost a commit on the public branch

`git reflog public` lists every state the branch has been in. Recover with `git reset --hard <sha>` then `git push --force-with-lease public public`.

### Accidentally pushed a personal path to the public remote

1. Push the same ref to the private remote immediately: `git push private main` (the private remote is still authoritative for your full history).
2. Rewrite `public` to a clean state: `git subtree split --prefix=. -b public --onto public-orphan`.
3. `git push --force-with-lease public public`.
4. On the public remote, history rewriting depends on the host. Personal repos on commercial forges support `git push --force` after a cooldown. Shared repos and forks are out of reach: the leak is permanent in third-party mirrors.
5. Treat the leaked content as compromised: rotate any secrets present, request cache scrubs where possible, and document the incident in your `_Private/planning/daily/`.

### Pre-push hook blocks a legitimate push

Inspect the diff the hook printed. If the paths are genuinely public, amend `.gitignore` and `.git/info/exclude`, recommit on `main`, refresh `public`, retry. If the paths are personal, you caught a mistake: do not bypass the hook.

## Trade-offs

- **One local repo, two responsibilities.** Mental cost: every push goes through a "which remote?" decision. The hook enforces it but you still have to think.
- **`subtree split` rewrites history.** The public branch's history is a rewriting of main's. `git blame` on a public file will not see commits that only touched personal files, which is what you want.
- **Public branch can drift.** If you forget to refresh `public` before push, the public remote ships an outdated subset. The pre-push hook does not detect stale `public`; it only checks for forbidden paths.
- **Forks on the public remote.** A leaked secret in a public remote lives forever in forks and clones. No git machinery can erase it from third-party mirrors. The hook is your only prevention; the audit is your only verification.

## References

- `_Helpers/scripts/diagnostic/audit_public_safety.py` - the safety gate, extended in step 6.
- `_Helpers/docs/005_public_release_checklist.md` - the pre-push procedure this guide builds on.
- `AGENTS.md` at the repo root - global conventions, including markdown style and frontmatter.
