#!/bin/bash
# OpenClaw-Forged Entrypoint
# Version: 2026.03.14-FORGED
# Responsibility: Preflight checks, config merging, and gateway start

set -e

# Run Preflight
echo "🚀 [ARIF-OCL] Starting OpenClaw Forged..."
/usr/local/bin/openclaw-preflight

# Check for config existence
if [ ! -f "/root/.openclaw/config.json" ] && [ -f "/configs/openclaw.json" ]; then
    echo "📋 [ARIF-OCL] Overriding with arifOS native config..."
    mkdir -p /root/.openclaw
    cp /configs/openclaw.json /root/.openclaw/config.json
fi

# Fix workspace paths
mkdir -p /root/.openclaw/workspace

# Execute OpenClaw gateway or command
if [ $# -eq 0 ]; then
    echo "🔗 [ARIF-OCL] Gateway active on port ${PORT:-18789} (Default)"
    exec node openclaw.mjs gateway --allow-unconfigured
else
    echo "🔗 [ARIF-OCL] Executing command: $@"
    exec "$@"
fi
