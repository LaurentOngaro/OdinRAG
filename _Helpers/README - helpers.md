---
title: "README - helpers"
date: "2026-07-01"
tags: [OdinRAG, reference]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# README - helpers

## Contents

Public RAG-management bucket. Two subtrees:

- `scripts/` - durable Python scripts (scrapers, fixers, audits, KB indexing)
- `docs/` - meta documentation about this repo (conventions, guides)
- `templates/` - internal OdinRAG templates (project scaffold, daily template, user config example)
- `prompts/` - reusable Kilo prompts
- `logs/` - cumulative script logs (gitignored)

## Conventions

- Scripts in `scripts/` are grouped by purpose (`diagnostic/`, `fixes/`, `indexing/`, `scrappers/`, `lib/`).
- `scripts/lib/` is the shared library imported by other scripts as `_Helpers.scripts.lib.*`.
- Documentation in `docs/` follows the `NNN_snake_case.md` filename convention.

## Cross-references

Full folder tree: [`001_folder_structure.md`](docs/001_folder_structure.md)
