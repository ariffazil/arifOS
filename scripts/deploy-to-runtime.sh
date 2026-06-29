#!/usr/bin/env bash
# deploy-to-runtime.sh — Bridge /root/arifOS source → /opt/arifos/app runtime
# DITEMPA BUKAN DIBERI — Forged, Not Given
#
# The arifOS runtime venv has an editable install pointing to /root/arifOS,
# so most Python changes are live immediately. This script additionally syncs
# the package tree into /opt/arifos/app/arifosmcp so explicit filesystem paths
# (e.g. nats heartbeat daemon) stay consistent, then restarts services and
# verifies health.

set -euo pipefail

SRC="/root/arifOS"
DST="/opt/arifos/app"
SERVICES=("arifos.service" "arifOS-NATS-heartbeat.service")

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

# ── Sanity checks ───────────────────────────────────────────────────────────
if [[ ! -d "$SRC/arifosmcp" ]]; then
    log "ERROR: source tree $SRC/arifosmcp not found"; exit 1
fi
if [[ ! -d "$DST/arifosmcp" ]]; then
    log "ERROR: runtime tree $DST/arifosmcp not found"; exit 1
fi

# ── Optional git status warning ─────────────────────────────────────────────
if git -C "$SRC" rev-parse --git-dir >/dev/null 2>&1; then
    if ! git -C "$SRC" diff --quiet; then
        log "WARN: /root/arifOS has uncommitted changes; deploying current working tree"
    fi
fi

# ── Sync package tree (preserve ABI daemon path) ────────────────────────────
log "Syncing $SRC/arifosmcp → $DST/arifosmcp"
rsync -a --delete \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    "$SRC/arifosmcp/" "$DST/arifosmcp/"

# ── Restart services ────────────────────────────────────────────────────────
for svc in "${SERVICES[@]}"; do
    log "Restarting $svc"
    systemctl restart "$svc" || { log "ERROR: failed to restart $svc"; exit 1; }
done

# ── Health gate ─────────────────────────────────────────────────────────────
log "Waiting for arifOS health..."
for i in {1..30}; do
    if curl -sf http://localhost:8088/health >/dev/null 2>&1; then
        log "arifOS health OK"
        break
    fi
    sleep 1
done

if ! curl -sf http://localhost:8088/health >/dev/null 2>&1; then
    log "ERROR: arifOS health check failed after restart"; exit 1
fi

log "Deploy bridge complete"
