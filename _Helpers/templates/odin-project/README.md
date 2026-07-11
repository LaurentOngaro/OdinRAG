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

### Where to put the devlog

Two options, pick one and stay consistent for the project's lifetime:

| Location                                                                                                                                                                              | Privacy model                                                    | Pros                                                                                             | Cons                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `code/projects/<project>/devlog/`                                                                                                                                                     | Private **by inheritance** (parent folder is private)            | Same folder as the code, natural locality.                                                       | Privacy is implicit; if the project ever goes public, the devlog leaks with it. |
| `_Private/devlogs/<project>/`                                                                                                                                                         | Private **explicit at the path** (`_Private/` is always private) | Survives any future decision to publish the project code; aligned with dailies, raw notes, ADRs. | Two hops to navigate between code and devlog; lose `Ctrl+P` locality.           |
| Recommended default for new projects: **`_Private/devlogs/<project>/`** (privacy by location, not by association). See `_Private/docs/003_devlog_location.md` for the full rationale. |

If you keep the devlog in `code/projects/<project>/devlog/`, no change is required - it still works because the parent `code/projects/` is already absent from the public branch. The migration to `_Private/` is optional and reversible.

## How to run

```bash
# From the repo root:
cd code/projects/<project>
ls src/                         # see the sources
cat AGENTS.md                   # context for the AI

# Devlog (legacy location, in the project):
cat devlog/J_*.md | head -50    # history

# Devlog (preferred location, in _Private/):
cat /_Private/devlogs/<project>/J_*.md | head -50    # history
```

> **Note**:
> this repo does NOT compile. To test the Odin code on your machine, copy the files from `src/` into a real Odin project (with `odin` on the PATH) and use `odin run .`.
