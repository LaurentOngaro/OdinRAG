---
name: kb-navigator
description: Search the OdinRAG KB (odin-knowledge-base + docs/ + code/) by topic, frontmatter, keyword, or module. Returns precise file paths with context (module, duration, source).
---

# Navigate the OdinRAG KB

Skill for querying the OdinRAG knowledge base. The KB is composed of three corpora (one per source). Volumes depend on what you have scraped locally:

| Corpus                                              | Volume       | Source                           | Required?                  |
| --------------------------------------------------- | ------------ | -------------------------------- | -------------------------- |
| `odin-knowledge-base/`                              | TBD lessons  | Skool programvideogames          | Optional (paid membership) |
| `odin-knowledge-base/docs/official/`                | TBD pages    | odin-lang.org/docs/              | Free, public               |
| `odin-knowledge-base/docs/karl_zylinski/`           | TBD articles | zylinski.se                      | Free, public               |
| `odin-knowledge-base/docs/karl_zylinski/odin-book/` | TBD chapters | Book "Understanding Odin" (Karl) | Optional (paid ebook)      |

> `TBD` means "regenerate after each scrape via `python _Helpers/scripts/indexing/build_kb_index.py`".
> See [`../../odin-knowledge-base/INDEX.md`](../../odin-knowledge-base/INDEX.md) for the live counts in your local checkout.

> **YAML convention**: see [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](../../_Helpers/docs/003_yaml_frontmatter_conventions.md) for the full nomenclature (hierarchical tags `topic/*`, `source/*`, `phase/*`).
> The filters below rely on these conventions.

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

If the requested topic is in the INDEX -> load the listed files directly.
If the topic is NOT listed -> fall back to grep (Step 3).

> **Rule**: never load the whole KB. Always go through the INDEX first.

## Quick filters by tag

Skool lessons can be filtered by Obsidian **hierarchical tag**:

| Filter                           | Command                                                              |
| -------------------------------- | -------------------------------------------------------------------- |
| All allocator lessons            | `grep -lr "topic/allocator" odin-knowledge-base/`                    |
| Skool lessons on FSM             | `grep -lr "topic/state-machine" odin-knowledge-base/`                |
| Official Odin lessons (language) | `grep -lr "source/official" docs/`                                   |
| Karl Zylinski articles           | `grep -lr "source/zylinski" odin-knowledge-base/docs/karl_zylinski/` |
| Whole KB for one topic           | `grep -rli "topic/raylib" odin-knowledge-base/ docs/`                |

## Search strategy

### Step 1: identify the relevant corpus

```
Question on Odin itself (syntax, types)        ->  odin-knowledge-base/docs/official/
Question on gamedev / specific patterns         ->  odin-knowledge-base/
Question on allocators / hot reload / DOD       ->  odin-knowledge-base/docs/karl_zylinski/
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
-> odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/metroidvania/020-211-finite-state-machine-movement.md
  Module: Metroidvania, Durée: 6.24 min
```

## Frequent Odin patterns (where to look)

| Pattern               | Key files (relative paths)                                                                                                                                                                                 |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Allocators            | `odin-knowledge-base/docs/karl_zylinski/temporary-allocator-your-first-arena.md`,`odin-knowledge-base/.../introduction/007-text-rendering-and-memory-allocators.md`,`.../rpg/088-26-tracking-allocator.md` |
| State machine (FSM)   | `odin-knowledge-base/.../metroidvania/020-211-finite-state-machine-movement.md`,`odin-knowledge-base/.../metroidvania/021-212-attacking.md`                                                                |
| Entity system         | `odin-knowledge-base/.../metroidvania/014-205-entities-state-physics-update.md`,`odin-knowledge-base/.../metroidvania/017-208-enemy-behaviors.md`,`.../rpg/067-05-entity-system.md`                        |
| Hot reload (DLL)      | `odin-knowledge-base/docs/karl_zylinski/hot-reload-gameplay-code.md`,`odin-knowledge-base/.../rpg/084-22-hot-reloading.md`,`odin-knowledge-base/.../rpg/085-23-hot-reloading-integration.md`               |
| DOD / SoA             | `odin-knowledge-base/docs/karl_zylinski/odin-dod-benchmarks.md`,`odin-knowledge-base/docs/karl_zylinski/data-oriented-ideas-for-small-gamedev-teams.md`                                                    |
| c-bindgen             | `odin-knowledge-base/docs/karl_zylinski/generate-odin-bindings-for-c-libraries.md`                                                                                                                         |
| Raylib intro          | `odin-knowledge-base/.../introduction/001-introduction-to-odin-and-raylib.md`                                                                                                                              |
| WASM / sokol-web      | `odin-knowledge-base/docs/karl_zylinski/odin-sokol-web.md`                                                                                                                                                 |
| Collision 2D          | `odin-knowledge-base/.../introduction/006-simple-collision-detection-and-resolution.md`,`odin-knowledge-base/.../metroidvania/016-207-command-buffers-better-debug-draw.md` (debug draw collision)         |
| Collision 3D          | `odin-knowledge-base/.../rpg/077-15-detecting-3d-collisions.md`,`odin-knowledge-base/.../rpg/080-18-3d-collision-response.md`                                                                              |
| Inventory             | `odin-knowledge-base/.../metroidvania/038-228-inventory-system.md`                                                                                                                                         |
| Save/Load             | `odin-knowledge-base/.../metroidvania/036-226-saving-and-loading.md`,`odin-knowledge-base/.../rpg/099-37-saving-loading-main-menu.md`                                                                      |
| Dialogue / Quest      | `odin-knowledge-base/.../rpg/101-39-dialogue-part-1.md`,`odin-knowledge-base/.../rpg/102-40-dialogue-part-2-choices-events-quests.md`                                                                      |
| Pathfinding (A\*)     | `odin-knowledge-base/.../rpg/090-28-navigation-system.md`                                                                                                                                                  |
| Procedural generation | `odin-knowledge-base/.../rpg/105-43-edit-mode-first-pass.md`                                                                                                                                               |
| Battle system         | `odin-knowledge-base/.../rpg/093-31-party-system-battle-resolution.md`,`odin-knowledge-base/.../rpg/094-32-variable-turn-order.md`                                                                         |
| Procedural dungeon    | `odin-knowledge-base/.../rpg/091-29-npc-movement-optimisation.md`                                                                                                                                          |
| Level editor          | `odin-knowledge-base/.../metroidvania/041-231-level-editor-introduction.md`,`.../metroidvania/045-235-zoom-pan-level-mode.md`                                                                              |

## Citation conventions

Always include:

1. **Relative path** from the repo root
2. **Module** (if Skool lesson)
3. **Duration** (if relevant)
4. **Section/heading** (if the content is in a specific section of the file)

Example of a good response:

```text
-> odin-knowledge-base/.../metroidvania/020-211-finite-state-machine-movement.md
  Module: Metroidvania
  Section: "The state machine"
  Shows how to define `Entity_State` enum + `switch` in `entity_update`.
```

## Anti-patterns

- Never return just "see the KB" without a precise path.
- Never summarise a file without having read its actual content (the KB contains up-to-date Odin code - always cite it).
- Never ignore the frontmatter (it gives immediate context: module, duration, level).
- Never mix KB and per-project devlog (`code/projects/<p>/devlog/`) - the devlog is user content, not a source.
