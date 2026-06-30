# Odin projects (game dev)

This folder is for **your own Odin projects** that share the workspace with the knowledge base (KB).

> **Guiding idea**: Kilo sees the **entire repo** as workspace, so when you code a project here, it has simultaneous access to your code, to Karl's docs, to the Skool lessons, and to your devlogs. That is what makes the AI assistance relevant.

## Recommended workflow

1. **Identify** 1-3 relevant Skool lessons or Karl chapters via `odin-knowledge-base/INDEX.md` or the `kb-navigator` skill
2. **Copy** the `_TEMPLATE_/` folder into a subfolder named after your project
3. **Customise** the `README.md` and `AGENTS.md` (point to the relevant lessons)
4. **Code** in `src/`, drawing inspiration from the patterns (never copy-paste from the KB)
5. **Devlog** every session in `<your-project>/devlog/J_YYYY-MM-DD_<topic>.md`

## Naming convention

- Subfolders in **kebab-case**: `my-2d-rpg/`, `raylib-particle-demo/`
- One subfolder = one project (or one throwaway prototype)
- For an unnamed "sandbox", use `_sandbox/` (the `_` prefix is a natural gitignore hint for some setups)

## Limitations to respect

- NEVER run `odin run .` from this folder - create a separate project elsewhere for code that compiles (the AGENTS.md anti-patterns section)
- Each subfolder must have at minimum a `README.md` (1 sentence) and an `AGENTS.md` (5-10 lines on the patterns used)
- `.kilo/agents/<project>.md` files are **optional** but useful: a subagent that knows the project-specific patterns
- Devlogs are NOT Odin code (they are prose: decisions, blockers, discoveries)

## Project index

| Project                        | Status | Main KB inspirations |
| ------------------------------ | ------ | --------------------- |
| `_TEMPLATE_/`                  | Model  | n/a                   |
| _no project yet_               |        |                       |

To add a project: copy `_TEMPLATE_/`, rename, edit README + AGENTS.
