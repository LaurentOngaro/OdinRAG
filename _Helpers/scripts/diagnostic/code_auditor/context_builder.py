"""KB context builder for the `code_auditor` Phase 3 report.

Given a `Finding`, this module produces a short Markdown block (3-5 lines per KB source) that the reporter inserts under the finding, between `Snippet` and `Sources KB`.
The block quotes the most relevant section of each cited KB file, so a human reading the report can see *why* the rule applies without opening the source themselves.

Heuristics (in priority order):

1. **Lesson-anchored match** - if `finding.lesson_refs` resolves to a known KB file via `KBIndex.lesson_to_file`, jump to the line range that mentions the lesson (or the first heading of the file).
2. **Keyword match** - scan each cited KB file for any of the rule's title words (length >= 4), rule ID (`ALLOC-002`), or category keywords, and quote the matching paragraph.
3. **Default heading** - fall back to the first heading of each cited file.

The output is plain ASCII Markdown: bullet list of `path -> excerpt`.
Excerpts are trimmed to `max_lines` (default 5) and at most `max_chars_per_line` chars wide.
The module is stdlib-only and never writes to disk.

Public surface:

- `ContextBuilder` - the builder.
- `ContextBuilder.extract(finding) -> str` - return the Markdown block (without trailing newline). Returns the empty string when no context can be built (caller decides whether to skip the section).
- `ContextBuilder.extract_for_paths(finding, paths) -> str` - same but with a caller-provided list of paths (used by tests and the reporter fallback).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

if TYPE_CHECKING:
    from kb_index import KBIndex
    from scanner import Finding


_DEFAULT_MAX_LINES = 5
_DEFAULT_MAX_CHARS = 160
_LESSON_LINE_RX = re.compile(
    r"\b(?:lesson|chapter|le[çc])[\s_-]*(\d{2,4})\b", re.IGNORECASE
)
_KEYWORD_MIN_LEN = 4
_COMMON_STOPWORDS = frozenset(
    {
        "this", "that", "with", "from", "have", "your", "they", "them",
        "into", "when", "where", "what", "which", "their", "should",
        "must", "only", "than", "more", "less", "very", "also", "such",
        "each", "other", "some", "most", "many", "much", "any",
    }
)


def _normalise_path(p: str) -> str:
    return p.strip().replace("\\", "/")


def _tokenise_title(title: str) -> list[str]:
    """Lowercased title words with stopwords + short tokens removed."""
    if not title:
        return []
    out: list[str] = []
    for raw in re.split(r"[^A-Za-z0-9_-]+", title):
        w = raw.strip().lower().strip("-_")
        if len(w) < _KEYWORD_MIN_LEN:
            continue
        if w in _COMMON_STOPWORDS:
            continue
        out.append(w)
    return out


def _resolve_kb_path(rel_path: str, kb_root: Path | None) -> Path | None:
    """Resolve a repo-relative KB path to an absolute file, when possible.

    Tries the literal path (cwd-rooted), then the KB-root-prefixed path. If `kb_root` is `None`, only the literal path is tried. Returns `None` if the file does not exist on disk.
    """
    norm = _normalise_path(rel_path)
    if not norm:
        return None
    candidates: list[Path] = []
    if kb_root is not None:
        candidates.append(kb_root.parent / norm)
    candidates.append(Path(norm))
    for cand in candidates:
        try:
            if cand.is_file():
                return cand.resolve()
        except OSError:
            continue
    return None


def _split_paragraphs(lines: list[str]) -> list[tuple[int, list[str]]]:
    """Group non-empty consecutive lines into paragraphs.

    Returns a list of `(start_line_no, lines)` where `start_line_no` is the 1-based line number of the first line of the paragraph. Markdown headings and code-fence boundaries each start a new paragraph.
    """
    paragraphs: list[tuple[int, list[str]]] = []
    current: list[str] = []
    current_start = 0
    in_code = False
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if current:
                paragraphs.append((current_start, current))
                current = []
                current_start = 0
            continue
        if in_code:
            continue
        if not stripped:
            if current:
                paragraphs.append((current_start, current))
                current = []
                current_start = 0
            continue
        if stripped.startswith(("#", ">", "-", "*")) and len(current) > 1:
            paragraphs.append((current_start, current))
            current = [line]
            current_start = idx
            continue
        if not current:
            current_start = idx
        current.append(line)
    if current:
        paragraphs.append((current_start, current))
    return paragraphs


def _pick_paragraph(
    paragraphs: list[tuple[int, list[str]]],
    keywords: Iterable[str],
) -> tuple[int, list[str]] | None:
    """Pick the paragraph with the highest keyword overlap.

    Returns the first paragraph when no keywords match. Returns `None` only if `paragraphs` is empty.
    """
    if not paragraphs:
        return None
    keywords_list = [k for k in keywords if k]
    if not keywords_list:
        return paragraphs[0]
    best: tuple[int, list[str]] | None = None
    best_score = -1
    for start, lines in paragraphs:
        joined = " ".join(lines).lower()
        score = sum(1 for k in keywords_list if k in joined)
        if score > best_score:
            best_score = score
            best = (start, lines)
    if best is not None and best_score > 0:
        return best
    return paragraphs[0]


def _trim_paragraph(
    paragraph: tuple[int, list[str]],
    max_lines: int,
    max_chars: int,
) -> str:
    """Format a paragraph as a Markdown blockquote, trimmed to fit."""
    start, lines = paragraph
    kept = lines[:max_lines]
    out: list[str] = []
    for line in kept:
        clean = line.rstrip()
        if len(clean) > max_chars:
            clean = clean[: max_chars - 3] + "..."
        out.append(f"  > {clean}")
    if len(lines) > max_lines:
        out.append(f"  > ... ({len(lines) - max_lines} more lines)")
    _ = start
    return "\n".join(out)


def _read_lines(path: Path) -> list[str]:
    """Read `path` and return its lines; empty list on failure."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return text.splitlines()


