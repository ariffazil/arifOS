#!/bin/bash
# arifOS Staging Deployment Script
# 72-hour burn-in with monitoring
# DITEMPA BUKAN DIBERI

set -e

echo "=================================================="
echo "arifOS Staging Deployment"
echo "=================================================="

# Configuration
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DEPLOY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$DEPLOY_DIR")"

cd "$PROJECT_ROOT"

echo "[1/5] Building Trinity MCP Server..."
docker build -t arifos-trinity:staging -f deploy/Dockerfile .

echo "[2/5] Building Burn-In Monitor..."
docker build -t arifos-burn-in:staging -f deploy/Dockerfile.monitor .

echo "[3/5] Starting staging stack..."
docker-compose -f deploy/docker-compose.staging.yml up -d

echo "[4/5] Waiting for services to be healthy..."
sleep 10

# Health check
echo "[5/5] Verifying deployment..."
for i in {1..10}; do
    if curl -sf http://localhost:8000/health > /dev/null; then
        echo "Health check PASSED"
        break
    fi
    echo "Waiting for health check... ($i/10)"
    sleep 5
done

echo ""
echo "=================================================="
echo "STAGING DEPLOYMENT COMPLETE"
echo "=================================================="
echo ""
echo "Services:"
echo "  Trinity MCP:  http://localhost:8000"
echo "  Health:       http://localhost:8000/health"
echo "  Metrics:      http://localhost:8000/metrics"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Prometheus:   http://localhost:9090"
echo "  Grafana:      http://localhost:3000 (admin/arifos-staging)"
echo ""
echo "Burn-in Monitor:"
echo "  Duration: 72 hours"
echo "  Reports:  ./reports/"
echo ""
echo "View logs: docker-compose -f deploy/docker-compose.staging.yml logs -f"
echo "Stop:      docker-compose -f deploy/docker-compose.staging.yml down"
echo "=================================================="
