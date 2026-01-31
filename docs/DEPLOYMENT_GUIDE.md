# Deployment Guide

**arifOS v53 — Railway, Docker, Claude Desktop, Cursor, Kimi**

---

## 1. Railway (Production)

arifOS is deployed on Railway with auto-deploy from GitHub.

### Auto-Deploy (Recommended)

1. Push to `main` branch on GitHub
2. Railway auto-builds from `Dockerfile` and deploys
3. Health check at `/health` validates liveness

### Configuration

**railway.toml:**
```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "codebase-mcp-sse"
healthcheckPath = "/health"
healthcheckTimeout = 120
restartPolicyType = "ON_FAILURE"
numReplicas = 1
```

### Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `PORT` | (set by Railway) | Server port |
| `ARIFOS_ENV` | `production` | Environment mode |
| `ARIFOS_VERSION` | `v53.2.7-CODEBASE-AAA7` | Version tag |
| `ARIFOS_LOG_LEVEL` | `INFO` | Log level |
| `REDIS_URL` | (Railway Redis plugin) | Session store (optional) |
| `BRAVE_API_KEY` | (your key) | For `_reality_` tool |

### Live Endpoints

| URL | Purpose |
|-----|---------|
| `https://aaamcp.arif-fazil.com/health` | Health check |
| `https://aaamcp.arif-fazil.com/mcp` | MCP protocol endpoint |
| `https://aaamcp.arif-fazil.com/dashboard` | Live telemetry |
| `https://aaamcp.arif-fazil.com/metrics/json` | JSON metrics |

---

## 2. Docker (Local/Self-Hosted)

### Build and Run

```bash
# Build
docker build -t arifos:v53 .

# Run
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e ARIFOS_ENV=production \
  arifos:v53

# Verify
curl http://localhost:8080/health
```

### Docker Compose

```yaml
version: "3.8"
services:
  arifos:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - ARIFOS_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 3. Claude Desktop (stdio)

Claude Desktop connects via stdio transport.

### claude_desktop_config.json

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS",
      "env": {
        "PYTHONPATH": "/path/to/arifOS"
      }
    }
  }
}
```

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

---

## 4. Claude Code (stdio)

### .mcp.json (project root)

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

---

## 5. Cursor (stdio)

Add to Cursor MCP settings:

```json
{
  "mcpServers": {
    "arifos": {
      "command": "python",
      "args": ["-m", "codebase.mcp"],
      "cwd": "/path/to/arifOS"
    }
  }
}
```

---

## 6. Kimi (Moonshot AI)

Kimi connects via SSE transport to the deployed server.

### Connection

```
MCP Endpoint: https://aaamcp.arif-fazil.com/mcp
Transport: SSE / Streamable HTTP
```

See `mcp/kimi/kimi_config.yaml` for adapter configuration.

---

## 7. ChatGPT / Codex (HTTP)

ChatGPT Developer Mode and OpenAI Codex connect via HTTP:

```
MCP URL: https://aaamcp.arif-fazil.com/mcp
Transport: Streamable HTTP (JSON-RPC 2.0)
```

Tools are auto-discovered via `tools/list`.

---

## Entry Points

| Command | Transport | Use Case |
|---------|-----------|----------|
| `python -m codebase.mcp` | stdio | Claude Desktop, Cursor |
| `codebase-mcp-sse` | HTTP/SSE | Railway, Docker, ChatGPT |
| `codebase-mcp` | stdio | Alternative alias |

---

## Health Check

All deployments should verify health:

```bash
curl https://aaamcp.arif-fazil.com/health
# {"status":"healthy","version":"v53.2.8-CODEBASE-AAA7","mode":"CODEBASE","transport":"streamable-http","tools":7}
```

Expected response:
- HTTP 200
- `status: "healthy"`
- `tools: 7`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: codebase` | Set `PYTHONPATH` to project root |
| Health check timeout | Ensure `/health` returns in < 1s (no external deps) |
| `ImportError: hardening` | Normal warning — legacy modules archived, engine uses hardened versions |
| Port conflict | Set `PORT` env var |
| Redis connection failed | Redis is optional; sessions fall back to in-memory |

---

*DITEMPA BUKAN DIBERI*
