#!/bin/bash
# arifOS Deploy Bridge
# Syncs /root/arifOS source changes to /opt/arifos/app runtime and restarts the service.
# DITEMPA BUKAN DIBERI — Forged, Not Given.

set -e

# ── deployment lease convergence (P0 complete mediation, 2026-10-26) ──────────
# This script mutates the production runtime, so it takes the SAME lease that
# `make deploy-local` takes. Two writers that share one lease serialise; two
# writers with two private locks do not. Refuses rather than interleaves.
_ARIFOS_PY="${ARIFOS_PYTHON:-/opt/arifos/current/venv/bin/python}"
_ARIFOS_LEASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/deploy_lease.py"
_ARIFOS_SHA="$(git -C /root/arifOS rev-parse HEAD 2>/dev/null || echo unknown)"
if ! "$_ARIFOS_PY" "$_ARIFOS_LEASE" acquire --actor "${DEPLOY_ACTOR:-$(whoami)}" \
     --base "$_ARIFOS_SHA" --candidate "$_ARIFOS_SHA" --ttl "${DEPLOY_LEASE_TTL:-1800}" >/dev/null; then
  echo "888_HOLD: HOLD_CONCURRENT_DEPLOY — another deployment owns production; nothing was written" >&2
  exit 3
fi
_arifos_release_lease() {
  local rc=$?
  trap - EXIT INT TERM
  "$_ARIFOS_PY" "$_ARIFOS_LEASE" release --actor "${DEPLOY_ACTOR:-$(whoami)}" \
    --receipt "${0##*/}" >/dev/null 2>&1 || echo "WARNING: lease release failed" >&2
  exit "$rc"
}
trap _arifos_release_lease EXIT INT TERM

DIR="/root/arifOS"
TARGET="/opt/arifos/app"

echo "=== arifOS Deploy Bridge: Syncing changes ==="

# Get current local commit SHA
GIT_SHA=$(git -C "$DIR" rev-parse --short=7 HEAD 2>/dev/null || echo "unknown")
if ! git -C "$DIR" diff --quiet 2>/dev/null; then
  GIT_SHA="${GIT_SHA}-dirty"
fi

echo "Source SHA: $GIT_SHA"
echo "Syncing canonical code to $TARGET..."

# Perform rsync (exclude venv, git, log, caches, etc.)
rsync -av --delete \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='logs/' \
  --exclude='reports/' \
  --exclude='tmp/' \
  --exclude='tests/' \
  --exclude='benchmarks/' \
  "$DIR/" "$TARGET/"

# Set permissions
chmod -R u+rwX,go+rX "$TARGET/arifosmcp/"
chmod 644 "$TARGET/.env" 2>/dev/null || true
chown -R arifos:arifos "$TARGET/" 2>/dev/null || true

# Write git commit marker
echo "$GIT_SHA" > "$TARGET/.git_commit"

echo "Restarting arifOS bare-metal service..."
systemctl restart arifos.service

# Wait for service health
echo "Waiting for kernel health..."
HEALTH_STATUS="unknown"
for i in $(seq 1 15); do
  status=$(curl -s -m 2 http://localhost:8088/health 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || true)
  if [ "$status" = "healthy" ]; then
    HEALTH_STATUS="healthy"
    echo "Kernel healthy after ${i}s"
    break
  fi
  sleep 1
done

if [ "$HEALTH_STATUS" != "healthy" ]; then
  echo "❌ 888_HOLD: kernel did not become healthy!"
  exit 1
fi

echo "Generating federation manifest..."
python3 "$DIR/scripts/generate_federation_manifest.py"

echo "=== Deploy Bridge Sync Completed Successfully ==="
