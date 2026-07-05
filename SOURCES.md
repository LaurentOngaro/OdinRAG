# SOURCES - How to obtain the content referenced by this KB

> The scrapers in `_Helpers/` target external sources that are **not redistributed** in this repository.
> This page lists every source, the licence / paywall status, and how to obtain it on your own so the scrapers work for you.

## Convention: samples vs full corpus

To keep this repo small and the licensing clear, the **public branch** of this repository ships a **curated subset** of each source:

- **Fully shipped** (Odin team content under MIT-style): `odin-knowledge-base/docs/official/`, `odin-knowledge-base/docs/newsletters/`, `odin-knowledge-base/docs/showcase/`.
- **5 sample articles shipped** (© authors, public-readable): `odin-knowledge-base/docs/karl_zylinski/`, `odin-knowledge-base/docs/gingerbill/`, `odin-knowledge-base/docs/jakubtomsu/`.
- **NOT in the public `public` branch** (paid / paywall), but **tracked in the local `main` branch** and pushed to the private remote `OdinRag-private`: `odin-knowledge-base/docs/karl_zylinski/odin-book/`, `odin-knowledge-base/courses/`.

The exclusion mechanism for the last category is the **two-branch strategy** (local `main` ↔ private remote / local `public` ↔ public remote), NOT `.gitignore`. See [`_Helpers/docs/007_mixing_public_and_private_history.md`](../_Helpers/docs/007_mixing_public_and_private_history.md).

To populate the full corpus of any sample source, run the corresponding scraper (`python _Helpers/scripts/scrapers/scrape_<source>.py`). All scrapers are idempotent.

## 1. Odin official documentation

| Source                                                                                    | Licence                                          | How to obtain                                      |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| `odin-lang.org/docs/*` (overview, install/\*, packages, statements, types, procedures...) | MIT-style (Odin source repo is BSD-3 / MIT-like) | Free, no auth: <https://odin-lang.org/docs/>       |
| `github.com/jakubtomsu/awesome-odin`                                                      | CC0 (curated list)                               | Free: <https://github.com/jakubtomsu/awesome-odin> |

**What ships in this repo**: every scraped official page, in `odin-knowledge-base/docs/official/`.

**Scraper**: `_Helpers/scripts/scrapers/scrape_official.py` (sitemap + crawl + static fallback).

## 2. Karl Zylinski blog (`zylinski.se`)

| Source                                 | Licence                                                  | How to obtain                        |
| -------------------------------------- | -------------------------------------------------------- | ------------------------------------ |
| Individual blog posts on `zylinski.se` | © Karl Zylinski, all rights reserved (publicly readable) | Free to read: <https://zylinski.se/> |

**What ships in this repo**: 5 sample articles in `odin-knowledge-base/docs/karl_zylinski/` (representative selection covering hot-reload, allocators, gamedev, c-bindgen, DOD). Run `python _Helpers/scripts/scrapers/scrape_zylinski.py` to populate the full corpus (19 posts).

**Scraper**: `_Helpers/scripts/scrapers/scrape_zylinski.py` (RSS auto-discovery + sitemap + crawl).

## 3. "Understanding the Odin Programming Language" (Karl Zylinski, ebook)

| Source                                   | Licence                                      | How to obtain                                                           |
| ---------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| Full HTML ebook (split into 33 chapters) | © Karl Zylinski, **paid** (commercial ebook) | Purchase on itch.io: <https://karl-zylinski.itch.io/understanding-odin> |

If you own the ebook:

1. Save the `understanding_the_odin_programming_language.html` file anywhere on disk.
2. Fill in `paths.karl_book_html` in your `_Private/.config/user_config.jsonc` (see [`_Helpers/templates/user_config.example.jsonc`](../_Helpers/templates/user_config.example.jsonc)) or set the `BOOK_HTML_SRC` env var.
3. Run:

   ```bash
   python _Helpers/scripts/fixes/book_html_to_md.py
   ```

4. Output: `odin-knowledge-base/docs/karl_zylinski/odin-book/01-...33-about-the-author.md` (33 MD files).

