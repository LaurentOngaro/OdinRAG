---
name: kb-navigator
description: "Search the OdinRAG KB (odin-knowledge-base + docs/ + code/) by topic, frontmatter, keyword, or module. Returns precise file paths with context (module, duration, source)."
---

# Navigate the OdinRAG KB

Skill for querying the OdinRAG knowledge base. The KB is composed of three corpora (one per source). Volumes depend on what you have scraped locally:

| Corpus                                              | Volume       | Source                           | Required?                  |
| --------------------------------------------------- | ------------ | -------------------------------- | -------------------------- |
| `odin-knowledge-base/`                              | TBD lessons  | Skool programvideogames          | Optional (paid membership) |
| `odin-knowledge-base/docs/official/`                | TBD pages    | odin-lang.org/docs/              | Free, public               |
| `odin-knowledge-base/docs/karl_zylinski/`           | TBD articles | zylinski.se                      | Free, public               |
| `odin-knowledge-base/docs/karl_zylinski/odin-book/` | TBD chapters | Book "Understanding Odin" (Karl) | Optional (paid ebook)      |
| `odin-knowledge-base/docs/gingerbill/`              | TBD articles | gingerbill.org                   | Free, public               |
| `odin-knowledge-base/docs/jakubtomsu/`              | TBD articles | jakubtomsu.github.io             | Free, public               |
| `odin-knowledge-base/docs/marianpekar/`             | 21 articles  | marianpekar.com                  | Free, public               |

> `TBD` means "regenerate after each scrape via `python _Helpers/scripts/indexing/build_kb_index.py`".
> See [`../../odin-knowledge-base/INDEX.md`](../../odin-knowledge-base/INDEX.md) for the live counts in your local checkout.
>
> **YAML convention**: see [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](../../_Helpers/docs/003_yaml_frontmatter_conventions.md) for the full nomenclature (hierarchical tags `topic/*`, `source/*`, `phase/*`).
> The filters below rely on these conventions.
>
> **REFERENCE BOOK** (once split via `_Helpers/scripts/fixes/book_html_to_md.py`):
> [`odin-knowledge-base/docs/karl_zylinski/odin-book/`](../../odin-knowledge-base/docs/karl_zylinski/odin-book/README.md)
> contains the full book "Understanding the Odin Programming Language" split into per-chapter MD files (numbered chapters + appendices + about-the-author).
> Many Odin code examples. For any **fundamental question about the Odin language**, start here.

## When to invoke

- The user wants an Odin pattern (state machine, allocator, etc.).
- The user asks for a code example on a specific topic.
- The user wants to compare several lessons on the same concept.
- The user wants to list the lessons of a module or filter by tag.

## Step 0: ALWAYS load the central INDEX first

Before any KB search, read [`odin-knowledge-base/INDEX.md`](../../odin-knowledge-base/INDEX.md) (~5 KB).

This file contains:

- **Big-picture view by source** (how many files in each corpus)
- **Index by topic** - for 11 common topics (allocators, FSM, entity, hot reload, etc.) with 1-5 pre-curated relevant files
- **Table of contents of Karl's book chapters** (28 + appendices)
- **Statistics**

If the requested topic is in the INDEX -> load the listed files directly. If the topic is NOT listed -> fall back to grep (Step 3).

> **Rule**: never load the whole KB. Always go through the INDEX first.

## Quick filters by tag

Skool lessons can be filtered by Obsidian **hierarchical tag**:

| Filter                           | Command                                                               |
| -------------------------------- | --------------------------------------------------------------------- |
| All allocator lessons            | `grep -lr "topic/allocator" odin-knowledge-base/`                     |
| Skool lessons on FSM             | `grep -lr "topic/state-machine" odin-knowledge-base/`                 |
| Official Odin lessons (language) | `grep -lr "source/official" odin-knowledge-base/docs/official/`       |
| Karl Zylinski articles           | `grep -lr "source/zylinski" odin-knowledge-base/docs/karl_zylinski/`  |
| Marian Pekar from-scratch series | `ls odin-knowledge-base/docs/marianpekar/` (renderer, physics, cloth) |
| Whole KB for one topic           | `grep -rli "topic/raylib" odin-knowledge-base/`                       |

## Search strategy

### Step 1: identify the relevant corpus

```
Question on Odin itself (syntax, types)        ->  odin-knowledge-base/docs/official/
Question on gamedev / specific patterns         ->  odin-knowledge-base/
Question on allocators / hot reload / DOD       ->  odin-knowledge-base/docs/karl_zylinski/
Question on rendering / physics from scratch    ->  odin-knowledge-base/docs/marianpekar/
Question on Raylib/Sokol (template setup)       ->  code/vendored templates/ + KB
```

### Step 2: filter by frontmatter (Skool KB)

Each Skool lesson has a YAML-like frontmatter:

```yaml
---
Cours: "Vertical Slice and Dice v1.0"
Module: "Metroidvania"
ID: "a66b2d6f77754bb899ca671d1d9653bf"
Durée: 7.0 min
---
```

Useful filters:

- `Module: "Metroidvania"` -> all lessons in the metroidvania module
- `Module: "RPG"` -> all RPG lessons
- `Durée: 7.0 min` -> short lessons (useful for a quick draft)

