#!/usr/bin/env bash
# Configure Git to use the versioned hooks directory (`_Helpers/scripts/dev/hooks`).
# Setting `core.hooksPath` replaces manual file copies and prevents hook drift.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
HOOKS_SRC="$REPO_ROOT/_Helpers/scripts/dev/hooks"

chmod +x "$HOOKS_SRC/pre-push"
git -C "$REPO_ROOT" config --local core.hooksPath "_Helpers/scripts/dev/hooks"
echo "[+] Configured git core.hooksPath -> _Helpers/scripts/dev/hooks"
