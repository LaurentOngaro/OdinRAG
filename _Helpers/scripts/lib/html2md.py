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
    container = next(
        (soup.find(tag) for tag in prefer_tags if soup.find(tag)),
        soup.body,
    )
    if container is None:
        return False

    markdown = html_to_markdown(str(container))
    if not markdown:
        return False

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(f"{markdown}\n\n>Source: {source_url}\n", encoding="utf-8")

    if format_odin and output_path.suffix.lower() == ".md":
        # Add _Helpers/scripts/fixes/ + repo root to sys.path so that odin_format can import _Helpers.scripts.lib.user_config.
        _scripts_fixes_dir = Path(__file__).resolve().parents[3] / "_Helpers" / "scripts" / "fixes"
        _repo_root = Path(__file__).resolve().parents[3]
        sys.path.insert(0, str(_scripts_fixes_dir))
        sys.path.insert(0, str(_repo_root))

        from _Helpers.scripts.fixes.odin_format import (  # noqa: E402
            ODINFMT_EXE,
            ODINFMT_CONFIG,
            MAX_FILE_BYTES,
            format_path_if_odin,
        )

        format_path_if_odin(output_path, silent=True)

    return True


def _collapse_blank_lines(text: str) -> str:
    import re
    return re.sub(r"\n{3,}", "\n\n", text)


def _tag_odin_code_blocks(text: str) -> str:
    """Replace bare ``` with ```odin so odinfmt formats the code blocks. Preserves blocks that already have a language tag."""
    import re
    return re.sub(r"```\s*\n", "```odin\n", text)


__all__ = ["html_to_markdown", "scrape_to_markdown"]
