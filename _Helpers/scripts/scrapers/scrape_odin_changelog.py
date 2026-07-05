#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/scrape_odin_changelog.py - Odin Changelog Scraper.

Fetches the N most recent Odin releases from the GitHub REST API (`https://api.github.com/repos/odin-lang/Odin/releases`) and writes them to `odin-knowledge-base/docs/official/changelog/`.

Two artefacts are produced:
    - one consolidated `odin_changelog.md` with all releases (newest first)
    - one file per release under `releases/<tag>.md` (idempotent: skip if the file is already present and the underlying release tag matches)

Usage:
    python _Helpers/scripts/scrapers/scrape_odin_changelog.py            # last 20 releases, skip if present
    python _Helpers/scripts/scrapers/scrape_odin_changelog.py --limit 50
    python _Helpers/scripts/scrapers/scrape_odin_changelog.py --force    # rewrite everything
    python _Helpers/scripts/scrapers/scrape_odin_changelog.py --check    # dry-run
    python _Helpers/scripts/scrapers/scrape_odin_changelog.py --include-prereleases

Prerequisites:
    pip install requests
    Optional: set the env var `GITHUB_TOKEN` to raise the rate limit from 60 to 5000 requests/hour.

Output:
    odin-knowledge-base/docs/official/changelog/odin_changelog.md
    odin-knowledge-base/docs/official/changelog/releases/<tag>.md

Exit codes:
    0   full success
    1   GitHub API error / rate-limited and no data
    2   partial success (at least one release failed)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

# Allow importing the `_Helpers/lib` package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.http_client import DEFAULT_HEADERS, DEFAULT_TIMEOUT, fetch  # noqa: E402

_DESCRIPTION = "Odin GitHub releases scraper (odin-lang/Odin)."

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = REPO_ROOT / "odin-knowledge-base" / "docs" / "official" / "changelog"
RELEASES_DIR = OUT_ROOT / "releases"

API_URL = "https://api.github.com/repos/odin-lang/Odin/releases"
DEFAULT_LIMIT = 20

# ─── Frontmatter template (aligned with `_Helpers/docs/003_yaml_frontmatter_conventions.md`) ──
FRONTMATTER_TMPL = """---
source: github-releases
repo: odin-lang/Odin
tag: {tag}
date: {date}
type: changelog
status: active
version: 1.0.0
lastUpdated: "{updated}"
updatedBy: "MiniMax-M3 (Kilo Code)"
tags: [OdinRAG, kb, source/official, changelog, odin]
---
"""


# ─── GitHub fetch ────────────────────────────────────────────────────────────
def _headers() -> dict[str, str]:
    """GitHub-aware headers, including optional auth token from env."""
    h = dict(DEFAULT_HEADERS)
    h["Accept"] = "application/vnd.github+json"
    h["X-GitHub-Api-Version"] = "2022-11-28"
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def fetch_releases(limit: int, include_prereleases: bool) -> list[dict[str, Any]]:
    """GET `releases?per_page=limit` and return parsed JSON list, newest first.

    `limit` is clamped to 100 (GitHub API hard cap per page).
    """
    per_page = max(1, min(100, limit))
    url = f"{API_URL}?per_page={per_page}"
    print(f"[*] GET {url}")
    resp = fetch(url, headers=_headers(), timeout=DEFAULT_TIMEOUT)
    if not resp:
        print("[ERR] no response (network error)")
        return []
    if resp.status_code != 200:
        print(f"[ERR] GitHub returned HTTP {resp.status_code}: {resp.text[:300]}")
        return []
    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        print(f"[ERR] invalid JSON: {exc}")
        return []
    if not isinstance(data, list):
        print(f"[ERR] unexpected payload type: {type(data).__name__}")
        return []
    if not include_prereleases:
        data = [r for r in data if not r.get("prerelease")]
    return data


# ─── Markdown rendering ──────────────────────────────────────────────────────
def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_release_md(release: dict[str, Any]) -> str:
    """Render one GitHub release as a standalone Markdown file."""
    tag = release.get("tag_name", "unknown")
    name = (release.get("name") or tag).strip()
    published = (release.get("published_at") or "")[:10] or "unknown"
    author = (release.get("author") or {}).get("login", "unknown")
    html_url = release.get("html_url", "")
    body = (release.get("body") or "").rstrip() + "\n"
    frontmatter = FRONTMATTER_TMPL.format(
        tag=tag, date=published, updated=_now(),
    )
    header = (
        f"# {name}\n\n"
        f"- **Tag**: `{tag}`\n"
        f"- **Published**: {published}\n"
        f"- **Author**: {author}\n"
        f"- **Source**: <{html_url}>\n\n"
        f"---\n\n"
    )
    return frontmatter + header + body


