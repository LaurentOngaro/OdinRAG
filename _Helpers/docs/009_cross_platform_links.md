---
title: "Cross-platform links (Windows junctions / Linux symlinks)"
date: "2026-10-25"
tags: [OdinRAG, reference, windows, linux, junction, symlink, workspace, tooling]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-10-25"
updatedBy: "Kilo Code (manifest + generator replacing the hand-made WSL symlinks; Windows junctions now resolve correctly)"
---

# 009_cross_platform_links

> **Why this document exists.** The workspace exposes folders that live OUTSIDE the repository (the personal Odin projects) under `code/projects/`, so that Kilo, VS Code and Zed see them as if they were local. The filesystem primitive is OS-specific: Windows uses NTFS junctions (`mklink /J`), Linux uses symbolic links (`ln -s`). This document describes the single mechanism that makes the same layout work on both systems, and why the "create both kinds of links in the same folder" idea was rejected.

## TL;DR

- One **manifest** declares the link topology: [`_Helpers/links.jsonc`](../links.jsonc) (tracked, portable, no personal path in it).
- One **generator** applies it on the current OS: [`_Helpers/scripts/dev/sync_links.py`](../scripts/dev/sync_links.py) (junction on Windows, symlink on Linux, same CLI on both).
- The **absolute paths** stay machine-specific in the gitignored `_Private/.config/user_config.jsonc` -> `links` section (one entry per OS).
- The links themselves are **never tracked by git**: they are machine state, and a junction cannot even be represented in a git tree.
- Daily use: `python _Helpers/scripts/dev/sync_links.py --check` (dry-run, exit 1 on drift) and `--apply` (create or repair).

```bash
# Dry-run: report what is missing or pointing somewhere else (exit 1 on drift)
python _Helpers/scripts/dev/sync_links.py --check

# Create / repair the links for the current OS
python _Helpers/scripts/dev/sync_links.py --apply

# Show the topology and the state of every link
python _Helpers/scripts/dev/sync_links.py --list
```

### VS Code tasks

| Task | Effect |
| --- | --- |
| `[LINKS] Sync workspace links (current OS)` | Runs `--apply`: regenerates every link with the primitive of the current host and replaces the links made for the other OS. |
| `[LINKS] Check workspace links (dry-run)` | Runs `--check`: reports the state of every link, changes nothing. |

Zed mirrors the sync task as `Links: Sync workspace links (current OS)` (`.zed/tasks.json`).

Run the sync task after moving from one machine to the other (Windows <-> WSL/Linux). It is idempotent: nothing changes when the links are already correct.

### Session bootstrap (for AI agents)

`AGENTS.md` instructs every coding agent to run `python _Helpers/scripts/dev/sync_links.py --check` before any file work, and to run `--apply` when the check reports a drift. The check takes about 100 ms, never modifies anything, and guarantees the agent reads the project files through a link that actually resolves on the current OS.

## The problem

A link that works on one OS is usually broken on the other:

| OS | Primitive | Command | Notes |
| --- | --- | --- | --- |
| Windows | NTFS junction | `mklink /J <link> <target>` | No administrator rights, no Developer Mode, local absolute targets only. |
| Windows | Symbolic link | `mklink /D` / `os.symlink` | Needs Developer Mode or an elevated shell. |
| Linux | Symbolic link | `ln -s <target> <link>` | Relative or absolute target. |

The failure mode is silent and confusing. A symlink created from WSL keeps its POSIX target (`/mnt/d/...`) inside the NTFS reparse point, so it resolves fine in WSL and is broken in Windows (`D:\mnt\d\...` does not exist). The reverse happens with a junction: WSL follows it, but the link is meaningless as soon as the folder is checked out on a machine without `mklink`.

That is exactly the state this repository was in: the three links under `code/projects/` were WSL-style symlinks pointing at `/mnt/D/...`, and they did not resolve from Windows.

## Why "both link types in the same folder" is a bad idea

