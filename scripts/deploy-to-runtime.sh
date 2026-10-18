#!/usr/bin/env bash
# deploy-to-runtime.sh — Bridge /root/arifOS source → runtime import surface
# DITEMPA BUKAN DIBERI — Forged, Not Given
#
# F13 2026-10-18: the previous header claimed "the runtime venv has an
# editable install pointing to /root/arifOS". It does not. Probe showed a
# REAL directory at:
#   /opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp
# so syncing only /opt/arifos/app/arifosmcp and restarting was a silent
# no-op — the kernel kept importing site-packages. This script now asks the
# venv where it actually imports from, syncs that path too, and verifies
# parity BEFORE restarting anything.

set -euo pipefail

SRC="/root/arifOS"
DST="/opt/arifos/app"
VENV_PY="/opt/arifos/current/venv/bin/python"
SERVICES=("arifos.service" "arifOS-NATS-heartbeat.service")

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

# ── Sanity checks ───────────────────────────────────────────────────────────
if [[ ! -d "$SRC/arifosmcp" ]]; then
    log "ERROR: source tree $SRC/arifosmcp not found"; exit 1
fi
if [[ ! -d "$DST/arifosmcp" ]]; then
    log "ERROR: runtime tree $DST/arifosmcp not found"; exit 1
fi
if [[ ! -x "$VENV_PY" ]]; then
    log "ERROR: runtime venv python not found at $VENV_PY"; exit 1
fi

# ── Optional git status warning ─────────────────────────────────────────────
if git -C "$SRC" rev-parse --git-dir >/dev/null 2>&1; then
    if ! git -C "$SRC" diff --quiet; then
        log "WARN: /root/arifOS has uncommitted changes; deploying current working tree"
    fi
fi

# ── Resolve the ACTUAL import path (no assumptions) ─────────────────────────
# find_spec locates the package without executing its __init__.py.
log "Resolving live arifosmcp import path via $VENV_PY"
if ! LIVE_PKG="$("$VENV_PY" -I - <<'PY'
import importlib.util
import sys

spec = importlib.util.find_spec("arifosmcp")
if spec is None or not spec.submodule_search_locations:
    sys.exit(2)
print(next(iter(spec.submodule_search_locations)))
PY
)"; then
    log "ERROR: cannot resolve arifosmcp import path from runtime venv"; exit 1
fi
log "Live import path: $LIVE_PKG"

# ── Sync package tree ───────────────────────────────────────────────────────
sync_tree() {
    local dst="$1"
    if [[ "$(realpath "$dst")" == "$(realpath "$SRC/arifosmcp")" ]]; then
        log "SKIP $dst (identical to source tree)"
        return 0
    fi
    log "Syncing $SRC/arifosmcp → $dst"
    rsync -a --delete \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        "$SRC/arifosmcp/" "$dst/"
}

sync_tree "$DST/arifosmcp"
sync_tree "$LIVE_PKG"

# ── Parity gate: the live import surface must carry SOURCE CONTENT ──────────
# The two destinations are different trees by design, so equality between
# them is NOT the invariant — content is. (2026-10-18: an earlier version of
# this gate asserted $LIVE_PKG == $DST/arifosmcp and fired falsely on a
# perfectly good deploy, because the kernel imports from site-packages while
# this script also maintains /opt/arifos/app.)
if [[ ! -f "$LIVE_PKG/__init__.py" ]]; then
    log "ERROR: $LIVE_PKG has no __init__.py — cannot verify parity"; exit 1
fi

if ! LIVE_PKG_AFTER="$("$VENV_PY" -I - <<'PY'
import importlib.util
import sys

spec = importlib.util.find_spec("arifosmcp")
if spec is None or not spec.submodule_search_locations:
    sys.exit(2)
print(next(iter(spec.submodule_search_locations)))
PY
)"; then
    log "ERROR: venv could not re-resolve arifosmcp after sync"; exit 1
fi
if [[ "$LIVE_PKG_AFTER" != "$LIVE_PKG" ]]; then
    log "ERROR: import path moved during deploy ($LIVE_PKG → $LIVE_PKG_AFTER)"
    exit 1
fi

for tree in "$DST/arifosmcp" "$LIVE_PKG"; do
    if ! diff -rq \
            --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
            "$SRC/arifosmcp" "$tree" >/dev/null 2>&1; then
        log "ERROR: tree drift after sync — $tree does not match source:"
        diff -rq --exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' \
            "$SRC/arifosmcp" "$tree" 2>&1 | head -20
        exit 1
    fi
done

src_sha="$(sha256sum "$SRC/arifosmcp/__init__.py" | cut -d' ' -f1)"
live_sha="$(sha256sum "$LIVE_PKG/__init__.py" | cut -d' ' -f1)"
if [[ "$src_sha" != "$live_sha" ]]; then
    log "ERROR: live arifosmcp/__init__.py (${live_sha:0:12}) != source (${src_sha:0:12})"
    exit 1
fi
log "Parity OK: $LIVE_PKG byte-matches source (${src_sha:0:12})"

# ── Write deploy receipt (fail-closed provenance binding) ───────────────────
RECEIPTS_DIR="/opt/arifos/current/receipts"
NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
COMMIT_SHA="$(git -C "$SRC" rev-parse HEAD)"
BRANCH="$(git -C "$SRC" rev-parse --abbrev-ref HEAD)"
HOST="$(hostname)"
DEPLOYED_BY="$(whoami)"
RECEIPT_FILE="$RECEIPTS_DIR/${NOW_UTC}.json"

log "Writing deploy receipt to $RECEIPT_FILE"
mkdir -p "$RECEIPTS_DIR" || { log "ERROR: failed to create $RECEIPTS_DIR"; exit 1; }

cat <<EOF > "$RECEIPT_FILE" || { log "ERROR: failed to write $RECEIPT_FILE"; exit 1; }
{
  "commit_sha": "$COMMIT_SHA",
  "branch": "$BRANCH",
  "build_time": "$NOW_UTC",
  "parity_hash": "$src_sha",
  "host": "$HOST",
  "deployed_by": "$DEPLOYED_BY"
}
EOF

ln -sf "$RECEIPT_FILE" "$RECEIPTS_DIR/latest.json" || cp -f "$RECEIPT_FILE" "$RECEIPTS_DIR/latest.json" || {
    log "ERROR: failed to update $RECEIPTS_DIR/latest.json"; exit 1;
}
log "Deploy receipt recorded: commit=${COMMIT_SHA:0:12} branch=$BRANCH"

# ── Update deployment commit stamps (SOT parity) ───────────────────────────
echo -n "${COMMIT_SHA:0:7}" > /opt/arifos/releases/deployed-commit
echo -n "$COMMIT_SHA" > /opt/arifos/app/.git_commit
echo -n "$COMMIT_SHA" > "$SRC/.git_commit"
if [[ -f /opt/arifos/releases/release-manifest.json ]]; then
    python3 -c "
import json
p = '/opt/arifos/releases/release-manifest.json'
with open(p) as f:
    d = json.load(f)
d['git_commit'] = '${COMMIT_SHA:0:7}'
d['origin_main_commit'] = '${COMMIT_SHA:0:7}'
with open(p, 'w') as f:
    json.dump(d, f, indent=2)
" || log "WARN: could not update release-manifest.json"
fi
log "Deployment commit stamps updated to ${COMMIT_SHA:0:7}"

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
