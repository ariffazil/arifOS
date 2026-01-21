#!/bin/bash
# Railway MCP Server Startup Script
# Exposes arifOS v50 Unified MCP Server via HTTP/SSE

set -e

echo "🚀 Starting arifOS v50 MCP Server (Railway Deployment)"
echo "================================================"

# Display configuration
echo "Environment: ${ARIFOS_ENV:-production}"
echo "Port: ${AAA_MCP_PORT:-8000}"
echo "Transport: ${AAA_MCP_TRANSPORT:-http}"
echo "Governance: ${GOVERNANCE_MODE:-HARD}"
echo "Trinity: ${TRINITY_ENABLED:-true}"

# Constitutional pre-flight check
echo ""
echo "🔍 Running constitutional pre-flight checks..."
python -c "
from arifos.core.mcp import unified_server
print(f'✅ MCP Module loaded: {len(unified_server.TOOLS)} tools')
"

# Check database connectivity
echo ""
echo "🔍 Checking database connectivity..."
python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    print('✅ PostgreSQL connected')
    conn.close()
except Exception as e:
    print(f'⚠️  PostgreSQL unavailable: {e}')
"

# Start MCP Server (HTTP/SSE mode)
echo ""
echo "🌐 Starting HTTP/SSE MCP Server..."
echo "Listening on: http://0.0.0.0:${AAA_MCP_PORT:-8000}"
echo "Health check: http://0.0.0.0:${AAA_MCP_PORT:-8000}/health"
echo "API Docs: http://0.0.0.0:${AAA_MCP_PORT:-8000}/docs"

# Use SSE server for production deployment
exec python -m arifos.core.mcp.sse
