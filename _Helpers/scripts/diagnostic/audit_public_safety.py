#!/usr/bin/env python
"""
audit_public_safety.py - Verify that no forbidden content exists where it must not be.

Two scopes are checked by default:

1. Working tree (git ls-files) - the local committed state. A forbidden file here means `.gitignore` or `.git/info/exclude` is wrong.

2. The local `public` branch (git ls-tree -r refs/heads/public) - the sanitised tree that will actually be pushed to GitHub via `git push public public`.
    A forbidden file here means the filter-branch pipeline did not strip it.

A forbidden file in either scope is a leak that must be fixed before pushing.

Usage:
    python audit_public_safety.py                  # check both scopes (default)
    python audit_public_safety.py --scope tree     # only working tree
    python audit_public_safety.py --scope branch   # only public branch
    python audit_public_safety.py --verbose        # list every forbidden file

Exit codes:
    0 - clean (nothing forbidden in either scope)
    1 - at least one forbidden file found
    2 - error (wrong cwd, git missing, public branch missing for --scope branch)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_BRANCH = "refs/heads/public"

# Forbidden path prefixes. MUST stay in sync with .gitignore + .git/info/exclude. # Structure: (path_prefix, human-readable reason)
FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    ("_Private/", "All _Private/ content is local-only (never push)"),
    ("code/projects/PVG03_RPG/", "Personal Odin project (not part of the RAG)"),
    ("odin-knowledge-base/courses/", "Skool courses (paywall)"),
    ("odin-knowledge-base/docs/karl_zylinski/odin-book/", "Karl Zylinski ebook (paid)"),
]

# A small set of files that DESCRIBE a forbidden source folder (README, INDEX...) and are explicitly curated for the public repo.
# They live next to copyrighted content but never contain it themselves.
ALLOWED_READMES: set[str] = {
    "odin-knowledge-base/docs/karl_zylinski/odin-book/README.md",
}


def git_ls_files() -> list[str]:
    """Return the list of files tracked by git (working tree's committed state)."""
    return _git_lines("git", "ls-files")


def git_ls_branch(branch: str) -> list[str]:
    """Return the list of file paths present in the given branch's tree.

    Uses `git ls-tree -r --name-only <branch>` which lists files WITHOUT nstantiating them on disk.
    Safe to call even when the branch's treeiffers from the working tree.
    """
    return _git_lines("git", "ls-tree", "-r", "--name-only", branch)


def _git_lines(*args: str) -> list[str]:
    result = subprocess.run(
        list(args),
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def branch_exists(branch: str) -> bool:
    """Return True if the named branch ref resolves to a commit."""
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", branch],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    return result.returncode == 0


def find_violations(paths: list[str]) -> list[tuple[str, str]]:
    """Return the list of (path, reason) for any path matching a forbidden pattern."""
    violations: list[tuple[str, str]] = []
    for path in paths:
        normalized = path.replace("\\", "/")
        if normalized in ALLOWED_READMES:
            continue
        for prefix, reason in FORBIDDEN_PATTERNS:
            if normalized.startswith(prefix):
                violations.append((path, reason))
                break
    return violations


def audit_scope(label: str, paths: list[str], verbose: bool) -> list[tuple[str, str]]:
    """Audit a single scope (either 'tree' or 'branch'). Returns the violations."""
    violations = find_violations(paths)
    if verbose:
        print(f"[audit:{label}] Files scanned: {len(paths)}")
        print(f"[audit:{label}] Violations:   {len(violations)}")
        for path, reason in violations:
            print(f"  [X] {path}  <-  {reason}")
    return violations


def run(args: argparse.Namespace) -> int:
    scope = args.scope
    verbose = args.verbose

    all_violations: list[tuple[str, str, str]] = []  # (scope, path, reason)

    if scope in {"tree", "both"}:
        tracked = git_ls_files()
        if verbose:
            print(f"[scope:tree] {len(tracked)} tracked files")
        for path, reason in audit_scope("tree", tracked, verbose):
            all_violations.append(("tree", path, reason))

    if scope in {"branch", "both"}:
        if not branch_exists(PUBLIC_BRANCH):
            if scope == "branch":
                print(f"[FAIL] Public branch '{PUBLIC_BRANCH}' does not exist.")
                print("       Run refresh_public_branch.py first.")
                return 2
            print(f"[warn] '{PUBLIC_BRANCH}' missing, skipping branch scope")
        else:
            branch_files = git_ls_branch(PUBLIC_BRANCH)
            if verbose:
                print(f"[scope:branch:{PUBLIC_BRANCH}] {len(branch_files)} files")
            for path, reason in audit_scope(f"branch:{PUBLIC_BRANCH}", branch_files, verbose):
                all_violations.append((f"branch:{PUBLIC_BRANCH}", path, reason))

    if not all_violations:
        print(f"[OK] Public safety audit ({scope}): clean.")
        return 0

    print(f"[FAIL] Public safety audit ({scope}): {len(all_violations)} violation(s).")
    print("       These files must not reach the public remote.")
    print()
    if scope in {"branch", "both"}:
        print("Branch violations -> run refresh_public_branch.py to regenerate the public branch with the correct filter.")
        print()
    if scope in {"tree", "both"}:
        print("Tree violations   -> update .gitignore or .git/info/exclude then `git rm --cached <path>` and recommit.")
        print("(NOTE: tree violations are EXPECTED in the public/private split workflow,")
        print(" because main is supposed to carry _Private/ etc. Only block pushes if you")
        print(" used --scope both by mistake.)")
        print()
    for scope_name, path, reason in all_violations[:20]:
        print(f"  [{scope_name}] {path}  <-  {reason}")
    if len(all_violations) > 20:
        print(f"  ... ({len(all_violations) - 20} more)")
    return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="audit_public_safety.py",
        description="Verify that no forbidden content exists in the working tree or the public branch.",
    )
    parser.add_argument(
        "--scope",
        choices=["tree", "branch", "both"],
        default="branch",
        help=(
            "Which scope to audit. Default 'branch' (the local refs/heads/public branch, "
            "i.e. the tree that will be pushed to GitHub). Use 'tree' to verify the "
            "working-tree ignore config, or 'both' for a paranoid double check."
        ),
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="List every scanned file and every violation.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        # argparse already printed usage; propagate the exit code
        return exc.code if isinstance(exc.code, int) else 2

    try:
        return run(args)
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] git command failed: {exc.stderr or exc.stdout}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print("[ERROR] git is not installed or not on PATH", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
