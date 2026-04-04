# arifOS MCP Platform Configuration Guide
**T000 Version:** 2026.02.15-FORGE-TRINITY-SEAL  
**Endpoint:** `https://arifosmcp.arif-fazil.com/mcp`  
**Health Check:** `https://arifosmcp.arif-fazil.com/health`

---

## 📋 Overview

arifOS provides constitutional AI governance through the **Model Context Protocol (MCP)**. This guide documents:

1. **For Humans**: How to configure arifOS with your AI assistant (Claude, ChatGPT, Cursor, etc.)
2. **For AI Agents**: How to interact with arifOS tools programmatically
3. **Current State**: What works now vs. future roadmap

> **Status Note**: The arifOS MCP server is **production-ready for the 000_INIT (anchor) stage** with full F11/F12 enforcement. Other tools (reason, integrate, etc.) are **placeholder implementations** awaiting integration with the core pipeline (see [TODO.md](./TODO.md)).

---

## 🚀 Quick Start (Human Configuration)

### 1. Choose Your Platform

| Platform | Transport | Status | Config Location |
|:---------|:---------:|:------:|:----------------|
| **Claude Desktop** | STDIO | ✅ Ready | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) |
| **OpenCode** | STDIO | ✅ Ready | `.opencode/opencode.json` or `333_APPS/L4_TOOLS/mcp-configs/opencode/` |
| **Codex CLI** | STDIO | ✅ Ready | `~/.codex/config.toml` |
| **Kimi CLI** | STDIO | ✅ Ready | Global Kimi config + project `mcp.json` |
| **Cursor** | STDIO | ⚠️ Needs Testing | `.cursor/mcp.json` |
| **ChatGPT Dev** | HTTP/SSE | 🔧 Experimental | Developer Mode UI |

### 2. Install arifOS

```bash
# Install from PyPI
pip install arifos

# Or clone from GitHub
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .
```

### 3. Configure Your Platform

#### **Claude Desktop**
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "aaa-mcp": {
      "command": "python",
      "args": ["-m", "aaa_mcp", "stdio"],
      "env": {
        "PYTHONPATH": "/path/to/arifOS",
        "ARIFOS_CONSTITUTIONAL_MODE": "AAA"
      }
    }
  }
}
```

#### **OpenCode**
Copy the pre-configured file:
```bash
cp 333_APPS/L4_TOOLS/mcp-configs/opencode/opencode.json ~/.config/opencode/
```

Or use the simplified version:
```json
// .opencode/opencode.json
{
  "mcp": {
    "aaa-mcp": {
      "type": "local",
      "command": ["python", "-m", "aaa_mcp", "stdio"],
      "cwd": ".",
      "enabled": true
    }
  }
}
```

#### **Codex CLI**
```toml
# ~/.codex/config.toml
[mcp.servers.aaa-mcp]
command = "python"
args = ["-m", "aaa_mcp", "stdio"]
cwd = "/path/to/arifOS"
```

### 4. Verify Installation

```bash
# Start server manually to test
python -m aaa_mcp stdio

# Expected output should show FastMCP banner and "✅ Container tools registered"
```

---

## 🤖 AI Agent Integration

### Tool Overview (9 Canonical Verbs)

| Tool | Stage | Floors | Status | Description |
|:-----|:------|:-------|:-------|:------------|
| **anchor** | 000 | F11, F12 | ✅ **PRODUCTION** | Init & Sense (injection guard, authority check) |
| **reason** | 222 | F2, F4, F8 | 🟡 **PLACEHOLDER** | Think & Hypothesize |
| **integrate** | 333 | F7, F10 | 🟡 **PLACEHOLDER** | Map & Ground |
| **respond** | 444 | F4, F6 | 🟡 **PLACEHOLDER** | Draft Plan |
| **validate** | 555 | F5, F6, F1 | 🟡 **PLACEHOLDER** | Safety & Impact |
| **align** | 666 | F9 | 🟡 **PLACEHOLDER** | Ethics & Constitution |
| **forge** | 777 | F2, F4, F7 | 🟡 **PLACEHOLDER** | Synthesize Solution |
| **audit** | 888 | F3, F11, F13 | 🟡 **PLACEHOLDER** | Verify & Judge |
| **seal** | 999 | F1, F3 | 🟡 **PLACEHOLDER** | Commit to Vault |

### API Usage Examples

#### **HTTP/SSE Transport (Production Cloud)**
```python
import requests
import json

# Health check
response = requests.get("https://arifosmcp.arif-fazil.com/health")
print(response.json())  # {"status": "healthy", "version": "2026.02.15-FORGE-TRINITY-SEAL", ...}

# List tools
payload = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
}
response = requests.post(
    "https://arifosmcp.arif-fazil.com/mcp",
    json=payload,
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)
print(response.json())
```

#### **anchor Tool (Production Ready)**
```python
# Example anchor call - the only fully implemented tool
payload = {
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "anchor",
        "arguments": {
            "query": "What is the capital of France?",
            "actor_id": "user-123",
            "auth_token": "optional-token",
            "mode": "conscience"
        }
    },
    "id": 2
}

