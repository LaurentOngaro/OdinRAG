#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/run_all_scrapers.py - Launch every scraper in this folder interactively.

Discovers every `*.py` sibling in `_Helpers/scripts/scrapers/`, shows the
description parsed from its module docstring, and asks for confirmation
before launching it. Designed to be the single entry point for a full KB
refresh without having to remember each scraper's name and flags.

Usage:
    python _Helpers/scripts/scrapers/run_all_scrapers.py             # interactive: prompt before each
    python _Helpers/scripts/scrapers/run_all_scrapers.py --check     # list every scraper, do not run
    python _Helpers/scripts/scrapers/run_all_scrapers.py --yes       # non-interactive: run every scraper in order
    python _Helpers/scripts/scrapers/run_all_scrapers.py --only skool --only changelog
    python _Helpers/scripts/scrapers/run_all_scrapers.py --skip gitingest --skip gists

Confirmation prompt:
    [O/n/q] O (default) = run this scraper
            n            = skip this scraper, continue with the next one
            q            = abort the whole run

Exit codes:
    0   all selected scrapers succeeded
    1   no scraper matched the filters
    2   at least one scraper exited non-zero
    130 aborted by user (Ctrl+C or `q` on the prompt)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SELF_NAME = Path(__file__).name

PROMPT_RUN = "O"
PROMPT_SKIP = "n"
PROMPT_QUIT = "q"


def parse_description(path: Path) -> str:
    """Extract a one-line description from a scraper's module docstring.

    The convention used by every scraper in this folder is a module-level
    docstring whose first line is `<path>.py - <description>`.

    Returns the description with the leading `path - ` prefix stripped,
    or the first non-empty line if that pattern is not found. Returns
    an empty string if the file has no usable docstring.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""

    quote: str | None = None
    lines: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if quote is None:
            if stripped.startswith('"""'):
                quote = '"""'
                rest = stripped[3:].strip()
                if rest.endswith('"""') and len(rest) >= 3:
                    lines.append(rest[:-3].strip())
                    break
                if rest:
                    lines.append(rest)
                continue
            if stripped.startswith("'''"):
                quote = "'''"
                rest = stripped[3:].strip()
                if rest.endswith("'''") and len(rest) >= 3:
                    lines.append(rest[:-3].strip())
                    break
                if rest:
                    lines.append(rest)
                continue
            continue
        if stripped.endswith(quote):
            tail = stripped[: -len(quote)].strip()
            if tail:
                lines.append(tail)
            break
        if stripped:
            lines.append(stripped)

    if not lines:
        return ""

    header = lines[0]
    if " - " in header:
        prefix, _, desc = header.partition(" - ")
        if prefix.strip().lower().endswith(".py"):
            return desc.strip()
    return header.strip()


def list_scrapers() -> list[Path]:
    """Return every `*.py` sibling in SCRIPT_DIR, alphabetically, except this orchestrator."""
    return sorted(
        p for p in SCRIPT_DIR.glob("*.py")
        if p.name != SELF_NAME
    )


def apply_filters(
    scripts: list[Path],
    only: list[str] | None,
    skip: list[str] | None,
) -> list[Path]:
    """Filter `scripts` by the repeated --only / --skip substring patterns (case-insensitive)."""
    if only:
        needles = [s.lower() for s in only]
        scripts = [p for p in scripts if any(n in p.name.lower() for n in needles)]
    if skip:
        needles = [s.lower() for s in skip]
        scripts = [p for p in scripts if not any(n in p.name.lower() for n in needles)]
    return scripts


def print_inventory(scripts: list[Path]) -> None:
    """Pretty-print the selected scrapers and their parsed descriptions."""
    width = max((len(p.name) for p in scripts), default=20)
    print("=" * 78)
    print(f"  Scrapers in {SCRIPT_DIR.name}/")
    print(f"  {len(scripts)} script(s) selected")
    print("=" * 78)
    if not scripts:
        print("  (none)")
        return
    for p in scripts:
        desc = parse_description(p) or "(no description)"
        print(f"  - {p.name:<{width}}  {desc}")


