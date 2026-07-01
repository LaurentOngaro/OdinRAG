# OdinRAG - Curated knowledge base for Odin game development

> A personal RAG knowledge base for the [Odin programming language](https://odin-lang.org/) applied to game development (Raylib, Sokol, hot-reload, allocators).
> Built and curated end-to-end with **MiniMax-M3** as the structural engineering agent.

## What is this

OdinRAG aggregates, formats, and indexes learning material about Odin game dev so it can be navigated quickly by either:

- a human (via Obsidian, Grep, or `INDEX.md` files)
- an AI agent (via the [`.kilo/skills/`](.kilo/skills) `kb-navigator` skill and the [`.kilo/agents/odin-gamedev.md`](.kilo/agents/odin-gamedev.md) subagent)

The repo ships **only** the curation workflow (scrapers, agents, skills, indexes, doc metadata). The copyrighted content the scrapers target - Skool courses, blog posts, the Karl Zylinski book - is **deliberately not redistributed** in this repo and stays in the user's local working directory. See [SOURCES.md](SOURCES.md) for how to obtain each source legally on your own.

## Structure

> **The full tree lives in [`_Helpers/docs/001_folder_structure.md`](_Helpers/docs/001_folder_structure.md).**
> This section gives a one-line summary of each bucket; refer to the structure doc for the complete tree.

- `odin-knowledge-base/` - **Bucket 1** (public, partly gitignored) - scraped KB + Skool courses
- `code/` - public code references (examples, gists, vendored templates, personal projects)
- `_Helpers/` - **Bucket 2** (public) - scripts, meta docs, internal templates, prompts, logs
- `_Private/` - **Bucket 3** (gitignored, never pushed) - config, planning, raw notes

> `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/*.md` are **gitignored** by design - they contain copyrighted content under your own subscription. The repo ships sample articles in `odin-knowledge-base/docs/{karl_zylinski,gingerbill,jakubtomsu}/`; run the corresponding scrapers to populate the full corpus on your own machine.

## Quick start

````bash
git clone https://github.com/LaurentOngaro/OdinRAG.git
cd OdinRAG

# Audit before any push (idempotent, exit 0 = clean)
python _Helpers/scripts/diagnostic/audit_public_safety.py

# Scrape the public sources (no paywall, no auth)
python _Helpers/scripts/scrappers/scrape_official.py
python _Helpers/scripts/scrappers/scrape_zylinski.py

# (Skool requires your own paid membership - see SOURCES.md)
python _Helpers/scripts/scrappers/scrape_skool.py

# Format all .odin + ```odin``` blocks in the working tree
python _Helpers/scripts/fixes/format_odin_in_files.py --path odin-knowledge-base
````

Requirements: Python 3.10+, `pip install requests beautifulsoup4 markdownify lxml`.

### Personal setup (paths and credentials)

All machine-specific paths and credentials live in a single gitignored file: `_Private/.config/user_config.jsonc`.

Setup:

```bash
cp _Helpers/templates/user_config.example.jsonc _Private/.config/user_config.jsonc
# edit the copy with your actual paths
```

The loader `_Helpers/scripts/lib/user_config.py` exposes them to the scrapers and `format_odin_in_files.py`. Override any value with an env var (e.g. `ODINFMT_EXE`, `BOOK_HTML_SRC`).
Keep credentials out of the JSON - use env vars like `SKOOL_PASSWORD` for secrets.

## Built with MiniMax-M3

This whole project - the scraper architecture, the frontmatter schema, the agent prompts, the 6 Kilo skills, the subagent design, the lint configs - was designed and iterated with [MiniMax-M3](https://minimax.io), powered via [Kilo Code](https://kilo.ai) as the agentic IDE.
M3 acts as the structural engineer; I act as the domain curator.

Every file in this repo is the result of a prompt + a code review between us. There is no `git blame` you can read to tell which line was M3's first draft and which was my edit - that's the point.

For the technical story of how M3 is used in this repo, see [`_Helpers/docs/002_how_minimax-m3_is_used_in_this_repository.md`](_Helpers/docs/002_how_minimax-m3_is_used_in_this_repository.md).

For the social posts around the MiniMax-M3 Showcase Round 2, see [`_Helpers/docs/social/`](_Helpers/docs/social).

## License

This repository's code (scrapers, agents, skills, scripts, configs) is released under the **MIT License** - see [LICENSE](LICENSE).

The third-party content referenced by the scrapers is **not** included in this repository and remains the property of its respective authors.
See [SOURCES.md](SOURCES.md) for attribution and licensing.

## Support this project

> **If this knowledge base saved you a few hours of Odin exploration, you can help it grow by [sponsoring its development](https://github.com/sponsors/LaurentOngaro)**.
> The code is open-source, the scrapers are free, no ads and no tracking - **your support is what keeps it that way**.

**Spread the word at zero cost:**

- Star the repo to help others find it: <https://github.com/LaurentOngaro/OdinRAG>
- Watch for new sources / patterns / scrapers
- Open issues for missing topics or broken scrapers
- Cite it in your blog / Reddit answer / Discord when it helps

### Where the sponsorship goes

Every dollar funds one of these (in order of priority):

1. **Scraper maintenance** - keeping `scrape_skool.py`, `scrape_official.py`, `scrape_zylinski.py` resilient against site changes, rate limits, and bot detection.
2. **New sources** - book ISBN API, dod-benchmarks tracker, official newsletter parser, etc.
3. **AI integration polish** - more Kilo skills, smarter subagent routing, frontmatter improvements for Obsidian / RAGnarok compatibility.
4. **Documentation** - English translations of French-only docs, code samples, video walkthroughs for the trickier topics (hot-reload, allocator patterns).

Sponsoring is entirely optional. The repo and the KB stay MIT-licensed and free to use regardless.
