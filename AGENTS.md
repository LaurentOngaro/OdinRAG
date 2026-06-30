# AGENTS.md - Context for AI coding agents (Kilo Code, Claude Code, etc.)

> This file is read first by AI coding agents to understand the structure, conventions, and tools of the OdinRAG repository. > **Keep it up to date** when the structure evolves.
> Built with **MiniMax-M3** via [Kilo Code](https://kilo.ai). See [`_Helpers/docs/MINIMAX_M3.md`](_Helpers/docs/MINIMAX_M3.md) for the technical story.

## TL;DR

OdinRAG is a **RAG knowledge base** for Odin (a systems language by Ginger Bill) applied to game development (Raylib, Sokol, hot-reload, allocators). The project:

- Scrapes + formats external doc into structured Markdown folders (Skool, odin-lang.org, Karl Zylinski's blog).
- Acts as curated context for AI assistants when developing Odin projects (gamedev, CLI tools, etc.).
- Is **not** an Odin project itself - but it can contain projects (demos, courses, tutorials) as reference.

The scraped content of paywalled or copyrighted sources is **never redistributed in this public repo** - see [`SOURCES.md`](SOURCES.md) for how to obtain each source legally on your own.

## Repository structure

````
OdinRAG/
├── README.md                        Index (read first)
├── SOURCES.md                       How to obtain the scraped content
├── LICENSE                          MIT
├── AGENTS.md                        This file - AI context
├── kilo.json / .kilo/kilo.jsonc     Kilo runtime config
├── odinfmt.json                     Odin formatter config (2-space, LF)
├── .markdownlint.json / .markdownlintignore
├── .editorconfig                    Base style
│
├── planning/                        Day-by-day planning
│   ├── ROADMAP.md                   Phases + milestones
│   ├── template/J_YYYY-MM-DD.md     Daily template (DO NOT EDIT)
│   └── daily/J_YYYY-MM-DD.md        Daily entries (gitignored)
│
├── docs/                            External documentation (publicly scrapable)
│   ├── official/                    odin-lang.org/docs/ (MIT-style, mirrored in repo)
│   ├── karl_zylinski/               zylinski.se (README only - see SOURCES.md § 2)
│   ├── newsletters/                 odin-lang.org/news/ (README only - § 4)
│   ├── gingerbill/                  gingerbill.org articles (public RSS)
│   ├── jakubtomsu/                  jakubtomsu.github.io articles (public RSS)
│   └── showcase/                    odin-lang.org/showcase/ (public)
│
├── code/                            Examples and templates
│   ├── examples/                    demo.odin (official)
│   ├── gists/                       Public gists (cloneable)
│   ├── templates/                   Project templates (cloneable)
│   │
├── _Helpers/                        ★ SCRIPTS AND LIBRARY
│   ├── scrape_skool.py              Active: scrapes the programvideogames Skool group
│   ├── scrape-official.py           Re-entrant: scrapes odin-lang.org/docs
│   ├── scrape-zylinski.py           Re-entrant: scrapes zylinski.se
│   ├── scrape-gingerbill.py         RSS: scrapes gingerbill.org (public)
│   ├── scrape-newsletters.py        Crawl: scrapes odin-lang.org/news/ (public)
│   ├── scrape-jakubtomsu.py         RSS: scrapes jakubtomsu.github.io (public)
│   ├── scrape-showcase.py           Crawl: scrapes odin-lang.org/showcase/ (public)
│   ├── book_html_to_md.py           Converts Karl's HTML ebook → per-chapter MD
│   ├── format_odin_in_files.py      CLI: format .odin + ```odin``` blocks via odinfmt
│   ├── build_kb_index.py            Regenerates odin-knowledge-base/INDEX.md
│   ├── download_gists.py            CLI: download public gists from awesome-odin
│   ├── download_odin_examples.py    CLI: download official Odin examples
│   ├── lint_pylance.py              CLI: run pyright on Python files
│   ├── fix_mojibake.py              CLI: repair UTF-8/Latin-1 mojibake in files
│   ├── audit_public_safety.py       Public-safety gate (run before any public push)
│   ├── lib/                         Shared library
│   │   ├── text_clean.py            repair_mojibake (UTF-8/Latin-1)
│   │   ├── http_client.py           fetch, normalize_url, sitemap/RSS parsers
│   │   ├── html2md.py               scrape_to_markdown (BeautifulSoup + markdownify)
│   │   └── user_config.py           Personal config loader (env > JSON > empty)
│   ├── archives/                    One-shot scripts (kept for audit, initially empty)
│   ├── logs/                        Cumulative logs (gitignored)
│   └── docs/                        Internal docs + social post templates
│
└── odinfmt.json                     (duplicate above the _Helpers/ block)
````

> Note: `odin-knowledge-base/` and the legacy `courses/` folder (containing the paid Skool scrape) are gitignored by design. They live only on the local machine that produced them.

## Dependencies

| Software             | Install                                                                            | Used by                           |
| -------------------- | ---------------------------------------------------------------------------------- | --------------------------------- |
| Python 3.10+         | system / `pyenv` / `conda`                                                         | Scrapers + audit + format scripts |
| `requests`/`bs4`/    | `pip install requests beautifulsoup4 markdownify lxml`                             | `scrape-*.py`, `html2md.py`       |
| `markdownify`/`lxml` | (same)                                                                             | (same)                            |
| `odinfmt` (ols)      | Download from <https://github.com/DanielGavin/ols/releases> (or build from source) | `format_odin_in_files.py`         |
| `skool-cli`          | `npm install -g skool-cli`                                                         | Optional - Skool scraping         |
| Playwright/Chromium  | `npx playwright install chromium`                                                  | Optional - Skool auth UI          |

### User config (personal paths and credentials)

All machine-specific paths and credentials live in a single gitignored file:`_Helpers/.private/user_config.jsonc`.
The loader is `_Helpers/lib/user_config.py`.

Setup:

```bash
cp _Helpers/docs/user_config.example.jsonc _Helpers/.private/user_config.jsonc
# edit the copy with your actual paths
```

Scripts that need personal info read from this config (with env var override):

| Script                        | Field                  | Env var                                 |
| ----------------------------- | ---------------------- | --------------------------------------- |
| `_Helpers/odin_format.py`     | `paths.odinfmt_exe`    | `ODINFMT_EXE`                           |
| `_Helpers/scrape_skool.py`    | `paths.yt_dlp_exe`     | `YT_DLP_EXE`                            |
| `_Helpers/scrape_skool.py`    | `skool.email`          | `SKOOL_EMAIL`                           |
| `_Helpers/scrape_skool.py`    | (password)             | `SKOOL_PASSWORD` (env ONLY, never JSON) |
| `_Helpers/book_html_to_md.py` | `paths.karl_book_html` | `BOOK_HTML_SRC`                         |
| `_Helpers/book_html_to_md.py` | `paths.karl_book_out`  | `BOOK_HTML_OUT`                         |

Chain of resolution per value: **env var > user_config.jsonc > empty string**.

## Conventions

### Markdown (knowledge base)

- **Frontmatter** - see [`_Helpers/docs/FRONTMATTER_CONVENTIONS.md`](_Helpers/docs/FRONTMATTER_CONVENTIONS.md) for the full schema (5 main fields + hierarchical Obsidian tags).
- Scraped Skool lessons have a scraping frontmatter (`Cours`, `Module`, `ID`, `Durée`) which can be extended with `topic/*` for classification.
- **2-space** indentation inside ```odin ...``` blocks (no tabs, no smart tabs). Configured via `odinfmt.json` at repo root.
- **LF** newlines everywhere (even on Windows).
- Inter-file links: relative `./module/lesson.md` or absolute from repo root.
- Unicode characters in content: OK (curly quotes, em-dashes, box-drawing).

### Planning (day-by-day)

- **Daily** entries live in `planning/daily/J_YYYY-MM-DD.md`, created each working day.
- **Template** in `planning/template/J_YYYY-MM-DD.md` is the reference - duplicate, never edit.
- **Roadmap** in `planning/ROADMAP.md` covers phases P0-P4.
- `TODO.md` is legacy - migrate progressively to the daily system.
- No retroactive dating - only create dailies for days actually worked.
- End-of-day **bilan** section is mandatory in each daily (never folded into "in progress").

### Python (scrapers)

- Python 3.10+, stdlib preferred. Minimal external dependencies.
- Style: `snake_case`, type hints, docstrings on public functions.
- Encoding: UTF-8 everywhere. `sys.stdout.reconfigure(encoding="utf-8")` at the top of every CLI script (with `# type: ignore[attr-defined]`).
- Lint: Pylance-compatible (no flake8/black enforced).
- No `print()` for debug - use `_log(level, msg)` and a structured logger.
- **After any edit to a `.py` file, run `python _Helpers/lint_pylance.py <file>` and fix every reported warning before considering the task done.** The script wraps `pyright` (CLI engine behind Pylance) and exits non-zero on remaining warnings.

### Durable vs one-shot scripts

> **Rule**: if an operation (indexing, reformatting, parsing, anything that **must be repeated** whenever a folder is updated), it MUST be implemented as a durable script in `_Helpers/` (idempotent CLI + `--check` for dry-run).
> Never as a throwaway script in a system temp folder (e.g. `/tmp/` on Unix, `%TEMP%` on Windows).

Examples of durable scripts that already live in `_Helpers/`:

- `build_kb_index.py` - regenerates `odin-knowledge-base/INDEX.md`
- `format_odin_in_files.py` - reformats `.odin` and  ```odin ...```  blocks
- `book_html_to_md.py` - converts Karl's HTML book → per-chapter MD
- `scrape_*.py` - re-scrape the KB

These scripts must:

1. Be idempotent (re-run = no-op if nothing changed)
2. Have a `--check` dry-run option
3. Log clearly what they're doing (`print(f"[+] {file}...")`)
4. Exit non-zero on error

### Odin (in the KB)

- No compilable Odin source in this repo.
- ```odin ...```  blocks in `.md` files are formatted by `odinfmt` automatically after each scrape, or manually via `_Helpers/format_odin_in_files.py --path odin-knowledge-base`.

## Style rules (project-wide)

These rules apply to every tracked `.md` file in this repo unless the file is explicitly excluded (see notes below).

### Punctuation: no em-dash

- **Never use the em-dash (Em dash) character (U+2014).** Use a plain ASCII hyphen-minus (`-`, U+002D) instead.
- Reason: some terminals and markdown renderers mishandle the en-dash / em-dash glyph (Windows terminals can render them as a question mark box), which breaks copy-paste and visual consistency. ASCII hyphen-minus renders the same everywhere.
- The same applies to other Unicode punctuation: prefer ASCII `'` over `'`, `"` over `"`/`"`, `-` over `-`/`-`, `...` over `...`. The lint config already enforces most of these via `MD026`.

### Markdown line length: no auto-wrap (book style, not 80s code style)

- **Do not auto-wrap or truncate Markdown lines at any character limit.** The markdownlint config explicitly disables `MD013` (line length rule). Lines stay as long as they need to be.
- **Preferred style: prose like a book, not like 80s code.** One sentence can be one line; one paragraph can be one line; only insert a line break where there is a logical separation (paragraph end, list item, heading, table row).
- When in doubt, write the paragraph as a single line. Editors (VS Code, Obsidian, etc.) can soft-wrap visually without inserting hard breaks.
- When editing an existing file, do NOT insert line breaks inside sentences, links, or table cells just to fit a magic number.

#### Concrete examples

WRONG (artificial wrap, "code of the 80s"):

```markdown
This is a paragraph that wraps at 80 chars because the
formatter or the author thought 80 was a magic number.
It makes prose harder to read because each line ends
mid-thought and the eye has to jump to find the
continuation.
```

RIGHT (book style, one paragraph = one line):

```markdown
This is a paragraph that wraps at 80 chars because the formatter or the author thought 80 was a magic number. It makes prose harder to read because each line ends mid-thought and the eye has to jump to find the continuation.
```

WRONG (truncated table cell):

```markdown
| Source  | Files |
| ------- | ----- |
| foo.md  | 12    |
| bar.md  | 7     |
```

RIGHT (table cells may exceed 120 chars if needed):

```markdown
| Source                | Files | Description                                                                              |
| --------------------- | ----- | ---------------------------------------------------------------------------------------- |
| `foo.md` (very long)  | 12    | A long description that legitimately needs more than 120 chars to be clear and complete. |
| `bar.md`              | 7     | Short description.                                                                       |
```

#### Why this matters

- Forced wrapping breaks sentence rhythm. Authors wrap where it makes sense; the formatter does not.
- Forcing a re-flow on every edit churns the git diff and makes code reviews unreadable.
- Soft-wrap in editors is the right solution when the user wants a narrow visual line.

#### For AI agents

When writing or editing a `.md` file, never break a sentence across multiple lines just to stay under a character limit. Write each paragraph as a single line; use double newlines only between paragraphs.

### Language: English only

- **All tracked `.md` files must be in English.** The repo is public and international. Any file authored or translated must be English. The same applies to frontmatter (`title`, `summary`).
- **Exception** (gitignored, exempt): `planning/daily/J_YYYY-MM-DD.md` - the author's personal daily notes. These never reach the public repo, so the author's preferred language is fine.
- Reason: consistency for search, AI tooling (the subagent prompt expects English keywords), and international contributors.

### Frontmatter / file conventions (unchanged)

The detailed rules for frontmatter, indentation, line endings, and code blocks remain in the subsections above. The style rules in this section are **additive** - they do not relax any other convention.

## Kilo sub-agents

See [`.kilo/agents/odin-gamedev.md`](.kilo/agents/odin-gamedev.md) for the specialised subagent (Odin gamedev, allocator patterns, etc.).

## Kilo skills

| Skill                               | Usage                                                                 |
| ----------------------------------- | --------------------------------------------------------------------- |
| `.kilo/skills/odin-format/`         | Re-format a single Odin file or a `.md`                               |
| `.kilo/skills/scraper-runner/`      | Run a scraper with the right flags                                    |
| `.kilo/skills/kb-navigator/`        | Search the KB by topic / frontmatter                                  |
| `.kilo/skills/odin-pattern-finder/` | Find a precise Odin pattern (state machine, allocator, hot reload...) |
| `.kilo/skills/planning-helper/`     | Manage `planning/daily/J_YYYY-MM-DD.md` (create, update, list)        |
| `.kilo/skills/pylance-check/`       | Run pyright on Python files and fix diagnostics                       |

## Anti-patterns

- they are auto-generated by `scrape_skool.py`.
- Editing them → overwritten on next scrape (unless `--force`).
- **Do NOT manually edit** files under `odin-knowledge-base/courses/*/`
- **Do NOT touch** `docs/official/` and `docs/karl_zylinski/` by hand for the same reason (README additions are OK).
- **Do NOT rename** KB folders without updating the generated indexes.

## Git workflow - always require user validation

- **NEVER** run `git commit` or `git push` without an explicit user request.
- After any modification (code, docs, configs, structure), stage the changes with `git add` and present a clear summary of what changed, then **WAIT** for the user to say "commit", "push", "OK to commit", or equivalent.
- If the user only asks for a fix / edit / dry-run, stop after the local edit. Do not interpret silence as approval.
- **Exception**: trivial tasks explicitly framed as "commit and push this" may proceed without a second confirmation, but the summary must be shown before the action.
- This rule exists to keep the user in control of every public mutation. The audit trail must remain their decision.

## Push to the public repo - checklist

Before any push to `github.com/LaurentOngaro/OdinRAG`:

1. `python _Helpers/audit_public_safety.py` → **must** exit 0.
2. Verify `.gitignore` `COPYRIGHTED SCRAPED CONTENT` section is intact.
3. Verify no `planning/daily/` or `_Raw/` files are staged.

Full procedure in [`_Helpers/docs/PUBLIC_RELEASE_CHECKLIST.md`](_Helpers/docs/PUBLIC_RELEASE_CHECKLIST.md).

## Alternate indexes (Kilo + RAG)

This project does not use RAGnarök yet. KB search currently goes through:

1. Kilo's global context (workspace = all tracked files of the repo).
2. Frontmatter semantic filtering (`Cours:`, `Module:`, `ID:`).
3. Kilo slash commands (see `kilo.json`).

If the workspace exceeds ~5000 files or latency becomes a problem, switch to RAGnarök or a dedicated vector index.
