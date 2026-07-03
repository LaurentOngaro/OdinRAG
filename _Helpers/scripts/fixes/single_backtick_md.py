#!/usr/bin/env python3
"""_Helpers/scripts/fixes/single_backtick_md.py - Replace ``X`` with `X` in Python files.

Removes the RST/Sphinx-style double-backtick markup from ``.py`` files (docstrings and comments) where it serves no purpose and triggers pyright warnings/errors like::
Expressions surrounded by backticks are not supported in Python 3.x; use repr instead "ake" is not defined

The transformation is **strict** to avoid clobbering legitimate use cases:

- `` ``foo`` `` (2 backticks around ``foo``) -> `` `foo` `` (1 backtick around)
- `` ```odin ... ``` `` (3 backticks, used to reference a Markdown code fence inside a docstring) -> **preserved**
- `` ``foo```bar`` `` (mixing double + triple) -> **preserved** (no double pair isolated)

Usage::

    python _Helpers/scripts/fixes/single_backtick_md.py --check
    python _Helpers/scripts/fixes/single_backtick_md.py --apply
    python _Helpers/scripts/fixes/single_backtick_md.py path/to/file.py

Default mode is ``--check`` (dry-run). ``--apply`` writes the changes.
Idempotent: re-running after a successful ``--apply`` produces zero changes.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# (?<!`)  negative lookbehind: previous char is NOT a backtick
# \`\`     exactly two backticks (no more, no less)
# ([^`]+) capture: one or more non-backtick chars
# \`\`     exactly two backticks
# (?!`)   negative lookahead: next char is NOT a backtick
STRICT_DOUBLE_BACKTICK = re.compile(r"(?<!`)\`\`([^`]+)\`\`(?!`)")


def process_text(text: str) -> tuple[str, int]:
    """Apply the strict replacement. Returns ``(new_text, replacement_count)``."""
    new_text, count = STRICT_DOUBLE_BACKTICK.subn(r"`\1`", text)
    return new_text, count


def _cprint(msg: str, color: str = "", bold: bool = False, file: Any = None) -> None:
    """Tiny color printer (no colorama import to keep this stdlib-only)."""
    colors = {
        "RED": "\x1b[31m",
        "GREEN": "\x1b[32m",
        "YELLOW": "\x1b[33m",
        "CYAN": "\x1b[36m",
        "BOLD": "\x1b[1m",
        "RESET": "\x1b[0m",
    }
    prefix = colors.get("BOLD", "") if bold else ""
    color_code = colors.get(color, "") if color else ""
    reset = colors.get("RESET", "")
    print(f"{prefix}{color_code}{msg}{reset}", file=file)


def _print_change(rel: str, count: int) -> None:
    _cprint(f"  {rel}: {count} replacement(s)", "CYAN")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="single_backtick_md.py",
        description="Replace RST-style ``X`` markup with `X` in Python source files.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Python files to process (default: every .py under _Helpers/scripts/).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: report changes that WOULD be made. Always exits 0.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Apply the changes to disk.",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress per-file output (only print totals).",
    )
    args = parser.parse_args(argv)

    if not args.check and not args.apply:
        args.check = True  # safe default per project convention (--apply requires explicit GO)

    if args.files:
        targets = [Path(f) for f in args.files]
    else:
        targets = sorted(Path("_Helpers/scripts").rglob("*.py"))

    # Skip this script itself: its docstring legitimately uses `` `` `` as
    # examples of the pattern being converted. Mutating those would
    # destroy the documentation. Use --apply with explicit file paths to
    # override (intentionally not supported to keep the script safe by default).
    self_path = Path(__file__).resolve()
    targets = [p for p in targets if p.resolve() != self_path]

    files_changed = 0
    total_replacements = 0
    for path in targets:
        if not path.is_file() or path.suffix != ".py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            _cprint(f"  [ERR] {path}: cannot read ({exc})", "RED")
            continue
        new_text, count = process_text(text)
        if count <= 0:
            continue
        files_changed += 1
        total_replacements += count
        try:
            rel = str(path.resolve().relative_to(Path.cwd()))
        except ValueError:
            rel = str(path)
        if not args.quiet:
            _print_change(rel, count)
        if args.apply:
            try:
                path.write_text(new_text, encoding="utf-8")
            except OSError as exc:
                _cprint(f"  [ERR] {path}: cannot write ({exc})", "RED")
                return 2

    _cprint("", "RESET")
    if args.apply:
        _cprint(
            f"[done] {total_replacements} replacement(s) applied across {files_changed} file(s)",
            "GREEN",
            bold=True,
        )
    else:
        _cprint(
            f"[check] {total_replacements} replacement(s) would be made in {files_changed} file(s) "
            "(dry-run; pass --apply to write)",
            "YELLOW",
            bold=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# Public alias for the color-print helper (matches other scripts in the repo).
cprint = _cprint
__all__ = ["STRICT_DOUBLE_BACKTICK", "process_text", "main", "cprint"]
