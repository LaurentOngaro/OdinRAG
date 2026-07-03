# README - diagnostic

## Purpose

Diagnostic and audit scripts. These are the manual pre-push checks that mirror what the GitHub Action runs automatically (see `.github/workflows/`). Three orthogonal axes:

- **Public/private safety** - the `.gitignore` + filter-branch pipeline is honoured.
- **Documentation coherence** - READMEs, wikilinks, frontmatter, filenames, content structure.
- **Code auditor** - the per-Odin-file static analysis (`code_auditor/`) sits in its own package.

## Scripts

- `audit_public_safety.py` - verify forbidden paths are absent from the working tree AND/OR the local `public` branch. Called by the pre-push hook and by CI. Exit codes: 0 = clean, 1 = violations, 2 = error.
- `auditReadmeCoherence.py` - verify per-folder READMEs reflect their host directory (wikilinks resolve, no missing files). Exit codes: 0 = clean, 1 = issues found.
- `vaultDiagnostic.py` - walk the whole repo and report issues per file: filename structure, frontmatter (delegated to `validateFrontmatter.py`), content (H1 must match filename when prefixed with `NNN_`, no long dashes). Exit codes: 0 = clean, 1 = issues found, 2 = frontmatter error with `--fail-on-error`.
- `validateFrontmatter.py` - validate every `.md` file's YAML frontmatter against the 8-field OdinRAG schema (see `_Helpers/docs/003_yaml_frontmatter_conventions.md`). Auto-fixes long dashes (en-dash/em-dash/horizontal bar to ASCII `-`). Exit codes: 0 = clean, 1 = errors (default), 2 = errors with `--fail-on-error`.

The 2 new scripts (`vaultDiagnostic.py`, `validateFrontmatter.py`) are R2 of the TerraBloom adoption (see `_Private/raw/2026-07-01_recommandations_terrabloom_vers_odinrag.md`). R1 was `auditReadmeCoherence.py` (delivered 2026-07-01).

## `audit_public_safety.py`

The script enforces the public/private split. After the 2026-07-02 refactor, it has TWO scopes:

- `--scope tree` (default `tree` only): the working tree's committed state. Will fail on `main` because the workflow intentionally tracks personal content on main. Useful for diagnosing ignore-config hygiene, NOT for the publish flow.
- `--scope branch` (default): the local `refs/heads/public` branch's tree. This is the tree that will be pushed to GitHub. Should always be clean before push.
- `--scope both`: paranoid double check (combines the two above).

Example before publishing:

```bash
python _Helpers/scripts/diagnostic/audit_public_safety.py           # default = branch scope
python _Helpers/scripts/diagnostic/audit_public_safety.py --verbose # list every file examined
python _Helpers/scripts/diagnostic/audit_public_safety.py --scope both --verbose
```

## `auditReadmeCoherence.py`

`auditReadmeCoherence.py [--scope <path>] [--quiet] [--fail-on-error]`

Walks the repo, reads each `README*.md`, and validates that:

- The referenced folder structure is real (no `[[wikilinks]]` to non-existent files)
- Wikilinks resolve to existing files (no 404s in rendered KB)
- Aspirational READMEs (describing future content) are explicitly marked as such

## `vaultDiagnostic.py` (R2)

`vaultDiagnostic.py [--source <path>] [--quiet] [--fail-on-error]`

Walks the repo (or a custom source folder) and classifies issues in 4 categories: `filename`, `frontmatter`, `content`, `system`. Frontmatter validation is delegated to `validateFrontmatter.check_file` so the two scripts share a single source of truth.

Filename rule: only enforced when the filename starts with `NNN_` (per AGENTS.md: top-level files like `AGENTS.md`, `README.md`, `SOURCES.md` are exempt).

Content rule: H1 must match the filename exactly when the filename starts with `NNN_`. Long dashes are reported (no auto-fix here; run `validateFrontmatter.py` to auto-fix).

## `validateFrontmatter.py` (R2)

`validateFrontmatter.py [--files <path>...] [--fail-on-error] [--no-content-check] [--quiet]`

Validates the YAML frontmatter against the 8-field OdinRAG schema:

- Required: `title`, `date`, `tags`, `type`, `status`, `version`, `lastUpdated`, `updatedBy`.
- Optional: `docId` (UPPER_SNAKE_CASE), `priority` (1/2/3).
- Enums: `type` in 9 values, `status` in 5 values, `tags` must include `OdinRAG` and have no `#` prefix / no spaces / max 2 hierarchical levels.

Auto-fixes long dashes in the file body (`-`, `-`, `-` -> ASCII `-`). Writes back to disk; the `--no-content-check` flag disables this.

Use `--fail-on-error` in CI to break the build on any frontmatter error. On 2026-07-03 the repo has 133 / 142 scanned files with at least one frontmatter error - work in progress to bring them to compliance.

## `code_auditor/` package (Phase 2)

The `code_auditor/` package (CLI + 6 heuristics) lives in its own self-contained subfolder. See [`code_auditor/README - code_auditor.md`](code_auditor/README%20-%20code_auditor.md) for the full doc. Wired via `[AUDIT] Odin Code Audit (PVG03_RPG)` task.

## For the public release checklist

See [`_Helpers/docs/005_public_release_checklist.md`](../../docs/005_public_release_checklist.md) for the full pre-push procedure that uses these scripts.
