#!/usr/bin/env python3
"""
_Helpers/scripts/scrappers/download_gists.py - Download public GitHub gists from awesome-odin.md.

Parses odin-knowledge-base/docs/official/awesome-odin.md to find all gist.github.com URLs, downloads each gist via the public GitHub API, and saves the raw content to code/gists/{gist_id}.odin (or .md for markdown files).

Re-entrant: skips already-downloaded gists unless --force.
--check: dry-run, lists gists that would be downloaded, exits 0.

Usage:
    python _Helpers/scripts/scrappers/download_gists.py             # download missing gists
    python _Helpers/scripts/scrappers/download_gists.py --check     # dry-run: list what would be downloaded
    python _Helpers/scripts/scrappers/download_gists.py --force     # re-download all gists
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
AWESOME_MD = REPO_ROOT / "odin-knowledge-base" / "docs" / "official" / "awesome-odin.md"
GISTS_DIR = REPO_ROOT / "code" / "gists"
GISTS_README = GISTS_DIR / "README.md"

GIST_URL_RE = re.compile(r"https://gist\.github\.com/([^/]+)/([0-9a-fA-F]+)")

API_URL = "https://api.github.com/gists/{}"
USER_AGENT = "OdinRAG/1.0 (gist-downloader; Python-urllib)"
REQUEST_DELAY = 0.3


def parse_gist_urls(path: Path) -> list[tuple[str, str, str]]:
    """Return list of (full_url, owner, gist_id) tuples found in the Markdown file."""
    text = path.read_text(encoding="utf-8")
    seen: set[str] = set()
    results: list[tuple[str, str, str]] = []
    for match in GIST_URL_RE.finditer(text):
        owner = match.group(1)
        gist_id = match.group(2)
        full_url = match.group(0)
        if gist_id not in seen:
            seen.add(gist_id)
            results.append((full_url, owner, gist_id))
    return results


def existing_gist_mapping(gists_dir: Path) -> dict[str, Path]:
    """Build mapping of gist_id -> existing file Path by reading // Source: lines. This allows files to be renamed descriptively while still being matched by gist ID."""
    mapping: dict[str, Path] = {}
    if not gists_dir.is_dir():
        return mapping
    for p in gists_dir.iterdir():
        if p.suffix.lower() not in (".odin", ".md") or p.name == "README.md":
            continue
        try:
            first_line = p.read_text(encoding="utf-8").split("\n")[0]
            if "gist.github.com" not in first_line:
                continue
            import re
            m = re.search(r"github\.com/[^/]+/([a-f0-9]+)", first_line)
            if m:
                mapping[m.group(1)] = p
        except Exception:
            pass
    return mapping


def existing_gist_ids(gists_dir: Path) -> set[str]:
    """Return set of gist IDs already present (via Source: line detection). Kept for compatibility."""
    return set(existing_gist_mapping(gists_dir).keys())


def fetch_gist(gist_id: str) -> dict | None:
    """Fetch gist metadata from GitHub API. Returns parsed JSON or None on failure."""
    url = API_URL.format(gist_id)
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            if resp.status != 200:
                print(f"  [ERR] {url} -> HTTP {resp.status}")
                return None
            return json.loads(resp.read().decode("utf-8"))
    except URLError as exc:
        print(f"  [ERR] {url} -> {exc}")
        return None


def determine_extension(files: dict) -> str:
    """Determine the file extension (.odin or .md) from the gist files dict."""
    for fname in files:
        lower = fname.lower()
        if lower.endswith(".odin"):
            return ".odin"
        if lower.endswith(".md") or lower.endswith(".markdown"):
            return ".md"
    return ".odin"


