#!/bin/bash
# Simplified Railway MCP Server Startup
# No emoji, no database checks, just start the server

set -e

echo "==================================="
echo "arifOS v50 MCP Server - Railway"
echo "==================================="

# Show environment
echo "PORT: ${PORT:-8000}"
echo "ARIFOS_ENV: ${ARIFOS_ENV:-production}"
echo ""

# Quick import test
echo "Testing imports..."
python -c "from arifos.core.mcp.sse import app; print('Imports OK - ' + str(len(app.routes)) + ' routes')"

# Start server
echo ""
echo "Starting server on 0.0.0.0:${PORT:-8000}..."
exec python -m uvicorn arifos.core.mcp.sse:app \
  --host 0.0.0.0 \
  --port ${PORT:-8000} \
  --log-level info \
  --timeout-keep-alive 75 \
  --timeout-graceful-shutdown 30
