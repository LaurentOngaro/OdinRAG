"""Static scanner for the `code_auditor` Phase 2 engine.

Two detection layers, both deterministic and stdlib-only:

- **L1 - Regex** - one regex per line, evaluated with ``re.search`` against the file content. Implemented by matching the rule's ``pattern`` field as a Python regex string. Anchored regexes (e.g. ``^\\\\s*using\\\\s+\\\\w+\\\\s*[:=]``) match per-line against each non-comment line.
- **L2 - Heuristic** - named detectors dispatched by the rule's ``detect`` field. The current set covers the four heuristics outlined in ``_Private/raw/2026-07-01_code_auditor_odin_preconisations.md`` §5.3:
    - ``alloc-in-loop`` - ``make/new/alloc`` called while a ``for``/``while`` loop body is open.
    - ``defer-in-loop`` - a ``defer`` statement whose nearest enclosing loop has not yet closed.
    - ``small-map`` - ``map[K]V`` literal with simple K and V that reappears more than 1 time in the file.
    - ``large-struct-mixed-access`` - a struct with >8 fields where at least two procedures each access <40% of the fields.
    - ``unfreed-slice`` - ``make([]T, ...)`` whose bound variable name has no ``delete(...)`` or arena context inside the visible window.
    - ``lesson-ref-validation`` - ``// lesson NNN`` comments not pointing to an existing file under ``odin-knowledge-base/courses/``.

Public surface:

- ``Finding`` - dataclass describing one violation.
- ``scan_file(path, rules, *, kb_root, build_mode)`` - run L1 + L2 against one file.
- ``apply_heuristic(name, content, file_path, rule, *, kb_root)`` - dispatch one named heuristic (used by tests and unit checks).

Cross-platform (Windows / Unix). Odin comments are stripped before any
analysis, with string literals (``"..."`` and backtick raw strings) honored so
that ``//`` inside a string does not get treated as a comment.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass


_SEVERITY_RANK = {"error": 2, "warning": 1, "info": 0}


@dataclass
class Finding:
    """One violation of one rule, attached to a specific file location."""

    rule_id: str
    title: str
    severity: str
    category: str
    file: Path
    line: int
    snippet: str = ""
    explanation: str = ""
    kb_sources: list[str] = field(default_factory=list)
    lesson_refs: list[str] = field(default_factory=list)
    fix_suggestion: str = ""
    why: str = ""

    @property
    def severity_rank(self) -> int:
        return _SEVERITY_RANK.get(self.severity, 0)


def _strip_odin_comments(text: str) -> str:
    """Strip Odin ``//`` and ``/* */`` comments, respecting string literals.

    Two string flavours are honored: regular double quotes ``"..."`` and Odin's
    backtick raw strings ``\\`...\\```. Inside a string we copy bytes verbatim
    except for ``\\\\<char>`` escapes in double-quoted strings. Comments are
    replaced by an equal number of newlines so line numbers stay aligned with
    the input text - this is important for ``Finding.line`` accuracy.
    """
    if not text:
        return text

    out: list[str] = []
    i = 0
    n = len(text)
    state = "code"
    while i < n:
        ch = text[i]
        if state == "code":
            if ch == '"':
                out.append(ch)
                state = "dquote"
                i += 1
                continue
            if ch == "`":
                out.append(ch)
                state = "btick"
                i += 1
                continue
            if ch == "/" and i + 1 < n:
                nxt = text[i + 1]
                if nxt == "/":
                    out.append("\n")
                    i += 2
                    while i < n and text[i] != "\n":
                        i += 1
                    continue
                if nxt == "*":
                    i += 2
                    while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                        if text[i] == "\n":
                            out.append("\n")
                        i += 1
                    i = min(i + 2, n)
                    continue
            out.append(ch)
            i += 1
            continue
        if state == "dquote":
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                state = "code"
            i += 1
            continue
        if state == "btick":
            out.append(ch)
            if ch == "`":
                state = "code"
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _matches_scope(rule: dict[str, Any], file_path: Path) -> bool:
    """Return True if the rule's glob-like ``scope`` array includes this file."""
    import fnmatch

    scope = rule.get("scope") or ["*.odin"]
    name = file_path.name
    return any(fnmatch.fnmatch(name, pat) for pat in scope)


