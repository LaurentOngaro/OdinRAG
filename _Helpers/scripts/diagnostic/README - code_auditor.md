# README - code_auditor

> User-facing doc for the Odin code auditor rules system. The auditor itself (CLI + LLM agent) lands in Phase 2 / Phase 4. Phase 1 ships only the data layer: this file, the JSONC rules file, and the schema.

## What this is

A static + heuristic audit of Odin code against project conventions and KB-cited best practices. It detects allocator misuse, wrong data structures, anti-patterns, and KB-citation drift. The rules are user-editable JSONC, validated against a JSON Schema.

The auditor is split in three layers:

- **L1 - Python regex** - <10 ms/fichier - tabs, `using`, `var` at top level, `tracking_allocator` outside Debug
- **L2 - Heuristic multi-line** - ~50 ms/fichier - allocations in loops, `defer` in `for`, struct field count
- **L3 - LLM via subagent** - 2-5 s/fichier - map vs slice tradeoff, SoA suggestion, allocator mismatch

L1+L2 run in headless mode and are deterministic. L3 runs in conversational mode and is non-deterministic.

## Files in this directory

- `odin_rules.jsonc` - The user-editable rules file (10 rules at v1.0.0) - Phase 1
- `odin_rules.schema.json` - JSON Schema draft-07 that validates `odin_rules.jsonc` - Phase 1
- `code_auditor.py` - CLI entry point (headless mode) - Phase 2 (not yet)
- `README - code_auditor.md` - This file - Phase 1
- `audit_public_safety.py` - Existing sibling script for the public/private split
- `auditReadmeCoherence.py` - Existing sibling script for README coherence

Shared libs (in `_Helpers/scripts/lib/`) will be added in Phase 2: `rule_loader.py`, `scanner.py`, `kb_index.py`, `context_builder.py`, `reporter.py`.

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

Then validate with the schema:

```bash
python -c "
import json, re, jsonschema
text = open('_Helpers/scripts/diagnostic/odin_rules.jsonc', encoding='utf-8').read()
clean = re.sub(r'(?m)^\s*//.*$|^/\*[\s\S]*?\*/', '', text)
data = json.loads(clean)
schema = json.load(open('_Helpers/scripts/diagnostic/odin_rules.schema.json', encoding='utf-8'))
jsonschema.validate(data, schema)
print('OK', len(data['rules']), 'rules validated')
"
```

Phase 2 will wrap this into `code_auditor.py --validate-rules`.

## Disabling a rule temporarily

Set `"severity": "info"` to silence the report but keep the rule documented. Phase 2 will support `"severity": "off"` as an extension.

Removing a rule entirely is fine too: just delete the JSON object. The KB links stay in git history.

## Profiles

Phase 2 will resolve these preset names via the `extends` array:

- `odin-core` - adds ODIN-_, ALLOC-_, DS-001, DS-002 - base for any Odin project
- `odin-pvg03-rpg` - adds core + RPG-lesson specific rules - for `code/projects/PVG03_RPG/`
- `odin-cli` - adds core + DS-* (no allocator specifics) - for CLI-only Odin projects
- `odin-strict` - everything bumped to `error` - CI-gate mode

The active profile is chosen by `--profile <name>` or auto-detected from the presence of `code/projects/PVG03_RPG/AGENTS.md` (maps to `odin-pvg03-rpg`).

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

JSONC keeps the file valid JSON after comment stripping, which means any standard JSON tool (linters, editors, diff viewers) can process it.

## Reference

- Spec: `_Private/raw/2026-07-01_code_auditor_odin_preconisations.md` (sections 4, 6, 7, 13)
- Schema: `_Helpers/scripts/diagnostic/odin_rules.schema.json`
- Rules file: `_Helpers/scripts/diagnostic/odin_rules.jsonc`
- KB aggregator: `odin-knowledge-base/INDEX.md` (generated by `build_kb_index.py`)
- KB source filter: `_Helpers/scripts/fixes/lint_pylance.py` (existing pyright wrapper for Phase 2 python code)
