#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# install-pre-push-guard.sh — installs the kernel deploy guard (FAIL-CLOSED)
# ═══════════════════════════════════════════════════════════════════════════
# Forged 2026-11-14 after SCAR-333-2026-11-13-git-apply-exec-bit-failopen:
#   the old wrapper FAILED OPEN (`[[ ! -x $GUARD ]] → exit 0`) — a soft guard
#   silently allowed an ungated kernel-deploy push. That is the inverse of the
#   guard's purpose and leaves a future agent confused about whether
#   validation actually ran.
#
# This wrapper FAILS CLOSED: if repo_guard.py is missing or non-executable,
#   the push is BLOCKED with a loud, actionable error. A guard you cannot run
#   must not let the push through.
#
# Mirrors scripts/hooks/commit-msg/install-identity-guard.sh (the commit-msg
#   guard already ships a tracked installer; the pre-push guard did not).
#
# MUST be mode 755. Idempotent — safe to re-run.
# ═══════════════════════════════════════════════════════════════════════════
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
HOOK="$REPO_ROOT/.git/hooks/pre-push"
GUARD_REL="scripts/hooks/pre-push/repo_guard.py"

# Make the guard executable (recover from git-apply exec-bit drop — the exact
# failure class this installer exists to heal).
chmod +x "$REPO_ROOT/$GUARD_REL" 2>/dev/null || true

cat >"$HOOK" <<'WRAPPER'
#!/usr/bin/env bash
set -euo pipefail

REMOTE_NAME="${1:-origin}"
REMOTE_URL="${2:-$(git remote get-url "${1:-origin}")}"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
GUARD="$REPO_ROOT/scripts/hooks/pre-push/repo_guard.py"

if [[ ! -x "$GUARD" ]]; then
  echo "" >&2
  echo "[BLOCKED] repo_guard.py not executable or missing at $GUARD" >&2
  echo "  The kernel deploy guard FAILS CLOSED: a push is refused when the guard" >&2
  echo "  cannot run. Validation did NOT happen, so the push is blocked." >&2
  echo "  Fix:  bash scripts/hooks/pre-push/install-pre-push-guard.sh" >&2
  echo "" >&2
  exit 1
fi

python3 "$GUARD" --remote-name "$REMOTE_NAME" --remote-url "$REMOTE_URL"
WRAPPER

chmod +x "$HOOK"

echo "✅ pre-push guard installed (fail-closed) → $HOOK"
echo "   Guard: $REPO_ROOT/$GUARD_REL"