### Step 3: grep inside contents

```bash
# Odin pattern in the whole KB
grep -ri "context.allocator" odin-knowledge-base/ docs/

# Hot reload (all sources)
grep -ri "hot.reload\|hot_reload\|hotreload" odin-knowledge-base/ odin-knowledge-base/docs/karl_zylinski/

# Tracking allocator
grep -ri "tracking_allocator\|Tracking_Allocator" odin-knowledge-base/
```

### Step 4: cite the context

Always return the **relative path** + the **module** in the response:

```text
-> odin-knowledge-base/courses/programvideogames/the-course-is-here/metroidvania/211-Finite State Machine - Movement.md
  Module: Metroidvania, Durée: 6.24 min
```

## Frequent Odin patterns (where to look)

| Pattern               | Key files (relative paths)                                                                                                                                                                                  |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Allocators            | `odin-knowledge-base/docs/karl_zylinski/temporary-allocator-your-first-arena.md`,`odin-knowledge-base/.../introduction/007-Text Rendering and Memory Allocators.md`,`.../rpg/088-26. Tracking Allocator.md` |
| State machine (FSM)   | `odin-knowledge-base/.../metroidvania/211-Finite State Machine - Movement.md`,`odin-knowledge-base/.../metroidvania/212-Attacking.md`                                                                       |
| Entity system         | `odin-knowledge-base/.../metroidvania/205-Entities, State, Physics Update.md`,`odin-knowledge-base/.../metroidvania/208-Enemy Behaviors.md`,`.../rpg/067-05. Entity System.md`                              |
| Hot reload (DLL)      | `odin-knowledge-base/docs/karl_zylinski/hot-reload-gameplay-code.md`,`odin-knowledge-base/.../rpg/084-22. Hot Reloading.md`,`odin-knowledge-base/.../rpg/085-23. Hot Reloading Integration.md`              |
| DOD / SoA             | `odin-knowledge-base/docs/karl_zylinski/odin-dod-benchmarks.md`,`odin-knowledge-base/docs/karl_zylinski/data-oriented-ideas-for-small-gamedev-teams.md`                                                     |
| c-bindgen             | `odin-knowledge-base/docs/karl_zylinski/generate-odin-bindings-for-c-libraries.md`                                                                                                                          |
| Raylib intro          | `odin-knowledge-base/.../introduction/001-Introduction to Odin and Raylib.md`                                                                                                                               |
| WASM / sokol-web      | `odin-knowledge-base/docs/karl_zylinski/odin-sokol-web.md`                                                                                                                                                  |
| Collision 2D          | `odin-knowledge-base/.../introduction/006-Simple Collision Detection and Resolution.md`,`odin-knowledge-base/.../metroidvania/207-Command Buffers - Better Debug Draw.md` (debug draw collision)            |
| Collision 3D          | `odin-knowledge-base/.../rpg/077-15. Detecting 3D Collisions.md`,`odin-knowledge-base/.../rpg/080-18. 3D Collision Response.md`                                                                             |
| Inventory             | `odin-knowledge-base/.../metroidvania/228-Inventory System.md`                                                                                                                                              |
| Save/Load             | `odin-knowledge-base/.../metroidvania/226-Saving and Loading.md`,`odin-knowledge-base/.../rpg/099-37. Saving, Loading, Main Menu.md`                                                                        |
| Dialogue / Quest      | `odin-knowledge-base/.../rpg/101-39. Dialogue Part 1.md`,`odin-knowledge-base/.../rpg/102-40. Dialogue Part 2 - Choices, Events, Quests.md`                                                                 |
| Pathfinding (A\*)     | `odin-knowledge-base/.../rpg/090-28. Navigation System.md`                                                                                                                                                  |
| Procedural generation | `odin-knowledge-base/.../rpg/105-43. Edit Mode First Pass.md`                                                                                                                                               |
| Battle system         | `odin-knowledge-base/.../rpg/093-31. Party System & Battle Resolution.md`,`odin-knowledge-base/.../rpg/094-32. Variable Turn Order.md`                                                                      |
| Procedural dungeon    | `odin-knowledge-base/.../rpg/091-29. NPC Movement Optimisation.md`                                                                                                                                          |
| Level editor          | `odin-knowledge-base/.../metroidvania/231-Level Editor Introduction.md`,`.../metroidvania/235-Zoom, Pan, Level Mode.md`                                                                                     |

## Citation conventions

Always include:

1. **Relative path** from the repo root
2. **Module** (if Skool lesson)
3. **Duration** (if relevant)
4. **Section/heading** (if the content is in a specific section of the file)

Example of a good response:

```text
-> odin-knowledge-base/.../metroidvania/211-Finite State Machine - Movement.md
  Module: Metroidvania
  Section: "The state machine"
  Shows how to define `Entity_State` enum + `switch` in `entity_update`.
```

## Anti-patterns

- Never return just "see the KB" without a precise path.
- Never summarise a file without having read its actual content (the KB contains up-to-date Odin code - always cite it).
- Never ignore the frontmatter (it gives immediate context: module, duration, level).
- Never mix KB and per-project devlog (`_Private/devlogs/<p>/J_*.md` preferred, `code/projects/<p>/devlog/` legacy) - the devlog is user content, not a source.
