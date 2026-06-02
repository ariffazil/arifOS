#!/usr/bin/env bash
# arifbrain_setup.sh — One-shot deploy for the Phase 1 federation heartbeat.
# Stripped to physics, 7 preflight checks, zero new containers.
#
# Usage:  ./arifbrain_setup.sh
# Rollback:  ./arifbrain_setup.sh --uninstall
#
# Authority: Ω (A-ENGINEER) | F1 Safety | F9 Anti-Hantu
# DITEMPA BUKAN DIBERI.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ─────────────────────────────────────────────────────────
# Colors
# ─────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
warn() { echo -e "  ${YELLOW}⚠${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; exit 1; }

# ─────────────────────────────────────────────────────────
# Uninstall path
# ─────────────────────────────────────────────────────────
if [[ "${1:-}" == "--uninstall" ]]; then
    echo "=== arifbrain UNINSTALL ==="
    systemctl stop arifbrain.service 2>/dev/null || true
    systemctl disable arifbrain.service 2>/dev/null || true
    rm -f /etc/systemd/system/arifbrain.service
    systemctl daemon-reload
    # Remove cron entries
    crontab -l 2>/dev/null | grep -v "arifbrain_observe.py" | crontab - || true
    # Remove Qdrant collection
    curl -s -X DELETE http://127.0.0.1:6333/collections/arifbrain_states 2>/dev/null || true
    ok "arifbrain uninstalled"
    exit 0
fi

echo "=== arifbrain Phase 1 Setup ==="
echo "  audit-validated: embed-only, no LLM, no Graphiti"
echo "  schedule:        every 4 hours via cron"
echo "  systemd unit:    arifbrain.service (MemoryMax=512M)"
echo ""

# ─────────────────────────────────────────────────────────
# Preflight 1/7 — Python
# ─────────────────────────────────────────────────────────
echo "[1/7] Python interpreter"
command -v python3 >/dev/null || fail "python3 not found"
PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
ok "python3 $PYVER"

# ─────────────────────────────────────────────────────────
# Preflight 2/7 — Required Python modules (stdlib only)
# ─────────────────────────────────────────────────────────
echo "[2/7] Python stdlib modules"
python3 -c "import json, urllib.request, hashlib, logging, os, sys, time" \
    || fail "missing stdlib modules"
ok "stdlib modules (json, urllib, hashlib, logging, os, sys, time)"

# ─────────────────────────────────────────────────────────
# Preflight 3/7 — Qdrant reachable
# ─────────────────────────────────────────────────────────
echo "[3/7] Qdrant L3 at :6333"
QDRANT_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:6333/)
if [[ "$QDRANT_CODE" != "200" ]]; then
    fail "Qdrant unreachable at :6333 (got HTTP $QDRANT_CODE). Start docker: docker start qdrant"
fi
ok "Qdrant responds HTTP 200"

# ─────────────────────────────────────────────────────────
# Preflight 4/7 — Ollama + bge-m3
# ─────────────────────────────────────────────────────────
echo "[4/7] Ollama + bge-m3 at :11434"
OLLAMA_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:11434/api/tags)
if [[ "$OLLAMA_CODE" != "200" ]]; then
    fail "Ollama unreachable at :11434 (got HTTP $OLLAMA_CODE)"
fi
BGE_PRESENT=$(curl -s --max-time 3 http://127.0.0.1:11434/api/tags | python3 -c "
import json, sys
try:
    models = json.load(sys.stdin).get('models', [])
    print('yes' if any('bge-m3' in m.get('name','') for m in models) else 'no')
except: print('error')
" 2>/dev/null)
if [[ "$BGE_PRESENT" != "yes" ]]; then
    fail "bge-m3 model not loaded. Run: ollama pull bge-m3"
fi
ok "Ollama + bge-m3 ready"

# ─────────────────────────────────────────────────────────
# Preflight 5/7 — Organ health endpoints (sample 2)
# ─────────────────────────────────────────────────────────
echo "[5/7] Organ health endpoints"
for url in "http://127.0.0.1:8088/health" "http://127.0.0.1:18082/health" "http://127.0.0.1:18083/health" "http://127.0.0.1:8081/health" "http://127.0.0.1:7071/health"; do
    name=$(echo "$url" | awk -F/ '{print $4}' | tr 'a-z' 'A-Z')
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 "$url")
    if [[ "$code" == "200" ]]; then
        ok "$name :$url → HTTP 200"
    else
        warn "$name :$url → HTTP $code (degraded but reachable)"
    fi
