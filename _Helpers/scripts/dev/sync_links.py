"""_Helpers/scripts/dev/sync_links.py - Cross-platform link manager (Windows + Linux).

The workspace exposes external folders (personal Odin projects) under `code/projects/`
so that Kilo, VS Code and Zed see them as if they were local. The filesystem
primitive is OS-specific: Windows uses NTFS junctions (`mklink /J`), POSIX uses
symbolic links (`ln -s`). This script hides that difference behind ONE manifest
(`_Helpers/links.jsonc`) and ONE CLI, so a Windows checkout and a Linux checkout
of the same repository expose exactly the same layout.

Design rules:
- The manifest (tracked) declares the TOPOLOGY only (logical names, link location).
- The machine-specific ABSOLUTE PATHS live in `_Private/.config/user_config.jsonc`
  -> "links" section, one entry per OS ("windows" / "linux" / "default").
- The links themselves are NEVER tracked by git: they are machine state, and a
  junction cannot be represented in a git tree at all.
- The script NEVER deletes real content: only links are created, replaced or removed.

Usage:
    python _Helpers/scripts/dev/sync_links.py --check   # dry-run, exit 1 on drift
    python _Helpers/scripts/dev/sync_links.py --apply   # create / repair
    python _Helpers/scripts/dev/sync_links.py --prune   # remove undeclared links
    python _Helpers/scripts/dev/sync_links.py --list    # show the topology

Exit codes:
    0  everything is in place (or was fixed with --apply)
    1  at least one link is missing / drifted / broken / unresolved / in conflict
    2  hard error (unreadable manifest, bad CLI usage)
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "_Helpers" / "links.jsonc"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.user_config import LINKS as USER_LINKS  # noqa: E402
from lib.user_config import load_jsonc_file  # noqa: E402

# Windows reparse point tags (see winnt.h).
TAG_MOUNT_POINT = 0xA0000003  # junction
TAG_SYMLINK = 0xA000000C  # symbolic link

STATUS_OK = "ok"
STATUS_MISSING = "missing"
STATUS_DRIFT = "drift"
STATUS_BROKEN = "broken"
STATUS_CONFLICT = "conflict"
STATUS_UNRESOLVED = "unresolved"
STATUS_SKIPPED = "skipped"

STATUS_ORDER = [STATUS_OK, STATUS_MISSING, STATUS_DRIFT, STATUS_BROKEN, STATUS_CONFLICT, STATUS_UNRESOLVED]


def _log(level: str, message: str) -> None:
    """Print a one-line log message with a stable prefix."""
    print(f"[{level}] {message}")


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


@dataclass
class LinkSpec:
    """One declared link: where it lives and what it must point to."""

    id: str
    link: Path
    target: dict[str, Any]
    scope: str
    description: str
    mode: str
    optional: bool

    @property
    def env_var(self) -> str:
        """Environment variable that overrides the resolved target."""
        return "ODINRAG_LINK_" + self.id.upper().replace(".", "_").replace("-", "_")


def load_manifest(path: Path = MANIFEST_PATH) -> list[LinkSpec]:
    """Parse `_Helpers/links.jsonc` and return the declared links."""
    raw = load_jsonc_file(path)
    specs: list[LinkSpec] = []
    for entry in raw.get("links", []):
        if not isinstance(entry, dict):
            raise ValueError("each entry of 'links' must be an object")
        link_rel = str(entry.get("link", "")).strip()
        if not link_rel:
            raise ValueError("each entry of 'links' needs a 'link' path")
        target = entry.get("target", "")
        if isinstance(target, str):
            target = {"repo": target}
        if not isinstance(target, dict):
            raise ValueError(f"'target' of '{link_rel}' must be a string or an object")
        specs.append(
            LinkSpec(
                id=str(entry.get("id", link_rel)),
                link=REPO_ROOT / link_rel,
                target=target,
                scope=str(entry.get("scope", "workspace")),
                description=str(entry.get("description", "")),
                mode=str(entry.get("mode", "auto")),
                optional=bool(entry.get("optional", False)),
            )
        )
    return specs


# ---------------------------------------------------------------------------
# Target resolution
# ---------------------------------------------------------------------------


def os_key() -> str:
    """Return the config key matching the current OS ("windows", "linux", "default")."""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    if system == "linux":
        return "linux"
    return "default"


def resolve_target(spec: LinkSpec) -> tuple[Path | None, str]:
    """Resolve the absolute target of a link for the current OS.

    Returns `(target, reason)`. `target` is None when the link cannot be
    resolved on this machine (missing config entry for this OS).
    """
    env_value = os.environ.get(spec.env_var, "").strip()
    if env_value:
        return Path(env_value).expanduser(), "env"

    if "repo" in spec.target:
        rel = str(spec.target["repo"]).strip()
        return (REPO_ROOT / rel).resolve(), "repo"

    if "config" in spec.target:
        key = str(spec.target["config"]).strip()
        entry = USER_LINKS.get(key)
        if not isinstance(entry, dict):
            return None, f"no user_config entry for '{key}'"
        value = entry.get(os_key()) or entry.get("default") or ""
        if not str(value).strip():
            return None, f"user_config '{key}' has no '{os_key()}' or 'default' path"
        return Path(str(value)).expanduser(), f"config:{key}"

    return None, "target must declare 'repo' or 'config'"


# ---------------------------------------------------------------------------
# Filesystem primitives (cross-platform)
# ---------------------------------------------------------------------------


def link_kind(path: Path) -> str | None:
    """Return "junction", "symlink" or None when `path` is not a link."""
    try:
        st = os.lstat(path)
    except (OSError, ValueError):
        return None
    tag = getattr(st, "st_reparse_tag", 0)
    if tag == TAG_MOUNT_POINT:
        return "junction"
    if tag == TAG_SYMLINK:
        return "symlink"
    if stat.S_ISLNK(st.st_mode):
        return "symlink"
    return None


def read_link_target(path: Path) -> str:
    """Return the raw target string of an existing link."""
    return os.readlink(path)


def normalize_path(value: str, base: Path | None = None) -> str:
    """Normalize a link target for comparison (strip `\\\\?\\`, abs, normcase)."""
    text = value
    if text.startswith("\\\\?\\"):
        text = text[4:]
    candidate = Path(text)
    if not candidate.is_absolute() and base is not None:
        candidate = base / candidate
    return os.path.normcase(os.path.abspath(candidate))


def same_target(actual: str, expected: Path, link: Path) -> bool:
    """True when the link already points to the expected target."""
    return normalize_path(actual, link.parent) == normalize_path(str(expected), link.parent)


def expected_kind(spec: LinkSpec, target: Path) -> str:
    """Return the link primitive this host expects for the given target.

    Windows: an NTFS junction for a directory (no elevation needed), a symbolic
    link otherwise. POSIX: always a symbolic link (a junction cannot exist).
    """
    if os.name == "nt":
        if spec.mode in ("auto", "junction") and target.is_dir():
            return "junction"
        return "symlink"
    return "symlink"


def remove_link(path: Path) -> None:
    """Remove a link (junction or symlink) WITHOUT touching the target content."""
    kind = link_kind(path)
    if kind is None:
        raise RuntimeError(f"refusing to remove '{path}': not a link")
    if kind == "junction":
        os.rmdir(path)
    else:
        os.unlink(path)


def create_link(link: Path, target: Path, mode: str = "auto") -> str:
    """Create the link with the primitive matching the current OS.

    Returns a short human-readable description of what was created.
    """
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        wants_junction = mode in ("auto", "junction") and target.is_dir()
        if wants_junction:
            result = subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(link), str(target)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return "junction"
            junction_error = (result.stderr or result.stdout).strip()
            try:
                os.symlink(target, link, target_is_directory=True)
                return "symlink (junction failed: %s)" % junction_error
            except OSError as exc:
                raise RuntimeError(
                    "cannot create '%s': junction failed (%s) and symlink failed (%s). "
                    "Enable Developer Mode or run as administrator to create symlinks." % (link, junction_error, exc)
                ) from exc
        os.symlink(target, link, target_is_directory=target.is_dir())
        return "symlink"
    os.symlink(target, link, target_is_directory=target.is_dir())
    return "symlink"


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------


@dataclass
class LinkState:
    """Observed state of one declared link."""

    spec: LinkSpec
    status: str
    detail: str
    target: Path | None

    @property
    def needs_action(self) -> bool:
        """True when the link is not in the expected state."""
        return self.status not in (STATUS_OK, STATUS_SKIPPED)


def inspect(spec: LinkSpec, target: Path | None) -> LinkState:
    """Inspect the current filesystem state of a declared link."""
    if target is None:
        if spec.optional:
            return LinkState(spec, STATUS_SKIPPED, "optional link, not configured on this OS", None)
        return LinkState(spec, STATUS_UNRESOLVED, "target not resolvable on this OS", None)

    kind = link_kind(spec.link)
    if kind is None:
        if spec.link.exists():
            return LinkState(spec, STATUS_CONFLICT, "a real file or directory occupies the link path", target)
        if spec.optional:
            return LinkState(spec, STATUS_SKIPPED, "optional link, not present on this OS", target)
        return LinkState(spec, STATUS_MISSING, "link not created yet", target)

    actual = read_link_target(spec.link)
    wanted = expected_kind(spec, target)
    if kind != wanted:
        if spec.optional:
            return LinkState(spec, STATUS_SKIPPED, "optional link, wrong primitive for this OS", target)
        return LinkState(spec, STATUS_DRIFT, "is a %s, this host expects a %s" % (kind, wanted), target)
    if not same_target(actual, target, spec.link):
        if spec.optional:
            return LinkState(spec, STATUS_SKIPPED, "optional link, target differs on this OS", target)
        return LinkState(spec, STATUS_DRIFT, "points to %s" % actual, target)
    if not target.exists():
        if spec.optional:
            return LinkState(spec, STATUS_SKIPPED, "optional link, target missing on this OS", target)
        return LinkState(spec, STATUS_BROKEN, "target does not exist: %s" % target, target)
    return LinkState(spec, STATUS_OK, kind, target)


def find_undeclared_links(specs: list[LinkSpec]) -> list[Path]:
    """List links living next to a declared link but not declared in the manifest.

    Only the containers of the "private" links are scanned (e.g. `code/projects/`).
    The repo root is never scanned: it hosts hand-made links (`.obsidian`, ...) that
    are not part of the manifest and must survive `--prune`.
    """
    declared = {spec.link for spec in specs}
    candidates: list[Path] = []
    for parent in {spec.link.parent for spec in specs if spec.scope == "private"}:
        if not parent.is_dir():
            continue
        for entry in parent.iterdir():
            if entry in declared or not link_kind(entry):
                continue
            candidates.append(entry)
    return sorted(candidates)


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


def apply_state(state: LinkState, dry_run: bool) -> str:
    """Create or repair one link. Returns the action performed."""
    if state.status == STATUS_OK:
        return "unchanged"
    if state.status == STATUS_CONFLICT:
        raise RuntimeError(state.detail)
    if state.status == STATUS_UNRESOLVED or state.target is None:
        raise RuntimeError(state.detail)

    verb = "would create" if dry_run else "created"
    if state.status == STATUS_DRIFT:
        verb = "would replace" if dry_run else "replaced"
        if not dry_run:
            remove_link(state.spec.link)
    elif state.status == STATUS_BROKEN:
        verb = "would recreate" if dry_run else "recreated"
        if not dry_run:
            remove_link(state.spec.link)

    if not dry_run:
        create_link(state.spec.link, state.target, state.spec.mode)
    return verb


def prune_links(specs: list[LinkSpec], dry_run: bool) -> list[Path]:
    """Remove undeclared links next to the declared ones (never touches real folders)."""
    removed: list[Path] = []
    for extra in find_undeclared_links(specs):
        try:
            actual = read_link_target(extra)
        except OSError:
            continue
        if normalize_path(actual, extra.parent).startswith(normalize_path(str(REPO_ROOT), REPO_ROOT)):
            continue  # points inside the repo: managed elsewhere, keep it
        if dry_run:
            removed.append(extra)
            continue
        remove_link(extra)
        removed.append(extra)
    return removed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(description="Manage the workspace links (Windows junctions / POSIX symlinks).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="dry-run: report the state, change nothing (default)")
    mode.add_argument("--apply", action="store_true", help="create or repair the links")
    mode.add_argument("--prune", action="store_true", help="remove the links that are not declared in the manifest")
    mode.add_argument("--list", action="store_true", help="list the declared links and their state")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    args = build_parser().parse_args(argv)

    try:
        specs = load_manifest()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _log("x", f"cannot read the manifest '{MANIFEST_PATH}': {exc}")
        return 2

    if not specs:
        _log("i", "the manifest declares no link")
        return 0

    dry_run = not args.apply

    if args.prune:
        removed = prune_links(specs, dry_run)
        for path in removed:
            _log("-", f"{'would remove' if dry_run else 'removed'} undeclared link: {path}")
        if not removed:
            _log("+", "no undeclared link to prune")
        return 0

    states = []
    for spec in specs:
        target, _reason = resolve_target(spec)
        states.append(inspect(spec, target))

    if args.list:
        _log("i", f"manifest: {MANIFEST_PATH.relative_to(REPO_ROOT)}  ({os_key()} host)")
        for state in states:
            target = state.target if state.target is not None else "?"
            _log("i", f"{state.spec.id:<32} {state.status:<11} {state.spec.link.relative_to(REPO_ROOT)} -> {target}")
        return 0

    failures = 0
    for state in states:
        rel = state.spec.link.relative_to(REPO_ROOT)
        if state.status == STATUS_OK:
            _log("+", f"ok       {rel} ({state.detail})")
            continue
        if state.status == STATUS_SKIPPED:
            _log("i", f"skipped  {rel} ({state.detail})")
            continue
        if state.status == STATUS_UNRESOLVED:
            failures += 1
            _log("!", f"unresolved {rel}: {state.detail}")
            continue
        if state.status == STATUS_CONFLICT:
            failures += 1
            _log("!", f"conflict  {rel}: {state.detail}")
            continue
        try:
            action = apply_state(state, dry_run)
        except (OSError, RuntimeError) as exc:
            failures += 1
            _log("!", f"failed   {rel}: {exc}")
            continue
        failures += 1
        _log("+" if not dry_run else "i", f"{action} {rel} -> {state.target}")

    if not dry_run:
        # Re-inspect: only the links that are STILL not in place are failures.
        failures = 0
        for spec in specs:
            target, _reason = resolve_target(spec)
            state = inspect(spec, target)
            if state.needs_action:
                failures += 1
                _log("!", f"still   {spec.link.relative_to(REPO_ROOT)}: {state.status} ({state.detail})")

    if failures:
        _log("i", f"{failures} link(s) need attention (run with --apply to fix)" if dry_run else f"{failures} link(s) still unresolved")
        return 1

    _log("+", f"all {len(states)} link(s) are in place")
    return 0


if __name__ == "__main__":
    sys.exit(main())
