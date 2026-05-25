#!/bin/bash
# check-estate-invariants.sh — arifOS Federation Estate Invariant Validator
# DITEMPA BUKAN DIBERI
# Run this before ANY edit to ensure you are not perpetuating stale state.
#
# Exits 0 if all invariants pass.
# Exits 1 if any invariant fails.
# No flags needed — run from any directory.

set -euo pipefail

FAILED=0
REPORT=""

pass() { echo "✅ $1"; }
fail() { echo "❌ $1"; FAILED=1; REPORT="$REPORT\n  - $1"; }

echo "═══════════════════════════════════════════"
echo " arifOS Federation Estate Invariant Check"
echo " $(date -Iseconds)"
echo "═══════════════════════════════════════════"
echo ""

# ── Port invariants ──────────────────────────────────────────────────────────

check_stale_port() {
    local file="$1"
    local stale="$2"
    local correct="$3"
    local context="$4"
    if grep -q "$stale" "$file" 2>/dev/null; then
        fail "STALE PORT: $file contains '$stale' (should be '$correct') — $context"
    else
        pass "Port invariant: $file has no '$stale'"
    fi
}

echo "── Port Invariants ──────────────────────"

# arifOS must not be on 8080 in any active config
for repo in arifOS A-FORGE arif-sites WEALTH; do
    for f in $(find /root/$repo -maxdepth 3 \( -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null); do
        check_stale_port "$f" "localhost:8080" "localhost:8088" "arifOS MCP"
        check_stale_port "$f" "127.0.0.1:8080" "127.0.0.1:8088" "arifOS MCP"
        check_stale_port "$f" ":8080/mcp" ":8088/mcp" "arifOS MCP"
    done
done

# GEOX must not be on 8081 in any active config
for repo in arifOS A-FORGE arif-sites WEALTH; do
    for f in $(find /root/$repo -maxdepth 3 \( -name "*.md" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" \) 2>/dev/null); do
        check_stale_port "$f" "localhost:8081" "localhost:18081" "GEOX daemon"
        check_stale_port "$f" "127.0.0.1:8081" "127.0.0.1:18081" "GEOX daemon"
    done
done

# arifOS Caddyfile routing
if [ -f /root/arifOS/Caddyfile ]; then
    CADDY_ARIFOS=$(grep -c "127.0.0.1:8080" /root/arifOS/Caddyfile 2>/dev/null || echo 0)
    if [ "$CADDY_ARIFOS" -gt 0 ]; then
        fail "Caddyfile: arifOS still routing to :8080 (dead port)"
    else
        pass "Caddyfile: arifOS routing not on :8080"
    fi
    CADDY_GEOX=$(grep -c "127.0.0.1:8081" /root/arifOS/Caddyfile 2>/dev/null || echo 0)
    if [ "$CADDY_GEOX" -gt 0 ]; then
        fail "Caddyfile: GEOX still routing to :8081 (wrong port, daemon is on :18081)"
    else
        pass "Caddyfile: GEOX routing not on :8081"
    fi
fi

echo ""

# ── Service state invariants ────────────────────────────────────────────────

echo "── Service State Invariants ──────────────"

# WEALTH must have governance wrapper active
if systemctl is-active wealth-organ &>/dev/null; then
    pass "WEALTH: systemd service is active"
    if curl -s --max-time 5 http://127.0.0.1:18082/health 2>/dev/null | grep -q '"status":"healthy"'; then
        pass "WEALTH: /health returns healthy"
    else
        fail "WEALTH: /health not healthy or not reachable"
    fi
    LOG=$(journalctl -u wealth-organ --no-pager -n 50 2>/dev/null | grep "governance\|GOVERNANCE" | tail -1)
    if echo "$LOG" | grep -qi "governance wrapper active"; then
        pass "WEALTH: governance wrapper confirmed ACTIVE"
    else
        fail "WEALTH: governance wrapper not confirmed active in logs"
    fi
else
    fail "WEALTH: systemd service not active"
fi

# arifOS must be accessible on 8088
if curl -s --max-time 5 http://127.0.0.1:8088/health 2>/dev/null | grep -q '"status":"healthy"'; then
    pass "arifOS: /health on 8088 returns healthy"
else
    fail "arifOS: /health on 8088 not healthy"
fi

# GEOX must be accessible on 18081
if curl -s --max-time 5 http://127.0.0.1:18081/health 2>/dev/null | grep -q '"status":"ok"'; then
    pass "GEOX: /health on 18081 returns ok"
else
    fail "GEOX: /health on 18081 not ok"
fi

echo ""

# ── Package structure invariants ─────────────────────────────────────────────

echo "── Package Structure Invariants ──────────"

# WEALTH internal/ must be a package
if [ -f /root/WEALTH/internal/__init__.py ]; then
    pass "WEALTH: internal/__init__.py exists (package)"
else
    fail "WEALTH: internal/__init__.py MISSING — governance imports will fail"
fi

# WEALTH organ_governance must use relative import in monolith
if grep -q "^    from organ_governance import" /root/WEALTH/internal/monolith.py 2>/dev/null; then
    fail "WEALTH: monolith.py uses bare 'from organ_governance' (must be relative)"
else
    pass "WEALTH: monolith.py uses relative organ_governance import"
fi

echo ""

# ── Public endpoint invariants ────────────────────────────────────────────────

echo "── Public Endpoint Invariants ───────────"

check_public_health() {
    local domain="$1"
    local expected_status="$2"
    local result
    result=$(curl -s --max-time 8 "https://$domain/health" -k 2>/dev/null)
    if echo "$result" | grep -q "$expected_status"; then
        pass "Public $domain/health: $expected_status"
    else
        fail "Public $domain/health: expected '$expected_status', got: $(echo $result | head -c100)"
    fi
}

check_public_404() {
    local domain="$1"
    local result
    result=$(curl -s --max-time 8 "https://$domain/health" -k -o /dev/null -w "%{http_code}" 2>/dev/null)
    if [ "$result" = "404" ]; then
        pass "Public $domain: returns 404 (correct — intentionally disabled)"
    else
        fail "Public $domain: returns $result, expected 404"
    fi
}

check_public_health "arifos.arif-fazil.com" '"status":"healthy"'
check_public_health "geox.arif-fazil.com" '"status":"ok"'
check_public_health "wealth.arif-fazil.com" '"status":"healthy"'
check_public_404 "well.arif-fazil.com"

echo ""

# ── MCP config invariants ───────────────────────────────────────────────────

echo "── MCP Config Invariants ────────────────"

# A-FORGE .mcp.json must not have stale arifOS endpoint
if [ -f /root/A-FORGE/.mcp.json ]; then
    if grep -q "localhost:8080\|127.0.0.1:8080\|:8080/mcp" /root/A-FORGE/.mcp.json 2>/dev/null; then
        fail "A-FORGE .mcp.json: stale arifOS endpoint :8080 found"
    else
        pass "A-FORGE .mcp.json: no stale :8080 endpoint"
    fi
fi

echo ""

# ── Git state invariants ────────────────────────────────────────────────────

echo "── Git State Invariants ─────────────────"

# arifOS must be on main branch (not side branch)
ARIFOS_BRANCH=$(git -C /root/arifOS symbolic-ref --short HEAD 2>/dev/null || echo "unknown")
if [ "$ARIFOS_BRANCH" = "main" ]; then
    pass "arifOS: on main branch"
else
    fail "arifOS: on '$ARIFOS_BRANCH' branch (should be main)"
fi

# No uncommitted changes in active service repos
for repo in WEALTH WELL GEOX; do
    if [ -d "/root/$repo/.git" ]; then
        UNCOMMITTED=$(git -C /root/$repo status --short 2>/dev/null | wc -l)
        if [ "$UNCOMMITTED" -gt 0 ]; then
            fail "$repo: $UNCOMMITTED uncommitted files"
        else
            pass "$repo: clean (no uncommitted changes)"
        fi
    fi
done

echo ""
echo "═══════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo "✅ ALL INVARIANTS PASSED"
    echo "   Safe to proceed with changes."
    exit 0
else
    echo "❌ $FAILED INVARIANT(S) FAILED"
    echo "   Do NOT proceed. Resolve failures first."
    echo "   Report:$REPORT"
    exit 1
fi
