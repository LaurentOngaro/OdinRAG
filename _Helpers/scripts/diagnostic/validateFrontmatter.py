#!/usr/bin/env python3
"""_Helpers/scripts/diagnostic/validateFrontmatter.py - YAML frontmatter validator for OdinRAG.

Adapted from TerraBloom's `validateFrontmatter.py` (H:/Sync/PKM_PROJECTS/TerraBloom/_Helpers/01_Diagnostic/validateFrontmatter.py) for the OdinRAG 8-field schema documented in `_Helpers/docs/003_yaml_frontmatter_conventions.md`.

What it does:

- Walks the repo (default) or specific files/paths (via ``--files``).
- For each file: extracts YAML frontmatter, validates against the schema, and optionally runs content-quality checks (long-dash auto-replacement, CJK warning).
- Auto-fixes long dashes (``-``, ``-``, ``-``) to ASCII ``-`` in the file body.
- Reports errors / warnings / info by category with colored output.
- Honors ``vaultConfigOdinRAG.should_validate`` for skip rules.

Usage:

    python _Helpers/scripts/diagnostic/validateFrontmatter.py                          # whole repo
    python _Helpers/scripts/diagnostic/validateFrontmatter.py --files path/to/file.md
    python _Helpers/scripts/diagnostic/validateFrontmatter.py --fail-on-error           # exit non-zero on errors
    python _Helpers/scripts/diagnostic/validateFrontmatter.py --no-content-check        # skip long-dash auto-fix

Exit codes:

    0 - no frontmatter errors
    1 - frontmatter errors found (only counted, not the auto-fix warnings)
    2 - tool-level error (missing config, bad args, ...)

Cross-platform (Windows / Unix). Depends on PyYAML (for safe_load).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

_DIAGNOSTIC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DIAGNOSTIC_DIR))

from vaultConfigOdinRAG import (  # noqa: E402
    ALLOWED_TYPES,
    COLORS,
    IGNORE_DIRS,
    IGNORE_FILES,
    LONG_DASH_PATTERN,
    LONG_DASH_REPLACEMENT,
    REQUIRED_FIELDS,
    cprint,
    extract_frontmatter,
    path_link,
    should_ignore_dir,
    should_ignore_file,
    should_validate,
    validate_frontmatter,
)

# Sanity: this script must not contain literal long-dash characters either,
# for the same reason documented in ``vaultConfigOdinRAG.LONG_DASH_PATTERN``.
# A global search-and-replace of U+2014 / U+2013 / U+2015 across the repo
# would otherwise turn the literal help text into broken replacement code.
for _literal in ("\u2013", "\u2014", "\u2015"):
    assert _literal not in __file__, (
        "validateFrontmatter.py must not contain a literal long-dash byte; "
        "use named Unicode escapes or LONG_DASH_REPLACEMENT instead."
    )
    del _literal


def check_content(text: str, do_content_check: bool) -> tuple[list[str], list[str], str]:
    """Run content quality checks. Returns (warnings, info, new_text).

    Auto-replaces ``-``, ``-``, ``-`` with ASCII ``-`` when ``do_content_check`` is True. Warns about CJK characters (informational only).
    """
    warnings: list[str] = []
    info: list[str] = []
    new_text = text

    if not do_content_check:
        return warnings, info, new_text

    long_dash_matches = LONG_DASH_PATTERN.findall(text)
    if long_dash_matches:
        new_text = LONG_DASH_PATTERN.sub(LONG_DASH_REPLACEMENT, text)
        info.append(
            f"Auto-replaced {len(long_dash_matches)} long dash(es) with ASCII '-' "
            f"(en-dash / em-dash / horizontal bar)"
        )

    from vaultConfigOdinRAG import CJK_PATTERN

    cjk_hits = list(CJK_PATTERN.finditer(new_text))
    if cjk_hits:
        bad_lines = sorted({
            new_text[:m.start()].count("\n") + 1 for m in cjk_hits
        })
        preview = ", ".join(f"L{n}" for n in bad_lines[:5])
        if len(bad_lines) > 5:
            preview += f", ... (+{len(bad_lines) - 5} more)"
        warnings.append(
            f"Found {len(cjk_hits)} CJK character(s) on {len(bad_lines)} line(s): {preview}"
        )

    return warnings, info, new_text


def _detect_line_ending(raw_bytes: bytes) -> str:
    """Return the dominant line ending found in ``raw_bytes`` ('\r\n' or '\n')."""
    crlf = raw_bytes.count(b"\r\n")
    lf_only = raw_bytes.count(b"\n") - crlf
    return "\r\n" if crlf > lf_only else "\n"


def check_file(path: Path, do_content_check: bool = True) -> tuple[list[str], list[str], list[str]]:
    """Validate one file. Returns (errors, warnings, info).

    Reads the file in binary mode to preserve the original line endings; only writes back when ``do_content_check`` produces a different body. The auto-fix path must NOT silently flip CRLF -> LF or vice versa (this was a real bug on 2026-07-03).
    """
    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        return [f"Cannot read file: {exc}"], [], []

    try:
        text = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"Cannot decode file as UTF-8: {exc}"], [], []

    (fm, _body_start) = extract_frontmatter(text)
    errors: list[str] = validate_frontmatter(fm)

    warnings: list[str] = []
    info: list[str] = []

    if do_content_check:
        content_warnings, content_info, fixed_text = check_content(text, do_content_check)
        warnings.extend(content_warnings)
        info.extend(content_info)

        if fixed_text != text:
            line_ending = _detect_line_ending(raw_bytes)
            normalized = fixed_text.replace("\r\n", "\n").replace("\n", line_ending)
            new_bytes = normalized.encode("utf-8")
            if new_bytes != raw_bytes:
                try:
                    path.write_bytes(new_bytes)
                except OSError as exc:
                    warnings.append(f"Could not persist auto-fixed content to disk: {exc}")

    return errors, warnings, info


def find_targets(
    files_arg: list[str] | None,
    *,
    ignore_dirs: bool = False,
    ignore_files: bool = False,
) -> list[Path]:
    """Resolve CLI ``--files`` targets (mix of files / dirs / globs) into a sorted unique list.

    The two ignore flags mirror the CLI options. Both default to False (scan everything).
    Pass ``ignore_dirs=True`` to apply ``IGNORE_DIRS`` and/or ``ignore_files=True`` to apply ``IGNORE_FILES``.
    """
    def _is_filtered(p: Path) -> bool:
        if ignore_dirs and should_ignore_dir(p):
            return True
        if ignore_files and should_ignore_file(p):
            return True
        return False

    if not files_arg:
        targets: list[Path] = []
        for p in Path.cwd().rglob("*.md"):
            if _is_filtered(p):
                continue
            targets.append(p)
        return sorted(set(targets))

    out: list[Path] = []
    for raw in files_arg:
        p = Path(raw)
        if p.is_file():
            if not _is_filtered(p):
                out.append(p)
            continue
        if p.is_dir():
            out.extend(
                child for child in p.rglob("*.md")
                if child.is_file() and not _is_filtered(child)
            )
            continue
        for hit in Path.cwd().glob(raw):
            if hit.is_file() and not _is_filtered(hit):
                out.append(hit)
    return sorted(set(out))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validateFrontmatter.py",
        description="Validate YAML frontmatter against the OdinRAG 8-field schema.",
    )
    parser.add_argument(
        "-f",
        "--files",
        nargs="*",
        help="Files or directories to validate (default: whole repo, excluding IGNORE_DIRS).",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit non-zero (2) if any frontmatter error is found. Without this flag, exit 1 on errors.",
    )
    parser.add_argument(
        "--no-content-check",
        action="store_true",
        help="Skip content quality checks (long dash auto-fix and CJK warnings).",
    )
    parser.add_argument(
        "--ignore-dirs",
        action="store_true",
        default=True,
        help=(
            "Skip files in folders listed in vaultConfigOdinRAG.IGNORE_DIRS (.git, _Private, code/vendored templates, odin-knowledge-base/courses, ...). Default: True (skip ignored directories)."
        ),
    )
    parser.add_argument(
        "--ignore-files",
        action="store_true",
        default=True,
        help=(
            "Skip files whose basename is listed in vaultConfigOdinRAG.IGNORE_FILES (README.md, .gitignore, ...). Default: TRUE (ignore some .md file)."
        ),
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress per-file output for files without issues.",
    )
    args = parser.parse_args(argv)

    if not args.ignore_dirs and not args.ignore_files:
        cprint(
            "[warn] Neither --ignore-dirs nor --ignore-files is set; the scan will walk every .md file under the current directory (including .git/, node_modules/, _Private/)."
            "Pass --ignore-dirs and/or --ignore-files to apply the curated skip lists.",
            "YELLOW",
            bold=True,
        )

    try:
        targets = find_targets(
            args.files,
            ignore_dirs=args.ignore_dirs,
            ignore_files=args.ignore_files,
        )
    except Exception as exc:
        print(f"[ERR] Failed to enumerate targets: {exc}", file=sys.stderr)
        return 2

    if not targets:
        print("[warn] No markdown files found to validate.", file=sys.stderr)
        return 0

    total_errors = 0
    total_warnings = 0
    total_info = 0
    files_with_errors = 0
    files_with_warnings = 0
    files_scanned = 0
    files_skipped = 0

    for target in targets:
        if not should_validate(target):
            files_skipped += 1
            continue
        files_scanned += 1
        try:
            errors, warnings, info = check_file(target, do_content_check=not args.no_content_check)
        except Exception as exc:
            cprint(f"{path_link(target)} - tool error: {exc}", "RED", bold=True)
            total_errors += 1
            continue

        total_errors += len(errors)
        total_warnings += len(warnings)
        total_info += len(info)

        if errors:
            files_with_errors += 1
            cprint(f"{path_link(target)} - {len(errors)} error(s):", "RED", bold=True)
            for e in errors:
                cprint(f"  - {e}", "RED")
            if warnings:
                for w in warnings:
                    cprint(f"  - (warn) {w}", "YELLOW")
            if info:
                for i in info:
                    cprint(f"  - (info) {i}", "CYAN")
            print("", file=sys.stderr)
            continue

        if warnings or info:
            files_with_warnings += 1 if warnings else 0
            if not args.quiet or info:
                cprint(f"{path_link(target)} - {len(warnings)} warning(s), {len(info)} info:", "YELLOW", bold=bool(warnings))
                for w in warnings:
                    cprint(f"  - (warn) {w}", "YELLOW")
                for i in info:
                    cprint(f"  - (info) {i}", "CYAN")
                if warnings or info:
                    print("", file=sys.stderr)
            continue

        if not args.quiet:
            cprint(f"{path_link(target)} - OK", "GREEN")

    print("", file=sys.stderr)
    cprint("=" * 60, "CYAN", bold=True)
    cprint("Frontmatter validation summary", "CYAN", bold=True)
    cprint(f"  Files scanned        : {files_scanned}", "CYAN")
    cprint(f"  Files skipped        : {files_skipped} (per should_validate)", "CYAN")
    cprint(f"  Files with errors    : {files_with_errors}", "RED" if files_with_errors else "GREEN", bold=files_with_errors > 0)
    cprint(f"  Total errors         : {total_errors}", "RED" if total_errors else "GREEN")
    cprint(f"  Total warnings       : {total_warnings}", "YELLOW" if total_warnings else "GREEN")
    cprint(f"  Total info           : {total_info}", "CYAN")
    cprint(f"  Required fields      : {', '.join(REQUIRED_FIELDS)}", "CYAN")
    cprint(f"  Allowed types        : {', '.join(sorted(ALLOWED_TYPES))}", "CYAN")
    cprint(
        f"  Ignore filters       : dirs={'on' if args.ignore_dirs else 'off'} ({len(IGNORE_DIRS)} entries), files={'on' if args.ignore_files else 'off'} ({len(IGNORE_FILES)} entries)",
        "CYAN",
    )
    cprint("=" * 60, "CYAN", bold=True)

    if total_errors > 0:
        if args.fail_on_error:
            return 2
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
