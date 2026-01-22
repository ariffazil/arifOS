# arifOS v50 Railway Deployment Guide

**Version**: v50.0.0
**Last Updated**: 2026-01-20
**Status**: Production Ready

---

## Overview

This guide walks you through deploying arifOS v50 Unified MCP Server to Railway, exposing 33 constitutional tools via HTTP/SSE for remote AI agents.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Railway Cloud Platform                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         arifOS MCP Server (HTTP/SSE)                  │ │
│  │  - 33 Constitutional Tools                            │ │
│  │  - FastAPI + Uvicorn                                  │ │
│  │  - Port: $PORT (auto-assigned by Railway)            │ │
│  └────────────┬──────────────────────────────────────────┘ │
│               │                                             │
│  ┌────────────┴─────────────┬────────────────┐            │
│  │  PostgreSQL (Ledger)     │  Redis (Cache) │            │
│  │  Railway Plugin          │  Railway Plugin│            │
│  └──────────────────────────┴────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            │
        ┌───────────────────┴───────────────────┐
        │      Remote AI Clients                │
        │  - Claude Code (remote)                │
        │  - Gemini CLI (cloud)                  │
        │  - OpenAI Codex (API)                  │
        │  - Custom MCP clients                  │
        └────────────────────────────────────────┘
```

---

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push arifOS to GitHub
3. **API Keys**: OpenAI, Anthropic, or Groq (for LLM engines)

---

## Step 1: Create Railway Project

### 1.1 Connect GitHub Repository

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your arifOS repository
4. Choose branch: `main`

### 1.2 Configure Build Settings

Railway should auto-detect:
- **Build Command**: (from `railway.json` or auto-detected)
- **Start Command**: Uses `Procfile` → `uvicorn arifos.core.mcp.sse:app`

---

## Step 2: Add Database Services

### 2.1 Add PostgreSQL (Ledger Storage)

1. Click "New" → "Database" → "Add PostgreSQL"
2. Railway auto-creates these variables:
   - `DATABASE_URL` (use this in your code)
   - `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`

**Remove manual PostgreSQL variables** (Railway manages these):
```bash
# DELETE THESE (managed by Railway plugin):
❌ POSTGRES_DB
❌ POSTGRES_USER
❌ POSTGRES_PASSWORD
❌ POSTGRES_PORT

# USE THIS INSTEAD:
✅ DATABASE_URL (auto-injected)
```

### 2.2 Add Redis (Cache)

1. Click "New" → "Database" → "Add Redis"
2. Railway auto-creates:
   - `REDIS_URL` (use this in your code)
   - `REDIS_HOST`, `REDIS_PORT`

**Remove manual Redis variable**:
```bash
❌ REDIS_PORT (managed by Railway)
✅ REDIS_URL (auto-injected)
```

### 2.3 Optional: Add Qdrant (Vector Database)

If using Qdrant for semantic search:

**Option A: Qdrant Cloud** (Recommended)
```bash
QDRANT_HOST=your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=arifos_vault999
```

**Option B: Self-Hosted Qdrant**
1. Deploy Qdrant container in Railway
2. Connect via internal DNS: `qdrant.railway.internal`

---

## Step 3: Configure Environment Variables

### 3.1 Core Configuration

Add these in Railway Dashboard → Variables:

```bash
# Environment
ARIFOS_ENV=production
ARIFOS_PORT=8000
LOG_LEVEL=info

# Constitutional Governance
FLOOR_ENFORCEMENT_MODE=strict
GOVERNANCE_MODE=HARD
TRINITY_ENABLED=true

# MCP Configuration (NEW)
AAA_MCP_TRANSPORT=http
AAA_MCP_PORT=8000
AAA_MCP_LLM_PROVIDER=auto

# Legacy Support (NEW)
ARIFOS_ALLOW_LEGACY_SPEC=1
ARIFOS_PHYSICS_DISABLED=0
```

### 3.2 LLM Provider Keys (Secrets)

⚠️ **Add as Railway Secrets** (not visible in logs):

```bash
# AGI Engine (Mind) - Choose one:
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# ASI Engine (Heart) - Choose one:
ANTHROPIC_API_KEY=sk-ant-...

