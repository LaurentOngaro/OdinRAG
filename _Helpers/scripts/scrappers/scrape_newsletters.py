#!/usr/bin/env python3
"""
_Helpers/scripts/scrappers/scrape_newsletters.py - Newsletter Scraper (odin-lang.org/news/)
[Re-entrant: skip if <slug>.md already exists; --force to rewrite]

Fetches ALL Odin newsletters from the https://odin-lang.org/news/ index and converts them into Markdown under odin-knowledge-base/docs/newsletters/.

Usage:
    python _Helpers/scripts/scrappers/scrape_newsletters.py            # skip if already exported (re-entrant)
    python _Helpers/scripts/scrappers/scrape_newsletters.py --force    # force full rewrite
    python _Helpers/scripts/scrappers/scrape_newsletters.py --check    # dry-run (report only, no writes)

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery strategy:
    1. Crawl https://odin-lang.org/news/ (index page), extract all <a href="/news/.../"> links
    2. Normalize + deduplicate URLs
    3. Fallback: static list (FALLBACK_ISSUES) if crawl fails

Output:
    odin-knowledge-base/docs/newsletters/<slug>.md  (one file per newsletter, with footer ">Source: <url>")
    odin-knowledge-base/docs/newsletters/README.md   (updated with scraper info if needed)

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless ``--force``.
    - ``--check`` dry-run: prints what would be scraped, exits 0, never writes.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).

Exit codes:
    0 full success (or --check dry-run complete)
    1 no newsletter discovered (all strategies exhausted)
    2 partial success (at least one page failed)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

import argparse
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

# Allow importing the ``_Helpers/lib`` package from the archive.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import (  # noqa: E402
    DEFAULT_HEADERS,
    DEFAULT_TIMEOUT,
    crawl_links,
    fetch,
    normalize_url,
)
from lib.html2md import scrape_to_markdown  # noqa: E402

_DESCRIPTION = "Odin Newsletter Scraper (odin-lang.org/news/) - re-entrant, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parents[3] / "odin-knowledge-base" / "docs" / "newsletters"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL   = "https://odin-lang.org"
NEWS_INDEX = f"{BASE_URL}/news/"

REQUEST_DELAY = 0.5

# Static fallback (used if crawl of the index page fails)
FALLBACK_ISSUES: list[str] = [
    "newsletter-2022-11",
    "newsletter-2022-12",
    "newsletter-2023-04",
    "newsletter-2023-06",
    "newsletter-2023-07",
    "newsletter-2023-08",
    "newsletter-2023-09",
    "newsletter-2023-11",
    "newsletter-2023-12",
    "newsletter-2024-01",
    "newsletter-2024-02",
    "newsletter-2024-03",
    "newsletter-2024-04",
    "newsletter-2024-05",
    "newsletter-2024-06",
    "newsletter-2024-07",
    "newsletter-2024-08",
    "newsletter-2024-09",
    "newsletter-2024-10",
    "newsletter-2024-12",
    "newsletter-2025-q1",
    "newsletter-2026-q1",
    "binding-to-c",
    "calling-odin-from-python",
    "declaration-syntax",
    "major-graphics-apis",
    "moving-towards-a-new-core-os",
    "new-package-documentation",
    "optional-semicolons",
    "orca-odin",
    "quine-in-odin",
    "read-a-file-line-by-line",
]
# ──────────────────────────────────────────────────────────────────────────────


def discover_via_index(index_url: str) -> list[str]:
    """Crawl the /news/ index page and extract newsletter links."""
    resp = fetch(index_url)
    if not resp or resp.status_code != 200:
        return []

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    found: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if not href:
            continue
        full = normalize_url(urljoin(index_url, str(href)))
        parsed = urlparse(full)
        if parsed.netloc == urlparse(BASE_URL).netloc and "/news/" in parsed.path:
            found.add(full)
    return sorted(found)


def discover_all() -> tuple[list[str], str]:
    """Chain the discovery strategies. Returns (urls, source)."""
    print("[*] Discovering newsletters...")

    urls = crawl_links(
        NEWS_INDEX,
        predicate=lambda _url, path: (
            "/news/" in path
            and normalize_url(NEWS_INDEX) != normalize_url(_url)
        ),
        follow_predicate=lambda path: False,
        max_pages=1,
        delay=REQUEST_DELAY,
    )
    if urls:
        print(f"  [+] {len(urls)} newsletters via crawl of /news/")
        return urls, "crawl"

    urls = discover_via_index(NEWS_INDEX)
    if urls:
        print(f"  [+] {len(urls)} newsletters via /news/ (direct parse)")
        return urls, "index"

    print("  [!] crawl failed, falling back to static list")
    urls = [f"{BASE_URL}/news/{slug}/" for slug in FALLBACK_ISSUES]
    print(f"  [+] {len(urls)} newsletters via fallback")
    return urls, "fallback"


def slug_from_url(url: str) -> str:
    """Extract the last path segment as a slug."""
    parts = [p for p in urlparse(url).path.split("/") if p]
    return parts[-1] if parts else "unknown"


def ensure_readme_updated() -> None:
    """Add scraper usage note to odin-knowledge-base/docs/newsletters/README.md if missing."""
    readme_path = OUT / "README.md"
    marker = "## How to scrape locally"
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        if "scrape-newsletters.py" not in content and marker in content:
            note = (
                "\nRun `python _Helpers/scripts/scrappers/scrape_newsletters.py` to scrape all newsletters "
                "(re-entrant, `--force` to rewrite, `--check` to dry-run).\n"
            )
            new_content = content.replace(
                marker + "\n",
                marker + "\n\n" + note,
            )
            readme_path.write_text(new_content, encoding="utf-8")
            print("  [+] Updated odin-knowledge-base/docs/newsletters/README.md with scraper info")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--force", action="store_true",
        help="Rewrite every .md even if it already exists (default: skip).",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: report what would be scraped, do not write anything.",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Odin Newsletter Scraper - full coverage")
    print("=" * 60)

    urls, source = discover_all()
    if not urls:
        print("[ERR] No newsletter discovered. Aborting.")
        return 1

    if args.check:
        print(f"\n[*] DRY-RUN: {len(urls)} newsletters would be scraped (source: {source})")
        for i, url in enumerate(urls, 1):
            slug = slug_from_url(url)
            out_path = OUT / f"{slug}.md"
            status = "[SKIP already present]" if (out_path.exists() and out_path.stat().st_size > 0) else "[WOULD SCRAPE]"
            print(f"  [{i:>2}/{len(urls)}] {slug}  {status}")
        return 0

    print(f"\n[*] Scraping {len(urls)} newsletters (source: {source}, "
            f"{'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, url in enumerate(urls, 1):
        slug = slug_from_url(url)
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

    ensure_readme_updated()

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(urls)} targeted newsletters ({source})")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
