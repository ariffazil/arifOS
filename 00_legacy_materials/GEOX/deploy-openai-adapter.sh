#!/bin/bash
#
# Deploy OpenAI Adapter to Production
# ═══════════════════════════════════════════════════════════════════════════════
# DITEMPA BUKAN DIBERI
#
# This script deploys the OpenAI Adapter (v0.6.1) to the GEOX production VPS.
# Run this on: srv1325122.hstgr.cloud as root or sudo user
#
# Usage:
#   chmod +x deploy-openai-adapter.sh
#   ./deploy-openai-adapter.sh
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/arifos/geox"
LOG_FILE="/var/log/geox-deploy-$(date +%Y%m%d-%H%M%S).log"
BACKUP_TAG="pre-openai-adapter-$(date +%Y%m%d-%H%M%S)"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     GEOX OpenAI Adapter — Production Deployment            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Timestamp:${NC} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo -e "${YELLOW}Version:${NC} v0.6.1"
echo -e "${YELLOW}Target:${NC} $DEPLOY_DIR"
echo -e "${YELLOW}Log:${NC} $LOG_FILE"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ] && ! sudo -n true 2>/dev/null; then
    log "${RED}ERROR: This script must be run as root or with sudo privileges${NC}"
    exit 1
fi

# Check if directory exists
if [ ! -d "$DEPLOY_DIR" ]; then
    log "${RED}ERROR: Deploy directory $DEPLOY_DIR not found${NC}"
    exit 1
fi

cd "$DEPLOY_DIR"

# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Pre-deployment Backup
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[1/8] Creating pre-deployment backup...${NC}"
docker commit geox_server "$BACKUP_TAG" 2>/dev/null || log "${YELLOW}  Warning: Could not create container backup (may not exist)${NC}"
git stash push -m "$BACKUP_TAG" 2>/dev/null || true
log "${GREEN}  ✓ Backup tag: $BACKUP_TAG${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# Step 2: Git Pull
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[2/8] Pulling latest code from origin/main...${NC}"
git fetch origin main
git reset --hard origin/main
GIT_COMMIT=$(git rev-parse --short HEAD)
log "${GREEN}  ✓ Code updated to commit: $GIT_COMMIT${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# Step 3: Verify OpenAI Adapter Files
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[3/8] Verifying OpenAI Adapter files...${NC}"
ADAPTER_FILES=(
    "geox-gui/src/adapters/openai_types.ts"
    "geox-gui/src/adapters/openai_adapter.ts"
    "geox-gui/src/adapters/useOpenAI.ts"
    "geox-gui/src/adapters/index.ts"
    "geox-gui/src/adapters/openai_manifest.json"
)

for file in "${ADAPTER_FILES[@]}"; do
    if [ -f "$file" ]; then
        log "${GREEN}  ✓ $file${NC}"
    else
        log "${RED}  ✗ MISSING: $file${NC}"
        exit 1
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Docker Compose Down
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[4/8] Stopping current containers...${NC}"
docker compose down --remove-orphans 2>&1 | tee -a "$LOG_FILE"
log "${GREEN}  ✓ Containers stopped${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# Step 5: Clean Docker Cache (Critical for GUI rebuild)
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[5/8] Cleaning Docker build cache...${NC}"
docker system prune -f --volumes 2>&1 | tee -a "$LOG_FILE"
docker volume prune -f 2>&1 | tee -a "$LOG_FILE"
log "${GREEN}  ✓ Cache cleaned${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# Step 6: Build with No Cache
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[6/8] Building Docker image (no cache)...${NC}"
log "${YELLOW}  This may take 5-15 minutes...${NC}"

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

docker compose build --no-cache --progress=plain geox_server 2>&1 | tee -a "$LOG_FILE"

if [ $? -eq 0 ]; then
    log "${GREEN}  ✓ Build successful${NC}"
else
    log "${RED}  ✗ Build failed — check $LOG_FILE${NC}"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 7: Start Containers
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[7/8] Starting containers...${NC}"
docker compose up -d geox_server 2>&1 | tee -a "$LOG_FILE"
sleep 5

# Check if container is running
if docker ps | grep -q "geox_server"; then
    log "${GREEN}  ✓ Container running${NC}"
else
    log "${RED}  ✗ Container failed to start${NC}"
    docker compose logs --tail=50 geox_server | tee -a "$LOG_FILE"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# Step 8: Verification
# ─────────────────────────────────────────────────────────────────────────────
log "${BLUE}[8/8] Verification...${NC}"

# Health check
HEALTH_STATUS=$(curl -s https://geox.arif-fazil.com/health || echo "FAILED")
if [ "$HEALTH_STATUS" = "OK" ]; then
    log "${GREEN}  ✓ Health check: OK${NC}"
else
    log "${RED}  ✗ Health check failed: $HEALTH_STATUS${NC}"
fi

# Version check
VERSION=$(curl -s https://geox.arif-fazil.com/health/details | grep -o '"version": "[^"]*"' | cut -d'"' -f4 || echo "unknown")
log "${BLUE}  Version: $VERSION${NC}"

# Check for Pilot tab
PILOT_CHECK=$(curl -s https://geox.arif-fazil.com/ | grep -i "pilot" | head -1 || echo "NOT FOUND")
if echo "$PILOT_CHECK" | grep -qi "pilot"; then
    log "${GREEN}  ✓ Pilot tab present${NC}"
else
    log "${YELLOW}  ⚠ Pilot tab not found (may need browser verification)${NC}"
fi

# Check for OpenAI Adapter files in container
ADAPTER_IN_CONTAINER=$(docker exec geox_server ls -la /app/geox-gui/src/adapters/ 2>/dev/null | wc -l)
if [ "$ADAPTER_IN_CONTAINER" -gt 0 ]; then
    log "${GREEN}  ✓ OpenAI Adapter files in container${NC}"
else
    log "${YELLOW}  ⚠ OpenAI Adapter files not visible in container (may be in build)${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              DEPLOYMENT COMPLETE                           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Commit:${NC} $GIT_COMMIT"
echo -e "${BLUE}Version:${NC} v0.6.1 (OpenAI Adapter enabled)"
echo -e "${BLUE}Health:${NC} https://geox.arif-fazil.com/health"
echo -e "${BLUE}Log:${NC} $LOG_FILE"
echo ""
echo -e "${YELLOW}Verification commands:${NC}"
echo "  curl https://geox.arif-fazil.com/health"
echo "  curl https://geox.arif-fazil.com/health/details"
echo "  docker compose logs -f geox_server"
echo ""
echo -e "${YELLOW}Rollback if needed:${NC}"
echo "  docker stop geox_server"
echo "  docker start geox_server_$BACKUP_TAG"
echo ""
echo -e "${GREEN}DITEMPA BUKAN DIBERI — Forged, Not Given${NC}"
