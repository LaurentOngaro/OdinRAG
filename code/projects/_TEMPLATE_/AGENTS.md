# <PROJECT_NAME> - Context for Kilo

## Goal

- _One sentence: what this project does._

## Stack

- _e.g. `vendor:raylib` + core + base_

## Main KB sources (exact paths)

> These 3-5 files are what Kilo will consult when helping you on this project.
> Format: `relative/path.md` - relevant section.

- `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/<MODULE>/<lesson>.md`
- `docs/karl_zylinski/odin-book/<NN>-<chapter>.md`
- `docs/official/<page>.md`

## Patterns already implemented

Check off as you go to give Kilo context on what is already in place.

- [ ] _e.g. Tracking allocator for debug_ (lesson 088)
- [ ] _e.g. Entity update loop_ (lesson 14)
- [ ] _e.g. Push/pop arena scope_ (lesson 13)

## Pitfalls identified (DO NOT fall for them again)

- _e.g. no `using` on entity fields (lesson 5 + Karl 23.1)_
- _e.g. prefer arena in production, tracking_allocator only in debug_

## Architectural decisions

- _e.g. Why arena over heap: pattern "many small allocations, freed all at once"_
- _e.g. Why no ECS with inheritance: indirection overhead + cache miss_

## Naming / style conventions

- _Odin conventions: PascalCase for types, snake_case for procs, etc._
- _See `AGENTS.md` at the root for global conventions._