def confirm(prompt: str, auto_yes: bool) -> str:
    """Read a confirmation answer from stdin, or return the default when auto_yes is set.

    Returns one of `PROMPT_RUN`, `PROMPT_SKIP`, `PROMPT_QUIT`.
    EOFError (piped stdin closed) is treated as `PROMPT_QUIT`.
    """
    if auto_yes:
        return PROMPT_RUN
    try:
        answer = input(f"  {prompt} [{PROMPT_RUN}/{PROMPT_SKIP}/{PROMPT_QUIT}] ").strip().lower()
    except EOFError:
        print()
        return PROMPT_QUIT
    except KeyboardInterrupt:
        print()
        return PROMPT_QUIT
    if answer in ("", PROMPT_RUN, "o", "oui", "y", "yes"):
        return PROMPT_RUN
    if answer in (PROMPT_SKIP, "no", "non"):
        return PROMPT_SKIP
    if answer in (PROMPT_QUIT, "quit", "exit", "stop"):
        return PROMPT_QUIT
    print(f"  [!] Unrecognised answer {answer!r}, treating as skip.")
    return PROMPT_SKIP


def run_one(python: str, script: Path) -> int:
    """Launch `python <script>` from SCRIPT_DIR, streaming its output. Returns its exit code."""
    print(f"  [->] Launching: {python} {script.name}")
    try:
        return subprocess.call([python, str(script)], cwd=str(SCRIPT_DIR))
    except FileNotFoundError as exc:
        print(f"  [ERR] {exc}")
        return 127


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: print the list of scrapers that would run, then exit.",
    )
    parser.add_argument(
        "--yes", "-y", action="store_true",
        help="Skip the confirmation prompt and run every selected scraper.",
    )
    parser.add_argument(
        "--only", action="append", default=[],
        help="Only run scripts whose filename contains this substring (case-insensitive). Repeatable.",
    )
    parser.add_argument(
        "--skip", action="append", default=[],
        help="Skip scripts whose filename contains this substring (case-insensitive). Repeatable.",
    )
    parser.add_argument(
        "--python", default=sys.executable,
        help="Python interpreter used to launch the scrapers (default: current interpreter).",
    )
    args = parser.parse_args(argv)

    scripts = apply_filters(list_scrapers(), args.only or None, args.skip or None)
    print_inventory(scripts)

    if args.check:
        return 0
    if not scripts:
        print("[ERR] No scraper matched the filters.")
        return 1

    print()
    print("-" * 78)
    print("  Interactive run. Each scraper will be confirmed before launch.")
    print("-" * 78)

    failures: list[tuple[str, int]] = []
    skipped = 0
    for idx, script in enumerate(scripts, start=1):
        print()
        print(f"  [{idx}/{len(scripts)}] {script.name}")
        desc = parse_description(script)
        if desc:
            print(f"           {desc}")

        answer = confirm("\nRun this scraper?\n", args.yes)
        if answer == PROMPT_QUIT:
            print("[!] Aborted by user.")
            return 130
        if answer == PROMPT_SKIP:
            print("  [skip]")
            skipped += 1
            continue

        rc = run_one(args.python, script)
        if rc == 0:
            print(f"  [ok]  {script.name}")
        else:
            print(f"  [fail] {script.name} exited with code {rc}")
            failures.append((script.name, rc))

    print()
    print("=" * 78)
    if failures:
        names = ", ".join(f"{n} (rc={c})" for n, c in failures)
        print(f"  {len(failures)} failure(s): {names}")
        if skipped:
            print(f"  {skipped} scraper(s) skipped by user.")
        print("=" * 78)
        return 2
    print(f"  All {len(scripts) - skipped} launched scraper(s) succeeded ({skipped} skipped by user).")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.exit(main())
