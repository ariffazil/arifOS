#!/bin/bash
# arifOS MCP startup bootstrapper
# Installs required Python packages to /tmp/pylibs (writable location for non-root user)
# then runs the MCP server

set -e

echo "[bootstrap] Installing Python packages to /tmp/pylibs..."
pip install --target=/tmp/pylibs asyncpg qdrant-client --quiet 2>/dev/null || {
    echo "[bootstrap] pip install failed, trying with --user..."
    pip install --user asyncpg qdrant-client --quiet 2>/dev/null || true
}

echo "[bootstrap] Starting arifOS MCP server..."
exec python -m arifosmcp.runtime.__main__
