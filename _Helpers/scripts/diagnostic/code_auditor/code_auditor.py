#!/usr/bin/env python3
"""_Helpers/scripts/diagnostic/code_auditor/code_auditor.py - Headless auditor for Odin code.

CLI entry point of the `code_auditor` system. Walks one or more files / directories, applies the rules from `_Helpers/scripts/diagnostic/code_auditor/odin_rules.jsonc`, and emits a Markdown report.

Quick start:

    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path code/projects/PVG03_RPG/src
    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --file src/main.odin
    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --check
    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --validate-rules
    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --list-rules --category allocator
    python _Helpers/scripts/diagnostic/code_auditor/code_auditor.py --path src --report _Helpers/scripts/diagnostic/code_auditor/latest_audit.md

Exit codes (per spec §6.3):

    0 - no error (only info, or no findings at all)
    1 - at least one warning (or rule-loading error)
    2 - at least one error
    3 - unrecoverable config / setup error

Stdlib only (plus `jsonschema` and the package's sibling modules). Cross-platform (Windows + Unix).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
import textwrap
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

_PKG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PKG_DIR.parents[3]

if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

from rule_loader import (
    RuleLoadError,
    list_active_rule_ids,
    load_rules,
    load_schema,
    validate_rules,
)
from scanner import Finding, scan_file
from reporter import ReportTarget, build_report


DEFAULT_RULES = _PKG_DIR / "odin_rules.jsonc"
DEFAULT_SCHEMA = _PKG_DIR / "odin_rules.schema.json"
DEFAULT_KB_ROOT = _REPO_ROOT / "odin-knowledge-base"

_PROFILE_PROJECT_HINTS = {
    "code/projects/PVG03_RPG/AGENTS.md": "odin-pvg03-rpg",
}

_CATEGORY_ORDER = (
    "allocator",
    "data-structure",
    "anti-pattern",
    "kb-compliance",
    "architecture",
    "style",
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Configure argparse per spec §6.1 and parse."""
    parser = argparse.ArgumentParser(
        prog="code_auditor.py",
        description=(
            "Headless static + heuristic auditor for Odin code. "
            "Walks .odin files, applies user-editable rules, emits a Markdown report."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            exit codes:
              0 - no error (only info, or no findings)
              1 - at least one warning, or rule-loading problem
              2 - at least one error
              3 - unrecoverable setup error
            """
        ),
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--file",
        "-f",
        help="Audit a single .odin file. Use --path for recursive scan.",
    )
    target.add_argument(
        "--path",
        "-p",
        help="Audit a directory recursively. Default scope: *.odin",
    )

    parser.add_argument(
        "--report",
        "-r",
        help="Write the Markdown report to this file (default: stdout).",
    )
    parser.add_argument(
        "--profile",
        default=None,
        help=(
            "Profile to apply (odin-core, odin-pvg03-rpg, odin-cli, odin-strict). "
            "Auto-detected from path if --profile is omitted."
        ),
    )
    parser.add_argument(
        "--rules",
        default=str(DEFAULT_RULES),
        help=f"Path to the JSONC rules file (default: {DEFAULT_RULES.name}).",
    )
    parser.add_argument(
        "--schema",
        default=str(DEFAULT_SCHEMA),
        help=f"Path to the JSON Schema (default: {DEFAULT_SCHEMA.name}).",
    )
    parser.add_argument(
        "--kb-root",
        default=None,
        help=(
            "Root for resolving lesson references in KB-001. "
            f"Default: {DEFAULT_KB_ROOT}"
        ),
    )
    parser.add_argument(
        "--build-mode",
        default="Debug",
        choices=["Debug", "Release"],
        help="Tracked in the report header (default: Debug).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blocking (exit 1) in addition to errors (exit 2).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable terminal colors (placeholder for future colored output).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: list active rules and exit (no scan performed).",
    )
    parser.add_argument(
        "--validate-rules",
        action="store_true",
        help="Validate the rules file against the schema, then exit.",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="List the active rules, optionally filtered by --category.",
    )
    parser.add_argument(
        "--category",
        help="Filter --list-rules by category (allocator, data-structure, etc.).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress per-file progress logs on stderr.",
    )
    return parser.parse_args(argv)


def _detect_profile(path: Path) -> str:
    """Return the active profile name based on `path`."""
    try:
        resolved = path.resolve()
    except OSError:
        return "default"
    rel = str(resolved)
    if "PVG03_RPG" in rel.replace("\\", "/"):
        return "odin-pvg03-rpg"
    return "default"


def _matches_profile(rule: dict, profile: str) -> bool:
    """Decide whether a rule is active for the given profile.

    Spec §4.2 only defines the profile names at a high level; Phase 2 treats
    every rule as active for every profile (the JSON file is small enough that
    additional filtering rules belong in a later phase). Keeps the doors open
    for an explicit `profile` field on each rule without shipping a buggy
    filter today.
    """
    if profile == "default":
        return True
    return True


def _walk_for_odin(paths: list[Path], quiet: bool) -> list[Path]:
    """Collect .odin files from the given list of files / dirs / globs."""
    seen: set[Path] = set()
    out: list[Path] = []
    for raw in paths:
        if not raw.exists():
            if not quiet:
                print(f"[skip] {raw} does not exist", file=sys.stderr)
            continue
        if raw.is_file():
            if raw.suffix.lower() == ".odin" and raw not in seen:
                seen.add(raw)
                out.append(raw)
            continue
        for p in raw.rglob("*"):
            if not p.is_file() or p.suffix.lower() != ".odin":
                continue
            if p in seen:
                continue
            seen.add(p)
            out.append(p)
    out.sort()
    return out


def _summaries_by_file(findings: list[Finding], files: list[Path]) -> list[tuple[str, int, int, int, int]]:
    """Return per-file (relpath, lines, errors, warnings, info) tuples."""
    by_file: dict[Path, dict[str, int]] = {
        p: {"errors": 0, "warnings": 0, "info": 0, "lines": 0} for p in files
    }
    for f in findings:
        slot = by_file.get(f.file)
        if slot is None:
            continue
        key = (
            "errors" if f.severity == "error"
            else "warnings" if f.severity == "warning"
            else "info"
        )
        slot[key] += 1
    rows: list[tuple[str, int, int, int, int]] = []
    for p in files:
        slot = by_file[p]
        try:
            lines_count = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            lines_count = 0
        rel = str(p).replace("\\", "/")
        rows.append((rel, lines_count, slot["errors"], slot["warnings"], slot["info"]))
    return rows


def _exit_code(findings: list[Finding], strict: bool) -> int:
    """Map findings to the appropriate exit code."""
    has_error = any(f.severity == "error" for f in findings)
    has_warning = any(f.severity == "warning" for f in findings)
    if has_error:
        return 2
    if has_warning and strict:
        return 1
    return 0


def _cmd_check(rules: list[dict], rule_path: Path) -> int:
    """Print active rules and exit. Used by --check."""
    print(f"[check] {len(rules)} active rule(s) in {rule_path}")
    for rule in rules:
        flags: list[str] = []
        if "pattern" in rule and rule.get("pattern"):
            flags.append("regex")
        if rule.get("detect"):
            flags.append(f"heuristic:{rule['detect']}")
        suffix = f" [{', '.join(flags)}]" if flags else ""
        print(f"  - {rule['id']:<12} {rule.get('severity', ''):<8} "
              f"{rule.get('category', ''):<14} {rule.get('title', '')}{suffix}")
    return 0


def _cmd_list_rules(rules: list[dict], category: str | None) -> int:
    """Print rules filtered by category (or all), then exit."""
    by_cat: dict[str, list[dict]] = {cat: [] for cat in _CATEGORY_ORDER}
    others: list[dict] = []
    for rule in rules:
        cat = str(rule.get("category", ""))
        if cat in by_cat:
            by_cat[cat].append(rule)
        else:
            others.append(rule)
    if category:
        if category not in by_cat:
            print(f"[ERR] Unknown category: {category}", file=sys.stderr)
            print(f"      Known categories: {', '.join(c for c in _CATEGORY_ORDER)}", file=sys.stderr)
            return 3
        rules = by_cat[category]
        print(f"[list] Category: {category} ({len(rules)} rule(s))")
        for rule in rules:
            print(f"  - {rule['id']} ({rule.get('severity', '')}) - {rule.get('title', '')}")
        return 0
    print(f"[list] {len(rules)} active rule(s), grouped by category:")
    for cat in _CATEGORY_ORDER:
        items = by_cat[cat]
        if not items:
            continue
        print(f"\n  {cat} ({len(items)} rule(s)):")
        for rule in items:
            print(f"    - {rule['id']:<12} {rule.get('severity', ''):<8} {rule.get('title', '')}")
    if others:
        print(f"\n  uncategorised ({len(others)} rule(s)):")
        for rule in others:
            print(f"    - {rule['id']} - {rule.get('title', '')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    rule_path = Path(args.rules)
    schema_path = Path(args.schema)
    if not rule_path.is_file():
        print(f"[ERR] Rules file not found: {rule_path}", file=sys.stderr)
        return 3
    if not schema_path.is_file():
        print(f"[ERR] Schema file not found: {schema_path}", file=sys.stderr)
        return 3

    try:
        rules_doc = load_rules(rule_path, schema_path)
    except RuleLoadError as exc:
        print(f"[ERR] {exc}", file=sys.stderr)
        return 3

    rules = rules_doc.get("rules", [])
    rule_ids = list_active_rule_ids(rules_doc)

    if args.check:
        return _cmd_check(rules, rule_path)
    if args.validate_rules:
        try:
            schema = load_schema(schema_path)
            validate_rules(rules_doc, schema)
        except RuleLoadError as exc:
            print(f"[ERR] Rules validation failed: {exc}", file=sys.stderr)
            return 1
        print(f"[OK] Rules valid against schema ({len(rules)} rule(s)): {', '.join(rule_ids)}")
        return 0
    if args.list_rules:
        return _cmd_list_rules(rules, args.category)

    targets: list[Path] = []
    target_label: Path
    if args.file:
        target_label = Path(args.file).resolve()
        targets = [Path(args.file)]
    elif args.path:
        target_label = Path(args.path).resolve()
        targets = [Path(args.path)]
    else:
        print("[ERR] Provide --file or --path (or use --check / --list-rules).", file=sys.stderr)
        return 3

    profile = args.profile or _detect_profile(target_label)
    if profile != "default":
        rules = [r for r in rules if _matches_profile(r, profile)]

    kb_root: Path | None
    if args.kb_root:
        kb_root = Path(args.kb_root)
    elif DEFAULT_KB_ROOT.exists():
        kb_root = DEFAULT_KB_ROOT
    else:
        kb_root = None

    files = _walk_for_odin(targets, quiet=args.quiet)
    if not files:
        print(f"[warn] No .odin files found under {targets}", file=sys.stderr)
        return 0

    findings: list[Finding] = []
    for path in files:
        if not args.quiet:
            print(f"[scan] {path}", file=sys.stderr)
        findings.extend(scan_file(path, rules, kb_root=kb_root, build_mode=args.build_mode))

    summaries = _summaries_by_file(findings, files)
    report_target = ReportTarget(
        target_path=target_label,
        profile=profile,
        build_mode=args.build_mode,
        rule_count=len(rules),
        files_scanned=len(files),
        file_summaries=summaries,
        extra_note=(
            f"{len(findings)} finding(s) across {len(files)} file(s)"
        ),
    )
    md = build_report(report_target, findings, len(rules))

    if args.report:
        out_path = Path(args.report)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"[+] Report written to {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(md)

    if not args.quiet:
        print(
            f"[done] {len(findings)} finding(s); exit code {_exit_code(findings, args.strict)}",
            file=sys.stderr,
        )

    return _exit_code(findings, args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
