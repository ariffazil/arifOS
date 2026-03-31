#!/bin/sh
# Restart OpenClaw Gateway

echo "🔄 Sending restart signal to OpenClaw Gateway..."

RESPONSE=$(curl -s -X POST https://hook.arifosmcp.arif-fazil.com/hooks/restart-openclaw \
  -H "X-Restart-Token: openclaw-restart-888")

echo "Response: $RESPONSE"
echo ""
echo "⏳ Waiting 10 seconds for restart..."
sleep 10

# Check status
if docker ps 2>/dev/null | grep -q "openclaw.*healthy"; then
    echo "✅ OpenClaw Gateway is healthy"
else
    echo "⚠️  Check status with: docker ps | grep openclaw"
fi
