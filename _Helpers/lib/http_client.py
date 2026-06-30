"""Shared HTTP utilities (fetch, sitemap, RSS, URLs).

Centralises:
- ``fetch(url)``                          - GET with timeout + error handling
- ``normalize_url(url)``                  - drop fragment / query / trailing slash
- ``discover_via_sitemap(sitemap_url, …)`` - parse sitemap.xml
- ``discover_via_rss(rss_url, …)``         - parse RSS feed (Hugo <link>)

All the shared code for ``scrape-official.py`` and ``scrape-zylinski.py``
(archived) lives here. ``scrape_skool.py`` only uses ``normalize_url`` (and
indirectly the User-Agent convention).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Callable
from urllib.parse import urljoin, urlparse

import requests

# ─── DEFAULTS ────────────────────────────────────────────────────────────────
DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (compatible; OdinRAG/1.0)",
}
DEFAULT_TIMEOUT: int = 30   # seconds
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


# ─── HTTP ───────────────────────────────────────────────────────────────────
def fetch(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> requests.Response | None:
    """GET with timeout. Returns ``None`` and prints the error on failure."""
    try:
        return requests.get(url, headers=headers or DEFAULT_HEADERS, timeout=timeout)
    except requests.RequestException as exc:
        print(f"  [ERR] fetch {url}: {exc}")
        return None


# ─── URLS ───────────────────────────────────────────────────────────────────
def normalize_url(url: str) -> str:
    """Drop fragment, query and trailing slash to deduplicate.

    >>> normalize_url("https://x/posts/foo/?utm=a#bar")
    'https://x/posts/foo'
    """
    return url.split("#")[0].split("?")[0].rstrip("/")


def path_to_filename(path: str, *, prefix_to_strip: str = "", ext: str = ".md") -> str:
    """Convert a URL path into a filename.

    >>> path_to_filename("/docs/install/linux/", "docs")
    'install-linux.md'
    """
    parts = [p for p in path.split("/") if p and p != prefix_to_strip]
    return ("-".join(parts) or "index") + ext


def slug_from_url(url: str, *, segment: str) -> str:
    """Extract the last URL segment after ``segment``.

    >>> slug_from_url("https://zylinski.se/posts/odin-sokol-web/", "posts")
    'odin-sokol-web'
    """
    parts = [p for p in urlparse(url).path.split("/") if p and p != segment]
    return parts[-1] if parts else "unknown"


# ─── SITEMAP / RSS ──────────────────────────────────────────────────────────
def discover_via_sitemap(
    sitemap_url: str,
    *,
    base_host: str,
    path_prefix: str,
    exclude_path: str | None = None,
) -> list[str]:
    """Parse sitemap.xml and return filtered URLs.

    Args:
        sitemap_url : full sitemap.xml URL.
        base_host   : host (e.g. ``"https://odin-lang.org"``) used as a filter.
        path_prefix : path prefix to keep (e.g. ``"/docs/"``).
        exclude_path: exact path to exclude (e.g. the ``/posts/`` index).
    """
    resp = fetch(sitemap_url)
    if not resp or resp.status_code != 200:
        return []
    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as exc:
        print(f"  [WARN] sitemap parse error: {exc}")
        return []

    urls: set[str] = set()
    for loc in root.findall(".//s:loc", SITEMAP_NS):
        url = normalize_url((loc.text or "").strip())
        if not url.startswith(f"{base_host}{path_prefix}"):
            continue
        if exclude_path and url == normalize_path_for_compare(exclude_path, base_host):
            continue
        urls.add(url)
    return sorted(urls)


def discover_via_rss(
    rss_url: str,
    *,
    must_contain: str,
    exclude_path: str | None = None,
) -> list[str]:
    """Parse an RSS feed (Hugo ``<link>`` inside ``<item>``) and filter.

    Args:
        rss_url      : feed URL.
        must_contain : substring each URL must contain (e.g. ``"/posts/"``).
        exclude_path : exact URL (normalised) to exclude.
    """
    resp = fetch(rss_url)
    if not resp or resp.status_code != 200:
        return []
    urls: set[str] = set()
    try:
        root = ET.fromstring(resp.text)
        for link in root.iter("link"):
            text = (link.text or "").strip()
            if must_contain not in text:
                continue
            norm = normalize_url(text)
            if exclude_path and norm == normalize_url(exclude_path):
                continue
            urls.add(norm)
    except ET.ParseError as exc:
        print(f"  [WARN] RSS parse error: {exc}")
    return sorted(urls)


def normalize_path_for_compare(path: str, base_host: str) -> str:
    """Helper: rebuild the canonical URL for a path for comparison."""
    if path.startswith("http"):
        return normalize_url(path)
    return normalize_url(f"{base_host.rstrip('/')}/{path.lstrip('/')}")


# ─── CRAWL ──────────────────────────────────────────────────────────────────
def crawl_links(
    start_url: str,
    *,
    predicate: Callable[[str, str], bool],
    follow_predicate: Callable[[str], bool] | None = None,
    max_pages: int = 20,
    delay: float = 0.0,
) -> list[str]:
    """BFS crawl from ``start_url``; collect links matching ``predicate``.

    Args:
        start_url       : starting URL.
        predicate       : ``predicate(full_url, parsed_path) -> bool``.
                          Returns ``True`` to add the URL to the result.
        follow_predicate: optional, ``follow_predicate(parsed_path) -> bool``.
                          If ``False``, the page is not re-crawled.
        max_pages       : safeguard against infinite loops.
        delay           : seconds between each request.
    """
    import time
    base_host = urlparse(start_url).netloc
    found: set[str] = set()
    next_urls: list[str] = [start_url]
    seen: set[str] = set()

    while next_urls and len(seen) < max_pages:
        page_url = next_urls.pop(0)
        if page_url in seen:
            continue
        seen.add(page_url)

        resp = fetch(page_url)
        if not resp or resp.status_code != 200:
            continue

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a.get("href")
            if not href:
                continue
            full = normalize_url(urljoin(page_url, str(href)))
            parsed = urlparse(full)
            if parsed.netloc != base_host:
                continue
            if predicate(full, parsed.path):
                found.add(full)
            elif follow_predicate and follow_predicate(parsed.path):
                next_urls.append(full)

        if delay:
            time.sleep(delay)

    return sorted(found)


__all__ = [
    "DEFAULT_HEADERS",
    "DEFAULT_TIMEOUT",
    "SITEMAP_NS",
    "fetch",
    "normalize_url",
    "path_to_filename",
    "slug_from_url",
    "discover_via_sitemap",
    "discover_via_rss",
    "crawl_links",
]
