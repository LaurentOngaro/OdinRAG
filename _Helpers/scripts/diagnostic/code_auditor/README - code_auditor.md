# README - code_auditor

> User-facing doc for the Odin code auditor rules system. The CLI is now functional (Phase 2).
> LLM-enhanced reviews (Phase 4) and `--fix-safe` (Phase 5) are still ahead. Phase 1 + Phase 2 are both delivered in this package.

## What this is

A static + heuristic audit of Odin code against project conventions and KB-cited best practices. It detects allocator misuse, wrong data structures, anti-patterns, and KB-citation drift. The rules are user-editable JSONC, validated against a JSON Schema.

The auditor is split in three layers:

- **L1 - Python regex** - <10 ms/file - tabs, `using`, `var` at top level, `tracking_allocator` outside Debug
- **L2 - Heuristic multi-line** - ~50 ms/file - allocations in loops, `defer` in `for`, struct field count, lesson references
- **L3 - LLM via subagent** - 2-5 s/file - map vs slice tradeoff, SoA suggestion, allocator mismatch (Phase 4)

L1+L2 run in headless mode (`code_auditor.py`) and are deterministic. L3 runs in conversational mode and is non-deterministic.

## Location

Everything related to the auditor lives in this self-contained folder:

```
_Helpers/scripts/diagnostic/code_auditor/
├── __init__.py                   <- package marker, docstring only
├── code_auditor.py               <- CLI entry point (headless mode)
├── odin_rules.jsonc              <- user-editable rules file (10 rules at v1.0.0)
├── odin_rules.schema.json        <- JSON Schema draft-07 that validates odin_rules.jsonc
├── rule_loader.py                <- JSONC parsing + jsonschema validation
├── scanner.py                    <- regex L1 + heuristics L2
├── reporter.py                   <- Markdown output per spec §6.2
└── README - code_auditor.md      <- this file
```

The package is self-contained: no other module in the repo imports its siblings today. If Phase 3 introduces `kb_index.py` / `context_builder.py` that want to share `scanner.Finding` or `reporter.build_report`, those helpers can be promoted back to `_Helpers/scripts/lib/` without breaking the CLI.

## CLI usage

Run from the repo root. Every command writes the Markdown report to stdout unless `--report <path>` redirects it to a file.

```bash
# Audit one file
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --file code/projects/PVG03_RPG/src/main.odin

# Audit a directory recursively (default scope: *.odin)
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path code/projects/PVG03_RPG/src

# Choose the build mode (controls ALLOC-001 trigger)
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path src --build-mode Release

# Save the report to a file
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path src --report audit.md

# Validate the rules file (no scan)
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --validate-rules

# List active rules (or filter by category)
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --list-rules
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --list-rules --category allocator

# Dry-run: list rules + their detection method
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --check

# CI: non-zero exit when any warning or error is found
python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path src --strict
```

Or invoke as a module (`python -m` adds the parent dir to `sys.path`):

```bash
cd _Helpers/scripts/diagnostic
python -m code_auditor.code_auditor --path ../../../code/projects/PVG03_RPG/src
```

## Exit codes

- `0` - no error found (only info, or no findings)
- `1` - at least one warning (or rule-loading problem); `--strict` promotes this gate
- `2` - at least one error
- `3` - unrecoverable setup error (missing rules file, bad args, ...)

## Detected heuristics (Phase 2)

Six heuristics are wired to the rules file via the `detect` field. They run after the comment stripper, so `// ...` inside strings or backtick raw strings is honored.

- `alloc-in-loop` - `make(...)`, `new(...)`, `alloc(...)` while a `for`/`while` block is still open
- `defer-in-loop` - a `defer` statement whose nearest enclosing loop has not yet closed
- `small-map` - `map[K]V` with both K and V simple (int / string / primitive)
- `large-struct-mixed-access` - `struct` with > 8 fields where >= 2 procedures each touch < 40% of them
- `unfreed-slice` - `make([]T, ...)` whose bound name has no `delete(...)` or arena context nearby
- `lesson-ref-validation` - `// lesson NNN` comments that resolve to NO file in `odin-knowledge-base/`

L1 regex rules (ALLOC-001, ODIN-001, ODIN-002) run straight against the rule's `pattern` field, line by line on the comment-stripped content. The `applies_when.build_mode` clause is honored (case-insensitive): rules declaring `{"build_mode": "release"}` are skipped in Debug mode.

## Rule file anatomy

Each rule in `odin_rules.jsonc` is one JSON object with these fields:

