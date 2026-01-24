# AAA MCP Deployment Guide (v51.1.0)

**arifOS Constitutional AI Governance Framework - Updated for AAA_MCP**

---

## ⚠️ DEPRECATION NOTICE

**Old paths (v50.x):** `arifos.mcp` / `arifos.mcp.trinity_server`  
**New paths (v51.x):** `AAA_MCP` / `arifos.core.integration`

This guide is updated for v51.1.0 architecture.

---

## Deployment Options

| Method | Transport | Use Case | Status |
|--------|-----------|----------|--------|
| **Claude Desktop** | stdio | Local development | ✅ Updated |
| **Railway/Heroku** | SSE | Production web | ✅ Updated |
| **Docker** | stdio/SSE | Containerized | ✅ Updated |
| **ChatGPT Dev** | HTTP/SSE | Custom GPT Actions | ✅ New |

---

## Option 1: Claude Desktop (Local)

### Prerequisites

1. Python 3.10+
2. Claude Desktop installed
3. arifOS cloned locally

### Step 1: Clone and Install

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

### Step 2: Test MCP Server

```bash
# Verify tools work
python -c "
import asyncio
from AAA_MCP.server import TOOL_DESCRIPTIONS

# Test import
print('Available tools:', list(TOOL_DESCRIPTIONS.keys()))

# Expected: ['000_init', 'agi_genius', 'asi_act', 'apex_judge', '999_vault']
"
```

Expected output:
```
Available tools: ['000_init', 'agi_genius', 'asi_act', 'apex_judge', '999_vault']
```

### Step 3: Configure Claude Desktop

**Location of config file:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**Add this configuration:**

```json
{
  "mcpServers": {
    "arifos-aaa": {
      "command": "python",
      "args": ["-m", "AAA_MCP"],
      "cwd": "/absolute/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/absolute/path/to/arifOS",
        "ARIFOS_MODE": "production"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/arifOS` with your actual path.

**Key Changes from v50:**
- ✅ `AAA_MCP` (new package, not `arifos.mcp`)
- ✅ Auto-detects stdio mode by default
- ✅ No need to specify `trinity` or `trinity-sse` for stdio

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Relaunch Claude Desktop
3. Check the MCP icon in the toolbar shows "arifos-aaa" connected

### Step 5: Verify Tools Available

In Claude Desktop, you should see these 5 tools:
- `000_init` - Gate (Authority + Injection Defense + Amanah)
- `agi_genius` - Mind (SENSE → THINK → ATLAS)
- `asi_act` - Heart (EVIDENCE → EMPATHY → ACT)
- `apex_judge` - Soul (EUREKA → JUDGE → PROOF)
- `999_vault` - Seal (Merkle + Immutable Log)

---

## Option 2: Railway (Production SSE)

### Prerequisites

