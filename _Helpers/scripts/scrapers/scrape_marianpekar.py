#!/usr/bin/env python3
"""
_Helpers/scripts/scrapers/scrape_marianpekar.py - Blog Scraper (Marian Pekar)
[Re-entrant: skip if <slug>.md already exists; --force to rewrite]

Fetches the Odin-related articles from the https://marianpekar.com blog and converts
them into Markdown under odin-knowledge-base/docs/marianpekar/.

The blog hosts three long "from scratch" series written in Odin with raylib
(Software Renderer, Physics Engine, 2D Cloth Simulation) plus older tutorials
on Unreal Engine and Unity. By default **only the Odin articles** are kept; the
Unity/Unreal material is out of scope for this knowledge base (pass `--all` to
override).

Usage:
    python _Helpers/scripts/scrapers/scrape_marianpekar.py            # skip if already exported (re-entrant)
    python _Helpers/scripts/scrapers/scrape_marianpekar.py --force    # force full rewrite
    python _Helpers/scripts/scrapers/scrape_marianpekar.py --check    # dry-run, list what would be scraped
    python _Helpers/scripts/scrapers/scrape_marianpekar.py --all      # also scrape the Unity/Unreal posts

Prerequisites:
    pip install requests markdownify beautifulsoup4 lxml

Discovery strategy (most reliable to most fragile):
    1. RSS feed        (/rss)       - the feed lists every post with title + date
    2. Sitemap XML     (/sitemap.xml)
    3. Paginated crawl (/)           - the blog index links every /blog/<slug>

HTML quirks handled by this scraper (they are why `scrape_to_markdown` cannot be
used directly on this site):
    - There is no `<article>` / `<main>`: the body lives in `<div class="post-content">`.
    - The editor wraps the whole body in a stray `<p><html><head></head><body>...</body></html></p>`.
    - Syntax highlighting is server-rendered by highlight.js, so every code block is
        polluted with `<span class="hljs-...">` wrappers that must be unwrapped.
    - A "support my work" call-to-action block is appended to every post.

Output:
    odin-knowledge-base/docs/marianpekar/<slug>.md (one file per article, footer ">Source: <url>")

Behaviour:
    - Re-entrant: a .md already present (size > 0) is SKIPPED unless `--force`.
    - Delay between requests: REQUEST_DELAY = 0.5s (politeness).
    - Every ```odin block is formatted through odinfmt (via fixes.odin_format).

Exit codes:
    0   full success
    1   no article discovered (all strategies exhausted)
    2   partial success (at least one page failed)
"""

import argparse
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

# Allow importing the `_Helpers/scripts/` packages (lib, fixes).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup  # noqa: E402
from bs4.element import Tag  # noqa: E402

from lib.html2md import html_to_markdown  # noqa: E402
from lib.http_client import fetch, normalize_url  # noqa: E402

_DESCRIPTION = "Marian Pekar blog scraper (marianpekar.com) - Odin posts only, re-entrant via RSS, --force to rewrite."

# ─── CONFIG ───────────────────────────────────────────────────────────────────
OUT = Path(__file__).resolve().parents[3] / "odin-knowledge-base" / "docs" / "marianpekar"
OUT.mkdir(parents=True, exist_ok=True)

BASE_URL = "https://marianpekar.com"
RSS_URL = f"{BASE_URL}/rss"
SITEMAP_URL = f"{BASE_URL}/sitemap.xml"
BLOG_INDEX = f"{BASE_URL}/"
BLOG_PATH_PREFIX = "/blog/"

REQUEST_DELAY = 0.5

AUTHOR = "Marian Pekar"
ATTRIBUTION = f"> Author: {AUTHOR} - <{BASE_URL}>"
COPYRIGHT = (
    f"> (c) {AUTHOR}. The posts stay freely readable on the author's site; this local copy is"
    " credited in `SOURCES.md` at the repo root. Please link back to the original article."
)

# A post is considered Odin-related when the keyword appears in its slug or title.
# All 21 Odin posts of the site match ("software-renderer-in-odin-...",
# "physics-engine-in-odin-...", "2d-cloth-simulation-in-odin-with-raylib").
ODIN_KEYWORDS = ("odin", )

# Page chrome to drop: never part of the article body.
_CHROME_CLASSES = ("navbar", "footer", "support-my-work", "video-container", "color-scheme-toggle", )
_CHROME_TAGS = ("script", "style", "noscript")
# ──────────────────────────────────────────────────────────────────────────────


