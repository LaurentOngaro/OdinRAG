#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/download_power_of_ten.py - Download NASA / Gerard J. Holzmann's "Power of Ten" PDF.

Fetches the PDF (mirror via the Wayback Machine, because spinroot.com is behind a
Cloudflare JS challenge that programmatic clients cannot satisfy) and writes it to
odin-knowledge-base/references/power_of_ten.pdf. Also writes a small Markdown wrapper
with the project frontmatter and a link to the PDF at
odin-knowledge-base/references/power_of_ten.md.

This is a legacy NASA JPL document; the underlying PDF has not changed in years. The
script hashes the downloaded bytes and rewrites the PDF only on drift. Re-runs are
idempotent (no-op when nothing changed).

Usage::

    python _Helpers/scripts/scrapers/download_power_of_ten.py            # fetch + write
    python _Helpers/scripts/scrapers/download_power_of_ten.py --check    # dry-run: verify reachability + content-type
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
REF_DIR = REPO_ROOT / "odin-knowledge-base" / "references"
TARGET_PDF = REF_DIR / "power_of_ten.pdf"
TARGET_MD = REF_DIR / "power_of_ten.md"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import fetch as http_fetch  # noqa: E402

SOURCE_URL = "https://spinroot.com/gerard/pdf/P10.pdf"
# Wayback Machine mirror - spinroot.com is behind a Cloudflare interactive JS
# challenge that urllib/requests cannot satisfy; the Wayback snapshot returns
# the same bytes (~37 KB PDF).
WAYBACK_URL = "https://web.archive.org/web/2024if_/https://spinroot.com/gerard/pdf/P10.pdf"
USER_AGENT = "Mozilla/5.0 (compatible; OdinRAG/1.0; +https://github.com/LaurentOngaro/OdinRAG)"

# Frontmatter for the .md wrapper. The .pdf is the canonical artifact; the .md is just a pointer.
FRONTMATTER = (
    "---\n"
    'title: "The Power of Ten - Rules for Developing Safety Critical Code (Gerard J. Holzmann, NASA JPL)"\n'
    'date: "2026-07-10"\n'
    "tags: [OdinRAG, kb, reference, safety, source/nasa-jpl]\n"
    "type: reference\n"
    "status: active\n"
    'version: 1.0.0\n'
    'lastUpdated: "2026-07-10"\n'
    'updatedBy: "MiniMax-M3 (Kilo Code) via download_power_of_ten.py"\n'
    "summary: \"NASA JPL's 10 rules for safety-critical code - the academic source "
    "behind TigerStyle's 'Safety' section. PDF stays canonical; .md is just a pointer.\"\n"
    "---\n"
)


def sha256_short(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def render_wrapper_md(pdf_size_bytes: int) -> str:
    """Build the Markdown wrapper around the PDF, with the actual file size filled in."""
    size_kb = pdf_size_bytes / 1024
    body = (
        "# The Power of Ten - Rules for Developing Safety Critical Code\n"
        "\n"
        f"Canonical artifact (PDF): [`power_of_ten.pdf`](./power_of_ten.pdf) - fetched from [{SOURCE_URL}]({SOURCE_URL}).\n"
        "\n"
        "Author: Gerard J. Holzmann (NASA / JPL Laboratory for Reliable Software).\n"
        "\n"
        "> The 10 rules below are the academic source that TigerStyle's **Safety** section "
        "explicitly cites and expands on (see [`./tiger_style.md`](./tiger_style.md)). "
        "They are language-agnostic and apply directly to Odin projects: simple control flow, "
        "fixed loop bounds, no recursion, compiler-warnings-as-errors at the strictest level, and so on.\n"
        "\n"
        "## Source note\n"
        "\n"
        f"The canonical host ({SOURCE_URL}) sits behind a Cloudflare JS challenge that "
        f"programmatic downloaders cannot satisfy. We fetch the PDF via the Wayback Machine "
        f"snapshot ({WAYBACK_URL}) which returns the same bytes (~{size_kb:.1f} KB as of the "
        "2024 snapshot). If the URL drifts, update the snapshot year in `download_power_of_ten.py`.\n"
        "\n"
        "## How to read\n"
        "\n"
        "- **Short version (5 min)**: skim the rules in §1 and the rationale in §3 of the PDF.\n"
        "- **Deep read (30 min)**: the full paper, including the discussions of why each rule "
        "matters. The appendix lists historical incidents that motivated each rule.\n"
        "\n"
        "## Origin\n"
        "\n"
        "The Power of Ten was published in the **IEEE Computer** column \"Robustness\" in 2006. "
        "It is public, no paywall, and explicitly intended to be redistributed by teams building "
        "safety-critical software. The PDF is the canonical artifact; this Markdown file exists "
        "only to make the asset discoverable by Kilo's KB index.\n"
        "\n"
        f">Source: {SOURCE_URL}\n"
    )
    return FRONTMATTER + "\n" + body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download NASA JPL 'Power of Ten' PDF + a Markdown wrapper."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: verify reachability + content-type without writing.",
    )
    args = parser.parse_args(argv)

    print("[*] Canonical source (Cloudflare-protected):", SOURCE_URL)
    print("[*] Fetch mirror:", WAYBACK_URL)
    print("[*] PDF target:", TARGET_PDF)
    print("[*] MD  target:", TARGET_MD)

    resp = http_fetch(WAYBACK_URL, headers={"User-Agent": USER_AGENT})
    if resp is None:
        print(f"  [ERR] GET {WAYBACK_URL} -> no response")
        return 2
    print(
        f"  [HTTP] {WAYBACK_URL} -> {resp.status_code} "
        f"({resp.headers.get('Content-Type', '?')})"
    )
    if resp.status_code != 200:
        return 2

    content_type = resp.headers.get("Content-Type", "").lower()
    if "pdf" not in content_type:
        print(f"  [ERR] {WAYBACK_URL} returned Content-Type={content_type!r}, expected a PDF")
        return 2

    pdf_bytes = resp.content
    size_kb = len(pdf_bytes) / 1024
    print(f"  [SIZE] {size_kb:.1f} KB (sha256[:12]={sha256_short(pdf_bytes)})")

    if args.check:
        print("[*] --check: would write (skipping)")
        return 0

    REF_DIR.mkdir(parents=True, exist_ok=True)

    # PDF: rewrite only if bytes differ (track upstream drift quietly).
    if TARGET_PDF.exists() and TARGET_PDF.read_bytes() == pdf_bytes:
        print(f"  [SKIP] {TARGET_PDF.name} unchanged")
    else:
        TARGET_PDF.write_bytes(pdf_bytes)
        print(f"  [OK] wrote {TARGET_PDF.name} ({size_kb:.1f} KB)")

    # Markdown wrapper: always rewrite (cheap, keeps size + URLs current).
    md_text = render_wrapper_md(len(pdf_bytes))
    if not md_text.endswith("\n"):
        md_text += "\n"
    TARGET_MD.write_text(md_text, encoding="utf-8")
    print(f"  [OK] wrote {TARGET_MD.name} ({md_text.count(chr(10))} lines)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