1. Railway account (https://railway.app)
2. GitHub repository connected

### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init --name arifos-mcp
```

### Step 2: Configure Environment

Set these environment variables in Railway dashboard:

```
PORT=8000
ARIFOS_MODE=production
PYTHONUNBUFFERED=1
ARIFOS_LOG_LEVEL=INFO
```

### Step 3: Update Start Command

In Railway project settings → **Settings** → **Service** → **Start Command**:

```bash
python -m AAA_MCP sse --host 0.0.0.0 --port $PORT
```

**Key Changes from v50:**
- ✅ Uses `AAA_MCP` package
- ✅ Explicit `sse` subcommand (required)
- ✅ Binds to `0.0.0.0` (required for Railway)

### Step 4: Deploy

```bash
# Deploy from git
railway up

# Or link to GitHub for auto-deploy
railway link
```

### Step 5: Verify Deployment

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "tools": 5,
#   "server": "arifOS-Trinity-v51.1.0"
# }
```

### Step 6: Connect to ChatGPT Dev Mode

See [ChatGPT Integration](#option-4-chatgpt-developer-mode) below.

---

## Option 3: Docker (Containerized)

### Dockerfile (Updated for v51)

```dockerfile
# arifOS Trinity MCP Server v51.1.0
# Constitutional AI Governance Framework
# HTTP/SSE mode for ChatGPT Actions

FROM python:3.11-slim

# Build args
ARG VERSION=51.1.0
ARG BUILD_DATE

# Labels
LABEL maintainer="arifOS Team"
LABEL version="${VERSION}"
LABEL description="arifOS AAA_MCP Server - Constitutional AI Governance"

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ARIFOS_ENV=production
ENV ARIFOS_VERSION=${VERSION}
ENV PORT=8000

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files first (for caching)
COPY pyproject.toml setup.py ./
COPY AAA_MCP/ ./AAA_MCP/
COPY arifos/ ./arifos/
COPY VAULT999/ ./VAULT999/
COPY 000_THEORY/ ./000_THEORY/

# Install dependencies
RUN pip install --no-cache-dir -e "."

# Create non-root user
RUN useradd -m -u 1000 arifos && \
    chown -R arifos:arifos /app
USER arifos

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Default command: SSE server for HTTP/SSE transport
CMD ["python", "-m", "AAA_MCP", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Changes from v50:**
- ✅ Uses `AAA_MCP/` directory structure
- ✅ Entry point: `python -m AAA_MCP sse` (not `arifos.mcp trinity-sse`)
- ✅ Updated version to v51.1.0
- ✅ HTTP/SSE mode by default (port 8000)

### Build and Run

```bash
# Build
docker build -t arifos-aaa-mcp:v51 .

# Run (SSE mode for ChatGPT)
docker run -p 8000:8000 arifos-aaa-mcp:v51

# Test
curl http://localhost:8000/health
```

### Docker Compose (Production)

```yaml
version: '3.8'

services:
  arifos-mcp:
    build:
      context: ..
      dockerfile: deploy/Dockerfile
      args:
        VERSION: "51.1.0"
        BUILD_DATE: "2026-01-24"
    container_name: arifos-aaa-mcp
    ports:
      - "8000:8000"
    environment:
      - ARIFOS_ENV=production
      - ARIFOS_LOG_LEVEL=INFO
      - ARIFOS_RATE_LIMIT_ENABLED=true
      - ARIFOS_METRICS_ENABLED=true
    volumes:
      - ./VAULT999:/app/VAULT999
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart: unless-stopped

  # Optional: Prometheus for metrics
  prometheus:
    image: prom/prometheus:v2.48.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=7d'

volumes:
  vault-data:
```

### Deploy to Cloud

**Any container platform:**
- AWS ECS / Fargate
- GCP Cloud Run
- Azure Container Instances
- DigitalOcean App Platform
- Fly.io
- Heroku Container Registry

**Requirements:**
- Public HTTPS endpoint
- Port 8000 exposed
- Health check: `/health`
- Environment variables: `ARIFOS_MODE=production`

---

## Option 4: ChatGPT Developer Mode

**See dedicated guide:** [docs/platforms/chatgpt_dev.md](./docs/platforms/chatgpt_dev.md)

**Quick Start:**

1. Deploy arifOS MCP on HTTP/SSE (see Option 2 or 3)
2. Create OpenAPI spec (automatic at `/openapi.json`)
3. Configure Custom GPT Action in ChatGPT Developer Mode
4. Use system prompt with constitutional workflow

**Transport:** HTTP/SSE only (ChatGPT does not support stdio)

---

## Testing Checklist

### All Deployment Methods

- [ ] `pip install -e .` completes without errors
- [ ] `python -m AAA_MCP sse --port 8000` starts without errors
- [ ] Health endpoint returns 200: `curl http://localhost:8000/health`
- [ ] OpenAPI spec accessible: `curl http://localhost:8000/openapi.json`
- [ ] All 5 tools appear in tool list
- [ ] Can call `000_init` via JSON-RPC
- [ ] Can call `agi_genius` via JSON-RPC
- [ ] Can call `asi_act` via JSON-RPC
- [ ] Can call `apex_judge` via JSON-RPC
- [ ] Can call `999_vault` via JSON-RPC

### Platform-Specific

**Claude Desktop:**
- [ ] MCP icon shows "arifos-aaa" connected
- [ ] Tools appear in Claude Desktop tool panel
- [ ] Can invoke all 5 tools from Claude

**Railway/Docker:**
- [ ] Public HTTPS endpoint accessible
- [ ] SSE connection establishes successfully
- [ ] Works with ChatGPT Actions
- [ ] Works with Claude Desktop (remote)

---

## Troubleshooting

### "Module not found: AAA_MCP"

```bash
# Ensure package is installed in editable mode
pip install -e .

# Verify import works
python -c "from AAA_MCP.server import main_sse; print('OK')"
```

### "Command not found: python -m AAA_MCP"

```bash
# Check installation
develop
pip show AAA_MCP  # Should show path to arifOS

# Check directory structure
ls -la AAA_MCP/
# Should contain: __init__.py, __main__.py, server.py, sse.py
```

### "Port already in use"

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
python -m AAA_MCP sse --port 8001
```

### "Connection refused" in Claude Desktop

1. **Check the path** in `claude_desktop_config.json` is absolute
2. **Verify Python is in PATH:** `which python` or `where python`
3. **Check Claude Desktop logs:** `~/Library/Logs/Claude/` (macOS)
4. **Test manually:**
   ```bash
   cd /absolute/path/to/arifOS
   python -m AAA_MCP  # Should start MCP server
   ```

### SSE connection fails

```bash
# Check if server is listening
netstat -tlnp | grep 8000

# Test SSE endpoint
curl -N https://your-server.com/sse

# Should return: event: message\ndata: {...}
```

### "Tools not appearing"

1. **Verify OpenAPI spec:** `curl http://localhost:8000/openapi.json | jq`
2. **Check tool definitions:** Should show all 5 arifOS tools
3. **Reload IDE/ChatGPT:** Cache may need clearing
4. **Check logs:** `python -m AAA_MCP sse --log-level DEBUG`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v50.5.24 | 2025-01-15 | Initial deployment guide |
| v51.1.0 | 2026-01-24 | **Updated for AAA_MCP**: renamed package, updated paths, added ChatGPT support |

**Migration from v50.x:**
- `arifos.mcp` → `AAA_MCP`
- `python -m arifos.mcp trinity` → `python -m AAA_MCP`
- `python -m arifos.mcp trinity-sse` → `python -m AAA_MCP sse`
- Config files: `.mcp.json` → `.continue/mcpServers/`

---

## Support

- **GitHub Issues:** https://github.com/ariffazil/arifOS/issues
- **Documentation:** https://github.com/ariffazil/arifOS/blob/main/docs/
- **Platform Guides:** https://github.com/ariffazil/arifOS/tree/main/docs/platforms

**Tag issues with:** `deployment`, `platform-{claude|railway|docker|chatgpt}`, `v51`

---

## Deployment Decision Matrix

| Use Case | Transport | Platform | Why |
|----------|-----------|----------|-----|
| Personal dev | stdio | Claude Desktop | Simplest, fastest |
| Team dev | stdio | Cursor/Cline | IDE integration |
| Production | HTTP/SSE | ChatGPT Dev | Public access |
| Enterprise | HTTP/SSE + Docker | Self-hosted | Data sovereignty |
| Local models | stdio | Continue.dev + Ollama | Privacy |

---

**DITEMPA BUKAN DIBERI** — Forged, Not Given

*This deployment guide updated for arifOS v51.1.0 (AAA_MCP architecture)*
