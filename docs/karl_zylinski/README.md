# docs/karl_zylinski/ - public index of zylinski.se content

> This folder is the **public landing** for the Karl Zylinski (`zylinski.se`) content.
> The scraped articles themselves are **not** redistributed in this repo - see [`../../SOURCES.md`](../../SOURCES.md) § 2 for licensing and how to obtain them legally on your own.

## What's here

Only `README.md` (this file). The actual blog articles (`*.md` per post) and the `odin-book/` split of the paid ebook are excluded from the public repo by design (see the `COPYRIGHTED SCRAPED CONTENT` section of the root `.gitignore`).

## How to populate this locally

If you want the full articles on your machine:

1. Read [`../../SOURCES.md`](../../SOURCES.md) § 2 (blog) and § 3 (ebook) for licensing.
2. Authenticate nothing - `zylinski.se` is public.
3. Run:

   ```bash
   python _Helpers/scrape-zylinski.py            # re-entrant: skip already scraped
   python _Helpers/scrape-zylinski.py --force    # force re-write
   ```

   Output (local only): 20+ files at the root of this folder, one per blog post,
   discovered via RSS / sitemap / crawl.
4. For the ebook (requires the paid HTML file), see
   [`../../SOURCES.md`](../../SOURCES.md) § 3.

## What topics are covered

Articles that the scraper can pull (specific count depends on your local run):

- Philosophy: *A Programming Language for Me*, *Know Why You Don't Like OOP*, *Writing a Book About Odin*, *Solo Devs and the Trap of the Game Engine*
- Allocators: *Dynamic Arrays and Arenas*, *Temporary Allocator - Your First Arena*, *Handle-Based Arrays*, *Handle-Based Maps - Three Implementations*
- Hot reload: *Hot Reload Gameplay Code*
- Bindings: *Generate Odin Bindings for C Libraries*
- Intro: *Introduction to Odin*
- Gamedev: *No-Engine Gamedev Using Odin and Raylib*, *GameDev for Beginners Using Odin and Raylib* (3 parts)
- Data: *Data-Oriented Ideas for Small GameDev Teams*
- Strings / UTF-8: *Iterating Strings and Manually Decoding UTF-8*
- Audio: *Audio in Karl2D - Software Mixing*
- Namespaces: *TOM's Namespaces*

## See also

- [`../official/`](../official/) - Odin official docs (public, included)
- [`../newsletters/`](../newsletters/) - Odin newsletters index
- [`../../SOURCES.md`](../../SOURCES.md) - source procurement guide
- [`../../_Helpers/docs/MINIMAX_M3.md`](../../_Helpers/docs/MINIMAX_M3.md) - how MiniMax-M3 powers this repo