# APEX Judge (Optional - for fast inference):
GROQ_API_KEY=gsk_...
```

**How to add secrets**:
1. Railway Dashboard → Variables
2. Click variable value field
3. Click "🔒" icon to mark as secret
4. Paste API key
5. Secret will be hidden in logs

### 3.3 Storage Paths

```bash
# Ledger (Constitutional audit trail)
LEDGER_PATH=/app/ledger

# Vault (Knowledge base)
VAULT_PATH=/app/VAULT999
```

**Note**: Railway uses ephemeral filesystem. For persistent storage:
- Use PostgreSQL for ledger (recommended)
- Use Railway Volumes for vault files

### 3.4 Remove Placeholder Variables

Delete these from Railway:

```bash
❌ CLOUDFLARE_TUNNEL_TOKEN (unless using Cloudflare)
❌ BUILD_DATE (Railway provides RAILWAY_GIT_COMMIT_SHA)
❌ VCS_REF (use RAILWAY_GIT_COMMIT_SHA instead)
❌ RENDER (not needed for Railway)
```

---

## Step 4: Deploy

### 4.1 Initial Deployment

Railway will automatically deploy when you:
1. Push to GitHub main branch
2. Modify variables in Railway Dashboard

**Monitor deployment**:
- Railway Dashboard → Deployments → View Logs

### 4.2 Verify Deployment

Check health endpoint:
```bash
curl https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "mode": "SSE",
  "tools": 33,
  "framework": "FastAPI",
  "doc_url": "/docs"
}
```

### 4.3 Access API Documentation

Visit your Railway URL:
```
https://your-app.up.railway.app/docs
```

You should see FastAPI Swagger UI with:
- `/sse` endpoint (MCP connection)
- `/messages` endpoint (MCP protocol)
- `/health` endpoint (health check)

---

## Step 5: Connect Remote AI Clients

### 5.1 Claude Code (Remote Mode)

Update `.claude/mcp.json` to use Railway URL:

```json
{
  "mcpServers": {
    "arifos-remote": {
      "transport": {
        "type": "sse",
        "url": "https://your-app.up.railway.app/sse"
      },
      "description": "arifOS v50 Remote MCP Server (Railway)"
    }
  }
}
```

### 5.2 Gemini CLI

```bash
# Configure Gemini to use Railway MCP server
export MCP_SERVER_URL="https://your-app.up.railway.app/sse"
gemini --mcp-transport=sse
```

### 5.3 Custom MCP Client

```python
import httpx
from mcp.client import Client
from mcp.client.sse import sse_client

async def connect_to_railway():
    async with sse_client("https://your-app.up.railway.app/sse") as (read, write):
        client = Client("custom-client")
        await client.initialize(read, write)

        # List tools
        tools = await client.list_tools()
        print(f"Connected to Railway: {len(tools)} tools available")

        # Call tool
        result = await client.call_tool("mcp_111_sense", {"query": "test"})
        print(result)
```

---

## Step 6: Production Optimization

### 6.1 Enable Constitutional Logging

Add structured logging for audit trail:

```bash
# Railway Variables
LOG_FORMAT=json
LOG_FILE=/app/logs/arifos.log
ENABLE_LEDGER_EXPORT=true
```

### 6.2 Scale Configuration

Railway auto-scales, but you can configure:

```bash
# Uvicorn workers (in Procfile)
web: uvicorn arifos.core.mcp.sse:app --host 0.0.0.0 --port $PORT --workers 4
```

**Recommended settings**:
- **Development**: 1 worker
- **Production**: 4 workers (for Railway Hobby plan)
- **Enterprise**: 8-16 workers (for Railway Pro plan)

### 6.3 Add Health Checks

Railway automatically monitors `/health` endpoint. Configure response:

```python
# In arifos/core/mcp/sse.py
@app.get("/health")
async def handle_health():
    return {
        "status": "healthy",
        "mode": "SSE",
        "tools": len(TOOLS),
        "framework": "FastAPI",
        "doc_url": "/docs",
        "version": "v50.0.0",
        "constitutional_floors": 13,
        "trinity_enabled": os.environ.get("TRINITY_ENABLED", "false")
    }
