"""Self-contained `code_auditor` package.

Bundles the headless Odin code auditor:

- `code_auditor` - CLI entry point (run with `python -m code_auditor` from `_Helpers/scripts/diagnostic` or invoke `code_auditor.py` directly).
- `rule_loader` - JSONC parsing + JSON Schema validation.
- `scanner` - regex L1 + heuristic L2 detectors.
- `reporter` - Markdown output per spec §6.2.
- `odin_rules.jsonc` / `odin_rules.schema.json` - the user-editable rule set and its schema.

Phase 3 will add `kb_index.py` and `context_builder.py` here.
"""