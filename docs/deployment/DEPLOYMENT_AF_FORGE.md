# 🚀 AF-FORGE Deployment Guide

## Overview
Deploying arifOS MCP v2 with 10 canonical tools to AF-FORGE execution substrate.

## Pre-Deployment Checklist

### 1. Code Status ✅
```bash
git log --oneline -3
# a154517 📚 DOCS: Update README + TOM_INTEGRATION for 9+1 Architecture
# 7970918 🔥 ToM-Anchored MCP: 9 Tools + Philosophy Registry v1.2.0
# 9e28a63 Fix philosophy injection in MCP tools
```

### 2. Build Artifacts
```bash
# Docker image
docker build -t arifos/arifosmcp:v2.0.0 .
docker tag arifos/arifosmcp:v2.0.0 arifos/arifosmcp:latest
```

### 3. Configuration Updates Needed on AF-FORGE

#### Environment Variables
```bash
# Core
ARIFOS_VERSION=2026.04.06-v2
ARIFOS_ENV=production
MCP_PROTOCOL_VERSION=2025-11-05

# VPS Connection
ARIFOS_VPS_URL=https://arifosmcp.arif-fazil.com
ARIFOS_GOVERNANCE_SECRET=<redacted>

# Database
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333

# Registry
REGISTRY_VERSION=1.2.0
PHILOSOPHY_REGISTRY_PATH=/app/data/philosophy_registry_v1.json
```

## Deployment Steps

### Step 1: Backup Current State
```bash
# On AF-FORGE machine
docker-compose exec arifosmcp python3 -c "
from arifosmcp.runtime.philosophy_registry import get_registry_stats
import json
print(json.dumps(get_registry_stats(), indent=2))
" > /backup/pre-v2-registry-state.json
```

### Step 2: Deploy New Container
```bash
# Pull latest
docker pull arifos/arifosmcp:latest

# Restart with v2
docker-compose down
docker-compose up -d arifosmcp

# Verify health
curl http://localhost:8080/health
```

### Step 3: Verify v2 Tools Registered
```bash
curl http://localhost:8080/tools | jq '.tools[].name'

# Expected output:
# "arifos.init"
# "arifos.sense"
# "arifos.mind"
# "arifos.route"
# "arifos.heart"
# "arifos.ops"
# "arifos.judge"
# "arifos.memory"
# "arifos.vault"
# "arifos.forge"
```

### Step 4: Test Philosophy Injection
```bash
curl -X POST http://localhost:8080/tools/arifos.init \
  -H "Content-Type: application/json" \
  -d '{"actor_id":"test","intent":"deployment_check"}' | jq '.philosophy'

# Should return S1 quote:
# "DITEMPA, BUKAN DIBERI."
```

### Step 5: Verify G★ Band Mapping
```bash
# Test that G★=0.1 returns Band 0 regardless of tool
curl -X POST http://localhost:8080/tools/arifos.judge \
  -H "Content-Type: application/json" \
  -d '{"candidate_action":"test","telemetry":{"G_star":0.1}}' | jq '.philosophy.band'

# Expected: 0
```

## Rollback Plan

If deployment fails:
```bash
docker-compose down
docker pull arifos/arifosmcp:previous
docker-compose up -d arifosmcp
```

## Post-Deployment Verification

### Constitutional Health Check
```bash
curl http://localhost:8080/health

# Expected:
{
  "status": "healthy",
  "floors_active": 13,
  "tools_loaded": 10,
  "version": "2026.04.06-v2",
  "registry_version": "1.2.0"
}
```

### End-to-End Test
```bash
# Full pipeline: init → sense → mind → heart → judge → forge (dry-run)
python3 /root/arifOS/test_e2e_v2.py
```

## Critical Changes in v2

| Change | Impact |
|--------|--------|
| Tool names changed | Horizon gateway maps old → new |
| Philosophy injection | Single point in _wrap_call() |
| 10th tool (forge) | Delegated execution bridge |
| G★ determines band | Tool identity has zero influence |
| INIT/SEAL override | Always returns S1 quote |

## Troubleshooting

### Issue: Tools returning 500
**Cause**: Old v1 tool names not recognized
**Fix**: Horizon gateway maps names, ensure it's running

### Issue: Philosophy not injecting
**Cause**: inject_philosophy() not called
**Fix**: Check _wrap_call() in tools_internal.py

### Issue: Wrong band returned
**Cause**: Stage-based mapping still active
**Fix**: Verify only G★ determines band

## Contact

Deployment issues: File issue at https://github.com/ariffazil/arifOS/issues
