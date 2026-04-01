# arifOS MCP Connection Guide

> **DITEMPA BUKAN DIBERI** — *Intelligence is forged, not given*

---

## What is arifOS MCP?

arifOS MCP is a **constitutional AI governance server** with:
- **40 tools** for various tasks
- **13 constitutional floors** — every action passes through safety checks
- **WebMCP** — connect via HTTP URL (no local server needed)

---

## Quick Connect (WebMCP)

### Option 1: For AI Agents (Claude, GPT, etc.)

Add to your MCP config:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://arifosmcp.arif-fazil.com/mcp"
    }
  }
}
```

### Option 2: Direct API Call (Any AI or Script)

```bash
curl -s -X POST "https://arifosmcp.arif-fazil.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "init_anchor",
      "arguments": {
        "mode": "status",
        "declared_name": "YourAgentName"
      }
    },
    "id": 1
  }'
```

---

## Available Tools

### Governance
| Tool | Description |
|------|-------------|
| `init_anchor` | Start session, load constitutional context |
| `apex_judge` | Check if action passes 13 floors |
| `vault_ledger` | Record decisions permanently |

### Intelligence
| Tool | Description |
|------|-------------|
| `agi_mind` | Deep reasoning |
| `agi_reason` | First-principles thinking |
| `engineering_memory` | Store/recall semantic memory |

### Machine
| Tool | Description |
|------|-------------|
| `physics_reality` | Web search, time, grounding |
| `math_estimator` | Thermodynamic cost estimation |
| `code_engine` | Safe Python execution |
| `search_reality` | Evidence-based search |

---

## Understanding Verdicts

Every tool call returns a **verdict**:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SEAL** | ✅ Approved | Execute the action |
| **VOID** | ❌ Rejected | Blocked by constitutional floors |
| **HOLD** | ⚠️ Need more info | Request clarification |
| **SABAR** | ⏳ Wait | Retry later |

---

## Example: Full Agent Workflow

```python
import requests

MCP_URL = "https://arifosmcp.arif-fazil.com/mcp"

def call_arifos_tool(tool_name, arguments):
    response = requests.post(
        MCP_URL,
        headers={"Content-Type": "application/json"},
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
    )
    return response.json()

# 1. Start session
result = call_arifos_tool("init_anchor", {
    "mode": "status",
    "declared_name": "MyAgent"
})
print(result["verdict"])  # Should be "SEAL"

# 2. Search for info
result = call_arifos_tool("physics_reality", {
    "mode": "search",
    "query": "What is MCP protocol?"
})
print(result["data"])

# 3. Check if safe to execute
result = call_arifos_tool("apex_judge", {
    "action": "execute_code",
    "code": "print('hello')"
})
print(result["verdict"])  # SEAL or VOID
```

---

## Health Check

```bash
curl -s https://arifosmcp.arif-fazil.com/health
```

Returns:
```json
{
  "version": "2026.03.25",
  "tools_loaded": 40,
  "ml_floors": "Active",
  "status": "HEALTHY"
}
```

---

## For Humans: How to Use

1. **Via Telegram:** Message [@ariffazil_bot](https://t.me/ariffazil_bot)
2. **Via API:** Use the HTTP endpoint above
3. **Via OpenClaw:** Already integrated

Just say what you need — arifOS MCP handles the rest with constitutional governance.

---

## Summary

| Item | Value |
|------|-------|
| **Endpoint** | https://arifosmcp.arif-fazil.com/mcp |
| **Protocol** | MCP 2025-03-26 |
| **Tools** | 40 |
| **Governance** | 13 floors (F1-F13) |
| **Verdicts** | SEAL / VOID / HOLD / SABAR |

---

**Ditempa Bukan Diberi** — Forged, Not Given [ΔΩΨ | ARIF]
