---
title: "007_mixing_public_and_private_history (pointer)"
date: "2026-07-02"
tags: [OdinRAG, reference, git, workflow]
type: how-to
status: active
version: 2.0.0
lastUpdated: "2026-07-02"
updatedBy: "MiniMax-M3 (Kilo Code)"
supersedes: "v1.0.0 archived at _Private/archives/007_mixing_public_and_private_history_EN_2026-07-02.md"
seeAlso: "_Private/docs/001_workflow_public_prive.md (French, detailed, personal use)"
---

# 007_mixing_public_and_private_history (pointer)

> **This file is now a short pointer.** The detailed workflow has moved to a French version for personal comprehension: see [`_Private/docs/001_workflow_public_prive.md`](../../_Private/docs/001_workflow_public_prive.md).
>
> The original English v1.0.0 (2026-07-01) is archived at [`_Private/archives/007_mixing_public_and_private_history_EN_2026-07-02.md`](../../_Private/archives/007_mixing_public_and_private_history_EN_2026-07-02.md).

## The strategy (one paragraph)

A single-repo / two-branch / two-remote workflow keeps full personal history local while pushing only a sanitized public subset to GitHub:

- `main` (local) carries everything: personal project, daily notes, raw research, paywalled scraped content
- `public` (local, filter-branch output) carries only the public subset
- `public-orphan` (local, single empty commit) anchors the diff check
- The `pre-push` hook refuses any push of `main` to the `public` remote
- The `_Helpers/scripts/diagnostic/audit_public_safety.py` script (to be extended) verifies both the working tree and the `public` branch are free of forbidden paths
- A GitHub Action (to be created) re-runs the audit on every push, blocking leaks even if the local hook is bypassed

## What changed in v2.0.0

1. `git subtree split --prefix=.` does NOT work for the repo root (returns `fatal: '.' does not exist`). Replaced by `git filter-branch --index-filter --prune-empty` which has the same effect ("everything except X") and works on the root.
2. Implementation used plumbing commands (`git mktree`, `git commit-tree`, `git update-ref`) to create a truly empty `public-orphan` anchor because `git checkout --orphan` did not reset the index on this Windows + git 2.54 setup.
3. Detailed workflow rewritten in French for personal comprehension. See the linked private doc for the full procedure, security recommendations, and TODO list.
4. PVG03_RPG's inner `.git/` was folded into the outer repo (the user chose "fold simple" - inner history lost).

## Where the canonical procedure lives

**For humans (French):** [`_Private/docs/001_workflow_public_prive.md`](../../_Private/docs/001_workflow_public_prive.md)
**For machines / scripts:** the `.git/hooks/pre-push` hook itself, which encodes the safety check

## Quick reference

```bash
# Refresh the public branch from main (with personal paths filtered out)
git filter-branch -f --index-filter '
  git rm --cached -r --ignore-unmatch code/projects/PVG03_RPG/
  git rm --cached -r --ignore-unmatch _Private/planning/daily
  git rm --cached -r --ignore-unmatch _Private/raw
  git rm --cached -r --ignore-unmatch odin-knowledge-base/courses
  git rm --cached -r --ignore-unmatch odin-knowledge-base/docs/karl_zylinski/odin-book
' --prune-empty -- public

# Push the sanitized branch (never push main!)
git push public public
```

## Outstanding work

See the French doc's "Section 3 - Ce qui reste à faire" for the prioritized TODO list (audit script extension, refresh-public helper script, GitHub Actions CI, etc.).