---
date: 2026-06-29
TODO
---

# 002_How MiniMax-M3 is used in this repository

This document is a quick technical reference for anyone reading the code and wondering "where is M3 actually being invoked, and what does it do here?". It is intentionally kept short.

## TL;DR

Every file in this repo - scrapers, skills, subagent prompts, frontmatter schemas, lint configs, planning templates - was designed, drafted, or rewritten through [Kilo Code](https://kilo.ai) powered by **[MiniMax-M3](https://minimax.io)**, the MiniMax MiniMax-M3 foundation model family.

The agent setup is described by [`../kilo.json`](../kilo.json) and the operational guardrails live in [`../../AGENTS.md`](../../AGENTS.md).

## Concrete invocations

### 1. Subagent routing - `odin-gamedev`

When a Kilo session receives a question that touches Odin syntax, allocators, hot reload, or game-dev patterns, it delegates to the subagent defined in [`.kilo/agents/odin-gamedev.md`](../../agents/odin-gamedev.md).

M3's job in that subagent is **citation discipline**: load `odin-knowledge-base/INDEX.md` first (~5 KB), pick 2-3 candidate files, return answers with explicit `file:line` references instead of paraphrasing.

### 2. Skill authoring - 5 skills in `.kilo/skills/`

| Skill                  | What M3 wrote                                                                   |
| ---------------------- | ------------------------------------------------------------------------------- |
| `kb-navigator/`        | The semantic search workflow (frontmatter filtering, KB layout rules)           |
| `odin-format/`         | The odinfmt invocation pattern (2-space + LF + post-scrape hook)                |
| `scraper-runner/`      | The CLI flag conventions (`--check`, `--force`, `--overwrite-existing-lessons`) |
| `odin-pattern-finder/` | The grep + frontmatter pattern matching routine                                 |
| `planning-helper/`     | The day-by-day planning template lifecycle                                      |

Each skill follows the progressive-disclosure pattern (SKILL.md is short, supporting scripts are loaded on demand).

### 3. Scraper architecture - `_Helpers/*.py`

Each of the four durable scrapers follows a contract M3 proposed:

- **idempotent** - re-running on an up-to-date scrape is a no-op
- **`--check`** - dry-run mode that prints what _would_ be written without writing
- **structured logging** - `_log(level, msg)` instead of `print()` so the logs go to a file in `_Helpers/logs/`
- **shared `lib/`** - `http_client.py`, `html2md.py`, `text_clean.py`, `odin_format.py` are imported, not copy-pasted
- **frontmatter discipline** - every scraped `.md` gets `Cours`, `Module`, `ID`, `Durée` metadata so semantic filtering works in Obsidian too

### 4. Audit script - `_Helpers/audit_public_safety.py`

M3 wrote the public-safety auditor used to gate pushes to this very repo. It mirrors the rules in `.gitignore` and exits non-zero if any copyrighted path is staged for push. See [`PUBLIC_RELEASE_CHECKLIST.md`](PUBLIC_RELEASE_CHECKLIST.md) § 2.

### 5. Social assets - `_Helpers/docs/social/`

Post drafts prepared (with M3) for the MiniMax-M3 Showcase Round 2 (June 29 - July 5, 2026):

- [`social/REDDIT_POST.md`](social/REDDIT_POST.md) - draft for `r/odinlang`
- [`social/TWITTER_THREAD.md`](social/TWITTER_THREAD.md) - thread for X
- [`social/DISCORD_NOTE.md`](social/DISCORD_NOTE.md) - note for `🧩丨show-your-case`

## What M3 is _not_ used for

- Generating the scraped content itself - M3 drives the scrapers, but the scraped output is whatever the source pages contain.
- Final code-review of Odin without cross-checking - the subagent is required to cite KB files with exact paths, not invent syntax.
- Running the scrapers - those are CLI scripts executed by the user.
- Decisions about licensing and content redistribution - those are human curator decisions (see [`../SOURCES.md`](../../SOURCES.md)).

## Reproducibility

To reproduce this workflow on your own machine:

```bash
pip install kilo-code    # https://kilo.ai
# Configure kilo.json with provider = MiniMax, model = MiniMax-M3
kilo                     # open the project
# In chat: "Apply the kb-navigator skill and find me arena allocator patterns in Odin"
```

## Credits

- Model: [MiniMax-M3](https://minimax.io)
- Agent runtime: [Kilo Code](https://kilo.ai)
- Domain: [Odin programming language](https://odin-lang.org/)