def _excerpt_for_path(
    rel_path: str,
    finding: "Finding",
    kb_root: Path | None,
    max_lines: int,
    max_chars: int,
) -> str | None:
    """Build the per-path excerpt block, or `None` when nothing usable."""
    abs_path = _resolve_kb_path(rel_path, kb_root)
    if abs_path is None:
        return None
    lines = _read_lines(abs_path)
    if not lines:
        return None
    paragraphs = _split_paragraphs(lines)
    if not paragraphs:
        return None

    lesson_refs = getattr(finding, "lesson_refs", None) or []
    keywords: list[str] = []
    if lesson_refs:
        for ref in lesson_refs:
            keywords.extend([f"lesson {ref}", f"chapter {ref}"])
    title_tokens = _tokenise_title(getattr(finding, "title", "") or "")
    keywords.extend(title_tokens)
    rule_id = getattr(finding, "rule_id", "")
    if rule_id:
        keywords.append(rule_id.lower())

    chosen = _pick_paragraph(paragraphs, keywords)
    if chosen is None:
        return None
    return _trim_paragraph(chosen, max_lines, max_chars)


class ContextBuilder:
    """Builds KB-context blocks for `code_auditor` findings.

    Stateless after construction: hold one instance per CLI run and call `extract()` for every finding.
    """

    def __init__(
        self,
        kb_index: "KBIndex | None" = None,
        *,
        max_lines: int = _DEFAULT_MAX_LINES,
        max_chars_per_line: int = _DEFAULT_MAX_CHARS,
    ):
        self._index = kb_index
        self._max_lines = max(1, int(max_lines))
        self._max_chars = max(40, int(max_chars_per_line))

    @property
    def max_lines(self) -> int:
        return self._max_lines

    @property
    def max_chars_per_line(self) -> int:
        return self._max_chars

    def kb_root(self) -> Path | None:
        """Return the KB root the builder resolves paths against."""
        if self._index is None:
            return None
        return self._index.kb_root

    def extract(self, finding: "Finding") -> str:
        """Return the Markdown block for `finding`. Empty string when nothing fits."""
        if self._index is None:
            return ""
        paths = self._index.files_for_finding(finding)
        return self.extract_for_paths(finding, paths)

    def extract_for_paths(
        self,
        finding: "Finding",
        paths: Iterable[str],
    ) -> str:
        """Same as `extract` but the caller picks the paths."""
        kb_root = self.kb_root()
        max_lines = self._max_lines
        max_chars = self._max_chars
        blocks: list[str] = []
        seen_paths: set[str] = set()
        for raw_path in paths:
            norm = _normalise_path(str(raw_path))
            if not norm or norm in seen_paths:
                continue
            seen_paths.add(norm)
            excerpt = _excerpt_for_path(norm, finding, kb_root, max_lines, max_chars)
            if excerpt is None:
                continue
            blocks.append(f"- `{norm}` :\n\n{excerpt}")
        return "\n\n".join(blocks)


__all__ = ["ContextBuilder"]
