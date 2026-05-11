#!/bin/bash
# GEOX Dimension-Native MCP Server — HTTP Transport
# DITEMPA BUKAN DIBERI

echo "🔥 GEOX Dimension-Native Server Starting"
echo "   Version: v2026.04.11-DIMENSION-NATIVE"
echo "   Seal: DITEMPA BUKAN DIBERI"
echo "   Profile: ${GEOX_PROFILE:-vps}"
echo "   Transport: HTTP SSE on port 8000"
echo ""

export GEOX_HOST=0.0.0.0
export GEOX_PORT=8000

# Run with HTTP transport
exec python geox_unified_mcp_server.py --transport http --host 0.0.0.0 --port 8000
