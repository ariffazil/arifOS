# arifOS Railway Deployment Runbook
## Governed Backend for aaa-mcp + aclip-cai + state/arifos mirror

**Version:** v60.0-FORGE  
**Status:** Production-Ready  
**Constitution:** 13 Floors (F1-F13) Enforced  

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Environment Variables](#2-environment-variables)
3. [MCP Endpoints](#3-mcp-endpoints)
4. [Health Checks](#4-health-checks)
5. [Migration from oo0-STATE](#5-migration-from-oo0-state)
6. [Deployment Procedures](#6-deployment-procedures)
7. [Operations & Monitoring](#7-operations--monitoring)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RAILWAY DEPLOYMENT                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐      │
│  │   PostgreSQL    │    │     Redis       │    │   arifOS App    │      │
│  │   (VAULT999)    │◄──►│  (Mind Vault)   │◄──►│  (MCP Server)   │      │
│  │                 │    │                 │    │                 │      │
│  │ • vault_ledger  │    │ • Session state │    │ • 10 Canon Tools│      │
│  │ • vault_head    │    │ • 24h TTL       │    │ • F1-F13 Floors │      │
│  │ • Merkle chain  │    │ • Cross-call    │    │ • Trinity ΔΩΨ   │      │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘      │
│           ▲                      ▲                      │                │
│           │                      │                      ▼                │
│           └──────────────────────┴────────► ┌─────────────────┐          │
│                                             │   External      │          │
│                                             │   Clients       │          │
│                                             │                 │          │
│                                             │ • aaa-mcp       │          │
│                                             │ • aclip-cai     │          │
│                                             │ • state/arifos  │          │
│                                             └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Service Topology

| Service | Type | Purpose | Persistence |
|---------|------|---------|-------------|
| arifos-governed-backend | Web Service | MCP Server with constitutional enforcement | Stateless (state in Postgres/Redis) |
| PostgreSQL | Plugin | VAULT999 immutable ledger | Persistent (Railway managed) |
| Redis | Plugin | Session state cache | Ephemeral (24h TTL) |

---

## 2. Environment Variables

### Required Variables (Auto-set by Railway)

| Variable | Source | Purpose |
|----------|--------|---------|
| `DATABASE_URL` | PostgreSQL plugin | VAULT999 ledger connection |
| `REDIS_URL` | Redis plugin | Mind Vault session cache |
| `PORT` | Railway runtime | Server listen port (typically 8080) |

### Required Variables (Set in Railway Dashboard)

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `HOST` | `0.0.0.0` | - | Bind address (keep as 0.0.0.0) |
| `ARIFOS_ENV` | `production` | production, staging | Runtime environment |
| `GOVERNANCE_MODE` | `HARD` | HARD, SOFT | Constitutional strictness |
| `VAULT_BACKEND` | `postgres` | postgres, memory | Persistence backend |
| `AAA_MCP_TRANSPORT` | `sse` | sse, http, stdio | MCP transport mode |
| `LOG_LEVEL` | `info` | debug, info, warning, error | Log verbosity |

### Optional Variables (Feature-dependent)

| Variable | Required For | Description |
|----------|--------------|-------------|
| `BRAVE_API_KEY` | `reality_search` tool | Brave Search API for web grounding |
| `BROWSERBASE_API_KEY` | Browser automation | Browserbase for web browsing |
| `PYTHONUNBUFFERED` | Log streaming | Set to `1` for real-time logs |

### Setting Variables in Railway

```bash
# Via Railway CLI
railway variables set GOVERNANCE_MODE=HARD
railway variables set BRAVE_API_KEY=your_key_here

# Via Railway Dashboard
# Project → Variables → Add Variable
```

---

## 3. MCP Endpoints

### Transport Modes

| Mode | Endpoint | Use Case |
|------|----------|----------|
| **SSE** (recommended) | `/sse` | Streaming events for Claude, Cursor |
| HTTP | `/messages` | Direct JSON-RPC POST |
| STDIO | stdin/stdout | Local agents only (not for Railway) |

### Endpoint Reference

```
GET  /              → Service info & endpoint catalog
GET  /health        → Health check (Railway monitoring)
GET  /sse           → SSE connection endpoint
POST /messages      → MCP JSON-RPC message endpoint
```

### Client Configuration

#### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "arifos-governed": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sse@latest",
        "https://arifos-your-project.up.railway.app/sse"
      ],
      "env": {
        "BRAVE_API_KEY": "your_key_here"
      }
    }
  }
}
```

#### Direct SSE Client

```python
from mcp import Client
from mcp.transports.sse import SseClientTransport

async with SseClientTransport("https://arifos-your-project.up.railway.app/sse") as transport:
    client = Client(transport)
    await client.connect()
    
    # Use the 10 canonical tools
    result = await client.call_tool("forge", {
        "query": "Analyze safety implications of...",
        "session_id": "demo-001",
        "mode": "full"
    })
```

### The 10 Canonical Tools

| # | Tool | Engine | Floors |
|---|------|--------|--------|
| 1 | `init_gate` | 000_INIT | F11, F12 |
| 2 | `agi_sense` | Δ MIND | F2, F4 |
| 3 | `agi_think` | Δ MIND | F4 |
| 4 | `agi_reason` | Δ MIND | F2, F4, F7 |
| 5 | `reality_search` | Δ MIND | F2, F10 |
| 6 | `asi_empathize` | Ω HEART | F5, F6 |
| 7 | `asi_align` | Ω HEART | F9 |
| 8 | `apex_verdict` | Ψ SOUL | F2, F3, F8 |
| 9 | `vault_seal` | 999_VAULT | F1 |
| 10 | `forge` | UNIFIED | F1-F13 |

---

## 4. Health Checks

### Endpoint: `GET /health`

**Railway Configuration:**
- Path: `/health`
- Timeout: 30 seconds
- Interval: Managed by Railway

**Response Schema:**

```json
{
  "status": "ok",
  "version": "60.0.0-FORGE",
  "mcp_tools": 10,
  "checks": {
    "postgres": "connected",
    "redis": "connected",
    "vault": "ready"
  }
}
```

### Health Check Failure Behavior

| Failure | Action | Recovery |
|---------|--------|----------|
| Postgres unavailable | Use memory fallback | Auto-retry every 30s |
| Redis unavailable | Use local fallback | Auto-retry every 30s |
| Both unavailable | Status: `degraded` | Manual intervention |

### Custom Health Monitoring

```python
import httpx

async def check_arifos_health(url: str = "https://arifos-your-project.up.railway.app"):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/health")
        data = response.json()
        
        assert data["status"] == "ok", "Service unhealthy"
        assert data["mcp_tools"] == 10, "Tools unavailable"
        
        return data
```

---

## 5. Migration from oo0-STATE

### Migration Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MIGRATION PATH                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LOCAL oo0-STATE ─────────────────────► RAILWAY DEPLOYMENT          │
│                                                                      │
│  ┌─────────────────┐                ┌─────────────────┐             │
│  │ Local SQLite    │ ──migrate──►   │ Railway Postgres │             │
│  │ (if any)        │                │ (VAULT999)       │             │
│  └─────────────────┘                └─────────────────┘             │
│                                                                      │
│  ┌─────────────────┐                ┌─────────────────┐             │
│  │ Local memory    │ ──migrate──►   │ Railway Redis    │             │
│  │ (in-process)    │                │ (Mind Vault)     │             │
│  └─────────────────┘                └─────────────────┘             │
│                                                                      │
│  ┌─────────────────┐                ┌─────────────────┐             │
│  │ Local env vars  │ ──migrate──►   │ Railway env vars │             │
│  │ (.env.oo0)      │                │ (dashboard)      │             │
│  └─────────────────┘                └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
```

### Pre-Migration Checklist

- [ ] Backup local state if needed
- [ ] Document current API keys from `.env.oo0`
- [ ] Verify Railway CLI installed: `npm install -g @railway/cli`
- [ ] Login to Railway: `railway login`

### Migration Steps

#### Step 1: Initialize Railway Project

```bash
cd /root/arifOS

# Link to existing Railway project or create new one
railway link

# Verify connection
railway status
```

#### Step 2: Provision Plugins

```bash
# Add PostgreSQL plugin (VAULT999 backend)
railway add --plugin postgresql

# Add Redis plugin (Mind Vault cache)
railway add --plugin redis
```

#### Step 3: Migrate Environment Variables

From `/root/.env.oo0`, migrate these keys:

```bash
# Required for reality_search tool
railway variables set BRAVE_API_KEY="BSAHQnxf-jTMFfGYe3MKmsJr7Uq8uEU"

# Optional: Browser automation
# railway variables set BROWSERBASE_API_KEY="your_key_here"

# Core settings
railway variables set GOVERNANCE_MODE=HARD
railway variables set VAULT_BACKEND=postgres
railway variables set AAA_MCP_TRANSPORT=sse
railway variables set LOG_LEVEL=info
```

#### Step 4: Database Migration

```bash
# Run the VAULT999 table migration
python scripts/railway_migration.py
```

This creates:
- `vault_ledger` - Immutable audit trail
- `vault_head` - Chain head tracking

#### Step 5: Verify Migration

```bash
# Test database connectivity and schema
python scripts/railway_verify.py
```

Expected output:
```
OK vault_ledger entries: 0
OK vault_head: empty
OK Test entry created: sequence=1
OK Total entries: 1
OK ALL CHECKS PASSED!
```

#### Step 6: Deploy

```bash
# Deploy to Railway
railway up

# Follow logs
railway logs --follow
```

### Post-Migration Verification

```bash
# Test health endpoint
curl https://arifos-your-project.up.railway.app/health

# Test MCP connection
# (Use Claude Desktop or direct SSE client)
```

---

## 6. Deployment Procedures

### Standard Deployment

```bash
# 1. Ensure tests pass
pytest tests/ -v

# 2. Deploy
railway up

# 3. Verify deployment
railway logs --follow
```

### Blue-Green Deployment (Zero Downtime)

Railway automatically handles this with rolling deployments:

```bash
# New deployment starts alongside old
# Health check passes → traffic switches
# Old deployment drains connections

railway up

# Monitor the transition
railway logs --follow
```

### Rollback Procedure

```bash
# List previous deployments
railway deployments

# Rollback to specific deployment
railway rollback <deployment-id>

# Or rollback to previous
railway rollback
```

### Environment Promotion

```
local → staging → production
```

```bash
# Deploy to staging
railway environment switch staging
railway up

# Promote to production
railway environment switch production
railway up
```

---

## 7. Operations & Monitoring

### Log Streaming

```bash
# Real-time logs
railway logs --follow

# Filter by service
railway logs --service arifos-governed-backend

# Last 100 lines
railway logs --tail 100
```

### Metrics Monitoring

The MCP server exposes constitutional metrics at runtime. Access via:

```python
# From within the service
from aaa_mcp.services.constitutional_metrics import get_flight_recorder

recorder = get_flight_recorder()
metrics = recorder.get_metrics()
```

### Database Operations

```bash
# Connect to Postgres
railway connect postgres

# Run SQL
railway run psql -c "SELECT COUNT(*) FROM vault_ledger;"

# Backup (via Railway dashboard or CLI)
railway variables get DATABASE_URL
# Use the URL with pg_dump
```

### Redis Operations

```bash
# Connect to Redis
railway connect redis

# Check keys
railway run redis-cli KEYS "arifos:session:*"

# Get session data
railway run redis-cli GET "arifos:session:your-session-id"
```

### Scaling

```bash
# Horizontal scaling (multiple replicas)
railway scale --replicas 3

# Vertical scaling (change instance type)
# Via Railway Dashboard → Service → Settings
```

---

## 8. Troubleshooting

### Common Issues

#### Issue: Database Connection Failed

**Symptoms:**
```
[SessionLedger] Postgres init failed: connection refused
```

**Resolution:**
```bash
# Verify DATABASE_URL is set
railway variables get DATABASE_URL

# Restart service to pick up new URL
railway up
```

#### Issue: Redis Connection Failed

**Symptoms:**
```
Redis connection failed: Error connecting to redis
```

**Resolution:**
```bash
# Check REDIS_URL
railway variables get REDIS_URL

# MindVault falls back to local memory - service continues
```

#### Issue: Health Check Failing

**Symptoms:**
- Railway shows unhealthy status
- Deployments failing

**Resolution:**
```bash
# Check logs
railway logs

# Verify /health endpoint manually
curl https://your-domain.up.railway.app/health

# Check if port binding is correct (must use PORT env var)
```

#### Issue: MCP Tools Not Responding

**Symptoms:**
- Client connects but tools timeout
- No response from forge/init_gate

**Resolution:**
```bash
# Check if server is running
railway status

# Verify tools are registered
# Look for "Registered 10 tools" in logs

# Test locally first
python -m aaa_mcp stdio
```

### Diagnostic Commands

```bash
# Full system status
railway status

# Service details
railway service

# Environment variables (sanitized)
railway variables

# Recent deployments
railway deployments
```

### Emergency Procedures

#### Complete Service Reset

```bash
# Scale to zero
railway scale --replicas 0

# Clear Redis (optional)
railway run redis-cli FLUSHDB

# Scale back up
railway scale --replicas 1
```

#### Database Recovery

```bash
# If vault_ledger is corrupted:
railway connect postgres

# Truncate and re-initialize (LOSES DATA)
TRUNCATE vault_ledger, vault_head;

# Re-run migration
python scripts/railway_migration.py
```

---

## Appendix A: File Reference

| File | Purpose |
|------|---------|
| `railway.json` | Railway service configuration |
| `railway.toml` | Alternative TOML configuration |
| `Dockerfile` | Container build instructions |
| `scripts/start_server.py` | Production entry point |
| `scripts/railway_migration.py` | Database migration tool |
| `scripts/railway_verify.py` | Post-migration verification |
| `aaa_mcp/server.py` | MCP server with 10 tools |
| `aaa_mcp/sessions/session_ledger.py` | VAULT999 persistence |
| `aaa_mcp/services/redis_client.py` | MindVault cache |

## Appendix B: Constitutional Compliance

All deployments must maintain:

| Floor | Requirement | Verification |
|-------|-------------|--------------|
| F1 Amanah | Immutable audit | `vault_ledger` table |
| F2 Truth | Evidence-backed | `reality_search` tool |
| F3 Tri-Witness | ΔΩΨ consensus | `apex_verdict` tool |
| F4 Clarity | Ambiguity reduction | `agi_sense` tool |
| F5 Peace² | Stability check | `asi_empathize` tool |
| F6 Empathy | Stakeholder protection | `asi_empathize` tool |
| F7 Humility | Uncertainty bounds | Ω₀ in all outputs |
| F8 Genius | Resource efficiency | Metrics logging |
| F9 Anti-Hantu | No fake consciousness | `asi_align` tool |
| F10 Ontology | Grounded claims | Axiom Engine |
| F11 Authority | Auth verification | `init_gate` tool |
| F12 Defense | Injection hardening | Pre-scan on all inputs |
| F13 Sovereign | Human veto | `888_HOLD` verdict |

---

*DITEMPA BUKAN DIBERI 🔥💜*  
*Forged, Not Given*