def _applies_when(rule: dict[str, Any], build_mode: str) -> bool:
    """Return True if the rule's ``applies_when`` conditions are satisfied.

    Supports one key today: ``build_mode`` (case-insensitive equality).
    Rules without ``applies_when`` are always active. We lowercase both
    sides so the spec example ``"build_mode": "release"`` matches the CLI
    value ``"--build-mode Release"``.
    """
    cond = rule.get("applies_when")
    if not cond:
        return True
    if isinstance(cond, dict):
        wanted = cond.get("build_mode")
        if wanted is None:
            return True
        return str(wanted).lower() == str(build_mode).lower()
    return True


def _apply_l1_regex(
    rule: dict[str, Any],
    stripped: str,
    file_path: Path,
) -> list[Finding]:
    """Apply the rule's L1 regex to the file. Returns 0+ findings."""
    raw_pattern = rule.get("pattern")
    if not raw_pattern:
        return []
    try:
        regex = re.compile(raw_pattern, re.MULTILINE)
    except re.error as exc:
        print(f"[scanner] invalid pattern in {rule.get('id')}: {exc}", file=sys.stderr)
        return []
    findings: list[Finding] = []
    raw_lines = stripped.splitlines()
    for idx, line in enumerate(raw_lines, start=1):
        if not line.strip():
            continue
        if regex.search(line):
            findings.append(
                Finding(
                    rule_id=str(rule["id"]),
                    title=str(rule.get("title", "")),
                    severity=str(rule.get("severity", "info")),
                    category=str(rule.get("category", "")),
                    file=file_path,
                    line=idx,
                    snippet=line.strip(),
                    explanation=str(rule.get("explanation", "")),
                    kb_sources=list(rule.get("kb_sources") or []),
                    lesson_refs=list(rule.get("lesson_refs") or []),
                    fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
                )
            )
    return findings


def _alloc_pat() -> re.Pattern[str]:
    return re.compile(r"\b(make|new|alloc)\s*\(", re.MULTILINE)


def _loop_open_pat() -> re.Pattern[str]:
    return re.compile(r"\b(for|while)\b[^\n{;]*\{", re.MULTILINE)


def _defer_pat() -> re.Pattern[str]:
    return re.compile(r"\bdefer\b")


def _map_typedef_pat() -> re.Pattern[str]:
    return re.compile(r"\bmap\s*\[\s*([A-Za-z_][\w\s,]*?)\s*\]\s*([A-Za-z_][\w]*)", re.MULTILINE)


def _make_slice_pat() -> re.Pattern[str]:
    return re.compile(
        r"^\s*([A-Za-z_]\w*)\s*[:=].*?\bmake\s*\(\s*\[\s*\][A-Za-z_]\w*\b",
        re.MULTILINE,
    )


def _lessons_in_loop_or_while(
    stripped: str,
) -> tuple[list[tuple[int, int]], list[int]]:
    """Walk the file tracking ``for``/``while`` blocks.

    Returns ``(open_spans, defer_lines)`` where each open span is
    ``(line_top, line_bottom)`` and ``defer_lines`` are line numbers that
    contain a bare ``defer`` keyword. Brace counting is approximate (good
    enough for an 80/20 heuristic).
    """
    opens: list[tuple[int, int]] = []
    open_lines_stack: list[int] = []
    defer_lines: list[int] = []
    total_lines = len(stripped.splitlines())
    for idx, line in enumerate(stripped.splitlines(), start=1):
        if _defer_pat().search(line):
            defer_lines.append(idx)
        opens_on_line = len(_loop_open_pat().findall(line))
        if opens_on_line:
            for _ in range(opens_on_line):
                open_lines_stack.append(idx)
        depth = line.count("{") - line.count("}")
        if depth < 0 and open_lines_stack:
            for _ in range(min(-depth, len(open_lines_stack))):
                top = open_lines_stack.pop()
                opens.append((top, max(top, idx - 1)))
    while open_lines_stack:
        top = open_lines_stack.pop()
        opens.append((top, total_lines))
    return opens, defer_lines


