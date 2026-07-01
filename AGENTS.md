# AGENTS.md - Context for AI coding agents (Kilo Code, Claude Code, etc.)

> This file is read first by AI coding agents to understand the structure, conventions, and tools of the OdinRAG repository.
> **Keep it up to date** when the structure evolves.
> Built with **MiniMax-M3** via [Kilo Code](https://kilo.ai).
> See [`_Helpers/docs/002_how_minimax-m3_is_used_in_this_repository.md`](_Helpers/docs/002_how_minimax-m3_is_used_in_this_repository.md) for the technical story.

## TL;DR

OdinRAG is a **RAG knowledge base** for Odin (a systems language by Ginger Bill) applied to game development (Raylib, Sokol, hot-reload, allocators). The project:

- Scrapes + formats external doc into structured Markdown folders (Skool, odin-lang.org, Karl Zylinski's blog).
- Acts as curated context for AI assistants when developing Odin projects (gamedev, CLI tools, etc.).
- Is **not** an Odin project itself - but it can contain projects (demos, courses, tutorials) as reference.

The scraped content of paywalled or copyrighted sources is **never redistributed in this public repo** - see [`SOURCES.md`](SOURCES.md) for how to obtain each source legally on your own.

## Repository structure

> **The full tree lives in [`_Helpers/docs/001_folder_structure.md`](_Helpers/docs/001_folder_structure.md).**
> This section gives a one-line summary of each bucket; refer to the structure doc for the complete tree.

- `odin-knowledge-base/` - **Bucket 1** (public, partly gitignored) - scraped KB + Skool courses
- `code/` - public code references (examples, gists, vendored templates, personal projects)
- `_Helpers/` - **Bucket 2** (public) - scripts, meta docs, internal templates, prompts, logs
- `_Private/` - **Bucket 3** (gitignored, never pushed) - config, planning, raw notes

> Note: `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/*.md` are gitignored by design (paywalled sources). They live only on the local machine that produced them.

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

All machine-specific paths and credentials live in a single gitignored file:`_Private/.config/user_config.jsonc`.
The loader is `_Helpers/scripts/lib/user_config.py`.

Setup:

```bash
cp _Helpers/templates/user_config.example.jsonc _Private/.config/user_config.jsonc
# edit the copy with your actual paths
```

Scripts that need personal info read from this config (with env var override):

| Script                                       | Field                  | Env var                                 |
| -------------------------------------------- | ---------------------- | --------------------------------------- |
| `_Helpers/scripts/fixes/odin_format.py`      | `paths.odinfmt_exe`    | `ODINFMT_EXE`                           |
| `_Helpers/scripts/scrappers/scrape_skool.py` | `paths.yt_dlp_exe`     | `YT_DLP_EXE`                            |
| `_Helpers/scripts/scrappers/scrape_skool.py` | `skool.email`          | `SKOOL_EMAIL`                           |
| `_Helpers/scripts/scrappers/scrape_skool.py` | (password)             | `SKOOL_PASSWORD` (env ONLY, never JSON) |
| `_Helpers/scripts/fixes/book_html_to_md.py`  | `paths.karl_book_html` | `BOOK_HTML_SRC`                         |
| `_Helpers/scripts/fixes/book_html_to_md.py`  | `paths.karl_book_out`  | `BOOK_HTML_OUT`                         |

Chain of resolution per value: **env var > user_config.jsonc > empty string**.

## Conventions

### File naming (NNN_ prefix)

- **Default** (authored docs under `_Helpers/docs/` and `_Private/planning/`): filename is `NNN_snake_case_slug.md` (3-digit prefix, lowercase + underscores + hyphens). NNN restarts at 001 in each folder. Chronological by creation date.
- **H1 title = filename exactly** (no leading `NNN_` in the H1 if the filename has one). Examples:
  - `003_yaml_frontmatter_conventions.md` → H1 `# 003_yaml_frontmatter_conventions`
  - `002_how_minimax-m3_is_used_in_this_repository.md` → H1 `# 002_how_minimax-m3_is_used_in_this_repository`
- **FS-unsafe characters forbidden in both filename and H1**: `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`. If the natural title would need one, rephrase.
- **READMEs in authored folders**: filename is `README - <topic>.md` where `<topic>` is the parent directory name. H1 matches the filename (per the rule above). Examples:
  - `_Helpers/scripts/README - scripts.md` → H1 `# README - scripts`
  - `_Helpers/docs/README - docs.md` → H1 `# README - docs`
- **NNN_ prefix is NOT applied** to files in these folder patterns (they keep their natural name):
  - `**/templates/**` (template files keep their semantic name, e.g. `J_YYYY-MM-DD.md`, `main.odin`, `odin-project.md`)
  - `**/planning/**` (planning files use semantic names: `J_YYYY-MM-DD.md`, `NNN_odin_learning_plan_*.md`, `NNN_roadmap.md` - the `NNN_` is REQUIRED here as it's the only way to order them; daily files do NOT use `NNN_`)
  - `**/prompts/**` (prompt files keep their descriptive name, e.g. `refresh_topic_index.md`)
  - `**/scripts/**` (Python files; the directory itself uses NNN_ ordering via its README only)
  - `**/social/**` (one-off social posts, no chronological order)
  - `**/daily/**` (dailies use `J_YYYY-MM-DD.md` - the `J_` prefix is the date tag)
  - `**/raw/**` (raw notes kept as-is, no frontmatter, no NNN_)
  - `code/**` (no NNN_ - code files keep their original names)
  - `odin-knowledge-base/**` (no NNN_ - scraped files keep their original slugs)
- **Dailies are gitignored**: they never reach the public repo, so their filename is purely personal.
- The full authoritative tree is in [`_Helpers/docs/001_folder_structure.md`](_Helpers/docs/001_folder_structure.md).

### Markdown (knowledge base)

- **Frontmatter** - see [`_Helpers/docs/003_yaml_frontmatter_conventions.md`](_Helpers/docs/003_yaml_frontmatter_conventions.md) for the full schema (5 main fields + hierarchical Obsidian tags).
- Scraped Skool lessons have a scraping frontmatter (`Cours`, `Module`, `ID`, `Durée`) which can be extended with `topic/*` for classification.
- **2-space** indentation inside `odin ...` blocks (no tabs, no smart tabs). Configured via `odinfmt.json` at repo root.
- **LF** newlines everywhere (even on Windows).
- Inter-file links: relative `./module/lesson.md` or absolute from repo root.
- Unicode characters in content: OK (curly quotes, em-dashes, box-drawing).

### Planning (day-by-day)

- **Daily** entries live in `_Private/planning/daily/J_YYYY-MM-DD.md`, created each working day.
- **Template** in `_Helpers/templates/planning-daily/J_YYYY-MM-DD.md` is the reference - duplicate, never edit.
- **Roadmap** in `_Private/planning/002_roadmap.md` covers phases P0-P4.
- `TODO.md` is legacy - migrate progressively to the daily system.
- No retroactive dating - only create dailies for days actually worked.
- End-of-day **bilan** section is mandatory in each daily (never folded into "in progress").

### Python (scrapers)

- Python 3.10+, stdlib preferred. Minimal external dependencies.
- Style: `snake_case`, type hints, docstrings on public functions.
- Encoding: UTF-8 everywhere. `sys.stdout.reconfigure(encoding="utf-8")` at the top of every CLI script (with `# type: ignore[attr-defined]`).
- Lint: Pylance-compatible (no flake8/black enforced).
- No `print()` for debug - use `_log(level, msg)` and a structured logger.
- **After any edit to a `.py` file, run `python _Helpers/scripts/fixes/lint_pylance.py <file>` and fix every reported warning before considering the task done.** The script wraps `pyright` (CLI engine behind Pylance) and exits non-zero on remaining warnings.

### Durable vs one-shot scripts

> **Rule**: if an operation (indexing, reformatting, parsing, anything that **must be repeated** whenever a folder is updated), it MUST be implemented as a durable script in `_Helpers/` (idempotent CLI + `--check` for dry-run).
> Never as a throwaway script in a system temp folder (e.g. `/tmp/` on Unix, `%TEMP%` on Windows).

Examples of durable scripts that already live in `_Helpers/`:

- `build_kb_index.py` - regenerates `odin-knowledge-base/INDEX.md`
- `format_odin_in_files.py` - reformats `.odin` and `odin ...` blocks
- `book_html_to_md.py` - converts Karl's HTML book → per-chapter MD
- `scrape_*.py` - re-scrape the KB

These scripts must:

1. Be idempotent (re-run = no-op if nothing changed)
2. Have a `--check` dry-run option
3. Log clearly what they're doing (`print(f"[+] {file}...")`)
4. Exit non-zero on error

### Odin (in the KB)

- No compilable Odin source in this repo.
- `odin ...` blocks in `.md` files are formatted by `odinfmt` automatically after each scrape, or manually via `_Helpers/scripts/fixes/format_odin_in_files.py --path odin-knowledge-base`.

## Style rules (project-wide)

These rules apply to every tracked `.md` file in this repo unless the file is explicitly excluded (see notes below).

### Punctuation: no em-dash

- **Never use the em-dash (Em dash) character (U+2014).** Use a plain ASCII hyphen-minus (`-`, U+002D) instead.
- Reason: some terminals and markdown renderers mishandle the en-dash / em-dash glyph (Windows terminals can render them as a question mark box), which breaks copy-paste and visual consistency. ASCII hyphen-minus renders the same everywhere.
- The same applies to other Unicode punctuation: prefer ASCII `'` over `'`, `"` over `"`/`"`, `-` over `-`/`-`, `...` over `...`. The lint config already enforces most of these via `MD026`.

### Markdown prose

- One paragraph = one physical line. No line break inside a sentence, no matter the line length. Table cells, code blocks, and frontmatter are exempt.
- Detailed rule, examples, and rationale in [`_Helpers/docs/004_markdown_style.md`](_Helpers/docs/004_markdown_style.md) (loaded on demand, not in first-context).

### Markdown structure: READMEs must reflect their directory

Every `README*.md` in this repo must accurately reflect the structure of its host directory:

- Files referenced via `[[wikilinks]]` must exist (otherwise the link is a 404 in the rendered KB).
- Files present in the host directory should be mentioned when a "Files produced" / "Structure" / "Files in this folder" section exists in the README.
- Aspirational READMEs (describing future or planned content) must be marked with a "Structure cible" or "Awaiting content" header so the audit script can skip them.

Verify with:

```bash
python _Helpers/scripts/diagnostic/auditReadmeCoherence.py
```

Non-zero exit code = issues found. Use `--scope <path>` to scope the audit (for example `--scope docs/official`), and `--quiet` to only show the summary line. Add `--fail-on-error` for CI-style use.

### Language: English only

- **All tracked `.md` files must be in English.** The repo is public and international. Any file authored or translated must be English. The same applies to frontmatter (`title`, `summary`).
- **Exception** (gitignored, exempt): `_Private/planning/daily/J_YYYY-MM-DD.md` - the author's personal daily notes. These never reach the public repo, so the author's preferred language is fine.
- Reason: consistency for search, AI tooling (the subagent prompt expects English keywords), and international contributors.

### Frontmatter / file conventions (unchanged)

The detailed rules for frontmatter, indentation, line endings, and code blocks remain in the subsections above. The style rules in this section are **additive** - they do not relax any other convention.

## Kilo sub-agents

See [`.kilo/agents/odin-gamedev.md`](.kilo/agents/odin-gamedev.md) for the specialised subagent (Odin gamedev, allocator patterns, etc.).

## Kilo skills

| Skill                               | Usage                                                                   |
| ----------------------------------- | ----------------------------------------------------------------------- |
| `.kilo/skills/odin-format/`         | Re-format a single Odin file or a `.md`                                 |
| `.kilo/skills/scraper-runner/`      | Run a scraper with the right flags                                      |
| `.kilo/skills/kb-navigator/`        | Search the KB by topic / frontmatter                                    |
| `.kilo/skills/odin-pattern-finder/` | Find a precise Odin pattern (state machine, allocator, hot reload...)   |
| `.kilo/skills/planning-helper/`     | Manage `_Private/planning/daily/J_YYYY-MM-DD.md` (create, update, list) |
| `.kilo/skills/pylance-check/`       | Run pyright on Python files and fix diagnostics                         |

## Anti-patterns

- they are auto-generated by `scrape_skool.py`.
- Editing them → overwritten on next scrape (unless `--force`).
- **Do NOT manually edit** files under `odin-knowledge-base/courses/*/`
- **Do NOT touch** `odin-knowledge-base/docs/official/` and `odin-knowledge-base/docs/karl_zylinski/` by hand for the same reason (README additions are OK).
- **Do NOT rename** KB folders without updating the generated indexes.

## Git workflow - always require user validation

- **NEVER** run `git commit` or `git push` without an explicit user request.
- After any modification (code, docs, configs, structure), stage the changes with `git add` and present a clear summary of what changed, then **WAIT** for the user to say "commit", "push", "OK to commit", or equivalent.
- If the user only asks for a fix / edit / dry-run, stop after the local edit. Do not interpret silence as approval.
- **Exception**: trivial tasks explicitly framed as "commit and push this" may proceed without a second confirmation, but the summary must be shown before the action.
- This rule exists to keep the user in control of every public mutation. The audit trail must remain their decision.

## Push to the public repo - checklist

Before any push to `github.com/LaurentOngaro/OdinRAG`:

1. `python _Helpers/scripts/diagnostic/audit_public_safety.py` → **must** exit 0.
2. Verify `.gitignore` `COPYRIGHTED SCRAPED CONTENT` section is intact.
3. Verify no `_Private/planning/daily/` or `_Private/raw/` files are staged.

Full procedure in [`_Helpers/docs/005_public_release_checklist.md`](_Helpers/docs/005_public_release_checklist.md).

## Alternate indexes (Kilo + RAG)

This project does not use RAGnarök yet. KB search currently goes through:

1. Kilo's global context (workspace = all tracked files of the repo).
2. Frontmatter semantic filtering (`Cours:`, `Module:`, `ID:`).
3. Kilo slash commands (see `kilo.json`).

If the workspace exceeds ~5000 files or latency becomes a problem, switch to RAGnarök or a dedicated vector index.
