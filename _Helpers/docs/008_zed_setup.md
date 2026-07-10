---
title: "Zed setup for OdinRAG"
date: 2026-07-10
tags: [OdinRAG, doc, reference, zed, editor]
type: reference
status: active
version: 1.1.0
lastUpdated: 2026-07-10
updatedBy: MiniMax-M3 (Kilo Code)
---

# 008_zed_setup

> **Audience**: contributors who want to use Zed instead of (or alongside) VSCode for OdinRAG work. Pair with `_Private/raw/2026-07-09_migration_vscode_vers_zed_odin.md` for the full migration rationale.

## TL;DR

Zed is treated as a **focused Odin profile**, not a full VSCode replacement. The shared config lives in `.zed/` at the repo root and is versioned; personal / cosmetic preferences stay at user level (`~/AppData/Roaming/Zed/settings.json` on Windows).

## File layout

```
OdinRAG/
└── .zed/
    ├── README - zed.md   <- orientation (mirror of this file, terser)
    ├── settings.json     <- Odin LSP + project-level search excludes
    ├── keymap.json       <- shortcuts layered on VSCode base keymap
    └── tasks.json        <- Odin build / run / check / format tasks
```

## What's already in place (user level)

The migration is split between two layers:

| Concern                                                                | Layer | Where it lives                        |
| ---------------------------------------------------------------------- | ----- | ------------------------------------- |
| `base_keymap: "VSCode"`                                                | user  | `~/AppData/Roaming/Zed/settings.json` |
| `buffer_font_family: "JetBrainsMonoNL Nerd Font"`                      | user  | same                                  |
| `buffer_font_size: 14`, `ui_font_size: 16`                             | user  | same                                  |
| `tab_size: 2`                                                          | user  | same                                  |
| `autosave: after_delay` (1000 ms)                                      | user  | same                                  |
| `soft_wrap: "none"`                                                    | user  | same                                  |
| `minimap.show: "never"`                                                | user  | same                                  |
| `remove_trailing_whitespace_on_save: true`                             | user  | same                                  |
| `ensure_final_newline_on_save: false`                                  | user  | same                                  |
| `terminal.font_size: 14`, `terminal.font_family: "FiraCode Nerd Font"` | user  | same                                  |
| `show_whitespaces: "trailing"`                                         | user  | same                                  |
| `theme: { dark: "Ayu Dark", light: "Ayu Light", mode: "system" }`      | user  | same                                  |
| `icon_theme: "Material Icon Theme"`                                    | user  | same                                  |
| MCP servers (Playwright + GitHub)                                      | user  | same                                  |
| Agent LLM (AiFlowBridge / MiniMax M3)                                  | user  | same                                  |

## What's project-level (this repo)

The shared `.zed/` folder handles things that **must be the same for every collaborator** opening the repo in Zed:

1. **Odin LSP wiring** (`.zed/settings.json > languages.Odin`) - format on save, 2-space tabs, OLS on PATH.
2. **Search / file-scan exclusions** (`.zed/settings.json > file_scan_exclusions`) - mirrors the `search.exclude` block from `.vscode/settings.json`.
3. **Editor / workspace keybindings** (`.zed/keymap.json`) - the 8 shortcuts from the migration note, plus `Ctrl+Shift+B` and `F5` for the two most-used Odin tasks.
4. **Critical Odin tasks** (`.zed/tasks.json`) - Build Debug / Release / DLL / Run / Check / Format. The other VSCode tasks (diagnostics, publish, scrapers) stay terminal-only for now.

## Why split between user and project

- **User-level** holds **personal** decisions: font family, theme, MCP tokens, agent LLM. Sharing these would leak secrets and override each collaborator's preferences.
- **Project-level** holds **collective** decisions: LSP config, file excludes, keymap, tasks. Sharing these makes "open OdinRAG in Zed" deterministic.

This split mirrors the existing `.vscode/` pattern in the repo:

```
.vscode/
├── settings.json    <- tracked (project-level overrides)
├── tasks.json       <- tracked (project-level tasks)
└── extensions.json  <- tracked (recommendations)
```

## Keybindings at a glance

| Shortcut       | Action                         | Source                       |
| -------------- | ------------------------------ | ---------------------------- |
| `Ctrl+Shift+P` | Command palette                | migration doc                |
| `Ctrl+P`       | Quick open file                | migration doc                |
| `F12`          | Go to definition               | migration doc                |
| `Shift+F12`    | Find all references            | migration doc                |
| `Ctrl+Shift+F` | Project search                 | migration doc                |
| `Alt+Shift+F`  | Format buffer                  | migration doc                |
| `F2`           | Rename symbol                  | migration doc                |
| `Ctrl+.`       | Code actions                   | migration doc                |
| `Ctrl+Shift+B` | Spawn "Odin: Build Debug" task | this file                    |
| `F5`           | Spawn "Odin: Run Debug" task   | this file                    |
| `Ctrl+\``      | Toggle terminal                | safety net (already default) |

## Differences vs VSCode (and why)

