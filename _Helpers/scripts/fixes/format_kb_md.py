#!/usr/bin/env python3
"""_Helpers/scripts/fixes/format_kb_md.py - Durable Markdown + Odin formatter for scraped KB files.

Runs a safe, idempotent pipeline on scraped Markdown files under `odin-knowledge-base/docs/`
and `odin-knowledge-base/courses/`:
  1. Fix broken closing code fences (` ```odin ` / ` ~~~odin ` -> ` ``` ` / ` ~~~ `).
  2. Format ```odin code blocks via `odinfmt` (using `odin_format.format_markdown_file`).
  3. Normalize tables, lists, spacing, and LF line endings via Prettier (`--prose-wrap preserve`).
  4. Apply auto-fixable `markdownlint-cli2` rules from `.markdownlint.json`.

Usage:
    python _Helpers/scripts/fixes/format_kb_md.py --check   # dry-run, exit 1 if changes needed
    python _Helpers/scripts/fixes/format_kb_md.py --apply   # format in place
    python _Helpers/scripts/fixes/format_kb_md.py --apply --path odin-knowledge-base/docs
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

ROOT_DIR = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fixes.odin_format import format_markdown_file, format_markdown_odin_blocks, odinfmt_available  # noqa: E402

DEFAULT_TARGETS: tuple[Path, ...] = (
    ROOT_DIR / "odin-knowledge-base" / "docs",
    ROOT_DIR / "odin-knowledge-base" / "courses",
)
_DESCRIPTION = "Format scraped KB Markdown files (closing fences, odinfmt, Prettier, markdownlint)."


def fix_closing_fences(text: str) -> tuple[str, bool]:
    """Fix closing code fences wrongly tagged with a language (e.g. ```odin -> ```).

    Walks line by line tracking fence state and restores bare closing delimiters.
    """
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    delim = ""
    changed = False

    for line in lines:
        stripped = line.strip()
        if not in_fence:
            if stripped.startswith("```"):
                in_fence = True
                delim = "```"
            elif stripped.startswith("~~~"):
                in_fence = True
                delim = "~~~"
            out.append(line)
        else:
            if stripped == f"{delim}odin":
                idx = line.find(delim)
                out.append(f"{line[:idx]}{delim}")
                in_fence = False
                delim = ""
                changed = True
            elif stripped == delim or (stripped.startswith(delim) and stripped.replace(delim[0], "") == ""):
                in_fence = False
                delim = ""
                out.append(line)
            else:
                out.append(line)

    if not changed:
        return text, False
    trailing_nl = "\n" if text.endswith("\n") else ""
    return "\n".join(out) + trailing_nl, True


def _iter_md_files(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for target in targets:
        if target.is_file() and target.suffix.lower() == ".md":
            files.append(target)
        elif target.is_dir():
            files.extend(sorted(p for p in target.rglob("*.md") if p.is_file()))
    return files


def _resolve_npx() -> str:
    return shutil.which("npx") or shutil.which("npx.cmd") or "npx"


def _run_prettier(targets: list[Path], *, apply: bool) -> tuple[int, list[str]]:
    npx_exe = _resolve_npx()
    patterns = [str(t / "**" / "*.md") if t.is_dir() else str(t) for t in targets]
    mode_flag = "--write" if apply else "--list-different"
    cmd = [
        npx_exe,
        "--yes",
        "prettier",
        "--ignore-path",
        "NUL" if sys.platform == "win32" else "/dev/null",
        "--prose-wrap",
        "preserve",
        "--end-of-line",
        "lf",
        mode_flag,
        *patterns,
    ]
    proc = subprocess.run(cmd, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return proc.returncode, lines


def _run_markdownlint(targets: list[Path], *, apply: bool) -> tuple[int, str]:
    npx_exe = _resolve_npx()
    lint_cfg = ROOT_DIR / ".markdownlint.json"
    patterns = [t.as_posix() + ("/**/*.md" if t.is_dir() else "") for t in targets]

    # Run from an isolated temp directory so repo-root `.markdownlintignore` /
    # `.markdownlint-cli2.jsonc` exclusions for `odin-knowledge-base/` do not mask targets.
    with tempfile.TemporaryDirectory() as tmp_dir:
        cmd = [npx_exe, "--yes", "markdownlint-cli2", "--config", str(lint_cfg)]
        if apply:
            cmd.append("--fix")
        cmd.extend(patterns)
        proc = subprocess.run(cmd, cwd=tmp_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_DESCRIPTION)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Dry-run: exit 1 if closing fences, odinfmt, or Prettier need changes.")
    mode.add_argument("--apply", action="store_true", help="Apply formatting in place.")
    parser.add_argument("--path", action="append", default=None, help="Target file/folder (repeatable; defaults to docs + courses).")
    parser.add_argument("--skip-lint", action="store_true", help="Skip markdownlint-cli2 --fix step.")
    args = parser.parse_args(argv)

    targets = [Path(p).resolve() if Path(p).is_absolute() else (ROOT_DIR / p).resolve() for p in args.path] if args.path else list(DEFAULT_TARGETS)
    targets = [t for t in targets if t.exists()]
    if not targets:
        print("[FAIL] No existing target paths found.", file=sys.stderr)
        return 2

    files = _iter_md_files(targets)
    print(f"[i] Scanning {len(files)} Markdown file(s)...")

    fence_changed = 0
    odin_changed = 0
    has_odinfmt = odinfmt_available()
    if not has_odinfmt:
        print("[warn] odinfmt not available; skipping Odin block formatting.")

    for path in files:
        raw = path.read_text(encoding="utf-8")
        fixed_text, f_changed = fix_closing_fences(raw)
        if f_changed:
            fence_changed += 1
            if args.apply:
                path.write_text(fixed_text, encoding="utf-8", newline="\n")

        if has_odinfmt:
            if args.apply:
                o_changed, _tot, _blk = format_markdown_file(path)
                if o_changed:
                    odin_changed += 1
            else:
                _new_t, _tot, blk_changed = format_markdown_odin_blocks(fixed_text)
                if blk_changed > 0:
                    odin_changed += 1

    prettier_rc, prettier_lines = _run_prettier(targets, apply=args.apply)
    if args.apply:
        print(f"[+] Closing fences fixed: {fence_changed}, odinfmt files updated: {odin_changed}")
        print(f"[+] Prettier applied (exit {prettier_rc})")
        if not args.skip_lint:
            lint_rc, lint_out = _run_markdownlint(targets, apply=True)
            summary = [line for line in lint_out.splitlines() if "Summary:" in line]
            print(f"[+] markdownlint-cli2 --fix finished (exit {lint_rc}, {summary[-1] if summary else 'done'})")
            # Re-run Prettier after markdownlint --fix so table/list alignment stays exact.
            _run_prettier(targets, apply=True)
        return 0

    prettier_diff_count = len(prettier_lines) if prettier_rc != 0 else 0
    print(f"[CHECK] fence_fixes={fence_changed}, odinfmt_pending={odin_changed}, prettier_pending={prettier_diff_count}")
    if args.check and (fence_changed or odin_changed or prettier_diff_count):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
