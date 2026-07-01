---
title: "README - scrappers"
date: "2026-07-01"
tags: [OdinRAG, reference]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# README - scrappers

## Contents

- `scrape_*.py` - one scraper per source (official, zylinski, gingerbill, jakubtomsu, newsletters, showcase, skool)
- `download_*.py` - one-shot downloaders for tracked code references (`download_gists.py`, `download_odin_examples.py`)

## Conventions

- Every scraper is re-entrant: by default it skips already scraped files. Use `--force` to rewrite.
- Scraped output goes under `odin-knowledge-base/docs/<source>/` (gitignored where the source is paid).

## Cross-references

Full folder tree: [`001_folder_structure.md`](../../../docs/001_folder_structure.md)
