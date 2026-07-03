"""_Helpers/scripts/diagnostic/vaultConfigOdinRAG.py - Shared config for the diagnostic scripts.

Minimal adaptation of TerraBloom's `_Helpers/vaultConfig.py` for the OdinRAG structure.
Provides:

- Path resolution (REPO_ROOT, HELPERS_DIR, KB_ROOT, etc.).
- IGNORE_DIRS / IGNORE_FILES tuned for OdinRAG (skips `_Private/`, `.git/`, vendored templates, etc.).
- Frontmatter rules (REQUIRED_FIELDS, ALLOWED_TYPES, ALLOWED_STATUS) matching `_Helpers/docs/003_yaml_frontmatter_conventions.md` (8 fields + 9 types + 5 statuses).
- `extract_frontmatter(content)` - YAML-safe_load + body offset.
- `validate_frontmatter(fm)` - returns list[str] errors.
- `should_ignore(path)` / `should_validate(path)` - predicates used by the CLI scripts.
- `path_link(path, label=None)` - OSC-8 clickable terminal link.

Cross-platform (Windows / Unix). PyYAML is the only third-party dependency.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError as exc:  # pragma: no cover - PyYAML is the only third-party dep
    raise ImportError(
        "vaultConfigOdinRAG requires PyYAML. Install with: pip install pyyaml"
    ) from exc

try:
    import colorama  # type: ignore[import-untyped]
    from colorama import Fore, Style

    colorama.init()
    COLORS: dict[str, str] = {
        "RED": Fore.RED,
        "YELLOW": Fore.YELLOW,
        "GREEN": Fore.GREEN,
        "CYAN": Fore.CYAN,
        "BOLD": Style.BRIGHT,
        "RESET": Style.RESET_ALL,
    }
except Exception:
    COLORS = dict.fromkeys(["RED", "YELLOW", "GREEN", "CYAN", "BOLD", "RESET"], "")


# --- PATHS ---
DIAGNOSTIC_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = DIAGNOSTIC_DIR.parent
HELPERS_DIR = SCRIPTS_DIR.parent
REPO_ROOT = HELPERS_DIR.parent
KB_ROOT = REPO_ROOT / "odin-knowledge-base"
CODE_ROOT = REPO_ROOT / "code"


# --- IGNORE LISTS ---
IGNORE_DIRS: set[str] = {
    ".git",
    ".vscode",
    ".obsidian",
    ".kilo",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    "logs",
    "build",
    "out",
    "_archives",
    ".private",
    "_Private",
    "_Raw",
    "_History",
    "_Tools",
    "_Refs",
    "Library",
    "Temp",
    "obj",
    "Builds",
    "Build",
    "UserSettings",
    "code",
    "odin-knowledge-base",
}

IGNORE_FILES: set[str] = {
    "README.md",
    ".gitignore",
    ".gitattributes",
    "kilocode.json",
    "copilot-instructions.md",
    "AGENTS.md"
}

VALIDATION_EXCLUDE_DIRS: set[str] = {
    "code/vendored templates",
    "code/gists",
    "code/examples",
    "_Helpers/_obsoletes",
    "_Private",
    "odin-knowledge-base/courses",
    "odin-knowledge-base/docs/karl_zylinski/odin-book",
}

VALIDATION_IGNORE_PATTERNS: list[str] = [
    r"(?i)^readme",
    r"(?i)index",
]

BUILTIN_BASENAME_EXCLUSIONS: tuple[str, ...] = (
    r"(?i)^readme",
    r"(?i)index",
)


# --- FRONTMATTER RULES (mirror `_Helpers/docs/003_yaml_frontmatter_conventions.md`) ---
REQUIRED_FIELDS: list[str] = [
    "title",
    "date",
    "tags",
    "type",
    "status",
    "version",
    "lastUpdated",
    "updatedBy",
]

OPTIONAL_FIELDS: list[str] = [
    "docId",
    "priority",
]

ALLOWED_TYPES: set[str] = {
    "note",
    "daily",
    "weekly",
    "monthly",
    "roadmap",
    "reference",
    "dev_log",
    "archive",
    "template",
}

ALLOWED_STATUS: set[str] = {
    "draft",
    "active",
    "done",
    "archived",
    "deprecated",
}

ALLOWED_PRIORITY: set[int] = {1, 2, 3}

REQUIRED_ROOT_TAG = "OdinRAG"

MAX_RAG_FILE_SIZE = 2 * 1024 * 1024  # 2MB per file


# --- REGEX PATTERNS ---
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
DOCID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*[A-Z0-9]$")
TAG_HIERARCHY_PATTERN = re.compile(r"^[a-z][a-z0-9]*(/[a-z0-9]+)?$|^OdinRAG$|^Skool$|^PVG03_RPG$")
LONG_DASH_PATTERN = re.compile(r"[\u2013\u2014\u2015]")
CJK_PATTERN = re.compile(
    r"[\u3000-\u303f\u3040-\u309f\u30a0-\u30ff"
    r"\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af"
    r"\uff00-\uffef]"
)
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


# --- UTILITIES ---
def should_ignore_file(path: Path | str) -> bool:
    """Return True if the basename of `path` is listed in `IGNORE_FILES`.

    Comparison is case-insensitive. Used by the CLI scripts to opt in to file
    filtering via `--ignore-files`. Decoupled from directory filtering so
    the user can enable either independently.
    """
    file_name = os.path.basename(str(path)).lower()
    return file_name in (name.lower() for name in IGNORE_FILES)


def should_ignore_dir(path: Path | str, ignore_dirs: set[str] | None = None) -> bool:
    """Return True if `path` is inside any folder listed in `IGNORE_DIRS`.

    Patterns containing `/` are split and ALL segments must appear as
    consecutive parts of the path - this prevents `Temp` from accidentally
    matching a folder called `TEMP_L~1`. Used by the CLI scripts to opt
    in to directory filtering via `--ignore-dirs`.
    """
    ignore_dirs = ignore_dirs if ignore_dirs is not None else IGNORE_DIRS
    p_str = str(path)
    parts_lower = [part.lower() for part in Path(p_str).parts]
    for pattern in ignore_dirs:
        pat = pattern.lower().replace("\\", "/").strip("/")
        segments = [seg for seg in pat.split("/") if seg]
        if not segments:
            continue
        if len(segments) == 1:
            if segments[0] in parts_lower:
                return True
            continue
        for i in range(len(parts_lower) - len(segments) + 1):
            if parts_lower[i:i + len(segments)] == segments:
                return True
    return False


def should_ignore(path: Path | str, ignore_dirs: set[str] | None = None) -> bool:
    """Backwards-compatible predicate: True if path matches `IGNORE_FILES` OR any `IGNORE_DIRS` folder.

    New code should prefer the explicit pair `should_ignore_file` +
    `should_ignore_dir` so the caller can decide which filters to apply
    (e.g. the `--ignore-dirs` / `--ignore-files` CLI flags).
    """
    return should_ignore_file(path) or should_ignore_dir(path, ignore_dirs)


def _is_all_uppercase_stem(name: str) -> bool:
    """Return True if the basename `name` has a stem of all-uppercase letters.

    The stem must contain at least one ASCII letter; if it is digits-only
    (e.g. `123.md`) the function returns False (no "uppercase" notion to
    apply). Digits, underscores, hyphens and the dot are allowed but ignored.

    Examples that return True:
        AGENTS.md, README.md, CHANGELOG.md, LICENSE.md, INDEX.md,
        J_TEMPLATE.md, SKILL.md, REDDIT_POST.md, TWITTER_THREAD.md,
        DISCORD_NOTE.md
    Examples that return False:
        007_yaml_frontmatter_conventions.md (lowercase letters present) main.odin (lowercase) auditReadmeCoherence.py (lowercase) 123.md (no letters)
    """
    stem = Path(name).stem
    if not any(c.isalpha() for c in stem):
        return False
    return stem == stem.upper()


def should_validate(path: Path | str) -> bool:
    """Return True if the frontmatter of this file should be validated.

    Skip rules (basename-scoped, checked first to avoid path false-positives):

    1. `BUILTIN_BASENAME_EXCLUSIONS` - regex patterns matched against the filename only: `README*` (any case) and any file with `index` in the basename (`INDEX.md`, `_index_*.md`, `refresh_topic_index.md`).
    2. `_is_all_uppercase_stem` - all-uppercase stem excludes stable metadata files (`AGENTS`, `CHANGELOG`, `LICENSE`, `SKILL`, `J_TEMPLATE`). Dailies in `_Private/` and templates in `_Helpers/templates/` are already caught by `should_ignore` so they never reach this branch.

    Then path-scoped rules:

    3. `VALIDATION_EXCLUDE_DIRS` - skip folders.
    4. `VALIDATION_IGNORE_PATTERNS` - legacy path-based regex (rarely needed; basename exclusions above already cover the common cases).
    """
    p_str = str(path)
    if should_ignore(p_str):
        return False
    file_name = os.path.basename(p_str)

    for pat in BUILTIN_BASENAME_EXCLUSIONS:
        if re.search(pat, file_name):
            return False

    if _is_all_uppercase_stem(file_name):
        return False

    parts_lower = [p.lower() for p in Path(p_str).parts]
    for ex in VALIDATION_EXCLUDE_DIRS:
        if ex.lower() in parts_lower:
            return False

    for pat in VALIDATION_IGNORE_PATTERNS:
        if re.search(pat, p_str, flags=re.IGNORECASE):
            return False

    return True


def extract_frontmatter(content: str) -> tuple[dict[str, Any] | None, int]:
    """Parse the leading `---` block. Returns (fm_dict_or_None, body_offset)."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, 0
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {"__yaml_error__": True}, m.end()
    if fm is None:
        return {}, m.end()
    if not isinstance(fm, dict):
        return {"__yaml_error__": f"Frontmatter root must be a mapping, got {type(fm).__name__}"}, m.end()
    return fm, m.end()