- `id` - required - string - Matches `^[A-Z]+-\d{3}$` (e.g. `ALLOC-001`, `DS-002`, `ODIN-003`)
- `title` - required - string - One-line description, min 10 chars
- `category` - required - enum - `style`, `allocator`, `data-structure`, `anti-pattern`, `architecture`, `kb-compliance`
- `severity` - required - enum - `error` (blocks strict-mode CI), `warning` (report-only), `info` (informational)
- `static` - required - boolean - True if regex/heuristic can detect without LLM
- `scope` - optional - array - Glob patterns like `["*.odin"]`
- `pattern` - optional - string - Python regex for L1 detection
- `detect` - optional - string - Named heuristic for L2 detection (e.g. `alloc-in-loop`)
- `applies_when` - optional - object - Conditions like `{"build_mode": "release"}`
- `explanation` - required - string - The "why" of the rule, min 20 chars, must be citable
- `kb_sources` - optional - array - Repo-relative paths to KB files
- `lesson_refs` - optional - array - Skool lesson IDs (e.g. `["088"]`)
- `fix_suggestion` - optional - string - Code-level hint

`pattern` and `detect` are mutually exclusive in practice: regex for static text patterns, named heuristic for multi-line structural analysis.

## Adding a rule

Copy an existing rule, give it a new ID, fill the fields. The ID format is `{CATEGORY}-{3 digits}`, with categories mapped to prefixes:

- `allocator` → `ALLOC-` (current: 3, ALLOC-001..003)
- `data-structure` → `DS-` (current: 3, DS-001..003)
- `anti-pattern` → `ODIN-` (current: 3, ODIN-001..003)
- `kb-compliance` → `KB-` (current: 1, KB-001)
- `architecture` → `ARCH-` (current: 0, free)
- `style` → `STYLE-` (current: 0, free, covered by `odinfmt`)

Then validate with `code_auditor.py --validate-rules`. If the new rule requires a new heuristic, also add a `detect_<name>` function in `scanner.py` and register it in the `_HEURISTICS` table.

## Disabling a rule temporarily

Remove the JSON object from `odin_rules.jsonc`. The KB links stay in git history; restoring the rule is a one-line revert. There is no in-rule `enabled: false` flag yet (deliberate, to keep the schema simple).

## Profiles

The `extends` array in the JSONC file declares which preset names are active for this rule file. Phase 2 does not yet apply per-profile filtering: every rule is active for every profile by default. The CLI accepts `--profile <name>` today (it sets the `Profile:` line of the report header) and auto-detects `odin-pvg03-rpg` when the target path contains `code/projects/PVG03_RPG/`.

Reserved profile names:

- `odin-core` - base for any Odin project
- `odin-pvg03-rpg` - adds RPG-lesson specific rules (auto-detected for PVG03_RPG)
- `odin-cli` - CLI-only Odin projects, allocator rules kept light
- `odin-strict` - CI-gate mode

## Extending for a project

Add a project override block:

```jsonc
{
  "project_overrides": {
    "MY_PROJECT": {
      "extra_rules": ["MY-001", "MY-002"]
    }
  }
}
```

`MY-001` and `MY-002` must exist as rule IDs somewhere (typically in `odin_rules.jsonc` itself or a project-local `odin_rules.<project>.jsonc`).

## Why JSONC, not YAML or TOML

- **JSONC (chosen)** - `//`, `/* */` comments, nested objects yes, full schema tooling, native JSON compatibility (after comment strip)
- **YAML** - comments yes, nested objects yes, full schema tooling, needs parsing
- **TOML** - comments yes, nested objects limited, limited schema tooling, needs parsing
- **JSON5** - comments yes, nested objects yes, limited schema tooling, native JSON compatibility (after parsing)

JSONC keeps the file valid JSON after comment stripping, which means any standard JSON tool (linters, editors, diff viewers) can process it. The `rule_loader.py` stripper understands string literals, so a comment-like `//` inside a string survives.

## Reference

- Spec: `_Private/raw/2026-07-01_code_auditor_odin_preconisations.md` (sections 4, 6, 7, 13)
- Package root: `_Helpers/scripts/diagnostic/code_auditor/`
- Schema: `_Helpers/scripts/diagnostic/code_auditor/odin_rules.schema.json`
- Rules file: `_Helpers/scripts/diagnostic/code_auditor/odin_rules.jsonc`
- CLI: `_Helpers/scripts/diagnostic/code_auditor/code_auditor.py`
- Libs (same folder): `rule_loader.py`, `scanner.py`, `reporter.py`
- KB aggregator: `odin-knowledge-base/INDEX.md` (generated by `build_kb_index.py`)
- VS Code task: `[AUDIT] Odin Code Audit (PVG03_RPG)` in `.vscode/tasks.json`
- Lint wrapper: `_Helpers/scripts/fixes/lint_pylance.py` (used to gate the Python modules)
