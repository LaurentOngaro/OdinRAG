---
title: "Markdown style rules"
date: 2026-07-01
tags: [OdinRAG, reference, style, markdown]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# 004_markdown_style

> Detailed convention. The 2-line pointer in [`../../AGENTS.md`](../../AGENTS.md) is the only first-load context. Read this file when in doubt.

## The rule

**One paragraph = one physical line.** In any tracked `.md` file, a prose paragraph is a single line of arbitrary length. Hard line breaks are reserved for logical separations only: paragraph end, list item, heading, table row, code block boundary, blockquote, setext underline, thematic break.

**Exempt**: table cells, code blocks (fenced and indented), frontmatter YAML, HTML blocks, and reference link definitions. These keep their own structural rules.

## Why

- `MD013` (line length) is disabled in [`.markdownlint.json`](../../.markdownlint.json) on purpose. The lint config and the prose style agree.
- The visual line is the editor's job, not the file's. Soft-wrap in VS Code / Obsidian / Sublime renders long lines at the user's preferred width without inserting any character in the file.
- Short lines force the reader's eye to track indentation, count words per line, and re-assemble sentences. Long lines let the reader follow the prose continuously.
- The git diff for a single sentence change is one line modified, not four. Code review and `git blame` stay readable.

## Examples

A paragraph in this repo looks like a single line, no matter how long it is:

```markdown
This is one paragraph. It is a single line. The editor may render it on multiple visual lines in a narrow window, but in the file itself there are no hard line breaks between these sentences, no matter how many characters they span across the screen of the user reading the file.
```

A new paragraph starts after a blank line:

```markdown
First paragraph as a single line.

Second paragraph also as a single line, separated from the first by exactly one blank line and nothing else.
```

A list item starts a new block, but the description of one item is a single line:

````markdown
- **Frontmatter** - the schema is in [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](003_yaml_frontmatter_conventions.md) (5 main fields + hierarchical Obsidian tags).
- **Tables** - may span any width; cells are not split.
- **Code blocks** - fenced with ` ``` `; never wrapped.
````

A table keeps its structure:

```markdown
| Source                                              | Files | Notes                                                         |
| --------------------------------------------------- | ----- | ------------------------------------------------------------- |
| `odin-knowledge-base/`                              | 118   | Skool 'programvideogames' lessons (Markdown with frontmatter) |
| `odin-knowledge-base/docs/karl_zylinski/odin-book/` | 34    | Karl's book split into 1 file per chapter                     |
```

A heading is its own line; the body that follows it is a single line:

```markdown
## Stack

The stack is Odin + Raylib + a per-frame arena allocator wired in debug builds only, and a tracking allocator that reports leaks on shutdown.
```

## What lives where

- **AGENTS.md**: 2-line pointer. No detailed rule, no examples. Reduces priming.
- **This file**: detailed rule, examples, rationale. Loaded on demand.
- **`.markdownlint.json`**: `MD013: false` enforces it at lint time.
- **No script**: there is no automated re-flow tool, by design. AI agents write the right shape on the first pass.

## For AI agents

When writing or editing a `.md` file in this repo:

- Write each prose paragraph as a single physical line. Do not insert `\n` inside a sentence, between a sentence and the next, or inside a link, to fit any character limit.
- Use `\n\n` (one blank line) between paragraphs, and `\n` between sibling list items / heading / table rows.
- Tables, code fences, frontmatter, and HTML blocks keep their own structure.
- If you produced a file with wrapped prose by accident, say so in the same response and rewrite it. Do not commit the wrapped version and rely on a post-hoc tool to clean it up.
-
