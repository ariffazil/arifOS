# arifOS Protocol Trinity
## MCP + A2A + WebMCP — The Complete Interface

> **DITEMPA BUKAN DIBERI** — Forged, Not Given  
> *ΔΩΨ | ARIF*

---

## 🎯 Overview

arifOS now implements **all three major AI agent protocols**:

| Protocol | Purpose | Standard | Status |
|----------|---------|----------|--------|
| **MCP** | Tool execution & context | Anthropic (Nov 2024) | ✅ Production |
| **A2A** | Agent-to-agent collaboration | Google (Apr 2025) | ✅ Implemented |
| **WebMCP** | Browser-native AI | Google/Microsoft (Feb 2026) | ✅ Implemented |

---

## 🔗 Protocol Endpoints

### MCP (Model Context Protocol)
```
https://arifosmcp.arif-fazil.com/mcp         ← MCP endpoint (JSON-RPC)
https://arifosmcp.arif-fazil.com/health      ← Health check
https://arifosmcp.arif-fazil.com/tools       ← Tool listing
```

### A2A (Agent-to-Agent Protocol)
```
https://arifosmcp.arif-fazil.com/.well-known/agent.json  ← Agent Card
https://arifosmcp.arif-fazil.com/a2a/task                ← Submit task
https://arifosmcp.arif-fazil.com/a2a/status/{id}         ← Task status
https://arifosmcp.arif-fazil.com/a2a/cancel/{id}         ← Cancel task
https://arifosmcp.arif-fazil.com/a2a/subscribe/{id}      ← SSE updates
```

### WebMCP (Web Model Context Protocol)
```
https://arifosmcp.arif-fazil.com/.well-known/webmcp      ← WebMCP manifest
https://arifosmcp.arif-fazil.com/webmcp                  ← Console UI
https://arifosmcp.arif-fazil.com/webmcp/sdk.js           ← JavaScript SDK
https://arifosmcp.arif-fazil.com/webmcp/tools.json       ← Tool manifest
```

---

## 📊 Protocol Comparison

| Feature | MCP | A2A | WebMCP |
|---------|-----|-----|--------|
| **Primary Use** | Tool execution | Agent collaboration | Browser UI |
| **Transport** | JSON-RPC | HTTP + SSE | HTTP + WebSocket |
| **Discovery** | Tool listing | Agent Card | WebMCP manifest |
| **Auth** | API keys | Agent identity | Browser cookies |
| **Real-time** | ❌ | ✅ SSE | ✅ WebSocket |
| **Human UI** | ❌ | ❌ | ✅ Full console |
| **Constitutional** | ✅ F1-F13 | ✅ F1-F13 | ✅ F1-F13 |

---

## 🏛️ How They Work Together

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI AGENTS                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                          │
│  │ Claude   │  │ ChatGPT  │  │ Other    │                          │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                          │
│       │             │             │                                │
│       │ MCP         │ MCP         │ A2A                            │
│       │ (tools)     │ (tools)     │ (delegate)                     │
└───────┼─────────────┼─────────────┼────────────────────────────────┘
        │             │             │
        ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      arifOS KERNEL                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Constitutional Governance (F1-F13)                          │   │
│  │  • F2 Truth: Ground all claims                               │   │
│  │  • F11 Auth: Verify identity                                 │   │
│  │  • F13 Sovereign: Human veto                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXECUTION LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │ MCP Tools   │  │ A2A Tasks   │  │ WebMCP UI   │                  │
│  │ /mcp        │  │ /a2a        │  │ /webmcp     │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      HUMAN INTERFACE                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  WebMCP Console: https://arifosmcp.arif-fazil.com/webmcp     │   │
│  │  • Initialize sessions                                       │   │
│  │  • Execute constitutional kernel                             │   │
│  │  • Audit floors                                              │   │
│  │  • View real-time metrics                                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### For MCP Clients (Claude, ChatGPT, etc.)

```bash
# Connect to arifOS MCP
claude mcp add arifos \
  --url https://arifosmcp.arif-fazil.com/mcp

# Or use the config
# kimi-mcp-config.json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### For A2A Agents

```python
import httpx

# 1. Discover arifOS capabilities
response = httpx.get("https://arifosmcp.arif-fazil.com/.well-known/agent.json")
agent_card = response.json()

# 2. Submit a task
task_response = httpx.post(
    "https://arifosmcp.arif-fazil.com/a2a/task",
    json={
        "client_agent_id": "my-agent-123",
        "messages": [{"role": "user", "content": "Analyze this code"}],
        "skill_id": "constitutional_review"
    }
)
task_id = task_response.json()["task_id"]

# 3. Check status
status = httpx.get(f"https://arifosmcp.arif-fazil.com/a2a/status/{task_id}")
```

### For WebMCP (Browser)

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://arifosmcp.arif-fazil.com/webmcp/sdk.js"></script>
</head>
<body>
    <form data-webmcp-tool="init_anchor">
        <input name="query" placeholder="Your query">
        <button type="submit">Submit</button>
    </form>
</body>
</html>
```