def read_file_with_fm(path: Path | str) -> tuple[tuple[dict[str, Any] | None, int], str]:
    """Read a file and return ((fm_dict, body_offset), raw_content)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError as exc:
        return ({"__read_error__": str(exc)}, 0), ""
    return extract_frontmatter(content), content


def validate_frontmatter(fm: dict[str, Any] | None) -> list[str]:
    """Validate `fm` against the 8-field OdinRAG schema. Returns list of error strings."""
    errors: list[str] = []

    if fm is None:
        return ["Missing or malformed frontmatter (no leading '---' block found)"]

    if "__yaml_error__" in fm:
        msg = fm["__yaml_error__"]
        return [f"YAML parse error: {msg}" if isinstance(msg, str) else "YAML parse error"]

    if "__read_error__" in fm:
        return [f"Cannot read file: {fm['__read_error__']}"]

    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing required field: '{field}'")
            continue
        value = fm[field]
        if value is None:
            errors.append(f"Empty required field: '{field}'")
            continue
        if isinstance(value, str) and not value.strip():
            errors.append(f"Empty required field: '{field}'")
            continue
        if isinstance(value, list) and not value:
            errors.append(f"Empty required field: '{field}'")

    if "type" in fm and isinstance(fm["type"], str) and fm["type"] not in ALLOWED_TYPES:
        errors.append(
            f"Invalid type: '{fm['type']}' (allowed: {', '.join(sorted(ALLOWED_TYPES))})"
        )

    if "status" in fm and isinstance(fm["status"], str) and fm["status"] not in ALLOWED_STATUS:
        errors.append(
            f"Invalid status: '{fm['status']}' (allowed: {', '.join(sorted(ALLOWED_STATUS))})"
        )

    if "priority" in fm:
        try:
            p = int(fm["priority"])
            if p not in ALLOWED_PRIORITY:
                errors.append(f"priority must be 1, 2, or 3 (got {p})")
        except (TypeError, ValueError):
            errors.append(f"priority must be 1, 2, or 3 (got {fm['priority']!r})")

    if "version" in fm and isinstance(fm["version"], str) and not VERSION_PATTERN.match(fm["version"]):
        errors.append(f"Invalid version format: '{fm['version']}' (expected semver X.Y.Z)")

    if "date" in fm and isinstance(fm["date"], str) and not DATE_PATTERN.match(fm["date"]):
        errors.append(f"Invalid date format: '{fm['date']}' (expected ISO YYYY-MM-DD)")

    if "lastUpdated" in fm and isinstance(fm["lastUpdated"], str) and not DATE_PATTERN.match(fm["lastUpdated"]):
        errors.append(f"Invalid lastUpdated format: '{fm['lastUpdated']}' (expected ISO YYYY-MM-DD)")

    if "docId" in fm and isinstance(fm["docId"], str) and fm["docId"] and not DOCID_PATTERN.match(fm["docId"]):
        errors.append(
            f"Invalid docId format: '{fm['docId']}' (expected UPPER_SNAKE_CASE, e.g. NAV_FM_001)"
        )

    if "tags" in fm:
        tags = fm["tags"]
        if not isinstance(tags, list):
            errors.append("tags must be a list (e.g. [OdinRAG, planning])")
        else:
            tag_strs = [t for t in tags if isinstance(t, str)]
            if REQUIRED_ROOT_TAG not in tag_strs:
                errors.append(f"Missing required root tag: '{REQUIRED_ROOT_TAG}'")
            for tag in tag_strs:
                if tag.startswith("#"):
                    errors.append(f"Tag contains '#' prefix: '{tag}' (Obsidian auto-strips it)")
                if not TAG_HIERARCHY_PATTERN.match(tag):
                    if "/" in tag and tag.count("/") >= 2:
                        errors.append(
                            f"Tag '{tag}' has more than 2 hierarchical levels (max: root/sub)"
                        )
                    elif " " in tag:
                        errors.append(f"Tag '{tag}' contains spaces (forbidden)")
                    else:
                        errors.append(
                            f"Tag '{tag}' does not match expected pattern (lowercase, optional one '/' sub)"
                        )

    return errors


def path_link(path: Path | str, label: str | None = None) -> str:
    """Return an OSC-8 clickable `file:///...` terminal link (or plain path on failure)."""
    try:
        p = Path(path).resolve()
        uri = p.as_uri()
        display = label or str(p)
        esc = "\033"
        return f"{esc}]8;;{uri}{esc}\\{display}{esc}]8;;{esc}\\"
    except Exception:
        return str(path)


def cprint(msg: str, color: str = "", bold: bool = False, file: Any = None) -> None:
    """Print with optional color + bold. Colorama on Windows, ANSI elsewhere."""
    prefix = COLORS.get("BOLD", "") if bold else ""
    color_code = COLORS.get(color, "") if color else ""
    reset = COLORS.get("RESET", "")
    try:
        print(f"{prefix}{color_code}{msg}{reset}", file=file)
    except UnicodeEncodeError:
        safe = msg.encode("ascii", errors="replace").decode("ascii")
        print(f"{prefix}{color_code}{safe}{reset}", file=file)


__all__ = [
    "DIAGNOSTIC_DIR",
    "SCRIPTS_DIR",
    "HELPERS_DIR",
    "REPO_ROOT",
    "KB_ROOT",
    "CODE_ROOT",
    "IGNORE_DIRS",
    "IGNORE_FILES",
    "VALIDATION_EXCLUDE_DIRS",
    "VALIDATION_IGNORE_PATTERNS",
    "REQUIRED_FIELDS",
    "OPTIONAL_FIELDS",
    "ALLOWED_TYPES",
    "ALLOWED_STATUS",
    "ALLOWED_PRIORITY",
    "REQUIRED_ROOT_TAG",
    "MAX_RAG_FILE_SIZE",
    "DATE_PATTERN",
    "VERSION_PATTERN",
    "DOCID_PATTERN",
    "TAG_HIERARCHY_PATTERN",
    "LONG_DASH_PATTERN",
    "CJK_PATTERN",
    "FRONTMATTER_RE",
    "should_ignore",
    "should_ignore_file",
    "should_ignore_dir",
    "should_validate",
    "extract_frontmatter",
    "read_file_with_fm",
    "validate_frontmatter",
    "path_link",
    "cprint",
]
