"""Markdown report builder for `code_auditor` Phase 2.

Produces a self-contained Markdown document that follows the template in `_Private/raw/2026-07-01_code_auditor_odin_preconisations.md` §6.2:

- Header block (target / profile / build mode / date / rule counts).
- Severity summary (error / warning / info counts) as a bullet list, then a verdict line.
- Errors / Warnings / Info sections, each grouped by rule ID, each with file, snippet, why, KB sources, lesson refs, fix suggestion when present.
- "Files audited" table at the end (one row per file).

Tables are reserved for the file-list summary (the only place a real spec template shows them; elsewhere we use bullet lists for markdownlint MD060 compatibility). All punctuation is ASCII (no em-dashes, no smart quotes) per the project's AGENTS.md § Punctuation.

Public surface:

- `ReportTarget` - dataclass describing the audit context.
- `build_report(target, findings, rule_count)` - return the Markdown text.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


@dataclass
class ReportTarget:
    """The audit context carried into the report header."""

    target_path: Path
    profile: str = "default"
    build_mode: str = "Debug"
    rule_count: int = 0
    extra_note: str = ""
    files_scanned: int = 0
    file_summaries: list[tuple[str, int, int, int, int]] = field(default_factory=list)


_SECTION_ORDER = ["error", "warning", "info"]
_SECTION_HEADING = {
    "error": "## Errors (blocking)",
    "warning": "## Warnings",
    "info": "## Info (suggestions)",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _group_by_rule(findings: Iterable) -> dict[str, list]:
    """Group findings by rule_id, preserving insertion order of rule_id."""
    grouped: dict[str, list] = {}
    for finding in findings:
        grouped.setdefault(finding.rule_id, []).append(finding)
    return grouped


def _finding_block(finding, target: ReportTarget) -> list[str]:
    """Build the Markdown bullet block for one Finding (body only, no heading)."""
    lines: list[str] = []
    try:
        rel = finding.file.resolve().relative_to(target.target_path.resolve().parent)
    except (ValueError, FileNotFoundError):
        rel = finding.file
    if isinstance(rel, Path):
        rel_str = str(rel).replace("\\", "/")
    else:
        rel_str = str(rel).replace("\\", "/")

    lines.append(f"- **File** : `{rel_str}:{finding.line}`")
    if finding.snippet:
        snippet = finding.snippet
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        lines.append(f"- **Snippet** : `{snippet}`")
    if finding.explanation:
        lines.append(f"- **Why** : {finding.explanation}")
    if finding.kb_sources:
        lines.append("- **Sources KB** :")
        for src in finding.kb_sources:
            lines.append(f"  - `{src}`")
    if finding.lesson_refs:
        lessons = ", ".join(finding.lesson_refs)
        lines.append(f"- **Lessons** : {lessons}")
    if finding.fix_suggestion:
        lines.append(f"- **Fix** : {finding.fix_suggestion}")
    lines.append("")
    return lines


def build_report(
    target: ReportTarget,
    findings: list,
    rule_count: int,
) -> str:
    """Render the Markdown report. Returns a string."""
    target.rule_count = rule_count
    parts: list[str] = []
    target_rel = target.target_path
    if isinstance(target_rel, Path):
        target_rel = str(target_rel).replace("\\", "/")

    parts.append("# Odin Code Audit Report")
    parts.append("")
    parts.append(f"- **Target** : `{target_rel}` ({target.files_scanned} files)")
    parts.append(f"- **Profile** : `{target.profile}`")
    parts.append(f"- **Build mode** : `{target.build_mode}`")
    parts.append(f"- **Date** : {_now_iso()}")
    parts.append(f"- **Active rules** : {rule_count}")
    if target.extra_note:
        parts.append(f"- **Note** : {target.extra_note}")
    parts.append("")
    parts.append("---")
    parts.append("")

    counts: dict[str, int] = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        if finding.severity in counts:
            counts[finding.severity] += 1

    parts.append("## Summary")
    parts.append("")
    parts.append(f"- error : {counts['error']}")
    parts.append(f"- warning : {counts['warning']}")
    parts.append(f"- info : {counts['info']}")
    parts.append("")

    if counts["error"] > 0:
        verdict = f"{counts['error']} blocking error(s) - must be fixed before commit."
    elif counts["warning"] > 0:
        verdict = f"{counts['warning']} warning(s) - review recommended."
    elif counts["info"] > 0:
        verdict = f"No errors or warnings. {counts['info']} info item(s) for context."
    else:
        verdict = "Clean - no findings from any active rule."
    parts.append(f"**Verdict** : {verdict}")
    parts.append("")
    parts.append("---")
    parts.append("")

    by_rule = _group_by_rule(findings)
    for severity in _SECTION_ORDER:
        rule_ids = [rid for rid, items in by_rule.items() if items and items[0].severity == severity]
        rule_ids.sort()
        section_findings = []
        for rid in rule_ids:
            section_findings.extend(by_rule[rid])
        if not section_findings:
            if severity == "error":
                parts.append("## Errors (blocking)")
                parts.append("")
                parts.append("None.")
                parts.append("")
                parts.append("---")
                parts.append("")
            continue
        parts.append(_SECTION_HEADING[severity])
        parts.append("")
        for rid in rule_ids:
            items = by_rule[rid]
            sample = items[0]
            parts.append(f"### [{rid}] {sample.title}")
            parts.append("")
            for f in items:
                parts.extend(_finding_block(f, target))
        parts.append("---")
        parts.append("")

    parts.append("## Files audited")
    parts.append("")
    parts.append("| File | Lines | Errors | Warnings | Info |")
    parts.append("| ---- | ----- | ------ | -------- | ---- |")
    if target.file_summaries:
        for path_str, lines_n, err_n, warn_n, info_n in target.file_summaries:
            rel = path_str.replace("\\", "/")
            parts.append(f"| `{rel}` | {lines_n} | {err_n} | {warn_n} | {info_n} |")
        total_lines = sum(s[1] for s in target.file_summaries)
        total_err = sum(s[2] for s in target.file_summaries)
        total_warn = sum(s[3] for s in target.file_summaries)
        total_info = sum(s[4] for s in target.file_summaries)
        parts.append(
            f"| **TOTAL** | {total_lines} | {total_err} | {total_warn} | {total_info} |"
        )
    else:
        parts.append("| _no files scanned_ | 0 | 0 | 0 | 0 |")
    parts.append("")

    return "\n".join(parts).rstrip() + "\n"


__all__ = ["ReportTarget", "build_report"]
