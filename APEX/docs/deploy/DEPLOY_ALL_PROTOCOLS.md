# Deploy arifOS with All 3 Protocols
## MCP + A2A + WebMCP — Complete Deployment Guide

---

## ✅ What Was Implemented

### 1. MCP (Already Working)
- **Endpoint**: `/mcp`
- **Status**: ✅ Production ready
- **Tools**: 25+ constitutional tools

### 2. A2A (NEW - Real Implementation)
- **File**: `arifosmcp/runtime/a2a/`
- **Endpoints**:
  - `/.well-known/agent.json` - Agent Card discovery
  - `/a2a/task` - Submit tasks
  - `/a2a/status/{id}` - Check status
  - `/a2a/cancel/{id}` - Cancel tasks
  - `/a2a/subscribe/{id}` - SSE real-time updates
- **Features**:
  - Task lifecycle management
  - Constitutional governance on all tasks
  - Real-time SSE streaming
  - Agent Card for discovery

### 3. WebMCP (NEW - Real W3C Standard)
- **File**: `arifosmcp/runtime/webmcp/real_webmcp.py`
- **Endpoints**:
  - `/.well-known/webmcp` - WebMCP manifest
  - `/webmcp` - Console UI
  - `/webmcp/sdk.js` - JavaScript SDK
  - `/webmcp/tools.json` - Tool manifest
  - `/webmcp/execute/{tool}` - Tool execution
  - `/webmcp/ws` - WebSocket
- **Features**:
  - Declarative API (HTML forms)
  - Imperative API (JavaScript)
  - Browser-native
  - Human-friendly console

---

## 🚀 Deployment Steps

### Step 1: Commit & Push Changes

```bash
cd /c/arifosmcp

# Add all new files
git add arifosmcp/runtime/a2a/
git add arifosmcp/runtime/webmcp/real_webmcp.py
git add arifosmcp/runtime/server.py
git add docker-compose.yml
git add PROTOCOLS_TRINITY.md
git add DEPLOY_ALL_PROTOCOLS.md

# Commit
git commit -m "feat: Implement real A2A and WebMCP protocols

- Add complete A2A server (Google protocol)
  /.well-known/agent.json, /a2a/task, /a2a/status, SSE
  
- Add real WebMCP gateway (W3C standard)
  /webmcp console, SDK, WebSocket
  
- Integrate all 3 protocols into main server
  MCP + A2A + WebMCP working together
  
- All protocols enforce F1-F13 constitutional floors

Ditempa Bukan Diberi"

# Push
git push origin main
```

### Step 2: Deploy on VPS

```bash
# SSH to server
ssh root@arif-fazil.com

# Navigate to deployment directory
cd /srv/arifosmcp

# Pull latest code
git pull origin main

# Rebuild container with all protocols
docker-compose down arifosmcp
docker-compose up -d --build arifosmcp

# Check logs
docker logs -f arifosmcp_server
```

### Step 3: Verify All Protocols

```bash
# Test MCP
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Test A2A Agent Card
curl https://arifosmcp.arif-fazil.com/.well-known/agent.json | jq

# Test A2A task submission
curl -X POST https://arifosmcp.arif-fazil.com/a2a/task \
  -H "Content-Type: application/json" \
  -d '{
    "client_agent_id": "test-agent",
    "messages": [{"role": "user", "content": "Hello arifOS"}]
  }'

# Test WebMCP manifest
curl https://arifosmcp.arif-fazil.com/.well-known/webmcp

# Test WebMCP console (should return HTML)
curl https://arifosmcp.arif-fazil.com/webmcp | head -20
```

---

## 🧪 Testing Checklist

| Test | Command | Expected |
|------|---------|----------|
| **MCP Tools** | `curl -X POST /mcp -d '{"method":"tools/list"}'` | List of 25+ tools |
| **A2A Agent Card** | `curl /.well-known/agent.json` | JSON with name, skills, endpoints |
| **A2A Task** | `curl -X POST /a2a/task -d '{...}'` | Task ID returned |
| **A2A Status** | `curl /a2a/status/{task_id}` | Task state |
| **WebMCP Manifest** | `curl /.well-known/webmcp` | JSON manifest |
| **WebMCP Console** | `curl /webmcp` | HTML page |
| **WebMCP SDK** | `curl /webmcp/sdk.js` | JavaScript code |
| **Health** | `curl /health` | `{status: "healthy"}` |

---

## 🔍 Troubleshooting

### Issue: A2A endpoints return 404

**Solution**: Check Traefik routing
```bash
# Check if routes are registered
docker exec traefik_router cat /etc/traefik/dynamic/docker.json | grep a2a

# Restart traefik if needed
docker-compose restart traefik
```

### Issue: WebMCP console not loading

**Solution**: Check if real_webmcp.py is imported correctly
```bash
# Check logs
docker logs arifosmcp_server 2>&1 | grep -i "webmcp\|a2a"

# Should see:
# "✅ Real WebMCP Gateway mounted at /webmcp"
# "✅ Real A2A Server mounted at /a2a"
```

### Issue: Module not found errors

**Solution**: Ensure __init__.py files exist
```bash
# Check if a2a module is recognized
python -c "from arifosmcp.runtime.a2a import create_a2a_server; print('OK')"

# If fails, check __init__.py exists
ls -la arifosmcp/runtime/a2a/__init__.py
```

---

## 📊 Protocol Status After Deploy

```
┌─────────────────────────────────────────────────────────────┐
│                    arifOS SERVER                             │
│                    Port 8080                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MCP (Model Context Protocol)         ✅ /mcp               │
│  ├── JSON-RPC transport                                   │
│  ├── 25+ constitutional tools                              │
│  └── Tool discovery + execution                            │
│                                                              │
│  A2A (Agent-to-Agent)                 ✅ /a2a               │
│  ├── /.well-known/agent.json                              │
│  ├── Task lifecycle management                             │
│  ├── SSE real-time updates                                 │
│  └── Cross-agent collaboration                             │
│                                                              │
│  WebMCP (Web Model Context)           ✅ /webmcp            │
│  ├── Browser-native console                                │
│  ├── Declarative + Imperative APIs                         │
│  ├── JavaScript SDK                                        │
│  └── WebSocket support                                     │
│                                                              │
│  All protocols enforce:                                    │
│  ├── F1-F13 Constitutional Floors                          │
│  ├── VAULT999 audit logging                                │
│  └── Thermodynamic governance (ΔΩΨ)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Next Steps After Deploy

1. **Test MCP**: Connect Claude Desktop to `https://arifosmcp.arif-fazil.com/mcp`

2. **Test A2A**: Use the A2A test script:
   ```bash
   python scripts/test_a2a.py
   ```

3. **Test WebMCP**: Open browser to `https://arifosmcp.arif-fazil.com/webmcp`

4. **Register with A2A directory**: Submit to A2A agent registries

5. **Enable monitoring**: Set up Prometheus/Grafana for all 3 protocols

---

## 📚 Documentation

- **Full Protocol Guide**: `PROTOCOLS_TRINITY.md`
- **MCP Docs**: `MCP_VERIFIED.md`
- **WebMCP Docs**: `WEBMCP_REAL.md`
- **A2A Code**: `arifosmcp/runtime/a2a/`

---

**Ready to deploy?** Run the commands in Step 1-3 above!