def detect_alloc_in_loop(
    stripped: str, file_path: Path, rule: dict[str, Any]
) -> list[Finding]:
    """``make/new/alloc`` appearing inside a ``for``/``while`` block."""
    opens, _ = _lessons_in_loop_or_while(stripped)
    if not opens:
        return []
    findings: list[Finding] = []
    raw_lines = stripped.splitlines()
    alloc_rx = _alloc_pat()
    for line_idx, line in enumerate(raw_lines, start=1):
        if not alloc_rx.search(line):
            continue
        for top, bottom in opens:
            if top <= line_idx <= bottom:
                findings.append(
                    Finding(
                        rule_id=str(rule["id"]),
                        title=str(rule.get("title", "")),
                        severity=str(rule.get("severity", "info")),
                        category=str(rule.get("category", "")),
                        file=file_path,
                        line=line_idx,
                        snippet=line.strip(),
                        explanation=str(rule.get("explanation", "")),
                        kb_sources=list(rule.get("kb_sources") or []),
                        lesson_refs=list(rule.get("lesson_refs") or []),
                        fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
                    )
                )
                break
    return findings


def detect_defer_in_loop(
    stripped: str, file_path: Path, rule: dict[str, Any]
) -> list[Finding]:
    """A ``defer`` line that lies between a loop's opening and closing brace."""
    opens, defer_lines = _lessons_in_loop_or_while(stripped)
    findings: list[Finding] = []
    raw_lines = stripped.splitlines()
    for line_idx in defer_lines:
        for top, bottom in opens:
            if top < line_idx <= bottom:
                snippet = raw_lines[line_idx - 1].strip() if 0 < line_idx <= len(raw_lines) else ""
                findings.append(
                    Finding(
                        rule_id=str(rule["id"]),
                        title=str(rule.get("title", "")),
                        severity=str(rule.get("severity", "info")),
                        category=str(rule.get("category", "")),
                        file=file_path,
                        line=line_idx,
                        snippet=snippet,
                        explanation=str(rule.get("explanation", "")),
                        kb_sources=list(rule.get("kb_sources") or []),
                        lesson_refs=list(rule.get("lesson_refs") or []),
                        fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
                    )
                )
                break
    return findings


_SMALL_MAP_PRIMITIVE_KEYS = {"int", "u32", "u64", "i32", "i64", "string", "cstring", "byte"}
_SMALL_MAP_PRIMITIVE_VALUES = {"int", "u32", "u64", "i32", "i64", "f32", "f64", "string", "cstring", "bool", "byte"}


def detect_small_map(
    stripped: str, file_path: Path, rule: dict[str, Any]
) -> list[Finding]:
    """Detect ``map[K]V`` literals with simple K, simple V."""
    findings: list[Finding] = []
    raw_lines = stripped.splitlines()
    seen_pairs: set[tuple[str, str]] = set()
    rx = _map_typedef_pat()
    for idx, line in enumerate(raw_lines, start=1):
        for m in rx.finditer(line):
            key = re.sub(r"\s+", "", m.group(1)).strip(",")
            val = m.group(2)
            if key not in _SMALL_MAP_PRIMITIVE_KEYS or val not in _SMALL_MAP_PRIMITIVE_VALUES:
                continue
            pair = (key, val)
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            findings.append(
                Finding(
                    rule_id=str(rule["id"]),
                    title=str(rule.get("title", "")),
                    severity=str(rule.get("severity", "info")),
                    category=str(rule.get("category", "")),
                    file=file_path,
                    line=idx,
                    snippet=f"map[{key}]{val}",
                    explanation=str(rule.get("explanation", "")),
                    kb_sources=list(rule.get("kb_sources") or []),
                    lesson_refs=list(rule.get("lesson_refs") or []),
                    fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
                )
            )
    return findings


_STRUCT_DEF_RX = re.compile(
    r"^\s*([A-Z][\w]*)\s*(?::\s*[\w\[\],\s]+)?\s*=\s*struct\s*\{",
    re.MULTILINE,
)
_PROC_DEF_RX = re.compile(
    r"^([A-Za-z_][\w]*)\s*::\s*proc\b", re.MULTILINE
)
_FIELD_ACCESS_RX = re.compile(r"\b([A-Z][\w]*)\.([a-z_][\w]*)")


