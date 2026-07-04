#!/usr/bin/env bash
# drift-check.sh — CI gate for transport contract alignment
# Verifies: port registry, protocol versions, endpoint availability, SEP compliance
# DITEMPA BUKAN DIBERI — Forged 2026-07-03
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

CONTRACT="/root/arifOS/contracts/transport/arifos.transport.v2.json"
PASS=0
FAIL=0
WARN=0

check() {
    local name="$1"
    local status="$2"
    local detail="${3:-}"
    if [ "$status" = "PASS" ]; then
        echo -e "  ${GREEN}✅${NC} $name"
        PASS=$((PASS + 1))
    elif [ "$status" = "WARN" ]; then
        echo -e "  ${YELLOW}⚠️${NC} $name: $detail"
        WARN=$((WARN + 1))
    else
        echo -e "  ${RED}❌${NC} $name: $detail"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "═══════════════════════════════════════════════"
echo " 🔍 DRIFT CHECK — Transport Contract Alignment"
echo "═══════════════════════════════════════════════"
echo ""

# 1. Contract file exists
[ -f "$CONTRACT" ] && check "Contract file exists" "PASS" || check "Contract file exists" "FAIL" "Not found at $CONTRACT"

# 2. Port registry vs actual processes
echo ""
echo "── Port Registry ──"
PORTS=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
reg = c['canonical_port_registry']
for name, info in reg.items():
    if info.get('port'):
        print(f\"{name}:{info['port']}\")
    if info.get('mcp_port'):
        print(f\"{name}:{info['mcp_port']}\")
")
for entry in $PORTS; do
    name="${entry%%:*}"
    port="${entry##*:}"
    if ss -tlnp 2>/dev/null | grep -q ":$port "; then
        check "Port $port ($name)" "PASS"
    else
        check "Port $port ($name)" "WARN" "Not listening — may be down or dynamic"
    fi
done

# 3. Protocol version support
echo ""
echo "── Protocol Versions ──"
PROTOCOLS=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
print('\n'.join(c.get('protocol_versions_supported', [])))
")
CANON=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
print(c.get('canonical_protocol_version', ''))
")
echo "  Canonical: $CANON"
CANON=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
print(c.get('canonical_protocol_version', ''))
")
# Check if arifOS MCP supports the canonical version
if curl -sf -X POST "http://localhost:8088/mcp" \
    -H "Content-Type: application/json" \
    -H "MCP-Protocol-Version: $CANON" \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"'"$CANON"'","capabilities":{},"clientInfo":{"name":"drift-check","version":"1.0"}}}' \
    > /dev/null 2>&1; then
    check "Protocol $CANON (canonical) handshake" "PASS"
else
    check "Protocol $CANON (canonical) handshake" "WARN" "initialize failed — may need restart"
fi

# 4. Required endpoints
echo ""
echo "── Required Endpoints ──"
ENDPOINTS=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
endpoints = [ep['path'] for ep in c.get('required_endpoints', [])]
print('\n'.join(endpoints))
")
for ep in $ENDPOINTS; do
    status=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:8088$ep" 2>/dev/null || echo "000")
    if [ "$status" = "200" ] || [ "$status" = "204" ]; then
        check "Endpoint $ep" "PASS"
    elif [ "$status" != "000" ]; then
        check "Endpoint $ep" "WARN" "HTTP $status on :8088$ep"
    else
        check "Endpoint $ep" "WARN" "No response on :8088$ep"
    fi
done

# 5. SEP compliance table integrity
echo ""
echo "── SEP Compliance ──"
python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
seps = c.get('mcp_spec_compliance', {}).get('sep_compliance', {})
print(f'  {len(seps)} SEPs documented:')
for sep, info in seps.items():
    icon = {'compliant': '✅', 'partial': '🟡', 'not_applicable': '➖', 'acknowledged': '📌'}
    print(f'    {icon.get(info[\"status\"], \"❓\")} {sep}: {info[\"status\"]} — {info[\"note\"][:60]}')
"

# 6. Dual_transport port sync check
echo ""
echo "── Config Sync ──"
CODE_PORT=$(grep -oP "port=\d+" /root/arifOS/arifosmcp/runtime/dual_transport.py 2>/dev/null | grep -oP "\d+" | head -1 || echo "unknown")
CONTRACT_PORT=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
print(c.get('canonical_port_registry', {}).get('arifos', {}).get('port', 'unknown'))
")
if [ "$CODE_PORT" = "$CONTRACT_PORT" ]; then
    check "Port sync (code=$CODE_PORT vs contract=$CONTRACT_PORT)" "PASS"
else
    check "Port sync (code=$CODE_PORT vs contract=$CONTRACT_PORT)" "FAIL" "MISMATCH — dual_transport.py says $CODE_PORT, contract says $CONTRACT_PORT"
fi

# 7. SSE port documented
SSE_PORT=$(python3 -c "
import json
with open('$CONTRACT') as f:
    c = json.load(f)
print(c.get('canonical_port_registry', {}).get('arifos', {}).get('sse_port', 'missing'))
")
if [ "$SSE_PORT" != "missing" ] && [ "$SSE_PORT" != "null" ]; then
    check "SSE port ($SSE_PORT) in contract" "PASS"
else
    check "SSE port documented" "FAIL" "SSE port missing from transport contract"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════"
echo -e " RESULTS:  ${GREEN}$PASS passed${NC}, ${YELLOW}$WARN warnings${NC}, ${RED}$FAIL failures${NC}"
echo "═══════════════════════════════════════════════"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}❌ DRIFT DETECTED — $FAIL failures found. Fix before deployment.${NC}"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  $WARN warnings — review recommended but not blocking.${NC}"
    exit 0
else
    echo -e "${GREEN}✅ No drift detected. All contracts aligned.${NC}"
    exit 0
fi
