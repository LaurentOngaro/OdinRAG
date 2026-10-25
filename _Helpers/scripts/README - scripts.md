# README - scripts

## Contents

Thematic sub-folders:

- `dev/` - editor integration scripts (`odin_task.ps1`) and workspace link management (`sync_links.py`)
- `diagnostic/` - pre-flight audits (`audit_public_safety.py`, `auditReadmeCoherence.py`)
- `fixes/` - one-shot maintenance (`format_odin_in_files.py`, `fix_mojibake.py`, `reflow_md.py`, `odin_format.py`, `book_html_to_md.py`, `lint_pylance.py`)
- `indexing/` - KB index regeneration (`build_kb_index.py`)
- `scrapers/` - HTTP/Markdown scrapers for the KB sources
- `lib/` - shared library (`html2md`, `http_client`, `text_clean`, `user_config`)

## Conventions

- All scripts are CLI + idempotent. Many accept `--check` for dry-run.
- Scripts that depend on user paths or credentials read from `_Private/.config/user_config.jsonc`.
- `dev/sync_links.py` creates the workspace links declared in `_Helpers/links.jsonc` (NTFS junction on Windows, symbolic link on Linux). See [009_cross_platform_links.md](../docs/009_cross_platform_links.md).

## Cross-references

Full folder tree: [`001_folder_structure.md`](../docs/001_folder_structure.md)
