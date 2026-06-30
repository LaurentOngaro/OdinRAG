---
name: odin-format
description: Re-format a .odin file or ```odin``` blocks inside a Markdown file via odinfmt (with the 2-space config). Use after creating or modifying Odin code.
---

# Re-format Odin code

Skill for calling `odinfmt` (the official Odin formatter) on a `.odin` file or on the ```odin ...``` blocks of a Markdown file.

## When to invoke

- After writing or modifying Odin code in a `.odin` file or in a `.md` file.
- When the user complains about inconsistent indentation (tabs instead of spaces, lines too long, etc.).
- Before committing a change that touches Odin code.

## How

### Single file

````bash
# Dry-run (check what would be modified)
python _Helpers/format_odin_in_files.py --file path/to/foo.odin --check

# Apply
python _Helpers/format_odin_in_files.py --file path/to/foo.odin

# For a .md (only formats the ```odin blocks, not the rest)
python _Helpers/format_odin_in_files.py --file path/to/foo.md
````

### Entire folder

```bash
# Whole KB (recursively re-format all .md and .odin)
python _Helpers/format_odin_in_files.py --path odin-knowledge-base --check
python _Helpers/format_odin_in_files.py --path odin-knowledge-base
```

### Automatic hook

The scrapers (`scrape_skool.py`, `scrape-official.py`, `scrape-zylinski.py`) already call `format_path_if_odin()` after every write. No need to re-run manually after a scrape.

## Active configuration

Formatting uses `odinfmt.json` (at the repo root).

To change the style, edit `odinfmt.json` (NOT the system-wide config bundled with OLS).

## Prerequisites

- `odinfmt.exe` must exist somewhere on disk. Set its absolute path in the `ODINFMT_EXE` constant in `_Helpers/odin_format.py` (or expose it via an environment variable).

## Error diagnostics

If `odinfmt` returns exit=1, it is likely a **syntax error** in the Odin source. Read the error message (first line), fix the code, retry.

```text
$ python _Helpers/format_odin_in_files.py --file foo.odin
[ERR] odinfmt exit=1 : foo.odin(12:5) Expected ';', got '}'
```

-> fix line 12 of `foo.odin` and re-run.

## Anti-patterns

- Never edit the system-wide `odinfmt.json` shipped with OLS to revert to tabs. The repo standard is 2 spaces, configurable via `odinfmt.json` at the root (see AGENTS.md).
- Never trust manual indentation inside an Odin block: always run odinfmt after a modification.
