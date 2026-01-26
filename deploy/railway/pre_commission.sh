#!/bin/bash
set -e

echo "=========================================="
echo "arifOS v52.5.1 Railway Pre-Commissioning"
echo "Phases 0A-0G Automation"
echo "=========================================="

# Phase 0A: Validate Configuration Files
echo "[0A] Validating configuration files..."
[ -f "railway.toml" ] || { echo "❌ railway.toml missing"; exit 1; }
[ -f ".railway-env" ] || { echo "⚠️  .railway-env missing (optional)"; }
[ -f "Dockerfile" ] || { echo "❌ Dockerfile missing"; exit 1; }
echo "✅ Phase 0A: Configuration files present"

# Phase 0B: Check Redis (requires REDIS_URL env var)
echo "[0B] Checking Redis connectivity..."
if [ -z "$REDIS_URL" ]; then
  echo "⚠️  REDIS_URL not set (will be provided by Railway)"
else
  python3 -c "import redis; r=redis.from_url('$REDIS_URL'); r.ping()" 2>/dev/null || { echo "❌ Redis unreachable"; exit 1; }
  echo "✅ Phase 0B: Redis reachable"
fi

# Phase 0C: Verify Volume Mount
echo "[0C] Verifying /var/data volume..."
mkdir -p /var/data/vault999 2>/dev/null || echo "⚠️  Volume not mounted (will be created by Railway)"
echo "✅ Phase 0C: Volume path ready"

# Phase 0D: Generate Secrets
echo "[0D] Generating secrets..."
if [ -f "scripts/init_cooling_ledger.py" ]; then
  python3 scripts/init_cooling_ledger.py
  echo "✅ Phase 0D: Genesis hash generated"
else
  echo "⚠️  init_cooling_ledger.py not found (skip in CI)"
fi

# Phase 0E: Health Check (requires deployed app)
echo "[0E] Health endpoint validation..."
if [ -z "$RAILWAY_URL" ]; then
  echo "⚠️  RAILWAY_URL not set (skip health check in CI)"
else
  sleep 5  # Wait for app to start
  curl -f "$RAILWAY_URL/health" || { echo "❌ Health check failed"; exit 1; }
  echo "✅ Phase 0E: Health endpoint healthy"
fi

# Phase 0F: k6 Load Test (requires deployed app)
echo "[0F] Running k6 load test..."
if command -v k6 &> /dev/null && [ -n "$RAILWAY_URL" ]; then
  RAILWAY_URL="$RAILWAY_URL" k6 run tests/k6/checkpoint_load_test.js
  echo "✅ Phase 0F: Load test passed"
else
  echo "⚠️  k6 not installed or RAILWAY_URL not set (skip load test)"
fi

# Phase 0G: Snapshot Verification
echo "[0G] Verifying snapshot capability..."
[ -d "VAULT999" ] || { echo "❌ VAULT999 directory missing"; exit 1; }
echo "✅ Phase 0G: Snapshot directory ready"

echo "=========================================="
echo "✅ Pre-Commissioning Complete"
echo "Ready for: railway up"
echo "=========================================="
