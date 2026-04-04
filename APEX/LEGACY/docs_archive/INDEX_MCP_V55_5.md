# arifOS MCP Documentation Index v60.0-FORGE

**Purpose:** Quick reference for AI/LLM agents deploying arifOS MCP Server  
**Version:** v60.0-FORGE (RUKUN AGI)  
**Architecture:** 5-Organ Constitutional Kernel

---

## Start Here

| If you want to... | Read this document |
|-------------------|-------------------|
| **Deploy to production** | [`MCP_DEPLOYMENT_GUIDE_V60.md`](MCP_DEPLOYMENT_GUIDE_V60.md) |
| **Connect an AI client** | [`MCP_CLIENT_CONFIGURATIONS.md`](MCP_CLIENT_CONFIGURATIONS.md) |
| **Deploy to Railway** | [`RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md) |
| **Quick reference** | [`../aaa_mcp/README.md`](../aaa_mcp/README.md) |
| **Architecture details** | [`V60_ARCHITECTURE.md`](V60_ARCHITECTURE.md) |

---

## Architecture Overview

### 5-Organ Constitutional Kernel

```
┌────────────────────────────────────────────────────────────┐
│                    AAA MCP Server                          │
│              (13 Tools / 13 Constitutional Floors)         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Airlock │→ │  Mind   │→ │  Heart  │→│  Soul   │→...   │
│  │  (000)  │  │(111-333)│  │(555-666)│  │(444-888)│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│   F11/F12      F2/F4/F7/F8   F1/F5/F6/F9  F3/F8/F9/F10    │
│                                                            │
│  ┌─────────┐                                               │
│  │ Memory  │                                               │
│  │  (999)  │                                               │
│  └─────────┘                                               │
│   F1/F3/F13                                                │
│                                                            │
│  core.pipeline.forge() — Single entrypoint                 │
└────────────────────────────────────────────────────────────┘
```

### Key Files

| File | Purpose |
|------|---------|
| `core/pipeline.py` | Unified 000-999 pipeline |
| `core/organs/_0_init.py` | Airlock (F11/F12) |
| `core/organs/_1_agi.py` | Mind (F2/F4/F7/F8) |
| `core/organs/_2_asi.py` | Heart (F1/F5/F6/F9) |
| `core/organs/_3_apex.py` | Soul (F3/F8/F9/F10/F13) |
| `core/organs/_4_vault.py` | Memory (F1/F13) |
| `aaa_mcp/server.py` | MCP tool definitions (13 tools) |
| `scripts/start_server.py` | Production entry point |

---

## Deployment Paths

### Path 1: Railway (Cloud) - RECOMMENDED

```bash
# Prerequisites
npm install -g @railway/cli
railway login

# Deploy
cd arifOS
railway up

# Configure
railway variables set PORT=8080
railway variables set AAA_MCP_TRANSPORT=sse

# Verify
railway domain
curl https://your-app.up.railway.app/health
```

**Docs:** [`RAILWAY_DEPLOYMENT.md`](RAILWAY_DEPLOYMENT.md)

### Path 2: Docker (Container)

```bash
# Build
docker build -t arifos-mcp:v60 .

# Run
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e AAA_MCP_TRANSPORT=sse \
  arifos-mcp:v60
```

**Docs:** [`MCP_DEPLOYMENT_GUIDE_V60.md`](MCP_DEPLOYMENT_GUIDE_V60.md) → Docker section

### Path 3: Local Development

```bash
# Install
pip install -e .

# Run stdio mode
python -m aaa_mcp

# Run SSE mode
python -m aaa_mcp sse

# Validate
python scripts/deploy_mcp.py --mode validate
```

---

## Client Configuration

### Kimi

**Path:** `.kimi/mcp.json`

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {"ARIFOS_CONSTITUTIONAL_MODE": "AAA"},
      "alwaysAllow": ["init_gate", "trinity_forge", "agi_reason", "apex_verdict"]
    }
  }
}
```

### Claude Desktop

**Path:** `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS"
    },
    "arifos-cloud": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/sse"
    }
  }
}
```

**Full configs:** [`MCP_CLIENT_CONFIGURATIONS.md`](MCP_CLIENT_CONFIGURATIONS.md)

---

## 13 MCP Tools

| Tool | Organ | Floors | Purpose |
|------|-------|--------|---------|
| `init_gate` | Airlock | F11, F12 | Session initialization |
| `trinity_forge` | All | F1-F13 | Unified 000-999 pipeline |
| `agi_sense` | Mind | F4, F7 | Intent classification |
| `agi_think` | Mind | F2, F4 | Hypothesis generation |
| `agi_reason` | Mind | F2, F4, F7 | Logical reasoning |
| `asi_empathize` | Heart | F5, F6 | Stakeholder analysis |
| `asi_align` | Heart | F5, F6, F9 | Ethics/policy check |
| `apex_verdict` | Soul | F3, F8, F9, F10 | Final judgment |
| `reality_search` | Mind | F2, F10 | Web grounding |
| `vault_seal` | Memory | F1, F3 | Immutable ledger |
| `tool_router` | Meta | — | Dynamic routing |
| `vault_query` | Memory | — | Ledger retrieval |
| `truth_audit` | Meta | F2, F4 | Claim verification |

---

## Environment Variables

### Required

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port |
| `HOST` | `0.0.0.0` | Bind address |
| `AAA_MCP_TRANSPORT` | `sse` | Transport (stdio/sse/http) |

### Optional

| Variable | Description |
|----------|-------------|
| `ARIFOS_CONSTITUTIONAL_MODE` | `AAA` (default), `SOFT`, `HARD` |
| `BRAVE_API_KEY` | Brave Search API |
| `BROWSERBASE_API_KEY` | Browserbase API |
| `DATABASE_URL` | PostgreSQL URL |
| `REDIS_URL` | Redis URL |
| `SECRET_KEY` | JWT signing secret |
| `LOG_LEVEL` | `info`, `debug`, `warning`, `error` |

---

## Endpoints

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `GET /` | Service info | None |
| `GET /health` | Health check | None |
| `GET /metrics` | Prometheus metrics | None |
| `GET /stats` | JSON statistics | None |
| `/sse` | SSE transport | None |
| `/messages` | MCP messages | None |

---

## Validation Checklist

Before declaring deployment complete:

- [ ] `python scripts/deploy_mcp.py --mode validate` passes
- [ ] `curl http://localhost:8080/health` returns healthy
- [ ] MCP client can list tools
- [ ] MCP client can call `init_gate`
- [ ] MCP client can call `trinity_forge`

---

## Troubleshooting Quick Reference

| Issue | Fix |
|-------|-----|
| "Module not found: core" | `pip install -e .` |
| "Port already in use" | `PORT=8000 python -m aaa_mcp` |
| "Core organs not available" | Check `core/` exists; reinstall |
| "Connection refused" | Check server is running |
| "Injection detected" | Check env vars for suspicious patterns |

---

## Important Notes for AI Agents

1. **Always validate first:** Run `scripts/deploy_mcp.py --mode validate` before any deployment

2. **Use stdio for local:** When connecting local AI clients (Kimi, Claude Desktop), use stdio transport

3. **Use SSE for cloud:** When deploying to Railway or remote servers, use SSE transport

4. **Core is the source of truth:** All 5 organs are in `core/organs/`, not in `codebase/` (which is archived)

5. **Unified pipeline:** The main entry is `core.pipeline.forge()`, not individual organ calls

6. **13 floors enforced:** Every query goes through all 13 constitutional floors automatically

7. **Tests exist:** Run `pytest core/tests/` to verify integrity

8. **Documentation is current:** This v60 documentation supersedes any v53 or earlier docs

---

## File Structure Reference

```
arifOS/
├── aaa_mcp/                  # MCP server package
│   ├── server.py             # 13 tool definitions
│   ├── core/                 # Engine adapters
│   │   ├── engine_adapters.py
│   │   └── constitutional_decorator.py
│   ├── infrastructure/       # Monitoring
│   │   └── monitoring.py
│   └── README.md             # Quick start
│
├── core/                     # 5-organ kernel
│   ├── organs/               # _0_init to _4_vault
│   ├── shared/               # Physics primitives
│   ├── pipeline.py           # Unified forge()
│   └── tests/                # 64 tests
│
├── scripts/                  # Deployment tools
│   ├── deploy_mcp.py         # Quick validation
│   ├── deploy_production.py  # Full deployment
│   └── start_server.py       # Entry point
│
├── docs/                     # Documentation
│   ├── MCP_DEPLOYMENT_GUIDE_V60.md    # ← START HERE
│   ├── MCP_CLIENT_CONFIGURATIONS.md   # Client configs
│   ├── RAILWAY_DEPLOYMENT.md          # Railway guide
│   └── INDEX_MCP_V60.md               # This file
│
├── Dockerfile                # Container image
├── railway.toml              # Railway config
├── railway.template.json     # Railway template
├── .env.production           # Env template
└── pyproject.toml            # Package config
```

---

## Quick Commands

```bash
# Validate deployment readiness
python scripts/deploy_mcp.py --mode validate

# Run locally (stdio)
python -m aaa_mcp

# Run locally (SSE)
python -m aaa_mcp sse

# Test health
curl http://localhost:8080/health

# Run tests
pytest core/tests/ -v

# Deploy to Railway
railway up

# Build Docker
docker build -t arifos-mcp:v60 .
```

---

## Version History

### v60.0-FORGE (Current)
- Unified 5-organ kernel
- `core.pipeline.forge()` entrypoint
- 64 test suite
- Production deployment tools
- Archived legacy codebase

### v55.5-HARDENED (Previous)
- Hybrid proxy architecture
- Codebase + Monolith layers
- Now superseded by v60

### v53.1.0-CODEBASE (Legacy)
- Microservices architecture
- Fully superseded

---

## Support

- **Full Guide:** [`MCP_DEPLOYMENT_GUIDE_V60.md`](MCP_DEPLOYMENT_GUIDE_V60.md)
- **Repository:** https://github.com/ariffazil/arifOS
- **Documentation:** https://arifos.arif-fazil.com
- **Health:** https://aaamcp.arif-fazil.com/health

---

**DITEMPA BUKAN DIBERI** 💎🔥🧠

*This documentation is current as of v60.0-FORGE. Always check version compatibility.*