- **No `.vscode/launch.json` equivalent** - Zed does not have a unified debug adapter story. For Odin builds the workflow stays "build then run", not "set breakpoints". Debug, when needed, falls back to VSCode.
- **No problem matchers in tasks** - Zed tasks do not yet support `problemMatcher`. Build errors surface as terminal text; the diagnostics panel picks them up via OLS.
- **No `breadcrumbs.enabled`** - Zed has no breadcrumb bar.
- **No `editor.minimap.enabled`** - Zed has a minimap, controlled by `minimap.show: "never"` (already in user config).
- **No `workbench.*`** - the workbench is fundamentally different.

## Adding more

After 2-3 real working sessions, revisit:

- Bindings that were missed (typical gap: terminal split panes).
- Tasks that turned out to be muscle-memory critical (e.g. publish, validate-frontmatter).
- LSP-specific tweaks once OLS inlay hints stabilise upstream.

Apply additions to `.zed/keymap.json` and `.zed/tasks.json` only. Re-validate that the JSON parses (`jq . .zed/keymap.json` / `.zed/tasks.json`).

## Still TODO (after install)

Concrete improvements identified during the migration. None are blocking; all are deferred to Phase 3 (Rationalisation) of the migration doc or to a future session. Order inside each list = suggested priority, top to bottom.

### Zed config follow-ups

1. **Fix `reflow_md.py` coverage gap** - the script does not join blockquote continuations nor indented list item descriptions; `--check` exits 0 on files that violate rule 1 of `_Helpers/docs/004_markdown_style.md`. Fix: treat a `>` line after another `>` as continuation, and allow indented joins even when the previous line is a block start.
2. **Template the OLS binary path** - `.zed/settings.json` currently uses `"path": "ols"` which depends on PATH. Add `paths.ols_exe` to `_Helpers/templates/user_config.example.jsonc` and document the manual copy-paste (Zed cannot substitute env vars at settings load time).
3. **Add a "Run all diagnostics" task** - wrap the three `[DIAG]` Python scripts (`auditReadmeCoherence`, `vaultDiagnostic`, `validateFrontmatter`) in `_Helpers/scripts/diagnostic/run_all_diags.ps1` and expose it as a single Zed task.
4. **Test `use_on_type_format: true` on `.odin`** - if OLS reformats on every keystroke instead of just indentation, set `languages.Odin.use_on_type_format` to `false` in `.zed/settings.json`.
5. **Activate inline diff in the Git panel** - user-level only; verify the gesture and decide if a keymap entry is worth adding.
6. **Document a focus mode shortcut** - Zed has a Zen / Focus mode useful for writing dailies and ADRs; add a personal keymap entry and mention it in `.zed/README - zed.md`.

### Project-wide follow-ups

1. **Move `_Private/raw/2026-07-09_migration_vscode_vers_zed_odin.md`** to `_Private/raw/Perplexity backlog/` per the convention in `AGENTS.md` § Perplexity workflow. Commit with `git add -f` (lives in `_Private/`, so it goes to the private remote only).
2. **Track `.vscode/settings.json` and `.vscode/extensions.json`** - mirror the `.zed/*` allowlist pattern in `.gitignore` (`!.vscode/settings.json`, `!.vscode/extensions.json`). Both files are useful to collaborators and are currently untracked by accident.
3. **Write a daily `J_2026-07-10.md`** in `_Private/planning/daily/` summarising the migration decision, files created, and the `reflow_md.py` gap. Use the `.kilo/skills/planning-helper` skill.
4. **Create an ADR** (`2026-07-10_ADR-XXX_zed_focused_odin_profile.md` in `_Private/docs/decisions/`) documenting the architectural decision: Zed as focused Odin profile, not full VSCode replacement. Captures context, alternatives rejected, and consequences.
5. **Strengthen `auditReadmeCoherence`** - the latest run reported only 1 reference resolved across 34 READMEs; verify whether the audit searches for `[[wikilinks]]` only or also relative Markdown links, then update the doc in `001_folder_structure.md`.
6. **Investigate the unstaged diffs** in `.markdownlint.json` (removed comment, added trailing newline) and `_Helpers/scripts/diagnostic/code_auditor/rule_loader.py` (~230-line reformat). Both appeared during the migration session; not committed by this commit, but should be reviewed and committed separately if benign.
7. **Move the GitHub MCP token out of `~/AppData/Roaming/Zed/settings.json`** - currently in plain text (`ghp_...`). Switch to env var or external file. Personal / cosmetic, do not version.

### Suggested order for this week

1. Fix `reflow_md.py` (~30 lines).
2. Daily `J_2026-07-10.md` via `planning-helper` (~5 min).
3. ADR for the Zed decision (~15 min).
4. Move the migration note + add `paths.ols_exe` to the user-config template (~10 min).

Everything else is post-stabilisation (Phase 3 of the migration doc).

## Cross-references

- `_Private/raw/2026-07-09_migration_vscode_vers_zed_odin.md` - the full migration source note (mapping tables, rationale, decision points).
- `001_folder_structure.md` - where `.zed/` lives in the tree.
- `.kilo/skills/odin-format` - the Odin formatter workflow (odinfmt).
- `_Helpers/scripts/dev/odin_task.ps1` - the PowerShell wrapper invoked by every task in `.zed/tasks.json`.
