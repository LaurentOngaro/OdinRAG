#!/usr/bin/env python3
"""
_Helpers/scripts/scrappers/scrape_zylinski.py - Blog Scraper (karl zylinski)
[Re-entrant: skip if <slug>.md already exists; --force to rewrite]

Fetches ALL articles from the https://zylinski.se blog and converts them into Markdown under odin-knowledge-base/docs/karl_zylinski/.

Usage:
    python _Helpers/scripts/scrappers/scrape_zylinski.py            # skip if already exported (re-entrant)
    python _Helpers/scripts/scrappers/scrape_zylinski.py --force    # force full rewrite

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery strategy (most reliable to most fragile):
    1. RSS feed        (/index.xml)         - Hugo, contains all canonical URLs
    2. Sitemap XML     (/sitemap.xml)
    3. Paginated crawl (/posts/, /posts/page/N/)
    4. Static list     - fallback (FALLBACK_SLUGS, 8 historical URLs)

Output:
    odin-knowledge-base/docs/karl_zylinski/<slug>.md (one file per article, with footer ">Source: <url>")

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless ``--force``.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).
    - Crawl capped at 20 pages (safeguard against infinite loops).

Exit codes:
    0   full success
    1   no article discovered (all strategies exhausted)
    2   partial success (at least one page failed)
"""
import argparse
import re
import sys
import time
from pathlib import Path

# Allow importing the ``_Helpers/lib`` package from the archive.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import (  # noqa: E402
    crawl_links,
    discover_via_rss,
    discover_via_sitemap,
    normalize_url,
    slug_from_url,
)
from lib.html2md import scrape_to_markdown  # noqa: E402

_DESCRIPTION = "Karl Zylinski blog scraper (zylinski.se) - re-entrant via RSS, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parents[3] / "odin-knowledge-base" / "docs" / "karl_zylinski"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL    = "https://zylinski.se"
RSS_URL     = f"{BASE_URL}/index.xml"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
POSTS_INDEX = f"{BASE_URL}/posts/"

REQUEST_DELAY = 0.5
POSTS_INDEX_NORM = normalize_url(POSTS_INDEX)

# Fallback (used if RSS + sitemap + crawl fail)
FALLBACK_SLUGS: list[str] = [
    "hot-reload-gameplay-code",
    "no-engine-gamedev-using-odin-and-raylib",
    "odin-dod-benchmarks",
    "odin-c-bindgen",
    "a-programming-language-for-me",
    "odin-sokol-web",
    "raylib-3d-experiments",
    "making-a-point-and-click-game",
]
# ──────────────────────────────────────────────────────────────────────────────


def discover_via_crawl(start_url: str) -> list[str]:
    """Crawl /posts/ and its /posts/page/N/ pages to extract article links."""
    return crawl_links(
        start_url,
        predicate=lambda _url, path: (
            path.startswith("/posts/")
            and path != "/posts/"
            and normalize_url(_url) != POSTS_INDEX_NORM
        ),
        follow_predicate=lambda path: bool(re.match(r".*/page/\d+/?$", path)),
        max_pages=20,
        delay=REQUEST_DELAY,
    )


def discover_all() -> tuple[list[str], str]:
    """Chain the discovery strategies. Returns (urls, source)."""
    print("[*] Discovering articles...")

    urls = discover_via_rss(
        RSS_URL, must_contain="/posts/", exclude_path=POSTS_INDEX,
    )
    if urls:
        print(f"  [+] {len(urls)} articles via RSS feed")
        return urls, "rss"

    urls = discover_via_sitemap(
        SITEMAP_URL, base_host=BASE_URL, path_prefix="/posts/",
        exclude_path=POSTS_INDEX,
    )
    if urls:
        print(f"  [+] {len(urls)} articles via sitemap.xml")
        return urls, "sitemap"

    print("  [i] RSS/sitemap unavailable, crawling /posts/...")
    urls = discover_via_crawl(POSTS_INDEX)
    if urls:
        print(f"  [+] {len(urls)} articles via crawl")
        return urls, "crawl"

    print("  [!] crawl failed, falling back to static list")
    urls = [f"{BASE_URL}/posts/{slug}" for slug in FALLBACK_SLUGS]
    print(f"  [+] {len(urls)} articles via fallback")
    return urls, "fallback"


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--force", action="store_true",
        help="Rewrite every .md even if it already exists (default: skip).",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Zylinski Blog Scraper - full coverage")
    print("=" * 60)

    urls, source = discover_all()
    if not urls:
        print("[ERR] No article discovered. Aborting.")
        return 1

    print(f"\n[*] Scraping {len(urls)} articles (source: {source}, "
            f"{'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, url in enumerate(urls, 1):
        slug = slug_from_url(url, segment="posts")
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

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(urls)} targeted articles ({source})")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
