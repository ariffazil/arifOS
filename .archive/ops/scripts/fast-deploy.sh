#!/bin/bash
# Fast Deployment Script for arifOS MCP Server
# Optimized for quick rebuilds using Docker BuildKit

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 arifOS Fast Deploy${NC}"
echo "=================================="

# Detect if we should use optimized Dockerfile
DOCKERFILE="Dockerfile.optimized"
if [ ! -f "$DOCKERFILE" ]; then
    echo -e "${YELLOW}⚠️  Optimized Dockerfile not found, using standard Dockerfile${NC}"
    DOCKERFILE="Dockerfile"
fi

# Export BuildKit variables for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

echo -e "${YELLOW}📦 Building with BuildKit optimizations...${NC}"
echo "   - Layer caching enabled"
echo "   - UV for fast package installs"
echo "   - Incremental builds for code changes"

# Build with cache mounts
docker build \
    --file "$DOCKERFILE" \
    --tag arifos/arifosmcp:latest \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --cache-from arifos/arifosmcp:latest \
    --progress=auto \
    . 2>&1

echo -e "${GREEN}✅ Build complete${NC}"

echo -e "${YELLOW}🔄 Restarting container...${NC}"
docker compose stop arifosmcp 2>/dev/null || true
docker compose rm -f arifosmcp 2>/dev/null || true
docker compose up -d arifosmcp

echo -e "${YELLOW}⏳ Waiting for healthcheck...${NC}"
for i in {1..30}; do
    if curl -fsS http://localhost:8080/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ arifOS MCP is healthy!${NC}"
        echo ""
        echo "📊 Status:"
        curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8080/health
        exit 0
    fi
    sleep 1
    echo -n "."
done

echo -e "${RED}❌ Health check timeout${NC}"
exit 1
