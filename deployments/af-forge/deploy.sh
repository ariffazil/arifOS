#!/bin/bash
# arifOS MCP — AF-FORGE Deployment Script
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

# Build metadata
export ARIFOS_BUILD_SHA=$(git -C "$SCRIPT_DIR/../.." rev-parse --short HEAD 2>/dev/null || echo "dev")
export ARIFOS_BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
export ARIFOS_APP_VERSION=${ARIFOS_APP_VERSION:-2026.04.06}

echo -e "${GREEN}🔨 arifOS MCP — AF-FORGE Deployment${NC}"
echo "   Build SHA: $ARIFOS_BUILD_SHA"
echo "   Build Time: $ARIFOS_BUILD_TIME"
echo "   Version: $ARIFOS_APP_VERSION"
echo ""

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose is required${NC}" >&2; exit 1; }

# Build and deploy
echo -e "${YELLOW}📦 Building images...${NC}"
docker-compose -f "$COMPOSE_FILE" build --no-cache

echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d

# Wait for healthcheck
echo -e "${YELLOW}⏳ Waiting for healthcheck...${NC}"
sleep 5

# Verify deployment
echo -e "${YELLOW}🔍 Verifying deployment...${NC}"
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/health 2>/dev/null || echo "000")

if [ "$HEALTH_STATUS" == "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed (HTTP $HEALTH_STATUS)${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=20
    exit 1
fi

# Show build info
echo -e "${YELLOW}📋 Build Info:${NC}"
curl -s http://localhost:3000/build | python3 -m json.tool 2>/dev/null || curl -s http://localhost:3000/build

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo "   MCP endpoint: http://localhost:3000/mcp"
echo "   Health:       http://localhost:3000/health"
echo "   Ready:        http://localhost:3000/ready"
echo "   Build:        http://localhost:3000/build"
echo ""
echo "   View logs: docker-compose -f $COMPOSE_FILE logs -f"