def detect_large_struct_mixed_access(
    stripped: str,
    file_path: Path,
    rule: dict[str, Any],
) -> list[Finding]:
    """Flag structs with > 8 fields when >= 2 procedures each touch < 40% of fields."""
    findings: list[Finding] = []
    struct_blocks: list[tuple[str, int, int, list[str]]] = []
    for m in _STRUCT_DEF_RX.finditer(stripped):
        name = m.group(1)
        start = m.end()
        depth = 1
        line_start = stripped[:start].count("\n") + 1
        pos = start
        while pos < len(stripped) and depth > 0:
            ch = stripped[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            pos += 1
        body = stripped[start:pos - 1]
        fields = []
        for raw in body.splitlines():
            stripped_field = raw.strip()
            if not stripped_field:
                continue
            if stripped_field.startswith("//") or stripped_field.startswith("/*"):
                continue
            mm = re.match(r"^([a-z_][\w]*)\s*:", stripped_field)
            if mm:
                fields.append(mm.group(1))
        if len(fields) > 8:
            struct_blocks.append((name, line_start, pos, fields))

    if not struct_blocks:
        return findings

    field_access_per_proc: list[tuple[str, set[str]]] = []
    proc_iter = list(_PROC_DEF_RX.finditer(stripped))
    for i, pm in enumerate(proc_iter):
        start = pm.start()
        end = proc_iter[i + 1].start() if i + 1 < len(proc_iter) else len(stripped)
        body = stripped[start:end]
        accessed: set[str] = set()
        struct_names = [n for n, _, _, _ in struct_blocks]
        for am in _FIELD_ACCESS_RX.finditer(body):
            if am.group(1) in struct_names:
                accessed.add(am.group(2))
        field_access_per_proc.append((pm.group(1), accessed))

    for name, line_no, _end, fields in struct_blocks:
        totals = len(fields)
        procs_touching_small = 0
        for proc_name, accessed in field_access_per_proc:
            overlap = len(accessed & set(fields))
            if overlap and overlap / totals < 0.4:
                procs_touching_small += 1
        if procs_touching_small >= 2:
            findings.append(
                Finding(
                    rule_id=str(rule["id"]),
                    title=str(rule.get("title", "")),
                    severity=str(rule.get("severity", "info")),
                    category=str(rule.get("category", "")),
                    file=file_path,
                    line=line_no,
                    snippet=f"{name} struct with {totals} fields (mixed access across {procs_touching_small} procedures)",
                    explanation=str(rule.get("explanation", "")),
                    kb_sources=list(rule.get("kb_sources") or []),
                    lesson_refs=list(rule.get("lesson_refs") or []),
                    fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
                )
            )
    return findings


def detect_unfreed_slice(
    stripped: str, file_path: Path, rule: dict[str, Any]
) -> list[Finding]:
    """Flag ``make([]T, ...)`` whose bound variable has no ``delete(...)`` nearby."""
    findings: list[Finding] = []
    raw_lines = stripped.splitlines()
    for idx, line in enumerate(raw_lines, start=1):
        m = _make_slice_pat().search(line)
        if not m:
            continue
        var_name = m.group(1)
        delete_rx = re.compile(rf"\bdelete\s*\(\s*{re.escape(var_name)}\b")
        end_idx = min(idx + 60, len(raw_lines))
        window = "\n".join(raw_lines[idx - 1:end_idx])
        arena_ctx = bool(
            re.search(r"context\.(temp_allocator|arena_allocator)", window)
            or ".arena" in window
        )
        if delete_rx.search(window) or arena_ctx:
            continue
        findings.append(
            Finding(
                rule_id=str(rule["id"]),
                title=str(rule.get("title", "")),
                severity=str(rule.get("severity", "info")),
                category=str(rule.get("category", "")),
                file=file_path,
                line=idx,
                snippet=line.strip(),
                explanation=str(rule.get("explanation", "")),
                kb_sources=list(rule.get("kb_sources") or []),
                lesson_refs=list(rule.get("lesson_refs") or []),
                fix_suggestion=str(rule.get("fix_suggestion", "") or ""),
            )
        )
    return findings


_LESSON_COMMENT_RX = re.compile(r"//[^\n]*?lesson\s+(\d{2,4})", re.IGNORECASE)
_KB_ROOT_MARKERS = (
    "odin-knowledge-base/courses/programvideogames",
    "odin-knowledge-base/docs/karl_zylinski",
    "odin-knowledge-base/docs/official",
)


def detect_lesson_ref_validation(
    original: str,
    file_path: Path,
    rule: dict[str, Any],
    *,
    kb_root: Path | None = None,
) -> list[Finding]:
    """Find ``// lesson NNN`` comments that resolve to NO file in the KB.

    Unlike other heuristics, this one runs against the ORIGINAL file content,
    not the comment-stripped content: lesson references live in line comments
    that the strpper erases. We still iterate line-by-line, so line numbers in
    the findings match the input file.
    """
    findings: list[Finding] = []
    raw_lines = original.splitlines()
    for idx, line in enumerate(raw_lines, start=1):
        m = _LESSON_COMMENT_RX.search(line)
        if not m:
            continue
        lesson_id = m.group(1)
        if not _lesson_exists(lesson_id, file_path, kb_root=kb_root):
            findings.append(
                Finding(
                    rule_id=str(rule["id"]),
                    title=str(rule.get("title", "")),
                    severity=str(rule.get("severity", "info")),
                    category=str(rule.get("category", "")),
                    file=file_path,
                    line=idx,
                    snippet=line.strip(),
                    explanation=str(rule.get("explanation", "")),
                    kb_sources=list(rule.get("kb_sources") or []),
                    lesson_refs=list(rule.get("lesson_refs") or []),
                    fix_suggestion=(
                        "Verify the lesson number exists in "
                        "odin-knowledge-base/courses/programvideogames/... "
                        f"or update AGENTS.md (lesson {lesson_id} not found)."
                    ),
                )
            )
    return findings


def _lesson_exists(lesson_id: str, file_path: Path, *, kb_root: Path | None) -> bool:
    """Heuristically check whether ``lesson_id`` matches a known KB file."""
    if kb_root is None:
        return True
    kb_root = kb_root.resolve()
    candidates = [
        kb_root / "courses" / "programvideogames" / lesson_id,
        kb_root / "docs" / "karl_zylinski" / "odin-book" / lesson_id,
    ]
    for cand in candidates:
        if cand.exists():
            return True
    normalised = str(kb_root).replace("\\", "/")
    for parent in kb_root.rglob(f"*{lesson_id}*"):
        parent_norm = str(parent).replace("\\", "/")
        if any(marker in parent_norm for marker in _KB_ROOT_MARKERS):
            return True
    return False


_HEURISTICS: dict[str, Callable[..., list[Finding]]] = {
    "alloc-in-loop": detect_alloc_in_loop,
    "defer-in-loop": detect_defer_in_loop,
    "small-map": detect_small_map,
    "large-struct-mixed-access": detect_large_struct_mixed_access,
    "unfreed-slice": detect_unfreed_slice,
    "lesson-ref-validation": detect_lesson_ref_validation,
}


def apply_heuristic(
    name: str,
    content: str,
    file_path: Path,
    rule: dict[str, Any],
    *,
    kb_root: Path | None = None,
) -> list[Finding]:
    """Dispatch one named heuristic. Unknown names return an empty list."""
    fn = _HEURISTICS.get(name)
    if fn is None:
        return []
    if name == "lesson-ref-validation":
        return fn(content, file_path, rule, kb_root=kb_root)
    return fn(content, file_path, rule)


def scan_file(
    path: Path | str,
    rules: list[dict[str, Any]],
    *,
    kb_root: Path | None = None,
    build_mode: str = "Debug",
) -> list[Finding]:
    """Run all applicable rules from ``rules`` against one file.

    ``build_mode`` controls the ``applies_when.build_mode`` filter. Rules
    declaring ``applies_when: { build_mode: 'release' }`` are skipped when
    this value is ``'Debug'`` (and vice versa).
    """
    file_path = Path(path)
    if not file_path.is_file():
        return []

    raw = file_path.read_text(encoding="utf-8", errors="replace")
    stripped = _strip_odin_comments(raw)
    findings: list[Finding] = []

    for rule in rules:
        if not rule.get("static", False):
            continue
        if not _matches_scope(rule, file_path):
            continue
        if not _applies_when(rule, build_mode):
            continue
        if "pattern" in rule and rule.get("pattern"):
            findings.extend(_apply_l1_regex(rule, stripped, file_path))
        elif rule.get("detect"):
            detect_name = str(rule["detect"])
            if detect_name == "lesson-ref-validation":
                findings.extend(
                    apply_heuristic(
                        detect_name, raw, file_path, rule, kb_root=kb_root
                    )
                )
            else:
                findings.extend(
                    apply_heuristic(
                        detect_name, stripped, file_path, rule, kb_root=kb_root
                    )
                )

    return findings


__all__ = [
    "Finding",
    "scan_file",
    "apply_heuristic",
    "_strip_odin_comments",
    "detect_alloc_in_loop",
    "detect_defer_in_loop",
    "detect_small_map",
    "detect_large_struct_mixed_access",
    "detect_unfreed_slice",
    "detect_lesson_ref_validation",
]
