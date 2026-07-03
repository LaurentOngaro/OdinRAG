# README - fixes

## Contents

- `format_odin_in_files.py` - run `odinfmt` on `.odin` files and ` ```odin ` blocks inside `.md`
- `fix_mojibake.py` - repair UTF-8 / Latin-1 mojibake in Markdown
- `reflow_md.py` - reflow Markdown prose into "one paragraph per line" book style
- `odin_format.py` - reusable `odinfmt` wrapper (importable)
- `book_html_to_md.py` - convert Karl's HTML book to one `.md` per chapter
- `lint_pylance.py` - run pyright on Python files and report Pylance diagnostics

## Conventions

Each script is idempotent and accepts `--check` for dry-run.

## Cross-references

Full folder tree: [`001_folder_structure.md`](../../../docs/001_folder_structure.md)
