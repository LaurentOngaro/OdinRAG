---
title: "OdinRAG Roadmap - Phases and milestones"
date: 2026-06-30
tags: [OdinRAG, planning, roadmap, reference]
type: roadmap
status: active
priority: 1
---

# OdinRAG Roadmap

> Status as of **2026-06-30, post-recreate-from-scratch** (public repo now in its initial release at
> [github.com/LaurentOngaro/OdinRAG](https://github.com/LaurentOngaro/OdinRAG)).
> For operational day-to-day notes, see the dailies in [`planning/daily/`](./daily/) (gitignored).
> For the daily format: [`planning/template/J_YYYY-MM-DD.md`](./template/J_YYYY-MM-DD.md).

## Overview

| Phase                           | Status | Goal                                                                               | Target period           |
| ------------------------------- | ------ | ---------------------------------------------------------------------------------- | ----------------------- |
| **P0** Setup                    | done   | Initial KB populated (scrape the sources listed in [SOURCES.md](../../SOURCES.md)) | 2026-06-19 → 2026-06-23 |
| **P1** Toolbox                  | done   | Maintenance tools (format, scraping re-entry, public-safety audit)                 | 2026-06-28 → 2026-06-29 |
| **P2** KB polish                | done   | Public release ready (hybrid conservative samples, coherence audit, M3 promo)      | 2026-06-29 → 2026-06-30 |
| **P3** Templates + bindings     | done   | Clone upstream templates, integrate gists                                          | 2026-06-30              |
| **P4** First Odin project (RPG) | active | Remake of module 2 (RPG) of the PVG course                                         | TBD                     |

> Status values: `TBD` (not started), `active` (in progress), `done` (completed), `backlog` (deferred).

## P0 - Setup

### Goal

Populate the KB with the sources you want to curate (see [SOURCES.md](../../SOURCES.md)).

### Milestones

- [x] Run `python _Helpers/scrape-official.py` to pull `odin-lang.org/docs/`
- [x] Run `python _Helpers/scrape-zylinski.py` to pull `zylinski.se` articles
- [x] (Optional, requires paid membership) Run `python _Helpers/scrape_skool.py`
- [x] (Optional, requires the HTML ebook) Run `python _Helpers/book_html_to_md.py`
- [x] Run `python _Helpers/build_kb_index.py` to regenerate `odin-knowledge-base/INDEX.md`

## P1 - Toolbox

### Goal

Put in place the tools that make the KB **maintainable** and **queryable** by Kilo + future agents, and the safety nets to push it publicly without leaking copyrighted content.

### Milestones

- [x] Read `_Helpers/docs/PUBLIC_RELEASE_CHECKLIST.md` before any private → public transition (used 3 times: initial release, blog trim, /devlog/ removal)
- [x] `_Helpers/audit_public_safety.py` exit 0 before each public push
- [x] `_Helpers/lint_pylance.py` zero diagnostics on tracked `.py` files (added pylance-check skill + MAX_VIDEO_RETRIES + SKOOL constant fix)
- [x] `_Helpers/reflow_md.py` available for "book style" line reflow

> Note: the original item "Add frontmatter to your daily notes" was dropped - dailies are gitignored personal logs that don't need frontmatter. The convention in
> [`FRONTMATTER_CONVENTIONS.md`](../_Helpers/docs/FRONTMATTER_CONVENTIONS.md) is reserved for tracked KB files.

## P2 - KB polish

### Goal

Make the public repo ready for the MiniMax-M3 Showcase Round 2 and any future external reader.
The repo must be **minimal and self-explanatory**: no personal data, no copyrighted bulk, no progression markers.

### Milestones

- [x] Hybrid-conservative trim: `docs/{karl_zylinski,gingerbill,jakubtomsu}/` ship 5+5+4 sample articles each (full corpus reproducible via scrapers)
- [x] All scraped content kept locally is properly listed in [SOURCES.md](../../SOURCES.md) with `©` + "how to obtain" link
- [x] `_Helpers/docs/ACTION_PLAN.md` + `LEARNING_PLAN_ODIN_GAMEDEV_2026.md` translated to English (no French strings left in tracked files)
- [x] `.kilo/skills/` (6 skills) and `.kilo/agents/odin-gamedev.md` finalised with citation discipline
- [x] Coherence audit: `audit_public_safety.py` + `lint_pylance.py` both clean on tracked files
- [x] `_Helpers/docs/social/{REDDIT_POST.md, TWITTER_THREAD.md, DISCORD_NOTE.md}` ready for the showcase (posted on 2026-06-30)

> Items **not applicable** (intentionally removed from this phase):
>
> - "Index Skool modules in main README.md" - Skool content is paywall + gitignored, indexing it publicly would expose links to paid material. Stays local in `odin-knowledge-base/`.
> - "Add summary + topic/\* to every Skool lesson" - same reason: applies only to local KB.

## P3 - Templates + bindings

### Goal

Have the upstream Odin templates and useful gists available locally for cloning into future projects.

### Milestones

- [x] Clone Karl's hot-reload templates into `code/templates/` (Raylib + Sokol, native + Web)
- [x] Download priority gists into `code/gists/` (25 gists from awesome-odin)
- [x] `code/templates/*/` and `code/gists/` gitignored so local clones cannot be accidentally committed
- [ ] Test `c-bindgen` on a small C library (Box2D or FreeType) - **backlog, low priority for P4**
- [ ] First WASM build with Sokol - **backlog, low priority for P4**

> Note: `code/gists/` and `code/examples/` (demo.odin + others) are downloader targets - they contain code from external sources and are kept gitignored.
> The README in each subfolder explains how to populate them locally via `_Helpers/download_gists.py` / `_Helpers/download_odin_examples.py`.

## P4 - First Odin project: Remake of module 2 (RPG) of the PVG course

### Goal

Reimplement from scratch the RPG module of the programvideogames course. This is a **pedagogical remake**, not a new game: scope, mechanics and progression follow the course's lesson plan so the KB (Skool lessons + Karl book + Odin official docs) drives every design choice.

### Where the project lives

- Source: `code/projects/_TEMPLATE_/` (public scaffold in this repo)
- Actual code: clone `_TEMPLATE_/` to a **gitignored** path (e.g. `D:\OdinProjects\rpg-remake\`).
  See [`code/projects/INTEGRATION.md`](../../code/projects/INTEGRATION.md) for the full convention.

### Why this project (and not the default "iterate state machine + tracking allocator")

The default P5 was too generic for the actual goal. The PVG module 2 RPG covers a much wider scope than a state-machine demo - see the phase breakdown below.

### P4.0 - Préparation (1-2 sessions)

- [x] List the ~42 lessons of module 2 (RPG) in `odin-knowledge-base/courses/programvideogames/`
- [ ] One recap note per lesson in `code/projects/rpg-remake/devlog/` (the per-project devlog)
- [ ] Plan target architecture (file structure, modules, deps) in the project's AGENTS.md
- [ ] Clone `_TEMPLATE_/` to a gitignored project location
- [ ] Wire Kilo to load this project's `AGENTS.md` as the priority context (per `kb-navigator` workflow)

### P4.1 - Foundation (3-4 sessions)

- [ ] Character system (stats, classes, level-up, equipment slots) - references: KB lesson 067 + Karl 5/13
- [ ] Inventory system (items, equipment, stacking) - references: KB lesson 038 (inventory)
- [ ] State machine for character states (idle / moving / attacking / dead) - references: KB lessons 020 + 021
- [ ] Tracking allocator wired in debug builds only - references: KB lesson 088
- [ ] Arena for per-frame allocations - references: Karl chapters 13 + zylinski temporary-allocator article

### P4.2 - Core RPG (4-6 sessions)

- [ ] Turn-based combat system with party + variable turn order - references: KB lesson 093
- [ ] NPC + dialogue tree - references: KB lesson 101 + 102
- [ ] Quest system (objectives, rewards, state machine) - references: KB lessons on FSM + a few KB items
- [ ] Save / load (binary, versioned) - references: KB lessons 036, 099
- [ ] UI: HUD + main menu + inventory screen - references: KB intro to Raylib drawing

### P4.3 - Polish + shipping (2-3 sessions)

- [ ] Functional DLL hot reload iteration cycle - references: KB lessons 084 + 085, Karl hot-reload article
- [ ] Battle UI polish (feedback, animations, sound)
- [ ] Performance profiling: Tracy bindings + mini allocator for hot paths
- [ ] First WASM build (stretch - uses Sokol, optional)
- [ ] Final cleanup, README, release notes

## Update conventions

- **Daily**: create/update `planning/daily/J_YYYY-MM-DD.md` (gitignored)
- **Per phase**: tick the milestones in this file as you go
- **No empty daily**: if there is nothing to do on a day, do not create the file
- **No retroactive dating**: do not create a daily for the past except for catch-up
- **Per-project devlog** (not the repo's): use `code/projects/<your-project>/devlog/J_YYYY-MM-DD_<topic>.md` for project-specific notes (the public `_TEMPLATE_/devlog/J_TEMPLATE.md` is the starter).

## Useful links

- `planning/daily/` - daily notes (gitignored)
- `planning/template/J_YYYY-MM-DD.md` - template to duplicate
- [`_Helpers/docs/FRONTMATTER_CONVENTIONS.md`](../_Helpers/docs/FRONTMATTER_CONVENTIONS.md) - YAML frontmatter convention
- [`_Helpers/docs/MINIMAX_M3.md`](../_Helpers/docs/MINIMAX_M3.md) - how MiniMax-M3 powered this project
- `_Helpers/docs/social/` - Reddit + X drafts (already published on 2026-06-30)
- [`../../SOURCES.md`](../../SOURCES.md) - how to obtain each scraped source
- [`../../code/projects/INTEGRATION.md`](../../code/projects/INTEGRATION.md) - project-code privacy convention
- [`../../TODO.md`](../../TODO.md) - technical backlog (legacy, migrate as needed)
