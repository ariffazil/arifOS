#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBHOOK_PORT="${WEBHOOK_PORT:-8443}"

if [ -z "${ARIFOS_WEBHOOK_SECRET:-}" ]; then
    if [ -f /root/compose/secrets/arifos_webhook_secret ]; then
        export ARIFOS_WEBHOOK_SECRET=$(cat /root/compose/secrets/arifos_webhook_secret)
    else
        echo "ERROR: ARIFOS_WEBHOOK_SECRET not set and secret file not found"
        exit 1
    fi
fi

export ARIFOS_DEPLOY_SCRIPT="${ARIFOS_DEPLOY_SCRIPT:-/root/arifOS/scripts/deploy_arifosmcp.sh}"

# Clear any inherited pycache
find "$SCRIPT_DIR" -name "__pycache__" -path "*webhook*" -exec rm -rf {} + 2>/dev/null || true

# Start with signal mask cleared
exec python3 -B "$SCRIPT_DIR/webhook_deploy_server.py" --port "$WEBHOOK_PORT"
