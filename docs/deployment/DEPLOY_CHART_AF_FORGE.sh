#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# ARIFOS MCP v2 — DEPLOYMENT CHART FOR AF-FORGE VPS
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║        🚀 ARIFOS MCP v2 — AF-FORGE DEPLOYMENT CHART                       ║"
echo "╠═══════════════════════════════════════════════════════════════════════════╣"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ───────────────────────────────────────────────────────────────────────────
# PHASE 0: PRE-DEPLOYMENT CHECKS
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "📋 PHASE 0: Pre-Deployment Checks"
echo "─────────────────────────────────────────────────────────────────────────────"

# Check git status
cd /root/arifOS
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo "Current commit: $CURRENT_COMMIT"

# Pull latest
echo "Pulling latest from origin/main..."
git pull origin main
NEW_COMMIT=$(git rev-parse --short HEAD)

if [ "$CURRENT_COMMIT" != "$NEW_COMMIT" ]; then
    echo -e "${GREEN}✅ Updated from $CURRENT_COMMIT to $NEW_COMMIT${NC}"
else
    echo -e "${YELLOW}⚠️  Already at latest commit${NC}"
fi

# ───────────────────────────────────────────────────────────────────────────
# PHASE 1: BACKUP CURRENT STATE
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "💾 PHASE 1: Backup Current State"
echo "─────────────────────────────────────────────────────────────────────────────"

BACKUP_DIR="/root/backups/arifos-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup current container logs
docker logs arifosmcp > "$BACKUP_DIR/container-logs-pre-deploy.txt" 2>&1 || true
echo "✅ Container logs backed up to $BACKUP_DIR"

# Backup current git state
git log --oneline -5 > "$BACKUP_DIR/git-log.txt"
echo "✅ Git state backed up"

# ───────────────────────────────────────────────────────────────────────────
# PHASE 2: BUILD NEW IMAGE
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "🔨 PHASE 2: Build New Docker Image"
echo "─────────────────────────────────────────────────────────────────────────────"

echo "Building arifos/arifosmcp:v2.0.0..."
docker build -t arifos/arifosmcp:v2.0.0 -f Dockerfile .
docker tag arifos/arifosmcp:v2.0.0 arifos/arifosmcp:latest

echo -e "${GREEN}✅ Image built successfully${NC}"

# ───────────────────────────────────────────────────────────────────────────
# PHASE 3: DEPLOY
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "🚀 PHASE 3: Deploy"
echo "─────────────────────────────────────────────────────────────────────────────"

echo "Stopping current container..."
docker compose stop arifosmcp

echo "Removing old container..."
docker compose rm -f arifosmcp

echo "Starting new container..."
docker compose up -d arifosmcp

echo "Waiting for container to be healthy..."
sleep 10

# Wait for health check
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Container is healthy${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# ───────────────────────────────────────────────────────────────────────────
# PHASE 4: VERIFICATION
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "✅ PHASE 4: Post-Deployment Verification"
echo "─────────────────────────────────────────────────────────────────────────────"

# Check health
HEALTH=$(curl -s http://localhost:8080/health | jq -r '.status' 2>/dev/null || echo "error")
if [ "$HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✅ Health check: HEALTHY${NC}"
else
    echo -e "${RED}❌ Health check: $HEALTH${NC}"
fi

# Check tool count
TOOL_COUNT=$(curl -s http://localhost:8080/tools | jq '.count' 2>/dev/null || echo "0")
if [ "$TOOL_COUNT" = "10" ]; then
    echo -e "${GREEN}✅ Tool count: $TOOL_COUNT (expected 10)${NC}"
else
    echo -e "${RED}❌ Tool count: $TOOL_COUNT (expected 10)${NC}"
fi

# Check philosophy injection
echo "Testing philosophy injection..."
PHILOSOPHY=$(curl -s -X POST http://localhost:8080/tools/arifos.init \
    -H "Content-Type: application/json" \
    -d '{"actor_id":"deploy","intent":"verify"}' | jq -r '.philosophy.entry.text' 2>/dev/null || echo "")

if echo "$PHILOSOPHY" | grep -q "DITEMPA"; then
    echo -e "${GREEN}✅ Philosophy injection: S1 quote returned${NC}"
else
    echo -e "${RED}❌ Philosophy injection failed${NC}"
fi

# ───────────────────────────────────────────────────────────────────────────
# PHASE 5: FINAL STATUS
# ───────────────────────────────────────────────────────────────────────────
echo ""
echo "📊 PHASE 5: Deployment Status"
echo "─────────────────────────────────────────────────────────────────────────────"

docker ps | grep arifosmcp

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                     🎉 DEPLOYMENT COMPLETE                                ║"
echo "╠═══════════════════════════════════════════════════════════════════════════╣"
echo "║  Commit: $NEW_COMMIT"
echo "║  Image: arifos/arifosmcp:v2.0.0"
echo "║  Tools: $TOOL_COUNT/10 registered"
echo "║  Health: $HEALTH"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

# Show logs
echo ""
echo "Recent logs (last 20 lines):"
docker logs --tail 20 arifosmcp 2>&1 | tail -20

