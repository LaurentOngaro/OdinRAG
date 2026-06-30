# REDDIT POST

## Titre

```
I built a curated RAG knowledge base for Odin game dev using MiniMax-M3 (idempotent scrapers, subagent + skills, curated KB index)
```

## Content

````markdown
Hey r/odinlang,

I've been working on a personal "second brain" for Odin game dev, entirely built and maintained with [MiniMax-M3](https://minimax.io) via Kilo Code as my agentic IDE.
Sharing it here since the MiniMax-M3 showcase round 2 is live and this is 100% M3-powered.

## What's in the box

- **`_Helpers/`** - durable, idempotent Python scrapers (pure stdlib + BeautifulSoup/markdownify):
  - `scrape_skool.py` (Skool programvideogames group - _runs locally on my own membership, content stays on my disk_)
  - `scrape-official.py` (odin-lang.org/docs/ + awesome-odin)
  - `scrape-zylinski.py` (RSS auto-discovery)
  - `format_odin_in_files.py` (wraps `odinfmt`, reads `odinfmt.json` at repo root)
  - Shared `lib/` (`text_clean`, `http_client`, `html2md`, `odin_format`)
- **`.kilo/agents/odin-gamedev.md`** - a specialized subagent that loads `INDEX.md` first, picks 2-3 KB files, and cites exact paths (`file:line`).
- **`.kilo/skills/`** - 6 Kilo skills: `kb-navigator`, `odin-format`, `scraper-runner`, `odin-pattern-finder`, `planning-helper`, `pylance-check` (KB search, re-formatting, scraper orchestration, daily planning, pyright lint).
- **`planning/`** - day-by-day planning with a strict template, never edited.
- **`docs/official/`** - 11 pages from odin-lang.org/docs/ (MIT-style license, kept with attribution).

## How MiniMax-M3 is actually used (not just chat)

1. **Subagent delegation** - M3 picks up "what pattern for arena allocators in Odin?" → routes to `odin-gamedev` subagent → returns citations like `docs/karl_zylinski/temporary-allocator-your-first-arena.md:42`.
2. **Re-entrant scrapers** - I asked M3 to write `_Helpers/scrape_skool.py` with `--check`, dry-run, idempotency, structured logging. Re-running = no-op if files exist.
3. **Skill authoring** - M3 authored the 6 skills above (SKILL.md + workflow) following progressive disclosure.
4. **Frontmatter discipline** - every lesson has `topic/*` tags so semantic search works in Obsidian too.
5. **Format gate** - after each scrape, `format_odin_in_files.py` is run to keep ```odin ...``` blocks consistent (no tabs, 2 spaces, LF).

## What I deliberately did NOT do

- No scraped course content or blog posts are published in this public repo (see `.gitignore`). The scrapers and the curated indexing workflow are open-source; the indexed content stays on my disk under my own paywall subscription.
- No vector DB / no RAGnarök yet - KB is small enough (~150 docs) that M3's context + frontmatter filtering is enough. Indexing trigger at ~5000 files.

## Try it / fork it

- Public repo: **https://github.com/LaurentOngaro/OdinRAG** (already public; reproducible from-scratch on your own data).
- Scrapers are pure stdlib Python + BeautifulSoup/markdownify.
- Skills follow the [Anthropic progressive disclosure pattern](https://docs.anthropic.com).

## Note for the MiniMax-M3 showcase

This whole project - scraping strategy, idempotency design, frontmatter schema, subagent prompts, skill authoring, daily planning, linting config - was done through Kilo Code powered by MiniMax-M3. I'm the curator and the domain expert; M3 is the executor and the structural engineer.

Happy to answer questions on the scraper architecture or the subagent design.

#MinimaxM3
````