The idea was: create `PVG03_RPG` as a junction AND `PVG03_RPG_link` as a symlink, so that whichever primitive the host supports, one of the two entries works. It does not work, for five reasons:

1. **Only one primitive can exist per host.** A junction cannot be created on Linux at all, and a symlink on Windows needs Developer Mode. The "other" entry is either a dangling link or a plain file, so the promise "both are always there" is false on both systems.
2. **Two names for the same project.** On Windows, `code/projects/PVG03_RPG` and `code/projects/PVG03_RPG_link` expose the same source tree twice. Kilo indexes it twice, the README coherence audit sees duplicate wikilinks, `odin_task.ps1` matches both with its `^code[\\/]projects[\\/]` regex, and every "which project is this?" question becomes ambiguous.
3. **The duplication drifts.** Adding a fourth project means remembering to create two entries in two places. The moment one is forgotten, the two hosts drift apart - which is the problem the whole mechanism was supposed to solve.
4. **Git sees them differently.** On Windows, Git classifies a junction as a symlink (mode `120000`), not as a directory. Two entries per project means two untracked entries, two entries to exclude, two entries to strip from the public branch.
5. **The consumer does not care.** Every tool that reads the workspace (`odin_task.ps1`, the VS Code launch configs, Kilo, the auditors) expects ONE path per project: `code/projects/<name>`. The primitive behind it is an implementation detail that only the generator should know.

The rule that replaces it: **one logical link, one path, one generator. The primitive is chosen by the host, never by the user.**

## The mechanism

### 1. The manifest (tracked)

[`_Helpers/links.jsonc`](../links.jsonc) declares the topology. It contains logical names and repo-relative locations only, so it is safe to publish.

```jsonc
{
  "id": "project.PVG03_RPG",
  "link": "code/projects/PVG03_RPG",
  "target": { "config": "project.PVG03_RPG" },
  "scope": "private",
  "description": "Personal Odin RPG project (external repository)."
}
```

| Field | Meaning |
| --- | --- |
| `id` | Logical identifier. Also drives the env var override `ODINRAG_LINK_<ID>`. |
| `link` | Where the link lives, relative to the repo root. |
| `target` | `{ "repo": "<relative path>" }` for a portable internal target, `{ "config": "<key>" }` for a machine-specific external target. |
| `scope` | `private` (personal content, must never reach the public branch) or `workspace` (points inside the repo). |
| `mode` | Optional: `auto` (default), `junction` or `symlink`. |
| `optional` | Optional: when true, a link that cannot be resolved on this OS is skipped instead of reported as an error. |

### 2. The machine paths (local, gitignored)

The absolute target of each external link lives in `_Private/.config/user_config.jsonc`, with one entry per OS:

```jsonc
"links": {
  "project.MyGame": {
    "windows": "D:/Projects/Odin/MyGame",
    "linux": "/mnt/d/Projects/Odin/MyGame"
  }
}
```

The generator picks the entry matching the current OS (`windows`, `linux`, then `default`). An environment variable (`ODINRAG_LINK_PROJECT_PVG03_RPG`) overrides everything, which is handy for a one-off run without editing the config.

### 3. The generator

[`_Helpers/scripts/dev/sync_links.py`](../scripts/dev/sync_links.py) is the only component that knows about junctions.

| Action | Behaviour |
| --- | --- |
| `--check` (default) | Read-only. Reports the state of every link and exits 1 if something must change. |
| `--apply` | Creates the missing links, replaces the links that point elsewhere, recreates the broken ones. Idempotent. |
| `--prune` | Removes the links that live next to the declared ones but are not declared (only inside the `code/projects/` container). |
| `--list` | Prints the topology, the resolved target and the state of every link. |

Per-OS behaviour:

- **Windows**: NTFS junction via `mklink /J` (no elevation needed), with an automatic fallback to a symbolic link when the junction cannot be created (network target, no Developer Mode).
- **Linux / WSL**: symbolic link via `os.symlink`.