class Article(NamedTuple):
    """One blog post discovered on the site."""

    url: str
    title: str
    date: str


# ─── DISCOVERY ────────────────────────────────────────────────────────────────
def _parse_pub_date(date_str: str) -> str:
    """Parse an RFC 2822 pubDate into a short human-readable date.

    >>> _parse_pub_date("Wed, 23 Sep 2026 19:28:25 GMT")
    '23 September 2026'
    """
    raw = date_str.strip()
    # Some feeds emit an ordinal suffix on the day ("1st Oct 2026"): drop it.
    raw = re.sub(r"(\d{1,2})(st|nd|rd|th)\b", r"\1", raw)
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%-d %B %Y")
        except ValueError:
            continue
    return raw


def _is_odin(article: Article) -> bool:
    """True when the post slug or title mentions Odin."""
    haystack = f"{article.url} {article.title}".lower()
    return any(keyword in haystack for keyword in ODIN_KEYWORDS)


def discover_via_rss(rss_url: str) -> list[Article]:
    """Parse the RSS feed and return every /blog/ post (title + date)."""
    resp = fetch(rss_url)
    if not resp or resp.status_code != 200:
        return []

    articles: list[Article] = []
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as exc:
        print(f"  [WARN] RSS parse error: {exc}")
        return []

    for item in root.iter("item"):
        link_el = item.find("link")
        if link_el is None or not link_el.text:
            continue
        url = normalize_url(link_el.text.strip())
        if f"{BASE_URL}{BLOG_PATH_PREFIX}" not in url:
            continue
        title_el = item.find("title")
        title = (title_el.text or "").strip() if title_el is not None else ""
        date_el = item.find("pubDate")
        raw_date = (date_el.text or "").strip() if date_el is not None else ""
        date = _parse_pub_date(raw_date) if raw_date else ""
        articles.append(Article(url=url, title=title, date=date))
    return articles


def discover_via_sitemap(sitemap_url: str) -> list[Article]:
    """Parse sitemap.xml as an RSS fallback (titles and dates are unknown here)."""
    resp = fetch(sitemap_url)
    if not resp or resp.status_code != 200:
        return []
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as exc:
        print(f"  [WARN] sitemap parse error: {exc}")
        return []

    articles: list[Article] = []
    for loc in root.iter():
        if not loc.tag.endswith("loc"):
            continue
        url = normalize_url((loc.text or "").strip())
        if f"{BASE_URL}{BLOG_PATH_PREFIX}" not in url:
            continue
        articles.append(Article(url=url, title="", date=""))
    return articles


def discover_via_index(index_url: str) -> list[Article]:
    """Crawl the blog index and collect every /blog/<slug> link."""
    resp = fetch(index_url)
    if not resp or resp.status_code != 200:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    seen: set[str] = set()
    articles: list[Article] = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"])
        if not href.startswith(BLOG_PATH_PREFIX):
            continue
        url = normalize_url(f"{BASE_URL}{href}")
        if url in seen or not url.startswith(f"{BASE_URL}{BLOG_PATH_PREFIX}"):
            continue
        seen.add(url)
        articles.append(Article(url=url, title=anchor.get_text(strip=True), date=""))
    return articles


def discover_all() -> tuple[list[Article], str]:
    """Chain the discovery strategies. Returns (articles, source)."""
    print("[*] Discovering articles...")

    for name, articles in (
        ("rss", discover_via_rss(RSS_URL)), ("sitemap", discover_via_sitemap(SITEMAP_URL)), ("crawl", discover_via_index(BLOG_INDEX)),
    ):
        if articles:
            print(f"  [+] {len(articles)} articles via {name}")
            return articles, name

    return [], "none"


