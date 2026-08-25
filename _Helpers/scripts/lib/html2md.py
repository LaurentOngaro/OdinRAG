"""HTML->Markdown conversion for doc scrapers.

Exposes a single function `scrape_to_markdown(url, output_path, source_url)`
that:
1. downloads the page,
2. extracts the main content (`<article>` / `<main>` / `<body>`),
3. strips navigation/script/style/aside/footer blocks,
4. converts to Markdown via `markdownify`,
5. appends a `>Source: <url>` footer.

Centralises the duplicated code from `scrape-official.py` and
`scrape-zylinski.py` (archived).
"""

from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify as md

from .http_client import fetch

# Tags to strip before conversion (page chrome, never content).
_NON_CONTENT_TAGS = ("nav", "script", "style", "aside", "footer")


def html_to_markdown(html_str: str) -> str:
    """Convert an HTML string into normalised Markdown.

    Args:
        html_str: raw HTML (typically the `<article>` / `<main>` of a page).

    Returns:
        Normalised Markdown: `heading_style=ATX`, `bullets='-'`, triple-newlines collapsed to double,
        `>Source: ...` footer added by `scrape_to_markdown`.
    """
    soup = BeautifulSoup(html_str, "html.parser")
    for tag in soup.find_all(list(_NON_CONTENT_TAGS)):
        tag.decompose()
    markdown = md(str(soup), heading_style="ATX", bullets="-")
    markdown = _collapse_blank_lines(markdown).strip()
    markdown = _tag_odin_code_blocks(markdown)
    return markdown


def scrape_to_markdown(
    url: str,
    output_path: str | Path,
    *,
    source_url: str | None = None,
    prefer_tags: tuple[str, ...] = ("article", "main"),
    format_odin: bool = True,
) -> bool:
    """Download `url`, convert to Markdown, write into `output_path`.

    Args:
        url         : URL to scrape.
        output_path : output file path (created/overwritten).
        source_url  : URL to display in the footer. Default: `url`.
        prefer_tags : tags to look for in order (`<article>` first, then `<main>`, then `<body>`).
        format_odin : run the written file through `odinfmt` (formats ```odin ... ``` blocks). Default: `True`.

    Returns:
        `True` on success, `False` on failure (non-200 HTTP, empty content).
    """
    source_url = source_url or url
    resp = fetch(url)
    if not resp or resp.status_code != 200:
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    container = next((soup.find(tag) for tag in prefer_tags if soup.find(tag)), soup.body, )
    if container is None:
        return False

    markdown = html_to_markdown(str(container))
    if not markdown:
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{markdown}\n\n>Source: {source_url}\n", encoding="utf-8")

    if format_odin and output_path.suffix.lower() == ".md":
        # Add _Helpers/scripts/ to sys.path so `from fixes.odin_format import …` works
        # (mirrors the convention used by every scraper in _Helpers/scripts/scrapers/).
        _scripts_dir = Path(__file__).resolve().parent.parent
        if str(_scripts_dir) not in sys.path:
            sys.path.insert(0, str(_scripts_dir))
        from fixes.odin_format import format_path_if_odin  # noqa: E402

        format_path_if_odin(output_path, silent=True)

    return True


def _collapse_blank_lines(text: str) -> str:
    import re
    return re.sub(r"\n{3,}", "\n\n", text)


def _tag_odin_code_blocks(text: str) -> str:
    """Replace bare opening ``` with ```odin so odinfmt formats the code blocks.

    Preserves blocks that already have a language tag and never touches closing fences.
    """
    lines: list[str] = []
    in_fence = False
    fence_delim = ""
    for line in text.splitlines():
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```"):
                in_fence = True
                fence_delim = "```"
                if stripped == "```":
                    indent = line[:line.find("`")]
                    lines.append(f"{indent}```odin")
                    continue
            elif stripped.startswith("~~~"):
                in_fence = True
                fence_delim = "~~~"
                if stripped == "~~~":
                    indent = line[:line.find("~")]
                    lines.append(f"{indent}~~~odin")
                    continue
        else:
            if stripped == fence_delim or (stripped.startswith(fence_delim) and stripped.replace(fence_delim[0], "") == ""):
                in_fence = False
                fence_delim = ""
        lines.append(line)
    return "\n".join(lines)


__all__ = ["html_to_markdown", "scrape_to_markdown"]
