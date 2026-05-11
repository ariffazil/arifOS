#!/bin/bash
# GEOX VPS Deployment Script
# DITEMPA BUKAN DIBERI
#
# Usage: ./deploy-vps.sh
# Deploys GEOX MCP server to production VPS at geox.arif-fazil.com

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "GEOX Earth Witness — VPS Deployment"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
VPS_HOST="srv1325122.hstgr.cloud"
VPS_USER="root"
DEPLOY_DIR="/opt/arifos/geox"
DOMAIN="geox.arif-fazil.com"

echo "Step 1: Building Docker images locally (Deep Forge)..."
docker build --no-cache -t geox-server:latest .
docker build --no-cache -t geox-gui:latest ./geox-gui

echo ""
echo "Step 2: Pushing to VPS..."
# Save and transfer images
docker save geox-server:latest | ssh ${VPS_USER}@${VPS_HOST} "docker load"
docker save geox-gui:latest | ssh ${VPS_USER}@${VPS_HOST} "docker load"

echo ""
echo "Step 3: Deploying on VPS..."
ssh ${VPS_USER}@${VPS_HOST} << EOF
  mkdir -p ${DEPLOY_DIR}
  cd ${DEPLOY_DIR}

  # Pull latest code
  if [ -d ".git" ]; then
    git pull origin main
  else
    git clone https://github.com/ariffazil/GEOX.git .
  fi

  # Ensure Traefik network exists
  docker network create traefik_network 2>/dev/null || true

  # Stop existing containers
  docker compose down 2>/dev/null || true

  # Start with new images
  docker compose up -d

  # Wait for health check
  echo "Waiting for health check (Expecting v0.6.0)..."
  sleep 5
  curl -s https://${DOMAIN}/health/details | grep "0.6.0" || { echo "❌ Version Mismatch or 504. Still stale!"; exit 1; }
  echo "✅ v0.6.0 Verified Live"
  curl -s http://localhost:8000/health || echo "Health check failed"

  echo ""
  echo "Server info:"
  curl -s http://localhost:8000/health/details 2>/dev/null | head -20 || echo "Details unavailable"
EOF

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Deployment Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Endpoints:"
echo "  Dashboard: https://${DOMAIN}/"
echo "  Health:    https://${DOMAIN}/health"
echo "  Details:   https://${DOMAIN}/health/details"
echo "  MCP (SSE): https://${DOMAIN}/mcp"
echo ""
echo "Test with:"
echo "  curl https://${DOMAIN}/health"
echo "  fastmcp list https://${DOMAIN}/mcp"
echo ""
echo "DITEMPA BUKAN DIBERI — 999 SEAL ALIVE"
