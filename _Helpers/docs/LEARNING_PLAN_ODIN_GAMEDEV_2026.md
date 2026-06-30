# Odin Learning Plan - Advanced Game Dev (2026)

## Overview

This plan IS MAINLY PERSONAL and has to be adapted to the individual developer's needs

Currently, it targets a developer who :

- has already completed the Odin 2025 introductory tutorials,
- owns Karl Zylinski's book ([odinbook.com](https://odinbook.com))
- is following the [programvideogames.com](https://programvideogames.com) course (as paid member), and has finished the first two modules (introductory and metroidvania).

The goal is to consolidate Odin mastery, deepen game-dev-specific patterns, and set up a local RAG dedicated to Odin / game dev in VS Code.

---

## Selected sources - 2026 reference

### Primary sources (essential, non-redundant)

| Source                                                                                                         | Type                           | Level                 | Status                                                            |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------ | --------------------- | ----------------------------------------------------------------- |
| [odin-lang.org/docs/overview](https://odin-lang.org/docs/overview/)                                            | Official docs                  | All                   | Live - nightly `dev-2026-06`                                      |
| [odin-lang.org/news](https://odin-lang.org/news/)                                                              | Official blog / newsletter     | All                   | Newsletter Q4-2025/Q1-2026 published                              |
| [pkg.odin-lang.org](https://pkg.odin-lang.org/)                                                                | Core/vendor packages reference | Intermediate+         | Live                                                              |
| [github.com/odin-lang/Odin - demo.odin](https://github.com/odin-lang/Odin/blob/master/examples/demo/demo.odin) | Official examples              | Intermediate          | Essential reference                                               |
| **Book**: _Understanding the Odin Programming Language_ - Karl Zylinski                                        | Book (already owned)           | Intermediate/Advanced | Main reference - manual memory, DOD, polymorphism                 |
| **Course**: [programvideogames.com](https://programvideogames.com)                                             | Structured course (Skool)      | Intermediate/Advanced | 104 lessons including 52 Metroidvania + 42 RPG                    |
| [zylinski.se](https://zylinski.se) - Karl Zylinski blog                                                        | Blog / Articles                | Intermediate/Advanced | Recent post April 2025 on no-engine gamedev; hot-reload article   |
| [github.com/karl-zylinski](https://github.com/karl-zylinski)                                                   | Templates + source code        | Advanced              | Hot-reload Raylib template, Sokol template                        |
| [github.com/jakubtomsu/awesome-odin](https://github.com/jakubtomsu/awesome-odin)                               | Aggregator resource            | All                   | 724 stars - exhaustive libs/bindings/gists list                   |
| [GingerGames YouTube](https://youtube.com/c/GingerGames)                                                       | YouTube - language creator     | Advanced              | Official language videos + UB behaviours (Sept. 2025)             |
| [Karl Zylinski YouTube](https://youtube.com/@karl_zylinski) - Snake + Breakout                                 | YouTube                        | Already seen (2025)   | Keep as reference                                                 |
| [forum.odin-lang.org](https://forum.odin-lang.org)                                                             | Official forum                 | All                   | Active in 2026                                                    |
| [discord.com/invite/odinlang](https://discord.com/invite/odinlang)                                             | Official Discord               | All                   | `#beginners` + `#gamedev` channels                                |
| [Memory Allocation Strategies - GingerBill](https://www.gingerbill.org/series/memory-allocation-strategies/)   | Article series                 | Advanced              | Absolute reference series on allocators                           |
| [jakubtomsu gists](https://gist.github.com/jakubtomsu)                                                         | Advanced gists                 | Advanced              | Collision, curves, fontstash, sokol_gfx - active until March 2025 |

### Sources to exclude

- Any Odin vs other languages presentation/comparison video (no longer relevant at this stage)
- Karl Zylinski's Snake/Breakout tutorials (already done in 2025)
- The Odin **Project** (web platform, no relation to Odin the language)
- Resources older than 2023 or not updated for 18+ months
- LLMs to generate Odin code: outputs are often outdated

---

## VS Code + RAG workspace architecture

### Recommended VS Code setup

**Must-have extensions:**

- `OLS` (DanielGavin) - Odin language server with autocompletion, hover, navigation
- `Odin` (Luke Wilson) - complementary syntax and snippets
- `RAGnarok` (hyorman) - local RAG based on LanceDB + local embeddings (ONNX/wasm), supports PDF/Markdown/HTML/code, fully offline

**OLS configuration (`ols.json`) at the workspace root:**

```json
{
  "collections": [
    { "name": "core", "path": "/path/to/Odin/core" },
    { "name": "vendor", "path": "/path/to/Odin/vendor" },
    { "name": "game", "path": "./src" }
  ],
  "enable_semantic_tokens": true,
  "enable_document_symbols": true,
  "enable_hover": true,
  "enable_snippets": true,
  "odin_command": "/path/to/odin"
}
```

**Recommended debugger:** RAD Debugger (Epic Games, open-source) or RemedyBG - both support the `.pdb` files generated by Odin with `-debug`.

### Odin RAG project structure

```
/odin-knowledge-base/
├── docs/
│   ├── official/          # markdown dump of odin-lang.org/docs
│   ├── karl_zylinski/     # zylinski.se articles (markdown scraped)
│   ├── newsletters/       # official newsletters Q1-Q4
│   └── awesome-odin.md    # copy of awesome-odin README
├── code/
│   ├── templates/         # hot-reload template, sokol template
│   ├── gists/             # jakubtomsu gists (collision, curves...)
│   └── examples/          # demo.odin + core examples
├── projects/
│   └── devlog/            # your .md devlogs per project
├── courses/
│   └── programvideogames/ # notes + code from the Skool course
└── ols.json
```

With RAGnarok, each folder is indexed as a **separate Topic**. At minimum, create:

1. `Topic: odin-official` -> `docs/official/`
2. `Topic: zylinski` -> `docs/karl_zylinski/` + `code/templates/`
3. `Topic: gamedev-libs` -> `awesome-odin.md` + `code/gists/`
4. `Topic: devlog` -> `projects/devlog/`

---

## Progressive learning plan (6 months)

### Phase 1 - Consolidation and tooling (Weeks 1-3)

**Goals:** Flawless working environment, exhaustive stdlib knowledge.

### Week 1 - Setup and audit

- Install OLS from sources (build.bat/build.sh) and configure VS Code
- Set up the RAG workspace (structure above) + RAGnarok
- Scrape and index: `odin-lang.org/docs/overview`, newsletters, `demo.odin`
- Read the official article _Moving Towards a New `core:os`_ (Oct. 2025)

### Week 2 - Deep core library

- Browse `core:mem`, `core:slice`, `core:math/linalg`, `core:reflect` in the compiler sources (Zylinski tip: read core sources as documentation)
- Exercise: implement a custom pool allocator, compare with `core:mem.pool_allocator`
- Re-read the memory chapters of the Zylinski book (allocators, temp allocator, tracking allocator)

### Week 3 - Advanced toolchain

- Hot reload: study the [odin-raylib-hot-reload-game-template](https://github.com/karl-zylinski/odin-raylib-hot-reload-game-template) line by line
- Read Zylinski's _Hot Reload Gameplay Code_ article
- `-vet`, `-strict-style`, debug flags: integrate into VS Code `tasks.json`
- Exercise: adapt the hot-reload template for a small personal mini-project

---

### Phase 2 - Advanced game dev patterns (Weeks 4-8)

**Goals:** Master idiomatic Odin patterns for game dev - unions, SOA, ECS-lite, state machines.

### Week 4 - Unions and state machines

- GingerGames video: _Gameplay State Machines Using Unions Great Odin Feature_ (2023, still relevant)
- Implement a complete game state machine (menu -> gameplay -> pause -> game over) with tagged unions
- Exercise: compare with a proc-pointer approach and measure readability

### Week 5 - Data-Oriented Design in practice

- Reference article: _Data-Oriented Design_ book online (Ericson/Acton)
- Odin supports native `#soa`: experiment SoA vs AoS on 10,000 entities with `core:time` for benchmarking
- Study [jakubtomsu/sds](https://github.com/jakubtomsu/sds) - static data structures
- Read [zylinski_odin-dod-benchmarks](file:16) (already in the Space files)

### Week 6 - Entity management without heavy ECS

- "There is no Entity" architecture: separate component tables indexed by integer ID
- Study the source code of [CAT & ONION](https://github.com/karl-zylinski) and [Solar Storm renderer article](https://zylinski.se)
- Implement a minimal entity system (spawn, update, destroy) without allocation per frame
- Continue the Metroidvania module of the [programvideogames.com] course

### Week 7 - Raylib / Sokol rendering pipeline

- Compare the two approaches: Raylib (simplicity) vs Sokol (control, WASM)
- Study [odin-sokol-terrain-example](https://github.com/karl-zylinski/odin-sokol-terrain-example) by Zylinski
- Exercise: port a simple GLSL shader to Sokol in Odin
- Optional: test WASM compilation with `odin-raylib-web`

### Week 8 - Serialization and assets

- `core:encoding/json`: saves, configuration, levels
- [LBP Serialization](https://github.com/jakubtomsu/awesome-odin) for binary scene serialization
- [LDtk loader](https://github.com/jakubtomsu/odin-ldtk) for 2D levels (Dead Cells creator)
- [Aseprite loader](https://github.com/jakubtomsu/awesome-odin) for animated sprites
- Exercise: full asset -> Odin struct -> Raylib render pipeline

---

### Phase 3 - Structured personal project (Weeks 9-16)

**Goals:** Consolidate by practice on a real project, applying the System Stack of the programvideogames course.

#### Weeks 9-10 - Project architecture

- Apply the **System Stack** (programvideogames course, modules 1-2 already done)
- Define the 5 layers of the project (Foundations -> View -> Simulation -> Mechanics -> Narrative)
- Set up hot-reload from the first commit
- Index the project code into RAGnarok (Topic: my-project)

#### Weeks 11-12 - Gameplay core loop

- Continue the RPG modules of the course (42 lessons, ~80% available)
- Implement: input, delta time, collision, basic pathfinding
- Use [pathgrid](https://github.com/jakubtomsu/awesome-odin) for 2D pathfinding
- Profile with Tracy ([Odin bindings](https://github.com/jakubtomsu/awesome-odin)) from this phase

#### Weeks 13-14 - Polish and "juiciness"

- Camera with lerp, screen shake, minimal particle system
- Animations with [Anima](https://github.com/jakubtomsu/awesome-odin) (2D lib inspired by LÖVE)
- Audio with `vendor:miniaudio`
- Integrate a debug UI with `vendor:microui`

#### Weeks 15-16 - Build, distribution, devlog

- Release build with `-o:speed` and strip symbols
- Test web compilation (Raylib or Sokol)
- Write the first structured devlog in `projects/devlog/` (indexed in RAG)
- Take stock: what questions remain open? -> prioritise for Phase 4

---

### Phase 4 - Advanced mastery (Months 5-6)

**Goals:** C bindings, metaprogramming, contribution to the ecosystem.

**C bindings**

- Read [zylinski_odin-c-bindgen](file:17) and the _Bindings to C_ article
- Exercise: create bindings for a small C lib (Box2D, FreeType...)
- Tool [odin-c-bindgen](https://github.com/karl-zylinski/odin-c-bindgen) by Zylinski

**Metaprogramming and `intrinsics`**

- `core:reflect`: type_info, runtime struct field iteration
- `#soa`, `#sparse`, `#simd`: when and why
- GingerGames video: _Does Odin have "Undefined Behaviour"?_ (Sept. 2025)
- Read the compiler sources (`core/` folder) to understand advanced patterns

**Contribution and watch**

- Submit a gist or a small lib on GitHub with the `odin-lang` tag
- Join the [Odin 7 Day Jam](https://itch.io/jam/odin-7-day-jam) (2026 edition)
- Subscribe to the official newsletter and to the `r/odinlang` subreddit

---

## Resources synthesis table

| Resource                      | Format            | Usage frequency   | Priority |
| ----------------------------- | ----------------- | ----------------- | -------- |
| odin-lang.org/docs + packages | Docs              | Daily (reference) | high     |
| odinbook.com (Zylinski)       | Book              | Phase 1-2         | high     |
| programvideogames.com         | Video/text course | Weekly            | high     |
| zylinski.se blog              | Articles          | As needed         | high     |
| awesome-odin (jakubtomsu)     | Reference         | Discovery         | high     |
| GingerGames YouTube           | Advanced videos   | Phase 2-4         | medium   |
| Memory Allocation Strategies  | Article series    | Phase 1-2         | high     |
| forum.odin-lang.org           | Forum             | Occasional        | medium   |
| Odin Discord                  | Chat              | Quick unblocking  | medium   |
| jakubtomsu gists              | Code              | Phase 2-3         | medium   |
| odin-lang.org/news            | Newsletter        | Monthly           | medium   |

---

## VS Code RAG checklist - Initial setup

- [ ] Install OLS from source + configure `ols.json`
- [ ] Install RAGnarok (VS Code Marketplace: `hyorman.ragnarok`)
- [ ] Create the knowledge base folder structure
- [ ] Index: `odin-lang.org/docs/overview` (export markdown)
- [ ] Index: official newsletters 2025-2026
- [ ] Index: full `awesome-odin` README
- [ ] Index: zylinski.se articles (hot-reload, no-engine gamedev, DOD benchmarks)
- [ ] Index: official `demo.odin`
- [ ] Index: programvideogames course notes as you go
- [ ] Create separate RAGnarok topics per domain (official, zylinski, gamedev-libs, devlog)
- [ ] Test semantic search: "context allocator game loop", "SoA entities", "hot reload DLL"

---

## Notes on Skool scraping

The Skool API is private and requires browser automation.
The `skool-cli` (npm) tool offers `list-lessons` and `list-courses` commands via Playwright to extract the detailed content. Once scraping is done, the lessons in Markdown can be indexed directly in RAGnarok as a dedicated `programvideogames` Topic.

---

## Odin 2026 roadmap

The language is considered "essentially finished" by its creators.
The expected 2026 changes are minor (HTTP library in core:net, consolidation of `core:os`).
The stability guarantees that the patterns learned today remain valid.

---

## References

1. [odin-lang.org/docs/overview](https://odin-lang.org/docs/overview/) - Official Odin documentation.
2. [odin-lang.org/news](https://odin-lang.org/news/) - Official Odin news and newsletters.
3. [Understanding the Odin Programming Language](https://odinbook.com) - Karl Zylinski's book.
4. [Structured Game Programming in Odin - Program Video Games](https://programvideogames.com) - Skool course.
5. [No-engine gamedev using Odin + Raylib](https://zylinski.se/posts/no-engine-gamedev-using-odin-and-raylib/) - Karl Zylinski.
6. [odin-raylib-hot-reload-game-template](https://github.com/karl-zylinski/odin-raylib-hot-reload-game-template) - Karl Zylinski's hot-reload Raylib template.
7. [RAGnarok - Local RAG for Copilot](https://marketplace.visualstudio.com/items?itemName=hyorman.ragnarok) - VS Code extension for local RAG.
8. [Gameplay State Machines Using Unions](https://www.youtube.com/watch?v=bGc7C3U89-I) - GingerGames on Odin's unions.
9. [Data-Oriented Design book online](https://www.dataorienteddesign.com/dodmain/node1.html) - Ericson/Acton reference.
10. [Memory Allocation Strategies - GingerBill](https://www.gingerbill.org/series/memory-allocation-strategies/) - The canonical series on allocators.
11. [Odin 7 Day Jam](https://itch.io/jam/odin-7-day-jam) - Annual Odin game jam.
12. [forum.odin-lang.org](https://forum.odin-lang.org/latest) - Official Odin forum.
13. [r/odinlang](https://www.reddit.com/r/odinlang/) - Odin subreddit.
14. [discord.com/invite/odinlang](https://discord.com/invite/odinlang) - Official Odin Discord.
