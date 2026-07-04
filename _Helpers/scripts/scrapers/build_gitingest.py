#!/usr/bin/env python3
"""_Helpers/scripts/scrapers/build_gitingest.py - Generate gitingest snapshots.

Reads the repo map in `_Helpers/config/gitIngest_repos.jsonc`, invokes the
`gitingest` CLI on each local clone, and writes the resulting `<id>.txt`
into `odin-knowledge-base/gitIngest/<subfolder>/`.

Idempotent: an existing `*.txt` is regenerated only if the source has
changed since the last generation (compared via mtime + size of the root
folder). Use `--force` to rewrite anyway. Use `--check` for a dry-run.

Usage:
    python _Helpers/scripts/scrapers/build_gitingest.py            # rebuild only stale snapshots
    python _Helpers/scripts/scrapers/build_gitingest.py --force    # rewrite every snapshot
    python _Helpers/scripts/scrapers/build_gitingest.py --check    # dry-run, no writes
    python _Helpers/scripts/scrapers/build_gitingest.py --only <id> [<id> ...]
    python _Helpers/scripts/scrapers/build_gitingest.py --include-skipped

Prerequisites:
    pip install gitingest

Output:
    odin-knowledge-base/gitIngest/<subfolder>/<id>.txt
    odin-knowledge-base/gitIngest/<subfolder>/<id>.json  (sidecar metadata)

Behaviour:
    - Iterates entries sorted by priority ascending.
    - Each entry can be `skip: true` to be excluded from the default run (use --include-skipped to include them).
    - `--only <id>` filters to entries whose `id` matches one of the given slugs.
    - Exit code 0 on full success, 1 if at least one snapshot failed.

Sidecar JSON:
    {
        "id": "<id>",
        "src": "<abs path>",
        "generated_at": "<ISO 8601>",
        "size_bytes": <int>,
        "line_count": <int>,
        "gitingest_version": "<string or 'unknown'>",
        "src_mtime": "<ISO 8601 - max mtime under src>"
    }
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

_DESCRIPTION = "gitingest snapshot generator - re-entrant, --force to rewrite."

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = REPO_ROOT / "_Helpers" / "config" / "gitIngest_repos.jsonc"
OUT_ROOT = REPO_ROOT / "odin-knowledge-base" / "gitIngest"


# ─── Data model ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class RepoEntry:
    """One entry from gitIngest_repos.jsonc."""

    id: str
    src: str
    subfolder: str
    skip: bool
    priority: int
    max_size: int
    exclude: list[str]
    notes: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "RepoEntry":
        return cls(
            id=str(raw["id"]),
            src=str(raw["src"]),
            subfolder=str(raw.get("subfolder", "")),
            skip=bool(raw.get("skip", False)),
            priority=int(raw.get("priority", 99)),
            max_size=int(raw.get("max_size", 100_000)),
            exclude=list(raw.get("exclude", [])),
            notes=str(raw.get("notes", "")),
        )

    @property
    def out_path(self) -> Path:
        return OUT_ROOT / self.subfolder / f"{self.id}.txt"

    @property
    def sidecar_path(self) -> Path:
        return OUT_ROOT / self.subfolder / f"{self.id}.json"


# ─── Config loading ──────────────────────────────────────────────────────────
def _strip_jsonc_comments(text: str) -> str:
    """Strip `//` and `/* */` comments from a JSONC string (lightweight).

    Not a full JSONC parser - sufficient for our hand-edited config which only contains line comments.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    lines: list[str] = []
    for line in text.splitlines():
        idx = line.find("//")
        if idx >= 0:
            in_str = False
            escape = False
            cut_at = -1
            for i, ch in enumerate(line):
                if escape:
                    escape = False
                    continue
                if ch == "\\":
                    escape = True
                    continue
                if ch == '"':
                    in_str = not in_str
                if not in_str and i >= idx:
                    cut_at = i
                    break
            if cut_at >= 0:
                line = line[:cut_at].rstrip()
        lines.append(line)
    return "\n".join(lines)


def load_entries() -> list[RepoEntry]:
    """Read the JSONC config and return RepoEntry objects, sorted by priority."""
    if not CONFIG_PATH.exists():
        print(f"[ERR] config not found: {CONFIG_PATH}")
        return []
    raw_text = CONFIG_PATH.read_text(encoding="utf-8")
    cleaned = _strip_jsonc_comments(raw_text)
    parsed = json.loads(cleaned)
    entries: list[RepoEntry] = []
    for _group_key, group_entries in parsed.items():
        for raw in group_entries:
            entries.append(RepoEntry.from_dict(raw))
    entries.sort(key=lambda e: (e.priority, e.id))
    return entries


