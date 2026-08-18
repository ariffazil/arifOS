#!/usr/bin/env bash
# rollback-arif-memory-idempotency.sh
# Rollback script for arif_memory idempotency key implementation
# Reverts the one-line payload injection fix and cleans up Redis dedup index
#
# Usage: make rollback-arif-memory-idempotency
# Or:    bash scripts/rollback-arif-memory-idempotency.sh
#
# F1 AMANAH: This script exists BEFORE implementation per spec.
# DITEMPA BUKAN DIBERI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="$REPO_ROOT/arifosmcp/runtime/megaTools/tool_13_arif_memory.py"
SNAPSHOT_DIR="$REPO_ROOT/forge_work/zen-snapshots"

echo "=== arif_memory idempotency key rollback ==="
echo "Target: $TARGET"
echo ""

# 1. Snapshot current state
TIMESTAMP=$(date -u +%Y%m%dT%H%M%S)
SNAP_FILE="$SNAPSHOT_DIR/${TIMESTAMP}-pre-idempotency-rollback-tool_13_arif_memory.py"
mkdir -p "$SNAPSHOT_DIR"
cp -a "$TARGET" "$SNAP_FILE"
echo "[1/4] Snapshot saved: $SNAP_FILE"

# 2. Remove the idempotency_key injection (the fix we applied)
# The fix added these two lines after line 305:
#   if idempotency_key:
#       payload["idempotency_key"] = idempotency_key
if grep -q 'payload\["idempotency_key"\] = idempotency_key' "$TARGET"; then
    # Use sed to remove the two-line block
    sed -i '/^    if idempotency_key:$/,/^        payload\["idempotency_key"\] = idempotency_key$/d' "$TARGET"
    echo "[2/4] Removed idempotency_key injection from arif_memory"
else
    echo "[2/4] idempotency_key injection not found (already reverted?)"
fi

# 3. Clean up Redis dedup index (if any entries exist)
if command -v redis-cli &>/dev/null; then
    # Scan for memory_idempotency:* keys and delete them
    KEYS=$(redis-cli --scan --pattern "memory_idempotency:*" 2>/dev/null || true)
    if [ -n "$KEYS" ]; then
        echo "$KEYS" | xargs redis-cli DEL 2>/dev/null || true
        KEY_COUNT=$(echo "$KEYS" | wc -l)
        echo "[3/4] Deleted $KEY_COUNT Redis dedup keys"
    else
        echo "[3/4] No Redis dedup keys found"
    fi
else
    echo "[3/4] redis-cli not available — skip Redis cleanup"
fi

# 4. Verify rollback
if grep -q 'payload\["idempotency_key"\] = idempotency_key' "$TARGET"; then
    echo "[4/4] FAIL: idempotency_key injection still present after rollback"
    echo "  Restoring snapshot..."
    cp -a "$SNAP_FILE" "$TARGET"
    exit 1
else
    echo "[4/4] Rollback verified — idempotency_key injection removed"
fi

echo ""
echo "=== Rollback complete ==="
echo "Snapshot: $SNAP_FILE"
echo "To restore the fix: git checkout $TARGET"
echo "To restore from snapshot: cp $SNAP_FILE $TARGET"
