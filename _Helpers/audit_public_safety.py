#!/usr/bin/env python
"""
audit_public_safety.py - Verify that the working tree does not contain any file that should NOT be published to the public GitHub repo.

Uses the same rules as .gitignore (COPYRIGHTED SCRAPED CONTENT section).

Usage:
    python _Helpers/audit_public_safety.py            # check (exit 0 if clean)
    python _Helpers/audit_public_safety.py --verbose  # list every tracked file

Exit codes:
    0 - clean (nothing copyrighted in the public tree)
    1 - at least one problematic file found
    2 - error (wrong cwd, git missing)

Designed to be hooked into a pre-push (future) or executed manually before each push to the public remote.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns interdits en public. DOIT rester synchro avec .gitignore
FORBIDDEN_PATTERNS = [
    ("odin-knowledge-base/courses/", "Skool courses (paywall)"),
    ("courses/programvideogames/", "Legacy Skool cours doublon"),
    ("docs/karl_zylinski/odin-book/", "Karl Zylinski ebook (paid)"),
    ("planning/daily/", "Daily planning personnel"),
    ("projects/devlog/", "Devlogs personnels"),
    ("_Raw/", "Captures brutes / one-shot"),
]


def git_ls_files() -> list[str]:
    """Return the list of files tracked by git (index + committed)."""
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [f for f in result.stdout.splitlines() if f]


def audit(verbose: bool = False) -> tuple[int, list[tuple[str, str]]]:
    tracked = git_ls_files()
    violations: list[tuple[str, str]] = []

    for path in tracked:
        for pattern, reason in FORBIDDEN_PATTERNS:
            # Match with both forward and backward slashes (Windows tolerance)
            path_normalized = path.replace("\\", "/")
            pattern_normalized = pattern.replace("\\", "/")
            if path_normalized.startswith(pattern_normalized):
                # Public-safety READMEs that document the source folder are allowed
                # to live alongside the copyrighted content. They're curated indexes,
                # not the scraped content itself.
                allowed_readmes = {
                    "docs/karl_zylinski/odin-book/README.md",
                }
                if path_normalized in allowed_readmes:
                    continue
                violations.append((path, reason))
                break

    if verbose:
        print(f"[audit] Tracked files scanned: {len(tracked)}")
        print(f"[audit] Violations:           {len(violations)}")
        for path, reason in violations:
            print(f"  [X] {path}  <-  {reason}")

    return len(violations), violations


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv or "-v" in argv

    count, violations = audit(verbose=verbose)

    if count == 0:
        print("[OK] Public safety audit: clean - no copyrighted content in the public set")
        return 0

    print(f"[FAIL] Public safety audit: {count} violation(s) found")
    print()
    print("These files would leak copyrighted/private content if pushed as-is.")
    print("Verify .gitignore is correct, then:")
    print("  git rm -r --cached <path>   # untrack without deleting local files")
    print()
    print("First 20 violations:")
    for path, reason in violations[:20]:
        print(f"  {path}  <-  {reason}")
    if len(violations) > 20:
        print(f"  ... ({len(violations) - 20} more)")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