The generator also compares the PRIMITIVE, not only the target: a symbolic link sitting where this host expects a junction is reported as `drift` and replaced by `--apply`. That is what makes the sync task a real OS switch: run it on the other machine and every link is rebuilt with the right primitive.

Statuses reported by `--check`: `ok`, `missing`, `drift` (wrong target or wrong primitive), `broken` (target gone), `conflict` (a real folder occupies the link path), `unresolved` (no path for this OS), `skipped` (optional link, not configured here).

### Safety guarantees

- The script **never deletes real content**. A link is removed with `os.unlink` (symlink) or `os.rmdir` (junction); a real directory sitting at the link path is reported as `conflict` and left untouched.
- It never follows a link into the target tree, so a project with 50 000 files is never walked.
- `--prune` only scans the container of the `private` links (`code/projects/`). The hand-made links at the repo root (`.obsidian`, ...) are never touched.
- `--apply` on a clean machine is a no-op.

## Adding a new project link

1. Declare the link in [`_Helpers/links.jsonc`](../../_Helpers/links.jsonc):

   ```jsonc
   {
     "id": "project.PVG04_MyGame",
     "link": "code/projects/PVG04_MyGame",
     "target": { "config": "project.PVG04_MyGame" },
     "scope": "private",
     "description": "Personal Odin project (external repository)."
   }
   ```

2. Add the absolute paths in `_Private/.config/user_config.jsonc`:

   ```jsonc
   "project.PVG04_MyGame": {
     "windows": "D:/Projects/Odin/MyGame",
     "linux": "/mnt/d/Projects/Odin/MyGame"
   }
   ```

3. Apply on the current host, then on the other one:

   ```bash
   python _Helpers/scripts/dev/sync_links.py --apply
   ```

4. Declare the project as forbidden content in the public-branch pipeline: `STRIP_RULES` in `publish_public.py` and `FORBIDDEN_PATTERNS` in `audit_public_safety.py` (the pre-push hook already covers every `code/projects/<folder>/`).

## Git rules

- The links are **local state**, never tracked: they are excluded by `.git/info/exclude` (`/code/projects/*`) and by `.gitignore` (`.agents/`, `/.obsidian`).
- A junction cannot be stored in a git tree, and a symlink stored in git only survives a Windows checkout when `core.symlinks=true` and Developer Mode is enabled. Tracking them would give a different tree on each OS. The manifest is the tracked artefact, the links are generated.
- The `private` scope means the link target is personal content: it must never reach the `public` branch (see [`007_mixing_public_and_private_history.md`](007_mixing_public_and_private_history.md)).

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `unresolved` for a project link | The key is missing from the `links` section of `_Private/.config/user_config.jsonc`, or it has no entry for the current OS. | Add the `windows` / `linux` / `default` entry. |
| `drift` after a move | The link points to the old location. | `--apply` (it replaces the link, never the content). |
| `drift` mentioning "this host expects a junction" | The link was created on the other OS (symlink on Windows, or the reverse). | `--apply` (or the `[LINKS] Sync` task) rebuilds it with the right primitive. |
| `conflict` | A real folder sits where the link should be. | Move or rename the folder, then `--apply`. |
| `broken` | The target folder was deleted or moved. | Fix the path in the config, then `--apply`. |
| The link exists but Windows cannot open it | The link was created with a POSIX target (`/mnt/d/...`) by an older manual setup. | `--apply` replaces it with a native junction. |
| `mklink` fails on a network target | Junctions only support local paths. | The generator falls back to a symbolic link; enable Developer Mode if the fallback also fails. |

## Cross-references

- [`007_mixing_public_and_private_history.md`](007_mixing_public_and_private_history.md) - what stays private and how the public branch is rebuilt.
- [`008_tasks_and_launch_wiring.md`](008_tasks_and_launch_wiring.md) - how the launch configs consume `code/projects/<name>`.
- `_Helpers/scripts/README - scripts.md` - the script inventory.
- [`../templates/user_config.example.jsonc`](../templates/user_config.example.jsonc) - the `links` section template.
- [`../links.jsonc`](../links.jsonc) - the manifest.