# ─── EXTRACTION ───────────────────────────────────────────────────────────────
def _clean_container(container: Tag, page_soup: BeautifulSoup) -> None:
    """Strip page chrome and editor artefacts from the post container, in place."""
    # The stray `<html><head></head><body>` wrapper emitted by the WYSIWYG editor:
    # unwrap it so the real block-level children are not nested inside a `<p>`.
    for wrapper in container.find_all(["html", "head", "body"]):
        wrapper.unwrap()

    for cls in _CHROME_CLASSES:
        for node in container.find_all(class_=cls):
            node.decompose()

    for tag in _CHROME_TAGS:
        for node in container.find_all(tag):
            node.decompose()

    # highlight.js spans are pure presentation: keep the text, drop the wrappers.
    for code in container.find_all("code"):
        for span in code.find_all("span"):
            span.unwrap()

    # Editor typo: `href="[https://..."` produces `[label]([https://...)` in Markdown.
    for anchor in container.find_all("a", href=True):
        href = str(anchor["href"])
        if href.startswith("[http"):
            anchor["href"] = href[1:]

    # Same fix on the whole page copy of the node (index pages share the helper).
    for anchor in page_soup.find_all("a", href=True):
        href = str(anchor["href"])
        if href.startswith("[http"):
            anchor["href"] = href[1:]


def extract_post(url: str, out_path: Path) -> bool:
    """Download `url`, convert the post body to Markdown, write `out_path`.

    Returns:
        `True` on success, `False` on a fetch failure or an empty body.
    """
    resp = fetch(url)
    if not resp or resp.status_code != 200:
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    container = (soup.find("div", class_="post-content") or soup.find("article") or soup.find("main") or soup.body)
    if container is None:
        return False

    # Title and date live in the page head; the body `<h1>` is dropped afterwards.
    title = ""
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        title = str(og_title["content"]).strip()
    heading = container.find("h1")
    if not title and heading is not None:
        title = heading.get_text(strip=True)
    if not title:
        title = out_path.stem

    date = ""
    note = container.find("p", class_="note")
    if note:
        date = note.get_text(strip=True)

    _clean_container(container, soup)

    body = html_to_markdown(str(container))
    if not body:
        return False

    # Drop the leading `<h1>` and the `date` line: they are re-emitted in the header.
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    if date and lines and lines[0].strip() == date:
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    body = "\n".join(lines).strip()

    header = [f"# {title}", ""]
    if date:
        header += [date, ""]
    footer = ["", ATTRIBUTION, COPYRIGHT, "", f">Source: {url}", ""]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(header) + "\n" + body + "\n" + "\n".join(footer), encoding="utf-8")

    _format_odin_blocks(out_path)
    return True


def _format_odin_blocks(out_path: Path) -> None:
    """Run odinfmt over every ```odin block of `out_path` (silent, best effort)."""
    try:
        from fixes.odin_format import format_path_if_odin  # noqa: PLC0415

        format_path_if_odin(out_path, silent=True)
    except Exception as exc:  # pragma: no cover - odinfmt is optional tooling
        print(f"  [WARN] odinfmt skipped for {out_path.name}: {exc}")


def extract_slug(url: str) -> str:
    """Extract the trailing slug from a blog URL.

    >>> extract_slug("https://marianpekar.com/blog/2d-cloth-simulation-in-odin-with-raylib")
    '2d-cloth-simulation-in-odin-with-raylib'
    """
    parts = [p for p in url.rstrip("/").split("/") if p and p != "blog"]
    return parts[-1] if parts else "unknown"


# ─── README ───────────────────────────────────────────────────────────────────
def _escape_link_text(text: str) -> str:
    """Escape pipe and bracket characters for Markdown link text."""
    return text.replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")


