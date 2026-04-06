#!/bin/bash
# arifOS MCP Deployment Script
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Configuration
VPS_HOST="${VPS_HOST:-af-forge.io}"
DEPLOY_DIR="/opt/arifOS"
IMAGE_NAME="arifos-mcp"
BUILD_SHA=$(git rev-parse HEAD)
BUILD_SHORT=$(git rev-parse --short HEAD)
BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[DEPLOY]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# ─── Pre-flight Checks ───────────────────────────────────────────────────────

check_ssh() {
    log "Checking SSH connection to ${VPS_HOST}..."
    if ! ssh -o ConnectTimeout=5 root@${VPS_HOST} "echo 'SSH OK'" 2>/dev/null; then
        error "Cannot SSH to ${VPS_HOST}. Check VPN/SSH config."
    fi
}

check_git() {
    log "Verifying git state..."
    if [ -n "$(git status --porcelain)" ]; then
        warn "Uncommitted changes detected. Commit before deploy."
        git status -s
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# ─── Build Phase ─────────────────────────────────────────────────────────────

build_image() {
    log "Building Docker image..."
    
    docker build \
        -t ${IMAGE_NAME}:${BUILD_SHORT} \
        -t ${IMAGE_NAME}:latest \
        --build-arg ARIFOS_BUILD_SHA=${BUILD_SHA} \
        --build-arg ARIFOS_BUILD_TIME=${BUILD_TIME} \
        --build-arg ARIFOS_APP_VERSION=2026.04.06 \
        -f deployments/af-forge/Dockerfile .
    
    log "Image built: ${IMAGE_NAME}:${BUILD_SHORT}"
}

# ─── Deploy Phase ────────────────────────────────────────────────────────────

deploy_to_vps() {
    log "Deploying to ${VPS_HOST}..."
    
    # Create deploy bundle
    log "Creating deploy bundle..."
    tar czf /tmp/arifos-deploy.tar.gz \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.venv' \
        --exclude='node_modules' \
        .
    
    # Copy to VPS
    log "Uploading to VPS..."
    scp /tmp/arifos-deploy.tar.gz root@${VPS_HOST}:${DEPLOY_DIR}/
    
    # Execute remote deploy
    log "Executing remote deploy..."
    ssh root@${VPS_HOST} << EOF
        set -e
        cd ${DEPLOY_DIR}
        
        # Backup current
        if [ -d "arifOS-backup" ]; then
            rm -rf arifOS-backup
        fi
        if [ -d "arifOS" ]; then
            mv arifOS arifOS-backup
        fi
        
        # Extract new
        mkdir arifOS
        tar xzf arifos-deploy.tar.gz -C arifOS --strip-components=0
        cd arifOS
        
        # Build and start
        export ARIFOS_BUILD_SHA=${BUILD_SHA}
        export ARIFOS_BUILD_TIME=${BUILD_TIME}
        export ARIFOS_APP_VERSION=2026.04.06
        
        docker compose -f deployments/af-forge/docker-compose.yml down || true
        docker compose -f deployments/af-forge/docker-compose.yml build --no-cache
        docker compose -f deployments/af-forge/docker-compose.yml up -d
        
        # Health check
        sleep 5
        echo "Checking health..."
        curl -s http://localhost:3000/health | jq .
        curl -s http://localhost:3000/build | jq .
        
        # Cleanup
        docker system prune -f
        
        echo "Deploy complete: ${BUILD_SHORT}"
EOF
    
    log "Deploy finished!"
}

# ─── Verification ────────────────────────────────────────────────────────────

verify_deploy() {
    log "Verifying deployment..."
    
    HEALTH=$(ssh root@${VPS_HOST} "curl -s http://localhost:3000/health")
    BUILD=$(ssh root@${VPS_HOST} "curl -s http://localhost:3000/build")
    
    log "Health: $(echo $HEALTH | jq -r '.status')"
    log "Version: $(echo $BUILD | jq -r '.version')"
    log "Build SHA: $(echo $BUILD | jq -r '.build_sha')"
    
    # Verify build SHA matches
    REMOTE_SHA=$(echo $BUILD | jq -r '.build_sha')
    if [ "$REMOTE_SHA" != "$BUILD_SHA" ]; then
        error "Build SHA mismatch! Expected: ${BUILD_SHA}, Got: ${REMOTE_SHA}"
    fi
    
    log "Verification passed!"
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
    log "arifOS MCP Deployment — ${BUILD_SHORT}"
    
    check_ssh
    check_git
    build_image
    deploy_to_vps
    verify_deploy
    
    log "🎉 Deployment successful!"
    log "Build: ${BUILD_SHA}"
    log "URL: https://${VPS_HOST}"
    log "Health: https://${VPS_HOST}/health"
}

# Handle command line
 case "${1:-}" in
    build)
        build_image
        ;;
    deploy)
        deploy_to_vps
        verify_deploy
        ;;
    verify)
        verify_deploy
        ;;
    *)
        main
        ;;
esac
