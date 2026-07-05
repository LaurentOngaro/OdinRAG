# README - scrappers

## Contents

- `scrape_*.py` - one scraper per source (official, zylinski, gingerbill, jakubtomsu, newsletters, showcase, skool)
- `download_*.py` - one-shot downloaders for tracked code references (`download_gists.py`, `download_odin_examples.py`)

## Conventions

- Every scraper is re-entrant: by default it skips already scraped files. Use `--force` to rewrite.
- Scraped output goes under `odin-knowledge-base/docs/<source>/` for public sources. Paid sources (Skool PVG courses, Karl Zylinski ebook) are written under `odin-knowledge-base/courses/` and `odin-knowledge-base/docs/karl_zylinski/odin-book/` respectively, **tracked in local `main`** and pushed to the private remote `OdinRag-private`, **absent from the public `public` branch** (two-branch strategy, not `.gitignore`).

## Cross-references

Full folder tree: [`001_folder_structure.md`](../../../docs/001_folder_structure.md)
