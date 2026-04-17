#!/bin/bash
# ArifOS MCP Server Entrypoint
# Fixes Python namespace package resolution for Docker volume mounts

set -e

# Create symlink so 'from arifOS.core.shared.types' resolves correctly
# when core/ is volume-mounted at /usr/src/app/core instead of /usr/src/app/arifOS/core
if [ -d "/usr/src/app/arifOS" ] && [ ! -L "/usr/src/app/arifOS/core" ] && [ -d "/usr/src/app/core" ]; then
    ln -sf /usr/src/app/core /usr/src/app/arifOS/core
    echo "[arifOS] Linked /usr/src/app/arifOS/core -> /usr/src/app/core"
fi

# Also fix arifosmcp -> arifOS/arifosmcp if needed
if [ -d "/usr/src/app/arifOS" ] && [ ! -L "/usr/src/app/arifOS/arifosmcp" ] && [ -d "/usr/src/app/arifosmcp" ]; then
    ln -sf /usr/src/app/arifosmcp /usr/src/app/arifOS/arifosmcp
    echo "[arifOS] Linked /usr/src/app/arifOS/arifosmcp -> /usr/src/app/arifosmcp"
fi

# Run the original command
exec "$@"
