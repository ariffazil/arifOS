#!/bin/bash
# =============================================================================
# arifOS Automated Deployment Script (Docker Compose)
# Triggered by GitHub Actions push to main
# =============================================================================

set -e

# Configuration
REPO_PATH="/root/arifOS"
ENV_FILE="$REPO_PATH/.env"
LOG_FILE="/var/log/arifos-deploy.log"
DEPLOYMENT_LOCK="/tmp/arifos-deploy.lock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }
error() { log "${RED}ERROR: $1${NC}"; }
success() { log "${GREEN}SUCCESS: $1${NC}"; }
warning() { log "${YELLOW}WARNING: $1${NC}"; }

# Prevent concurrent deployments
if [ -f "$DEPLOYMENT_LOCK" ]; then
    PID=$(cat "$DEPLOYMENT_LOCK")
    if ps -p "$PID" > /dev/null 2>&1; then
        error "Deployment already in progress (PID: $PID)"
        exit 1
    else
        warning "Removing stale lock file"
        rm -f "$DEPLOYMENT_LOCK"
    fi
fi
echo $$ > "$DEPLOYMENT_LOCK"
trap 'rm -f "$DEPLOYMENT_LOCK"' EXIT

log "🚀 Starting arifOS automated deployment..."

# Check if running as root (for Docker)
if [ "$EUID" -ne 0 ]; then
    warning "Script not running as root. Docker commands may fail."
fi

# Change to repo directory
cd "$REPO_PATH"

# Pull latest code
log "📥 Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main
success "Code updated to $(git rev-parse --short HEAD)"

# Ensure .env exists
if [ ! -f "$ENV_FILE" ]; then
    error ".env file not found at $ENV_FILE"
    error "Run: cp $REPO_PATH/.env.example $ENV_FILE and configure"
    exit 1
fi

# Check environment file permissions
PERMS=$(stat -c "%a" "$ENV_FILE")
if [ "$PERMS" != "600" ]; then
    warning ".env permissions are $PERMS, should be 600"
    chmod 600 "$ENV_FILE"
    success "Fixed .env permissions to 600"
fi

# Load environment variables
export $(grep -v '^#' "$ENV_FILE" | xargs)

# =============================================================================
# PHASE 1: Core Infrastructure (Postgres + Redis)
# =============================================================================
log "🔧 Phase 1: Deploying Core Infrastructure..."

# Create networks if they don't exist
for network in arifos-internal arifos-public; do
    if ! sudo docker network inspect "$network" > /dev/null 2>&1; then
        log "Creating Docker network: $network"
        sudo docker network create "$network"
    fi
done

# Deploy Phase 1
if [ -f "$REPO_PATH/docker-compose.phase1.yml" ]; then
    log "Starting Phase 1 services..."
    sudo docker compose -f docker-compose.phase1.yml up -d
    
    # Wait for services to be healthy
    log "⏳ Waiting for services to be healthy..."
    sleep 10
    
    # Check Postgres
    if sudo docker exec arifos-postgres pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" > /dev/null 2>&1; then
        success "PostgreSQL is healthy"
    else
        error "PostgreSQL health check failed"
        sudo docker logs arifos-postgres --tail 20
        exit 1
    fi
    
    # Check Redis
    if sudo docker exec arifos-redis redis-cli -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; then
        success "Redis is healthy"
    else
        error "Redis health check failed"
        sudo docker logs arifos-redis --tail 20
        exit 1
    fi
    
    success "Phase 1 deployment complete"
else
    warning "Phase 1 compose file not found, skipping..."
fi

# =============================================================================
# PHASE 2: arifOS MCP Server
# =============================================================================
log "🔧 Phase 2: Building arifOS MCP Server..."

# Build the arifOS image
log "Building Docker image..."
sudo docker build -t arifos/mcp-server:latest "$REPO_PATH"

# Deploy with docker-compose.yml (main file)
if [ -f "$REPO_PATH/docker-compose.yml" ]; then
    log "Starting arifOS MCP server..."
    sudo docker compose up -d
    
    # Wait for service to be ready
    log "⏳ Waiting for arifOS to start..."
    sleep 5
    
    # Health check
    MAX_RETRIES=10
    RETRY=0
    while [ $RETRY -lt $MAX_RETRIES ]; do
        if curl -fsS "http://127.0.0.1:8080/health" > /dev/null 2>&1; then
            success "arifOS MCP server is healthy on port 8080"
            break
        fi
        RETRY=$((RETRY + 1))
        log "⏳ Health check retry $RETRY/$MAX_RETRIES..."
        sleep 3
    done
    
    if [ $RETRY -eq $MAX_RETRIES ]; then
        error "Health check failed after $MAX_RETRIES attempts"
        sudo docker logs arifosmcp --tail 50
        exit 1
    fi
else
    log "Using systemd service for MCP server..."
    
    # Fall back to systemd if docker-compose.yml not available
    if [ -f "/etc/systemd/system/arifos-mcp.service" ]; then
        sudo systemctl daemon-reload
        sudo systemctl restart arifos-mcp
        
        # Wait for service
        sleep 5
        
        if systemctl is-active --quiet arifos-mcp; then
            success "arifOS MCP systemd service is active"
        else
            error "Systemd service failed to start"
            journalctl -u arifos-mcp --no-pager -n 20
            exit 1
        fi
    else
        warning "No deployment method available (no docker-compose.yml or systemd service)"
    fi
fi

# =============================================================================
# FINAL VERIFICATION
# =============================================================================
log "🔍 Running final verification..."

# Check all containers
echo ""
echo "=== Running Containers ==="
sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Network status
echo "=== Network Topology ==="
sudo docker network inspect arifos_arifos-internal --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{printf "\n"}}{{end}}' 2>/dev/null || \
sudo docker network inspect arifos-internal --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{printf "\n"}}{{end}}'
echo ""

# Test endpoints
echo "=== Endpoint Tests ==="
if curl -fsS "http://127.0.0.1:8080/health" > /dev/null 2>&1; then
    echo "✅ Health endpoint: http://127.0.0.1:8080/health"
else
    echo "⚠️  Health endpoint not responding"
fi

echo ""
success "🎉 Deployment complete!"

# Get public IP
PUBLIC_IP=$(curl -fsS ifconfig.me 2>/dev/null || echo "VPS_IP")
echo ""
echo "📊 Deployment Summary:"
echo "   Commit: $(git rev-parse --short HEAD)"
echo "   Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo "   Public: http://$PUBLIC_IP:8080"
echo "   Local: http://127.0.0.1:8080"
echo ""
echo "🧪 Test commands:"
echo "   curl http://$PUBLIC_IP:8080/health"
echo "   curl http://$PUBLIC_IP:8080/sse"
echo ""
echo "📊 Monitor:"
echo "   sudo docker logs -f arifosmcp"
echo "   sudo docker stats"
