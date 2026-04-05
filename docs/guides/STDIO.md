# 🔌 arifOS STDIO Transport Guide

> Connect arifOS to Claude Desktop, Cursor, Gemini CLI, VS Code, and any MCP-compatible client via STDIO.

---

## Overview

arifOS supports **three transport modes**:

| Transport | Use Case | URL/Command |
|-----------|----------|-------------|
| **STDIO** | Local AI assistants (Claude, Cursor, Gemini) | `python stdio_server.py` |
| **HTTP** | Web clients, mobile apps, third-party integrations | `http://localhost:8080/mcp` |
| **SSE** | Server-sent events for streaming | `http://localhost:8080/sse` |

**STDIO** is the simplest for local development and Claude Desktop integration.

---

## Quick Start

### 1. Verify STDIO Works

```bash
cd /root/arifOS

# Run in stdio mode
python stdio_server.py

# Or use the CLI
arifos stdio
```

You should see:
```
🔥 arifOS STDIO Server starting...
   Mode: Local (minimal)
   Transport: STDIO
   Floors: F1-F13 (constitutional governance enabled)
```

### 2. Test with FastMCP CLI

```bash
# List tools via stdio
fastmcp list stdio_server.py

# Call a tool
fastmcp call stdio_server.py init_anchor actor_id=test

# Or use the mcp.json
fastmcp list mcp.json
```

---

## Client Configurations

### Claude Desktop

**Config file:** `~/.config/claude/mcp.json` (macOS/Linux) or `%APPDATA%/Claude/mcp.json` (Windows)

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["/root/arifOS/stdio_server.py"],
      "env": {
        "ARIFOS_DEPLOYMENT": "local"
      }
    }
  }
}
```

**Quick install:**
```bash
# Copy config to Claude
mkdir -p ~/.config/claude
cp /root/arifOS/.claude/mcp.json ~/.config/claude/mcp.json

# Restart Claude Desktop
```

---

### Cursor IDE

**Config file:** `.cursor/mcp.json` in your project or `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "arifOS": {
      "command": "python",
      "args": ["/root/arifOS/stdio_server.py"],
      "description": "arifOS Constitutional AI Governance"
    }
  }
}
```

**Quick install:**
```bash
# Project-local config
cp /root/arifOS/.cursor/mcp.json /your/project/.cursor/mcp.json

# Or global config
mkdir -p ~/.cursor
cp /root/arifOS/.cursor/mcp.json ~/.cursor/mcp.json
```

Restart Cursor after adding the config.

---

### Gemini CLI

**Config file:** `~/.gemini/settings.json`

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

**Quick install:**
```bash
mkdir -p ~/.gemini
cp /root/arifOS/.gemini/settings.json ~/.gemini/settings.json
```

---

### VS Code + Copilot

Use the **MCP Server** extension and add to `.vscode/settings.json`:

```json
{
  "mcp.servers": {
    "arifOS": {
      "type": "stdio",
      "command": "python",
      "args": ["stdio_server.py"],
      "cwd": "/root/arifOS"
    }
  }
}
```

---

## Available Tools in STDIO Mode

When running in STDIO mode, arifOS exposes the **11 Mega-Tools**:

| Tool | Description | Availability |
|------|-------------|--------------|
| `init_anchor` | 000_INIT: Session initialization | ✅ STDIO |
| `arifOS_kernel` | 444_ROUTER: Metabolic orchestration | ✅ STDIO |
| `apex_soul` | 888_JUDGE: Constitutional enforcement | ✅ STDIO |
| `vault_ledger` | 999_VAULT: Immutable audit trail | ✅ STDIO |
| `agi_mind` | 333_MIND: Reasoning & synthesis | ✅ STDIO |
| `asi_heart` | 666_HEART: Safety & critique | ✅ STDIO |
| `engineering_memory` | 555_MEMORY: Vector memory & RAG | ✅ STDIO |
| `physics_reality` | 111_SENSE: Web search & grounding | ✅ STDIO |
| `math_estimator` | 777_OPS: Thermodynamic calculations | ✅ STDIO |
| `code_engine` | 222_EVAL: Code execution | ✅ STDIO |
| `architect_registry` | 000_INIT: Tool discovery | ✅ STDIO |

**Note:** Some tools (like `code_engine`) may request confirmation before execution.

---

## How It Works

```
┌─────────────────┐         ┌──────────────────┐
│  Claude Desktop │◄───────►│  arifOS STDIO    │
│  / Cursor / etc │  JSON   │  Server          │
└─────────────────┘  RPC    └──────────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  11 Tools    │
                        │  F1-F13 Gov  │
                        └──────────────┘
```

1. Client (Claude) spawns `python stdio_server.py` as subprocess
2. Communication happens via stdin/stdout (JSON-RPC)
3. arifOS executes tools and returns results
4. Client displays results to user

---

## Transport Comparison

| Feature | STDIO | HTTP | SSE |
|---------|-------|------|-----|
| **Use Case** | Local AI assistants | Web/mobile clients | Real-time streaming |
| **Setup** | One command | Server deployment | Server deployment |
| **Security** | Process isolation | TLS + auth | TLS + auth |
| **State** | Session per process | Stateless | Connection-based |
| **Best For** | Desktop tools | Production APIs | Live dashboards |

---

## Advanced: Custom STDIO Server

Create your own minimal arifOS server:

```python
# my_arifos_stdio.py
import os
os.environ["ARIFOS_MINIMAL_STDIO"] = "1"

from arifosmcp.runtime.server import create_aaa_mcp_server

mcp = create_aaa_mcp_server()

# Add custom tool
@mcp.tool
def my_custom_tool(query: str) -> str:
    """My custom tool with constitutional governance."""
    return f"Processed: {query}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

---

## Troubleshooting

### "Module not found"
```bash
# Install arifosmcp
pip install -e /root/arifOS

# Or set PYTHONPATH
export PYTHONPATH=/root/arifOS:$PYTHONPATH
```

### "Permission denied"
```bash
# Make stdio_server.py executable
chmod +x /root/arifOS/stdio_server.py
```

### Claude not showing tools
1. Check config path: `~/.config/claude/mcp.json`
2. Verify JSON syntax: `cat ~/.config/claude/mcp.json | python -m json.tool`
3. Restart Claude Desktop completely
4. Check logs: `~/.config/claude/logs/`

### Tools not responding
```bash
# Test stdio directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python stdio_server.py
```

---

## Three Deployment Modes Summary

| Mode | Command | Best For |
|------|---------|----------|
| **STDIO (Local)** | `python stdio_server.py` | Claude Desktop, Cursor, Gemini CLI |
| **HTTP (VPS)** | `docker-compose up` or `arifos http` | Production API, web clients |
| **HTTP (Horizon)** | Auto-deploy from GitHub | Public demo, serverless |

---

## Next Steps

1. ✅ Test STDIO: `python stdio_server.py`
2. ✅ Configure Claude Desktop
3. ✅ Try Cursor IDE integration
4. ✅ Compare with HTTP mode

---

**arifOS** — *Works everywhere you do* 🔥☁️💻

*Ditempa Bukan Diberi* — Forged, Not Given [ΔΩΨ | ARIF]
