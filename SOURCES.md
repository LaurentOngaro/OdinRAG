# SOURCES - How to obtain the content referenced by this KB

> The scrapers in `_Helpers/` target external sources that are **not redistributed** in this repository.
> This page lists every source, the licence / paywall status, and how to obtain it on your own so the scrapers work for you.

## Convention: samples vs full corpus

To keep this repo small and the licensing clear, the public repository ships a **curated subset** of each source:
- **Fully shipped** (Odin team content under MIT-style): `docs/official/`, `docs/newsletters/`, `docs/showcase/`.
- **5 sample articles shipped** (© authors, public-readable): `docs/karl_zylinski/`, `docs/gingerbill/`, `docs/jakubtomsu/`.
- **NOT shipped** (paid / paywall): `docs/karl_zylinski/odin-book/`, `odin-knowledge-base/courses/`.

To populate the full corpus of any sample source, run the corresponding scraper (`python _Helpers/scrape-<source>.py`). All scrapers are idempotent.

## 1. Odin official documentation

| Source                                                                                    | Licence                                          | How to obtain                                      |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------- |
| `odin-lang.org/docs/*` (overview, install/\*, packages, statements, types, procedures...) | MIT-style (Odin source repo is BSD-3 / MIT-like) | Free, no auth: <https://odin-lang.org/docs/>       |
| `github.com/jakubtomsu/awesome-odin`                                                      | CC0 (curated list)                               | Free: <https://github.com/jakubtomsu/awesome-odin> |

**What ships in this repo**: every scraped official page, in `docs/official/`.

**Scraper**: `_Helpers/scrape-official.py` (sitemap + crawl + static fallback).

## 2. Karl Zylinski blog (`zylinski.se`)

| Source                                 | Licence                                                  | How to obtain                        |
| -------------------------------------- | -------------------------------------------------------- | ------------------------------------ |
| Individual blog posts on `zylinski.se` | © Karl Zylinski, all rights reserved (publicly readable) | Free to read: <https://zylinski.se/> |

**What ships in this repo**: 5 sample articles in `docs/karl_zylinski/` (representative selection covering hot-reload, allocators, gamedev, c-bindgen, DOD). Run `python _Helpers/scrape-zylinski.py` to populate the full corpus (19 posts).

**Scraper**: `_Helpers/scrape-zylinski.py` (RSS auto-discovery + sitemap + crawl).

## 3. "Understanding the Odin Programming Language" (Karl Zylinski, ebook)

| Source                                   | Licence                                      | How to obtain                                                           |
| ---------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------- |
| Full HTML ebook (split into 33 chapters) | © Karl Zylinski, **paid** (commercial ebook) | Purchase on itch.io: <https://karl-zylinski.itch.io/understanding-odin> |

If you own the ebook:

1. Save the `understanding_the_odin_programming_language.html` file anywhere on disk.
2. Fill in `paths.karl_book_html` in your `_Helpers/.private/user_config.json` (see [`_Helpers/docs/user_config.example.json`](../_Helpers/docs/user_config.example.json)) or set the `BOOK_HTML_SRC` env var.
3. Run:

   ```bash
   python _Helpers/book_html_to_md.py
   ```

4. Output: `docs/karl_zylinski/odin-book/01-...33-about-the-author.md` (all gitignored).

**What ships in this repo**: an `odin-book/README.md` index of the 33 chapters.

## 4. Odin newsletters

| Source                              | Licence                                   | How to obtain                       |
| ----------------------------------- | ----------------------------------------- | ----------------------------------- |
| Each issue at `odin-lang.org/news/` | MIT-style (Odin project official content) | Free: <https://odin-lang.org/news/> |

**What ships in this repo**: 32 scraped newsletters in `docs/newsletters/` (all issues).

**Scraper**: `_Helpers/scrape-newsletters.py` (crawl).

## 5. Ginger Bill's blog (gingerbill.org)

