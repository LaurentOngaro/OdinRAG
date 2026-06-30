---
title: "OdinRAG Roadmap - Phases and milestones"
date: YYYY-MM-DD
tags: [OdinRAG, planning, roadmap, reference]
type: roadmap
status: active
priority: 1
---

# OdinRAG Roadmap

> Phased planning scaffold. Fill in your own phases and milestones as the project evolves. For operational detail, see the dailies in:
> [`planning/daily/`](./daily/) (gitignored). For the daily format:
> [`planning/template/J_YYYY-MM-DD.md`](./template/J_YYYY-MM-DD.md).

## Overview

| Phase                       | Status | Goal                                                                               | Target period |
| --------------------------- | ------ | ---------------------------------------------------------------------------------- | ------------- |
| **P0** Setup                | TBD    | Initial KB populated (scrape the sources listed in [SOURCES.md](../../SOURCES.md)) | TBD           |
| **P1** Toolbox              | TBD    | Maintenance tools (format, scraping re-entry, public-safety audit)                 | TBD           |
| **P2** KB polish            | TBD    | Semantic indexing, mature KB-navigator, standardised frontmatter                   | TBD           |
| **P3** First project        | TBD    | Start a real Odin project (gamedev) using the KB                                   | TBD           |
| **P4** Templates + bindings | TBD    | Clone upstream templates, integrate gists, first WASM build                        | TBD           |

> Status values: `TBD` (not started), `active` (in progress), `done`
> (completed), `backlog` (deferred).
> Target period is whatever you decide; "TBD" is the initial value.

## P0 - Setup

### Goal

Populate the KB with the sources you want to curate (see [`../../SOURCES.md`](../../SOURCES.md)).

### Milestones

- [ ] Run `_Helpers/scrape-official.py` to pull `odin-lang.org/docs/`
- [ ] Run `_Helpers/scrape-zylinski.py` to pull `zylinski.se` articles
- [ ] (Optional, requires paid membership) Run `_Helpers/scrape_skool.py`
- [ ] (Optional, requires the HTML ebook) Run `_Helpers/book_html_to_md.py`
- [ ] Run `python _Helpers/build_kb_index.py` to regenerate `odin-knowledge-base/INDEX.md`

## P1 - Toolbox

### Goal

Put in place the tools that make the KB **maintainable** and **queryable** by Kilo + future agents.

### Milestones

- [ ] Read `_Helpers/docs/PUBLIC_RELEASE_CHECKLIST.md` before any private -> public transition
- [ ] Add frontmatter to your daily notes (see `_Helpers/docs/FRONTMATTER_CONVENTIONS.md`)
- [ ] Pick a phase-1 milestone cadence that matches your workflow

## P2 - KB polish

When P1 is done:

- [ ] Index the Skool modules in the main `README.md`
- [ ] Cross the Odin topics (state-machine, allocators, etc.) between `docs/` and the KB
- [ ] Add `summary` + `topic/*` to every Skool lesson (batch script if needed)
- [ ] Validate the inventory: all READMEs up to date (coherence rule)
- [ ] Decide if RAGnarok becomes necessary (measure Kilo latency)

## P3 - First Odin project

Ideally, **clone one of the templates** in `code/templates/odin-*-hot-reload/` then start the project elsewhere (not in this repo).

Pedagogical goals (adapt to your project):

- [ ] Iterate on a state machine
- [ ] Integrate a tracking allocator (debug only)
- [ ] Functional DLL hot reload
- [ ] First game prototype (any scope)

## P4 - Templates and bindings

- [ ] `git clone` upstream templates into `code/templates/`
- [ ] Download the priority gists into `code/gists/`
- [ ] Test c-bindgen on a small C library
- [ ] First WASM build with sokol

## Update conventions

- **Daily**: create/update `planning/daily/J_YYYY-MM-DD.md` (gitignored)
- **Per phase**: tick the milestones in this file as you go
- **No empty daily**: if there is nothing to do on a day, do not create the file
- **No retroactive dating**: do not create a daily for the past except for catch-up

## Useful links

- `planning/daily/` - daily notes (gitignored)
- `planning/template/J_YYYY-MM-DD.md` - template to duplicate
- `_Helpers/docs/FRONTMATTER_CONVENTIONS.md` - YAML convention
- `TODO.md` - technical backlog
- [`../../SOURCES.md`](../../SOURCES.md) - where to obtain each scraped source
