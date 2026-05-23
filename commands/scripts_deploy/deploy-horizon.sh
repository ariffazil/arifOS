#!/bin/bash
# arifOS MCP → Prefect Horizon Deployment Script
# Run this on the VPS after configuring env vars in Horizon UI

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  arifOS MCP → Prefect Horizon Deployment"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if prefect is installed
if ! command -v prefect &> /dev/null; then
    echo "❌ Prefect CLI not found. Installing..."
    pip install prefect>=3.0.0
fi

# Verify login
echo "🔐 Checking Prefect Cloud login..."
prefect cloud login || {
    echo "❌ Login failed. Run: prefect cloud login"
    exit 1
}

# Create work pool if it doesn't exist
echo "📦 Creating work pool..."
prefect work-pool create arifos-pool --type prefect:managed 2>/dev/null || echo "   Pool already exists"

# Deploy
echo "🚀 Deploying arifOS MCP server..."
cd /root/arifOS
prefect deploy --prefect-file prefect.yaml --name arifos-mcp-server

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Deployment Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Monitor at: https://app.prefect.cloud"
echo "Horizon UI: https://horizon.prefect.io/arifos/servers/arifOS"
echo ""
echo "Verification commands:"
echo "  prefect deployment ls"
echo "  prefect server ls"
echo ""
