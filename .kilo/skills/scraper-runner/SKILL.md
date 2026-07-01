---
name: scraper-runner
description: Run a scraper (_Helpers/scripts/scrappers/scrape_*.py) with the right flags. Covers scrape_skool (Skool programvideogames), scrape_official (odin-lang.org), scrape_zylinski (zylinski.se), scrape_gingerbill.py, scrape_newsletters.py, scrape_jakubtomsu.py, scrape_showcase.py, download_gists.py, download_odin_examples.py. All re-entrant.
---

# Run a scraper

Skill for re-running one of the project's scrapers.
All scrapers are **re-entrant**: an already exported file is skipped unless `--force` is passed.

## Overview

| Scraper                     | Source                             | Output                                           | Prerequisites            |
| --------------------------- | ---------------------------------- | ------------------------------------------------ | ------------------------ |
| `scrape_skool.py`           | Skool "programvideogames"          | `odin-knowledge-base/courses/programvideogames/` | skool-cli + Playwright   |
| `scrape-official.py`        | odin-lang.org/docs/ + awesome-odin | `odin-knowledge-base/docs/official/`             | requests + BeautifulSoup |
| `scrape-zylinski.py`        | zylinski.se blog                   | `odin-knowledge-base/docs/karl_zylinski/`        | requests + BeautifulSoup |
| `scrape-gingerbill.py`      | gingerbill.org RSS                 | `odin-knowledge-base/docs/gingerbill/`           | requests + BeautifulSoup |
| `scrape-newsletters.py`     | odin-lang.org/news/                | `odin-knowledge-base/docs/newsletters/`          | requests + BeautifulSoup |
| `scrape-jakubtomsu.py`      | jakubtomsu.github.io RSS           | `odin-knowledge-base/docs/jakubtomsu/`           | requests + BeautifulSoup |
| `scrape-showcase.py`        | odin-lang.org/showcase/            | `odin-knowledge-base/docs/showcase/`             | requests + BeautifulSoup |
| `download_gists.py`         | awesome-odin gist URLs             | `code/gists/`                                    | None (stdlib urllib)     |
| `download_odin_examples.py` | Odin repo examples/                | `code/examples/`                                 | None (stdlib urllib)     |

## How

### Re-scrape a source (idempotent skip)

```bash
python _Helpers/scripts/scrappers/scrape_official.py
python _Helpers/scripts/scrappers/scrape_zylinski.py
python _Helpers/scripts/scrappers/scrape_skool.py
```

-> Skip already-present files, only write new ones.

### Force a full rewrite

```bash
python _Helpers/scripts/scrappers/scrape_official.py --force
python _Helpers/scripts/scrappers/scrape_zylinski.py --force
python _Helpers/scripts/scrappers/scrape_skool.py --overwrite-existing-lessons
```

-> Rewrite ALL files (useful after a KB refactor or an HTML format change on the source side).

### scrape_skool - useful options

```bash
# A single lesson (fuzzy title filter)
python _Helpers/scripts/scrappers/scrape_skool.py --lesson "entities state physics"

# Resume after an interruption (skip the first 50)
python _Helpers/scripts/scrappers/scrape_skool.py --skip-until 50

# Also download YouTube videos
python _Helpers/scripts/scrappers/scrape_skool.py --download-video

# Also download the ZIPs attached to lessons
python _Helpers/scripts/scrappers/scrape_skool.py --download-support-files

# With explicit credentials (otherwise interactive prompt)
export SKOOL_EMAIL="your@email.com"
export SKOOL_PASSWORD="yourpassword"
python _Helpers/scripts/scrappers/scrape_skool.py
```

Exit codes:

- `0`: success
- `1`: missing prerequisites (skool-cli not found, credentials missing)
- `2`: (reserved)

## Prerequisites per scraper

### scrape_skool

1. **Node.js**: <https://nodejs.org/>
2. **skool-cli**: `npm install -g skool-cli`
3. **Playwright Chromium**: `npx playwright install chromium`
4. **skool-cli patches** (anti-bot AWS WAF + retry goto):

- On Windows: `%AppData%\npm\node_modules\skool-cli\dist\core\browser-manager.js`
- On Windows: `%AppData%\npm\node_modules\skool-cli\dist\core\page-ops.js`

1. **yt-dlp** (if `--download-video`): any directory on your PATH is fine
2. **Skool credentials**:

- Env var `SKOOL_EMAIL` / `SKOOL_PASSWORD`, OR
- File `_Private/.config/skool_credentials.txt` (gitignored)

1. **Windows**: disable Defender firewall (Playwright Chromium otherwise fails with `ERR_NETWORK_ACCESS_DENIED`)

### scrape-official / scrape-zylinski

```bash
pip install requests beautifulsoup4 markdownify lxml
```

## Diagnostics

### Typical successful output

```
=== With -config odinfmt.json ===
odinfmt : <path-to-odinfmt>/odinfmt.exe
Mode    : WRITE
Target  : odin-knowledge-base

Scanned   : TBD  (depends on your KB)
Modified  : 0   <- already clean
Errors    : 0
```

### Common errors

| Error                                 | Cause                               | Fix                                         |
| ------------------------------------- | ----------------------------------- | ------------------------------------------- |
| `[ERR] skool-cli not found`           | `npm install -g skool-cli` not done | Run the command                             |
| `ERR_NETWORK_ACCESS_DENIED`           | Windows firewall blocks Playwright  | Disable Defender or add an exception        |
| `Sign in to confirm you're not a bot` | YouTube rate-limit                  | Wait + add `YOUTUBE_COOKIES_FILE`           |
| `HTTP Error 429/403`                  | YouTube anti-bot                    | Automatic exponential backoff (90/180/360s) |
| `[ERR] odinfmt exit=1`                | Odin syntax error                   | Fix the source code                         |
| `Missing path to format`              | odinfmt called without argument     | Add `-stdin` or a file                      |

## Anti-patterns

- Do NOT delete `_Helpers/scripts/fixes/fix_mojibake.py` even if the KB is clean: it is a safety net if a new scrape introduces mojibake.
- Do NOT disable re-entrancy by adding an automatic `force`. Idempotence is valuable for large KBs (Skool courses can run into the hundreds of lessons).
- Do NOT scrape in `--force` mode without running `--check` first to estimate the scope of the changes.
