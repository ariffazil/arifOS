#!/bin/bash
# Fast deployment - sync code and restart container without full rebuild

set -e
cd /root/arifOS

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║        ⚡ FAST DEPLOYMENT — Code Sync + Container Restart                 ║"
echo "╠═══════════════════════════════════════════════════════════════════════════╣"

echo ""
echo "📋 Step 1: Git Sync"
echo "─────────────────────────────────────────────────────────────────────────────"
git pull origin main
echo "✅ Code synced to: $(git rev-parse --short HEAD)"

echo ""
echo "🔧 Step 2: Copy code to running container"
echo "─────────────────────────────────────────────────────────────────────────────"
# Copy the new v2 code into the container
docker cp arifosmcp/runtime/tools_v2.py arifosmcp:/usr/src/project/arifosmcp/runtime/
docker cp arifosmcp/runtime/tools_v2_forge.py arifosmcp:/usr/src/project/arifosmcp/runtime/
docker cp arifosmcp/runtime/tool_specs_v2.py arifosmcp:/usr/src/project/arifosmcp/runtime/
docker cp arifosmcp/runtime/philosophy_registry.py arifosmcp:/usr/src/project/arifosmcp/runtime/
docker cp arifosmcp/server_horizon.py arifosmcp:/usr/src/project/arifosmcp/
docker cp data/philosophy_registry_v1.json arifosmcp:/usr/src/project/data/ 2>/dev/null || true
echo "✅ Code copied to container"

echo ""
echo "🔄 Step 3: Restart container"
echo "─────────────────────────────────────────────────────────────────────────────"
docker restart arifosmcp
echo "✅ Container restarted"

echo ""
echo "⏳ Step 4: Wait for health check"
echo "─────────────────────────────────────────────────────────────────────────────"
sleep 5
for i in {1..20}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Container healthy"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "✅ Step 5: Verify v2 Tools"
echo "─────────────────────────────────────────────────────────────────────────────"
TOOL_COUNT=$(curl -s http://localhost:8080/tools | jq '.count' 2>/dev/null || echo "0")
echo "Tools registered: $TOOL_COUNT"

# Test philosophy injection
echo ""
echo "Testing philosophy injection..."
PHIL=$(curl -s -X POST http://localhost:8080/tools/arifos.init \
    -H "Content-Type: application/json" \
    -d '{"actor_id":"deploy","intent":"verify"}' | jq -r '.philosophy.entry.text' 2>/dev/null || echo "FAILED")

if echo "$PHIL" | grep -q "DITEMPA"; then
    echo "✅ Philosophy injection: $PHIL"
else
    echo "❌ Philosophy injection failed: $PHIL"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     🎉 FAST DEPLOYMENT COMPLETE                           ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
