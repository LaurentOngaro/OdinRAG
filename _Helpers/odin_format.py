"""_Helpers/odin_format.py - Reusable odinfmt wrapper.

Exposes two functions that the scrapers call after writing `.md` or
`.odin` files:

    `format_odin_file(path) -> bool`
    Format a .odin file in place. Returns True if modified.

    `format_markdown_odin_blocks(text) -> tuple[str, int, int]`
    Format the ```odin ... ``` blocks of a Markdown text.
    Returns (modified_text, total_blocks, modified_blocks).

`format_path(path) -> bool`
    Dispatch by extension (.odin -> format_odin_file,
    .md -> format_markdown_odin_blocks).

    Relies on `format_odin_in_files.py` (full CLI: --path, --file,
    --check, --verbose).

    Style applied (via `odinfmt.json` at the repo root):
    - Indentation: 2 SPACES (no tabs).
    - Newlines:   CRLF (default odinfmt on Windows, configurable).
    - Line width: 150 columns.
    To customise, edit `odinfmt.json` (NOT the system-wide config
    shipped with OLS).

    The path to the `odinfmt.exe` executable is read in this order:
    1. environment variable ODINFMT_EXE
    2. `_Helpers/.private/user_config.jsonc` (field paths.odinfmt_exe)
    3. empty string (calls will fail with a clear message)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _Helpers.lib.user_config import env_or_config

# ─── CONFIG ───────────────────────────────────────────────────────────────────
ODINFMT_EXE   = Path(env_or_config("paths.odinfmt_exe", "ODINFMT_EXE"))
ODINFMT_CONFIG = Path(__file__).resolve().parent.parent / "odinfmt.json"
MAX_FILE_BYTES = 5 * 1024 * 1024

# odinfmt expects the `-config=PATH` syntax (single-dash, attached value).
_CONFIG_FLAG = f"-config={ODINFMT_CONFIG}"

_ODIN_FENCE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<fence>`{3,})odin\b[^\n]*\n"
    r"(?P<body>.*?)"
    r"^(?P=indent)(?P=fence)\s*$",
    re.IGNORECASE | re.DOTALL | re.MULTILINE,
)


# ─── ODINFMT WRAPPER ─────────────────────────────────────────────────────────
def odinfmt_available() -> bool:
    return ODINFMT_EXE.is_file() and ODINFMT_CONFIG.is_file()


def odinfmt_format(source: str) -> str | None:
    """Pipe `source` through `odinfmt -stdin -config=...` and return the result.

    Returns `None` if odinfmt fails, is not found, or if the source
    is invalid (parse error).
    """
    try:
        proc = subprocess.run(
            [str(ODINFMT_EXE), "-stdin", _CONFIG_FLAG],
            input=source,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None

    if proc.returncode != 0:
        return None
    return proc.stdout


# ─── FILE FORMATTERS ─────────────────────────────────────────────────────────
def format_odin_file(path: Path) -> bool:
    """Format a .odin file in place. Returns True if modified."""
    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False

    formatted = odinfmt_format(original)
    if formatted is None or formatted == original:
        return False

    try:
        path.write_text(formatted, encoding="utf-8")
    except OSError:
        return False
    return True


def format_markdown_odin_blocks(text: str) -> tuple[str, int, int]:
    """Format the ```odin ... ``` blocks of a Markdown text.

    Returns:
        (texte_modifié, nb_blocs_total, nb_blocs_modifiés).
    """
    blocks_total = blocks_changed = 0

    def repl(match: re.Match) -> str:
        nonlocal blocks_total, blocks_changed
        indent = match.group("indent")
        fence = match.group("fence")
        body = match.group("body")
        blocks_total += 1

        formatted = odinfmt_format(body)
        if formatted is None:
            return match.group(0)

        formatted = formatted.rstrip("\n") + "\n"
        if formatted != body:
            blocks_changed += 1

        return f"{indent}{fence}odin\n{formatted}{indent}{fence}"

    new_text = _ODIN_FENCE_RE.sub(repl, text)
    return new_text, blocks_total, blocks_changed


def format_markdown_file(path: Path) -> tuple[bool, int, int]:
    """Format the odin blocks of a Markdown file in place.

    Returns:
        (modifié, nb_blocs_total, nb_blocs_modifiés).
    """
    try:
        size = path.stat().st_size
    except OSError:
        return False, 0, 0
    if size > MAX_FILE_BYTES:
        return False, 0, 0

    try:
        original = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False, 0, 0

    new_text, total, changed = format_markdown_odin_blocks(original)
    if total == 0 or changed == 0:
        return False, total, changed

    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError:
        return False, total, changed
    return True, total, changed


# ─── DISPATCH ────────────────────────────────────────────────────────────────
def format_path(path: Path) -> bool:
    """Dispatch by file extension.

    Supporte `.odin` et `.md` (case-insensitive). Retourne True si modifié.
    """
    if not odinfmt_available():
        return False
    ext = path.suffix.lower()
    if ext == ".odin":
        return format_odin_file(path)
    if ext == ".md":
        changed, _total, _changed = format_markdown_file(path)
        return changed
    return False


def format_path_if_odin(path: Path, *, silent: bool = False) -> bool:
    """Variante silencieuse : ne logue rien, retourne juste `True/False`."""
    if path.suffix.lower() not in (".odin", ".md"):
        return False
    if not odinfmt_available():
        if not silent:
            print(f"  [WARN] odinfmt not found ({ODINFMT_EXE}) or missing config file ({ODINFMT_CONFIG})", file=sys.stderr)
        return False
    return format_path(path)


__all__ = [
    "ODINFMT_EXE",
    "ODINFMT_CONFIG",
    "odinfmt_available",
    "odinfmt_format",
    "format_odin_file",
    "format_markdown_odin_blocks",
    "format_markdown_file",
    "format_path",
    "format_path_if_odin",
]
