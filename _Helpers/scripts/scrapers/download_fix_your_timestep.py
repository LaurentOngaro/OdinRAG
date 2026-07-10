#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/download_fix_your_timestep.py - Download Glenn Fiedler's "Fix Your Timestep!" article as Markdown.

Fetches https://gafferongames.com/post/fix_your_timestep/, converts the article HTML to
Markdown via the shared `lib.html2md` pipeline, normalizes project-forbidden Unicode
punctuation (em-dash, smart quotes, ellipsis), prepends the canonical YAML frontmatter,
and writes to odin-knowledge-base/references/fix_your_timestep.md.

The article is a single static page (frozen since 2015) so the script is simple;
re-running produces a diff-free result if the page has not changed upstream.

Usage::

    python _Helpers/scripts/scrapers/download_fix_your_timestep.py           # fetch + convert + normalize + write
    python _Helpers/scripts/scrapers/download_fix_your_timestep.py --check   # dry-run: verify reachability
    python _Helpers/scripts/scrapers/download_fix_your_timestep.py --force   # always rewrite
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
TARGET = REF_DIR / "fix_your_timestep.md"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.html2md import html_to_markdown  # noqa: E402
from lib.http_client import fetch as http_fetch  # noqa: E402

SOURCE_URL = "https://gafferongames.com/post/fix_your_timestep/"
USER_AGENT = "Mozilla/5.0 (compatible; OdinRAG/1.0; +https://github.com/LaurentOngaro/OdinRAG)"

FRONTMATTER = (
    "---\n"
    'title: "Fix Your Timestep! - Game loop timing theory (Glenn Fiedler, 2015)"\n'
    'date: "2026-07-10"\n'
    "tags: [OdinRAG, kb, reference, gamedev, topic/gameloop, source/gafferongames]\n"
    "type: reference\n"
    "status: active\n"
    'version: 1.0.0\n'
    'lastUpdated: "2026-07-10"\n'
    'updatedBy: "MiniMax-M3 (Kilo Code) via download_fix_your_timestep.py"\n'
    'summary: "Glenn Fiedler\'s canonical article on game loop timesteps: '
    "fixed-step accumulator, semi-fixed, and variable-step tradeoffs. "
    "Essential for any game with physics or animation; informs why OdinRAG recommends a "
    'fixed-step accumulator at the core of every game loop."\n'
    "---\n"
)

# Project-forbidden Unicode chars (AGENTS.md "Punctuation: no AI-typical characters").
# Kept as a string so the count-step below iterates over `str` characters (not dict keys).
_FORBIDDEN_CHARS = "\u2014\u2013\u201c\u201d\u2018\u2019\u2026"
_FORBIDDEN = str.maketrans(
    {
        "\u2014": "-",
        "\u2013": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2026": "...",
    }
)


def normalize_unicode(text: str) -> str:
    return text.translate(_FORBIDDEN)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download Glenn Fiedler's 'Fix Your Timestep!' article as Markdown."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: verify the upstream URL is reachable without writing.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Always rewrite even if the target file is unchanged.",
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

    # Convert HTML to clean Markdown (uses BeautifulSoup + markdownify under the hood,
    # strips nav/script/style/aside/footer, prefers <article> then <main> then <body>).
    body_md = html_to_markdown(resp.text)
    if not body_md:
        print(f"  [ERR] html_to_markdown produced empty output for {SOURCE_URL}")
        return 2

    # Compose: frontmatter + blank line + body + source footer.
    composed = FRONTMATTER + "\n" + body_md + f"\n\n>Source: {SOURCE_URL}\n"
    cleaned = normalize_unicode(composed)
    if not cleaned.endswith("\n"):
        cleaned += "\n"

    # Skip the write if the file would be identical (helps diff review + avoids noise).
    if TARGET.exists() and TARGET.read_text(encoding="utf-8") == cleaned and not args.force:
        print(f"  [SKIP] {TARGET.name} already up to date (re-run with --force to rewrite)")
        return 0

    TARGET.write_text(cleaned, encoding="utf-8")
    lines = cleaned.count("\n")
    before_chars = sum(resp.text.count(c) for c in _FORBIDDEN_CHARS)
    print(
        f"  [OK] wrote {TARGET.name} ({lines} lines, {len(cleaned)} bytes; "
        f"normalized {before_chars} forbidden Unicode chars)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
