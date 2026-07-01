"""
_Helpers/reflow_md.py - Reflow Markdown into the "book style" the repo uses.

Walks a directory tree and rewrites every ``.md`` file so that prose paragraphs become a single physical line (one paragraph = one line). This matches the convention documented in the root ``AGENTS.md`` and enforced by ``MD013: false`` in ``.markdownlint.json``: do not auto-wrap prose, tables, or URLs at any character limit.

Idempotent: re-running on an already-reflowed file is a no-op (the file is not rewritten unless at least one paragraph would change).

Blocks preserved verbatim (never joined across them):

- YAML frontmatter (between leading ``---`` markers)
- Fenced code blocks (```` ``` ```` and `~~~`)
- Tables (lines starting with ``|``)
- ATX headings (lines starting with ``#``)
- Blockquotes (lines starting with ``>``)
- Lists (lines starting with ``-``, ``*``, ``+``, or ``N.``/``N)``)
- Setext heading underlines (a line of ``===`` or ``---`` immediately after a non-special line is treated as the underline of that heading and kept on its own line)
- Thematic breaks (a line of ``---`` / ``***`` / ``___`` after a blank line)
- Reference link definitions (``[label]: url``)
- Indented continuation lines (a line starting with 2+ spaces or a tab is treated as a continuation of the previous block)

Usage:
    python _Helpers/reflow_md.py            # dry-run
    python _Helpers/reflow_md.py --apply    # rewrite the files
    python _Helpers/reflow_md.py --path X   # alternate root
    python _Helpers/reflow_md.py --check    # exit non-zero if any file would change

Exit codes:
    - 0: nothing to do (dry-run / apply successful / --check clean)
    - 1: --check found at least one file that would change
    - 2: invalid arguments (root not found, etc.)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_ROOT = ROOT_DIR
_DESCRIPTION = "Reflow Markdown prose into one-paragraph-per-line 'book style'."

TEXT_EXTENSIONS: tuple[str, ...] = (".md", ".markdown")

# Directories to skip entirely. These either contain third-party content (node_modules) or transient / cache material that should not be touched.
SKIP_DIRS: tuple[str, ...] = (
    "node_modules",
    ".git",
    ".kilo/cache",
    ".kilo/sessions",
    ".kilo/worktrees",
    "build",
    "_logs",
    "_raw",
    "_archives",
    "_refs",
    "_tools",
    "_private",
)

# Fence delimiters we recognize. A code fence is opened by a line that starts with ``` ``` ``` or `~~~` (optionally followed by an info string) and is closed by the next line that uses the same delimiter with at least as many characters.
FENCE_CHARS = ("```", "~~~")


def _is_fence_open(line: str) -> str | None:
    """Return the fence delimiter (`` ``` `` or `~~~`) if ``line`` opens one."""
    stripped = line.lstrip()
    for delim in FENCE_CHARS:
        if stripped.startswith(delim):
            return delim
    return None


def _is_fence_close(line: str, delim: str) -> bool:
    stripped = line.lstrip()
    if not stripped.startswith(delim):
        return False
    # The closing fence must use only the delimiter + optional spaces (no info string), and must have at least as many chars as the opener.
    # We accept any length >= 3 here since the opener is at least 3 chars by definition.
    rest = stripped[len(delim):]
    return rest.strip() == ""


def _is_continuation(line: str) -> bool:
    """A line that should be glued to the previous block, not start a new one.

    Indented continuation lines (2+ spaces or a tab) belong to the previous list / blockquote / paragraph, so we never break the block at them.
    """
    if not line:
        return False
    if line.startswith(("  ", "\t")):
        return True
    return False


def _looks_like_setext_underline(line: str) -> bool:
    """A line that is only ``=`` or ``-`` (with at least one char)."""
    s = line.rstrip()
    if not s:
        return False
    return all(c == "=" for c in s) or all(c == "-" for c in s)


def _looks_like_thematic_break(line: str) -> bool:
    """A line of repeated ``-`` / ``*`` / ``_`` (Markdown spec)."""
    s = line.strip()
    if len(s) < 3:
        return False
    return all(c == "-" for c in s) or all(c == "*" for c in s) or all(c == "_" for c in s)


def _is_block_start(line: str) -> bool:
    """A line that starts a new block (must NOT be joined to the previous one). Conservative: anything that looks structural gets its own line.
    """
    if not line:
        return False
    s = line.lstrip()
    if not s:
        return False
    if s.startswith("#"):                          # ATX heading
        return True
    if s.startswith(">"):                          # blockquote
        return True
    if s.startswith("|"):                          # table
        return True
    if s.startswith(("-", "*", "+")):              # list item or thematic break
        return True
    # Ordered list: "1." "2)" etc.
    i = 0
    while i < len(s) and s[i].isdigit():
        i += 1
    if i > 0 and i < len(s) and s[i] in (".", ")") and (i + 1 >= len(s) or s[i + 1] == " "):
        return True
    # Reference link definition
    if s.startswith("["):
        return True
    return False


def _reflow(text: str) -> str:
    """Return ``text`` with paragraphs collapsed to a single line each."""
    lines = text.splitlines()
    out: list[str] = []
    in_frontmatter = False
    frontmatter_seen_open = False
    in_code = False
    fence_delim = ""

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        # --- Frontmatter handling (only at top of file) ---------------------
        if not in_code and not in_frontmatter and not frontmatter_seen_open and i == 0 and line.strip() == "---":
            in_frontmatter = True
            frontmatter_seen_open = True
            out.append(line)
            i += 1
            continue
        if in_frontmatter:
            out.append(line)
            if line.strip() == "---" and out[-2].strip() != "---":
                # Closing fence of the frontmatter.
                in_frontmatter = False
            i += 1
            continue

        # --- Code fence handling -------------------------------------------
        if not in_code:
            opener = _is_fence_open(line)
            if opener is not None:
                in_code = True
                fence_delim = opener
                out.append(line)
                i += 1
                continue
        else:
            out.append(line)
            if _is_fence_close(line, fence_delim):
                in_code = False
                fence_delim = ""
            i += 1
            continue

        # --- Blank line ----------------------------------------------------
        if not line.strip():
            out.append("")
            i += 1
            continue

        # --- Setext heading: previous emitted line is the title, this is
        #     the underline (=== or ---) ------------------------------------
        if _looks_like_setext_underline(line) and out and out[-1].strip() and not _is_block_start(out[-1]):
            # Treat the underline as its own line.
            out.append(line)
            i += 1
            continue

        # --- Thematic break ------------------------------------------------
        if _looks_like_thematic_break(line):
            out.append(line)
            i += 1
            continue

        # --- Continuation line (indented): glue to previous block ---------
        if _is_continuation(line) and out and out[-1].strip():
            out[-1] = out[-1].rstrip() + " " + line.strip()
            i += 1
            continue

        # --- New block start: emit as own line ----------------------------
        if _is_block_start(line):
            out.append(line)
            i += 1
            continue

        # --- Otherwise: it's a prose line --------------------------------
        if out and out[-1].strip() and not _is_block_start(out[-1]) and not _is_continuation(out[-1]):
            # Join to the previous prose line.
            out[-1] = out[-1].rstrip() + " " + line.strip()
        else:
            out.append(line.strip())
        i += 1

    # Collapse runs of 3+ blank lines to a single blank line (paragraph separator), but never strip a trailing newline (preserves POSIX file convention).
    cleaned: list[str] = []
    blank_run = 0
    for ln in out:
        if not ln.strip():
            blank_run += 1
            if blank_run <= 1:
                cleaned.append("")
        else:
            blank_run = 0
            cleaned.append(ln)
    result = "\n".join(cleaned)
    if text.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def iter_text_files(root: Path):
    """Yield ``.md`` / ``.markdown`` files under ``root`` (recursive).

    If ``root`` is a single file, yield it directly (if it has the right extension).
    """
    if root.is_file():
        if root.suffix.lower() in TEXT_EXTENSIONS:
            yield root
        return
    for path in sorted(root.rglob("*")):
        # Skip excluded directories (and everything inside).
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def scan_and_reflow(root: Path, apply: bool) -> tuple[int, int, int]:
    """Walk ``root`` and reflow every Markdown file.

    Returns (scanned, reflowed, unchanged).
    """
    scanned = reflowed = unchanged = 0
    for path in iter_text_files(root):
        scanned += 1
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            rel = path if root.is_file() else path.relative_to(root)
            print(f"  [SKIP] {rel}  (not valid UTF-8)")
            continue

        reflowed_text = _reflow(original)
        if reflowed_text == original:
            unchanged += 1
            continue

        # Count lines saved as a quick visibility metric.
        orig_lines = original.count("\n")
        new_lines = reflowed_text.count("\n")
        saved = orig_lines - new_lines
        rel = path if root.is_file() else path.relative_to(root)
        print(f"  [REFLOW] {rel}  (-{saved} line(s))")
        reflowed += 1

        if apply:
            path.write_text(reflowed_text, encoding="utf-8")

    return scanned, reflowed, unchanged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument( "--path", type=Path, default=DEFAULT_ROOT, help=f"Root to scan (default: repo root = {DEFAULT_ROOT.relative_to(ROOT_DIR)}). Accepts a single file or a directory.", )
    parser.add_argument( "--apply", action="store_true", help="Apply the reflow (without this flag: dry-run)", )
    parser.add_argument( "--check", action="store_true", help="Exit non-zero if any file would change (for CI / pre-commit)", )
    args = parser.parse_args(argv)

    root: Path = args.path
    if not root.exists():
        print(f"[ERR] Root not found: {root}")
        return 2

    apply = args.apply and not args.check
    print(f"Scan  : {root}")
    print(f"Mode  : {'APPLY (writes to disk)' if apply else 'CHECK (would change)' if args.check else 'DRY-RUN (no writes)'}")
    print()

    scanned, reflowed, unchanged = scan_and_reflow(root, apply=apply)

    print()
    print("-" * 60)
    print(f"Scanned   : {scanned}")
    print(f"Reflowed  : {reflowed}")
    print(f"Unchanged : {unchanged}")

    if args.check and reflowed:
        print()
        print("Reflow needed. Re-run with --apply to fix, or run without --check to preview.")
        return 1
    if not args.apply and reflowed and not args.check:
        print()
        print("Re-run with --apply to write the fixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
