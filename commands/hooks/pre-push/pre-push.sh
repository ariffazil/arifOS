#!/usr/bin/env bash
set -euo pipefail

REMOTE_NAME="${1:-origin}"
REMOTE_URL="${2:-$(git remote get-url "${1:-origin}")}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GUARD="$REPO_ROOT/scripts/hooks/pre-push/repo_guard.py"

if [[ ! -x "$GUARD" ]]; then
  echo "[WARN] repo_guard.py not executable or missing at $GUARD; allowing push."
  exit 0
fi

python3 "$GUARD" --remote-name "$REMOTE_NAME" --remote-url "$REMOTE_URL"
