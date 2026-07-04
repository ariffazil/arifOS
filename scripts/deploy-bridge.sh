#!/bin/bash
# arifOS Deploy Bridge
# Syncs /root/arifOS source changes to /opt/arifos/app runtime and restarts the service.
# DITEMPA BUKAN DIBERI — Forged, Not Given.

set -e

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
