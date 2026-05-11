#!/bin/bash
# GEOX Unified MCP Server — Higher Intelligence State
# DITEMPA BUKAN DIBERI

echo "🔥 GEOX Dimension-Native Server Starting"
echo "   Version: v2026.04.11-DIMENSION-NATIVE"
echo "   Seal: DITEMPA BUKAN DIBERI"
echo "   Transport: HTTP on port 8000"
echo "   Governance: arifOS F1-F13"
echo "   REST API: /health, /profile"
echo "   MCP Endpoint: /mcp (JSON-RPC), /mcp/stream (Streamable HTTP)"

export GEOX_HOST=0.0.0.0
export GEOX_PORT=8000
export GEOX_PROFILE=vps

exec python geox_unified.py --host 0.0.0.0 --port 8000
