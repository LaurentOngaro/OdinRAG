---
title: "Mixing public and private history in a single repo"
date: "2026-07-01"
tags: [OdinRAG, reference, git, workflow]
type: how-to
status: active
version: 3.0.0
lastUpdated: "2026-07-02"
updatedBy: "MiniMax-M3 (Kilo Code)"
supersedes: "v1.0.0 (2026-07-01) and v2.0.0 (2026-07-02, pointer stub). v2.0.0 was reverted because it referenced private docs and was not self-sufficient for the public audience."
---

# 007_mixing_public_and_private_history

## The problem

You maintain a repo whose public remote must stay clean of personal content (e.g. an open-source knowledge base or a curated RAG scaffold), yet you also want full local git history for:

- per-project code and devlogs in `code/projects/<your-project>/`
- personal daily notes, planning, raw research in a private folder
- scraped content under fair-use restrictions in `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/`

Having those paths in `.gitignore` means they never reach history. This guide documents the **single-repo / two-branch / one-or-two-remote** strategy that keeps everything versioned locally while keeping the public remote clean.

The intended audience is the public maintainer of the repo. The workflow is described in full here so a fresh collaborator can follow it without reference to any private documentation.

## The strategy in one diagram

```text
working tree (single folder, one .git/)
        |
        | git commit (always lands on local main)
        v
+----------------+        push public public       +--------------------+
|  local main    | -----------------------------> |  remote public     |
| (full history) |                                | (github.com etc.)  |
+----------------+                                +--------------------+
        |
        | git filter-branch --index-filter --prune-empty  (see step 4)
        v
+----------------+
|  local public  |   (sanitised subset, ready to push)
| (public only)  |
+----------------+
```

Layered safety net (in order, before any leak escapes the workstation):

1. **Local hook** — `.git/hooks/pre-push` refuses any push of `main` to the `public` remote.
2. **Audit script** — `_Helpers/scripts/diagnostic/audit_public_safety.py` verifies the `public` branch is free of forbidden paths before you push.
3. **Refresh helper** — `_Helpers/scripts/diagnostic/refresh_public_branch.py` regenerates the sanitised `public` branch in one command (idempotent, refuses a dirty working tree).
4. **GitHub Action** — `.github/workflows/public_safety.yml` re-runs the audit on every push and pull request targeting `main`, blocking leaks even if the local hook is bypassed.
5. **CI auto-cleanup** — the GitHub Action also prunes the filter-branch backup ref so no orphan state survives in CI.

## Why not the alternatives

- **Two clones side by side**: loses unified history and breaks AI tooling that expects a single working tree (the `kb-navigator` and `odin-pattern-finder` skills ship with this repo and assume one workspace).
- **Submodule**: breaks the same tooling, with the added friction of branch juggling when contributors clone.
- **Two remotes with no local split**: forces every push to choose the right destination manually, and one typo (`git push public main`) ships everything.

One repo, one working tree, two branches, one or two remotes gives you all of: local history, single editor context, public isolation, multi-layer safety.

## Prerequisites

- `git` 2.30 or newer (for `--orphan`, modern `filter-branch`, and refspec syntax).
- A public remote you already push to. This guide renames it to `public` in step 1; pick any consistent name.
- (Optional but recommended) A private remote you control — a self-hosted Gitea, a private repo on a trusted forge, a `git` daemon over SSH. The URL only lives in your local git config; never in any tracked file.
- The audit script `_Helpers/scripts/diagnostic/audit_public_safety.py` present and lint-clean on its current branch.

## Step 1 - rename the public remote (and optionally add a private remote)

The rename is purely cosmetic — stay consistent. Rename `origin` to `public`:

```bash
git remote rename origin public
git remote -v
```

If you have a private remote, add it now (otherwise skip — local history is enough on its own):

```bash
git remote add private <URL_OF_YOUR_PRIVATE_REMOTE>
git remote -v
```

