---
title: "References - Cross-language style and design references"
date: "2026-07-10"
tags: [OdinRAG, kb, reference, doc]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-10"
updatedBy: "MiniMax-M3 (Kilo Code)"
summary: "Hand-picked external references that are not Odin-specific but inform OdinRAG project decisions (coding style, design philosophy, performance methodology)."
---

# README - References

## Purpose

This folder collects hand-picked external references that inform OdinRAG project decisions but are **not Odin-specific**. These documents live alongside the language-specific KB under `odin-knowledge-base/docs/` and `odin-knowledge-base/courses/`, but cover broader engineering topics: coding style for safety-critical systems, design philosophy, performance methodology, game loop theory.

## Distinction from `docs/` and `courses/`

| Folder        | Scope                                | Source                                                  | Frontmatter                    | Public branch                |
| ------------- | ------------------------------------ | ------------------------------------------------------- | ------------------------------ | ---------------------------- |
| `docs/`       | Odin-specific (scraped)              | odin-lang.org, zylinski.se, gingerbill.org, jakubtomsu  | minimal                        | yes                          |
| `courses/`    | Odin-specific (paid Skool content)   | skool.com/programvideogames                             | scraping-style (`Cours:` etc.) | absent (two-branch strategy) |
| `references/` | Cross-language, general design       | curated by hand (TigerBeetle, Sean Barrett, NASA, etc.) | full (matches AGENTS.md)       | yes                          |

The boundary rule: if a document is **about Odin** (its language, ecosystem, idioms), it goes in `docs/` or `courses/`. If it is **outside Odin** but **informs how we code Odin**, it goes in `references/`.

## Contents

| File                | Topic                                                      | Why it's here                                                                                                       |
| ------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `tiger_style.md`    | TigerBeetle coding style guide for safety-critical code    | Safety-critical mindset (assertions density, no recursion, fixed-size types, in-place init) carries to Odin         |
| `tiger_style-fr.md` | French translation of TigerStyle                           | Personal reading aid. Annotated with `exception:` in frontmatter per AGENTS.md ("all public docs in English" rule)  |

More candidates are listed in the inline chat decisions; not yet committed to disk.

## Conventions

- All files in this folder MUST carry a full YAML frontmatter (title, date, tags, type, status, version, lastUpdated, updatedBy, summary), matching the schema used in `_Helpers/docs/*.md`.
- Tags MUST include `OdinRAG` and `reference`. Add hierarchical `source/<name>` and `topic/<concept>` tags where relevant (e.g. `source/tigerbeetle`, `topic/style-guide`).
- Forbidden Unicode punctuation (em-dash U+2014, en-dash U+2013, smart quotes U+201C/D, single smart quotes U+2018/9, ellipsis U+2026) MUST be replaced with ASCII equivalents: `-` for dashes, `"` and `'` for quotes, `...` for ellipsis.
- Translations MUST be annotated with `exception: "<reason>"` in frontmatter. The English original is the canonical reference; translations may lag behind.
- One prose paragraph = one physical line. Tables, code blocks, frontmatter, and list markers keep their own structure. See [`../../_Helpers/docs/004_markdown_style.md`](../../_Helpers/docs/004_markdown_style.md).
- No new `.odin` compilable code lives here. `odin ...` blocks (if any) get auto-formatted by the `odin-format` skill after edits.

## Updating procedure

When adding a new reference:

1. **Pick a filename** in `snake_case`, optionally prefixed by `NNN_` if ordering matters. No `NNN_` required otherwise.
2. **Source attribution**: if copied from a public source, keep the URL and ingestion date. If synthesized, note that explicitly in the body.
3. **Fill the frontmatter** with the full schema (see Conventions above).
4. **Add a row** to the Contents table in this README.
5. **If substantial**, add an entry to [`../INDEX.md`](../INDEX.md) manual zone (the section after `<!-- BEGIN MANUAL -->`).
6. **Cross-link** from related entries in `docs/` (e.g. link to `sean_barrett` from the Raylib tutorial files).
7. **Validate**: run `markdownlint` on the new file. Run `python _Helpers/scripts/diagnostic/auditReadmeCoherence.py --scope references` to confirm this README stays in sync.

## Cross-references

- Full folder tree: [`../../_Helpers/docs/001_folder_structure.md`](../../_Helpers/docs/001_folder_structure.md)
- Frontmatter schema: [`../../_Helpers/docs/003_yaml_frontmatter_conventions.md`](../../_Helpers/docs/003_yaml_frontmatter_conventions.md)
- Markdown style rules: [`../../_Helpers/docs/004_markdown_style.md`](../../_Helpers/docs/004_markdown_style.md)
- KB central index: [`../INDEX.md`](../INDEX.md)
- Top-level KB README: [`../README - odin knowledge base.md`](../README%20-%20odin%20knowledge%20base.md)