def render_consolidated(releases: list[dict[str, Any]]) -> str:
    """Render a consolidated file with every release (newest first)."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    head = FRONTMATTER_TMPL.format(
        tag="consolidated", date=today, updated=_now(),
    )
    head += (
        f"# Odin Changelog (consolidated, {len(releases)} releases)\n\n"
        f"> Generated from the [odin-lang/Odin releases]"
        f"(https://github.com/odin-lang/Odin/releases) feed on {today}.\n"
        f"> Re-run `python _Helpers/scripts/scrapers/scrape_odin_changelog.py` "
        f"to refresh.\n\n"
    )
    body_parts: list[str] = []
    for r in releases:
        tag = r.get("tag_name", "unknown")
        name = (r.get("name") or tag).strip()
        published = (r.get("published_at") or "")[:10] or "unknown"
        author = (r.get("author") or {}).get("login", "unknown")
        html_url = r.get("html_url", "")
        body_parts.append(
            f"## {tag} - {published}\n\n"
            f"**{name}** by {author} - <{html_url}>\n\n"
            f"{(r.get('body') or '').rstrip()}\n\n---\n\n"
        )
    return head + "".join(body_parts)


# ─── Per-release idempotence ─────────────────────────────────────────────────
def release_already_scraped(tag: str) -> bool:
    """A release is considered already scraped if its file exists AND its frontmatter `tag:` matches (cheap content sanity check).
    """
    path = RELEASES_DIR / f"{tag}.md"
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        head = path.read_text(encoding="utf-8")[:400]
    except OSError:
        return False
    return f"tag: {tag}" in head


# ─── Main ────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help=f"Max releases to fetch (default {DEFAULT_LIMIT}, capped at 100).")
    parser.add_argument("--force", action="store_true", help="Rewrite every release even if already present.")
    parser.add_argument("--check", action="store_true", help="Dry-run: report what would be fetched, do not write.")
    parser.add_argument("--include-prereleases", action="store_true", help="Include pre-release / dev-nightly releases.")
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Odin Changelog Scraper - github.com/odin-lang/Odin")
    print("=" * 60)

    releases = fetch_releases(args.limit, args.include_prereleases)
    if not releases:
        print("[ERR] no releases fetched")
        return 1
    print(f"  [+] {len(releases)} releases fetched")

    if args.check:
        print(f"\n[*] DRY-RUN: {len(releases)} releases")
        for i, r in enumerate(releases, 1):
            tag = r.get("tag_name", "unknown")
            already = release_already_scraped(tag)
            status = "SKIP already present" if (already and not args.force) else "WOULD WRITE"
            print(f"  [{i:>3}/{len(releases)}] {tag}  [{status}]")
        return 0

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    scraped = skipped = failed = 0
    for i, r in enumerate(releases, 1):
        tag = r.get("tag_name", "unknown")
        out_path = RELEASES_DIR / f"{tag}.md"
        if not args.force and release_already_scraped(tag):
            print(f"  [{i:>3}/{len(releases)}] {tag}  [SKIP already present]")
            skipped += 1
            continue
        try:
            content = render_release_md(r)
            out_path.write_text(content, encoding="utf-8")
            size = out_path.stat().st_size
            print(f"  [{i:>3}/{len(releases)}] {tag}  [OK] {size:,} bytes")
            scraped += 1
        except OSError as exc:
            print(f"  [{i:>3}/{len(releases)}] {tag}  [FAIL write: {exc}]")
            failed += 1

    consolidated_path = OUT_ROOT / "odin_changelog.md"
    try:
        consolidated_path.write_text(render_consolidated(releases), encoding="utf-8")
        print(f"  [+] consolidated -> {consolidated_path.name} "
                f"({consolidated_path.stat().st_size:,} bytes)")
    except OSError as exc:
        print(f"  [ERR] consolidated write failed: {exc}")
        failed += 1

    print("\n" + "=" * 60)
    print(f"  {scraped} new, {skipped} skipped, {failed} failures")
    print(f"  -> {OUT_ROOT}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
