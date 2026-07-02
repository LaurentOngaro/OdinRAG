#!/usr/bin/env bash
#
# .kilo/skills/markdown-style/install.sh
#
# One-shot installer for the markdown-style pre-commit hook.
#
# The hook is INFORMATIONAL: it refuses `git commit` when staged .md files
# contain wrapped prose paragraphs (the project's "one paragraph = one line"
# rule, enforced by reflow_md.py). It NEVER auto-modifies files; the user
# controls reflow decisions via `reflow_md.py --apply` (manual only).
#
# Idempotent: refuses to overwrite an existing pre-commit (so the existing
# pre-push hook for the public/private split is preserved). Backup and
# remove the existing hook first if you want to overwrite.
#
# Usage:
#   bash .kilo/skills/markdown-style/install.sh
#
# Bypass per-commit (after install):
#   git commit --no-verify

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_PATH="$REPO_ROOT/.git/hooks/pre-commit"

if [ -e "$HOOK_PATH" ]; then
  echo "[ERR] $HOOK_PATH already exists." >&2
  echo "      This installer refuses to overwrite (the existing hook may" >&2
  echo "      implement features this skill does not know about)." >&2
  echo "" >&2
  echo "      To replace it:" >&2
  echo "        mv $HOOK_PATH ${HOOK_PATH}.bak" >&2
  echo "        bash $SCRIPT_DIR/install.sh" >&2
  exit 1
fi

cat > "$HOOK_PATH" <<'PRECOMMIT_EOF'
#!/usr/bin/env bash
# Pre-commit hook installed by .kilo/skills/markdown-style/install.sh.
# See .kilo/skills/markdown-style/SKILL.md for the workflow.
#
# This hook is INFORMATIONAL: it refuses commits where staged .md files have
# wrapped prose (project rule: one paragraph = one line). It NEVER modifies
# files automatically. To bypass this check for one commit, use
# `git commit --no-verify`.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REFLOW="$REPO_ROOT/_Helpers/scripts/fixes/reflow_md.py"

if [ ! -f "$REFLOW" ]; then
  echo "[pre-commit] reflow script not found at $REFLOW" >&2
  echo "             Skipping markdown style check." >&2
  exit 0
fi

# Get staged .md files (added, copied, modified, renamed — but not deleted).
staged_md=$(git diff --cached --name-only --diff-filter=ACMR -- '*.md' '*.markdown' 2>/dev/null || true)

if [ -z "$staged_md" ]; then
  exit 0
fi

needs_reflow=""
for f in $staged_md; do
  output=$(python "$REFLOW" --quiet --check --path "$f" 2>&1) || true
  if [ -n "$output" ]; then
    needs_reflow="$needs_reflow$output"$'\n'
  fi
done

if [ -n "$needs_reflow" ]; then
  echo "[pre-commit] Reflow needed on these staged .md files:" >&2
  echo "" >&2
  printf '%s' "$needs_reflow" >&2
  echo "" >&2
  echo "Fix manually:" >&2
  echo "  python _Helpers/scripts/fixes/reflow_md.py --path <file>" >&2
  echo "  # Inspect the proposed change, then re-stage: git add <file>" >&2
  echo "" >&2
  echo "Or bypass this check for one commit with:" >&2
  echo "  git commit --no-verify" >&2
  exit 1
fi

exit 0
PRECOMMIT_EOF

# chmod +x - the executable bit is set automatically on git for Windows with a
# shebang; on Unix this is required.
chmod +x "$HOOK_PATH" 2>/dev/null || true

echo "[+] Installed pre-commit hook at $HOOK_PATH"
echo "    - Checks staged .md files via reflow_md.py --quiet --check."
echo "    - Never auto-modifies files."
echo "    - Bypass per-commit: git commit --no-verify"
