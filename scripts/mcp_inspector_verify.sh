#!/bin/bash
#
# MCP Inspector Verification Script for arifOS
# Tests all critical paths after deployment
#

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  arifOS MCP Inspector Verification                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

SERVER_URL="${ARIFOS_SERVER:-http://localhost:8080}"
PASS=0
FAIL=0

# Helper function
check_test() {
    if [ $1 -eq 0 ]; then
        echo "✓ $2"
        ((PASS++))
    else
        echo "✗ $2"
        ((FAIL++))
    fi
}

echo "Server: $SERVER_URL"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# P0 Tests: Critical functionality
# ═══════════════════════════════════════════════════════════════════════════════

echo "═══════════════════════════════════════════════════════════════"
echo "P0 CRITICAL TESTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 1: Health check
echo "1. Health Check"
response=$(curl -s "$SERVER_URL/health" || echo "{}")
if echo "$response" | grep -q '"status".*"healthy"'; then
    check_test 0 "Server health endpoint responds"
else
    check_test 1 "Server health endpoint"
fi

# Test 2: arifos.init - must not return INIT_KERNEL_500
echo ""
echo "2. arifos.init (circular dependency fix)"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.init",
        "input": {
            "actor": "inspector",
            "intent": "Verify deployment",
            "risk": "low",
            "session": "inspector-test-001"
        }
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q 'INIT_KERNEL_500'; then
    check_test 1 "arifos.init still has circular dependency"
elif echo "$response" | grep -q '"ok".*true\|"verdict".*"SEAL"'; then
    check_test 0 "arifos.init works (no INIT_KERNEL_500)"
else
    check_test 1 "arifos.init response unclear"
fi

# Test 3: canonical_tool_name populated
echo ""
echo "3. canonical_tool_name populated"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.init",
        "input": {
            "actor": "inspector",
            "intent": "Test canonical name",
            "risk": "low",
            "session": "inspector-test-002"
        }
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q '"canonical_tool_name".*"arifos.init"'; then
    check_test 0 "canonical_tool_name is populated"
elif echo "$response" | grep -q '"canonical_tool_name".*null'; then
    check_test 1 "canonical_tool_name is null"
else
    check_test 1 "canonical_tool_name not found in response"
fi

# Test 4: arifos.sense empty query validation
echo ""
echo "4. arifos.sense empty query validation"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.sense",
        "input": {
            "query": "",
            "mode": "search",
            "risk": "low",
            "session": "inspector-test-003"
        }
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q 'SENSE_QUERY_EMPTY\|"verdict".*"VOID"'; then
    check_test 0 "arifos.sense validates empty query"
else
    check_test 1 "arifos.sense empty query validation"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# P1 Tests: Clean output format
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "P1 CLEAN OUTPUT TESTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 5: Clean output structure (operator view)
echo "5. Clean Output Structure (operator view)"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.init",
        "input": {
            "actor": "inspector",
            "intent": "Test clean output",
            "risk": "low",
            "session": "inspector-test-004",
            "options": {"verbose": false}
        }
    }' 2>/dev/null || echo '{}')

has_execution=$(echo "$response" | grep -c '"execution"' || true)
has_governance=$(echo "$response" | grep -c '"governance"' || true)
has_operator=$(echo "$response" | grep -c '"operator"' || true)
has_context=$(echo "$response" | grep -c '"context"' || true)

if [ "$has_execution" -gt 0 ] && [ "$has_governance" -gt 0 ] && [ "$has_operator" -gt 0 ] && [ "$has_context" -gt 0 ]; then
    check_test 0 "Clean output has fixed block structure"
else
    check_test 1 "Clean output structure incomplete"
fi

# Test 6: No legacy name leakage
echo ""
echo "6. No Legacy Name Leakage"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.mind",
        "input": {
            "query": "Test reasoning",
            "risk": "low",
            "session": "inspector-test-005"
        }
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q '"tool".*"agi_mind"\|"tool".*"init_anchor"'; then
    check_test 1 "Legacy tool names still leaking"
else
    check_test 0 "No legacy tool name leakage"
fi

# Test 7: Verbose output includes system block
echo ""
echo "7. Verbose Output (options.verbose: true)"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.init",
        "input": {
            "actor": "inspector",
            "intent": "Test verbose",
            "risk": "low",
            "session": "inspector-test-006",
            "options": {"verbose": true}
        }
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q '"system"'; then
    check_test 0 "Verbose output includes system block"
else
    check_test 1 "Verbose output missing system block"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# P2 Tests: Extended features
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "P2 EXTENDED TESTS"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 8: Tools list endpoint
echo "8. Tools List Endpoint"
response=$(curl -s "$SERVER_URL/tools" || echo "{}")
if echo "$response" | grep -q 'arifos.init\|arifos.mind\|arifos.judge'; then
    check_test 0 "Tools endpoint lists arifOS tools"
else
    check_test 1 "Tools endpoint"
fi

# Test 9: Version endpoint
echo ""
echo "9. Version Endpoint"
response=$(curl -s "$SERVER_URL/version" || echo "{}")
if echo "$response" | grep -q '"version"'; then
    check_test 0 "Version endpoint responds"
else
    check_test 1 "Version endpoint"
fi

# Test 10: Error handling
echo ""
echo "10. Error Handling (typed error codes)"
response=$(curl -s -X POST "$SERVER_URL/mcp" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "arifos.nonexistent",
        "input": {}
    }' 2>/dev/null || echo '{}')

if echo "$response" | grep -q '"code"\|"error"'; then
    check_test 0 "Error responses include typed codes"
else
    check_test 1 "Error handling"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "VERIFICATION SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✓ ALL TESTS PASSED - DEPLOYMENT VERIFIED                  ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 0
elif [ $FAIL -le 2 ]; then
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ⚠ MOSTLY PASSED - REVIEW FAILURES                         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 1
else
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✗ MULTIPLE FAILURES - CONSIDER ROLLBACK                   ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 2
fi
