#!/usr/bin/env python
"""
refresh_public_branch.py - Regenerate the local `public` branch from `main`, with all personal paths filtered out via `git filter-branch`.

Idempotent: if `public` already represents a clean view of `main` (same tip, or just-empty content diff with nothing else), the script exits without doing anything.
Otherwise it rewrites `refs/heads/public` from `main`'s tip with the filter set below.

Why filter-branch and not subtree split:
    `git subtree split --prefix=.` returns `fatal: '.' does not exist` because `git subtree` requires a sub-directory under the repo root, not the root itself.
    `git filter-branch --index-filter` does the same "everything except X" job and works at the root. (Filter-branch is deprecated; long-term replacement is `git filter-repo`, see Section 3 of the French workflow doc.)

Usage:
    python refresh_public_branch.py            # refresh (no-op if already current)
    python refresh_public_branch.py --check    # dry-run: show what would happen
    python refresh_public_branch.py --force    # bypass idempotence check
    python refresh_public_branch.py --verify   # additionally run audit_public_safety

Exit codes:
    0 - public branch refreshed (or already current / no change)
    1 - public branch could not be refreshed (git error, etc.)
    2 - --verify requested and the refreshed branch still fails the safety audit
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
MAIN_BRANCH = "refs/heads/main"
PUBLIC_BRANCH = "refs/heads/public"

# Paths to STRIP from the public branch's tree.
# MUST stay in sync with _Helpers/docs/007_mixing_*.md (canonical reference) and with audit_public_safety.py FORBIDDEN_PATTERNS.
STRIP_RULES: list[str] = [
    "code/projects/PVG03_RPG",
    "_Private",
    "odin-knowledge-base/courses",
    "odin-knowledge-base/docs/karl_zylinski/odin-book",
]


def _git_capture(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {result.returncode}): "
            f"{result.stderr.strip() or result.stdout.strip()}"
        )
    return result.stdout


def rev(ref: str) -> str:
    """Return the short SHA for a ref, or '' if it does not exist."""
    try:
        out = _git_capture("rev-parse", "--verify", "--quiet", ref)
        return out.strip()[:12]
    except RuntimeError:
        return ""


def public_is_in_sync_with_main() -> tuple[bool, str]:
    """Return (in_sync, reason). A branch is 'in sync' when its tip equals main's tip.

    Note: this is the conservative check.
    A future improvement could diff the trees (to detect "public is older but content is identical"); for now we trust SHAs because filter-branch rewrites them on every change.
    """
    public_sha = rev(PUBLIC_BRANCH)
    main_sha = rev(MAIN_BRANCH)
    if not main_sha:
        return False, f"{MAIN_BRANCH} does not exist"
    if not public_sha:
        return False, f"{PUBLIC_BRANCH} does not exist"
    if public_sha == main_sha:
        return False, (
            "public SHA == main SHA: filter-branch was never run, or was reset. "
            "Run refresh_public_branch.py to actually generate the public branch."
        )
    # We can't cheaply prove the public branch is up-to-date without comparing trees.
    # Easier heuristic: the public branch is "in sync" when it contains the same commit graph as main (commits reachable from main that are also reachable from public). Otherwise it's stale.
    try:
        # `git merge-base --is-ancestor <main> <public>`: is main an ancestor of public?
        _git_capture("merge-base", "--is-ancestor", MAIN_BRANCH, PUBLIC_BRANCH)
        return True, (
            f"public ({public_sha}) already contains everything main ({main_sha})"
        )
    except RuntimeError:
        return False, f"public ({public_sha}) does not contain main ({main_sha})"


def build_filter_command() -> list[str]:
    """Return the index-filter expression passed to git filter-branch.

    Each STRIP_RULE triggers a `git rm --cached -r --ignore-unmatch <path>` so commits whose trees contained personal paths become empty (and then dropped by --prune-empty).
    """
    parts = ["git rm --cached -r --ignore-unmatch " + r for r in STRIP_RULES]
    return ["sh", "-c", " ; ".join(parts)]


def working_tree_is_dirty() -> tuple[bool, str]:
    """Return (dirty, summary). Filter-branch refuses to run against a dirty tree."""
    try:
        out = _git_capture("status", "--porcelain")
    except RuntimeError:
        return False, ""
    if out.strip():
        # `git status --porcelain` lists one file per line; show the first few.
        lines = [line for line in out.splitlines() if line][:5]
        return True, "\n".join(lines)
    return False, ""


def run_refresh(force: bool) -> tuple[bool, str]:
    """Actually regenerate the public branch. Returns (changed, human_log)."""
    main_sha = rev(MAIN_BRANCH)
    if not main_sha:
        return False, f"[FAIL] {MAIN_BRANCH} does not exist - nothing to refresh"

    # Filter-branch refuses to run with unstaged changes. Bail out clearly rather than silently stash (the user might have meaningful uncommitted work).
    dirty, sample = working_tree_is_dirty()
    if dirty:
        return False, (
            "[FAIL] working tree has unstaged changes; git filter-branch refuses to run.\n"
            f"First few dirty entries:\n  {sample.replace(chr(10), chr(10) + '  ')}\n"
            "Workaround: `git stash push -u -m 'wip'` then re-run, then `git stash pop`."
        )

    # Step 1: (re)create the public branch at main's tip.
    public_was_absent = not rev(PUBLIC_BRANCH)
    if public_was_absent:
        _git_capture("branch", "public", MAIN_BRANCH)
        log = f"[+] created {PUBLIC_BRANCH} at {main_sha}"
    else:
        # Use --force to overwrite even if the branch currently points at old commits.
        _git_capture("branch", "-f", PUBLIC_BRANCH, MAIN_BRANCH)
        log = f"[+] reset {PUBLIC_BRANCH} to {main_sha}"

    # Step 2: prune any existing filter-branch backup before re-running.
    try:
        _git_capture("update-ref", "-d", "refs/original/refs/heads/public")
    except RuntimeError:
        pass  # backup doesn't exist; nothing to do

    # Step 3: run filter-branch.
    shell_filter = " ; ".join(
        f"git rm --cached -r --ignore-unmatch {rule}" for rule in STRIP_RULES
    )
    cmd = [
        "filter-branch", "-f",
        "--index-filter", f"sh -c '{shell_filter}'",
        "--prune-empty",
        "--", PUBLIC_BRANCH,
    ]
    _git_capture(*cmd)

    # Step 4: clean up the backup filter-branch just created.
    try:
        _git_capture("update-ref", "-d", "refs/original/refs/heads/public")
    except RuntimeError:
        pass

    new_sha = rev(PUBLIC_BRANCH)
    if not new_sha or new_sha == main_sha:
        # filter-branch produced an empty diff (no personal content to strip).
        return False, f"{log}\n[OK] {PUBLIC_BRANCH} == {MAIN_BRANCH} (no personal content to strip)"
    return True, f"{log}\n[OK] {PUBLIC_BRANCH} rewritten: {main_sha} -> {new_sha}"


def run_verify() -> tuple[bool, str]:
    """Run audit_public_safety.py on the public branch. Returns (passed, log)."""
    audit_script = Path(__file__).resolve().parent / "audit_public_safety.py"
    if not audit_script.exists():
        return False, f"[FAIL] audit script not found: {audit_script}"

    if shutil.which("python") is None and shutil.which("python3") is None:
        return False, "[FAIL] python interpreter not on PATH"
    py = "python" if shutil.which("python") else "python3"

    result = subprocess.run(
        [py, str(audit_script), "--scope", "branch"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    log = (result.stdout or "") + (result.stderr or "")
    if result.returncode == 0:
        return True, "[OK] audit: public branch clean"
    return False, f"[FAIL] audit: exit {result.returncode}\n{log.strip()}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="refresh_public_branch.py",
        description="Regenerate the local 'public' branch from 'main' (with personal paths stripped).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: print what would happen, do not modify refs.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass idempotence check and always refresh.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After refresh, run audit_public_safety.py --scope branch to validate.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    in_sync, reason = public_is_in_sync_with_main()
    if in_sync and not args.force:
        print(reason)
        if args.verify:
            ok, log = run_verify()
            print(log)
            return 0 if ok else 2
        return 0

    if args.check:
        print(f"[check] Would refresh public branch ({reason})")
        return 0

    try:
        changed, log = run_refresh(force=args.force)
    except RuntimeError as exc:
        print(f"[FAIL] refresh failed: {exc}")
        return 1
    print(log)

    if changed and args.verify:
        ok, verify_log = run_verify()
        print(verify_log)
        if not ok:
            return 2

    # If we refreshed and didn't fail verification, exit 0.
    # If we didn't refresh (no changes needed), also exit 0.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
