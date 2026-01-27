# Railway Deployment Verification Guide

## After Railway deploys this fix, verify with these commands:

### 1. Health Check (Primary - MUST return 200 OK)
```bash
curl -s https://arifos.arif-fazil.com/health | python -m json.tool
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "v53.2.0-STANDALONE",
  "mode": "standalone",
  "port": 8000,
  "server": "arifOS-MCP",
  "tools": 5,
  "deployment": "railway",
  "domain": "arifos.arif-fazil.com",
  "endpoints": {
    "health": "/health",
    "root": "/",
    "metrics": "/metrics/json"
  }
}
```

### 2. Root Endpoint
```bash
curl -s https://arifos.arif-fazil.com/ | python -m json.tool
```

**Expected Response:**
```json
{
  "name": "arifOS MCP Server",
  "version": "v53.2.0-STANDALONE",
  "status": "operational",
  "domain": "arifos.arif-fazil.com",
  "endpoints": {
    "health": "/health",
    "metrics": "/metrics/json"
  },
  "tools": [
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999"
  ],
  "documentation": "https://github.com/ariffazil/arifOS"
}
```

### 3. Metrics Endpoint
```bash
curl -s https://arifos.arif-fazil.com/metrics/json | python -m json.tool
```

**Expected Response:**
```json
{
  "version": "v53.2.0-STANDALONE",
  "mode": "standalone",
  "status": "operational",
  "tools_count": 5,
  "tools": [
    "init_000",
    "agi_genius",
    "asi_act",
    "apex_judge",
    "vault_999"
  ]
}
```

### 4. HTTP Status Check
```bash
curl -I https://arifos.arif-fazil.com/health
```

**Expected:**
```
HTTP/2 200
content-type: application/json
```

### 5. Railway Fallback URL
If custom domain has issues, test Railway direct URL:
```bash
curl -s https://arifos-production.up.railway.app/health
```

Should return the same response as the custom domain.

## Troubleshooting

### If deployment still fails:

1. **Check Railway Logs**
   - Go to Railway dashboard
   - Navigate to your service
   - Check "Deploy Logs" tab
   - Look for Python errors or import failures

2. **Verify Build Phase**
   - Build should complete without errors
   - `pip install -e .` should succeed
   - No missing dependencies

3. **Verify Start Phase**
   - Should see: `Starting arifOS MCP Server (Standalone)`
   - Should see: `Uvicorn running on http://0.0.0.0:8000`
   - Should see: `Application startup complete`

4. **Check Healthcheck**
   - Railway will probe `/health` every few seconds
   - Should see successful 200 responses in logs
   - If you see 503 or timeout, server didn't start properly

5. **Domain Configuration**
   - If custom domain fails but Railway URL works, check Cloudflare DNS
   - CNAME should point to Railway service
   - Cloudflare proxy can be orange (proxied) or gray (DNS only)

## Success Indicators

✅ Deployment status shows "Active" in Railway dashboard
✅ Health endpoint returns 200 OK
✅ Custom domain https://arifos.arif-fazil.com/ resolves
✅ All 3 endpoints (/, /health, /metrics/json) return valid JSON
✅ Railway logs show "Application startup complete"

## Quick Test Script

```bash
#!/bin/bash
echo "Testing arifOS MCP Server..."
echo "================================"

echo -e "\n1. Health Check:"
curl -s https://arifos.arif-fazil.com/health | jq -r '.status'

echo -e "\n2. Version:"
curl -s https://arifos.arif-fazil.com/ | jq -r '.version'

echo -e "\n3. Tools Count:"
curl -s https://arifos.arif-fazil.com/metrics/json | jq -r '.tools_count'

echo -e "\n4. Domain:"
curl -s https://arifos.arif-fazil.com/health | jq -r '.domain'

echo -e "\n================================"
echo "✓ All tests completed!"
```

Save as `test_deployment.sh`, make executable, and run:
```bash
chmod +x test_deployment.sh
./test_deployment.sh
```

---

**Version**: v53.2.0
**Status**: Ready for deployment
**Expected Result**: Railway deployment succeeds within 2 minutes
