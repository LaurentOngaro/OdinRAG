# README - projects

## Contents

Personal Odin projects. Each subfolder is **tracked in the local `main` branch** and pushed to the private remote `OdinRag-private`.
**Absent from the public `public` branch** (two-branch strategy).
They are NOT gitignored - see [`_Helpers/docs/007_mixing_public_and_private_history.md`](../../_Helpers/docs/007_mixing_public_and_private_history.md).

- `PVG03_RPG/` - the author's remake of the ProgramVideoGame RPG module (see [`PVG03_RPG/AGENTS.md`](PVG03_RPG/AGENTS.md))

## Conventions

- See [`../INTEGRATION.md`](../INTEGRATION.md) for the full convention.
- New projects are scaffolded from [`_Helpers/templates/odin-project/`](../../_Helpers/templates/odin-project/).
- A project that lives OUTSIDE this repository is exposed here as a **link** (NTFS junction on Windows, symbolic link on Linux). The links are declared in [`_Helpers/links.jsonc`](../../_Helpers/links.jsonc) and created by `_Helpers/scripts/dev/sync_links.py` - never by hand. See [`_Helpers/docs/009_cross_platform_links.md`](../../_Helpers/docs/009_cross_platform_links.md).

## Cross-references

Full folder tree: [`001_folder_structure.md`](../../_Helpers/docs/001_folder_structure.md)