**Where the output lives**: the 33 chapters are **tracked in the local `main` branch** and pushed to the private remote `OdinRag-private`.
They are **absent from the public `public` branch** (so a fresh `git clone` of `github.com/LaurentOngaro/OdinRAG` won't see them).
The exclusion is done via the two-branch strategy, not `.gitignore`. Local `git status` keeps them hidden via `.git/info/exclude` (LOCAL only).

**What ships in the public branch of this repo**: an `odin-book/README.md` index of the 33 chapters (the only file in the public branch).

## 4. Odin newsletters

| Source                              | Licence                                   | How to obtain                       |
| ----------------------------------- | ----------------------------------------- | ----------------------------------- |
| Each issue at `odin-lang.org/news/` | MIT-style (Odin project official content) | Free: <https://odin-lang.org/news/> |

**What ships in this repo**: 32 scraped newsletters in `odin-knowledge-base/docs/newsletters/` (all issues).

**Scraper**: `_Helpers/scripts/scrapers/scrape_newsletters.py` (crawl).

## 5. Ginger Bill's blog (gingerbill.org)

| Source                                | Licence                                                | How to obtain                                       |
| ------------------------------------- | ------------------------------------------------------ | --------------------------------------------------- |
| Articles on `gingerbill.org/article/` | © Ginger Bill, all rights reserved (publicly readable) | Free to read: <https://www.gingerbill.org/article/> |

**What ships in this repo**: 5 sample articles in `odin-knowledge-base/docs/gingerbill/` (representative selection covering C/Zig comparisons, allocators, Odin philosophy, relative-pointers). Run `python _Helpers/scripts/scrapers/scrape_gingerbill.py` to populate the full corpus (44 posts).

**Scraper**: `_Helpers/scripts/scrapers/scrape_gingerbill.py` (RSS).

## 6. Jakub Tomsu's blog (jakubtomsu.github.io)

| Source                                    | Licence                           | How to obtain                                 |
| ----------------------------------------- | --------------------------------- | --------------------------------------------- |
| Articles on `jakubtomsu.github.io/posts/` | © Jakub Tomsu (publicly readable) | Free to read: <https://jakubtomsu.github.io/> |

**What ships in this repo**: 4 sample articles in `odin-knowledge-base/docs/jakubtomsu/` (representative selection covering bit-pools, game loop, renderer, validation). Run `python _Helpers/scripts/scrapers/scrape_jakubtomsu.py` to populate the full corpus (11 posts).

**Scraper**: `_Helpers/scripts/scrapers/scrape_jakubtomsu.py` (RSS).

## 7. Odin Showcase

| Source                                      | Licence                                   | How to obtain                           |
| ------------------------------------------- | ----------------------------------------- | --------------------------------------- |
| Showcase pages at `odin-lang.org/showcase/` | MIT-style (Odin project official content) | Free: <https://odin-lang.org/showcase/> |

**What ships in this repo**: 7 scraped showcase pages in `odin-knowledge-base/docs/showcase/` (all pages).

**Scraper**: `_Helpers/scripts/scrapers/scrape_showcase.py` (crawl).

## 8. Skool "programvideogames" group (Vertical Slice and Dice + Metroidvania courses)

| Source                                                          | Licence                                       | How to obtain                                              |
| --------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------- |
| All Skool "programvideogames" lessons (Vertical Slice and Dice) | © course author, **paid membership required** | Join the group: <https://www.skool.com/programvideogames/> |

> **Note on ToS**: scraping behind Skool's login with your own credentials is a grey area.
> The repository ships **only the scraper**, not the lessons. Personal use (indexing for yourself, querying through your own LLM) is generally tolerated;
> **do not redistribute the scraped output publicly**.

**What ships in this repo**: the scraper `_Helpers/scripts/scrapers/scrape_skool.py`. Lesson metadata (slug, duration, module) is also written locally only.

**Prerequisites** (see AGENTS.md for full setup):

- `npm install -g skool-cli`
- `npx playwright install chromium`
- Authenticate with your paid Skool account in the browser session
- Run `python _Helpers/scripts/scrapers/scrape_skool.py`

## 9. Odin & Raylib changelogs (GitHub Releases API)

| Source                               | Licence                                   | How to obtain                                      |
| ------------------------------------ | ----------------------------------------- | -------------------------------------------------- |
| `github.com/odin-lang/Odin/releases` | MIT-style (Odin project official content) | Free: <https://github.com/odin-lang/Odin/releases> |
| `github.com/raysan5/raylib/releases` | zlib/libpng (Raylib, free redistribution) | Free: <https://github.com/raysan5/raylib/releases> |

**What ships in this repo**:

- `odin-knowledge-base/docs/official/changelog/` - 20 last Odin releases (one `.md` per release + one consolidated `odin_changelog.md`).
- `odin-knowledge-base/docs/raylib/changelog/` - 10 last Raylib releases (same layout).

**Scrapers**:

- `_Helpers/scripts/scrapers/scrape_odin_changelog.py`
- `_Helpers/scripts/scrapers/scrape_raylib_changelog.py`

Both are idempotent (frontmatter `tag:` check), support `--check` dry-run and an optional `GITHUB_TOKEN` env var for the 5000 req/hour rate limit.

## 10. GitIngest snapshots (Perplexity Space fallback layer)

| Source                              | Licence                          | How to obtain                                                           |
| ----------------------------------- | -------------------------------- | ----------------------------------------------------------------------- |
| Local clones of public GitHub repos | Same as the upstream (MIT-style) | Free: `git clone <url>` from the upstream, then point the script at it. |

> **Purpose**: when MCP GitHub is unavailable or you want a permanent "context anchor" in the Perplexity Space, the `gitingest` CLI produces a single `.txt` per repo that bundles the whole project tree in one file. See `_Private/raw/Perplexity backlog/2026-07-04_04_odin_assistant_optimisation_espace_perplexity.md` for the strategic rationale.

**What ships in this repo**: `odin-knowledge-base/gitIngest/` (20 snapshots + 20 sidecar `.json` + `README - gitIngest.md`).

**Generator**: `_Helpers/scripts/scrapers/build_gitingest.py`. Reads `_Helpers/config/gitIngest_repos.jsonc` and runs `gitingest` on each entry. Idempotent (`--check` dry-run, `--force` rewrite, `--only <id>` filter).

**Important**:

- This folder is **regenerated on demand**, never pushed to the public branch by default. Add it to `.gitignore` if you fork a private repo you don't want tracked.
- Snapshots are **fallback context, not primary source of truth**. The curated KB under `odin-knowledge-base/docs/` is always preferred over a raw gitIngest dump when available.
- The Perplexity Space should only ingest the small curated files (changelogs, INDEX, charte) - NOT the bulk snapshots. See the backlog doc for the precise keep/drop list.

## 11. Code references (always-public)

| Source                                          | Licence               | How to obtain                                                                                                 |
| ----------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------- |
| Official Odin examples (10 .odin files)         | Odin core (MIT-style) | Bundled in Odin releases, also at <https://github.com/odin-lang/Odin/tree/master/examples/demo>               |
| `code/examples/*` (ships: `demo.odin` + README) | Odin core (MIT-style) | Scraper: `_Helpers/scripts/scrapers/download_odin_examples.py` pulls them locally (tracked: `demo.odin` only) |
| 25 public gists from awesome-odin               | Public, MIT-style     | Scraper: `_Helpers/scripts/scrapers/download_gists.py`                                                        |
| `code/gists/*`                                  | Public, MIT-style     | See file headers for attribution                                                                              |
| `code/vendored templates/*`                     | MIT (this repo)       | Bundled in this repo                                                                                          |

## Attributions & trademarks

- "Odin" is a programming language by [Ginger Bill](https://github.com/gingerBill).
- "Odin" and the Odin logo are trademarks of their respective owners.
- "Raylib" is by [Ramon Santamaria](https://www.raylib.com/).
- "Sokol" is by [Andre Weissflog](https://github.com/floooh/sokol).
- Skool is a paid community platform at <https://www.skool.com>.

This project is unofficial and unaffiliated with any of the above. It is a personal RAG workflow maintained by the repo author.
