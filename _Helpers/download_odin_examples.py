#!/usr/bin/env python3
"""
_Helpers/download_odin_examples.py - Official Odin example files downloader
[Re-entrant: skip if .odin already present; --force to redownload]

Downloads additional official Odin example files (.odin) from the odin-lang/Odin GitHub repository into code/examples/.

Usage:
    python _Helpers/download_odin_examples.py             # download new files (re-entrant)
    python _Helpers/download_odin_examples.py --force     # force redownload all
    python _Helpers/download_odin_examples.py --check     # dry-run (report only, no writes)

Source: GitHub Contents API (public, no auth)
    - https://api.github.com/repos/odin-lang/Odin/contents/examples/demo

Only `demo.odin` is downloaded - the `all_*.odin` files are doc-generator import lists with no instructional value.

Prerequisites: Python 3.10+ (stdlib only: urllib, json, pathlib).

Output:
    code/examples/<name>.odin   (flattened from subdirs by prefix stripping)

Exit codes:
    0   full success (or --check dry-run complete)
    1   API error (no files discovered)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

_API_BASE = "https://api.github.com/repos/odin-lang/Odin/contents"
_API_PATHS: list[str] = [
    "examples/demo",
]
RAW_BASE = "https://raw.githubusercontent.com/odin-lang/Odin/master"

OUT_DIR = Path(__file__).resolve().parent.parent / "code" / "examples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REQUEST_DELAY = 0.3  # seconds between API calls (politeness)
_TIMEOUT = 15


def _api_fetch(path: str) -> list[dict] | None:
    """GET a GitHub Contents API path, return parsed JSON list or None on error."""
    url = f"{_API_BASE}/{path}"
    req = Request(url, headers={"User-Agent": "OdinRAG/1.0", "Accept": "application/vnd.github.v3+json"})
    try:
        with urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                return data
            return [data]
    except (URLError, json.JSONDecodeError, OSError) as exc:
        print(f"  [ERR] API {url}: {exc}")
        return None


def _discover_odin_files() -> list[dict]:
    """Walk all API paths and collect .odin file info dicts (deduplicated by path)."""
    seen: set[str] = set()
    result: list[dict] = []

    for api_path in _API_PATHS:
        entries = _api_fetch(api_path)
        if not entries:
            continue
        for entry in entries:
            if entry["type"] != "file":
                continue
            if not entry["name"].endswith(".odin"):
                continue
            if entry["path"] in seen:
                continue
            seen.add(entry["path"])
            result.append(entry)
        time.sleep(REQUEST_DELAY)

    return result


def _local_name(entry: dict) -> str:
    """Derive a flat filename from the API entry path.

    Strips the 'examples/' prefix and subdirectory names, keeping the original .odin filename. e.g.:
        examples/demo/demo.odin            -> demo.odin
        examples/all/all_main.odin         -> all_main.odin
        examples/all/sdl3/all_sdl3.odin    -> all_sdl3.odin
    """
    raw_path = entry["path"]
    return Path(raw_path).name


def _download_file(entry: dict) -> str | None:
    """Download a single .odin file via raw.githubusercontent.com.

    Returns the content string on success, None on failure.
    """
    url = f"{RAW_BASE}/{entry['path']}"
    req = Request(url, headers={"User-Agent": "OdinRAG/1.0"})
    try:
        with urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read().decode("utf-8")
    except (URLError, OSError) as exc:
        print(f"  [ERR] download {url}: {exc}")
        return None


def _generate_readme(files: list[str]) -> str:
    """Generate the README.md content from the list of present .odin filenames."""
    descriptions: dict[str, str] = {
        "demo.odin": "Exhaustive demo of every language feature",
    }

    lines = [
        "# Official Odin examples",
        "",
        "> `demo.odin` (2966 lines) is the **most exhaustive single-file example** of the Odin language.",
        "> It covers procedures, structs, unions, foreign imports, SIMD, streams, Vulkan, and more.",
        "",
        "## Source",
        "",
        "Official example files from the [odin-lang/Odin](https://github.com/odin-lang/Odin) repository.",
        "Downloaded via `_Helpers/download_odin_examples.py`.",
        "",
        "## Files",
        "",
        "| File | Lines | Description |",
        "| ---- | ----- | ----------- |",
    ]
    for fname in sorted(files):
        desc = descriptions.get(fname, "Odin example file")
        dest = OUT_DIR / fname
        line_count = "?" if not dest.exists() else str(len(dest.read_text(encoding="utf-8").splitlines()))
        lines.append(f"| `{fname}` | {line_count} | {desc} |")

    lines.append("")
    lines.append("> The `all_*.odin` files (import lists for the doc generator) were intentionally excluded "
                "-- they contain no instructional code, only `import` statements. "
                "See [`docs/official/overview.md`](../docs/official/overview.md) for the language overview.")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download official Odin example .odin files from GitHub into code/examples/.",
        epilog="Re-entrant: skips files already present. --force to redownload. --check for dry-run.",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Redownload every .odin file even if already present.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: list what would be downloaded/skipped, exit 0, never write.",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  Odin Examples Downloader - GitHub API")
    print("=" * 60)

    print("\n[*] Discovering .odin files via GitHub API...")
    entries = _discover_odin_files()
    if not entries:
        print("[ERR] No .odin files discovered. Check your network.")
        return 1
    print(f"  [+] {len(entries)} .odin file(s) found\n")

    if args.check:
        print("[*] --check: dry-run (no files will be written)\n")
        for entry in entries:
            fname = _local_name(entry)
            dest = OUT_DIR / fname
            status = "ALREADY PRESENT" if dest.exists() else "WOULD DOWNLOAD"
            print(f"  [{status}] {fname}  <{entry['download_url']}>")
        return 0

    downloaded = 0
    skipped = 0
    failed = 0

    for entry in entries:
        fname = _local_name(entry)
        dest = OUT_DIR / fname

        if not args.force and dest.exists():
            print(f"  [SKIP] {fname} - already present")
            skipped += 1
            continue

        print(f"  [FETCH] {fname} <- {entry['download_url']}")
        content = _download_file(entry)
        if content is None:
            failed += 1
            continue

        dest.write_text(content, encoding="utf-8")
        print(f"    [OK] {fname} ({len(content)} bytes)")
        downloaded += 1
        time.sleep(REQUEST_DELAY)

    # Update README.md
    present_files = sorted(
        p.name for p in OUT_DIR.glob("*.odin") if p.is_file()
    )
    readme_path = OUT_DIR / "README.md"
    new_readme = _generate_readme(present_files)

    if not args.force and readme_path.exists() and readme_path.read_text(encoding="utf-8") == new_readme:
        print(f"\n  [SKIP] README.md - unchanged")
    else:
        readme_path.write_text(new_readme, encoding="utf-8")
        print(f"\n  [OK] README.md updated")

    print("\n" + "=" * 60)
    print(f"  {downloaded} downloaded, {skipped} already present, {failed} failures")
    print(f"  Total: {len(entries)} .odin files discovered")
    print(f"  -> {OUT_DIR}")
    print("=" * 60)
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    sys.exit(main())