def download_raw_content(raw_url: str) -> str | None:
    """Download raw file content. Returns text or None on failure."""
    req = Request(raw_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except URLError as exc:
        print(f"    [ERR] {raw_url} -> {exc}")
        return None


def download_one(full_url: str, _owner: str, gist_id: str, existing: dict[str, Path], force: bool) -> bool:
    """Download a single gist if not already present. When a gist is already present under a descriptive name (matched by Source: line), it is skipped entirely without overwriting to preserve the descriptive filename and comments."""
    if not force and gist_id in existing:
        print(f"  [SKIP] {gist_id} -> {existing[gist_id].name} (already present)")
        return True

    print(f"  [FETCH] {full_url}")
    gist = fetch_gist(gist_id)
    if gist is None:
        return False

    files = gist.get("files", {})
    if not files:
        print(f"    [WARN] gist {gist_id} has no files")
        return True

    ext = determine_extension(files)
    out_path = GISTS_DIR / f"{gist_id}{ext}"

    success = True
    for fname, finfo in files.items():
        raw_url = finfo.get("raw_url", "")
        if not raw_url:
            print(f"    [WARN] {fname}: no raw_url")
            continue
        content = download_raw_content(raw_url)
        if content is None:
            success = False
            continue

        source_line = f"// Source: {full_url}\n"
        if content.startswith("// Source:"):
            out_content = content
        else:
            out_content = source_line + content

        out_path.write_text(out_content, encoding="utf-8")
        print(f"    [OK] {out_path.name}")
        break

    return success


def update_readme(downloaded: list[tuple[str, str, str]], gists_dir: Path) -> None:  # noqa: ARG001
    """Append downloaded gists to the catalogue table in code/gists/README.md."""
    if not downloaded:
        return

    readme_path = GISTS_README
    if not readme_path.exists():
        print("  [WARN] code/gists/README.md not found, skipping update")
        return

    existing_text = readme_path.read_text(encoding="utf-8")
    new_entries: list[str] = []
    for full_url, owner, gist_id in downloaded:
        existing = existing_gist_mapping(GISTS_DIR)
        if gist_id in existing:
            local_file = f"`{existing[gist_id].name}`"
        else:
            ext = ".odin"
            for suffix in (".odin", ".md"):
                if (GISTS_DIR / f"{gist_id}{suffix}").exists():
                    ext = suffix
                    break
            local_file = f"`{gist_id}{ext}`"
        entry = f"| {local_file} | | {full_url} | no |"
        new_entries.append(entry)

    lines = existing_text.splitlines()
    new_lines: list[str] = []
    appended = False
    for line in lines:
        new_lines.append(line)
        if not appended and line.strip().startswith("| `box2d-raylib"):
            for entry in new_entries:
                new_lines.append(entry)
            appended = True

    if not appended:
        new_lines.extend(new_entries)

    readme_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  [+] Updated {readme_path.name} with {len(new_entries)} new entries")


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Download public GitHub gists from awesome-odin.md")
    parser.add_argument("--check", action="store_true", help="Dry-run: list gists that would be downloaded")
    parser.add_argument("--force", action="store_true", help="Re-download all gists even if already present")
    args = parser.parse_args(argv)

    if not AWESOME_MD.exists():
        print(f"[ERR] {AWESOME_MD} not found. Run scrape-official.py first.")
        return 1

    GISTS_DIR.mkdir(parents=True, exist_ok=True)

    gists = parse_gist_urls(AWESOME_MD)
    print(f"[*] Found {len(gists)} unique gist(s) in awesome-odin.md")

    if args.check:
        existing = set(existing_gist_mapping(GISTS_DIR).keys())
        to_download = [(url, owner, gid) for url, owner, gid in gists if args.force or gid not in existing]
        if to_download:
            print(f"\n[*] Would download {len(to_download)} gist(s):")
            for url, owner, gid in to_download:
                print(f"    {gid}  ({owner})  {url}")
        else:
            print("\n[*] All gists already present, nothing to download.")
        return 0

    existing_map = existing_gist_mapping(GISTS_DIR)
    existing = set(existing_map.keys())
    downloaded: list[tuple[str, str, str]] = []
    failed = skipped = 0

    for full_url, owner, gist_id in gists:
        was_skip = not args.force and gist_id in existing
        ok = download_one(full_url, owner, gist_id, existing_map, args.force)
        if not ok:
            failed += 1
        elif was_skip:
            skipped += 1
        else:
            downloaded.append((full_url, owner, gist_id))
        time.sleep(REQUEST_DELAY)

    if downloaded:
        update_readme(downloaded, GISTS_DIR)

    print(f"\n[*] {len(downloaded)} downloaded, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
