---
name: markdown-style
description: "Distills all text, code, and markdown style rules (180-char code limit, LF/CRLF line endings, no em-dash/en-dash, strict French accent preservation, Prettier table alignment, and 0 markdownlint warning). Use BEFORE creating or editing any .md or text file. Post-write: run Prettier, markdownlint-cli2 --fix, and reflow_md.py --quiet --check before considering the task done."
---

# Markdown & text style enforcer

## When to load me

LOAD BEFORE:

- creating a new `.md` file (authored doc, README, etc.)
- modifying an existing `.md` file (any non-trivial prose or table change)
- suggesting prose changes during a review

LOAD AFTER (when relevant):

- the user asks "is this markdown compliant?"
- after a batch of markdown edits, before declaring the batch done

SKIP:

- reading markdown files (no need)
- running scripts that only emit non-markdown output

## HARD RULES (never violate)

### 1. Line length: 180 characters for code/scripts, single-line paragraphs for Markdown prose

- **Code, scripts, and config files** (`.py`, `.odin`, `.ps1`, `.sh`, `.json`, `.yaml`, `.toml`): maximum line length is **180 characters** (`max_line_length = 180`, `character_width = 180`, `printWidth: 180`). Never artificially wrap code at 80, 100, or 150 characters.
- **Markdown prose (`.md`)**: **One paragraph = one physical line (`MD013: false`, `proseWrap: preserve`).** NEVER wrap prose at any column width. Long sentences stay on ONE LINE, even if they exceed 200 characters. The project uses "book style" paragraphs - every prose paragraph collapsed to a single physical line.

```text
# CORRECT (one paragraph = one line, however long):
This is a paragraph that goes on one single line regardless of its length and even when it contains multiple sentences, because soft wrapping is explicitly forbidden by the project rules.

# WRONG (this is the violation the user keeps seeing):
This is a paragraph that goes
on multiple physical lines
because that breaks the reflow_md invariant.
```

Tables, code fences, headings, lists, blockquotes, frontmatter are preserved verbatim by `reflow_md.py`.

Detect violations after every write with:

```bash
python _Helpers/scripts/fixes/reflow_md.py --quiet --check --path <file>
# exit 0 = clean, exit 1 = reflow needed (paths printed one per line)
```

### 2. Uniform line endings (LF everywhere, CRLF only for Windows native scripts)

- Encoding: **UTF-8 without BOM** across all text files.
- **`LF` (`\n`) mandatory everywhere** for code, Markdown documentation, config files, and Unix scripts (`* text=auto eol=lf`).
- **`CRLF` (`\r\n`) reserved exclusively** for native Windows scripts (`*.bat`, `*.cmd`, `*.ps1`, `*.reg`).
- `git config --local core.autocrlf false` must be set on every clone. Never create a commit that only changes line endings.

### 3. No AI-typical punctuation & strict preservation of French accents

Em-dash, en-dash, curly quotes, and ellipsis are almost exclusively used by AI assistants in prose, not by humans in their daily writing. Their presence in a tracked file is a strong signal of AI-generated content. Replace them with their ASCII equivalents:

| Wrong                         | Right | Notes                      |
| ----------------------------- | ----- | -------------------------- |
| em-dash (`U+2014`)            | `-`   | `U+2014` -> `U+002D`       |
| en-dash (`U+2013`)            | `-`   | `U+2013` -> `U+002D`       |
| `'` `'` (curly quotes)        | `'`   | `U+2019` / `U+2018` -> `'` |
| `"` `"` (curly double quotes) | `"`   | `U+201C` / `U+201D` -> `"` |
| `…` (ellipsis)                | `...` | `U+2026` -> three dots     |

**Accented letters MUST be strictly preserved**: whenever writing or editing French text (in `_Private/`, raw notes, comments, or French documentation), **all French accented characters and diacritics must be kept in UTF-8** (`é`, `è`, `ê`, `ë`, `à`, `â`, `ù`, `û`, `ç`, `œ`, `î`, `ï`, `ô`, `ÿ`, `É`, `È`, `À`, `Ç`...). **Never strip or degrade French text into bare ASCII without accents.**

