#!/usr/bin/env bash
# ============================================================================
# create_junctions.sh -- create the _refs/ symlinks to the local Odin SDK
# ============================================================================
# Linux/Fedora equivalent of create_junctions.ps1. The PowerShell version
# creates NTFS junctions pointing at $FLD_APPS\_odin\{core,examples,vendor};
# this script creates POSIX symlinks pointing at the local Odin distribution.
#
# WHY THE LINKS EXIST
#   ols.json declares three collections (core, examples, vendor) resolved
#   through _refs/. Odin resolves `import "core:fmt"` against the real SDK
#   path, so the editor needs the same three subtrees visible from the project.
#
# IDEMPOTENCY
#   Re-running is safe. Each link is validated before being touched: a valid
#   link is left alone, a stale or broken entry is replaced. This mirrors the
#   New-Or-Repair-Junction helper in the .ps1 version.
#
# OVERRIDING THE ODIN ROOT
#   The SDK root is auto-detected, in order:
#     1. $ODIN_ROOT            (explicit override)
#     2. `odin root`           (what the compiler on PATH reports)
#     3. /opt/odin, $FLD_OLS_DIST, $ODIN_INSTALL_DIR, ~/.odin
#   Override explicitly with:  ODIN_ROOT=/path/to/odin ./create_junctions.sh
# ============================================================================

set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: create_junctions.sh [options]

Creates or repairs the _refs/{core,examples,vendor} symlinks that point at
the local Odin SDK, so ols.json can resolve its collections.

Options:
  -f, --force      Recreate all links even when they already point correctly
  -v, --verbose    Print the detected Odin root and per-link details
  -h, --help       Show this help

Environment:
  ODIN_ROOT        Explicit path to the Odin distribution root (contains
                   base/ core/ examples/ vendor/). Overrides auto-detection.

Exit codes:
  0  success
  1  wrong platform (not Linux/macOS)
  2  Odin root not found
  3  _refs/ folder missing
USAGE
}

FORCE=0
VERBOSE=0

while [ $# -gt 0 ]; do
  case "$1" in
    -f|--force)   FORCE=1 ;;
    -v|--verbose) VERBOSE=1 ;;
    -h|--help)    usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
  shift
done

log()  { printf '%s\n' "$*"; }
vlog() { [ "$VERBOSE" = "1" ] && printf '%s\n' "$*"; return 0; }
# die <message> [exit_code] - the code is consumed, never printed.
die() {
  local message="$1" code="${2:-1}"
  printf 'ERROR: %s\n' "$message" >&2
  exit "$code"
}

# ----------------------------------------------------------------------------
# Platform guard: the .ps1 stays for Windows, this one is for POSIX.
# ----------------------------------------------------------------------------
case "$(uname -s)" in
  Linux*)  ;;
  Darwin*) ;;
  *) die "This script targets Linux/macOS. On Windows use create_junctions.ps1." 1 ;;
esac

# ----------------------------------------------------------------------------
# Resolve the project root and the _refs folder (script lives in <root>/_tools).
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
REFS_DIR="$PROJECT_ROOT/_refs"

vlog "Script directory : $SCRIPT_DIR"
vlog "Project root     : $PROJECT_ROOT"
vlog "_refs folder     : $REFS_DIR"

[ -d "$REFS_DIR" ] || die "_refs folder not found: $REFS_DIR
Create it first (mkdir -p _refs), then re-run this script." 3

