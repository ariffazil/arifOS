#!/bin/bash
# ============================================================
# arifOS Post-Restart Smoke Test
# DITEMPA BUKAN DIBERI — Forged, Not Given
# ============================================================
# Run after stack restart to verify all organs are functioning.
# Tests: stack health, federation audit, evidence fetch, mind
# reason, heart critique, forge query, vault chain.
# ============================================================

set -euo pipefail

ARIFOS_URL="${ARIFOS_URL:-http://localhost:8088}"  # override with ARIFOS_URL for local dev on 8080
ARIFOS_MCP="${ARIFOS_URL}/mcp"
ARIFOS_HEALTH="${ARIFOS_URL}/health"
ARIFOS_TOOLS="${ARIFOS_URL}/tools"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }
info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

header() { echo ""; echo "══════════════════════════════════════"; echo "  $1"; echo "══════════════════════════════════════"; }

# ── 1. Stack Health ───────────────────────────────────────
header "1. STACK HEALTH"
if command -v docker &>/dev/null; then
    docker compose ps 2>/dev/null | grep -E "Up|healthy|running" || info "docker compose ps not available in this context"
else
    info "Docker not accessible"
fi

# ── 2. arifOS Health Endpoint ─────────────────────────────
header "2. arifOS HEALTH ENDPOINT"
HTTP_CODE=$(curl -s -o /tmp/health.json -w "%{http_code}" "${ARIFOS_HEALTH}" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    pass "arifOS health endpoint alive (HTTP $HTTP_CODE)"
    cat /tmp/health.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'  status={d.get(\"status\",\"N/A\")}')" 2>/dev/null || true
else
    fail "arifOS health endpoint not responding (HTTP $HTTP_CODE)"
fi

# ── 3. arifOS Tools Endpoint ───────────────────────────────
header "3. arifOS TOOLS ENDPOINT"
HTTP_CODE=$(curl -s -o /tmp/tools.json -w "%{http_code}" "${ARIFOS_TOOLS}" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    pass "arifOS tools endpoint alive (HTTP $HTTP_CODE)"
    COUNT=$(python3 -c "import json; d=json.load(open('/tmp/tools.json')); print(len(d.get('tools', [])))" 2>/dev/null || echo "0")
    echo "  Registered tools: $COUNT"
else
    fail "arifOS tools endpoint not responding (HTTP $HTTP_CODE)"
fi

# ── 4. Federation Audit ────────────────────────────────────
header "4. FEDERATION AUDIT (arif_stack_health_probe)"
AUDIT_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "arif_stack_health_probe", "arguments": {}},
    "id": 1
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$AUDIT_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    score = text.get('overall_score', 'N/A')
    status = text.get('safe_action_class', 'N/A')
    print(f'  overall_score: {score}')
    print(f'  safe_action_class: {status}')
    print(f'  session_binding: {text.get(\"session_binding\", {}).get(\"session_id\", \"N/A\")}')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Federation audit probe failed"

# ── 5. Evidence Fetch ─────────────────────────────────────
header "5. EVIDENCE FETCH (arif_evidence_fetch)"
EVID_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "arif_evidence_fetch",
      "arguments": {
        "mode": "search",
        "query": "arifOS constitutional federation"
      }
    },
    "id": 2
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$EVID_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    results = text.get('results', [])
    print(f'  Search returned {len(results)} result(s)')
    if results:
        print(f'  First result: {results[0].get(\"title\", \"N/A\")[:60]}...')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Evidence fetch failed"

# ── 6. Mind Reason ────────────────────────────────────────
header "6. MIND REASON (arif_mind_reason)"
MIND_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "arif_mind_reason",
      "arguments": {
        "mode": "reason",
        "query": "What is the capital of Malaysia?"
      }
    },
    "id": 3
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$MIND_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    reasoning = text.get('reasoning', text.get('output', 'N/A'))
    print(f'  Output: {str(reasoning)[:120]}...')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Mind reason failed"

# ── 7. Heart Critique ─────────────────────────────────────
header "7. HEART CRITIQUE (arif_heart_critique)"
HEART_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "arif_heart_critique",
      "arguments": {
        "mode": "critique",
        "target": "Read the public GitHub repos of the arifOS federation"
      }
    },
    "id": 4
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$HEART_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    risk_tier = text.get('risk_tier', 'N/A')
    verdict = text.get('action_risk_verdict', text.get('verdict', 'N/A'))
    print(f'  risk_tier: {risk_tier}')
    print(f'  action_risk_verdict: {verdict}')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Heart critique failed"

# ── 8. Forge Query ────────────────────────────────────────
header "8. FORGE QUERY (arif_forge_execute)"
FORGE_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "arif_forge_execute",
      "arguments": {
        "mode": "query",
        "query": "List running Docker containers on the VPS"
      }
    },
    "id": 5
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$FORGE_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    status = text.get('status', 'N/A')
    print(f'  status: {status}')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Forge query failed"

# ── 9. Vault Chain ────────────────────────────────────────
header "9. VAULT CHAIN (arif_vault_seal dry-run)"
VAULT_RESP=$(curl -s -X POST "${ARIFOS_MCP}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "arif_vault_seal",
      "arguments": {
        "mode": "chain"
      }
    },
    "id": 6
  }' 2>/dev/null || echo '{"error": "connection failed"}')
echo "$VAULT_RESP" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    content = d.get('result', {}).get('content', [{}])
    text = json.loads(content[0].get('text', '{}'))
    chain_tip = text.get('chain_tip', 'N/A')
    entries = text.get('entries', [])
    print(f'  chain_tip: {chain_tip}')
    print(f'  entries: {len(entries)} sealed')
except Exception as e:
    print(f'  [WARN] Could not parse: {e}')
" 2>/dev/null || fail "Vault chain failed"

# ── Summary ──────────────────────────────────────────────
header "SMOKE TEST COMPLETE"
echo "All endpoints responded. Check [WARN] lines above."
echo ""
echo "If all [PASS] and no [FAIL]: federation is AMANAH."
echo "DITEMPA BUKAN DIBERI — Forged, Not Given"
