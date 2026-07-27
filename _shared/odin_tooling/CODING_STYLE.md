# CODING_STYLE - Odin Project Conventions

> This file is the **canonical reference** for Odin coding conventions used
> across all Odin projects (PVG02, PVG03, Odin_Skeleton, and future ones).
>
> It is read by:
>
> - Humans (developers + reviewers)
> - AI agents (Copilot, Kilo, Claude, etc.) to ground style suggestions
>
> It is enforced by:
>
> - `odinfmt.json` for formatting (auto-rewritten by `odinfmt -w`)
> - `ols.json` + `odin check` for linting (via `check_and_format.bat`)
> - Reviewer judgement for everything else

---

## 1. Indentation and line endings

- **2 spaces, never tabs.**
- **CRLF line endings** (matches Windows-native editor defaults).
- Enforced by `odinfmt.json`: `spaces: 2`, `tabs: false`, `newline_style: "CRLF"`.

## 2. Brace style

- **`_1TBS`** (one true brace style): opening brace on the same line as the declaration for control flow, **except** for function/proc bodies where it goes on the **next line**.
- Example:

  ```odin
  if condition {
      do_thing()
  }

  entity_create :: proc() -> Entity_Handle {
      // ...
  }
  ```

- Enforced by `odinfmt.json`: `brace_style: "_1TBS"`.

## 3. Naming conventions

| Kind                         | Convention             | Example                           |
| ---------------------------- | ---------------------- | --------------------------------- |
| Types (struct, enum, alias)  | `PascalCase`           | `Entity`, `Battle_State`          |
| Procs                        | `snake_case`           | `entity_create`, `battle_resolve` |
| Module-level constants       | `SCREAMING_SNAKE_CASE` | `MAX_PARTY_SIZE = 4`              |
| Enum variants                | `PascalCase`           | `Battle_State.Active`             |
| Package-private helpers      | `internal_` prefix     | `internal_format_value`           |
| Variables (local, parameter) | `snake_case`           | `move_dir`, `stored_generation`   |
| Struct fields                | `snake_case`           | `frame_count`, `player_handle`    |

## 4. Package layout

- One **package** per project (`package main`).
- One **concept** per file (`entity.odin`, `battle.odin`, `dialogue.odin`).
- Imports use the `import` block, sorted alphabetically:

  ```odin
  import "core:fmt"
  import "core:mem"
  import rl "vendor:raylib"
  ```

## 5. Block separators inside a file

- Use `/*=== X ===*/` to mark sections. This is purely visual; Odin ignores it.
- Recommended sections (in order):

  ```odin
  /*===
  STRUCT
  ===*/

  /*===
  CONSTANTS
  ===*/

  /*===
  VARS
  ===*/

  /*===
  PROCS
  ===*/
  ```

## 6. Blank lines

- **One blank line** between every top-level `proc`, `struct`, `enum`, `var`, `const`.
- **No blank line** between `package` declaration and the first declaration.
- **Two blank lines** allowed for major section breaks within a file (rare).
- **Enforced manually** (Odin has no built-in lint rule for this as of `dev-2026-06`).
- See §13 for the rationale on why this rule is convention, not tool-enforced.

## 7. Comments

- **Doc comments** above declarations use `//`:

  ```odin
  // Creates a new entity and returns a handle to it.
  entity_create :: proc() -> Entity_Handle {
  ```

- **Inline comments** use `//` (never `/* */`).
- **Section separators** use the `/*=== X ===*/` form (see §5).
- Comments should explain **why**, not **what** (the code already shows what).

## 8. Allocator policy

Three tiers (per the OdinRAG AGENTS.md):

| Tier | Allocator            | When                                   | Lifetime     |
| ---- | -------------------- | -------------------------------------- | ------------ |
| 0    | `tracking_allocator` | Debug builds ONLY                      | Program-wide |
| 1    | `arena` (per-frame)  | Transient per-frame data               | One frame    |
| 2    | `arena` (per-scene)  | Scene-stable data (entities, tilemaps) | One scene    |
| 3    | `heap` (default)     | Save/load + permanent state            | Program-wide |

See `odin-knowledge-base/courses/programvideogames/vertical-slice-and-dice-v10/rpg/088-26. Tracking Allocator.md`
for the canonical reference (when present in the KB).

## 9. Linting rules

- All `-vet-*` flags listed in `ols.json checker_args` are **mandatory**:
  - `-vet-unused`
  - `-vet-unused-variables`
  - `-vet-unused-imports`
  - `-vet-shadowing`
  - `-vet-style`
  - `-vet-semicolon`
  - `-vet-cast`
- The CI pipeline (`check_and_format.bat`) must pass before any commit.

## 10. Error handling

- Use Odin's built-in `Result` type idiom or multiple-return values for recoverable errors.
- Reserve `log.error` / `log.panic` for **unexpected** situations only.
- In `.bat` scripts: `goto :ERROR` on failure, never silent fallthrough.

## 11. What NOT to do

These are **banned patterns** with documented reasons:

| Anti-pattern                         | Why banned                                                |
| ------------------------------------ | --------------------------------------------------------- |
| `using` on entity fields             | Pollutes scope, breaks named access (Karl 23.1, lesson 5) |
| Package-level mutable state          | Anti-pattern (Karl 23.3, lessons 064 + 098)               |
| ECS inheritance chain                | Composition over inheritance (lessons 5 + 67)             |
| `transmute`                          | Use `cast` (also caught by `-vet-cast`)                   |
| `goto` outside error-handling blocks | Reserved for `goto :ERROR` pattern                        |
| `defer` inside loops                 | Defer-in-loops anti-pattern (Karl 23)                     |
| Tracking allocator in release builds | Costs 2-3x perf, reports false leaks (Karl 13.1.1)        |
| Hardcoded absolute Windows paths     | Breaks portability; use `${workspaceFolder}` or env vars  |

## 12. File headers

- Each file starts with a one-line summary and a separator:

  ```odin
  // Entity struct and related functions for managing entities in the game.
  //
  // ---------------
  package main
  ```

## 13. Rationale and enforcement level

For each rule, the enforcement level is documented above. Summary:

| Rule                          | Enforcement                         |
| ----------------------------- | ----------------------------------- |
| §1 Indentation / line endings | Tool (odinfmt)                      |
| §2 Brace style                | Tool (odinfmt)                      |
| §3 Naming                     | Convention + reviewer               |
| §4 Package layout             | Convention + reviewer               |
| §5 Block separators           | Convention only                     |
| §6 Blank lines                | Convention only                     |
| §7 Comments                   | Convention + reviewer               |
| §8 Allocator policy           | Convention + reviewer               |
| §9 Linting                    | Tool (ols + odin check)             |
| §10 Error handling            | Convention + reviewer               |
| §11 Banned patterns           | Mixed (some -vet-\*, rest reviewer) |
| §12 File headers              | Convention only                     |

If you want to add a **tool-enforced** rule (e.g. blank lines between procs), propose it upstream to `odin-lang/Odin` first.
The canonical list of Odin-supported flags is in `README - Odin Tooling.md` (§ Supported Odin flags).
