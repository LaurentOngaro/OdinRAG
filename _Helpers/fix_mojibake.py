"""
_Helpers/fix_mojibake.py - Fix 'UTF-8 read as Latin-1' mojibake

Walks ``odin-knowledge-base/`` and applies ``repair_mojibake()`` (shared
lib ``_Helpers/lib/text_clean``) on every text file (Markdown).

Symptoms fixed:
- Broken Unicode ASCII-art: â”œ â”€ â”‚ â”” â”Œ â”˜ â”¤ â”¬ â”´ â”¼
- Curly typography    : â€™ â€œ â€¦ â€“ â€” â‚¬
- Arrows              : â†’ â† â†‘ â†“ â†” â‡’ â‡
- French accents      : Ã© Ã¨ Ã Ãª Ã« Ã® Ã¯ Ã´ Ã¹ Ã» Ã§
- Double-encoded NBSP : Â (followed by a Latin-1 character)

Usage:
- python _Helpers/fix_mojibake.py            # dry-run
- python _Helpers/fix_mojibake.py --apply    # write the fixes
- python _Helpers/fix_mojibake.py --path X   # alternate root
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Force stdout UTF-8 (otherwise cp1252 chokes on box-drawing characters).
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

# Allow importing ``_Helpers/lib`` from the archive.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.text_clean import repair_mojibake  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_ROOT = ROOT_DIR / "odin-knowledge-base"
_DESCRIPTION = "Fix 'UTF-8 read as Latin-1' mojibake (one-shot archive)."

# Extensions considered text.
TEXT_EXTENSIONS: tuple[str, ...] = (".md", ".markdown", ".txt", ".rst")


def iter_text_files(root: Path):
    """Yield text files under ``root`` (recursive)."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            yield path


def scan_and_fix(root: Path, apply: bool) -> tuple[int, int, int]:
    """Walk ``root`` and repair mojibake.

    Returns (scanned, fixed, unchanged).
    """
    scanned = fixed = unchanged = 0
    for path in iter_text_files(root):
        scanned += 1
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"  [SKIP] {path.relative_to(root)}  (not valid UTF-8)")
            continue

        repaired = repair_mojibake(original)
        if repaired == original:
            unchanged += 1
            continue

        rel = path.relative_to(root)
        diff_chars = sum(1 for a, b in zip(original, repaired) if a != b)
        diff_chars += abs(len(repaired) - len(original))
        print(f"  [FIX] {rel}  ({diff_chars} char(s) modified)")
        fixed += 1

        if apply:
            path.write_text(repaired, encoding="utf-8")

    return scanned, fixed, unchanged


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--path", type=Path, default=DEFAULT_ROOT,
        help=f"Root to scan (default: {DEFAULT_ROOT.relative_to(ROOT_DIR)})",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Apply the fixes (without this flag: dry-run)",
    )
    args = parser.parse_args(argv)

    root: Path = args.path
    if not root.exists():
        print(f"[ERR] Root not found: {root}")
        return 2

    print(f"Scan : {root}")
    print(f"Mode : {'APPLY (writes to disk)' if args.apply else 'DRY-RUN (no writes)'}")
    print()

    scanned, fixed, unchanged = scan_and_fix(root, apply=args.apply)

    print()
    print("─" * 60)
    print(f"Scanned   : {scanned}")
    print(f"Modified  : {fixed}")
    print(f"Unchanged : {unchanged}")
    if not args.apply and fixed:
        print()
        print("Re-run with --apply to write the fixes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
