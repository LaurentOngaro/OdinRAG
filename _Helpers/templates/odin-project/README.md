---
title: "Odin project template - README"
date: 2026-07-01
tags: [OdinRAG, template, odin-project, reference]
type: template
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# README

> One sentence describing this project in 2-30 words. e.g. "Top-down 2D RPG with Raylib - entity system, arena allocator, hot-reload DLL."

## Status

- **Phase**: _idea_ / _exploration_ / _prototype_ / _production_
- **Stack**: Odin + Raylib / Sokol / etc.
- **KB inspiration**: 1-3 references to `odin-knowledge-base/` or `docs/`

## KB inspirations (precise references)

Fill in with the exact paths of the lessons/chapters that inspired this project.
Examples:

- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/rpg/067-05-entity-system.md` (entity component pattern)
- `odin-knowledge-base/docs/karl_zylinski/odin-book/13-making-manual-memory-management-easier.md` (arena allocator)
- `odin-knowledge-base/docs/official/overview.md` (language reference)

## Folder layout (target project)

Files shipped in this template (clone + rename the project root):

```
_Helpers/templates/odin-project/
├── README.md                              <- this file
├── AGENTS.md                              <- context for Kilo (patterns used, pitfalls)
├── src/main.odin                          <- minimal Odin entry point
├── devlog/J_TEMPLATE.md                   <- template for a daily devlog entry
└── .kilo/agents/odin-project.md           <- optional PVG subagent
```

When cloned into `code/projects/<project>/`, the target structure becomes:

```
<project>/
├── README.md              <- edited copy of this file
├── AGENTS.md              <- edited copy of the template AGENTS
├── src/                   <- Odin code (.odin sources)
├── devlog/                <- session history (J_YYYY-MM-DD_<topic>.md)
└── .kilo/agents/          <- optional subagent for this project
```

## How to run

```bash
# From the repo root:
cd code/projects/<project>
ls src/                         # see the sources
cat AGENTS.md                   # context for the AI
cat devlog/J_*.md | head -50    # history
```

> **Note**:
> this repo does NOT compile. To test the Odin code on your machine, copy the files from `src/` into a real Odin project (with `odin` on the PATH) and use `odin run .`.
