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
> Every other document (AGENTS.md, README.md, per-folder READMEs) should reference this file rather than duplicating the tree. Update this file FIRST, then propagate references.

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
├── odin-knowledge-base/     <- Bucket 1 - Odin KB (sanitized in public branch, full in local main)
├── code/                    <- Bucket 1b - Public code references + personal projects (sanitized in public)
├── _Helpers/                <- Bucket 2 - Public RAG management
└── _Private/                <- Bucket 3 - Private (tracked in local main, absent from public branch)
```

> **Important - what "private" means in this repo**: paywalled and personal content is **NOT gitignored**.
> It is **tracked in the local `main` branch** and pushed to the **private remote `OdinRag-private`**.
> It is excluded from the public `public` branch via the **two-branch strategy** (canonical reference: [`007_mixing_public_and_private_history.md`](007_mixing_public_and_private_history.md)).
> The actual tracked `.gitignore` only contains secrets + build/IDE ignores; local-only excludes live in `.git/info/exclude` (never version-controlled).

## Bucket 1 - `odin-knowledge-base/`

```text
odin-knowledge-base/
├── README - odin knowledge base.md
├── INDEX.md                 <- central index (auto + manual zones)
├── docs/                    <- scraped Markdown sources
│   ├── official/            <- odin-lang.org/docs/ + awesome-odin (MIT-style, public branch)
│   ├── karl_zylinski/       <- zylinski.se sample + book README index (public branch)
│   │   └── odin-book/       <- 33 MD chapters of Karl's paid ebook (ABSENT from public)
│   ├── newsletters/         <- odin-lang.org/news/ (Odin team, public branch)
│   ├── gingerbill/          <- gingerbill.org (5 sample articles in public, full corpus in main)
│   ├── jakubtomsu/          <- jakubtomsu.github.io (sample in public, full corpus in main)
│   └── showcase/            <- odin-lang.org/showcase/ (Odin team, public branch)
├── gitIngest/               <- gitingest snapshots of local Odin repo clones (public branch, regenerable)
└── courses/                 <- Skool programvideogames content (ABSENT from public)
```

## Bucket 1b - `code/`

```text
code/
├── README - code.md
├── INTEGRATION.md           <- convention for personal Odin projects under projects/
├── examples/                <- public Odin examples (demo.odin)
├── gists/                   <- 25 public Odin gists from awesome-odin
├── vendored templates/      <- third-party project templates (each its own git repo, content .gitignored, only README tracked)
│   ├── odin-raylib-hot-reload/
│   ├── odin-raylib-web/
│   ├── odin-sokol-hot-reload/
│   └── odin-sokol-web/
└── projects/                <- personal Odin projects (ABSENT from public)
    ├── README - projects.md
    └── PVG03_RPG/           <- the author's RPG remake
```

## Bucket 2 - `_Helpers/`

```text
_Helpers/
├── README - helpers.md
├── scripts/                 <- thematic sub-folders
│   ├── README - scripts.md
│   ├── diagnostic/          <- audit_public_safety.py, auditReadmeCoherence.py, publish_public.py, vaultConfigOdinRAG.py + vaultDiagnostic.py + validateFrontmatter.py (R2 TerraBloom port)
│   │   └── code_auditor/    <- code_auditor.py + odin_rules.{jsonc,schema.json} + rule_loader.py + scanner.py + kb_index.py + context_builder.py + reporter.py + README - code_auditor.md (self-contained package, Phase 1+2+3)
│   ├── fixes/               <- format_odin_in_files, fix_mojibake, reflow_md, odin_format, book_html_to_md, lint_pylance
│   ├── indexing/            <- build_kb_index.py
│   ├── scrapers/            <- scrape_*.py + download_*.py
│   └── lib/                 <- text_clean, http_client, html2md, user_config (shared libs; per-package modules stay inside their own folder)
├── docs/                    <- meta docs about this repo (NNN_*.md)
│   ├── README - docs.md
│   ├── 001_folder_structure.md
│   ├── 002_how_minimax_m3_is_used_in_this_repository.md
│   ├── 003_yaml_frontmatter_conventions.md
│   ├── 004_markdown_style.md
│   ├── 005_public_release_checklist.md
│   ├── 007_mixing_public_and_private_history.md
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
├── .config/                 <- user_config.jsonc, cookies.txt, skool_credentials.txt (DOUBLY: .gitignore + main-only)
├── archives/                <- archived/superseded docs (ABSENT from public)
│   ├── README - archives.md
│   └── ...
├── docs/                    <- private meta docs (ABSENT from public)
│   ├── README - docs.md
│   └── ...
├── planning/                <- day-by-day planning (ABSENT from public)
│   ├── README - planning.md
│   ├── ...
│   └── daily/               <- one file per working day, J_YYYY-MM-DD.md (no NNN_ prefix)
└── raw/                     <- raw research notes, kept as-is (no NNN_ prefix, no frontmatter)
```

> `_Private/` content is **NOT gitignored** — it is tracked in the local `main` branch and pushed to the private remote `OdinRag-private`, then excluded from the public `public` branch via `refresh_public_branch.py` (two-branch strategy). Local `git status` keeps personal paths quiet via `.git/info/exclude` (LOCAL only, never version-controlled). Only `/_Private/.config/` is doubly protected (also in the tracked `.gitignore`) because credentials must never reach history.
>
> The `archives/` subfolder keeps the evolution of decisions traceable when a doc is rewritten or translated.
> See [`_Private/archives/README - archives.md`](../../_Private/archives/README%20-%20archives.md) for the convention (when to archive, naming, frontmatter annotations).
>
> For PUBLIC archives (old versions of public-facing docs that should stay visible to collaborators), use a `_Helpers/archives/` folder instead - to be created on first need.

## Where this file is referenced

- [`AGENTS.md`](../../AGENTS.md) - global agent context (top-level reference)
- [`README.md`](../../README.md) - top-level repo intro (top-level reference)
- All `README - <topic>.md` files in authored folders (one per folder)
- This is the only place where the full tree lives; everything else links here.

## Update procedure

When the tree changes:

1. Edit this file FIRST.
2. Update the per-folder `README - <topic>.md` to point here for the global view.
3. Update any path reference that explicitly depends on the changed folder (use a search like `Get-ChildItem -Recurse -Include *.md | Select-String -Pattern "<old_path>"`).
4. Run the validation suite (see AGENTS.md "Push to the public repo - checklist" plus `markdownlint-cli2` and `auditReadmeCoherence.py`).
