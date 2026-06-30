---
title: "YAML Frontmatter - Simplified conventions"
date: 2026-06-29
tags: [OdinRAG, convention, 500_classification, planning]
type: reference
status: active
priority: 1
docId: NAV_FM_001
---

# YAML Convention - Frontmatter

**Goal**: standardise a minimal frontmatter, **Obsidian-compatible**, sufficient for RAG indexing (Kilo + LLM) without the complexity of TerraBloom (32+ hierarchical tags, `completion_*`, etc.).

> For the full (reference) version, see the TerraBloom project.
> For this project, we keep **5 main fields + Obsidian hierarchical tags**.

## Recommended fields

| Field      | Format                  | Example                           | Required?                 |
| ---------- | ----------------------- | --------------------------------- | ------------------------- |
| `title`    | string                  | `"Daily 2026-06-28 - Kilo setup"` | yes for personal notes    |
| `date`     | ISO 8601 (`YYYY-MM-DD`) | `2026-06-28`                      | yes everywhere            |
| `tags`     | array                   | `[OdinRAG, planning, daily]`      | yes everywhere            |
| `type`     | enum (see list)         | `daily`                           | if applicable             |
| `status`   | enum (see list)         | `active`                          | if applicable             |
| `priority` | 1-3                     | `2`                               | optional                  |
| `docId`    | string                  | `NAV_FM_001`                      | except for reference docs |

**Obsidian note**: Obsidian ignores fields it doesn't recognize and displays those it knows (`tags`, `aliases`, `cssclass`). Custom fields (`priority`, `docId`, etc.) don't break anything.

## Types (`type`)

List reduced to the essentials for this project:

| Value       | Usage                                                |
| ----------- | ---------------------------------------------------- |
| `note`      | Free note, brainstorm, thought                       |
| `daily`     | Daily note (`J_YYYY-MM-DD`)                          |
| `weekly`    | Weekly review (`W_YYYY-WW`)                          |
| `monthly`   | Monthly review (`M_YYYY-MM`)                         |
| `roadmap`   | Action plan, milestones (e.g. `planning/ROADMAP.md`) |
| `reference` | Cheatsheet, stable doc (conventions, index)          |
| `dev_log`   | Per-project devlog (`code/projects/<p>/devlog/`)     |
| `archive`   | Saved for history, no longer edited                  |
| `template`  | Document template (used as a base to create)         |

## Statuses (`status`)

| Value        | Usage                                    |
| ------------ | ---------------------------------------- |
| `draft`      | Draft, not finalised                     |
| `active`     | In use / kept up to date                 |
| `done`       | Completed                                |
| `archived`   | History kept (no longer actively edited) |
| `deprecated` | Obsolete, do not use                     |

## Tags - nomenclature (Obsidian-compatible)

### Root project tag

- `OdinRAG` - present in **all** project documents (acts as a filter).

### Domain tags (1-2 per doc)

- `odin` - Odin code (`.odin` or `odin` blocks)
- `kb` - knowledge base (Skool lessons, scraped docs)
- `planning` - roadmap, daily, weekly
- `devlog` - personal dev journal
- `ragnarok` - reference to the VSCode extension (if used later)
- `kilo` - Kilo config files (`.kilo/`, `kilo.json`, etc.)
- `scraper` - `_Helpers/` scrape scripts
- `doc` - general documentation (READMEs, AGENTS.md, etc.)

### Source tags (KB only)

Format: `source/<name>` (Obsidian hierarchical)

- `source/skool` - Skool programvideogames lesson
- `source/official` - odin-lang.org/docs/
- `source/zylinski` - zylinski.se blog

### Topic tags (Skool KB + devlog)

Format: `topic/<concept>` (Obsidian hierarchical)

