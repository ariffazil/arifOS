#!/bin/bash
# Test MCP connection to arifOS

set -e

ARIFOS_MCP="${ARIFOS_MCP_ENDPOINT:-http://127.0.0.1:8088/mcp}"

echo "=== MCP Client Test ==="
echo "Endpoint: $ARIFOS_MCP"
echo ""

# Test 1: Initialize (with proper Accept header)
echo "1. Testing MCP initialize..."
RESPONSE=$(curl -fsS -X POST "$ARIFOS_MCP" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {"name": "bridge-test", "version": "1.0.0"}
    }
  }' 2>&1) && echo "✅ Initialize OK" || echo "❌ Initialize failed: $RESPONSE"

echo "Response: $RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
echo ""

# Test 2: List tools
echo "2. Testing tools/list..."
curl -fsS -X POST "$ARIFOS_MCP" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list"
  }' | jq '.result.tools[].name' 2>/dev/null | head -5 && echo "✅ Tools list OK" || echo "❌ Tools list failed"

echo ""

# Test 3: Call apex_judge
echo "3. Testing tools/call apex_judge..."
RESULT=$(curl -fsS -X POST "$ARIFOS_MCP" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "apex_judge",
      "arguments": {
        "query": "Test query from bridge",
        "actor_id": "bridge-test"
      }
    }
  }' 2>&1)

# Check if result contains a verdict
if echo "$RESULT" | jq -e '.result.content[0].text | fromjson | .verdict' >/dev/null 2>&1; then
  echo "✅ apex_judge returned verdict"
  echo "$RESULT" | jq '.result.content[0].text | fromjson'
else
  echo "Response:"
  echo "$RESULT" | jq . 2>/dev/null || echo "$RESULT"
fi

echo ""
echo "=== MCP Test Complete ==="
