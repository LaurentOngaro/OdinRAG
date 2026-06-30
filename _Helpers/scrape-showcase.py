#!/usr/bin/env python3
"""
_Helpers/scrape-showcase.py - Odin Showcase Scraper (odin-lang.org/showcase/)
[Re-entrant: skip if <slug>.md already exists; --force to rewrite]

Fetches all showcase entries from https://odin-lang.org/showcase/ and converts each individual showcase page into Markdown under docs/showcase/.

Usage:
    python _Helpers/scrape-showcase.py            # skip if already exported (re-entrant)
    python _Helpers/scrape-showcase.py --force    # force full rewrite
    python _Helpers/scrape-showcase.py --check    # dry-run: list what would be scraped

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery strategy (most reliable to most fragile):
    1. Crawl of /showcase/    - parse index page, collect /showcase/*/ links
    2. Static list             - fallback if crawl fails (FALLBACK_SLUGS)

Output:
    docs/showcase/<slug>.md      (each showcase page, footer ">Source: <url>")
    docs/showcase/README.md      (generated index of all scraped pages)

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless --force.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).
    - User-Agent: "Mozilla/5.0 (compatible; OdinRAG/1.0)".

Exit codes:
    0   full success
    1   no page discovered (all strategies exhausted)
    2   partial success (at least one page failed)
    3   --check mode found nothing to scrape
"""
import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Allow importing the _Helpers/lib package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import (  # noqa: E402
    crawl_links,
    fetch,
    slug_from_url,
)
from lib.html2md import scrape_to_markdown  # noqa: E402

_DESCRIPTION = "Odin Showcase Scraper (odin-lang.org/showcase/) - re-entrant, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parent.parent / "docs" / "showcase"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL     = "https://odin-lang.org"
SHOWCASE_URL = f"{BASE_URL}/showcase/"

REQUEST_DELAY = 0.5  # seconds between each request (politeness)

FALLBACK_SLUGS: list[str] = [
    "ols",
    "embergen",
    "understanding_the_odin_programming_language",
    "solar_storm",
    "cat_and_onion",
    "spall",
    "todool",
]
# ──────────────────────────────────────────────────────────────────────────────


def discover_via_index(index_url: str) -> list[str]:
    """Crawl /showcase/ to extract /showcase/<slug>/ links."""
    return crawl_links(
        index_url,
        predicate=lambda _url, path: (
            path.startswith("/showcase/")
            and path != "/showcase/"
        ),
        follow_predicate=lambda path: path == "/showcase/",
        max_pages=1,
        delay=REQUEST_DELAY,
    )


def discover_all() -> tuple[list[str], str]:
    """Chain the discovery strategies. Returns (urls, source)."""
    print("[*] Discovering showcase entries...")

    urls = discover_via_index(SHOWCASE_URL)
    if urls:
        print(f"  [+] {len(urls)} entries via /showcase/")
        return urls, "crawl"

    print("  [!] crawl failed, falling back to static list")
    urls = [f"{BASE_URL}/showcase/{slug}/" for slug in FALLBACK_SLUGS]
    print(f"  [+] {len(urls)} entries via fallback")
    return urls, "fallback"


def generate_readme(slugs: list[str]) -> None:
    """Generate docs/showcase/README.md listing all scraped pages."""
    lines: list[str] = [
        "# Odin Showcase",
        "",
        "Mirrored from [odin-lang.org/showcase/](https://odin-lang.org/showcase/).",
        "",
        "## Entries",
        "",
    ]
    for slug in slugs:
        lines.append(
            f"- [{slug}](./{slug}.md)"
            f" ([source]({BASE_URL}/showcase/{slug}/))"
        )
    lines.append("")
    readme_path = OUT / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--force", action="store_true",
        help="Rewrite every .md even if it already exists (default: skip).",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: discover pages and show what would be scraped, then exit.",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Odin Showcase Scraper")
    print("=" * 60)

    urls, source = discover_all()
    if not urls:
        print("[ERR] No showcase entry discovered. Aborting.")
        return 1

    slugs: list[str] = []
    for url in urls:
        slug = slug_from_url(url, segment="showcase")
        slugs.append(slug)

    if args.check:
        print("\n[*] --check mode: would scrape the following:")
        for i, slug in enumerate(slugs, 1):
            out_path = OUT / f"{slug}.md"
            exists = out_path.exists() and out_path.stat().st_size > 0
            status = "PRESENT (skip)" if exists and not args.force else "SCRAPE"
            print(f"  [{i:>2}] {slug}  [{status}]")
        print(f"\n  {len(slugs)} entries from {source}")
        return 0

    print(f"\n[*] Scraping {len(urls)} entries (source: {source}, "
          f"{'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, url in enumerate(urls, 1):
        slug = slugs[i - 1]
        out_path = OUT / f"{slug}.md"
        if not args.force and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  [{i:>2}/{len(urls)}] {slug}  [SKIP already present]")
            skipped += 1
            continue
        print(f"  [{i:>2}/{len(urls)}] {url}")
        if scrape_to_markdown(url, out_path):
            print(f"          [OK] {slug}.md")
            scraped += 1
        else:
            print(f"          [FAIL]")
            failed += 1
        time.sleep(REQUEST_DELAY)

    generate_readme(slugs)

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(urls)} targeted entries ({source})")
    print(f"  README generated")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