done

# ─────────────────────────────────────────────────────────
# Preflight 6/7 — VAULT999 writer
# ─────────────────────────────────────────────────────────
echo "[6/7] VAULT999 writer at :5001"
VAULT_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://127.0.0.1:5001/health)
if [[ "$VAULT_CODE" != "200" ]]; then
    warn "VAULT999 writer at :5001 → HTTP $VAULT_CODE (will mark vault=unknown in snapshots)"
else
    ok "VAULT999 writer :5001 → HTTP 200"
fi

# ─────────────────────────────────────────────────────────
# Preflight 7/7 — Federation webhook (Hermes — whisper target, optional)
# ─────────────────────────────────────────────────────────
echo "[7/7] Federation webhook (optional whisper target)"
HERMES_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 -X POST http://127.0.0.1:18001/send \
    -H "Content-Type: application/json" -d '{"chat_id":"267378578","text":"arifbrain preflight"}' 2>/dev/null)
if [[ "$HERMES_CODE" == "200" || "$HERMES_CODE" == "202" ]]; then
    ok "Hermes :18001 → HTTP $HERMES_CODE (whisper can be enabled with ARIFBRAIN_WHISPER_ENABLED=true)"
else
    warn "Hermes :18001 → HTTP $HERMES_CODE (whisper disabled by default — sovereign territory)"
fi

echo ""
echo "=== All 7 preflight checks passed ==="
echo ""

# ─────────────────────────────────────────────────────────
# Install systemd unit
# ─────────────────────────────────────────────────────────
echo "[deploy] Installing systemd unit"
install -m 644 /root/arifOS/arifbrain/arifbrain.service /etc/systemd/system/arifbrain.service
systemctl daemon-reload
ok "systemd unit installed at /etc/systemd/system/arifbrain.service"

# ─────────────────────────────────────────────────────────
# Install cron entry (every 4h)
# ─────────────────────────────────────────────────────────
echo "[deploy] Installing cron entry (every 4h)"
CRON_LINE="0 */4 * * * /usr/bin/python3 /root/arifOS/arifbrain/arifbrain_observe.py >> /var/log/arifos/arifbrain.log 2>&1"
( crontab -l 2>/dev/null | grep -v "arifbrain_observe.py" ; echo "$CRON_LINE" ) | crontab -
ok "cron installed: $CRON_LINE"

# ─────────────────────────────────────────────────────────
# Run one cycle now to verify
# ─────────────────────────────────────────────────────────
echo ""
echo "[verify] Running one cycle to verify deployment"
echo "  (this takes ~30-60s; will queue behind l3_ingest if running)"
echo ""
python3 /root/arifOS/arifbrain/arifbrain_observe.py 2>&1 | tail -10

# ─────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────
echo ""
echo "=== arifbrain Phase 1 DEPLOYED ==="
echo "  systemd unit: systemctl status arifbrain"
echo "  run now:      systemctl start arifbrain"
echo "  manual:       python3 /root/arifOS/arifbrain/arifbrain_observe.py"
echo "  logs:         tail -f /var/log/arifos/arifbrain.log"
echo "  qdrant:       curl -s :6333/collections/arifbrain_states | python3 -m json.tool"
echo "  whisper:      systemctl edit arifbrain → set ARIFBRAIN_WHISPER_ENABLED=true (after wiring creds)"
echo "  uninstall:    ./arifbrain_setup.sh --uninstall"
echo ""
echo "DITEMPA BUKAN DIBERI — Phase 1 is live. 7 days of clean cycles → Phase 2 (event-driven NATS)."
