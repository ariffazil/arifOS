#!/bin/bash
# guard-health-check.sh — gates A3 merge on governance health
# DITEMPA BUKAN DIBERI
set -euo pipefail

ARIFOS_DIR="${ARIFOS_DIR:-/root/arifos}"
MCP_URL="${MCP_URL:-http://localhost:8080}"
ARIFOS_REF="$(git -C "$ARIFOS_DIR" rev-parse HEAD)"

echo "=== arifOS guard health check ==="
echo "arifOS SHA: $ARIFOS_REF"
echo ""

# ── Test 1: constitutional_guard importable ──────────────────
echo -n "Test 1 — constitutional_guard importable... "
python3 - << 'PYEOF'
import sys; sys.path.insert(0, '/root/arifos')
from arifos.core.middleware.constitutional_guard import constitutional_guard
print("OK")
PYEOF
echo ""

# ── Test 2: direct guard returns non-CLAIM_ONLY for hostile input
echo -n "Test 2 — guard upgrades CLAIM_ONLY to proper verdict... "
RESULT=$(python3 - << 'PYEOF'
import sys; sys.path.insert(0, '/root/arifos')
from arifos.core.middleware.constitutional_guard import constitutional_guard
r = constitutional_guard(tool_name="arifos_444_kernel", raw_output={"verdict": "CLAIM_ONLY"})
print(r["verdict"])
PYEOF
)
if [ "$RESULT" = "CLAIM_ONLY" ]; then
    echo "FAIL — guard must upgrade CLAIM_ONLY"
    exit 1
fi
echo "OK (got $RESULT)"

# ── Test 3: MCP server health ──────────────────────────────────
echo -n "Test 3 — MCP server health... "
HTTP_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$MCP_URL/health" || echo "000")
if [ "$HTTP_STATUS" != "200" ]; then
    echo "FAIL (HTTP $HTTP_STATUS)"
    exit 1
fi
echo "OK"

# ── Test 4: AMANAH score via python ────────────────────────────
AMANAH_FILE="$ARIFOS_DIR/logs/amanah_results.json"
if [ -f "$AMANAH_FILE" ]; then
    SCORE=$(python3 -c "import json; print(json.load(open('$AMANAH_FILE'))['amanah_score'])")
    echo -n "Test 4 — AMANAH score >= 85... "
    PASSES=$(python3 -c "import sys; score=float('$SCORE'); sys.exit(0 if score>=85 else 1)" && echo 1 || echo 0)
    if [ "$PASSES" = "0" ]; then
        echo "FAIL (score $SCORE < 85) — guard wiring still needed"
        exit 1
    fi
    echo "OK ($SCORE)"
else
    echo "Test 4 — SKIP (no amanah results)"
fi

echo ""
echo "ALL GUARD HEALTH CHECKS: PASS ✅"
echo "A3 merge gate: OPEN — awaiting Arif F1 approval + guard wiring"
exit 0