Expected output: two remotes listed, `public` and (optionally) `private`. Nothing is pushed yet, and no commit history has changed.

## Step 2 - personal paths belong in `.git/info/exclude`, not `.gitignore`

`.gitignore` is tracked and shows up in every public clone. Patterns that scream "ignore personal content here" leak intent to anyone who clones. Move them out of `.gitignore` and into `.git/info/exclude` (local-only, never version-controlled).

Replace this section of `.gitignore`:

```gitignore
_Private/
_Raw/                                    # legacy, ignored if present
odin-knowledge-base/courses/
courses/                                 # legacy, ignored if present
odin-knowledge-base/docs/karl_zylinski/odin-book/**/*.md
!odin-knowledge-base/docs/karl_zylinski/odin-book/README.md
/code/projects/PVG03_RPG/
```

with this single defense-in-depth line (kept for credentials, not for content):

```gitignore
# Personal paths are intentionally not ignored at the repo level.
# Each developer maintains their own .git/info/exclude (see this doc, step 2).
# The single line below is the secrets-only defense in depth: even if a private remote is added later, credentials must never reach any remote.
/_Private/.config/
```

And put the precise personal patterns in `.git/info/exclude`:

```gitignore
# Personal paths tracked locally via `git add -f`. Local-only; this file is per-clone and not version-controlled. See _Helpers/docs/007_mixing_*.md.
/code/projects/<YOUR-PROJECT>/
/_Private/
/odin-knowledge-base/courses/
/odin-knowledge-base/docs/karl_zylinski/odin-book/
```

Adapt the patterns to your own private folders. Keep them in sync with `FORBIDDEN_PATTERNS` in `audit_public_safety.py` and `STRIP_RULES` in `refresh_public_branch.py` — three places to update when the set of personal paths changes.

## Step 3 - import personal content under the override

The `-f` flag bypasses the per-clone exclusion rules so personal files can be staged. Run on `main`:

```bash
# Example for this repo - adapt to your own paths
git add -f code/projects/PVG03_RPG/ \
         _Private/planning/daily/ \
         _Private/raw/ \
         odin-knowledge-base/courses/ \
         odin-knowledge-base/docs/karl_zylinski/odin-book/

git status
git commit -m "chore: import personal history into private main"
```

`_Private/.config/` is permanently gitignored. Do **not** stage it, even with `-f` — credentials must never reach history at all. If credentials have ever been committed by accident, see the "Recovery" section below.

After this, `git log -- <your-personal-path>/` shows full project history locally. The public remote has not been touched.

## Step 4 - generate the sanitised `public` branch

The standard `git subtree split --prefix=.` advice in the original v1.0.0 of this doc DOES NOT WORK for a whole-repo split. Git returns `fatal: '.' does not exist` because `subtree` expects a sub-directory, not the root. This implementation uses `git filter-branch --index-filter --prune-empty` instead, which has the same "everything except X" effect and works at the root.

### Step 4a - create the empty anchor branch

`git checkout --orphan` on Windows + recent git sometimes does not reset the index, leaving a non-empty initial commit. Use plumbing commands so the anchor is guaranteed empty:

```bash
# Reset HEAD to a new orphan branch ref
git symbolic-ref HEAD refs/heads/public-orphan

# Drop everything from the index
git read-tree --empty

# Write the well-known empty tree (4b825dc642cb6eb9a060e54bf8d69288fbee4904)
empty_tree=$(git write-tree)

# Create a single commit pointing at it
orphan_commit=$(git commit-tree "$empty_tree" -m "chore: public branch anchor")

# Restore HEAD on main and the index
git symbolic-ref HEAD refs/heads/main
git read-tree HEAD

# Save the orphan ref
git branch -f public-orphan "$orphan_commit"

# Verify: the orphan tree should be empty
git ls-tree -r public-orphan | wc -l   # -> 0
```

### Step 4b - regenerate `public` from `main` via the helper script

