"""JSONC parsing and schema validation for the `code_auditor` rules file.

Public surface:

- `strip_jsonc_comments(text)` - strip `//` line comments and `/* */` block comments from JSONC text, returning JSON-parseable text.
- `load_rules(path)` - read a `.jsonc` rules file, strip comments, validate against the schema, return the parsed `dict`.
- `load_schema(path)` - load the JSON Schema from disk.
- `validate_rules(rules, schema)` - raise `jsonschema.ValidationError` if invalid, otherwise return `None`.
- `RuleLoadError` - exception class for reporting parse / validate failures with context.

Stdlib only (`json`, `re`, `pathlib`, `dataclasses`) plus the optional third-party `jsonschema` package. Cross-platform (Windows / Unix).
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import jsonschema  # type: ignore[import-untyped]
except ImportError as exc:  # pragma: no cover - jsonschema is mandatory for the auditor
    raise ImportError(
        "The `jsonschema` package is required by code_auditor.rule_loader. "
        "Install it with: pip install jsonschema>=4.0"
    ) from exc

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


def strip_jsonc_comments(text: str) -> str:
    """Return `text` with `//` line comments and `/* */` block comments removed.

    A correct JSONC stripper must understand string literals: a `//` inside a JSON string is NOT a comment, it is part of the value.
    We implement this with a small state machine that walks the input character by character, tracking whether we are inside a double-quoted string.
    Backslash escapes inside a string are respected, so a literal `\"` does not toggle the string state.
    This is stdlib-only and matches the behaviour expected by the `odin_rules.jsonc` file shipped with the auditor, whose KB-001 title legitimately contains the literal text `// lesson NNN` between backticks.
    """
    if not text:
        return text

    out: list[str] = []
    i = 0
    n = len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\":
                if i + 1 < n:
                    out.append(text[i + 1])
                    i += 2
                    continue
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            out.append(ch)
            in_string = True
            i += 1
            continue
        if ch == "/" and i + 1 < n:
            nxt = text[i + 1]
            if nxt == "/":
                while i < n and text[i] != "\n":
                    i += 1
                continue
            if nxt == "*":
                i += 2
                while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                    i += 1
                i = min(i + 2, n)
                continue
        out.append(ch)
        i += 1
    return "".join(out)


@dataclass
class RuleLoadError(Exception):
    """Raised when a rules file cannot be loaded or fails schema validation.

    Attributes:
        message: human-readable summary.
        path: rules file path (may be `None`).
        issues: list of structured diagnostics (line / col / msg when available).
    """

    message: str
    path: Path | None = None
    issues: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        head = self.message if not self.path else f"{self.message} ({self.path})"
        if not self.issues:
            return head
        body = "\n  - ".join(self.issues)
        return f"{head}\n  - {body}"


def load_schema(path: Path | str) -> dict[str, Any]:
    """Load and return the JSON Schema from `path` as a Python dict."""
    schema_path = Path(path)
    if not schema_path.is_file():
        raise RuleLoadError(f"Schema file not found: {schema_path}", path=schema_path)
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuleLoadError(f"Cannot read schema: {exc}", path=schema_path) from exc
    if not isinstance(data, dict):
        raise RuleLoadError("Schema root must be a JSON object", path=schema_path)
    return data


def _collect_schema_issues(exc: jsonschema.ValidationError) -> list[str]:
    """Walk a `ValidationError` tree and emit one human-readable line per leaf error."""
    issues: list[str] = []

    def walk(err: jsonschema.ValidationError, prefix: str) -> None:
        if err.context:
            for sub in err.context:
                walk(sub, prefix)
            return
        if err.absolute_path:
            loc = "/".join(str(p) for p in err.absolute_path)
            loc_str = f"$.{loc}"
        else:
            loc_str = prefix or "$"
        issues.append(f"{loc_str}: {err.message}")

    walk(exc, prefix="rules[]")
    return issues


def validate_rules(rules: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate `rules` against `schema`. Raise `RuleLoadError` on failure."""
    validator_cls = jsonschema.Draft7Validator
    validator = validator_cls(schema)
    errors = sorted(validator.iter_errors(rules), key=lambda e: list(e.absolute_path))
    if not errors:
        return
    first = errors[0]
    raise RuleLoadError(
        "Rules file failed schema validation",
        path=None,
        issues=_collect_schema_issues(first),
    )


def load_rules(
    path: Path | str,
    schema_path: Path | str | None = None,
) -> dict[str, Any]:
    """Load a `.jsonc` rules file, strip comments, optionally validate against the schema.

    Args:
        path: path to the `.jsonc` file to load.
        schema_path: optional path to the JSON Schema. If `None`, no validation is performed and the raw dict is returned.

    Returns:
        Parsed rules dict, with at least the keys `version` (str) and `rules` (list).
    """
    rules_path = Path(path)
    if not rules_path.is_file():
        raise RuleLoadError(f"Rules file not found: {rules_path}", path=rules_path)

    try:
        with open(rules_path, "r", encoding="utf-8") as f:
            raw = f.read()
    except OSError as exc:
        raise RuleLoadError(f"Cannot read rules file: {exc}", path=rules_path) from exc

    try:
        stripped = strip_jsonc_comments(raw)
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise RuleLoadError(
            f"Rules file is not valid JSONC (line {exc.lineno}, col {exc.colno}): {exc.msg}",
            path=rules_path,
        ) from exc

    if not isinstance(data, dict):
        raise RuleLoadError(
            "Rules file root must be a JSON object",
            path=rules_path,
        )
    if "rules" not in data or not isinstance(data["rules"], list):
        raise RuleLoadError(
            "Rules file must contain a top-level 'rules' array",
            path=rules_path,
        )
    if not data["rules"]:
        raise RuleLoadError(
            "Rules file must declare at least one rule",
            path=rules_path,
        )

    if schema_path is not None:
        schema = load_schema(schema_path)
        try:
            validate_rules(data, schema)
        except RuleLoadError as exc:
            exc.path = rules_path
            raise

    return data


def list_active_rule_ids(rules: dict[str, Any]) -> list[str]:
    """Return the IDs of the rules declared in the file, in source order."""
    return [str(rule["id"]) for rule in rules["rules"] if isinstance(rule, dict) and "id" in rule]


__all__ = [
    "RuleLoadError",
    "strip_jsonc_comments",
    "load_schema",
    "validate_rules",
    "load_rules",
    "list_active_rule_ids",
]
