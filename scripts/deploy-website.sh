#!/bin/bash
# Deploy script for arifOS website
# Handles: arif-fazil.com, apex.arif-fazil.com, arifos.arif-fazil.com, mcp.arif-fazil.com

set -e

echo "🚀 Deploying arifOS v55.1 Website..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Pull latest changes
echo -e "${YELLOW}📦 Pulling latest changes...${NC}"
git pull origin main

# Build and start services
echo -e "${YELLOW}🔨 Building containers...${NC}"
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Health checks
echo -e "${YELLOW}🏥 Running health checks...${NC}"

HEALTH_URLS=(
    "http://localhost:8000/health"
)

for url in "${HEALTH_URLS[@]}"; do
    if curl -sf "$url" > /dev/null; then
        echo -e "${GREEN}✅ $url is healthy${NC}"
    else
        echo -e "${RED}❌ $url is unhealthy${NC}"
        docker-compose logs arifos
        exit 1
    fi
done

# Check Caddy
echo -e "${YELLOW}🔒 Checking Caddy...${NC}"
if docker-compose ps | grep -q "caddy.*Up"; then
    echo -e "${GREEN}✅ Caddy is running${NC}"
else
    echo -e "${RED}❌ Caddy is not running${NC}"
    docker-compose logs caddy
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Deployment successful!${NC}"
echo ""
echo "Website URLs:"
echo "  • https://arif-fazil.com (redirects to arifos)"
echo "  • https://apex.arif-fazil.com (APEX Judgment Engine)"
echo "  • https://arifos.arif-fazil.com (Main Dashboard)"
echo "  • https://mcp.arif-fazil.com (MCP Server)"
echo ""
echo "Logs:"
echo "  docker-compose logs -f arifos"
echo "  docker-compose logs -f caddy"