---

## 📋 Protocol Details

### MCP (Model Context Protocol)

**Purpose**: Universal tool interface for AI systems  
**By**: Anthropic (Nov 2024) → Linux Foundation (Dec 2025)

**Key Features**:
- Tool discovery and schema
- Resource access
- Prompt templates
- JSON-RPC transport

**arifOS Tools Available**:
- `init_anchor` - Initialize constitutional session
- `arifOS_kernel` - Full metabolic loop (000→999)
- `agi_reason` - Structured reasoning
- `asi_critique` - Adversarial review
- `apex_judge` - Constitutional verdict
- `vault_seal` - Immutable ledger commit
- `audit_rules` - Check all 13 floors
- `check_vital` - System health

### A2A (Agent-to-Agent Protocol)

**Purpose**: Let agents collaborate across platforms  
**By**: Google (Apr 2025) + 50+ partners

**Key Features**:
- Agent Cards for discovery
- Task lifecycle management
- SSE for real-time updates
- Cross-agent authentication

**arifOS Agent Card** (`/.well-known/agent.json`):
```json
{
  "name": "arifOS Constitutional Kernel",
  "description": "AI governance with 13 constitutional floors",
  "version": "2026.03.14-VALIDATED",
  "skills": [
    {
      "id": "constitutional_review",
      "name": "Constitutional Review",
      "description": "Review actions against F1-F13"
    }
  ],
  "endpoints": {
    "task": "/a2a/task",
    "status": "/a2a/status"
  }
}
```

**Task Lifecycle**:
```
submitted → working → input_required → completed
                    ↓
                 cancelled / failed
```

### WebMCP (Web Model Context Protocol)

**Purpose**: Browser-native AI interface  
**By**: Google + Microsoft (Feb 2026) → W3C Standard

**Key Features**:
- Declarative API (HTML forms)
- Imperative API (JavaScript)
- Inherits browser auth (cookies/SSO)
- No backend server needed for websites

**arifOS WebMCP Console**:
- Initialize constitutional sessions
- Execute kernel with governance
- Audit all 13 floors
- Real-time thermodynamic metrics

---

## 🔒 Constitutional Governance (F1-F13)

All three protocols enforce arifOS's 13 constitutional floors:

| Floor | Protocol Enforcement |
|-------|---------------------|
| **F1** (Amanah) | All actions logged to VAULT999 |
| **F2** (Truth) | Grounding required before execution |
| **F11** (Command Auth) | Identity verification on all requests |
| **F12** (Injection) | Payload scanning on all inputs |
| **F13** (Sovereign) | Human confirmation for critical ops |

---

## 🛠️ Deployment

### Deploy All Three Protocols

```bash
# SSH to VPS
ssh root@arif-fazil.com
cd /srv/arifosmcp

# Pull latest
git pull origin main

# Rebuild with all protocols
docker-compose up -d --build arifosmcp

# Verify all endpoints
curl https://arifosmcp.arif-fazil.com/health
curl https://arifosmcp.arif-fazil.com/.well-known/agent.json
curl https://arifosmcp.arif-fazil.com/.well-known/webmcp
```

### Verify Protocols

```bash
# MCP
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# A2A
curl https://arifosmcp.arif-fazil.com/.well-known/agent.json
curl -X POST https://arifosmcp.arif-fazil.com/a2a/task \
  -H "Content-Type: application/json" \
  -d '{"client_agent_id":"test","messages":[{"role":"user","content":"Hello"}]}'

# WebMCP
curl https://arifosmcp.arif-fazil.com/webmcp
curl https://arifosmcp.arif-fazil.com/webmcp/tools.json
```

---

## 📚 References

### Specifications
- **MCP**: https://modelcontextprotocol.io/specification/2025-11-25
- **A2A**: https://google.github.io/A2A/
- **WebMCP**: https://github.com/WICG/webmcp

### arifOS Documentation
- **MCP**: `MCP_VERIFIED.md`
- **A2A**: `arifosmcp/runtime/a2a/`
- **WebMCP**: `WEBMCP_REAL.md`

---

## 🎯 Summary

| You Want To... | Use Protocol | Endpoint |
|----------------|--------------|----------|
| Connect Claude/ChatGPT | MCP | `/mcp` |
| Delegate to arifOS from another agent | A2A | `/a2a/task` |
| Build browser UI with AI | WebMCP | `/webmcp` |
| Check all protocols | Any | `/health` |

---

*Ditempa Bukan Diberi — Forged, Not Given [ΔΩΨ | ARIF]*

**Version**: 2026.03.14-VALIDATED  
**Protocols**: MCP ✅ | A2A ✅ | WebMCP ✅