Box-drawing characters (`─`, `│`, `╭`, `╮`, ...) and arrow symbols (`->`, `=>`, `<-`) are OK for diagrams and table separators.

### 4. English only for PUBLIC docs (`AGENTS.md`)

- Public buckets (English mandatory): top-level, `_Helpers/`, `odin-knowledge-base/`, `code/`.
- Private buckets (any language OK, with mandatory French accents when written in French): `_Private/`, `**/raw/**`, personal logs / planning / dailies.

Rationale: the `public` branch is pushed to github.com, an international public repo. Consistency for search, AI tooling (subagent prompts expect English keywords), and international contributors.

### 5. Frontmatter & filename conventions for authored docs

Required in `_Helpers/docs/`, `_Private/docs/`, etc. Frontmatter schema in `_Helpers/docs/003_yaml_frontmatter_conventions.md` (load on demand).

Quick rules:

- 5 main fields + hierarchical Obsidian tags
- `title`, `date`, `tags`, `type`, `status`, `version`, `lastUpdated`, `updatedBy`
- H1 title MUST match the filename exactly when the filename has an `NNN_` prefix
- FS-unsafe characters forbidden in filenames and H1 titles: `< > : " / \ | ? *` -> rephrase the natural title.

## PRE-FLIGHT checklist (before writing prose)

- [ ] Plan the prose as SINGLE LINES from the start. Write unwrapped, do not write wrapped and expect to fix.
- [ ] Identify the bucket: public (English required) or private (any language OK, keep all French accents in UTF-8)?
- [ ] Filename follows `NNN_*.md` convention if in an authored folder?
- [ ] Frontmatter planned for authored docs (`title`, `date`, `tags`, `type`, `status`, `version`, `lastUpdated`, `updatedBy`)?
- [ ] No em-dash (`U+2014`), en-dash (`U+2013`), smart quotes, or ellipsis in draft?

## POST-FLIGHT checklist (after writing - MANDATORY, 0 markdownlint warning)

1. Format tables and spacing with Prettier (`--prose-wrap preserve` preserves single-line paragraphs while aligning GFM tables):

```bash
npx --yes prettier --prose-wrap preserve --end-of-line lf --write <file>
```

2. Run `markdownlint-cli2 --fix` and verify 0 remaining errors:

```bash
npx --yes markdownlint-cli2 --fix <file>
```

3. Run reflow check (THE primary signal for rule 1):

```bash
python _Helpers/scripts/fixes/reflow_md.py --quiet --check --path <file>
```

- Exit `0` -> clean.
- Exit `1` -> reflow needed (paths printed one per line). Fix wrapped lines in source.
- Exit `2` -> tool error (root not found, etc.).

4. Loop until `markdownlint-cli2` reports `0 error(s)` and `reflow_md.py --quiet --check` exits `0`.

## Tools reference

| Tool                                                               | Use                                      | When                                                    |
| ------------------------------------------------------------------ | ---------------------------------------- | ------------------------------------------------------- |
| `npx --yes prettier --prose-wrap preserve --write <file>`          | Align GFM tables & normalize spacing     | every write                                             |
| `npx --yes markdownlint-cli2 --fix <file>`                         | Auto-fix & verify 0 `markdownlint` error | every write                                             |
| `python _Helpers/scripts/fixes/reflow_md.py --quiet --check <arg>` | Detect wrapped paragraphs (rule 1)       | every write                                             |
| `python _Helpers/scripts/fixes/reflow_md.py --apply --path <file>` | Auto-fix rule 1                          | MANUAL only, never automated, requires explicit user GO |

## References

- `AGENTS.md` - Style rules (Code & script line length, Punctuation, Markdown prose, Language, Markdown structure)
- `_Helpers/docs/004_markdown_style.md` - full markdown style with examples
- `_Helpers/docs/003_yaml_frontmatter_conventions.md` - frontmatter schema
- `.markdownlint.json` & `.markdownlint-cli2.jsonc` - markdownlint-cli2 config (`MD013: false`, `MD060: true`, etc.)
- `.prettierrc.json` & `.prettierignore` - Prettier config (`printWidth: 180`, `proseWrap: preserve`, `endOfLine: lf`)
- `_Helpers/scripts/fixes/reflow_md.py` - the reflow checker/fixer