def generate_readme(articles: list[Article]) -> None:
    """Write the folder index at odin-knowledge-base/docs/marianpekar/README.md."""
    readme_path = OUT / "README.md"
    odin_posts = [a for a in articles if _is_odin(a)]
    other_posts = [a for a in articles if not _is_odin(a)]

    lines = [
        f"# odin-knowledge-base/docs/marianpekar/ - {AUTHOR} blog index", "",
        "> Technical blog mainly focused on building things from scratch in Odin (software renderer, physics engine, cloth simulation), with older tutorials covering Unreal Engine and Unity topics.",
        "", "## What's here", "", f"One file per Odin post, scraped from `https://{BASE_URL.removeprefix('https://')}/rss`.", "",
        f"- **Author**: {AUTHOR}", f"- **Upstream**: <{BASE_URL}>",
        f"- **Licence**: posts are (c) {AUTHOR}, free to read online. They are credited in [`../../SOURCES.md`](../../SOURCES.md); please link back to the original article.",
        "", "## Odin posts", "", f"{len(odin_posts)} posts covering two long multi-part series plus one standalone article.", "",
    ]

    for a in odin_posts:
        slug = extract_slug(a.url)
        date_label = f" - {a.date}" if a.date else ""
        lines.append(f"- [{_escape_link_text(a.title or slug)}](./{slug}.md){date_label}")

    lines += [
        "", "## Series covered", "", "| Series | Parts | Slug pattern |", "| --- | --- | --- |",
        "| Software Renderer in Odin from Scratch | 14 | `software-renderer-in-odin-from-scratch-part-*` |",
        "| Physics Engine in Odin from Scratch | 6 | `physics-engine-in-odin-from-scratch-part-*` |",
        "| 2D Cloth Simulation in Odin with raylib | 1 | `2d-cloth-simulation-in-odin-with-raylib` |", "", "## Out of scope", "",
        f"The scraper filters out the {len(other_posts)} older posts about Unreal Engine, Unity and tooling, which are not Odin-related:", "",
    ]

    for a in other_posts:
        slug = extract_slug(a.url)
        lines.append(f"- `{slug}` - <{a.url}>")

    lines += [
        "", "Run `python _Helpers/scripts/scrapers/scrape_marianpekar.py --all` to fetch them anyway.", "", "## How to repopulate locally", "",
        "```bash", "python _Helpers/scripts/scrapers/scrape_marianpekar.py            # re-entrant: skip already scraped",
        "python _Helpers/scripts/scrapers/scrape_marianpekar.py --check    # dry-run listing",
        "python _Helpers/scripts/scrapers/scrape_marianpekar.py --force    # force re-write", "```", "", "## See also", "",
        "- [`../karl_zylinski/`](../karl_zylinski/) - Karl Zylinski blog index", "- [`../gingerbill/`](../gingerbill/) - Ginger Bill blog index",
        "- [`../jakubtomsu/`](../jakubtomsu/) - Jakub Tomsu blog index", "- [`../../SOURCES.md`](../../SOURCES.md) - source procurement guide", "",
    ]

    readme_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[+] README.md written -> {readme_path}")


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument("--force", action="store_true", help="Rewrite every .md even if it already exists (default: skip).", )
    parser.add_argument("--check", action="store_true", help="Dry-run: list the posts that would be scraped, then exit 0.", )
    parser.add_argument("--all", action="store_true", help="Also scrape the non-Odin posts (Unity, Unreal Engine, tooling).", )
    args = parser.parse_args(argv)

    print("=" * 60)
    print(f"  Marian Pekar Blog Scraper - Odin{'+all' if args.all else ' only'}")
    print("=" * 60)

    discovered, source = discover_all()
    if not discovered:
        print("[ERR] No article discovered (RSS, sitemap and crawl all failed). Aborting.")
        return 1

    articles = discovered if args.all else [a for a in discovered if _is_odin(a)]
    skipped_by_filter = len(discovered) - len(articles)
    print(
        f"\n[*] {len(articles)} articles selected via {source}"
        f"{f' ({skipped_by_filter} non-Odin posts filtered out)' if skipped_by_filter else ''}"
    )

    todo: list[tuple[Article, Path]] = []
    for article in articles:
        out_path = OUT / f"{extract_slug(article.url)}.md"
        already_there = out_path.exists() and out_path.stat().st_size > 0
        todo.append((article, out_path))
        if already_there and not args.force:
            print(f"  - {out_path.stem}  [SKIP already present]")
        else:
            print(f"  - {out_path.stem}  [{'rewrite' if already_there else 'would scrape'}]")

    if args.check:
        pending = sum(1 for a, p in todo if args.force or not (p.exists() and p.stat().st_size > 0))
        print(f"\n[*] --check: dry-run done, {pending} article(s) would be scraped")
        return 0

    print(f"\n[*] Scraping {len(todo)} articles ({'force rewrite' if args.force else 'skip if present'})...")
    scraped = failed = skipped = 0
    for i, (article, out_path) in enumerate(todo, 1):
        slug = out_path.stem
        if not args.force and out_path.exists() and out_path.stat().st_size > 0:
            print(f"  [{i:>2}/{len(todo)}] {slug}  [SKIP already present]")
            skipped += 1
            continue
        print(f"  [{i:>2}/{len(todo)}] {article.url}")
        if extract_post(article.url, out_path):
            print(f"          [OK] {slug}.md")
            scraped += 1
        else:
            print("          [FAIL]")
            failed += 1
        time.sleep(REQUEST_DELAY)

    generate_readme(discovered)

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} already present, {failed} failures")
    print(f"  Total: {len(articles)} targeted articles ({source})")
    print(f"  -> {OUT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
