# .zed - OdinRAG project-level Zed configuration

> This folder mirrors the role of `.vscode/` for VSCode: a tracked, project-scoped configuration overlay applied ON TOP of the user-level `~/AppData/Roaming/Zed/settings.json`. It contains the minimal configuration needed to make Zed a first-class citizen for OdinRAG development, without duplicating personal / cosmetic preferences that belong at the user level.

## Files

| File            | Role                                                                    | Equivalent in `.vscode/`   |
| --------------- | ----------------------------------------------------------------------- | -------------------------- |
| `settings.json` | Odin language server, formatter, project-level exclusions               | `.vscode/settings.json`    |
| `keymap.json`   | Editor / workspace keybindings layered on top of the VSCode base keymap | `.vscode/keybindings.json` |
| `tasks.json`    | Critical Odin build / run / check / format tasks                        | `.vscode/tasks.json`       |

## Design rules

1. **Lean file** - keep only project-specific settings here. Cosmetic stuff (font family, theme, terminal font, base keymap) lives at user level.
2. **Mirror the `.vscode/*` intent, not its shape** - the doc `_Private/raw/2026-07-09_migration_vscode_vers_zed_odin.md` is explicit: the migration is a _selective mapping_, not a port.
3. **Versioned** - `.zed/*` is tracked in git (the `.gitignore` keeps only transient exclusions, mirroring the `.vscode/*` pattern).
4. **Idempotent** - opening OdinRAG in Zed should produce a stable, expected state.

## Conventions inherited from VSCode (do NOT break)

- **Indent**: 2 spaces for Odin source and `odin` blocks inside Markdown (enforced by `odinfmt.json` at the repo root and by `format_on_save: "on"` in `languages.Odin` here).
- **Final newline**: NOT inserted on save (matches the VSCode setting `files.insertFinalNewline: false`).
- **Trailing whitespace**: trimmed on save (matches `files.trimTrailingWhitespace: true`).
- **Search excludes**: `build/`, `node_modules/`, `vendor/`, `_Private/raw/`, `_Private/planning/daily/`, `code/vendored templates/*/`, `_Private/.config/`.

## Critical tasks

| Shortcut (from `keymap.json`) | Task label                        |
| ----------------------------- | --------------------------------- |
| `Ctrl+Shift+B`                | Odin: Build Debug                 |
| `F5`                          | Odin: Run Debug                   |
| (via command palette)         | Odin: Build Release               |
| (via command palette)         | Odin: Hot Reload - Build DLL      |
| (via command palette)         | Odin: Check (vet only)            |
| (via command palette)         | Odin: Format Odin blocks (manual) |

The other VSCode tasks (`[DIAG]`, `[PUBLISH]`, `[SCRAPE]`) remain accessible through the integrated terminal - they are one-shot CLI invocations and do not justify a keybinding yet.

## Where to read more

- `_Private/raw/2026-07-09_migration_vscode_vers_zed_odin.md` - source migration note (rationale + mapping tables).
- `_Helpers/docs/008_zed_setup.md` - condensed KB version of the same content.
- `~/.config/zed` is NOT used on Windows; the user-level config lives in `~/AppData/Roaming/Zed/`.
