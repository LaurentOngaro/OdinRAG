#!/usr/bin/env python
"""
publish_public.py - Publish the public branch (chain: private push, regen, public push).

This is the daily publishing flow for the public/private split workflow:
1. Push the current main to the `private` remote (full history backup)
2. Regenerate the `public` branch from main (with personal paths stripped)
3. Audit the sanitized public branch (no personal paths leaked)
4. Push the public branch to the `public` remote

Usage:
    python publish_public.py              # full run
    python publish_public.py --check      # dry-run, no pushes, no regen
    python publish_public.py --skip-private  # skip the private push (already done)

Exit codes:
    0 - publish succeeded
    1 - precondition failed (dirty tree, missing remotes, etc.)
    2 - audit found personal paths in the public branch (BEFORE the push was made)
    3 - git command failed unexpectedly

See _Helpers/docs/007_mixing_public_and_private_history.md for the workflow
this script implements.
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
MAIN_REF = "refs/heads/main"
PUBLIC_REF = "refs/heads/public"
MAIN_REMOTE = "private"
PUBLIC_REMOTE = "public"

# Paths to STRIP from the public branch. MUST stay in sync with:
# - audit_public_safety.py FORBIDDEN_PATTERNS
# - the pre-push hook pattern
# - _Helpers/docs/007_mixing_public_and_private_history.md
STRIP_RULES: list[str] = [
    "code/projects/PVG03_RPG",
    "_Private",
    "odin-knowledge-base/courses",
    "odin-knowledge-base/docs/karl_zylinski/odin-book",
]


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a git command in the repo root, raise on failure unless check=False."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed (exit {result.returncode}):\n"
            f"  stderr: {result.stderr.strip()}\n"
            f"  stdout: {result.stdout.strip()}"
        )
    return result


def _step(label: str) -> None:
    print(f"\n[publish] === {label} ===")


def _ok(msg: str) -> None:
    print(f"[+] {msg}")


def _warn(msg: str) -> None:
    print(f"[warn] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}", file=sys.stderr)


def _remote_exists(name: str) -> bool:
    result = _git("remote", "get-url", name, check=False)
    return result.returncode == 0


def _working_tree_is_dirty() -> bool:
    result = _git("status", "--porcelain", check=False)
    return bool(result.stdout.strip())


def clean_dangling_refs() -> None:
    """Delete dangling symrefs and stray dirs that confuse filter-branch.

    filter-branch refuses to operate on `refs/heads/public` if a dangling
    `refs/remotes/public/HEAD` or a stray `refs/heads/refs/heads/public` exists.
    This is a recurring issue (these refs come back after some operations).
    Clean them up before regenerating.
    """
    for ref in [
        "refs/remotes/public/HEAD",
        "refs/remotes/public/main",
        "refs/heads/refs/heads/public",
    ]:
        _git("update-ref", "-d", ref, check=False)
    # Belt-and-suspenders: remove leftover files in case git didn't see them.
    for leftover in [
        REPO_ROOT / ".git" / "refs" / "remotes" / "public" / "HEAD",
        REPO_ROOT / ".git" / "refs" / "heads" / "refs",
    ]:
        if leftover.is_dir():
            shutil.rmtree(leftover, ignore_errors=True)
        elif leftover.exists():
            leftover.unlink(missing_ok=True)


def regenerate_public() -> None:
    """Reset public to main, run filter-branch to strip personal paths.

    Uses the SHORT name `public` for git branch commands (not the full refname)
    because the buggy refname-full approach created stray branches earlier.
    The dangling-ref cleanup is what makes this safe.
    """
    clean_dangling_refs()
    _git("branch", "-f", "public", "main")

    # Build the index-filter: remove each STRIP_RULE recursively from the index.
    # Joined with `;` so sh -c runs them sequentially.
    filter_inner = "; ".join(
        f"git rm --cached -r --ignore-unmatch {rule}" for rule in STRIP_RULES
    )
    # Pass the full `sh -c '...'` as a single arg to filter-branch.
    _git(
        "filter-branch", "-f",
        "--index-filter", f"sh -c '{filter_inner}'",
        "--prune-empty",
        "public",
    )
    # Clean up the backup ref that filter-branch leaves.
    _git("update-ref", "-d", "refs/original/refs/heads/public", check=False)


def find_leaks_in_public() -> list[str]:
    """Return the list of public-branch paths that match a STRIP_RULE."""
    result = _git("ls-tree", "-r", "--name-only", "public", check=False)
    leaks: list[str] = []
    for path in result.stdout.splitlines():
        normalized = path.replace("\\", "/")
        if any(normalized.startswith(rule + "/") for rule in STRIP_RULES):
            leaks.append(path)
    return leaks


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="publish_public.py",
        description=(
            "Publish the public branch: push private, regenerate public from main, "
            "audit, push public. Always refuses to run on a dirty working tree."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run. Regenerate public in the local ref (no pushes), audit, report. No remote interaction.",
    )
    parser.add_argument(
        "--skip-private",
        action="store_true",
        help="Skip the push to the private remote (use when you already pushed manually).",
    )
    parser.add_argument(
        "--no-preflight",
        action="store_true",
        help=(
            "Skip the preflight checks (dirty working tree, remote presence). "
            "Intended for CI runners that have no remotes configured and may "
            "have stray refs left by a previous failed filter-branch."
        ),
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    # Preflight: dirty tree, missing remotes. Skippable for CI via --no-preflight.
    if not args.no_preflight:
        if _working_tree_is_dirty():
            _fail("working tree has unstaged changes; commit or stash first.")
            result = _git("status", "--porcelain", check=False)
            for line in result.stdout.splitlines()[:5]:
                print(f"        {line}")
            return 1

        for remote in (MAIN_REMOTE, PUBLIC_REMOTE):
            if not _remote_exists(remote):
                _fail(f"remote '{remote}' is not configured. Run `git remote add {remote} <url>`.")
                return 1

    main_sha = _git("rev-parse", MAIN_REF).stdout.strip()
    public_before_sha = _git("rev-parse", PUBLIC_REF, check=False).stdout.strip()

    if args.check:
        _step("[check] dry-run: regenerate locally, audit, no pushes")
        regenerate_public()
        public_after_sha = _git("rev-parse", PUBLIC_REF).stdout.strip()
        print(f"[check] main={main_sha[:12]} -> public {public_before_sha[:12]} -> {public_after_sha[:12]}")
        leaks = find_leaks_in_public()
        if leaks:
            _fail(f"public branch would contain {len(leaks)} personal path(s):")
            for p in leaks[:10]:
                print(f"        {p}")
            return 2
        _ok("public branch would be clean (no personal paths)")
        return 0

    # Real run.
    # Step 1: push private.
    if not args.skip_private:
        _step(f"push {MAIN_REF} -> {MAIN_REMOTE}")
        _git("push", MAIN_REMOTE, MAIN_REF)
        _ok(f"pushed {main_sha[:12]} to {MAIN_REMOTE}")
    else:
        print(f"[skip] push to {MAIN_REMOTE} (--skip-private)")

    # Step 2: regenerate public locally.
    _step("regenerate public branch from main")
    regenerate_public()
    public_after_sha = _git("rev-parse", PUBLIC_REF).stdout.strip()
    print(f"[+] public rewritten: {public_before_sha[:12]} -> {public_after_sha[:12]}")

    # Step 3: audit BEFORE the public push.
    _step("audit public branch (no personal paths)")
    leaks = find_leaks_in_public()
    if leaks:
        _fail(f"{len(leaks)} personal path(s) leaked into public:")
        for p in leaks[:10]:
            print(f"        {p}")
        print()
        print("The public push was NOT made. The regen left personal paths in the")
        print("regenerated branch, which is unexpected. Inspect STRIP_RULES above.")
        return 2
    _ok("public branch is clean (no personal paths)")

    # Step 4: push public.
    # The local `public` branch is regenerated from `main` every run, so it
    # naturally diverges from the remote `public` (which is from a previous
    # run, or from an older workflow). Non-fast-forward is the expected case.
    # We try a normal push first (clean case for the very first publish), then
    # fall back to --force-with-lease (safer than --force: refuses if someone
    # else pushed in the meantime).
    _step(f"push {PUBLIC_REF} -> {PUBLIC_REMOTE}")
    result = _git("push", PUBLIC_REMOTE, PUBLIC_REF, check=False)
    if result.returncode == 0:
        _ok(f"pushed {public_after_sha[:12]} to {PUBLIC_REMOTE} (fast-forward)")
    else:
        if "non-fast-forward" not in result.stderr and "! [rejected]" not in result.stderr:
            _fail(f"git push {PUBLIC_REMOTE} {PUBLIC_REF} failed:")
            print(result.stderr)
            return 3
        _warn("remote public has diverged; this is expected (each run regenerates from main)")
        _warn("retrying with --force-with-lease to overwrite the remote with the local version")
        _git("push", "--force-with-lease", PUBLIC_REMOTE, PUBLIC_REF)
        _ok(f"pushed {public_after_sha[:12]} to {PUBLIC_REMOTE} (force-with-lease)")

    print()
    print("[OK] publish complete.")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv if argv is not None else sys.argv[1:])
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        return run(args)
    except RuntimeError as exc:
        _fail(str(exc))
        return 3


if __name__ == "__main__":
    sys.exit(main())
