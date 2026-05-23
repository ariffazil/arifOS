#!/bin/bash
# arif_auto_session.sh — Inject persistent session binding into all arifOS MCP tool calls
# Usage: source arif_auto_session.sh [session_id] [actor_id]
# Then all subsequent arifOS tool calls will carry the session binding.

export ARIFOS_SESSION_ID="${1:-SEAL-cbc5d95eb9df4bad}"
export ARIFOS_ACTOR_ID="${2:-a-forge}"
export ARIFOS_MCP_URL="${ARIFOS_MCP_URL:-http://localhost:8080/mcp}"

echo "✅ arifOS session binding active"
echo "   session_id: $ARIFOS_SESSION_ID"
echo "   actor_id:   $ARIFOS_ACTOR_ID"
echo "   mcp_url:    $ARIFOS_MCP_URL"
echo ""
echo "All arifOS tools will now auto-inject session + actor binding."
echo "Usage: arif_tool <tool-name> <json-arguments>"
echo ""
echo "Example:"
echo "  arif_tool arif_memory_recall '{\"mode\":\"search\",\"query\":\"PETRONAS\"}'"
