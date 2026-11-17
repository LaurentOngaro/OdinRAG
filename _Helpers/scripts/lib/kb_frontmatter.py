"""_Helpers/scripts/lib/kb_frontmatter.py - Deterministic YAML frontmatter generator for scraped KB docs.

Shared by `_Helpers/scripts/fixes/add_kb_frontmatter.py` (retro-injection) and
`_Helpers/scripts/lib/html2md.py` / `scrape_marianpekar.py` (native injection on scrape).
Python stdlib-only.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

SOURCE_TAG_BY_DIR: dict[str, str] = {
    "gingerbill": "source/gingerbill",
    "jakubtomsu": "source/jakubtomsu",
    "karl_zylinski": "source/zylinski",
    "marianpekar": "source/marianpekar",
    "newsletters": "source/newsletters",
    "official": "source/official",
    "showcase": "source/showcase",
}

TOPIC_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("topic/allocator", re.compile(r"\b(?:allocator|arena|tracking_allocator|temp_allocator)\b", re.IGNORECASE)),
    ("topic/state-machine", re.compile(r"\b(?:state machine|fsm)\b", re.IGNORECASE)),
    ("topic/entity-system", re.compile(r"\b(?:ecs|entity system|handle-based|generational handle)\b", re.IGNORECASE)),
    ("topic/collision", re.compile(r"\b(?:collision|raycast|aabb|separating axis)\b", re.IGNORECASE)),
    ("topic/hot-reload", re.compile(r"\b(?:hot[- ]reload|dynlib)\b", re.IGNORECASE)),
    ("topic/rendering", re.compile(r"\b(?:software renderer|rasterization|shader|phong|sprite)\b", re.IGNORECASE)),
    ("topic/raylib", re.compile(r"\braylib\b", re.IGNORECASE)),
    ("topic/sokol", re.compile(r"\bsokol\b", re.IGNORECASE)),
    ("topic/dod", re.compile(r"\b(?:data[- ]oriented|soa|aos)\b", re.IGNORECASE)),
    ("topic/wasm", re.compile(r"\b(?:wasm|webassembly)\b", re.IGNORECASE)),
    ("topic/binding", re.compile(r"\b(?:foreign import|c-bindgen|bindgen|ffi)\b", re.IGNORECASE)),
)

_ISO_DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\b")
_MONTH_DATE_RE = re.compile(r"^([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\b")
_ORDINAL_DATE_RE = re.compile(r"^(\d{1,2})(?:st|nd|rd|th)\s+([A-Z][a-z]+\s+\d{4})\b")
_SOURCE_FOOTER_RE = re.compile(r"^>\s*Source:\s*(https?://\S+)", re.IGNORECASE | re.MULTILINE)
_HEADING_RE = re.compile(r"^#{1,2}\s+(.+)$")
_ANCHOR_SUFFIX_RE = re.compile(r"\s*\[#\]\(#[^)]+\)\s*$")


def has_frontmatter(text: str) -> bool:
    """Return True if `text` already begins with a YAML frontmatter block."""
    normalized = text.lstrip("\ufeff").replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return False
    end = normalized.find("\n---\n", 4)
    return end != -1


def infer_source_tag(file_path: Path, docs_root: Path | None = None) -> str | None:
    """Infer `source/<name>` tag from a path under `odin-knowledge-base/docs/<source>/`."""
    parts = file_path.resolve().parts
    if docs_root is not None:
        try:
            rel_parts = file_path.resolve().relative_to(docs_root.resolve()).parts
            if rel_parts:
                return SOURCE_TAG_BY_DIR.get(rel_parts[0])
        except ValueError:
            pass
    for idx, part in enumerate(parts):
        if part == "docs" and idx + 1 < len(parts):
            tag = SOURCE_TAG_BY_DIR.get(parts[idx + 1])
            if tag:
                return tag
    return None


def _clean_heading_text(raw: str) -> str:
    text = _ANCHOR_SUFFIX_RE.sub("", raw).strip()
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.replace("*", "").replace("`", "").strip()
    return text


def _extract_title(text: str, stem: str) -> str:
    for line in text.splitlines()[:40]:
        stripped = line.strip()
        m = _HEADING_RE.match(stripped)
        if m:
            cleaned = _clean_heading_text(m.group(1))
            if cleaned and cleaned.lower() not in ("contents", "table of contents"):
                return cleaned
    return stem.replace("-", " ").replace("_", " ").strip().title()


def _extract_date(text: str) -> str | None:
    for line in text.splitlines()[:15]:
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("!"):
            continue
        m_iso = _ISO_DATE_RE.match(s)
        if m_iso:
            return m_iso.group(1)
        m_mon = _MONTH_DATE_RE.match(s)
        if m_mon:
            try:
                return datetime.strptime(m_mon.group(1), "%B %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                pass
        m_ord = _ORDINAL_DATE_RE.match(s)
        if m_ord:
            cleaned = f"{m_ord.group(1)} {m_ord.group(2)}"
            try:
                return datetime.strptime(cleaned, "%d %B %Y").strftime("%Y-%m-%d")
            except ValueError:
                pass
    return None


def _extract_source_url(text: str) -> str | None:
    matches = _SOURCE_FOOTER_RE.findall(text)
    return matches[-1].strip() if matches else None


def _infer_topics(text: str, limit: int = 5) -> list[str]:
    topics: list[str] = []
    for tag, pattern in TOPIC_PATTERNS:
        if pattern.search(text):
            topics.append(tag)
            if len(topics) >= limit:
                break
    return topics


def _yaml_escape(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_kb_frontmatter(
    body: str,
    *,
    file_path: Path,
    source_tag: str | None = None,
    source_url: str | None = None,
    title: str | None = None,
    date_str: str | None = None,
    docs_root: Path | None = None,
) -> str:
    """Build a YAML frontmatter block for a scraped KB Markdown document."""
    resolved_title = title.strip() if title else _extract_title(body, file_path.stem)
    resolved_date = date_str.strip() if date_str else _extract_date(body)
    resolved_source_url = source_url.strip() if source_url else _extract_source_url(body)
    resolved_source_tag = source_tag or infer_source_tag(file_path, docs_root=docs_root)

    tags: list[str] = ["OdinRAG", "kb"]
    if resolved_source_tag:
        tags.append(resolved_source_tag)
    tags.extend(_infer_topics(f"{resolved_title}\n{body[:8000]}"))

    lines = [
        "---",
        f"title: {_yaml_escape(resolved_title)}",
    ]
    if resolved_date:
        lines.append(f"date: {resolved_date}")
    if resolved_source_url:
        lines.append(f"source: {_yaml_escape(resolved_source_url)}")
    lines.extend([
        f"tags: [{', '.join(tags)}]",
        "type: reference",
        "status: active",
        "---",
    ])
    return "\n".join(lines)


def ensure_kb_frontmatter(
    text: str,
    *,
    file_path: Path,
    source_tag: str | None = None,
    source_url: str | None = None,
    title: str | None = None,
    date_str: str | None = None,
    docs_root: Path | None = None,
) -> tuple[str, bool]:
    """Prepend YAML frontmatter if `text` does not already have one.

    Returns:
        `(new_text, changed)` where `changed` is `False` if frontmatter already existed.
    """
    if has_frontmatter(text):
        return text, False
    normalized = text.lstrip("\ufeff").replace("\r\n", "\n").lstrip("\n")
    fm = build_kb_frontmatter(
        normalized,
        file_path=file_path,
        source_tag=source_tag,
        source_url=source_url,
        title=title,
        date_str=date_str,
        docs_root=docs_root,
    )
    return f"{fm}\n\n{normalized}", True