```

---

## Step 7: Monitoring & Debugging

### 7.1 View Logs

Railway Dashboard → Service → Logs

Filter by level:
```bash
# Error logs only
grep "ERROR" in Railway logs

# Constitutional violations
grep "VOID" in Railway logs
```

### 7.2 Constitutional Metrics

Add Prometheus metrics endpoint:

```python
# In sse.py
from prometheus_client import Counter, Histogram

tool_calls = Counter("arifos_tool_calls", "Total MCP tool calls")
constitutional_violations = Counter("arifos_violations", "Constitutional floor violations")

@app.get("/metrics")
async def metrics():
    # Export Prometheus metrics
    pass
```

### 7.3 Debug Mode

Enable debug logging in Railway variables:

```bash
LOG_LEVEL=debug
ARIFOS_DEBUG=1
```

⚠️ **Disable in production** - debug logs may expose sensitive data.

---

## Troubleshooting

### Issue 1: "Module not found" Error

**Symptom**: Railway build fails with `ModuleNotFoundError`

**Solution**: Check `requirements.txt` includes all dependencies:
```bash
# Verify locally
pip install -r requirements.txt
python -m arifos.core.mcp.sse
```

### Issue 2: Database Connection Timeout

**Symptom**: `psycopg2.OperationalError: timeout`

**Solution**: Increase connection pool timeout:
```python
# In your database config
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections every hour
)
```

### Issue 3: MCP Client Can't Connect

**Symptom**: `McpError: -32001: Request timed out`

**Solution**: Check Railway URL is correct:
```bash
# Test Railway endpoint
curl https://your-app.up.railway.app/health

# Check Railway logs for errors
Railway Dashboard → Logs → Filter "ERROR"
```

### Issue 4: Constitutional Floor Violations

**Symptom**: Tools return `{"verdict": "VOID", "reason": "F1 Amanah violation"}`

**Solution**: Check floor enforcement mode:
```bash
# Temporarily relax for debugging
FLOOR_ENFORCEMENT_MODE=soft
GOVERNANCE_MODE=SOFT

# Re-enable for production
FLOOR_ENFORCEMENT_MODE=strict
GOVERNANCE_MODE=HARD
```

---

## Security Checklist

Before going to production:

- [ ] **Secrets in Railway Secrets Manager** (not plaintext variables)
- [ ] **HTTPS Enabled** (Railway provides automatic SSL)
- [ ] **API Keys Rotated** (if exposed in Git history)
- [ ] **Database Backups Enabled** (Railway automatic backups)
- [ ] **Rate Limiting Configured** (prevent abuse)
- [ ] **CORS Configured** (restrict allowed origins)
- [ ] **Constitutional Floors on HARD Mode** (`GOVERNANCE_MODE=HARD`)
- [ ] **Audit Logging Enabled** (`ENABLE_LEDGER_EXPORT=true`)

---

## Cost Optimization

### Railway Pricing

**Hobby Plan** ($5/month):
- 500 hours execution time
- $0.000231/min after
- Suitable for personal use

**Pro Plan** ($20/month):
- Unlimited execution time
- Priority support
- Recommended for production

### Optimization Tips

1. **Use Railway Plugins**: Managed databases are cost-effective
2. **Enable Caching**: Redis reduces database queries
3. **Optimize Workers**: Don't over-provision (start with 2 workers)
4. **Monitor Usage**: Railway Dashboard → Metrics

---

## Next Steps

1. ✅ **Deploy to Railway** - Follow this guide
2. ✅ **Test MCP Connection** - Connect from Claude Code/Gemini CLI
3. ✅ **Enable Monitoring** - Set up logging and metrics
4. ✅ **Scale as Needed** - Adjust workers based on load

---

## Support

**Documentation**:
- [Railway Docs](https://docs.railway.app)
- [MCP Specification](https://modelcontextprotocol.io)
- [arifOS GitHub](https://github.com/arif/arifOS)

**Issues**:
- Railway: [Railway Help](https://help.railway.app)
- arifOS: GitHub Issues

---

**Version**: v50.0.0
**Status**: PRODUCTION READY ✅
**Authority**: F1-F13 Constitutional Governance Enforced