# ----------------------------------------------------------------------------
# Detect the Odin SDK root.
# ----------------------------------------------------------------------------
detect_odin_root() {
  # 1. explicit override. It is validated strictly: if the user names a root,
  #    a wrong one must fail loudly rather than silently skip every link.
  if [ -n "${ODIN_ROOT:-}" ]; then
    if [ -d "$ODIN_ROOT/vendor" ] && [ -d "$ODIN_ROOT/core" ]; then
      printf '%s\n' "$ODIN_ROOT"
      return 0
    fi
    return 1
  fi

  # 2. ask the compiler on PATH
  if command -v odin >/dev/null 2>&1; then
    local reported
    reported="$(odin root 2>/dev/null || true)"
    # `odin root` may print the binary path; the SDK root is its parent.
    if [ -n "$reported" ] && [ -d "$reported" ]; then
      if [ -d "$reported/vendor" ] && [ -d "$reported/core" ]; then
        printf '%s\n' "$reported"
        return 0
      fi
      local parent
      parent="$(dirname -- "$reported")"
      if [ -d "$parent/vendor" ] && [ -d "$parent/core" ]; then
        printf '%s\n' "$parent"
        return 0
      fi
    fi
  fi

  # 3. well-known locations
  local candidate
  for candidate in \
      "${FLD_ODS_DIST:-}" \
      /opt/odin \
      "${ODIN_INSTALL_DIR:-}" \
      "${HOME}/.odin" \
      /usr/local/share/odin \
      /usr/share/odin
  do
    [ -n "$candidate" ] || continue
    if [ -d "$candidate/vendor" ] && [ -d "$candidate/core" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

if ! ODIN_SDK_ROOT="$(detect_odin_root)"; then
  # A user-supplied ODIN_ROOT that lacks core/ or vendor/ is a configuration
  # mistake, not an auto-detection miss: report it precisely.
  if [ -n "${ODIN_ROOT:-}" ]; then
    die "ODIN_ROOT does not look like an Odin SDK root: $ODIN_ROOT
Expected it to contain core/ and vendor/ subfolders.
Check the path, or unset ODIN_ROOT to fall back to auto-detection." 2
  fi
  die "Could not auto-detect the Odin SDK root.
Looked at: 'odin root', \$FLD_OLS_DIST, /opt/odin, \$ODIN_INSTALL_DIR, ~/.odin, /usr/share/odin

Re-run with an explicit path, for example:
  ODIN_ROOT=/opt/odin ./create_junctions.sh" 2
fi

# `odin root` reports a trailing separator, and the candidate list may hold a
# user-supplied path with one. Strip it so the links read "/opt/odin/core"
# rather than "/opt/odin//core" and so readlink comparison stays exact.
ODIN_SDK_ROOT="${ODIN_SDK_ROOT%/}"

log "Odin SDK root: $ODIN_SDK_ROOT"
vlog "Detected via  : ${ODIN_ROOT:-(auto)}"

# ----------------------------------------------------------------------------
# Validate the link.
# Returns 0 when $1 already points at $2, 1 otherwise.
# ----------------------------------------------------------------------------
link_is_valid() {
  local link="$1" target="$2"

  [ -L "$link" ] || return 1
  [ -e "$link" ] || return 1              # broken symlink
  [ -d "$link" ] || return 1

  # Compare the resolved paths, not the raw link text: a link created by the
  # PowerShell version (or with a trailing slash) resolves to the same place.
  local current resolved
  current="$(readlink -- "$link")"
  resolved="$(cd -- "$current" 2>/dev/null && pwd)" || return 1
  local expected
  expected="$(cd -- "$target" 2>/dev/null && pwd)" || return 1
  [ "$resolved" = "$expected" ]
}

# ----------------------------------------------------------------------------
# Create or repair a single link.
# ----------------------------------------------------------------------------
create_or_repair() {
  local name="$1"
  local source="$ODIN_SDK_ROOT/$name"
  local link="$REFS_DIR/$name"

  if [ ! -d "$source" ]; then
    log "  [skip] $name - not present in the SDK ($source)"
    return 0
  fi

  if [ "$FORCE" -eq 0 ] && link_is_valid "$link" "$source"; then
    log "  [ok]   $name -> $source (already valid)"
    return 0
  fi

  # Remove whatever is there: a stale symlink, a broken one, or a real
  # directory left over from a previous run on another OS.
  if [ -e "$link" ] || [ -L "$link" ]; then
    if [ -d "$link" ] && [ ! -L "$link" ]; then
      die "$link is a real directory, not a symlink.
Remove or rename it manually, then re-run this script." 1
    fi
    rm -f -- "$link"
    vlog "         removed stale entry at $link"
  fi

  ln -s -- "$source" "$link"
  log "  [fixed] $name -> $source"
}

# ----------------------------------------------------------------------------
# Main.
# ----------------------------------------------------------------------------
log "Creating _refs junctions (POSIX symlinks) in $REFS_DIR"
create_or_repair core
create_or_repair examples
create_or_repair vendor

log ""
log "Done. Verify with: ls -la $REFS_DIR"