# Response includes:
# - verdict: "SEAL" | "VOID" | "888_HOLD"
# - session_id: for subsequent calls
# - f12_score: injection risk (0.0-1.0)
# - query_type: factual/creative/crisis/routine
```

#### **Full 000-999 Pipeline (Via Core)**
For full constitutional pipeline, use the core module directly:
```python
from core.pipeline import forge

result = await forge(
    query="Analyze this code for security vulnerabilities",
    actor_id="security-auditor-001"
)

# result includes:
# - verdict: SEAL/PARTIAL/SABAR/VOID/888_HOLD
# - session_id
# - floors_failed: list of failed constitutional floors
# - remediation: guidance for correction
```

---

## 🔧 Configuration Details

### Environment Variables

| Variable | Default | Purpose |
|:---------|:--------|:--------|
| `ARIFOS_API_KEY` | - | Bearer token for cloud authentication |
| `PORT` | 8080 | HTTP server port |
| `HOST` | 0.0.0.0 | Bind address |
| `AAA_MCP_TRANSPORT` | stdio | `stdio`/`sse`/`http` |
| `DATABASE_URL` | - | PostgreSQL for VAULT999 ledger |
| `REDIS_URL` | - | Redis for session state |

### Transport Modes

1. **STDIO** (Default): For desktop clients
   ```bash
   python -m aaa_mcp stdio
   ```

2. **SSE**: For web clients
   ```bash
   python -m aaa_mcp sse
   # Endpoint: /mcp/sse
   ```

3. **Streamable HTTP**: For REST APIs
   ```bash
   python -m aaa_mcp http
   # Endpoint: /mcp
   ```

---

## 🛡️ Security & Authentication

### F11 Authority Enforcement
- `actor_id` is **required** (no default "user" bypass)
- Anonymous queries return `VOID` with `F11_FAIL: No actor identity`
- Telegram/WhatsApp contexts auto-populate actor_id

### F12 Injection Defense
**Critical patterns** (score ≥ 0.8): Immediate `VOID`
- "ignore previous instructions"
- "forget your instructions"
- "you are now a different AI"

**High-risk patterns** (score 0.5-0.8): Sanitization
- Role-playing prompts
- System prompt extraction attempts

### API Key Authentication (Cloud)
```bash
curl -H "Authorization: Bearer $ARIFOS_API_KEY" \
  https://arifosmcp.arif-fazil.com/health
```

---

## 📊 Monitoring & Debugging

### Health Endpoints
```bash
# Basic health
curl https://arifosmcp.arif-fazil.com/health

# Transport info
curl https://arifosmcp.arif-fazil.com/transport

# Tool schema
curl -X POST https://arifosmcp.arif-fazil.com/mcp \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Logging
Structured JSON logs available when `ARIFOS_LOGGING=structured`:
```json
{
  "timestamp": "2026-02-15T08:48:00Z",
  "level": "INFO",
  "logger": "aaa_mcp.server",
  "message": "anchor tool invoked",
  "correlation_id": "SESS-ABC123DEF456",
  "tool": "anchor",
  "floor": "F12",
  "f12_score": 0.15
}
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|:------|:---------|
| **"python: command not found"** | Use `python3` in MCP config |
| **Connection refused** | Server not running; check `python -m aaa_mcp stdio` |
| **"F11_FAIL: No actor identity"** | Provide `actor_id` parameter |
| **Tool returns placeholder** | Tool not fully implemented; use core pipeline instead |
| **SSE timeout** | Use HTTP transport or check firewall |

---

## 🔮 Roadmap & Current Limitations

### ✅ Production Ready
- **anchor tool** with full F11/F12 enforcement
- Multi-transport support (STDIO, SSE, HTTP)
- Railway cloud deployment
- PyPI package distribution

### 🟡 In Development (T000: 2026.02.15-FORGE-TRINITY-SEAL)
- Core ↔ MCP tool integration (P1 priority)
- ASI hardening with embedding models
- Test suite recovery (≥80% pass rate)
- Production observability metrics

### 🔴 Future
- Recursive AGI governance
- Institutional consensus modeling (L6)
- Cross-platform federation

---

## 📚 Resources

- **GitHub**: https://github.com/ariffazil/arifOS
- **PyPI**: https://pypi.org/project/arifos/
- **Live API**: https://arifosmcp.arif-fazil.com/health
- **Documentation**: https://arifos.arif-fazil.com/
- **Theory**: https://apex.arif-fazil.com/

---

## 🎯 Support

**For configuration issues:**
1. Check `333_APPS/L4_TOOLS/mcp-configs/` for platform examples
2. Test with `python -m aaa_mcp stdio` first
3. Review logs for constitutional floor violations

**For feature requests:**
See [TODO.md](./TODO.md) and contribute via GitHub.

> **Motto:** *DITEMPA BUKAN DIBERI* — Forged, Not Given 🔥💎🧠