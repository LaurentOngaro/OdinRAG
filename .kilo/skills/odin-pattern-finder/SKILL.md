---
name: odin-pattern-finder
description: Find a precise Odin pattern (state machine, allocator, hot reload, etc.) by cross-referencing the Skool KB + Karl's book + Zylinski articles. Returns at most 2-4 files, ordered by relevance, with code excerpts.
---

# odin-pattern-finder

Skill for finding a **precise Odin pattern** in the knowledge base, without loading everything. Returns the 2-4 most relevant files with a key code excerpt.

## When to invoke

- The user wants to know **how to implement X in Odin** (state machine, allocator, hot reload, etc.)
- The user has a specific problem ("how to do a tracking allocator", "how to handle errors"...)
- The user wants to **compare** several approaches (arena vs heap, SoA vs AoS) - The user wants **code examples** for a pattern, not just a conceptual explanation

## Search strategy

### Step 1: read the central INDEX

**ALWAYS read [`odin-knowledge-base/INDEX.md`](../../odin-knowledge-base/INDEX.md) first** (~5 KB).
Search in its "Index by topic" section:

- `Memory / allocators` -> files listed
- `State machines (FSM)` -> files listed
- `Hot reload` -> files listed
- etc.

(The exact count per topic depends on your local INDEX - after each `build_kb_index.py` run, the section updates.)

If the topic is listed, **don't run extra greps**: the files are already curated and ordered.

### Step 2: if the topic is NOT in the INDEX

If the request does not match any pre-curated topic, **grep with discriminant**:

```bash
# Topic: "how to handle queues"
grep -rli "queue\|fifo\|ring" odin-knowledge-base/ docs/ 2>/dev/null
# -> lists files containing the pattern
```

Always combine the topic terms with an Odin language term to avoid false positives.

### Step 3: load at most 2-4 files

Once you have a list, pick the 2-4 most relevant **by reading only the frontmatter + the first 100 lines**. If the need is precise (pattern X), search inside the file:

```bash
grep -A 30 "## <pattern title>" <file>
```

### Step 4: return a code excerpt

Always return:

1. **Exact file path** (so Kilo can cite it)
2. **Section/heading** where the pattern is
3. **Code excerpt** (5-30 lines) that shows the pattern in action

## Response format

````markdown
# {topic} in Odin ({N} sources found)

## {Source 1} (most relevant)

**File**: `relative/path/file.md`
**Section**: `## <title>`
**Excerpt**:

```odin
<5-30 lines of code>
```
````

**Why this source**: <1 sentence>

## {Source 2} (complement)

...

```md
Always have a **"Why this source"** section to explain why the file is relevant (avoids forcing the user to guess).

## Common patterns (quick reference list)

If the request matches one of these patterns, go directly to the corresponding INDEX section:

| Pattern         | INDEX section                                    |
| --------------- | ------------------------------------------------ |
| allocator/arena | "Memory / allocators"                            |
| state machine   | "State machines (FSM)"                           |
| entity system   | "Entity system / component"                      |
| hot reload      | "Hot reload"                                     |
| collision       | "Collision / physics"                            |
| raylib          | "Rendering / Raylib"                             |
| data-oriented   | "Data-oriented / perf"                           |
| handle-based    | "Allocation patterns (general)"                  |
| ffi / c-bindgen | "C bindings / vendor:"                           |
| error handling  | INDEX section "Language fundamentals" (chap. 16) |

## Anti-patterns

- **Never** open the whole KB (hundreds of files).
- **Never** propose a pattern without a code excerpt (too abstract).
- **Always** cite the exact file path (never "Karl's book" without a path).
- If the request is too vague ("how to make an Odin game?"), ask for clarification instead of listing 30 files.
- Never invent a code excerpt - always quote the exact text of the KB file.

## Limits

This skill is effective for:

- Game patterns (entity, FSM, allocator, hot reload)
- Odin language concepts (struct, union, defer, context.allocator)
- Community conventions (vendor:, c-bindgen)

This skill is NOT designed for:

- Finding a bug in user code (use the `odin-gamedev` subagent)
- Understanding a specific project file (read the file directly)
- Covering all aspects of Odin (use `.kilo/agents/odin-gamedev.md` for open questions)
```