- `topic/allocator` - allocators (arena, tracking, virtual, SoA)
- `topic/state-machine` - FSM, state transitions
- `topic/entity-system` - ECS, entity, component
- `topic/collision` - 2D/3D collisions
- `topic/hot-reload` - DLL hot reload
- `topic/rendering` - Raylib/Sokol draw
- `topic/raylib` - Raylib specific
- `topic/sokol` - Sokol specific
- `topic/dod` - data-oriented design
- `topic/wasm` - WebAssembly
- `topic/binding` - c-bindgen, vendor:xxx

### Status tags (optional, for tasks/planning)

Format: `status/<state>` (hierarchical)

- `status/active`
- `status/done`
- `status/backlog`
- `status/blocked`

### Project phase tags (planning)

Format: `phase/<num>` (relative to project start, not calendar date)

- `phase/P1` - phase 1 (KB initialisation + setup)
- `phase/P2` - phase 2 (first Odin project)

For daily milestones: `J1`, `J2`, `J3`... (relative to the first daily entry of the phase, or absolute `J_2026-06-28`).

## Strict rules

1. **No `#` in YAML values**: `tags: [odin]` ok, `tags: ["#odin"]` wrong
2. **Double quotes** for `title`, `date`, `priority` (string values):

   ```yaml
   title: "My title with : and /"
   date: 2026-06-28
   ```

3. **ISO dates**: `YYYY-MM-DD` (not `28/06/2026`, not `June 28 2026`).
4. **No spaces in tags**: `topic/raylib` ok, `topic/ray lib` wrong
5. **Hierarchical tags count as 1**: `topic/allocator` = 1 tag, not 2.
6. **Maximum 2 hierarchical levels**: `topic/raylib` ok, `topic/gamedev/raylib` wrong
7. **Lowercase** by default. Uppercase only for proper names: `OdinRAG`, `Skool`.

## Example documents from the project

### Planning note (daily)

```markdown
---
title: "Daily 2026-06-28 - Kilo setup"
date: 2026-06-28
tags: [OdinRAG, planning, daily, kilo, status/active]
type: daily
status: active
---

# Daily 2026-06-28 - Kilo setup

## Goal of the day

- [x] Create AGENTS.md
- [x] Create kilo.json
- [ ] Set up .kilo/skills/

## Progress

...

## Next

...
```

### Skool lesson (KB)

```markdown
---
title: "2.21 - Sound Effects and Music"
date: 2026-06-23
tags: [OdinRAG, kb, source/skool, topic/audio]
type: note
status: archived # KB frozen
Cours: "Vertical Slice and Dice v1.0"
Module: "Metroidvania"
ID: "a66b2d6f77754bb899ca671d1d9653bf"
Durée: 5.01 min
---
```

### Reference doc (AGENTS.md, conventions)

```markdown
---
title: "AGENTS.md - Project context"
date: 2026-06-28
tags: [OdinRAG, doc, kilo, reference]
type: reference
status: active
priority: 1
docId: NAV_AGENTS
---
```

## What we DON'T use (vs TerraBloom)

To stay simple, we don't use:

- `completion_read` / `completion_todo` / `completion_steps` -> use a simple `- [ ]` markdown list inside the body.
- Numeric prefixes `100_planning`, `300_setup` -> use hierarchical tags `phase/P1`, `topic/allocator`, etc.
- `version`, `lastUpdated`, `updatedBy` -> git history is enough.
- Obsidian `aliases` -> add them ad-hoc if needed.

## Quick validation

To verify a frontmatter is compliant:

```bash
# List of tags used (should be small and stable)
grep -rh "^tags:" --include="*.md" | sort -u

# Files without frontmatter (probably READMEs - OK)
for f in $(find . -name "*.md" -not -path "./node_modules/*"); do
  head -1 "$f" | grep -q "^---" || echo "NO FM: $f"
done
```

## Anti-patterns

- Tag with `#` inside the YAML value (Obsidian removes it from indexing)
- Mixing English and French for tags (`planification` AND `planning`)
- Date in `28/06/2026` format (not ISO)
- 3+ level hierarchy (`topic/gamedev/raylib/2d`)
- Frontmatter different from the model above without a documented reason
