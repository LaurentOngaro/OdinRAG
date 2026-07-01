# odin-knowledge-base/docs/gingerbill/ - public index of gingerbill.org content

> This folder is the **public landing** for the Ginger Bill (`gingerbill.org`) content.
> The scraped articles themselves are **not** redistributed in this repo - see
> [`../../../SOURCES.md`](../../../SOURCES.md) for licensing and how to obtain them legally on your own.

## What's here

Only `README.md` (this file). The actual blog articles (`*.md` per post) are excluded
from the public repo by design (see the `COPYRIGHTED SCRAPED CONTENT` section of the root `.gitignore`).

## How to populate this locally

If you want the full articles on your machine:

1. Read [`../../../SOURCES.md`](../../../SOURCES.md) for licensing.
2. Authenticate nothing - `gingerbill.org` is public.
3. Run:

   ```bash
   python _Helpers/scripts/scrappers/scrape_gingerbill.py            # re-entrant: skip already scraped
   python _Helpers/scripts/scrappers/scrape_gingerbill.py --force    # force re-write
   ```

   Output (local only): 40+ files at the root of this folder, one per blog post,
   discovered via RSS.

## What topics are covered

Articles that the scraper can pull (specific count depends on your local run):

- **The Aesthetic Problem of Namespacing** (2026-05-13) - https://www.gingerbill.org/article/2026/05/13/aesthetic-namespacing
- **Signed By Default Camp** (2026-05-03) - https://www.gingerbill.org/article/2026/05/03/signed-by-default
- **Blessed Syntax and Ergonomics** (2026-04-29) - https://www.gingerbill.org/article/2026/04/29/blessed-syntax-and-ergonomics
- **Odin's Fiasco with Wikipedia** (2026-04-20) - https://www.gingerbill.org/article/2026/04/20/odin-wikipedia-fiasco
- **Designing Odin's Casting Syntax** (2026-02-23) - https://www.gingerbill.org/article/2026/02/23/designing-odins-casting-syntax
- **Does Syntax Matter?** (2026-02-21) - https://www.gingerbill.org/article/2026/02/21/does-syntax-matter
- **Choosing a Language Based on its Syntax?** (2026-02-19) - https://www.gingerbill.org/article/2026/02/19/choosing-a-language-based-on-syntax
- **The Only Two Markup Languages** (2026-01-19) - https://www.gingerbill.org/article/2026/01/19/two-families-of-markup-languages
- **Mitigating the Billion Dollar Mistake** (2026-01-11) - https://www.gingerbill.org/article/2026/01/11/mitigating-the-billion-dollar-mistake
- **Was it really a Billion Dollar Mistake?** (2026-01-02) - https://www.gingerbill.org/article/2026/01/02/was-it-really-a-billion-dollar-mistake
- **contextâ€”Odin's Most Misunderstood Feature** (2025-12-15) - https://www.gingerbill.org/article/2025/12/15/odins-most-misunderstood-feature-context
- **Package Managers are Evil** (2025-09-08) - https://www.gingerbill.org/article/2025/09/08/package-managers-are-evil
- **If Odin Had Macros** (2025-07-31) - https://www.gingerbill.org/article/2025/07/31/if-odin-had-macros
- **Unstructured Thoughts on the Problems of OSS/FOSS** (2025-04-22) - https://www.gingerbill.org/article/2025/04/22/unstructured-thoughts-on-oss
- **OpenGL is not Right-Handed** (2024-11-10) - https://www.gingerbill.org/article/2024/11/10/opengl-is-not-right-handed
- **Marketing the Odin Programming Language is Weird** (2024-09-08) - https://www.gingerbill.org/article/2024/09/08/odin-weird-to-market
- **Why People are Angry over Go 1.23 Iterators** (2024-06-17) - https://www.gingerbill.org/article/2024/06/17/go-iterator-design
- **String Type Distinctions** (2024-04-05) - https://www.gingerbill.org/article/2024/04/05/string-type-distinctions
- **The Video That Inspired Me To Create Odin** (2024-04-04) - https://www.gingerbill.org/article/2024/04/04/video-that-inspired-odin
- **Why I Hate Language Benchmarks** (2024-01-22) - https://www.gingerbill.org/article/2024/01/22/comparing-language-benchmarks
- **Reverse Engineering Alembic** (2022-07-11) - https://www.gingerbill.org/article/2022/07/11/reverse-engineering-alembic
- **Multiple Return Values Research** (2021-12-15) - https://www.gingerbill.org/article/2021/12/15/multiple-return-values-research
- **Memory Allocation Strategies - Part 6** (2021-12-02) - https://www.gingerbill.org/article/2021/12/02/memory-allocation-strategies-006
- **Memory Allocation Strategies - Part 5** (2021-11-30) - https://www.gingerbill.org/article/2021/11/30/memory-allocation-strategies-005
- **The Value Propagation Experiment Part 2** (2021-09-06) - https://www.gingerbill.org/article/2021/09/06/value-propagation-experiment-part-2
- **The Value Propagation Experiment** (2021-07-05) - https://www.gingerbill.org/article/2021/07/05/value-propagation-experiment
- **Untyped Types** (2021-03-07) - https://www.gingerbill.org/article/2021/03/07/untyped-types
- **Structured Control Flow (Brain Dump)** (2021-02-02) - https://www.gingerbill.org/article/2021/02/02/structured-control-flow
- **The Essence of Programming** (2021-02-01) - https://www.gingerbill.org/article/2021/02/01/the-essence-of-programming
- **The Fatal Flaw of Ownership Semantics** (2020-06-21) - https://www.gingerbill.org/article/2020/06/21/the-ownership-semantics-flaw
- **Flash Fads Model (Audio Article)** (2020-06-13) - https://www.gingerbill.org/article/2020/06/13/flash-fads-model
- **Pragmatism in Programming Proverbs** (2020-05-31) - https://www.gingerbill.org/article/2020/05/31/programming-pragmatist-proverbs
- **Relative Pointers** (2020-05-17) - https://www.gingerbill.org/article/2020/05/17/relative-pointers
- **A Reply to _Let's stop copying C_** (2020-01-25) - https://www.gingerbill.org/article/2020/01/25/a-reply-to-lets-stop-copying-c
- **A Reply to _The Road to Zig 1.0_** (2019-05-13) - https://www.gingerbill.org/article/2019/05/13/a-reply-to-the-road-to-zig
- **A Quine in Odin** (2019-03-10) - https://www.gingerbill.org/article/2019/03/10/quine-in-odin
- **Memory Allocation Strategies - Part 4** (2019-02-16) - https://www.gingerbill.org/article/2019/02/16/memory-allocation-strategies-004
- **Memory Allocation Strategies - Part 3** (2019-02-15) - https://www.gingerbill.org/article/2019/02/15/memory-allocation-strategies-003
- **Memory Allocation Strategies - Part 2** (2019-02-08) - https://www.gingerbill.org/article/2019/02/08/memory-allocation-strategies-002
- **Memory Allocation Strategies - Part 1** (2019-02-01) - https://www.gingerbill.org/article/2019/02/01/memory-allocation-strategies-001
- **ExceptionsAnd Why Odin Will Never Have Them** (2018-09-05) - https://www.gingerbill.org/article/2018/09/05/exceptions---and-why-odin-will-never-have-them
- **On the Aesthetics of the Syntax of Declarations** (2018-03-12) - https://www.gingerbill.org/article/2018/03/12/on-the-aesthetics-of-the-syntax-of-declarations
- **The Metaprogramming Dilemma** (2016-12-01) - https://www.gingerbill.org/article/2016/12/01/the-metaprogramming-dilemma
- **A Defer Statement For C++11** (2015-08-19) - https://www.gingerbill.org/article/2015/08/19/defer-in-cpp

## See also

- [`../official/`](../official/) - Odin official docs (public, included)
- [`../karl_zylinski/`](../karl_zylinski/) - Karl Zylinski blog index
- [`../newsletters/`](../newsletters/) - Odin newsletters index
- [`../../../SOURCES.md`](../../../SOURCES.md) - source procurement guide
