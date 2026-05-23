#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
HOOK_SRC="$REPO_ROOT/scripts/hooks/pre-push/pre-push.sh"
HOOK_DST="$REPO_ROOT/.git/hooks/pre-push"

if [[ ! -x "$HOOK_SRC" ]]; then
  echo "Hook source missing or not executable: $HOOK_SRC"
  exit 1
fi

cp "$HOOK_SRC" "$HOOK_DST"
chmod +x "$HOOK_DST"

echo "Installed pre-push hook: $HOOK_DST"
echo "Guard script: $REPO_ROOT/scripts/hooks/pre-push/repo_guard.py"
