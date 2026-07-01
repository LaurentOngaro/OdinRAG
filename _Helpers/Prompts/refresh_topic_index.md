---
title: "refresh_topic_index"
date: 2026-07-01
tags: [OdinRAG, reference]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# Prompt: refresh the "Index by topic" section of `odin-knowledge-base/INDEX.md`

> Use this prompt when the KB has grown significantly (new Skool lessons, new Karl book chapters, new gingerbill/jakubtomsu articles) and the hardcoded "Index by topic" section in `odin-knowledge-base/INDEX.md` is stale.

## When to invoke

- After running the scrapers and seeing the existing INDEX.md "Index by topic" section reference paths that no longer exist
- After a major KB restructure (new courses, new chapter splits)
- After ~30+ new files in `odin-knowledge-base/` since the last manual curation
- **Not** for every scrape - only when the curated section is meaningfully out of date

## Inputs (paste these into your Kilo prompt)

```
INPUT A - the current "Index by topic (QUICK SEARCH)" section:
$(cat odin-knowledge-base/INDEX.md | sed -n '/## Index by topic (QUICK SEARCH)/,/## Skill to navigate/p')

INPUT B - list of .md files in the KB (with topic frontmatter tags):
$(find odin-knowledge-base docs -name '*.md' -type f | xargs -I{} sh -c 'echo "=== {} ==="; head -5 "{}"')

INPUT C - frontmatter summary:
$(find odin-knowledge-base docs -name '*.md' -type f | xargs -I{} grep -l "topic/" "{}" | head -30)
```

## Prompt body (paste after the inputs)

````
You are maintaining an INDEX for an Odin language knowledge base.

TASK
1. Read each .md file's first 30 lines and frontmatter (if any).
2. Group files by topic. Suggested topics (adapt to actual content):
   - Memory / allocators
   - State machines (FSM)
   - Entity system / component
   - Hot reload
   - Collision / physics
   - Rendering / Raylib
   - Data-oriented / perf
   - Allocation patterns (general)
   - C bindings / vendor:
   - Build / compile
   - Language fundamentals
   - Workflow / tooling
3. For each topic with ≥3 files, select the 3-5 most representative ones (most cited, most complete, broadest coverage).
4. For topics with 1-2 files, include them all.
5. If a file path from INPUT A no longer exists, mark it `[DEPRECATED: <old-path>]` so the human reviewer can decide.
6. If a new file isn't covered by any current topic, propose a new topic section.

CONSTRAINTS
- Use real paths from INPUT B only - do NOT invent paths.
- Output format: a single Markdown section in "book style":
    ## Index by topic (QUICK SEARCH)

    <one paragraph intro>

    ### Topic name

    - `<relative/path.md>` - one-line description from H1 or first paragraph
    - `<relative/path.md>` - description

    ### Next topic name

    - ...
- One paragraph = one line (no artificial wrap, no manual line breaks).
- Don't invent descriptions - use one phrase per file from its H1 or first paragraph.
- Preserve the [DEPRECATED] markers verbatim from step 5.

OUTPUT
A single Markdown code block (```...```) containing the new section, ready to replace the current "## Index by topic (QUICK SEARCH)" section in `odin-knowledge-base/INDEX.md`.

DO NOT
- Modify `odin-knowledge-base/INDEX.md` yourself.
- Reformat the AUTO sections (Overview, Skool, Karl book, Statistics, Skill to navigate).
- Include the manual "How this file is generated" section (it's a separate MANUAL block).
````

## After receiving the AI output

1. Review the proposed section
2. Open `odin-knowledge-base/INDEX.md`
3. Find the block between `<!-- BEGIN MANUAL (your curated content - preserved across scrapes) -->` and `<!-- END MANUAL -->`
4. Replace the `## Index by topic (QUICK SEARCH)` part (preserve the "How this file is generated" part that comes after)
5. Save

## Alternative: skip the script entirely

If you have Kilo (MiniMax-M3) running, you can just say to Kilo:

> _Read `odin-knowledge-base/INDEX.md`, read all `.md` files in `odin-knowledge-base/`, `docs/`, and `_Helpers/templates/odin-project/`. Propose an updated `## Index by topic (QUICK SEARCH)` section that covers the current KB. Output the new section as a code block - do NOT modify INDEX.md._

Kilo will execute the prompt directly. No script needed.
