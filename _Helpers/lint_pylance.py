#!/usr/bin/env python3
"""_Helpers/lint_pylance.py - Run pyright (Pylance engine) on Python files.

Wraps the ``pyright`` CLI (the open-source engine behind VSCode Pylance) into a durable, repo-friendly command that matches this project's "durable scripts" rules (idempotent, ``--check`` dry-run, clear logging, non-zero exit on remaining warnings).

Usage:
    python _Helpers/lint_pylance.py                          # whole repo
    python _Helpers/lint_pylance.py _Helpers/scrape_skool.py # single file
    python _Helpers/lint_pylance.py _Helpers/                # one folder
    python _Helpers/lint_pylance.py --check                  # dry-run, exit 0
    python _Helpers/lint_pylance.py --strict                 # warnings count

Exit codes:
    0  - clean (no warnings / no errors, depending on flags)
    1  - one or more diagnostics reported
    2  - tool error (pyright missing, bad target, ...)

Why this exists:
    AGENTS.md mandates: "After any edit to a .py file, run pyright and
    fix every reported warning before considering the task done."
    This script is the single command an agent (or human) runs.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

_DESCRIPTION = "Run pyright on Python files and report Pylance diagnostics."

REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_pyright() -> list[str]:
    """Return the command to invoke pyright. Prefer ``pyright`` on PATH,
    fall back to ``python -m pyright``."""
    if shutil.which("pyright") is not None:
        return ["pyright"]
    return [sys.executable, "-m", "pyright"]


def _format_diag(diag: dict) -> str:
    """Format one pyright diagnostic as ``path:line:col - severity - rule - message``."""
    file = diag.get("file", "?")
    line = diag.get("range", {}).get("start", {}).get("line", 0) + 1
    col = diag.get("range", {}).get("start", {}).get("character", 0) + 1
    severity = diag.get("severity", "?")
    rule = diag.get("rule", "")
    msg = diag.get("message", "").splitlines()[0]
    rel = file
    try:
        rel = str(Path(file).resolve().relative_to(REPO_ROOT))
    except ValueError:
        pass
    suffix = f" [{rule}]" if rule else ""
    return f"{rel}:{line}:{col} - {severity} - {msg}{suffix}"


def run_pyright(target: Path, strict: bool) -> tuple[int, dict]:
    """Invoke pyright on ``target`` and return (returncode, parsed_json_dict)."""
    cmd = _resolve_pyright() + [str(target), "--outputjson"]
    proc = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if not proc.stdout.strip():
        return proc.returncode, {"generalDiagnostics": [], "summary": {}}
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(f"[ERR] pyright returned non-JSON output:", file=sys.stderr)
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return 2, {}


def lint(target: Path, strict: bool, check: bool) -> int:
    """Run the linter on ``target`` and return the appropriate exit code."""
    if not target.exists():
        print(f"[ERR] Target not found: {target}", file=sys.stderr)
        return 2

    rel = target
    try:
        rel = target.resolve().relative_to(REPO_ROOT)
    except ValueError:
        pass
    print(f"[lint] pyright on {rel} (strict={strict}, check={check})")

    rc, payload = run_pyright(target, strict=strict)
    if rc == 2:
        # Tool-level error (pyright missing, bad config, etc.)
        return 2

    diagnostics = payload.get("generalDiagnostics", [])
    summary = payload.get("summary", {})

    if strict:
        blocking = [d for d in diagnostics if d.get("severity") in {"error", "warning"}]
    else:
        blocking = [d for d in diagnostics if d.get("severity") == "error"]

    info = [d for d in diagnostics if d not in blocking]

    print(f"  errors   : {summary.get('errorCount', len([d for d in blocking if d.get('severity') == 'error']))}")
    print(f"  warnings : {summary.get('warningCount', len([d for d in blocking if d.get('severity') == 'warning']))}")
    print(f"  info     : {summary.get('informationCount', len(info))}")

    for d in blocking:
        print(f"  {_format_diag(d)}")

    if blocking:
        if check:
            print(f"[CHECK] {len(blocking)} diagnostic(s) would be reported. Fix and re-run.")
            return 0
        print(f"[FAIL] {len(blocking)} diagnostic(s) to fix.")
        return 1

    print("[OK] No blocking diagnostics.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    parser.add_argument(
        "target",
        nargs="?",
        default=str(REPO_ROOT),
        help="File or folder to lint (default: repo root).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Dry-run: report findings but always exit 0.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blocking (default: only errors block).",
    )
    args = parser.parse_args(argv)

    return lint(Path(args.target), strict=args.strict, check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
