# OdinRAG - Curated knowledge base for Odin game development

> A personal RAG knowledge base for the [Odin programming language](https://odin-lang.org/) applied to game development (Raylib, Sokol, hot-reload, allocators).
> Built and curated end-to-end with **MiniMax-M3** as the structural engineering agent.

## What is this

OdinRAG aggregates, formats, and indexes learning material about Odin game dev so it can be navigated quickly by either:

- a human (via Obsidian, Grep, or `INDEX.md` files)
- an AI agent (via the [`.kilo/skills/`](.kilo/skills) `kb-navigator` skill and the [`.kilo/agents/odin-gamedev.md`](.kilo/agents/odin-gamedev.md) subagent)

The repo ships **only** the curation workflow (scrapers, agents, skills, indexes, doc metadata). The copyrighted content the scrapers target - Skool courses, blog posts, the Karl Zylinski book - is **deliberately not redistributed** in this repo and stays in the user's local working directory. See [SOURCES.md](SOURCES.md) for how to obtain each source legally on your own.

## Structure

````
OdinRAG/
├── README.md                  ← you are here
├── SOURCES.md                 ← how to obtain the copyrighted sources this KB references
├── LICENSE                    ← MIT
├── AGENTS.md                  ← conventions for AI-coding agents (Kilo, Claude Code...)
├── kilo.json                  ← AI agent runtime config
├── odinfmt.json               ← Odin formatter config (2-space, LF)
├── .markdownlint.json         ← markdown lint config
│
├── docs/                      ← scraped sources (samples shipped; full corpus via scrapers)
│   ├── official/              ← odin-lang.org/docs/ + awesome-odin (MIT-style, fully shipped)
│   ├── karl_zylinski/         ← 5 sample articles from zylinski.se (run scraper for full 19)
│   ├── gingerbill/            ← 5 sample articles from gingerbill.org (run scraper for full 44)
│   ├── jakubtomsu/            ← 4 sample articles from jakubtomsu.github.io (run scraper for full 11)
│   ├── newsletters/           ← 32 odin-lang.org/news/ issues (fully shipped, Odin team)
│   └── showcase/              ← 7 odin-lang.org/showcase/ pages (fully shipped, Odin team)
│
├── code/                      ← public code references
│   ├── examples/              ← official demo.odin (1 file, see SOURCES.md § 9)
│   ├── gists/                 ← 25 public gists from awesome-odin
│   ├── templates/             ← README with clone instructions (no templates checked-in - see SOURCES.md)
│   └── projets/               ← project conventions + template + integration guide
│
├── _Helpers/                  ← scrapers + utilities (PUBLIC, runnable on your own data)
│   ├── scrape_skool.py        ← scrapes the programvideogames Skool group
│   ├── scrape-official.py     ← scrapes odin-lang.org/docs/ + awesome-odin
│   ├── scrape-zylinski.py     ← scrapes zylinski.se (RSS auto-discovery)
│   ├── scrape-gingerbill.py   ← scrapes gingerbill.org (RSS)
│   ├── scrape-newsletters.py  ← scrapes odin-lang.org/news/
│   ├── scrape-jakubtomsu.py   ← scrapes jakubtomsu.github.io (RSS)
│   ├── scrape-showcase.py     ← scrapes odin-lang.org/showcase/
│   ├── odin_format.py         ← wrapper over odinfmt (CLI + library)
│   ├── format_odin_in_files.py← runs odinfmt over .odin + ```odin``` blocks
│   ├── book_html_to_md.py     ← converts Karl's book HTML → per-chapter MD
│   ├── build_kb_index.py      ← regenerates odin-knowledge-base/INDEX.md
│   ├── fix_mojibake.py        ← archival - repair UTF-8/Latin-1 mojibake
│   ├── reflow_md.py           ← reflow .md into book style (1-paragraph-per-line)
│   ├── lint_pylance.py        ← pyright-based linter (enforced zero warnings)
│   ├── audit_public_safety.py ← verifies the working tree is safe to push publicly
│   ├── download_gists.py      ← downloads public gists from awesome-odin
│   ├── download_odin_examples.py ← downloads official Odin examples
│   ├── lib/                   ← shared library (__init__, text_clean, http_client, html2md, user_config)
│   └── docs/                  ← internal docs + social post templates + user_config.example.json
│
└── odinfmt.json               ← formatter config (duplicate listed above for IDE visibility)
````

> `odin-knowledge-base/` and `courses/` (the local scraped output) are **gitignored** by design - they contain copyrighted content under your own subscription. The repo ships sample articles in `docs/{karl_zylinski,gingerbill,jakubtomsu}/`; run the corresponding scrapers to populate the full corpus on your own machine.

## Quick start

````bash
git clone https://github.com/LaurentOngaro/OdinRAG.git
cd OdinRAG

# Audit before any push (idempotent, exit 0 = clean)
python _Helpers/audit_public_safety.py

# Scrape the public sources (no paywall, no auth)
python _Helpers/scrape-official.py
python _Helpers/scrape-zylinski.py

# (Skool requires your own paid membership - see SOURCES.md)
python _Helpers/scrape_skool.py

# Format all .odin + ```odin``` blocks in the working tree
python _Helpers/format_odin_in_files.py --path odin-knowledge-base
````

Requirements: Python 3.10+, `pip install requests beautifulsoup4 markdownify lxml`.

### Personal setup (paths and credentials)

All machine-specific paths and credentials live in a single gitignored file: `_Helpers/.private/user_config.json`.

Setup:

```bash
cp _Helpers/docs/user_config.example.json _Helpers/.private/user_config.json
# edit the copy with your actual paths
```

The loader `_Helpers/lib/user_config.py` exposes them to the scrapers and `format_odin_in_files.py`. Override any value with an env var (e.g. `ODINFMT_EXE`, `BOOK_HTML_SRC`).
Keep credentials out of the JSON - use env vars like `SKOOL_PASSWORD` for secrets.

## Built with MiniMax-M3

This whole project - the scraper architecture, the frontmatter schema, the agent prompts, the 6 Kilo skills, the subagent design, the lint configs - was designed and iterated with [MiniMax-M3](https://minimax.io), powered via [Kilo Code](https://kilo.ai) as the agentic IDE.
M3 acts as the structural engineer; I act as the domain curator.

Every file in this repo is the result of a prompt + a code review between us. There is no `git blame` you can read to tell which line was M3's first draft and which was my edit - that's the point.

For the technical story of how M3 is used in this repo, see [`_Helpers/docs/MINIMAX_M3.md`](_Helpers/docs/MINIMAX_M3.md).

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

1. **Scraper maintenance** - keeping `scrape_skool.py`, `scrape-official.py`, `scrape-zylinski.py` resilient against site changes, rate limits, and bot detection.
2. **New sources** - book ISBN API, dod-benchmarks tracker, official newsletter parser, etc.
3. **AI integration polish** - more Kilo skills, smarter subagent routing, frontmatter improvements for Obsidian / RAGnarok compatibility.
4. **Documentation** - English translations of French-only docs, code samples, video walkthroughs for the trickier topics (hot-reload, allocator patterns).

Sponsoring is entirely optional. The repo and the KB stay MIT-licensed and free to use regardless.
