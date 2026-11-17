#!/usr/bin/env python3
"""_Helpers/scripts/fixes/add_kb_frontmatter.py - Inject minimal YAML frontmatter into KB docs.

Walks `odin-knowledge-base/docs/` (skipping `odin-book/`, `README.md`, and files that
already have YAML frontmatter) and injects standardized frontmatter (`title`, optional `date`,
optional `source`, `tags`, `type`, `status`).

Usage:
    python _Helpers/scripts/fixes/add_kb_frontmatter.py --check   # dry-run, exit 1 if any missing
    python _Helpers/scripts/fixes/add_kb_frontmatter.py --apply   # inject frontmatter in place
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.kb_frontmatter import ensure_kb_frontmatter, has_frontmatter  # noqa: E402

DEFAULT_DOCS_DIR = ROOT_DIR / "odin-knowledge-base" / "docs"
SKIP_DIR_NAMES = frozenset({"odin-book"})
SKIP_FILENAMES = frozenset({"README.md", "INDEX.md"})
_DESCRIPTION = "Inject minimal YAML frontmatter into scraped KB Markdown files."


def iter_kb_targets(docs_dir: Path) -> list[Path]:
    """Return sorted Markdown files under `docs_dir` eligible for frontmatter."""
    if not docs_dir.exists():
        return []
    targets: list[Path] = []
    for path in sorted(docs_dir.rglob("*.md")):
        if not path.is_file():
            continue
        if path.name in SKIP_FILENAMES:
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(docs_dir).parts):
            continue
        targets.append(path)
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Dry-run: exit 1 if any target file lacks frontmatter.")
    mode.add_argument("--apply", action="store_true", help="Write generated frontmatter to files lacking one.")
    parser.add_argument("--path", default=str(DEFAULT_DOCS_DIR), help="Target directory (default: odin-knowledge-base/docs).")
    args = parser.parse_args(argv)

    docs_dir = Path(args.path)
    if not docs_dir.exists():
        print(f"[FAIL] Target directory not found: {docs_dir}", file=sys.stderr)
        return 2

    targets = iter_kb_targets(docs_dir)
    missing: list[Path] = []
    updated = 0

    for path in targets:
        raw = path.read_text(encoding="utf-8")
        if has_frontmatter(raw):
            continue
        missing.append(path)
        if args.apply:
            new_text, changed = ensure_kb_frontmatter(raw, file_path=path, docs_root=DEFAULT_DOCS_DIR)
            if changed:
                path.write_text(new_text, encoding="utf-8", newline="\n")
                updated += 1
                print(f"[+] {path.relative_to(ROOT_DIR)}")

    if args.apply:
        print(f"[+] Updated {updated}/{len(targets)} file(s) with YAML frontmatter.")
        return 0

    if missing:
        print(f"[CHECK] {len(missing)}/{len(targets)} KB file(s) missing YAML frontmatter:")
        for p in missing[:15]:
            print(f"  - {p.relative_to(ROOT_DIR)}")
        if len(missing) > 15:
            print(f"  ... ({len(missing) - 15} more)")
        return 1 if args.check else 0

    print(f"[OK] All {len(targets)} KB file(s) already have YAML frontmatter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
