# <PROJECT_NAME>

> One sentence describing this project in 2-30 words. e.g. "Top-down 2D RPG with Raylib - entity system, arena allocator, hot-reload DLL."

## Status

- **Phase**: _idea_ / _exploration_ / _prototype_ / _production_
- **Stack**: Odin + Raylib / Sokol / etc.
- **KB inspiration**: 1-3 references to `odin-knowledge-base/` or `docs/`

## KB inspirations (precise references)

Fill in with the exact paths of the lessons/chapters that inspired this project.
Examples:

- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/rpg/067-05-entity-system.md` (entity component pattern)
- `docs/karl_zylinski/odin-book/13-making-manual-memory-management-easier.md` (arena allocator)
- `docs/official/overview.md` (language reference)

## Folder structure

```
<project>/
├── README.md              <- this file
├── AGENTS.md              <- context for Kilo (patterns used, pitfalls)
├── src/                   <- Odin code (.odin sources)
├── devlog/                <- session history (J_YYYY-MM-DD_<topic>.md)
└── .kilo/agents/          <- optional subagent for this project
```

## How to run

```bash
# From the repo root:
cd code/projets/<project>
ls src/                         # see the sources
cat AGENTS.md                   # context for the AI
cat devlog/J_*.md | head -50    # history
```

> **Note**:
> this repo does NOT compile. To test the Odin code on your machine, copy the files from `src/` into a real Odin project (with `odin` on the PATH) and use `odin run .`.
