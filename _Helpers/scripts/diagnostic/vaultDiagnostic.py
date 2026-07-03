#!/usr/bin/env python3
"""_Helpers/scripts/diagnostic/vaultDiagnostic.py - Whole-vault diagnostic for OdinRAG.

Adapted from TerraBloom's `vaultDiagnostic.py` (H:/Sync/PKM_PROJECTS/TerraBloom/_Helpers/01_Diagnostic/vaultDiagnostic.py) for the OdinRAG layout. Walks the repo (default) or a custom source folder, and reports issues in four categories:

- ``filename`` - structural filename problems (e.g., forbidden chars, wrong README pattern).
- ``frontmatter`` - delegated to ``validateFrontmatter.check_file`` (8-field schema + auto-fix).
- ``content`` - H1 must match the filename (per AGENTS.md), no long dashes, no extra blank lines.
- ``system`` - files too large, unreadable, etc.

Usage:

    python _Helpers/scripts/diagnostic/vaultDiagnostic.py
    python _Helpers/scripts/diagnostic/vaultDiagnostic.py --source path/to/scan
    python _Helpers/scripts/diagnostic/vaultDiagnostic.py --fail-on-error
    python _Helpers/scripts/diagnostic/vaultDiagnostic.py --quiet

Exit codes:

    0 - no issues
    1 - issues found (no error)
    2 - tool error (missing config, bad args)

Cross-platform (Windows / Unix). Depends on PyYAML (delegated through ``validateFrontmatter``).
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

_DIAGNOSTIC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_DIAGNOSTIC_DIR))

from vaultConfigOdinRAG import (  # noqa: E402
    FRONTMATTER_RE,
    IGNORE_DIRS,
    IGNORE_FILES,
    LONG_DASH_PATTERN,
    MAX_RAG_FILE_SIZE,
    REPO_ROOT,
    cprint,
    extract_frontmatter,
    path_link,
    should_ignore_dir,
    should_ignore_file,
    should_validate,
)

import validateFrontmatter as vfm  # noqa: E402

REPO_ROOT_NAME = REPO_ROOT.name
H1_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
FS_UNSAFE_RE = re.compile(r'[<>:"/\\|?*]')
README_PATTERN = re.compile(r"^README - .+\.md$")
NNN_PREFIX_RE = re.compile(r"^\d{3}_")
NNN_SNAKE_RE = re.compile(r"^\d{3}_[a-z0-9_]+\.md$")


class VaultDiagnostic:
    """Walk the repo, classify issues per file, render a structured report."""

    def __init__(self) -> None:
        self.issues: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.files_scanned = 0
        self.files_skipped = 0
        self.files_with_issues = 0
        self.ignore_dirs_active = True
        self.ignore_files_active = True

    def log_issue(self, filepath: Path, category: str, message: str, line: int | None = None) -> None:
        entry: dict[str, Any] = {"file": filepath, "message": message}
        if line is not None:
            entry["line"] = line
        self.issues[category].append(entry)

    def check_filename(self, filepath: Path) -> None:
        name = filepath.name
        if not name.endswith(".md"):
            return

        if FS_UNSAFE_RE.search(name):
            forbidden = sorted(set(FS_UNSAFE_RE.findall(name)))
            self.log_issue(
                filepath,
                "filename",
                f"Filename contains forbidden chars ({''.join(forbidden)}): '{name}'",
            )

        if name.lower().startswith("readme"):
            return

        if not NNN_PREFIX_RE.match(name):
            return

        if not NNN_SNAKE_RE.match(name):
            self.log_issue(
                filepath,
                "filename",
                f"Filename '{name}' starts with NNN_ but does not follow NNN_snake_case.md "
                f"(allowed chars: lowercase letters, digits, underscores)",
            )

    def check_content(self, filepath: Path, full_content: str) -> None:
        h1_match = H1_RE.search(full_content)
        if not h1_match:
            self.log_issue(
                filepath,
                "content",
                "No H1 title found in file (Markdown best practice: every file should start with '# Title')",
            )
            return

        h1_title = h1_match.group(1).strip()
        h1_line_num = full_content[:h1_match.start()].count("\n") + 1

        if NNN_PREFIX_RE.match(filepath.name) and h1_title != filepath.stem:
            self.log_issue(
                filepath,
                "content",
                f"H1 title '{h1_title}' does not match filename '{filepath.stem}' (per AGENTS.md: "
                f"NNN_-prefixed files must have an exact-match H1)",
                line=h1_line_num,
            )

        body_after_h1 = full_content[h1_match.end():]
        for m in LONG_DASH_PATTERN.finditer(body_after_h1):
            line_no = body_after_h1[:m.start()].count("\n") + h1_line_num + 1
            self.log_issue(
                filepath,
                "content",
                f"Long dash character found ({m.group(0)!r}); replace with ASCII '-' per AGENTS.md",
                line=line_no,
            )

        fm_match = FRONTMATTER_RE.match(full_content)
        if fm_match:
            body = full_content[fm_match.end():]
            trailing_blank = re.search(r"\n\n\n+", body)
            if trailing_blank:
                line_no = body[:trailing_blank.start()].count("\n") + 1
                self.log_issue(
                    filepath,
                    "content",
                    "Multiple consecutive blank lines detected (MD012 no-multiple-blanks)",
                    line=line_no,
                )

    def check_frontmatter(self, filepath: Path) -> None:
        if not should_validate(filepath):
            return
        try:
            errors, warnings, info = vfm.check_file(filepath, do_content_check=False)
        except Exception as exc:
            self.log_issue(
                filepath,
                "frontmatter",
                f"check_file raised an exception: {exc}",
            )
            return
        for err in errors:
            self.log_issue(filepath, "frontmatter", err)
        for warn in warnings:
            self.log_issue(filepath, "frontmatter", f"(warn) {warn}")

    def scan(self, root: Path, *, ignore_dirs: bool = False, ignore_files: bool = False) -> None:
        cprint(f"[scan] root: {root}", "CYAN")
        self.ignore_dirs_active = ignore_dirs
        self.ignore_files_active = ignore_files
        for path in sorted(root.rglob("*.md")):
            if not path.is_file():
                continue
            if ignore_dirs and should_ignore_dir(path):
                self.files_skipped += 1
                continue
            if ignore_files and should_ignore_file(path):
                self.files_skipped += 1
                continue
            self.files_scanned += 1
            try:
                size = path.stat().st_size
                if size > MAX_RAG_FILE_SIZE:
                    self.log_issue(
                        path,
                        "system",
                        f"File too large ({size / 1024 / 1024:.1f}MB > {MAX_RAG_FILE_SIZE / 1024 / 1024:.0f}MB), skipping body analysis.",
                    )
                    continue
            except OSError:
                self.log_issue(path, "system", "Cannot stat file")
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                self.log_issue(path, "system", f"Cannot read file: {exc}")
                continue

            self.check_filename(path)
            self.check_content(path, text)
            self.check_frontmatter(path)

    def print_report(self) -> None:
        cprint("", "CYAN")
        cprint("=" * 60, "CYAN", bold=True)
        cprint("OdinRAG vault diagnostic report", "CYAN", bold=True)
        cprint(f"  Files scanned : {self.files_scanned}", "CYAN")
        cprint(
            f"  Files skipped : {self.files_skipped} (dirs={'on' if self.ignore_dirs_active else 'off'}, files={'on' if self.ignore_files_active else 'off'})",
            "CYAN",
        )

        total = sum(len(v) for v in self.issues.values())
        cprint(f"  Total issues  : {total}", "RED" if total else "GREEN", bold=bool(total))

        if total == 0:
            cprint("\nNo issues found. Vault is coherent.", "GREEN", bold=True)
            return

        for category in sorted(self.issues.keys()):
            entries = self.issues[category]
            cprint(f"\n--- {category.upper()} ({len(entries)}) ---", "YELLOW", bold=True)
            by_file: dict[Path, list[dict[str, Any]]] = defaultdict(list)
            for entry in entries:
                by_file[entry["file"]].append(entry)
            for filepath in sorted(by_file.keys()):
                file_issues = by_file[filepath]
                rel = filepath
                try:
                    rel = filepath.resolve().relative_to(REPO_ROOT)
                except ValueError:
                    pass
                cprint(f"  {path_link(rel)}:", "CYAN", bold=True)
                for issue in file_issues:
                    line_suffix = f":{issue['line']}" if "line" in issue else ""
                    cprint(f"    [ ] {issue['message']}{line_suffix}", "RED" if category == "frontmatter" else "YELLOW")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vaultDiagnostic.py",
        description="Whole-vault diagnostic for OdinRAG (filename + frontmatter + content).",
    )
    parser.add_argument(
        "-s",
        "--source",
        default=str(REPO_ROOT),
        help=f"Root folder to scan (default: {REPO_ROOT}).",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Exit non-zero (2) if any frontmatter error is found.",
    )
    parser.add_argument(
        "--ignore-dirs",
        action="store_true",
        default=True,
        help=(
            "Skip files in folders listed in vaultConfigOdinRAG.IGNORE_DIRS (.git, _Private, code/vendored templates, odin-knowledge-base/courses, ...). Default: True (skip ignored directories)."
        ),
    )
    parser.add_argument(
        "--ignore-files",
        action="store_true",
        default=True,
        help=(
            "Skip files whose basename is listed in vaultConfigOdinRAG.IGNORE_FILES (README.md, .gitignore, ...). Default: True (ignore specified files)."
        ),
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress messages on stderr.",
    )
    args = parser.parse_args(argv)

    root = Path(args.source).resolve()
    if not root.is_dir():
        print(f"[ERR] source is not a directory: {root}", file=sys.stderr)
        return 2

    if not args.ignore_dirs and not args.ignore_files:
        cprint(
            "[warn] Neither --ignore-dirs nor --ignore-files is set; the scan will walk every .md "
            "file under the source directory (including .git/, node_modules/, _Private/). "
            "Pass --ignore-dirs and/or --ignore-files to apply the curated skip lists.",
            "YELLOW",
            bold=True,
        )

    diag = VaultDiagnostic()
    try:
        diag.scan(
            root,
            ignore_dirs=args.ignore_dirs,
            ignore_files=args.ignore_files,
        )
    except Exception as exc:
        print(f"[ERR] scan failed: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        diag.print_report()
    else:
        diag.print_report()

    total_issues = sum(len(v) for v in diag.issues.values())
    frontmatter_errors = len(diag.issues.get("frontmatter", []))

    if frontmatter_errors > 0 and args.fail_on_error:
        return 2
    if total_issues > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