The wrapper at `_Helpers/scripts/diagnostic/refresh_public_branch.py` is the durable entry point. It is **idempotent** (no-op when the `public` branch is already in sync) and **refuses to run on a dirty working tree** (filter-branch limitation — stash first, then `git stash pop`).

```bash
# Dry-run: show what would happen, do nothing
python _Helpers/scripts/diagnostic/refresh_public_branch.py --check

# Refresh if needed (the first run after Step 3 always does something)
python _Helpers/scripts/diagnostic/refresh_public_branch.py

# Refresh + run the audit in one go
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
```

Under the hood the script runs:

```bash
# 1. Reset the public branch at main's tip
git branch -f public main

# 2. Run filter-branch with the personal-pattern index-filter (--prune-empty drops commits whose trees become entirely personal)
git filter-branch -f \
  --index-filter 'sh -c '"'"'
    git rm --cached -r --ignore-unmatch code/projects/PVG03_RPG
    git rm --cached -r --ignore-unmatch _Private
    git rm --cached -r --ignore-unmatch odin-knowledge-base/courses
    git rm --cached -r --ignore-unmatch odin-knowledge-base/docs/karl_zylinski/odin-book
  '"'"' \
  --prune-empty \
  -- public

# 3. Prune the backup ref filter-branch just created
git update-ref -d refs/original/refs/heads/public || true
```

Adapt the `--index-filter` paths to your own personal set. The double shell quoting (the unusual `'"'"'` sequence) is there to embed the `sh -c` payload safely inside PowerShell or bash; copy it carefully.

Once `public` looks right, push it once to the public remote to create the upstream branch:

```bash
git push -u public public
```

Verify the tree sent is what you expect:

```bash
git ls-tree -r public --name-only | head -20
```

You should see nothing starting with `_Private/`, nothing under `code/projects/<your-project>`, and no `odin-knowledge-base/courses/` files.

### Why filter-branch and not filter-repo

