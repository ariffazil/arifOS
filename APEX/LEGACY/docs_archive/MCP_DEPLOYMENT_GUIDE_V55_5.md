# arifOS MCP Deployment Guide v60.0-FORGE

**Version:** v60.0-FORGE (RUKUN AGI)  
**Architecture:** 5-Organ Constitutional Kernel  
**Status:** PRODUCTION READY  
**Motto:** *Ditempa Bukan Diberi* — Forged, Not Given  

---

## Executive Summary

This guide provides comprehensive instructions for deploying the arifOS Constitutional MCP Server to production environments. The v60 architecture features a unified 5-organ kernel (Airlock, Mind, Heart, Soul, Memory) with 13 Constitutional Floors enforcement.

| Component | Technology | Status |
|-----------|------------|--------|
| **Core Engine** | Python 3.10+ | ✅ Hardened |
| **MCP Protocol** | FastMCP 1.0+ | ✅ Active |
| **Transports** | stdio / SSE / HTTP | ✅ Multi-mode |
| **Deployment** | Railway / Docker / Local | ✅ Ready |
| **Monitoring** | Prometheus / Health | ✅ Built-in |

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Quick Start (Local)](#quick-start-local)
3. [Deployment Options](#deployment-options)
4. [Environment Configuration](#environment-configuration)
5. [Client Integration](#client-integration)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)
8. [Reference](#reference)

---

## Architecture Overview

### 5-Organ Constitutional Kernel

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AAA MCP Server                              │
│                    (Model Context Protocol)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  Airlock │→ │   Mind   │→ │  Heart   │→│   Soul   │→│ Memory │ │
│  │  (000)   │  │ (111-333)│  │ (555-666)│  │(444-888) │  │ (999)  │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│      F11            F2/F4              F1/F5              F3/F8    │
│      F12            F7/F8              F6/F9              F10/F13  │
└─────────────────────────────────────────────────────────────────────┘
                           ↓
                    core.pipeline.forge()
```

### 13 Constitutional Floors

| Floor | Name | Type | Threshold | Enforcement |
|:-----:|:-----|:----:|:----------|:------------|
| F1 | **Amanah** | HARD | Reversible | All actions auditable/undoable |
| F2 | **Truth** | HARD | τ ≥ 0.99 | Factual fidelity |
| F3 | **Consensus** | DERIVED | W₃ ≥ 0.95 | Tri-Witness (Human×AI×System) |
| F4 | **Clarity** | SOFT | ΔS ≤ 0 | Entropy reduction |
| F5 | **Peace²** | SOFT | ≥ 1.0 | Safety margins |
| F6 | **Empathy** | HARD | κᵣ ≥ 0.70 | Stakeholder protection |
| F7 | **Humility** | HARD | Ω₀ ∈ [0.03,0.05] | Uncertainty band |
| F8 | **Genius** | DERIVED | G ≥ 0.80 | G = A×P×X×E² |
| F9 | **Anti-Hantu** | SOFT | C_dark < 0.30 | No consciousness claims |
| F10 | **Ontology** | HARD | Grounded | Reality check |
| F11 | **Authority** | HARD | Valid | Command authentication |
| F12 | **Defense** | HARD | Clean | Injection scanning |
| F13 | **Sovereign** | HARD | Override | Human veto (888_HOLD) |

---

## Quick Start (Local)

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment (recommended)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# 2. Create virtual environment
python -m venv .venv

# 3. Activate (Windows)
.venv\Scripts\activate

# 4. Activate (macOS/Linux)
source .venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
pip install -e .

# 6. Verify installation
python scripts/deploy_mcp.py --mode validate
```

### Running Locally

**Option A: stdio Mode (for Claude Desktop, Kimi)**

```bash
python -m aaa_mcp
```

**Option B: SSE Mode (for networked clients)**

```bash
python -m aaa_mcp sse
# Or explicitly:
AAA_MCP_TRANSPORT=sse python -m aaa_mcp
```

**Option C: HTTP Mode (Streamable HTTP)**

```bash
python -m aaa_mcp http
```

### Test the Server

```bash
# Health check
curl http://localhost:8080/health

# Expected response:
# {"status": "healthy", "version": "60.0-FORGE", ...}
```

---

## Deployment Options

### Option 1: Railway (Recommended for Cloud)

Railway provides the easiest path to production with automatic HTTPS, scaling, and monitoring.

#### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

#### Step 2: Login & Initialize

```bash
# Login to Railway
railway login

# Navigate to project
cd arifOS

# Link to existing project or create new
railway link
# OR
railway init
```

#### Step 3: Configure Environment Variables

In Railway Dashboard or via CLI:

```bash
railway variables set PORT=8080
railway variables set HOST=0.0.0.0
railway variables set AAA_MCP_TRANSPORT=sse
railway variables set ARIFOS_CONSTITUTIONAL_MODE=AAA
railway variables set PYTHONUNBUFFERED=1

# Optional: External APIs
railway variables set BRAVE_API_KEY=your_key_here
railway variables set BROWSERBASE_API_KEY=your_key_here
```

#### Step 4: Deploy

```bash
railway up
```

#### Step 5: Verify

```bash
# Get deployment URL
railway domain

# Test health endpoint
curl https://your-app.up.railway.app/health
```

#### Step 6: Custom Domain (Optional)

1. **Cloudflare DNS:**
   ```
   Type: CNAME
   Name: mcp
   Target: your-app.up.railway.app
   Proxy: Enabled (orange cloud)
   ```

2. **Railway Settings:**
   - Dashboard → Settings → Domains
   - Add Domain: `mcp.yourdomain.com`

### Option 2: Docker

#### Build & Run

```bash
# Build image
docker build -t arifos-mcp:v60 .

# Run container
docker run -d \
  --name arifos-mcp \
  -p 8080:8080 \
  -e PORT=8080 \
  -e HOST=0.0.0.0 \
  -e AAA_MCP_TRANSPORT=sse \
  arifos-mcp:v60

# Check logs
docker logs arifos-mcp

# Health check
curl http://localhost:8080/health
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  arifos-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - HOST=0.0.0.0
      - AAA_MCP_TRANSPORT=sse
      - ARIFOS_CONSTITUTIONAL_MODE=AAA
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### Option 3: Manual Server Deployment

For bare metal or VM deployment:

```bash
# Systemd service setup
sudo tee /etc/systemd/system/arifos-mcp.service > /dev/null <<EOF
[Unit]
Description=arifOS MCP Server
After=network.target

[Service]
Type=simple
User=arifos
WorkingDirectory=/opt/arifOS
Environment=PORT=8080
Environment=HOST=0.0.0.0
Environment=AAA_MCP_TRANSPORT=sse
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/arifOS/.venv/bin/python -m aaa_mcp
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable arifos-mcp
sudo systemctl start arifos-mcp
```

---

## Environment Configuration

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | Server port |
| `HOST` | `0.0.0.0` | Bind address |
| `AAA_MCP_TRANSPORT` | `sse` | Transport mode (stdio/sse/http) |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `ARIFOS_CONSTITUTIONAL_MODE` | `AAA` (default), `SOFT`, or `HARD` |
| `BRAVE_API_KEY` | Brave Search API for reality_grounding |
| `BROWSERBASE_API_KEY` | Browserbase API for web browsing |
| `DATABASE_URL` | PostgreSQL for persistent VAULT999 |
| `REDIS_URL` | Redis for session state |
| `SECRET_KEY` | JWT signing secret |
| `LOG_LEVEL` | `info`, `debug`, `warning`, `error` |

### Production Checklist

```bash
# Copy template
cp .env.production .env

# Edit with your values
nano .env

# Required for production:
# - Set strong SECRET_KEY
# - Configure external APIs (Brave, Browserbase)
# - Set up PostgreSQL (optional but recommended)
# - Configure Redis (optional but recommended)
```

---

## Client Integration

### Kimi Configuration

**File:** `.kimi/mcp.json` (Windows: `%USERPROFILE%\.kimi\mcp.json`)

```json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "C:\\Users\\User\\arifOS\\.venv\\Scripts\\python.exe",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "C:/Users/User/arifOS",
      "env": {
        "PYTHONPATH": "C:/Users/User/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUNBUFFERED": "1"
      },
      "disabled": false,
      "alwaysAllow": [
        "init_gate",
        "trinity_forge",
        "agi_sense",
        "agi_think",
        "agi_reason",
        "asi_empathize",
        "asi_align",
        "apex_verdict",
        "vault_seal"
      ]
    }
  }
}
```

### Claude Desktop Configuration

**File:**
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "arifos-local": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    },
    "arifos-cloud": {
      "transport": "sse",
      "url": "https://mcp.yourdomain.com/sse"
    }
  }
}
```

### Cursor Configuration

**File:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

### Generic MCP Client

For any MCP-compatible client:

**stdio Mode:**
```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "env": {
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

**SSE Mode:**
```json
{
  "mcpServers": {
    "arifos": {
      "transport": "sse",
      "url": "http://localhost:8080/sse"
    }
  }
}
```

---

## Monitoring & Observability

### Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Health check (Railway-compatible) |
| `GET /metrics` | Prometheus metrics |
| `GET /stats` | JSON statistics |

### Prometheus Metrics

```bash
curl http://localhost:8080/metrics

# Output:
# arifos_executions_total{verdict="SEAL"} 42
# arifos_executions_total{verdict="VOID"} 3
# arifos_latency_ms 0.48
# arifos_entropy_delta -0.15
```

### Key Metrics to Monitor

| Metric | Alert Threshold | Meaning |
|--------|-----------------|---------|
| `latency_ms` | > 100ms | Pipeline performance |
| `void_rate` | > 10% | Constitutional violations |
| `error_rate` | > 1% | System errors |
| `entropy_delta` | > 0 | Clarity degradation |

---

## Troubleshooting

### Common Issues

#### Issue: "Module not found: core"

**Cause:** Package not installed in editable mode

**Fix:**
```bash
pip install -e .
```

#### Issue: "Port already in use"

**Fix:**
```bash
# Use different port
PORT=8000 python -m aaa_mcp sse
```

#### Issue: "Injection detected" on startup

**Cause:** Environment variables may contain suspicious patterns

**Fix:**
```bash
# Check env vars
echo $QUERY_STRING  # May trigger F12

# Unset if problematic
unset QUERY_STRING
```

#### Issue: "Core organs not available" (fallback mode)

**Cause:** Import error in core module

**Fix:**
```bash
# Test core import
python -c "from core.pipeline import forge; print('OK')"

# If error, check:
pip install -e .
python -c "import core; print(core.__file__)"
```

### Debug Mode

```bash
# Enable debug logging
LOG_LEVEL=debug python -m aaa_mcp

# Verbose validation
python scripts/deploy_mcp.py --mode validate --verbose
```

### Getting Help

1. **Check documentation:** https://arifos.arif-fazil.com
2. **Health endpoint:** https://aaamcp.arif-fazil.com/health
3. **GitHub Issues:** https://github.com/ariffazil/arifOS/issues

---

## Reference

### 13 MCP Tools

| Tool | Organ | Floors | Purpose |
|------|-------|--------|---------|
| `init_gate` | Airlock | F11, F12 | Session initialization |
| `trinity_forge` | All | F1-F13 | Unified 000-999 pipeline |
| `agi_sense` | Mind | F4, F7 | Intent classification |
| `agi_think` | Mind | F2, F4 | Hypothesis generation |
| `agi_reason` | Mind | F2, F4, F7 | Logical reasoning |
| `asi_empathize` | Heart | F5, F6 | Stakeholder analysis |
| `asi_align` | Heart | F5, F6, F9 | Ethics/policy check |
| `apex_verdict` | Soul | F3, F8, F9 | Final judgment |
| `reality_search` | Mind | F2, F10 | Web grounding |
| `vault_seal` | Memory | F1, F3 | Immutable ledger |
| `tool_router` | Meta | — | Dynamic routing |
| `vault_query` | Memory | — | Ledger retrieval |
| `truth_audit` | Meta | F2, F4 | Claim verification |

### Transport Comparison

| Transport | Use Case | Latency | Security |
|-----------|----------|---------|----------|
| **stdio** | Local agents (Claude Desktop) | Lowest | Process isolation |
| **SSE** | Networked streaming | Low | HTTPS + auth |
| **HTTP** | Stateless clients | Medium | HTTPS + auth |

### File Structure

```
arifOS/
├── aaa_mcp/              # MCP server package
│   ├── server.py         # 13 canonical tools
│   ├── core/             # Engine adapters
│   └── infrastructure/   # Monitoring
├── core/                 # 5-organ kernel
│   ├── organs/           # _0_init to _4_vault
│   ├── shared/           # Physics primitives
│   └── pipeline.py       # Unified forge()
├── scripts/              # Deployment tools
│   ├── deploy_mcp.py     # Quick validation
│   ├── deploy_production.py  # Full deployment
│   └── start_server.py   # Entry point
├── Dockerfile            # Container image
├── railway.toml          # Railway config
└── pyproject.toml        # Package config
```

---

## Changelog

### v60.0-FORGE (2026-02-09)

- **NEW:** Unified 5-organ kernel (Airlock, Mind, Heart, Soul, Memory)
- **NEW:** `core.pipeline.forge()` — single entrypoint for 000-999
- **NEW:** 64 test suite (core/tests/)
- **NEW:** Deployment validation tools
- **NEW:** Prometheus metrics endpoint
- **REFACTOR:** Archive old codebase to `archive/core_legacy/`
- **DEPRECATE:** Old hybrid proxy architecture

---

*DITEMPA BUKAN DIBERI* 💎🔥🧠

**Repository:** https://github.com/ariffazil/arifOS  
**Documentation:** https://arifos.arif-fazil.com  
**Health:** https://aaamcp.arif-fazil.com/health
