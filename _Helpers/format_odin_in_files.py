#!/usr/bin/env python3
"""
_Helpers/format_odin_in_files.py - Format .odin files and ```odin ... ``` blocks in Markdown files within a given folder.

Wraps `odinfmt` (https://github.com/DanielGavin/ols), the official Odin language formatter (reads stdin, writes stdout).

Usage:
    - python _Helpers/format_odin_in_files.py --path DIR          # recursive
    - python _Helpers/format_odin_in_files.py --path DIR --check  # dry-run
    - python _Helpers/format_odin_in_files.py --file FILE         # single file

Modes:
    - `.odin` file    -> piped through odinfmt, rewritten in place.
    - `.md` file      -> extracts the ```odin ... ``` blocks, formats each, re-assembles.
    - Folder (`--path`) -> recursive, applies to all `*.odin`/`*.md`.

Exit codes:
    - 0   success
    - 1   odinfmt not found
    - 2   invalid argument
    - 3   I/O error
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

# Allow importing the `_Helpers/` package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from odin_format import (  # noqa: E402
    MAX_FILE_BYTES,
    ODINFMT_EXE,
    ODINFMT_CONFIG,
    format_markdown_file,
    format_markdown_odin_blocks,
    odinfmt_available,
    odinfmt_format,
)


# ─── FILE PROCESSORS ─────────────────────────────────────────────────────────
def _process_odin(path: Path, *, check: bool, verbose: bool) -> bool:
    try:
        original = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  [ERR] {path}: {exc}")
        return False
    formatted = odinfmt_format(original)
    if formatted is None:
        return False
    if formatted == original:
        if verbose:
            print(f"  [=] {path}  (already clean)")
        return False
    print(f"  [~] {path}  ({len(original)} -> {len(formatted)} chars)")
    if not check:
        path.write_text(formatted, encoding="utf-8")
    return True


def _process_md(path: Path, *, check: bool, verbose: bool) -> bool:
    try:
        size = path.stat().st_size
    except OSError as exc:
        print(f"  [ERR] {path}: {exc}")
        return False
    if size > MAX_FILE_BYTES:
        print(f"  [SKIP] {path}  ({size // (1024*1024)} MB > safeguard)")
        return False
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"  [SKIP] {path}  (not valid UTF-8)")
        return False
    except OSError as exc:
        print(f"  [ERR] {path}: {exc}")
        return False

    if check:
        new_text, total, changed = format_markdown_odin_blocks(original)
        if total == 0:
            if verbose:
                print(f"  [=] {path}  (no odin block)")
            return False
        if verbose:
            print(f"  [i] {path}  {changed}/{total} odin block(s)")
        if changed == 0:
            return False
        print(f"  [~] {path}  ({changed}/{total} odin block(s))")
        return True

    changed_flag, total, changed = format_markdown_file(path)
    if total == 0:
        if verbose:
            print(f"  [=] {path}  (no odin block)")
        return False
    if verbose:
        print(f"  [i] {path}  {changed}/{total} odin block(s)")
    if changed == 0:
        return False
    print(f"  [~] {path}  ({changed}/{total} odin block(s))")
    return changed_flag


def process_file(path: Path, *, check: bool, verbose: bool) -> bool:
    """Dispatch by extension. Returns True if modified."""
    ext = path.suffix.lower()
    if ext == ".odin":
        return _process_odin(path, check=check, verbose=verbose)
    if ext == ".md":
        return _process_md(path, check=check, verbose=verbose)
    print(f"  [SKIP] {path}  (unsupported extension {ext!r})")
    return False


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def iter_files(root: Path):
    """Yield every `.odin` and `.md` file under `root` (recursive)."""
    for ext in (".odin", ".md"):
        yield from sorted(root.rglob(f"*{ext}"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[1] if __doc__ else "",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", "-p", type=Path, help="Folder to scan recursively.")
    group.add_argument("--file", "-f", type=Path, help="Single file to format (.odin or .md).")
    parser.add_argument("--check", action="store_true", help="Dry-run: change nothing, only display.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Also display files already clean / without odin block.")
    args = parser.parse_args(argv)

    if not odinfmt_available():
        print(f"[ERR] odinfmt not found ({ODINFMT_EXE}) or missing config ({ODINFMT_CONFIG})", file=sys.stderr)
        return 1

    target: Path = args.path or args.file
    if not target.exists():
        print(f"[ERR] Target not found: {target}", file=sys.stderr)
        return 2

    print(f"odinfmt : {ODINFMT_EXE}")
    print(f"Mode    : {'CHECK (no writes)' if args.check else 'WRITE'}")
    print(f"Target  : {target}")
    print()

    files = [target] if target.is_file() else list(iter_files(target))
    if not files:
        print(f"[i] No .odin or .md file found under {target}")
        return 0

    scanned = modified = errors = 0
    for f in files:
        scanned += 1
        try:
            if process_file(f, check=args.check, verbose=args.verbose):
                modified += 1
        except Exception as exc:   # noqa: BLE001 - isolate any crash per file
            errors += 1
            print(f"  [ERR] {f}: {exc}", file=sys.stderr)

    print()
    print("─" * 60)
    print(f"Scanned   : {scanned}")
    print(f"Modified  : {modified}")
    print(f"Errors    : {errors}")
    if args.check and modified:
        print()
        print("Re-run without --check to apply the fixes.")
    return 0 if errors == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