`git filter-repo` is the modern, faster, safer replacement recommended by upstream. It is a separate Python tool (`pip install git-filter-repo`) and not bundled with `git`. Until filter-repo is a dependency of this repo, we rely on filter-branch. The migration is mechanical when the time comes — see [Trade-offs](#trade-offs).

## Step 5 - install the pre-push hook

Save the script below as `.git/hooks/pre-push` (no extension). On git for Windows the executable bit is set automatically when the file has a shebang; on Unix run `chmod +x .git/hooks/pre-push`.

```bash
#!/usr/bin/env bash
# Pre-push hook: refuses pushes to the `public` remote that contain personal paths.
# See _Helpers/docs/007_mixing_public_and_private_history.md for the full workflow.

set -euo pipefail

remote="$1"

# Only enforce on the public remote.
if [ "$remote" != "public" ]; then
  exit 0
fi

# Personal patterns anchored at repo root. MUST stay in sync with refresh_public_branch.py STRIP_RULES and audit_public_safety.py FORBIDDEN_PATTERNS.
personal_pattern='^(code/projects/PVG03_RPG/|_Private/|odin-knowledge-base/courses/|odin-knowledge-base/docs/karl_zylinski/odin-book/)'

while read -r local_ref _remote_ref; do
  if [ -z "$local_ref" ]; then
    continue
  fi

  diff_output="$(git diff --name-only "public-orphan..$local_ref" 2>/dev/null || true)"

  if echo "$diff_output" | grep -qE "$personal_pattern"; then
    echo "Refusing push to public remote: personal paths detected in $local_ref." >&2
    echo "Push that branch to the 'private' remote, not 'public'." >&2
    echo "" >&2
    echo "Offending paths:" >&2
    echo "$diff_output" | grep -E "$personal_pattern" >&2
    exit 1
  fi
done

exit 0
```

To test without risking a real push:

```bash
git push public main --dry-run     # expect: refusal + leaked path list
git push public public --dry-run   # expect: success (no personal paths on public)
```

## Step 6 - extend `_Helpers/scripts/diagnostic/audit_public_safety.py`

This step documents the v3.0.0 extension shipped with this guide. If you are reading this from an older checkout, apply the changes below.

The audit script now scans **the local `public` branch's tree** (the thing actually going to GitHub) in addition to the working tree. Two scopes, with the publish-time check as the default:

```bash
# Default: audit the local public branch (what will be pushed). Pass.
python _Helpers/scripts/diagnostic/audit_public_safety.py

# Only the working tree. Used to verify ignore-pattern hygiene.
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope tree

# Both. Used for paranoid double-checks. NOTE: with the public/private split workflow the working tree will always show personal files because main is supposed to carry them — this scope is for diagnosis, not for the push gate.
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope both

# List every file examined (useful when chasing a false positive).
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose
```

Exit codes:

- `0` — clean.
- `1` — forbidden paths found. Re-run `refresh_public_branch.py` if it's a branch issue, or update `.gitignore` / `.git/info/exclude` if it's a tree issue.
- `2` — git missing, branch absent, etc.

The script's `FORBIDDEN_PATTERNS` list drives both the audit scan and the inline display. Keep it in sync with the `personal_pattern` regex in the hook and the `STRIP_RULES` list in `refresh_public_branch.py`.

## Step 7 - CI: GitHub Action for paranoid double-check

Add `.github/workflows/public_safety.yml`. It re-runs the refresh + audit on GitHub's runners for every push to `main` and every pull request targeting `main`, so a leak is caught even if the local hook is bypassed or a contributor runs the workflow from a fork.

Key behaviour:

- `actions/checkout@v4` with `fetch-depth: 0` — filter-branch needs the full commit graph.
- `actions/setup-python@v5` — only needed for the audit script (stdlib-only).
- `FILTER_BRANCH_SQUELCH_WARNING=1` — silences the multi-line gotcha warning; the workflow is intentional.
- The "Regenerate local public branch from main" step is essentially a copy of the script in step 4b, inlined so the workflow does not depend on the helper script being present at the time the GH Action runs.
- The final audit step fails the job on any violation, blocking the PR / push.

If the workflow ever fails, treat the public remote as compromised (see Recovery).

## Daily workflow

```bash
# 1. Work on main as usual.
git add -A
git commit -m "..."

# 2. When ready to publish:
git stash push -u -m "wip-publish"        # only if working tree is dirty
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify
git stash pop                              # only if you stashed

# 3. Push the sanitised branch (the hook refuses main!).
git push public public
```

The `public` branch can lag behind `main` by hours, days, or weeks. That lag is a feature, not a bug: it gives you time to review what becomes public.

If you also use a private remote:

```bash
# Backup your full history.
git push private main
```

## Recovery procedures

### Lost a commit on the public branch

`git reflog public` lists every state the branch has been in. Recover with `git reset --hard <sha>` then `git push --force-with-lease public public`.

### Accidentally pushed a personal path to the public remote

1. Push the same ref to the private remote immediately (`git push private main` if you have one). The local copy is the source of truth.
2. Rewrite `public` to a clean state with `python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify`.
3. `git push --force-with-lease public public`.
4. On the public remote, history rewriting depends on the host. Personal repos on commercial forges support `git push --force` after a cooldown. Shared repos and forks are out of reach: the leak is permanent in third-party mirrors.
5. Treat the leaked content as compromised: rotate every secret that lives (or lived) in the leaked paths, request cache scrubs where possible (Google cache, GitHub search), and document the incident in your private notes.

### Pre-push hook blocks a legitimate push

Inspect the diff the hook printed. If the paths are genuinely public, amend `.gitignore` and `.git/info/exclude`, recommit on `main`, run `refresh_public_branch.py --verify`, retry. If the paths are personal, you caught a mistake — do not bypass the hook.

### `_Private/.config/` (credentials) ever gets committed

Reset-and-rebuild is the only safe response. Git cannot truly erase a secret from history if the repo has any clones or forks. Rotate the credential first, THEN scrub history. The simple version (acceptable for small repos with no public clones yet):

```bash
# Move credentials out of git's reach first.
mkdir -p ../credentials-backup
mv _Private/.config/* ../credentials-backup/
chmod 600 ../credentials-backup/*

# Re-scrub history (filter-branch will rewrite every commit to drop them).
python _Helpers/scripts/diagnostic/refresh_public_branch.py --verify

# Wipe local main and rebuild from public + personal-content import commits.
# (Detailed recipe depends on your history shape - see Karl Zylinski's book chapter on manual memory management for the general pattern.)
```

For repos that have already been pushed to a public remote with secrets inside, treat them as compromised AND consult a security expert. The hook only catches future leaks.

## Trade-offs

- **One local repo, two responsibilities.** Mental cost: every push goes through a "which remote?" decision. The hook enforces it; you still have to think.
- **`filter-branch` rewrites history.** The public branch's history is a rewriting of main's. `git blame` on a public file will not see commits that only touched personal files, which is what you want. The downside is older commits that produced identical content on `public` may vanish via `--prune-empty`.
- **Public branch can drift.** If you forget to refresh `public` before push, the public remote ships an outdated subset. The pre-push hook does not detect stale `public`; it only checks for forbidden paths.
- **`filter-branch` is deprecated.** Upstream recommends `git filter-repo`. Migration is mechanical when this repo gains a Python dependency on filter-repo: replace the `git filter-branch` calls in `refresh_public_branch.py` and the GitHub Action with the equivalent `git filter-repo --path ... --invert-paths` invocations.
- **Filter-branch leaves a backup ref.** `refs/original/refs/heads/public` is created on every run. The helper script and the GitHub Action both delete it after success. A stale backup is harmless but consumes space.
- **Forks on the public remote.** A leaked secret in a public remote lives forever in forks and clones. No git machinery can erase it from third-party mirrors. The hook is your only prevention; the audit is your only verification.
- **The pre-push hook only checks paths.** It does not inspect commit messages, author identities, or dates. A commit message that says "fix \_Private/planning/daily typo" reaches the public remote if no path on its content side is personal (because filter-branch already rewrote the trees). If that matters, add a stricter CI check.

## Configuration files this strategy creates

After completing all steps you will have touched these files (paths are repo-root-relative):

| Path                                                   | Purpose                                             | Tracked?   |
| ------------------------------------------------------ | --------------------------------------------------- | ---------- |
| `.gitignore`                                           | secrets + build/IDE ignores only                    | yes        |
| `.git/info/exclude`                                    | per-clone personal ignores                          | NO (local) |
| `refs/heads/main`                                      | full history, the local source of truth             | yes        |
| `refs/heads/public-orphan`                             | empty anchor for `public-orphan..<ref>` diff checks | yes        |
| `refs/heads/public`                                    | filter-branch output, pushed to the public remote   | yes        |
| `.git/hooks/pre-push`                                  | refuses main -> public pushes                       | NO (local) |
| `_Helpers/scripts/diagnostic/audit_public_safety.py`   | `--scope tree/branch/both`, lint-clean              | yes        |
| `_Helpers/scripts/diagnostic/refresh_public_branch.py` | idempotent wrapper, lint-clean                      | yes        |
| `.github/workflows/public_safety.yml`                  | CI re-runs audit on push + PR                       | yes        |

## References

- `_Helpers/docs/005_public_release_checklist.md` - the pre-push procedure this guide builds on, updated to use the helper script.
- `_Helpers/scripts/diagnostic/README - diagnostic.md` - the audit + refresh + coherence scripts.
- `.github/workflows/public_safety.yml` - the CI guard-rail.
- `AGENTS.md` at the repo root - global conventions, including markdown style and frontmatter.
- `SOURCES.md` - if you add a new paid source, update `audit_public_safety.py FORBIDDEN_PATTERNS` and `refresh_public_branch.py STRIP_RULES` so the two scripts stay in sync.
