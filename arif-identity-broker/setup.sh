#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# arifOS Identity Broker — Setup Script
# ═══════════════════════════════════════════════════════════════════════════
# Generates ~/.arif/identity.json with a secure broker_secret.
# Usage:
#   curl -sL <this-url> | bash
#   python -m arif_identity_broker.broker --setup
#   python -m arif_identity_broker.broker --generate /path/to/identity.json
# ═══════════════════════════════════════════════════════════════════════════

set -euo pipefail

ARIF_DIR="$HOME/.arif"
ARIF_IDENTITY_FILE="$ARIF_DIR/identity.json"

echo "╔══════════════════════════════════════════════════╗"
echo "║  arifOS Identity Broker — Setup                ║"
echo "║  DITEMPA BUKAN DIBERI — Forged, Not Given       ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 required but not found."
    exit 1
fi

# Check httpx
if ! python3 -c "import httpx" 2>/dev/null; then
    echo "⚠️  httpx not found. Installing..."
    pip install httpx aiohttp
fi

# Generate identity
echo "→ Generating identity file at $ARIF_IDENTITY_FILE"
python3 -c "
import sys
sys.path.insert(0, '$(dirname "$0")')
from broker import IdentityLoader
identity = IdentityLoader.generate('$ARIF_IDENTITY_FILE')
print(f'   actor_id: {identity[\"actor_id\"]}')
print(f'   state:    {identity[\"identity_state\"]}')
print(f'   secret:   {identity[\"broker_secret\"][:8]}...{identity[\"broker_secret\"][-4:]}')
"

echo ""
echo "✅ Setup complete."
echo ""
echo "Next steps:"
echo "  1. Start the broker:"
echo "       python broker.py --port 8088"
echo "       # or with systemd:"
echo "       sudo cp arif-identity-broker.service /etc/systemd/system/"
echo "       sudo systemctl enable --now arif-identity-broker"
echo ""
echo "  2. Point OpenCode MCP at the broker:"
echo "       # In OpenCode config, set arifOS MCP URL to:"
echo "       http://localhost:8088/mcp"
echo ""
echo "  3. Verify:"
echo "       curl http://localhost:8088/health"
echo ""
echo "⚠️  Keep ~/.arif/identity.json SECURE. chmod 600 applied."
echo "   Never commit this file. Never share the broker_secret."
