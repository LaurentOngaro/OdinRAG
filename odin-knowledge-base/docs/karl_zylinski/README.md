# odin-knowledge-base/docs/karl_zylinski/ - public index of zylinski.se content

> This folder is the **public landing** for the Karl Zylinski (`zylinski.se`) content.
> The scraped articles themselves are **not** redistributed in this repo - see [`../../../SOURCES.md`](../../../SOURCES.md) § 2 for licensing and how to obtain them legally on your own.

## What's here

Only `README.md` (this file) is present in the **public branch** of this repo.
The actual blog articles (`*.md` per post) and the `odin-book/` split of the paid ebook are **tracked in the local `main` branch** and pushed to the private remote `OdinRag-private`.
They are excluded from the public `public` branch via the **two-branch strategy**, NOT via `.gitignore`.
Canonical reference: [`007_mixing_public_and_private_history.md`](../../../_Helpers/docs/007_mixing_public_and_private_history.md).

## How to populate this locally

If you want the full articles on your machine:

1. Read [`../../../SOURCES.md`](../../../SOURCES.md) § 2 (blog) and § 3 (ebook) for licensing.
2. Authenticate nothing - `zylinski.se` is public.
3. Run:

   ```bash
   python _Helpers/scripts/scrappers/scrape_zylinski.py            # re-entrant: skip already scraped
   python _Helpers/scripts/scrappers/scrape_zylinski.py --force    # force re-write
   ```

   Output (local only): 20+ files at the root of this folder, one per blog post,
   discovered via RSS / sitemap / crawl.

4. For the ebook (requires the paid HTML file), see
   [`../../../SOURCES.md`](../../../SOURCES.md) § 3.

## What topics are covered

Articles that the scraper can pull (specific count depends on your local run):

- Philosophy: _A Programming Language for Me_, _Know Why You Don't Like OOP_, _Writing a Book About Odin_, _Solo Devs and the Trap of the Game Engine_
- Allocators: _Dynamic Arrays and Arenas_, _Temporary Allocator - Your First Arena_, _Handle-Based Arrays_, _Handle-Based Maps - Three Implementations_
- Hot reload: _Hot Reload Gameplay Code_
- Bindings: _Generate Odin Bindings for C Libraries_
- Intro: _Introduction to Odin_
- Gamedev: _No-Engine Gamedev Using Odin and Raylib_, _GameDev for Beginners Using Odin and Raylib_ (3 parts)
- Data: _Data-Oriented Ideas for Small GameDev Teams_
- Strings / UTF-8: _Iterating Strings and Manually Decoding UTF-8_
- Audio: _Audio in Karl2D - Software Mixing_
- Namespaces: _TOM's Namespaces_

## See also

- [`../official/`](../official/) - Odin official docs (public, included)
- [`../newsletters/`](../newsletters/) - Odin newsletters index
- [`../../../SOURCES.md`](../../../SOURCES.md) - source procurement guide
