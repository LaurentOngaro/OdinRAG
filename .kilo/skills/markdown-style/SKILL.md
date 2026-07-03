---
name: markdown-style
description: "Distills all markdown style rules (project + personal) into one place. Use BEFORE creating or editing any .md file. Post-write: run reflow_md.py --quiet --check and lint fixes before considering the task done. Enforced by AGENTS.md § Markdown prose."
---

# Markdown style enforcer

## When to load me

LOAD BEFORE:

- creating a new `.md` file (authored doc, README, etc.)
- modifying an existing `.md` file (any non-trivial prose change)
- suggesting prose changes during a review

LOAD AFTER (when relevant):

- the user asks "is this markdown compliant?"
- after a batch of markdown edits, before declaring the batch done

SKIP:

- reading markdown files (no need)
- running scripts that only emit non-markdown output
- editing YAML / Python / Odin files (different style rules apply)

## HARD RULES (never violate)

### 1. One paragraph = one physical line (THE rule I keep breaking)

NEVER wrap prose at any column width. Long sentences are ONE LINE, even if they exceed 200 characters. The project uses "book style" paragraphs - every prose paragraph collapsed to a single physical line.

```
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

### 2. ASCII punctuation only

| Wrong                         | Right | Notes                    |
| ----------------------------- | ----- | ------------------------ |
| em-dash                       | `-`   | U+2014 → U+002D          |
| en-dash                       | `-`   | U+2013 → U+002D          |
| `'` `'` (curly quotes)        | `'`   | U+2019 / U+2018 → U+0027 |
| `"` `"` (curly double quotes) | `"`   | U+201C / U+201D → U+0022 |
| `…` (ellipsis)                | `...` | U+2026 → three dots      |

### 3. English only for PUBLIC docs (`AGENTS.md`)

- Public buckets (English mandatory): top-level, `_Helpers/`, `odin-knowledge-base/`, `code/`.
- Private buckets (any language OK): `_Private/`, `**/raw/**`, personal logs / planning / dailies.

Rationale: the `public` branch is pushed to github.com, an international public repo. Consistency for search, AI tooling (subagent prompts expect English keywords), and international contributors.

### 4. Frontmatter for authored docs

Required in `_Helpers/docs/`, `_Private/docs/`, etc. Frontmatter schema in `_Helpers/docs/003_yaml_frontmatter_conventions.md` (load on demand).

Quick rules:

- 5 main fields + hierarchical Obsidian tags
- `title`, `date`, `tags`, `type`, `status`, `version`, `lastUpdated`, `updatedBy`
- H1 title MUST match the filename exactly when the filename has an `NNN_` prefix
- FS-unsafe characters forbidden in filenames and H1 titles: `< > : " / \ | ? *`

### 5. Filename / H1 forbidden characters

`<` `>` `:` `"` `/` `\` `|` `?` `*` → rephrase the natural title.

## PRE-FLIGHT checklist (before writing prose)

- [ ] Plan the prose as SINGLE LINES from the start. Write unwrapped, do not write wrapped and expect to fix.
- [ ] Identify the bucket: public (English required) or private (any language OK)?
- [ ] Filename follows `NNN_*.md` convention if in an authored folder?
- [ ] Frontmatter planned for authored docs (`title`, `date`, `tags`, `type`, `status`, `version`, `lastUpdated`, `updatedBy`)?
- [ ] No em-dash, smart quotes, ellipsis in draft?

## POST-FLIGHT checklist (after writing - MANDATORY)

1. Run reflow check (THE primary signal for rule 1):

```bash
python _Helpers/scripts/fixes/reflow_md.py --quiet --check --path <file>
```

- Exit `0` → clean.
- Exit `1` → reflow needed (paths printed one per line). I wrapped when I shouldn't have → fix my source. Reflow (`--apply`) is MANUAL recovery controlled by the user; I do NOT invoke it without explicit GO.
- Exit `2` → tool error (root not found, etc.).

2. Run markdownlint-cli2 (catches MD024, MD025, etc.):

```bash
npx markdownlint-cli2 <file>
```

3. Loop until both exit `0`.

## Tools reference

| Tool                                         | Use                                | When                                                    |
| -------------------------------------------- | ---------------------------------- | ------------------------------------------------------- |
| `reflow_md.py --quiet --check --path <file>` | Detect wrapped paragraphs (rule 1) | every write                                             |
| `reflow_md.py --apply --path <file>`         | Auto-fix rule 1                    | MANUAL only, never automated, requires explicit user GO |
| `npx markdownlint-cli2 <file>`               | Catch other MD rules               | every write                                             |

## Never-automated list (read-and-respect)

The following actions MUST NOT happen without an explicit user request in the same conversation turn:

- `reflow_md.py --apply` (any path)
- `npx markdownlint-cli2 --fix` (if used)

These exist for the user's manual recovery. I surface them as options when relevant; I do not invoke them.

## References

- `AGENTS.md` § Markdown prose + Language + Markdown structure
- `_Helpers/docs/004_markdown_style.md` - full markdown style with examples
- `_Helpers/docs/003_yaml_frontmatter_conventions.md` - frontmatter schema
- `.markdownlint.json` - markdownlint-cli2 config (MD013 off, etc.)
- `_Helpers/scripts/fixes/reflow_md.py` - the auto-fix tool (has `--quiet` flag for low-noise checks)
