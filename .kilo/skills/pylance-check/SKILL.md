---
name: pylance-check
description: Run pyright (Pylance engine) on Python files and fix every reported diagnostic. Use after any .py edit, before considering the task done. Enforced by AGENTS.md § Python (scrapers).
---

# Pylance check

This repo enforces **zero Pylance warnings** on every `.py` file (see `AGENTS.md` § Python).
The lint is reproducible via the open-source `pyright` engine wrapped by a durable script:

```bash
python _Helpers/scripts/fixes/lint_pylance.py <path>
```

- `<path>` = a single file, a folder, or omit it to lint the whole repo.
- Exit code `0` = clean, `1` = blocking diagnostics, `2` = tool error.
- `--check` makes it a dry-run (always exit 0).
- `--strict` makes warnings blocking too.

## When to invoke

After **any** edit to a `.py` file, before considering the task done.
Also useful as a sanity check before opening a PR / pushing to the public repo.

## Typical workflow

```bash
# 1. Edit your .py file
# 2. Run the linter on the same file
python _Helpers/scripts/fixes/lint_pylance.py _Helpers/<your_script>.py

# 3. Fix every reported diagnostic, loop until clean.

# 4. (optional) Lint the whole repo as a smoke test
python _Helpers/scripts/fixes/lint_pylance.py
```

## Common diagnostic patterns in this repo

| Pattern                                                                  | Root cause                                            | Fix                                                                      |
| ------------------------------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------------------ |
| `"splitlines" is not a known attribute of "None"`                        | `__doc__: Optional[str]` is `None` under `python -OO` | Use a module-level `_DESCRIPTION` constant, never `__doc__.splitlines()` |
| `"existing" is possibly unbound`                                         | Variable assigned only inside a branch                | Initialise before the branch: `existing = ""`                            |
| `"append" is not a known attribute of "str"`                             | `tag.get("class") or []` keeps a `str` branch         | Coerce: `if isinstance(classes, str): classes = classes.split()`         |
| `Cannot access attribute "startswith" for class "AttributeValueList"`    | BS4 `Tag.attrs` keys are over-typed in stubs          | `# type: ignore[attr-defined]` or filter with `isinstance`               |
| `Argument of type "list[Any]" cannot be assigned to parameter "default"` | BS4 `Tag.get(key, default)` rejects `list` as default | Drop the default and use `get(key) or []`                                |

## Installation

If `pyright` is missing:

```bash
pip install pyright
```

The script falls back to `python -m pyright` if the `pyright` binary is not on PATH.

## Why this skill exists

Without it, AI agents (and humans) forget to lint after edits, and Pylance warnings pile up. The skill + the AGENTS.md rule together make the check automatic.
