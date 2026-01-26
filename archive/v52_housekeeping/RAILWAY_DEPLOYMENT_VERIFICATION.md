# Railway Deployment Verification - v51.1.0
## Immediate Action Required: Deploy AAA_MCP to Production

**Status**: PRE-DEPLOYMENT | **Priority**: CRITICAL  
**Current State**: Body API deployed, AAA_MCP MCP server NOT deployed  
**Target**: Deploy AAA_MCP SSE server to Railway and validate

---

## 1. Current Production State (WRONG)

### What's Actually Deployed

```bash
# railway.toml shows:
startCommand = "uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"

# This is the Body API (FastAPI), NOT the MCP server
URL: https://arifos-production.up.railway.app/
Health: /health (returns Body API health)

# This does NOT expose:
# - /sse (MCP SSE endpoint)
# - /messages (MCP message endpoint)
# - 5 constitutional tools
```

### What's Missing (NEEDED)

```bash
# AAA_MCP SSE server should be:
startCommand = "python -m AAA_MCP sse"

# Should expose:
# - GET /sse (MCP SSE connection)
# - POST /messages (MCP messages)
# - GET /health (MCP health with tool list)
# - 5 tools: 000_init, agi_genius, asi_act, apex_judge, 999_vault
```

---

## 2. Immediate Action: Deploy AAA_MCP

### Option A: Quick Deploy (Recommended)

```bash
# 1. Update railway.toml for MCP
cat > railway.toml << 'EOF'
[build]
builder = "nixpacks"
buildCommand = "pip install -e ."

[deploy]
startCommand = "python -m AAA_MCP sse"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
numReplicas = 1
EOF

# 2. Deploy to Railway
railway login
railway link  # Link to arifos-production project
railway variables set ARIFOS_MCP_PORT=8000
railway up

# 3. Verify deployment
sleep 30  # Wait for startup
curl https://arifos-production.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "tools": 5,
#   "tool_names": ["000_init", "agi_genius", "asi_act", "apex_judge", "999_vault"],
#   "version": "v51.1.0",
#   "engines_available": true
# }
```

### Option B: Dual Deployment (Advanced)

Deploy BOTH Body API AND AAA_MCP on same project:

```toml
# railway.toml - Dual service
[[services]]
name = "arifos-body-api"
type = "web"
buildCommand = "pip install -e ."
startCommand = "uvicorn arifos.core.integration.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"
healthcheckPath = "/health"
port = 8000

[[services]]
name = "arifos-mcp"
type = "web"
buildCommand = "pip install -e ."
startCommand = "python -m AAA_MCP sse"
healthcheckPath = "/health"
port = 8001

# Access:
# - Body API: https://arifos-production.up.railway.app/
# - MCP: https://arifos-production.up.railway.app:8001/
```

---

## 3. Pre-Deployment Validation

### Local Testing (MUST PASS)

```bash
# Test 1: AAA_MCP starts locally
python -m AAA_MCP sse &
PID=$!
sleep 5
curl http://localhost:8000/health
echo "✅ AAA_MCP health check"
kill $PID

# Expected: JSON with status, tools, version

# Test 2: Stdio mode (Claude Desktop)
python -m AAA_MCP &
PID=$!
sleep 2
# Should show banner with tools
kill $PID

# Test 3: Tool listing
timeout 10 python -c "
import asyncio
from AAA_MCP.server import create_aaa_server
from mcp.server.stdio import stdio_server

async def test():
    async with stdio_server() as (read, write):
        server = create_aaa_server()
        tools = await server.list_tools()
        print(f'Tools: {[t.name for t in tools]}')

asyncio.run(test())
"
# Expected: ['000_init', 'agi_genius', 'asi_act', 'apex_judge', '999_vault']
```

### Dependencies Check

```bash
# Verify all core imports work
python -c "
from AAA_MCP.bridge import (
    ENGINES_AVAILABLE,
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)
print(f'Kernels available: {ENGINES_AVAILABLE}')
print(f'Bridge routers: loaded')
"

# Expected: Kernels available: True (or False with fallback mode)
```

---

## 4. Post-Deployment Validation

### Health Check Verification

