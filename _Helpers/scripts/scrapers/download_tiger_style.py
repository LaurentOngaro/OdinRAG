#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/download_tiger_style.py - Download TigerStyle from TigerBeetle's GitHub.

Fetches https://raw.githubusercontent.com/tigerbeetle/tigerbeetle/main/docs/TIGER_STYLE.md,
normalizes forbidden Unicode punctuation (em-dash -> hyphen, smart quotes -> ASCII, ellipsis -> ...),
prepends the project canonical YAML frontmatter, and writes to
odin-knowledge-base/references/tiger_style.md.

This script is idempotent: re-running overwrites with the latest upstream content. The
canonical frontmatter is preserved verbatim at the top, so a diff between two runs only shows
real upstream changes (not metadata churn).

Usage::

    python _Helpers/scripts/scrapers/download_tiger_style.py           # fetch + normalize + write
    python _Helpers/scripts/scrapers/download_tiger_style.py --check   # dry-run: verify reachability
    python _Helpers/scripts/scrapers/download_tiger_style.py --force   # same as no-flag (alias for clarity)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
REF_DIR = REPO_ROOT / "odin-knowledge-base" / "references"
TARGET = REF_DIR / "tiger_style.md"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import fetch as http_fetch  # noqa: E402

SOURCE_URL = "https://raw.githubusercontent.com/tigerbeetle/tigerbeetle/main/docs/TIGER_STYLE.md"
USER_AGENT = "OdinRAG/1.0 (tiger_style-downloader)"

# Canonical frontmatter for this KB reference. Keep schema in sync with
# odin-knowledge-base/references/README - references.md and AGENTS.md "Language" rule.
FRONTMATTER = (
    "---\n"
    'title: "TigerStyle - Coding style guide for safety-critical systems"\n'
    'date: "2026-07-10"\n'
    "tags: [OdinRAG, kb, reference, style, source/tigerbeetle]\n"
    "type: reference\n"
    "status: active\n"
    'version: 1.0.0\n'
    'lastUpdated: "2026-07-10"\n'
    'updatedBy: "MiniMax-M3 (Kilo Code) via download_tiger_style.py"\n'
    'summary: "TigerBeetle\'s coding style guide for safety-critical systems, '
    "distilled for Odin projects - safety, performance, naming, off-by-one prevention.\"\n"
    "---\n"
)

# Project rule from AGENTS.md: never use em-dash / smart quotes / ellipsis in tracked MD.
# Kept as a string to preserve a type-narrow iteration later (`text.count(c)`).
_FORBIDDEN_CHARS = "\u2014\u2013\u201c\u201d\u2018\u2019\u2026"
_FORBIDDEN = str.maketrans(
    {
        "\u2014": "-",  # em-dash
        "\u2013": "-",  # en-dash
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u2026": "...",  # ellipsis
    }
)


def normalize_unicode(text: str) -> str:
    """Replace project-forbidden Unicode punctuation with ASCII equivalents."""
    return text.translate(_FORBIDDEN)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download TigerStyle from TigerBeetle's GitHub main branch."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: verify the upstream URL is reachable without writing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always rewrite (default behaviour; kept for run_all_scrapers.py uniformity).",
    )
    args = parser.parse_args(argv)

    print(f"[*] Source: {SOURCE_URL}")
    print(f"[*] Target: {TARGET}")

    resp = http_fetch(SOURCE_URL, headers={"User-Agent": USER_AGENT})
    if resp is None:
        print(f"  [ERR] GET {SOURCE_URL} -> no response")
        return 2
    print(f"  [HTTP] {SOURCE_URL} -> {resp.status_code}")
    if resp.status_code != 200:
        return 2

    if args.check:
        print("[*] --check: would write (skipping)")
        return 0

    REF_DIR.mkdir(parents=True, exist_ok=True)

    raw = resp.text
    cleaned = normalize_unicode(raw)
    body = cleaned.lstrip("\n")
    # Source already provides an `# TigerStyle` H1; we prepend the frontmatter + one blank line.
    out = FRONTMATTER + "\n" + body
    if not out.endswith("\n"):
        out += "\n"
    TARGET.write_text(out, encoding="utf-8")

    lines = out.count("\n")
    before_chars = sum(raw.count(c) for c in _FORBIDDEN_CHARS)
    print(
        f"  [OK] wrote {TARGET.name} ({lines} lines, {len(out)} bytes; "
        f"normalized {before_chars} forbidden Unicode chars)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