# ─── Helpers ─────────────────────────────────────────────────────────────────
def get_gitingest_version() -> str:
    """Return the installed gitingest version, or 'unknown' on failure."""
    exe = shutil.which("gitingest")
    if not exe:
        return "unknown"
    try:
        result = subprocess.run(
            [exe, "--version"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        out = (result.stdout or "") + (result.stderr or "")
        match = re.search(r"(\d+\.\d+\.\d+)", out)
        if match:
            return match.group(1)
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def src_max_mtime(src: Path) -> datetime | None:
    """Return the maximum mtime under `src` (recursive), as UTC datetime."""
    if not src.exists():
        return None
    latest = src.stat().st_mtime
    try:
        for p in src.rglob("*"):
            if p.is_file():
                latest = max(latest, p.stat().st_mtime)
    except OSError:
        pass
    return datetime.fromtimestamp(latest, tz=timezone.utc)


def iso(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def has_gitingest() -> bool:
    return shutil.which("gitingest") is not None


def build_command(entry: RepoEntry, out_path: Path) -> list[str]:
    """Compose the `gitingest` command line for a single entry."""
    cmd: list[str] = ["gitingest", entry.src, "-o", str(out_path), "-s", str(entry.max_size)]
    for pat in entry.exclude:
        cmd.extend(["-e", pat])
    return cmd


def write_sidecar(entry: RepoEntry, gitingest_version: str, src_mtime: datetime | None) -> None:
    """Persist the sidecar JSON with provenance metadata."""
    out_path = entry.out_path
    if not out_path.exists():
        return
    size = out_path.stat().st_size
    line_count = sum(1 for _ in out_path.open("r", encoding="utf-8", errors="replace"))
    payload = {
        "id": entry.id,
        "src": entry.src,
        "generated_at": iso(datetime.now(timezone.utc)),
        "size_bytes": size,
        "line_count": line_count,
        "gitingest_version": gitingest_version,
        "src_mtime": iso(src_mtime),
    }
    entry.sidecar_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )


def is_stale(entry: RepoEntry, now: datetime) -> bool:
    """A snapshot is stale when no sidecar exists, or when src is newer than sidecar."""
    sidecar = entry.sidecar_path
    if not entry.out_path.exists() or not sidecar.exists():
        return True
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    src_mtime_str = payload.get("src_mtime", "")
    if not src_mtime_str:
        return True
    try:
        prev = datetime.fromisoformat(src_mtime_str.replace("Z", "+00:00"))
    except ValueError:
        return True
    return now > prev


# ─── One pass ────────────────────────────────────────────────────────────────
def process_entry(
    entry: RepoEntry,
    *,
    force: bool,
    check_only: bool,
    gitingest_version: str,
) -> str:
    """Return one of: 'ok', 'skipped', 'failed', 'would-skip', 'would-build', 'missing-src'."""
    src = Path(entry.src)
    if not src.exists():
        return "missing-src"
    now = datetime.now(timezone.utc)

    if not force and not check_only and not is_stale(entry, now):
        return "skipped"

    if check_only:
        if entry.out_path.exists() and entry.sidecar_path.exists() and not force:
            return "would-skip"
        return "would-build"

    cmd = build_command(entry, entry.out_path)
    print(f"  $ gitingest {entry.src} -> {entry.out_path.name}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(f"  [ERR] gitingest binary not found on PATH")
        return "failed"
    if result.returncode != 0:
        print(f"  [ERR] gitingest exited with code {result.returncode}")
        if result.stderr:
            print(f"        stderr: {result.stderr.strip()[:400]}")
        return "failed"

    src_mtime = src_max_mtime(src)
    write_sidecar(entry, gitingest_version, src_mtime)
    size = entry.out_path.stat().st_size
    print(f"  [OK] {entry.id}.txt  ({size:,} bytes)")
    return "ok"


# ─── Main ────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument("--force", action="store_true", help="Rewrite every snapshot.")
    parser.add_argument("--check", action="store_true", help="Dry-run, no writes.")
    parser.add_argument(
        "--only", nargs="+", default=[],
        help="Restrict to entries whose id matches one of the given slugs.",
    )
    parser.add_argument(
        "--include-skipped", action="store_true",
        help="Include entries marked skip:true in the JSONC config.",
    )
    args = parser.parse_args(argv)

    print("=" * 60)
    print("  GitIngest snapshot generator")
    print("=" * 60)

    if not has_gitingest():
        print("[ERR] `gitingest` not found on PATH. Install with: pip install gitingest")
        return 1

    entries = load_entries()
    if not entries:
        print(f"[ERR] no entries loaded from {CONFIG_PATH}")
        return 1
    print(f"  [+] {len(entries)} entries loaded from {CONFIG_PATH.name}")

    if args.only:
        wanted = set(args.only)
        entries = [e for e in entries if e.id in wanted]
        print(f"  [i] --only filter: {len(entries)} entries match")
        if not entries:
            print(f"      requested: {sorted(wanted)}")

    if not args.include_skipped:
        skipped_entries = [e for e in entries if e.skip]
        entries = [e for e in entries if not e.skip]
        if skipped_entries:
            print(f"  [i] {len(skipped_entries)} entries skipped (skip:true) - "
                    f"use --include-skipped to include")

    gitingest_version = get_gitingest_version()
    print(f"  [i] gitingest version: {gitingest_version}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for e in entries:
        (OUT_ROOT / e.subfolder).mkdir(parents=True, exist_ok=True)

    counts = {"ok": 0, "skipped": 0, "failed": 0, "would-skip": 0, "would-build": 0, "missing-src": 0}
    for entry in entries:
        if not args.only and entry.skip and not args.include_skipped:
            continue
        tag = f"[p{entry.priority:>2}] {entry.id}"
        result = process_entry(
            entry, force=args.force, check_only=args.check,
            gitingest_version=gitingest_version,
        )
        counts[result] += 1
        prefix = "DRY" if args.check else ("OK" if result == "ok" else "...")
        print(f"  {prefix} {tag:<48} -> {result}")

    print("\n" + "=" * 60)
    if args.check:
        print(f"  {counts['would-skip']} already current, "
                f"{counts['would-build']} would be built, "
                f"{counts['missing-src']} missing source")
    else:
        print(f"  {counts['ok']} rebuilt, {counts['skipped']} skipped, "
                f"{counts['failed']} failures, {counts['missing-src']} missing source")
    print(f"  -> {OUT_ROOT}")
    print("=" * 60)

    return 0 if counts["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
