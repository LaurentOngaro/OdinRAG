#!/usr/bin/env python3
"""
_Helpers/scrape-gingerbill.py - Scrape gingerbill.org articles via RSS.
[Re-entrant: skip if <slug>.md already exists; --force to rewrite]

Fetches ALL articles from the https://www.gingerbill.org/article/ RSS feed and converts them into Markdown under docs/gingerbill/.

Usage:
    python _Helpers/scrape-gingerbill.py            # skip if already exported (re-entrant)
    python _Helpers/scrape-gingerbill.py --force    # force full rewrite
    python _Helpers/scrape-gingerbill.py --check    # dry-run, list what would be scraped

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery: RSS feed only (https://www.gingerbill.org/article/index.xml).
The feed is comprehensive, containing all articles since 2015.

Output:
    docs/gingerbill/<slug>.md (one file per article, with footer ">Source: <url>")

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless ``--force``.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).
    - ``--check`` dry-run lists articles without downloading.

Exit codes:
    0   full success
    1   no article discovered (RSS feed unavailable or empty)
    2   partial success (at least one page failed)
"""
import argparse
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import (  # noqa: E402
    fetch,
    normalize_url,
)
from lib.html2md import scrape_to_markdown  # noqa: E402

_DESCRIPTION = "Ginger Bill blog scraper (gingerbill.org) - re-entrant via RSS, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parent.parent / "docs" / "gingerbill"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://www.gingerbill.org"
RSS_URL = f"{BASE_URL}/article/index.xml"

REQUEST_DELAY = 0.5
# ──────────────────────────────────────────────────────────────────────────────


class Article(NamedTuple):
    url: str
    title: str
    date: str


def discover_via_rss_extended(rss_url: str) -> list[Article]:
    """Parse RSS feed, return articles with title and date."""
    resp = fetch(rss_url)
    if not resp or resp.status_code != 200:
        return []

    articles: list[Article] = []
    try:
        root = ET.fromstring(resp.text)
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            date_el = item.find("pubDate")
            if link_el is None or not link_el.text:
                continue
            url = normalize_url(link_el.text.strip())
            if not url.startswith(f"{BASE_URL}/article/"):
                continue
            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            date = _parse_pub_date(date_el.text) if date_el is not None and date_el.text else ""
            articles.append(Article(url=url, title=title, date=date))
    except ET.ParseError as exc:
        print(f"  [WARN] RSS parse error: {exc}")
        return []
    return articles


def _parse_pub_date(date_str: str) -> str:
    """Parse RFC 2822 pubDate into ISO 8601 date string."""
    try:
        dt = datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_str.strip(), "%a, %d %b %Y %H:%M:%S %Z")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return date_str.strip()


def extract_slug(url: str) -> str:
    """Extract the slug from a gingerbill.org article URL.

    >>> extract_slug("https://www.gingerbill.org/article/2026/05/13/aesthetic-namespacing/")
    'aesthetic-namespacing'
    """
    parts = [p for p in url.rstrip("/").split("/") if p]
    return parts[-1] if parts else "unknown"


def generate_readme(articles: list[Article]) -> None:
    """Write or update docs/gingerbill/README.md index."""
    readme_path = OUT / "README.md"
    lines = [
        "# docs/gingerbill/ - public index of gingerbill.org content",
        "",
        "> This folder is the **public landing** for the Ginger Bill (`gingerbill.org`) content.",
        "> The scraped articles themselves are **not** redistributed in this repo - see",
        "> [`../../SOURCES.md`](../../SOURCES.md) for licensing and how to obtain them legally on your own.",
        "",
        "## What's here",
        "",
        "Only `README.md` (this file). The actual blog articles (`*.md` per post) are excluded",
        "from the public repo by design (see the `COPYRIGHTED SCRAPED CONTENT` section of the root `.gitignore`).",
        "",
        "## How to populate this locally",
        "",
        "If you want the full articles on your machine:",
        "",
        "1. Read [`../../SOURCES.md`](../../SOURCES.md) for licensing.",
        "2. Authenticate nothing - `gingerbill.org` is public.",
        "3. Run:",
        "",
        "   ```bash",
        "   python _Helpers/scrape-gingerbill.py            # re-entrant: skip already scraped",
        "   python _Helpers/scrape-gingerbill.py --force    # force re-write",
        "   ```",
        "",
        "   Output (local only): 40+ files at the root of this folder, one per blog post,",
        "   discovered via RSS.",
        "",
        "## What topics are covered",
        "",
        "Articles that the scraper can pull (specific count depends on your local run):",
        "",
    ]

    if articles:
        for a in articles:
            safe_title = _escape_link_text(a.title)
            date_label = f" ({a.date})" if a.date else ""
            lines.append(f"- **{safe_title}**{date_label} - {a.url}")
    else:
        lines.append("_Run the scraper to populate this list._")

    lines += [
        "",
        "## See also",
        "",
        "- [`../official/`](../official/) - Odin official docs (public, included)",
        "- [`../karl_zylinski/`](../karl_zylinski/) - Karl Zylinski blog index",
        "- [`../newsletters/`](../newsletters/) - Odin newsletters index",
        "- [`../../SOURCES.md`](../../SOURCES.md) - source procurement guide",
        "- [`../../_Helpers/docs/002_How MiniMax-M3 is used in this repository.md`](../../_Helpers/docs/002_How MiniMax-M3 is used in this repository.md) - how MiniMax-M3 powers this repo",
        "",
    ]

    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[+] README.md written -> {readme_path}")


def _escape_link_text(text: str) -> str:
    """Escape pipe and bracket characters for markdown link text."""
    return text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "--force", action="store_true",
        help="Rewrite every .md even if it already exists (default: skip).",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: list articles that would be scraped, exit 0.",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Ginger Bill Blog Scraper - RSS coverage")
    print("=" * 60)

    articles = discover_via_rss_extended(RSS_URL)
    if not articles:
        print("[ERR] No article discovered via RSS. Aborting.")
        return 1

    print(f"\n[*] Discovered {len(articles)} articles via RSS")

    if args.check:
        print("[*] --check: listing articles (dry-run)\n")
        for i, a in enumerate(articles, 1):
            slug = extract_slug(a.url)
            out_path = OUT / f"{slug}.md"
            status = "exists" if (out_path.exists() and out_path.stat().st_size > 0) else "would scrape"
            print(f"  [{i:>2}/{len(articles)}] {slug}  [{status}]")
        print(f"\n[*] Would scrape {sum(1 for a in articles if not ((OUT / f'{extract_slug(a.url)}.md').exists() and (OUT / f'{extract_slug(a.url)}.md').stat().st_size > 0))} new articles")
        return 0

    print(f"\n[*] Scraping {len(articles)} articles ({'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, a in enumerate(articles, 1):
        slug = extract_slug(a.url)
        out_path = OUT / f"{slug}.md"
        if not args.force and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  [{i:>2}/{len(articles)}] {slug}  [SKIP already present]")
            skipped += 1
            continue
        print(f"  [{i:>2}/{len(articles)}] {a.url}")
        if scrape_to_markdown(a.url, out_path):
            print(f"          [OK] {slug}.md")
            scraped += 1
        else:
            print(f"          [FAIL]")
            failed += 1
        time.sleep(REQUEST_DELAY)

    generate_readme(articles)

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(articles)} targeted articles (rss)")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
