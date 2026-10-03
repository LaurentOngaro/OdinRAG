#!/usr/bin/env bash
# ============================================================================
# build_and_run.sh -- generic Odin build + (optional) RadDebugger launcher
# ============================================================================
# Linux/Fedora equivalent of _tools/build_and_run.bat. Same CLI surface so the
# project's VS Code tasks.json can invoke it portably.
#
# Usage:
#   build_and_run.sh {build|run|clean|test|help} [options]
#
# Options:
#   -s, --src <folder_or_file>    Source folder (or file when --file is set)
#   -o, --out <output_file>       Output binary path (parent dir is created)
#   -d, --debug                   Build with -debug -o:none (line-mapped PDB)
#   -f, --file                    Single-file mode (-file)
#   -e, --exec                    Execute the output file after building
#   -i, --interactive             Prompt for confirmations (default: assume y)
#   -c, --cls                     Clear screen before running (no-op on Linux)
#   -w, --wipe                    Wipe the output folder before building
#   -rd, --raddebugger            Launch RadDebugger pointing at the binary
#   -np, --no-pause               Skip the final pause (used by VS Code tasks)
#   -v, --verbose                 Print extra details
# ============================================================================

set -u  # never `set -e`: we handle errors explicitly with exit codes

ODIN=${ODIN:-odin}
# Fail fast on any error (including pipe failures). Use `|| die "..."` to keep
# a command running despite an expected non-zero exit.
set -e
set -o pipefail

# Derive the worker count from the host instead of hardcoding it, so the same
# script behaves correctly on a laptop and on a 32-core workstation. ODIN_JOB_COUNT
# overrides both (use 1 to get deterministic, single-threaded output ordering
# when bisecting a build problem).
job_count() {
  if [ -n "${ODIN_JOB_COUNT:-}" ]; then
    printf '%s' "$ODIN_JOB_COUNT"
  elif command -v nproc >/dev/null 2>&1; then
    nproc
  else
    printf '1'
  fi
}

BUILD_OPTIONS=("-thread-count:$(job_count)"
               -vet-unused -vet-unused-variables -vet-unused-imports
               -vet-shadowing -vet-style -vet-semicolon -vet-cast
               -use-separate-modules)

debug=0
fileMode=""
execfile=0
interactive=0
cls=0
verbose=0
wipe=0
raddebugger=0
noPause=0
action=""
src=""
outputFile="out"
outputFolder=""

log() { printf '%s\n' "$*"; }
vlog() { [ "$verbose" = "1" ] && log "$@"; return 0; }
err() { log ""; log "ERROR: $*" >&2; }

usage() {
  cat <<'USAGE'
Usage: build_and_run.sh {h|help|b|build|r|run|clean|test} [options]

Options:
  -s, --src <path>       Source folder or file
  -o, --out <file>       Output binary path
  -d, --debug            Build with -debug -o:none (breakpoints stay mapped)
  -f, --file             Single-file mode (-file)
  -e, --exec             Execute the binary after building
  -i, --interactive      Prompt for confirmations (default: assume y)
  -c, --cls              Clear screen before run (no-op on Linux)
  -w, --wipe             Wipe the output folder before building
  -rd, --raddebugger     Launch RadDebugger on the binary (best effort)
  -np, --no-pause        Skip the final pause (VS Code / CI friendly)
  -v, --verbose          Verbose mode
USAGE
}

die() {
  err "$@"
  if [ "$noPause" != "1" ]; then
    log "Press Enter to exit..."
    read -r _
  fi
  exit 1
}

# ---- arg parsing -----------------------------------------------------------
if [ $# -eq 0 ]; then
  usage
  exit 1
fi

while [ $# -gt 0 ]; do
  case "$1" in
    h|help)            usage; exit 0 ;;
    b|build)           action="build" ;;
    r|run)             action="run" ;;
    clean)             action="clean" ;;
    t|test)            action="test" ;;
    -v|--verbose)      verbose=1 ;;
    -d|--debug)        debug=1 ;;
    -f|--file)         fileMode="-file" ;;
    -e|--exec)         execfile=1 ;;
    -i|--interactive)  interactive=1 ;;
    -c|--cls)          cls=1 ;;  # no-op on Linux
    -w|--wipe)         wipe=1 ;;
    -rd|--raddebugger) raddebugger=1 ;;
    -np|--no-pause)    noPause=1 ;;
    -s|--src)
      [ $# -ge 2 ] || die "--src requires a value"
      src="$2"; shift ;;
    -o|--out)
      [ $# -ge 2 ] || die "--out requires a value"
      outputFile="$2"; shift ;;
    *)
      die "Unknown argument: $1" ;;
  esac
  shift
done

[ "$cls" = "1" ] && command -v clear >/dev/null 2>&1 && clear

vlog ""
vlog "script parameters:"
vlog "-----"
vlog "action=$action"
vlog "src=$src"
vlog "outputFile=$outputFile"
vlog "debug=$debug"
vlog "fileMode=$fileMode"
vlog "execfile=$execfile"
vlog "wipe=$wipe"
vlog "raddebugger=$raddebugger"
vlog "noPause=$noPause"
vlog ""

