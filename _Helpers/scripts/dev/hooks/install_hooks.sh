#!/usr/bin/env bash
# Install versioned git hooks into .git/hooks/
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
HOOKS_SRC="$REPO_ROOT/_Helpers/scripts/dev/hooks"
HOOKS_DEST="$REPO_ROOT/.git/hooks"

if [ ! -d "$HOOKS_DEST" ]; then
  echo "Error: .git/hooks directory not found at $HOOKS_DEST" >&2
  exit 1
fi

for hook in "$HOOKS_SRC"/*; do
  hook_name="$(basename "$hook")"
  if [ "$hook_name" = "install_hooks.sh" ]; then
    continue
  fi
  cp "$hook" "$HOOKS_DEST/$hook_name"
  chmod +x "$HOOKS_DEST/$hook_name"
  echo "[+] Installed hook: $hook_name -> .git/hooks/$hook_name"
done
