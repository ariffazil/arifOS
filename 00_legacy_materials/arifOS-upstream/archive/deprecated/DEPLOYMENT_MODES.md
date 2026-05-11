# 🚀 arifOS Deployment Modes

> arifOS supports **three transport modes** and **three deployment targets**. Choose the right mode for your use case.

---

## 📊 Transport Modes

| Transport | Command | Use Case |
|-----------|---------|----------|
| **STDIO** | `python stdio_server.py` | Local AI assistants (Claude, Cursor, Gemini) |
| **HTTP** | `arifos http` or Docker | Web clients, APIs, production |
| **SSE** | `arifos sse` | Streaming, real-time dashboards |

---

## 🎯 Deployment Targets

| Target | Transport | URL/Command | Purpose |
|--------|-----------|-------------|---------|
| **Local Dev** | STDIO | `python stdio_server.py` | Development & testing |
| **VPS** | HTTP | `https://arifos.arif-fazil.com` | Sovereign production |
| **Horizon** | HTTP | `https://arifos.fastmcp.app` | Public/demo serverless |

---

## 🔄 The Complete Matrix

```
                    Transport
                 ┌────────┬────────┬────────┐
                 │ STDIO  │  HTTP  │  SSE   │
    ┌────────────┼────────┼────────┼────────┤
    │ Local Dev  │   ✅   │   ✅   │   ✅   │
 D  ├────────────┼────────┼────────┼────────┤
 e  │ VPS        │   ✅   │   ✅   │   ✅   │
 p  ├────────────┼────────┼────────┼────────┤
 l  │ Horizon    │   ❌   │   ✅   │   ✅   │
 o  └────────────┴────────┴────────┴────────┘
 y
```

---

## 🔥 Mode 1: STDIO (Local Assistants)

**Best for:** Claude Desktop, Cursor IDE, Gemini CLI, VS Code

```bash
# Run locally
python stdio_server.py

# Or via CLI
arifos stdio
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["/root/arifOS/stdio_server.py"]
    }
  }
}
```

**Features:**
- ✅ All 11 Mega-Tools available
- ✅ Full F1-F13 constitutional enforcement
- ✅ Local VAULT999 (SQLite/memory)
- ✅ Process isolation (secure)
- ⚡ Fastest startup

---

## 🌐 Mode 2: HTTP (Production)

**Best for:** Web clients, mobile apps, third-party integrations

```bash
# Via Docker (recommended)
docker-compose up -d

# Or directly
arifos http

# Or Python
python -c "from server import mcp; mcp.run(transport='http', port=8080)"
```

**URLs:**
- Health: `http://localhost:8080/health`
- MCP: `http://localhost:8080/mcp`
- WebMCP: `http://localhost:8080/`
- A2A: `http://localhost:8080/a2a`

**Features:**
- ✅ Protocol Trinity (MCP + A2A + WebMCP)
- ✅ Middleware stack (auth, rate limit, CORS)
- ✅ Stateless HTTP requests
- ✅ Auto-scaling with Docker

---

## 📡 Mode 3: SSE (Streaming)

**Best for:** Real-time dashboards, live updates

```bash
arifos sse
```

**Features:**
- ✅ Server-sent events
- ✅ Connection-based state
- ✅ Streaming responses
- ⚡ Lower latency for frequent updates

---

## 🏛️ Deployment Target 1: VPS (Sovereign)

**Your Hostinger VPS — Full Sovereignty**

```yaml
# docker-compose.yml
services:
  arifos:
    image: ghcr.io/ariffazil/arifos:latest
    environment:
      - ARIFOS_DEPLOYMENT=vps
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    ports:
      - "8080:8080"
```

**Characteristics:**
- 🔥 **Sovereignty**: You control the substrate
- 🔒 **Security**: Private keys never leave your hardware
- 💾 **VAULT999**: Local PostgreSQL
- 🧠 **Memory**: Local Redis/Qdrant
- 📊 **All Tools**: 11 Mega-Tools (full surface)
- 🏛️ **All Floors**: F1-F13 constitutional enforcement

**Access:**
```bash
# Direct
https://arifos.arif-fazil.com/mcp

# With FastMCP CLI
fastmcp list https://arifos.arif-fazil.com/mcp
fastmcp call https://arifos.arif-fazil.com/mcp init_anchor actor_id=arif
```

---

## ☁️ Deployment Target 2: Horizon (Public)

**Prefect Horizon — Serverless Scale**

```bash
# Auto-deploys from GitHub
# Config: fastmcp.json
{
  "entrypoint": "server.py:mcp",
  "port": 8000
}
```

**Characteristics:**
- ☁️ **Managed**: Prefect handles infrastructure
- 🌍 **Global**: Edge deployment
- 📈 **Auto-scale**: Handles viral traffic
- 🔐 **Built-in Auth**: OAuth ready
- 🛠️ **Limited Tools**: 8 public-safe tools
- 🏛️ **Core Floors**: F1, F2, F3, F5, F7, F9, F12

