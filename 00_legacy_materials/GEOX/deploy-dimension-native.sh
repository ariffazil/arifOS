#!/bin/bash
# GEOX Dimension-Native Architecture Deployment
# DITEMPA BUKAN DIBERI

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "GEOX Dimension-Native Architecture — VPS Deployment"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
VPS_HOST="geox.arif-fazil.com"
DOMAIN="geox.arif-fazil.com"
GEOX_PROFILE="${GEOX_PROFILE:-vps}"

echo "Profile: $GEOX_PROFILE"
echo "Domain: $DOMAIN"
echo ""

if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
else
    COMPOSE_CMD=(docker-compose)
fi

# Check if we're on the VPS or local
if [ "$(hostname)" = "srv1325122" ] || [ "$(hostname)" = "geox" ]; then
    echo "✓ Running on VPS — local deployment"
    ON_VPS=true
else
    echo "✓ Running locally — remote deployment"
    ON_VPS=false
fi

echo ""
echo "Step 1: Validating Dimension-Native Structure..."
echo "───────────────────────────────────────────────────────────────"

# Check required files exist
required_files=(
    "geox_unified.py"
    "registries/__init__.py"
    "registries/prospect.py"
    "registries/well.py"
    "registries/physics.py"
    "registries/map.py"
    "registries/cross.py"
    "services/governance/judge.py"
    "services/evidence_store/store.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing: $file"
        exit 1
    fi
    echo "✓ Found: $file"
done

echo ""
echo "Step 2: Checking Evidence Store Data..."
echo "───────────────────────────────────────────────────────────────"

if [ -f "data/evidence/PROSPECT_ALPHA.json" ]; then
    echo "✓ PROSPECT_ALPHA evidence found"
else
    echo "⚠ PROSPECT_ALPHA evidence not found — will seed during deployment"
fi

if [ -f "data/evidence/W-101.json" ]; then
    echo "✓ W-101 evidence found"
else
    echo "⚠ W-101 evidence not found — will seed during deployment"
fi

echo ""
echo "Step 3: Building Docker Image..."
echo "───────────────────────────────────────────────────────────────"

# Stop existing containers
"${COMPOSE_CMD[@]}" -f docker-compose.unified.yml down 2>/dev/null || true

# Build with new Dockerfile
"${COMPOSE_CMD[@]}" -f docker-compose.unified.yml build --no-cache

echo ""
echo "Step 4: Starting Dimension-Native Services..."
echo "───────────────────────────────────────────────────────────────"

GEOX_PROFILE=$GEOX_PROFILE "${COMPOSE_CMD[@]}" -f docker-compose.unified.yml up -d

echo ""
echo "Step 5: Health Verification..."
echo "───────────────────────────────────────────────────────────────"

sleep 5

# Check health
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Health endpoint responding"
    echo "Health: $(curl -s http://localhost:8000/health)"
    curl -s http://localhost:8000/health/details | python3 -m json.tool 2>/dev/null || true
else
    echo "⚠ Health check failed — checking logs..."
    "${COMPOSE_CMD[@]}" -f docker-compose.unified.yml logs --tail=50 geox
    exit 1
fi

echo ""
echo "Step 6: Verifying Dimension Registry..."
echo "───────────────────────────────────────────────────────────────"

# Check profile status
PROFILE_STATUS=$(curl -sf http://localhost:8000/profile 2>/dev/null || echo "{}")
echo "Profile Status: $PROFILE_STATUS"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Deployment Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Dimension-Native GEOX is live:"
echo "  Dashboard:  https://${DOMAIN}/"
echo "  Health:     https://${DOMAIN}/health"
echo "  MCP:        https://${DOMAIN}/mcp"
echo ""
echo "Enabled Dimensions (Profile: $GEOX_PROFILE):"
case $GEOX_PROFILE in
    core)
        echo "  • PHYSICS (Governance)"
        echo "  • MAP (Context)"
        ;;
    vps)
        echo "  • PROSPECT (Play Fairway)"
        echo "  • WELL (Borehole Truth)"
        echo "  • EARTH_3D (Seismic)"
        echo "  • MAP (Spatial Context)"
        echo "  • PHYSICS (Verification)"
        ;;
    full)
        echo "  • ALL 7 DIMENSIONS"
        echo "  • Including SECTION, TIME_4D"
        echo "  • Including physics_judge_verdict"
        ;;
esac

echo ""
echo "Test commands:"
echo "  curl https://${DOMAIN}/health"
echo "  curl https://${DOMAIN}/profile"
echo "  fastmcp list https://${DOMAIN}/mcp/"
echo ""
echo "DITEMPA BUKAN DIBERI — 999 SEAL ALIVE"