```bash
# After railway up succeeds:

# 1. Basic health
HEALTH_RESPONSE=$(curl -s https://arifos-production.up.railway.app/health)
echo "$HEALTH_RESPONSE" | jq '.'

# Must contain:
# - status: "healthy"
# - tools: 5
# - tool_names: list of 5 tools
# - version: "v51.1.0"

# 2. Tool list verification
if echo "$HEALTH_RESPONSE" | jq -e '.tools == 5' > /dev/null; then
    echo "✅ Tool count correct"
else
    echo "❌ Tool count wrong"
    exit 1
fi

# 3. SSE endpoint test
curl -N https://arifos-production.up.railway.app/sse
# Should start SSE stream (hangs, cancel with Ctrl+C)
```

### Claude Desktop Integration Test

```json
{
  "mcpServers": {
    "arifos-aaa-test": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "/path/to/arifOS",
      "env": {
        "AAA_MCP_PORT": "8000"
      }
    }
  }
}
```

Test: Ask Claude to "Use the agi_genius tool to check if climate change is real"  
Expected: Should invoke tool, get SEAL verdict with truth_score ≥ 0.99

---

## 5. Troubleshooting

### Problem: Health check fails

```bash
# Check Railway logs
railway logs --tail=100

# Common issues:
# 1. Port binding wrong
# Current: startCommand = "python -m AAA_MCP sse"
# Should use $PORT env var

# Fix:
railway variables set AAA_MCP_PORT=$PORT
# Or update code to respect PORT env var
```

### Problem: Core kernels not available

```bash
# AAA_MCP logs show: ENGINES_AVAILABLE=False

# Fix 1: Ensure arifos is installed properly
railway variables set PYTHONPATH=/app

# Fix 2: Install in editable mode
buildCommand = "pip install -e ."

# Fix 3: Run dependency check
python -c "from arifos.core.agi.kernel import AGINeuralCore; print('OK')"
```

### Problem: CORS errors

```bash
# SSE endpoint needs CORS
# AAA_MCP/sse.py should have:
allow_origins=["*"]

# Railway specific: Add CORS domain
railway variables set ALLOWED_ORIGINS="https://claude.ai,https://cline.bot"
```

---

## 6. Success Criteria

**MUST HAVE before v52 planning**:

- [ ] ✅ `curl https://arifos-production.up.railway.app/health` returns 200
- [ ] ✅ Health JSON shows `"tools": 5` with correct names
- [ ] ✅ SSE endpoint accessible: `curl -N https://.../sse` works
- [ ] ✅ Tool invocation works via MCP protocol  
- [ ] ✅ Version shows `v51.1.0` in health response
- [ ] ✅ Rate limiting functional (optional but preferred)
- [ ] ✅ Logs show no errors on startup
- [ ] ✅ Can sustain 10+ concurrent connections
- [ ] ✅ Response time < 100ms for simple tool calls
- [ ] ✅ Claude Desktop can connect and use tools

**Timeline**: Deploy within 24-48 hours, validate within 72 hours  
**Blocker**: v52 planning cannot proceed until v51 is production-verified

---

## 7. Next Steps After v51 Deployment

### Immediate (Next 72 hours):
1. Deploy AAA_MCP SSE to Railway
2. Validate health endpoint
3. Test with Claude Desktop
4. Document any issues
5. Create v51.1.0-SEAL git tag

### Short-term (Week 1):
1. Monitor metrics for 7 days
2. Verify SEAL rate > 80%  
3. Check for constitutional violations
4. Document production behavior
5. Prepare v51 retrospective

### Medium-term (Week 2-3):
1. Analyze performance data
2. Identify bottlenecks
3. Plan v52 improvements (if needed)
4. Begin bridge purification (if v51 stable)

---

## 8. Authority & Escalation

**Decision Point**: v51 must be Railway-deployed and validated  
**Authority**: 000 (arif) must approve this deployment  
**If Blocked**: Create GitHub issue with deployment logs  
**If Fails**: Rollback to Body API and document failure modes

---

**Status**: PRE-DEPLOYMENT | **Action Required**: Deploy AAA_MCP to Railway  
**Verdict**: **888_HOLD** ⏸️ - Cannot proceed to v52 until v51 is production-validated

**DITEMPA BUKAN DIBERI** - First deploy, then improve