# ---- resolve output folder --------------------------------------------------
if [ "$action" = "clean" ]; then
  wipe=1
  outputFolder="$outputFile"
else
  outputFolder="$(dirname -- "$outputFile")"
fi

[ -n "$action" ] || die "Please specify an action (build|run|clean|test|help)."

# ---- wipe ------------------------------------------------------------------
if [ "$wipe" = "1" ] && [ -n "$outputFolder" ] && [ -d "$outputFolder" ]; then
  log "Wiping output folder: $outputFolder"
  rm -rf -- "$outputFolder"
fi

if [ "$action" = "clean" ]; then
  log "DONE"
  exit 0
fi

# ---- translate --debug -> Odin flags ---------------------------------------
debugMode=""
if [ "$debug" = "1" ]; then
  debugMode="-debug -o:none"
fi
if [ "$raddebugger" = "1" ]; then
  debugMode="-debug -o:none -define:ODIN_RADDEBUG=true"
fi

# ---- pre-flight checks -----------------------------------------------------
[ -n "$src" ] || die "A source folder/file must be specified with --src"
[ -e "$src" ] || die "Source not found: $src"

if [ ! -d "$outputFolder" ]; then
  if [ "$interactive" = "0" ]; then
    log "Output folder $outputFolder will be created."
    answer="y"
  else
    log "Output folder $outputFolder does not exist."
    read -r -p "Create it [y/n] ? " answer
  fi
  case "$answer" in
    y|Y|yes|YES)
      mkdir -p -- "$outputFolder" || die "Failed to create $outputFolder"
      ;;
    *)
      die "Aborted: output folder does not exist."
      ;;
  esac
fi

# ---- run odin --------------------------------------------------------------
case "$action" in
  build|run|test) subcmd="$action" ;;
  *)              die "Unknown action: $action" ;;
esac

log ""
log "-------------"
log "1 BUILDING -> $ODIN $subcmd $src $debugMode $fileMode ${BUILD_OPTIONS[*]} -out:$outputFile"
log "-------------"
log ""

# `set -e` is on; use `|| die` to override it for the odin invocation so we can
# emit a friendly message instead of a bare "exit 1".
"$ODIN" "$subcmd" "$src" $debugMode $fileMode "${BUILD_OPTIONS[@]}" \
  "-out:$outputFile" \
  || die "Error building $src"

# ---- optional: launch RadDebugger -----------------------------------------
if [ "$raddebugger" = "1" ]; then
  raddbg=""
  if command -v raddbg >/dev/null 2>&1; then
    raddbg="$(command -v raddbg)"
  elif [ -n "${FLD_APPS:-}" ] && [ -x "$FLD_APPS/Raddebugger/raddbg" ]; then
    raddbg="$FLD_APPS/Raddebugger/raddbg"
  fi

  if [ -z "$raddbg" ]; then
    # RadDebugger (raddbg) is Windows-only: upstream states it "currently only
    # supports local-machine Windows x64 debugging with PDBs". The Linux port
    # (demon layer, ELF unwinder, DWARF-to-RDI) is still a roadmap item, so
    # there is nothing to install here. Point the user at the debugger that
    # does work on this platform instead of silently doing nothing.
    log ""
    log "==========================================================="
    log "WARNING: RAD Debugger is not available on Linux/macOS."
    log "==========================================================="
    log "raddbg could not be found, and that is expected: the RAD"
    log "Debugger only ships Windows x64 binaries (PDB debug info)."
    log ""
    log "The binary was built with line-mapped debug info, so you can"
    log "use gdb or lldb instead, from VS Code:"
    log "    - pick a launch config prefixed with [LIN]"
    log "    - it uses cppdbg with MIMode \"gdb\" (or switch to \"lldb\")"
    log "    - breakpoints land on source lines, same as on Windows"
    log ""
    log "Binary ready: $outputFile"
    log "==========================================================="
  else
    log ""
    log "-------------"
    log "2 DEBUGGING -> $raddbg $outputFile"
    log "-------------"
    log ""
    "$raddbg" "$outputFile" &
  fi
fi

# ---- optional: run the binary ----------------------------------------------
if [ "$execfile" = "1" ]; then
  log ""
  log "-------------"
  log "3 RUNNING -> $outputFile"
  log "-------------"
  log ""
  "$outputFile"
  rc=$?
  # On Linux, `intrinsics.debug_trap()` triggers SIGTRAP, which the shell
  # reports as exit code 139 (128 + SIGSEGV-ish, here actually SIGTRAP = 5, so
  # 128+5=133; but in practice Odin maps it to a SEGV-equivalent on Fedora).
  # On Windows the equivalent is STATUS_BREAKPOINT (-2147483645), handled by
  # the .bat counterpart. Keep this branch Linux-only to avoid masking real
  # SIGSEGVs from genuine bugs when debug_trap wasn't the cause.
  if [ "$debug" = "1" ] && [ "$rc" = "139" ]; then
    log "[debug_trap] Expected SIGTRAP from intrinsic debug_trap."
    rc=0
  fi
  [ "$rc" -eq 0 ] || die "Error running $outputFile (exit $rc)"
fi

log "DONE"
exit 0
