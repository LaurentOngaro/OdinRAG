---
title: "Folder structure reference"
date: "2026-07-01"
tags: [OdinRAG, reference, structure]
type: reference
status: active
version: 1.0.0
lastUpdated: "2026-07-01"
updatedBy: "MiniMax-M3 (Kilo Code)"
---

# 001_folder_structure

> **Single source of truth for the OdinRAG folder tree.**
> Every other document (AGENTS.md, README.md, per-folder READMEs) should reference this file
> rather than duplicating the tree. Update this file FIRST, then propagate references.

## Top-level tree

```text
OdinRAG/
├── README.md
├── SOURCES.md
├── LICENSE
├── AGENTS.md
├── TODO.md
├── kilo.json                <- Kilo runtime config (single source)
├── odinfmt.json
├── .markdownlint.json
├── .markdownlintignore
├── .editorconfig
├── .gitignore
│
├── odin-knowledge-base/     <- Bucket 1 - Odin KB (public, partly gitignored)
├── code/                    <- Bucket 1b - Public code references
├── _Helpers/                <- Bucket 2 - Public RAG management
└── _Private/                <- Bucket 3 - Private (gitignored, never pushed)
```

## Bucket 1 - `odin-knowledge-base/`

```text
odin-knowledge-base/
├── README - odin knowledge base.md
├── INDEX.md                 <- central index (auto + manual zones)
├── docs/                    <- scraped Markdown sources
│   ├── official/            <- odin-lang.org/docs/ + awesome-odin (MIT-style)
│   ├── karl_zylinski/       <- zylinski.se + book README (full book gitignored)
│   ├── newsletters/         <- odin-lang.org/news/ (Odin team)
│   ├── gingerbill/          <- gingerbill.org (5 sample articles)
│   ├── jakubtomsu/          <- jakubtomsu.github.io (4 sample articles)
│   └── showcase/            <- odin-lang.org/showcase/ (Odin team)
└── courses/                 <- Skool programvideogames content (gitignored, paid)
```

## Bucket 1b - `code/`

```text
code/
├── README - code.md
├── INTEGRATION.md           <- convention for personal Odin projects under projects/
├── examples/                <- public Odin examples (demo.odin)
├── gists/                   <- 25 public Odin gists from awesome-odin
├── vendored templates/      <- third-party project templates (each its own git repo, gitignored)
│   ├── odin-raylib-hot-reload/
│   ├── odin-raylib-web/
│   ├── odin-sokol-hot-reload/
│   └── odin-sokol-web/
└── projects/                <- personal Odin projects (each gitignored)
    ├── README - projects.md
    └── PVG03_RPG/           <- the author's RPG remake
```

## Bucket 2 - `_Helpers/`

```text
_Helpers/
├── README - helpers.md
├── scripts/                 <- thematic sub-folders
│   ├── README - scripts.md
│   ├── diagnostic/          <- audit_public_safety.py, auditReadmeCoherence.py
│   ├── fixes/               <- format_odin_in_files, fix_mojibake, reflow_md, odin_format,
│   │                            book_html_to_md, lint_pylance
│   ├── indexing/            <- build_kb_index.py
│   ├── scrappers/           <- scrape_*.py + download_*.py
│   └── lib/                 <- text_clean, http_client, html2md, user_config
├── docs/                    <- meta docs about this repo (NNN_*.md)
│   ├── README - docs.md
│   ├── 002_how_minimax-m3_is_used_in_this_repository.md
│   ├── 003_yaml_frontmatter_conventions.md
│   ├── 004_markdown_style.md
│   ├── 005_public_release_checklist.md
│   ├── 007_mixing_public_and_private_history.md
│   ├── 001_folder_structure.md
│   └── social/              <- social posts (REDDIT_POST.md, TWITTER_THREAD.md, DISCORD_NOTE.md)
├── templates/               <- INTERNAL OdinRAG templates (clone these, never edit in place)
│   ├── README - templates.md
│   ├── odin-project/        <- project scaffold (AGENTS, README, src/main.odin, devlog, subagent)
│   ├── planning-daily/      <- daily entry template (001_J_YYYY-MM-DD.md)
│   └── user_config.example.jsonc
├── prompts/                 <- reusable Kilo prompts (lowercase, no NNN_ prefix)
│   ├── README - prompts.md
│   └── refresh_topic_index.md
└── logs/                    <- cumulative script logs (gitignored)
```

## Bucket 3 - `_Private/`

```text
_Private/
├── README - private.md
├── .config/                 <- user_config.jsonc, cookies.txt, skool_credentials.txt (gitignored)
├── docs/                    <- private meta docs (gitignored, currently just README - docs.md)
│   └── README - docs.md
├── planning/                <- day-by-day planning (gitignored)
│   ├── README - planning.md
│   ├── 001_odin_learning_plan_advanced_game_dev_2026.md
│   ├── 002_roadmap.md
│   └── daily/               <- one file per working day, J_YYYY-MM-DD.md (no NNN_ prefix)
└── raw/                     <- raw research notes, kept as-is (no NNN_ prefix, no frontmatter)
```

## Where this file is referenced

- [`AGENTS.md`](../../AGENTS.md) - global agent context (top-level reference)
- [`README.md`](../../README.md) - top-level repo intro (top-level reference)
- All `README - <topic>.md` files in authored folders (one per folder)
- This is the only place where the full tree lives; everything else links here.

## Update procedure

When the tree changes:

1. Edit this file FIRST.
2. Update the per-folder `README - <topic>.md` to point here for the global view.
3. Update any path reference that explicitly depends on the changed folder
   (use a search like `Get-ChildItem -Recurse -Include *.md | Select-String -Pattern "<old_path>"`).
4. Run the validation suite (see AGENTS.md "Push to the public repo - checklist" plus
   `markdownlint-cli2` and `auditReadmeCoherence.py`).
