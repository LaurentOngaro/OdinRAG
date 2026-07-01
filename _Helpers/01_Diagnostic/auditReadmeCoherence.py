"""Audit coherence between README files and their host directory.

Adapted from TerraBloom's `auditReadmeCoherence.py` for OdinRAG structure.

Detects:
- Files referenced by wikilinks that don't exist
- Subdirectories mentioned in README that don't exist (when used in structure sections)
- Files present in the directory but listed in a "Structure" section as missing

Usage:
    python _Helpers/01_Diagnostic/auditReadmeCoherence.py
    python _Helpers/01_Diagnostic/auditReadmeCoherence.py --fail-on-error
    python _Helpers/01_Diagnostic/auditReadmeCoherence.py --scope docs
    python _Helpers/01_Diagnostic/auditReadmeCoherence.py --scope docs/official

Notes for OdinRAG:
- The script does NOT depend on TerraBloom's `vaultConfig.py`. If `vaultConfig` is found in `sys.path` it is used (so VAULT_ROOT can be overridden), otherwise it falls back to the repo root inferred from `__file__`.
- The regex patterns for inline filenames / folder references (`FILENAME_PATTERN`, `DIRNAME_PATTERN`, `FOLDER_WIKILINK_PATTERN`) are designed for the TerraBloom convention `NNN_Title.md`. They will rarely trigger in OdinRAG (no `NNN_` prefix), but the wikilink detection still works fine and is the main useful check here.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import colorama
    from colorama import Fore, Style

    colorama.init()
    COLORS = {"RED": Fore.RED, "YELLOW": Fore.YELLOW, "GREEN": Fore.GREEN, "CYAN": Fore.CYAN, "BOLD": Style.BRIGHT, "RESET": Style.RESET_ALL}
except Exception:
    COLORS = dict.fromkeys(["RED", "YELLOW", "GREEN", "CYAN", "BOLD", "RESET"], "")


def cprint(msg: str, color: str = "", bold: bool = False) -> None:
    prefix = COLORS.get("BOLD") if bold else ""
    color_code = COLORS.get(color, "")
    reset = COLORS.get("RESET", "")
    # Encode-safe replacement of common Unicode chars that break Windows console
    safe_msg = (
        msg
        .replace("\u2192", "->")  # right arrow
        .replace("\u2190", "<-")  # left arrow
        .replace("\u2194", "<->")  # left-right arrow
        .replace("\u2026", "...")
    )
    try:
        print(f"{prefix}{color_code}{safe_msg}{reset}")
    except UnicodeEncodeError:
        print(f"{prefix}{color_code}{safe_msg.encode('ascii', errors='replace').decode('ascii')}{reset}")


# Resolve helpers dir and repo root
HELPERS_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = HELPERS_DIR.parent

# Optional dependency: vaultConfig (TerraBloom). Falls back gracefully.
VAULT_ROOT = ROOT_DIR
try:
    import vaultConfig as cfg  # type: ignore
    VAULT_ROOT = Path(getattr(cfg, "VAULT_ROOT", ROOT_DIR))
except ImportError:
    # OdinRAG does not ship vaultConfig.py - use repo root.
    # Also try the parent (for "_Helpers" import) before giving up.
    try:
        sys.path.insert(0, str(HELPERS_DIR))
        import vaultConfig as cfg  # type: ignore
        VAULT_ROOT = Path(getattr(cfg, "VAULT_ROOT", ROOT_DIR))
    except ImportError:
        pass


# Folders to skip during scan
SKIP_DIRS = {
    # Generic / tooling
    ".git", ".vscode", ".obsidian", "node_modules", "__pycache__",
    "_Data_consolidation", "_History", ".pytest_cache",
    "_Helpers/_obsoletes", "_Helpers/__pycache__",
    "Library", "Temp", "obj", "Builds", "Build",
    "Logs", "UserSettings",
    # OdinRAG-specific
    "odin-knowledge-base",   # gitignored, contains scraped SKOOL content
    "_Raw",                  # gitignored, personal drafts
    "logs",                  # cumulative scraper logs (gitignored)
    ".private",              # personal user_config.jsonc (gitignored)
    ".kilo",                 # Kilo runtime config + node_modules
    "_TEMPLATE_",            # project template (not real content)
    "out",                   # scrapers output
    "__pycache__",           # python bytecode cache (duplicate safety)
}


# Regex patterns
WIKILINK_PATTERN = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
# Matches inline filenames - requires underscore between prefix and rest, ends with .md, no space in middle
FILENAME_PATTERN = re.compile(r"(?<![`\w/\d])(\d{3}_[A-Za-z0-9_-]+\.md)(?!\S*\d)")
# Matches directory references like "851_Curated_AssetsList/" or "301_IA_Tools/"
DIRNAME_PATTERN = re.compile(r"(?:^|[\s`(])(?:[*+-]\s+)?(\d{3}_[A-Za-z0-9_]+)/")
# Matches folder wikilinks [[Folder/]] (with trailing slash, no extension)
FOLDER_WIKILINK_PATTERN = re.compile(r"\[\[(\d{3}_[A-Za-z0-9_]+)/\]\]")


def iter_readmes(scope: Path) -> Iterable[Path]:
    """Yield all README*.md files under scope."""
    if scope.is_file():
        if scope.name.startswith("README") and scope.suffix == ".md":
            yield scope
        return
    for path in scope.rglob("*.md"):
        if not path.name.startswith("README"):
            continue
        rel = path.relative_to(VAULT_ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        yield path


def extract_references(readme: Path, host_dir: Path) -> tuple[set[str], set[str], set[str]]:
    """Extract file/subdir/wikilink references from a README.

    Returns:
        wikilinks: names referenced via [[wikilinks]] (no folder path)
        filenames: names referenced inline as paths
        subdirs: subdirectory names referenced inline (without trailing slash)

    Notes:
        - Wikilinks with explicit folder paths (e.g. [[Folder/Name]]) are skipped (they're vault-wide references, not local consistency checks).
        - Inline filenames are matched conservatively (no premature cutoff at spaces).
        - Content inside markdown code blocks (between ``` fences) is skipped (examples should not be checked for filesystem consistency).
    """
    wikilinks: set[str] = set()
    filenames: set[str] = set()
    subdirs: set[str] = set()

    try:
        text = readme.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return wikilinks, filenames, subdirs

    # Strip content inside markdown code blocks (```...```)
    # This excludes code-fenced examples from being checked
    text_no_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Also strip inline code `...`
    text_no_code = re.sub(r"`[^`]+`", "", text_no_code)

    # Extract wikilinks (skip those with explicit folder paths)
    for m in WIKILINK_PATTERN.finditer(text_no_code):
        target = m.group(1).strip()
        # Skip vault-wide references with explicit paths
        if "/" in target:
            continue
        # Skip Obsidian internal references
        if target.startswith("#") or not target:
            continue
        wikilinks.add(target)

    # Extract folder wikilinks [[Folder/]]
    for m in FOLDER_WIKILINK_PATTERN.finditer(text_no_code):
        subdirs.add(m.group(1).strip())

    # Extract inline filenames (conservative match)
    for m in FILENAME_PATTERN.finditer(text_no_code):
        filenames.add(m.group(1).strip())

    # Extract inline subdirs
    for m in DIRNAME_PATTERN.finditer(text_no_code):
        subdirs.add(m.group(1).strip())

    return wikilinks, filenames, subdirs


def resolve_wikilink(target: str, host_dir: Path, vault_root: Path) -> Path | None:
    """Resolve a wikilink name to an actual file path.

    Obsidian convention: [[Name]] resolves to Name.md in the same vault.
    We check:
    1. host_dir / f"{target}.md"
    2. vault_root / f"{target}.md" (recursive search)
    3. host_dir / target (directory)
    """
    # Direct in host dir
    candidate = host_dir / f"{target}.md"
    if candidate.exists():
        return candidate

    # Recursive search in vault
    for path in vault_root.rglob(f"{target}.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(vault_root).parts):
            continue
        if path.is_file():
            return path

    return None


def audit_readme(readme: Path, vault_root: Path) -> dict:
    """Audit a single README against its host directory.

    Returns a dict with keys:
        missing_files: filenames referenced but not found
        missing_subdirs: subdir names referenced but not found
        present_files_unlisted: files in the dir that look like they should be in README
        present_subdirs_unlisted: subdirs in the dir that look like they should be in README
        resolved_count: number of references that resolved
        unresolved_count: number of references that did not resolve
    """
    host_dir = readme.parent
    wikilinks, filenames, subdirs = extract_references(readme, host_dir)

    missing_files: list[str] = []
    missing_subdirs: list[str] = []
    resolved_count = 0
    unresolved_count = 0

    # Resolve wikilinks
    for target in sorted(wikilinks):
        # Strip "Folder/" prefix if present (wikilinks can include path)
        name = target.rsplit("/", 1)[-1].strip()
        if not name or name.startswith("_"):
            continue  # skip auto-generated indexes
        if resolve_wikilink(name, host_dir, vault_root):
            resolved_count += 1
        else:
            missing_files.append(name)
            unresolved_count += 1

    # Resolve inline filenames
    for fname in sorted(filenames):
        if not fname.endswith(".md"):
            continue
        candidate = host_dir / fname
        if candidate.exists():
            resolved_count += 1
        else:
            # Try one level up (common pattern)
            if (host_dir.parent / fname).exists():
                resolved_count += 1
            else:
                missing_files.append(fname)
                unresolved_count += 1

    # Resolve inline subdirs
    for subdir in sorted(subdirs):
        candidate = host_dir / subdir
        if candidate.exists() and candidate.is_dir():
            resolved_count += 1
        else:
            missing_subdirs.append(subdir)
            unresolved_count += 1

    # Detect present files/subdirs that might be missing from README
    # Only flag if README has a "📁 Structure" or similar section that should enumerate them
    try:
        text = readme.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        text = ""

    has_structure_section = bool(re.search(r"##\s*📁.*Structure|##\s*Structure\s+du|##\s*Contenu\s+du\s+Vault|##\s*Files?\s+in|##\s*Folder\s+Structure", text, re.IGNORECASE))

    present_files_unlisted: list[str] = []
    present_subdirs_unlisted: list[str] = []

    if has_structure_section:
        # Get actual content of host_dir (excluding README itself and auto-generated indexes)
        try:
            entries = list(host_dir.iterdir())
        except Exception:
            entries = []

        actual_md_files = {
            e.name for e in entries
            if e.is_file() and e.suffix == ".md"
            and not e.name.startswith("README")
            and not e.name.startswith("_index_")
        }
        actual_subdirs = {
            e.name for e in entries
            if e.is_dir() and not e.name.startswith(".")
            and not e.name.startswith("_")
            and e.name not in SKIP_DIRS
        }

        # Files referenced by README
        referenced_files = set()
        for fname in filenames:
            referenced_files.add(fname)
        for target in wikilinks:
            name = target.rsplit("/", 1)[-1].strip()
            if name:
                referenced_files.add(f"{name}.md")

        # Subdirs referenced (from inline + folder wikilinks)
        referenced_subdirs = set(subdirs)
        # Also add subdirs inferred from file wikilinks that point to host dir
        for target in wikilinks:
            name = target.rsplit("/", 1)[-1].strip()
            if name and (host_dir / name).exists() and (host_dir / name).is_dir():
                referenced_subdirs.add(name)

        # Find unlisted
        for f in sorted(actual_md_files - referenced_files):
            # Don't flag very generic names
            if f.startswith("_") or f == "README.md":
                continue
            present_files_unlisted.append(f)

        for d in sorted(actual_subdirs - referenced_subdirs):
            present_subdirs_unlisted.append(d)

    return {
        "missing_files": missing_files,
        "missing_subdirs": missing_subdirs,
        "present_files_unlisted": present_files_unlisted,
        "present_subdirs_unlisted": present_subdirs_unlisted,
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit README <-> filesystem coherence")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit non-zero if issues found")
    parser.add_argument("--scope", help="Limit audit to a path (relative to repo root)", default=None)
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress per-README output")
    args = parser.parse_args()

    scope = VAULT_ROOT / args.scope if args.scope else VAULT_ROOT
    if not scope.exists():
        cprint(f"ERROR: Scope path does not exist: {scope}", "RED", bold=True)
        return 2

    cprint("=" * 60, "CYAN", bold=True)
    cprint("README <-> Filesystem Coherence Audit", "CYAN", bold=True)
    try:
        cprint(f"Scope: {scope.relative_to(VAULT_ROOT)}", "CYAN")
    except ValueError:
        cprint(f"Scope: {scope}", "CYAN")
    cprint("=" * 60, "CYAN", bold=True)

    readmes = list(iter_readmes(scope))
    cprint(f"README files found: {len(readmes)}", "CYAN")

    total_missing = 0
    total_unlisted = 0
    total_resolved = 0
    total_unresolved = 0
    files_with_issues = 0

    for readme in readmes:
        result = audit_readme(readme, VAULT_ROOT)
        total_resolved += result["resolved_count"]
        total_unresolved += result["unresolved_count"]

        n_issues = len(result["missing_files"]) + len(result["missing_subdirs"]) + len(result["present_files_unlisted"]) + len(result["present_subdirs_unlisted"])

        if n_issues == 0:
            if not args.quiet:
                rel = readme.relative_to(VAULT_ROOT)
                cprint(f"  [OK] {rel}", "GREEN")
            continue

        files_with_issues += 1
        total_missing += len(result["missing_files"]) + len(result["missing_subdirs"])
        total_unlisted += len(result["present_files_unlisted"]) + len(result["present_subdirs_unlisted"])

        rel = readme.relative_to(VAULT_ROOT)
        cprint(f"\n  [ISSUES] {rel}", "YELLOW", bold=True)

        if result["missing_files"]:
            cprint(f"    Missing files ({len(result['missing_files'])}):", "RED")
            for f in result["missing_files"]:
                cprint(f"      - {f}", "RED")
        if result["missing_subdirs"]:
            cprint(f"    Missing subdirs ({len(result['missing_subdirs'])}):", "RED")
            for d in result["missing_subdirs"]:
                cprint(f"      - {d}/", "RED")
        if result["present_files_unlisted"]:
            cprint(f"    Present files unlisted in README ({len(result['present_files_unlisted'])}):", "YELLOW")
            for f in result["present_files_unlisted"]:
                cprint(f"      - {f}", "YELLOW")
        if result["present_subdirs_unlisted"]:
            cprint(f"    Present subdirs unlisted in README ({len(result['present_subdirs_unlisted'])}):", "YELLOW")
            for d in result["present_subdirs_unlisted"]:
                cprint(f"      - {d}/", "YELLOW")

    cprint("\n" + "=" * 60, "CYAN", bold=True)
    cprint("Summary", "CYAN", bold=True)
    cprint(f"  README files scanned:        {len(readmes)}", "CYAN")
    cprint(f"  Files with issues:           {files_with_issues}", "YELLOW" if files_with_issues > 0 else "GREEN")
    cprint(f"  Total references:            {total_resolved + total_unresolved}", "CYAN")
    cprint(f"  Resolved:                    {total_resolved}", "GREEN")
    cprint(f"  Unresolved (missing):        {total_unresolved}", "RED" if total_unresolved > 0 else "GREEN")
    cprint(f"  Unlisted present files:      {total_unlisted}", "YELLOW" if total_unlisted > 0 else "GREEN")
    cprint("=" * 60, "CYAN", bold=True)

    # VS Code task: [DIAG] Audit Cohérence READMEs

    if files_with_issues > 0:
        cprint(f"\nAudit reported {files_with_issues} README(s) with potential issues.", "YELLOW", bold=True)
        cprint("Notes:", "CYAN")
        cprint("  - 'Missing' = referenced in README but not found in vault", "CYAN")
        cprint("  - 'Unlisted' = exists in dir but README has Structure section that should mention it", "CYAN")
        cprint("  - Aspirational READMEs (empty dirs, 'Structure cible') should NOT trigger these.", "CYAN")
        cprint("    If a README is intentionally aspirational, add a 'Structure cible' section marker.", "CYAN")
        return 2 if args.fail_on_error else 1

    cprint("\nAudit OK - no README coherence issues found", "GREEN", bold=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
