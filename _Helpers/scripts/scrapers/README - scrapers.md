# README - scrapers

## Files in this folder

### Scrapers (`scrape_*.py`)

One scraper per source. Each one is re-entrant (skips already scraped files by default, `--force` to rewrite) and runs every `\u0060\u0060\u0060odin\u0060\u0060\u0060` block of its output through `odinfmt` (or the whole `.odin` file when applicable) via `fixes/odin_format.format_path_if_odin(..., silent=True)`.

- `scrape_official.py` - odin-lang.org docs + the awesome-odin README → `odin-knowledge-base/docs/official/`.
- `scrape_zylinski.py` - Karl Zylinski blog articles → `odin-knowledge-base/docs/karl_zylinski/`.
- `scrape_gingerbill.py` - gingerbill.org blog articles via RSS → `odin-knowledge-base/docs/gingerbill/`.
- `scrape_jakubtomsu.py` - Jakub Tomsu blog articles → `odin-knowledge-base/docs/jakubtomsu/`.
- `scrape_newsletters.py` - odin-lang.org/news/ newsletters → `odin-knowledge-base/docs/newsletters/`.
- `scrape_showcase.py` - odin-lang.org/showcase/ pages → `odin-knowledge-base/docs/showcase/`.
- `scrape_skool.py` - Skool `programvideogames` group, paywalled, tracks in `main`, absent from `public` → `odin-knowledge-base/courses/programvideogames/`.
- `scrape_odin_changelog.py` - odin-lang/Odin GitHub releases → `odin-knowledge-base/docs/official/changelog/`.
- `scrape_raylib_changelog.py` - raysan5/raylib GitHub releases → `odin-knowledge-base/docs/raylib/changelog/`.

### Downloaders (`download_*.py`)

Re-entrant downloaders for tracked code references (raw `.odin` source, formatted on write by `odinfmt`).

- `download_odin_examples.py` - official Odin example files → `code/examples/`.
- `download_gists.py` - public GitHub gists referenced from `awesome-odin.md` → `code/gists/`.

### Build helpers

- `build_gitingest.py` - `gitingest` snapshots per repo listed in `_Helpers/config/gitIngest_repos.jsonc` → `odin-knowledge-base/gitIngest/`.
- `run_all_scrapers.py` - interactive orchestrator. Lists every `*.py` in this folder, parses the description from its module docstring, then asks `[O/n/q]` confirmation before launching each. Supports `--check` (dry-run listing), `--yes` (non-interactive), and repeatable `--only` / `--skip` substring filters. Exit codes: 0 success, 1 no match, 2 at least one failure, 130 user-aborted.

### Runtime

- `logs/` - append-only per-scraper log files (`logs/<script>.log`). One file per run, never truncated unless the scraper is invoked with `--log-reset` (where supported).

## Conventions

- **Re-entrant by default**: every scraper skips already scraped files. Use `--force` to rewrite.
- **odinfmt on every write**: every `.odin` file and every `\u0060\u0060\u0060odin\u0060\u0060\u0060` block written by a scraper goes through `odinfmt` (via `format_path_if_odin`). This guarantees 2-space indentation + LF newlines (per `odinfmt.json` at repo root).
- **Imports**: scrapers add `sys.path.insert(0, str(Path(__file__).resolve().parent.parent))` (= `_Helpers/scripts/`) and then use `from lib.X import ...` / `from fixes.X import ...`. The absolute `_Helpers.scripts.X` form is forbidden: it requires the repo root on `sys.path` and breaks in subprocess/child contexts (every failed import reported so far traced back to this pattern).
- **Output paths**: public sources go under `odin-knowledge-base/docs/<source>/`. Paid sources (Skool PVG courses, Karl Zylinski ebook) go under `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/` respectively, **tracked in local `main`** and pushed to the private remote `OdinRag-private`, **absent from the public `public` branch** (two-branch strategy, not `.gitignore`).
- **No tabs**: 2 spaces, LF newlines. Enforced by the repo root `odinfmt.json`.
- **Pylance**: every `.py` in this folder is checked by `python _Helpers/scripts/fixes/lint_pylance.py <file>` after each edit. 0 errors / 0 warnings is the gate.

## Cross-references

- Full folder tree: [`001_folder_structure.md`](../../../docs/001_folder_structure.md).
- Scraper runbook (flags, prereqs, common diagnostics): [`.kilo/skills/scraper-runner/SKILL.md`](../../../.kilo/skills/scraper-runner/SKILL.md).
- Pre-push audit (public-branch leak detection): [`.kilo/skills/audit-public-safety/SKILL.md`](../../../.kilo/skills/audit-public-safety/SKILL.md).
- Markdown style + lint gates (one-paragraph-per-line, ASCII punctuation): [`.kilo/skills/markdown-style/SKILL.md`](../../../.kilo/skills/markdown-style/SKILL.md).
