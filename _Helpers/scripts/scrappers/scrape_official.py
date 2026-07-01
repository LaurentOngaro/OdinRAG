#!/usr/bin/env python3
"""
_Helpers/scripts/scrappers/scrape_official.py - Official Docs Scraper (odin-lang.org)
[Re-entrant: skip if <output>.md already exists; --force to rewrite]

Fetches the COMPLETE official Odin documentation (all /docs/ pages) in Markdown, plus the awesome-odin index (raw README from GitHub).

Usage:
    python _Helpers/scripts/scrappers/scrape_official.py            # skip if already exported (re-entrant)
    python _Helpers/scripts/scrappers/scrape_official.py --force    # force full rewrite

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery strategy (most reliable to most fragile):
    1. /sitemap.xml         - all official URLs
    2. Crawl of /docs/      - follow the sidebar to find pages
    3. Static list          - fallback if the site exposes no sitemap (FALLBACK_PAGES)

Output:
    odin-knowledge-base/docs/official/<path>.md      (/docs/ pages, footer ">Source: <url>")
    odin-knowledge-base/docs/official/awesome-odin.md  (raw README from jakubtomsu/awesome-odin)

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless ``--force``.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).
    - User-Agent: "Mozilla/5.0 (compatible; OdinRAG/1.0)".

Exit codes:
    0   full success
    1   no page discovered (all strategies exhausted)
    2   partial success (at least one page failed)
"""
import sys
import time
from pathlib import Path
import argparse

# Allow importing the ``_Helpers/lib`` package from the archive.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import (  # noqa: E402
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
    crawl_links,
    discover_via_sitemap,
    fetch,
    normalize_url,
    path_to_filename,
)
from lib.html2md import scrape_to_markdown  # noqa: E402

_DESCRIPTION = "Official Docs Scraper (odin-lang.org) - re-entrant, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parents[3] / "odin-knowledge-base" / "docs" / "official"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL    = "https://odin-lang.org"
DOCS_INDEX  = f"{BASE_URL}/docs/"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"

AWESOME_RAW = (
    "https://raw.githubusercontent.com/jakubtomsu/awesome-odin/main/README.md"
)

REQUEST_DELAY = 0.5   # seconds between each request (politeness)

# Static fallback list (used if sitemap + crawl fail)
FALLBACK_PAGES: list[str] = [
    "/docs/overview/", "/docs/install/", "/docs/install/linux/",
    "/docs/install/macos/", "/docs/install/windows/", "/docs/install/wasm/",
    "/docs/editor/", "/docs/misc/", "/docs/packages/", "/docs/testing/",
    "/docs/faq/", "/docs/guidelines/", "/docs/statements-and-declarations/",
    "/docs/types/", "/docs/procedures/", "/docs/control-flow/",
    "/docs/expressions/", "/docs/attributes/", "/docs/directives/",
    "/docs/builtin/", "/docs/changelog/",
]
# ──────────────────────────────────────────────────────────────────────────────


def discover_via_index(index_url: str) -> list[str]:
    """Crawl /docs/ and the sidebar to find linked pages."""
    return crawl_links(
        index_url,
        predicate=lambda _url, path: path.startswith("/docs/"),
        follow_predicate=lambda path: path == "/docs/" or path.startswith("/docs/"),
        max_pages=20,
        delay=REQUEST_DELAY,
    )


def discover_all() -> list[str]:
    """Chain the discovery strategies."""
    print("[*] Discovering official pages...")
    pages = discover_via_sitemap(
        SITEMAP_URL, base_host=BASE_URL, path_prefix="/docs/",
    )
    if pages:
        print(f"  [+] {len(pages)} pages via sitemap.xml")
        return pages

    print("  [i] sitemap unavailable, crawling /docs/...")
    pages = discover_via_index(DOCS_INDEX)
    if pages:
        print(f"  [+] {len(pages)} pages via /docs/")
        return pages

    print("  [!] crawl failed, falling back to static list")
    pages = [f"{BASE_URL}{p}" for p in FALLBACK_PAGES]
    print(f"  [+] {len(pages)} pages via fallback")
    return pages


def scrape_awesome() -> bool:
    """Download the awesome-odin raw README."""
    print("[*] awesome-odin.md...")
    resp = fetch(AWESOME_RAW)
    if not resp or resp.status_code != 200:
        status = resp.status_code if resp else "no response"
        print(f"  [ERR] awesome-odin: status={status}")
        return False
    (OUT / "awesome-odin.md").write_text(resp.text, encoding="utf-8")
    print(f"  [+] awesome-odin.md ({len(resp.text)} chars)")
    return True


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--force", action="store_true",
        help="Rewrite every .md even if it already exists (default: skip).",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Odin Official Docs Scraper - full coverage")
    print("=" * 60)

    pages = discover_all()
    if not pages:
        print("[ERR] No page discovered. Aborting.")
        return 1

    print(f"\n[*] Scraping {len(pages)} pages "
            f"({'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, url in enumerate(pages, 1):
        filename = path_to_filename(url.replace(BASE_URL, ""), prefix_to_strip="docs")
        out_path = OUT / filename
        if not args.force and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  [{i:>2}/{len(pages)}] {filename}  [SKIP already present]")
            skipped += 1
            continue
        print(f"  [{i:>2}/{len(pages)}] {url} -> {filename}")
        if scrape_to_markdown(url, out_path):
            print(f"          [OK] {filename}")
            scraped += 1
        else:
            print(f"          [FAIL]")
            failed += 1
        time.sleep(REQUEST_DELAY)

    awesome_ok = scrape_awesome()

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(pages)} targeted pages")
    print(f"  awesome-odin: {'OK' if awesome_ok else 'FAIL'}")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