| Source                                | Licence                                                | How to obtain                                       |
| ------------------------------------- | ------------------------------------------------------ | --------------------------------------------------- |
| Articles on `gingerbill.org/article/` | © Ginger Bill, all rights reserved (publicly readable) | Free to read: <https://www.gingerbill.org/article/> |

**What ships in this repo**: 5 sample articles in `docs/gingerbill/` (representative selection covering C/Zig comparisons, allocators, Odin philosophy, relative-pointers). Run `python _Helpers/scrape-gingerbill.py` to populate the full corpus (44 posts).

**Scraper**: `_Helpers/scrape-gingerbill.py` (RSS).

## 6. Jakub Tomsu's blog (jakubtomsu.github.io)

| Source                                    | Licence                           | How to obtain                                 |
| ----------------------------------------- | --------------------------------- | --------------------------------------------- |
| Articles on `jakubtomsu.github.io/posts/` | © Jakub Tomsu (publicly readable) | Free to read: <https://jakubtomsu.github.io/> |

**What ships in this repo**: 4 sample articles in `docs/jakubtomsu/` (representative selection covering bit-pools, game loop, renderer, validation). Run `python _Helpers/scrape-jakubtomsu.py` to populate the full corpus (11 posts).

**Scraper**: `_Helpers/scrape-jakubtomsu.py` (RSS).

## 7. Odin Showcase

| Source                                      | Licence                                   | How to obtain                           |
| ------------------------------------------- | ----------------------------------------- | --------------------------------------- |
| Showcase pages at `odin-lang.org/showcase/` | MIT-style (Odin project official content) | Free: <https://odin-lang.org/showcase/> |

**What ships in this repo**: 7 scraped showcase pages in `docs/showcase/` (all pages).

**Scraper**: `_Helpers/scrape-showcase.py` (crawl).

## 8. Skool "programvideogames" group (Vertical Slice and Dice + Metroidvania courses)

| Source                                                          | Licence                                       | How to obtain                                              |
| --------------------------------------------------------------- | --------------------------------------------- | ---------------------------------------------------------- |
| All Skool "programvideogames" lessons (Vertical Slice and Dice) | © course author, **paid membership required** | Join the group: <https://www.skool.com/programvideogames/> |

> **Note on ToS**: scraping behind Skool's login with your own credentials is a grey area.
> The repository ships **only the scraper**, not the lessons. Personal use (indexing for yourself, querying through your own LLM) is generally tolerated;
> **do not redistribute the scraped output publicly**.

**What ships in this repo**: the scraper `_Helpers/scrape_skool.py`. Lesson metadata (slug, duration, module) is also written locally only.

**Prerequisites** (see AGENTS.md for full setup):

- `npm install -g skool-cli`
- `npx playwright install chromium`
- Authenticate with your paid Skool account in the browser session
- Run `python _Helpers/scrape_skool.py`

## 9. Code references (always-public)

| Source                                          | Licence               | How to obtain                                                                                   |
| ----------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------- |
| Official Odin examples (10 .odin files)         | Odin core (MIT-style) | Bundled in Odin releases, also at <https://github.com/odin-lang/Odin/tree/master/examples/demo> |
| `code/examples/*` (ships: `demo.odin` + README) | Odin core (MIT-style) | Scraper: `_Helpers/download_odin_examples.py` pulls them locally (tracked: `demo.odin` only)    |
| 25 public gists from awesome-odin               | Public, MIT-style     | Scraper: `_Helpers/download_gists.py`                                                           |
| `code/gists/*`                                  | Public, MIT-style     | See file headers for attribution                                                                |
| `code/templates/*`                              | MIT (this repo)       | Bundled in this repo                                                                            |

## Attributions & trademarks

- "Odin" is a programming language by [Ginger Bill](https://github.com/gingerBill).
- "Odin" and the Odin logo are trademarks of their respective owners.
- "Raylib" is by [Ramon Santamaria](https://www.raylib.com/).
- "Sokol" is by [Andre Weissflog](https://github.com/floooh/sokol).
- Skool is a paid community platform at <https://www.skool.com>.

This project is unofficial and unaffiliated with any of the above. It is a personal RAG workflow maintained by the repo author.