**Access:**
```bash
https://arifos.fastmcp.app/mcp
```

---

## 💻 Deployment Target 3: Local (Dev)

**Your Machine — Development & Testing**

```bash
# STDIO mode
python stdio_server.py

# HTTP mode
arifos http

# With auto-reload
uvicorn arifosmcp.runtime.server:app --reload
```

**Characteristics:**
- 💻 **Fast**: No network latency
- 🐛 **Debuggable**: Full stack traces
- 🔄 **Hot Reload**: Code changes apply instantly
- 💾 **SQLite**: Local file-based VAULT999
- 🧪 **All Tools**: Full 11-tool surface

---

## 🎭 Use Case Scenarios

### Scenario 1: Personal Development
```bash
# Just you, coding on your VPS
python stdio_server.py
# → Use with Claude Desktop
```

### Scenario 2: Team Production
```bash
# Deploy to VPS
docker-compose up -d
# → Team accesses https://arifos.arif-fazil.com
```

### Scenario 3: Public Demo
```bash
# Auto-deploy to Horizon
# → Public accesses https://arifos.fastmcp.app
```

### Scenario 4: Hybrid (Recommended)
```
🔥 VPS (Sovereign): Private tools, VAULT999, strict auth
   └── https://arifos.arif-fazil.com

☁️ Horizon (Public): Demo tools, public access, OAuth
   └── https://arifos.fastmcp.app

💻 Local (Dev): Fast iteration, debugging
   └── python stdio_server.py
```

---

## 🔐 Security by Mode

| Mode | Data Residency | Auth | Trust Boundary |
|------|----------------|------|----------------|
| **STDIO Local** | Your machine | Process isolation | Maximum |
| **HTTP VPS** | Your VPS | API keys + TLS | High |
| **HTTP Horizon** | Prefect cloud | OAuth + TLS | Shared |

---

## 💰 Cost by Mode

| Mode | Monthly Cost | Scaling |
|------|--------------|---------|
| **STDIO** | $0 (your hardware) | Single user |
| **VPS** | $15-25 fixed | Manual |
| **Horizon** | $0-50+ usage-based | Auto |

---

## 🚀 Quick Commands

```bash
# STDIO (local assistant)
python stdio_server.py

# HTTP (production server)
arifos http

# SSE (streaming)
arifos sse

# Docker (full stack)
docker-compose up -d

# Deploy to VPS (via GitHub Actions)
git push origin main

# Check all modes
fastmcp list stdio_server.py          # STDIO
fastmcp list http://localhost:8080/mcp # Local HTTP
fastmcp list https://arifos.arif-fazil.com/mcp  # VPS
fastmcp list https://arifos.fastmcp.app/mcp   # Horizon
```

---

## 📁 File Reference

| File | Transport | Purpose |
|------|-----------|---------|
| `stdio_server.py` | STDIO | Local assistant integration |
| `server.py` | HTTP | Production server entry point |
| `arifosmcp/runtime/server.py` | All | Core FastMCP server definition |
| `fastmcp.json` | HTTP | Horizon deployment config |
| `docker-compose.yml` | HTTP | VPS orchestration |
| `.claude/mcp.json` | STDIO | Claude Desktop config |
| `.cursor/mcp.json` | STDIO | Cursor IDE config |
| `.gemini/settings.json` | STDIO | Gemini CLI config |

---

## 🎯 Decision Tree

```
Where do you want to use arifOS?
│
├── Local AI assistant (Claude, Cursor)
│   └── Use: STDIO (stdio_server.py)
│
├── Production API (your apps)
│   └── Use: HTTP on VPS (docker-compose up)
│
├── Public demo (anyone can try)
│   └── Use: HTTP on Horizon (auto-deploy)
│
└── All of the above
    └── Use: DUAL SOVEREIGNTY (VPS + Horizon + local STDIO)
```

---

## ✅ Summary

| Question | Answer |
|----------|--------|
| **STDIO supported?** | ✅ YES — `python stdio_server.py` |
| **HTTP supported?** | ✅ YES — `arifos http` or Docker |
| **SSE supported?** | ✅ YES — `arifos sse` |
| **Claude Desktop?** | ✅ YES — via STDIO |
| **Cursor IDE?** | ✅ YES — via STDIO |
| **Gemini CLI?** | ✅ YES — via STDIO |
| **VPS deploy?** | ✅ YES — Docker Compose |
| **Horizon deploy?** | ✅ YES — Auto from GitHub |
| **All from same repo?** | ✅ YES — Single codebase |

---

**arifOS** — *Every transport, every target, one constitution* 🔥☁️💻

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
