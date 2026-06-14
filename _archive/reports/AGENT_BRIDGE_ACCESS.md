# AGENT BRIDGE ACCESS — All Agents, All Scaffolds

> **Canonical reference:** How every agent on `af-forge` accesses the four forged scaffolds.
> **Last updated:** 2026-06-05
> **DITEMPA BUKAN DIBERI**

---

## The Four Scaffolds

| Scaffold | What It Does | Access Methods |
|----------|--------------|----------------|
| **Capability Index** | Vector search + ranked selection over 97 MCP tools | MCP server (stdio/HTTP), Python import, CLI |
| **Playwright MCP** | Deterministic browser automation (navigate, click, type, screenshot, extract, evaluate) | MCP server (stdio), Python import |
| **NATS Agent Bridge** | Cross-agent memory bus — publish telemetry, consume learnings | Python import, CLI, NATS subject |
| **Evals Harness** | Deterministic tests for tool accuracy + constitutional compliance | pytest, CLI, systemd timer |

---

## Per-Agent Access Matrix

| Agent | MCP Support | Capability Index | Playwright | Agent Bridge | Evals |
|-------|-------------|------------------|------------|--------------|-------|
| **Kimi** | ✅ Full | ✅ MCP server | ✅ MCP server | ✅ Python import | ✅ pytest |
| **Claude** | ✅ Full | ✅ MCP server | ✅ MCP server | ✅ Python import | ✅ pytest |
| **Continue** | ✅ Full | ✅ MCP server | ✅ Already had it | ✅ Python import | ✅ pytest |
| **Copilot** | ✅ Full | ✅ MCP server | ✅ Already had it | ✅ Python import | ✅ pytest |
| **Codex** | ⚠️ Newer versions | ✅ Config ready | ✅ Config ready | ✅ Python import | ✅ pytest |
| **Aider** | ⚠️ Experimental | ✅ Python fallback | ✅ Python fallback | ✅ Python import | ✅ pytest |
| **Gemini / antigravity** | ❌ None | ✅ Python/HTTP fallback | ✅ Python/HTTP fallback | ✅ Python import | ✅ pytest |

---

## MCP Server Endpoints

### Federation Organs (existing)

| Server | URL | Transport |
|--------|-----|-----------|
| arifOS | `http://127.0.0.1:8088/mcp` | streamable-http |
| WEALTH | `http://127.0.0.1:18082/mcp` | streamable-http |
| WELL | `http://127.0.0.1:18083/mcp` | streamable-http |
| GEOX | `http://127.0.0.1:8081/mcp` | streamable-http |

### New Scaffolds

| Server | Command / URL | Transport |
|--------|---------------|-----------|
| **capability-index** | `cd /root/arifOS && PYTHONPATH=core .venv/bin/python core/capability_index/mcp_server.py` | stdio |
| **playwright-mcp** | `cd /root/playwright-mcp && /root/arifOS/.venv/bin/python server.py` | stdio |

To run capability-index as HTTP instead:
```bash
cd /root/arifOS && PYTHONPATH=core .venv/bin/python core/capability_index/mcp_server.py --port 18084
```

---

## Quick Start by Agent

### Kimi Code CLI

Config: `/root/.kimi/mcp.json`

Already connected to 7 MCP servers. Two new servers added:
- `playwright-mcp` — browser automation
- `capability-index` — contextual tool discovery

**Restart Kimi** or reload MCP servers to pick up changes.

### Claude Code

Config: `/root/.claude/settings.json`

Previously only had minimax SSE servers. Now has the full federation:
- arifOS, WEALTH, WELL, github, brave-search, meyhem
- `playwright-mcp`, `capability-index`

**Restart Claude Code** to pick up new MCP servers.

### Continue

Config: `/root/.continue/config.yaml`

Already had the richest MCP setup. Added:
- `capability-index` (stdio)

**Restart Continue** or reload config.

### Copilot (VS Code)

Config: `/root/.copilot/mcp-config.json`

Previously only had arifOS + playwright. Now added:
- WEALTH, WELL, github, brave-search, meyhem, capability-index

**Reload VS Code window** to pick up changes.

### Codex CLI

Config: `/root/.codex/mcp.json` (new file)

Created a ready-to-use MCP config with the full federation stack.
If your Codex version supports MCP, point it to this file.
If not, use the Python fallbacks below.

### Aider

Config: `/root/.aider.conf.yml`

Aider's MCP support is experimental. Use Python fallbacks:
```python
from capability_index.store import CapabilityStore
store = CapabilityStore()
results = store.search("calculate zakat", limit=5)
```

Or call via subprocess:
```bash
cd /root/arifOS && PYTHONPATH=core python3 -c "from capability_index.store import CapabilityStore; print([r.tool_name for r in CapabilityStore().search('your intent')])"
```

### Gemini / antigravity

The antigravity Go binary does not support MCP natively.
Use HTTP calls or Python subprocess to reach the scaffolds.

**Example:** Query capability index via HTTP (if running on port 18084):
```bash
curl -X POST http://localhost:18084/mcp/capability_select \
  -H "Content-Type: application/json" \
  -d '{"intent": "calculate zakat", "risk_tier": "low"}'
```

Or use Python subprocess from the antigravity agent:
```bash
cd /root/arifOS && PYTHONPATH=core python3 -c "
from capability_index.store import CapabilityStore
for r in CapabilityStore().search('calculate zakat', 3):
    print(r.tool_name, r.server)
"
```

---

## Python Fallbacks (Universal)

Every agent — even those without MCP — can import these modules directly.

### Capability Index

```python
import sys
sys.path.insert(0, "/root/arifOS/core")
from capability_index.store import CapabilityStore

store = CapabilityStore()

# Simple search
for r in store.search("analyze capital flow", limit=5):
    print(f"{r.tool_name} ({r.server}): {r.description}")

# Select with risk filtering
from capability_index.mcp_server import _rank_and_filter
# ... (see mcp_server.py for full API)
```

### Playwright (without MCP)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    text = page.inner_text("body")
    browser.close()
```

### NATS Agent Bridge

```python
import sys, asyncio
sys.path.insert(0, "/root/arifOS/core")
from agent_bridge.publisher import TelemetryPublisher
from agent_bridge.models import AgentTelemetry

async def publish():
    pub = await TelemetryPublisher.connect()
    await pub.publish(AgentTelemetry(
        agent_id="kimi",
        session_id="sess-123",
        task_hash="abc123",
        intent="refactor sandbox",
        tools_used=["arif_forge_execute"],
        outcome="SEAL",
        learnings=["NodeSandbox needs isolated-vm"],
    ))
    await pub.close()

asyncio.run(publish())
```

### Evals

```bash
cd /root/arifOS && PYTHONPATH=core python3 -m pytest evals/ -v
```

---

## NATS Subject Conventions

| Subject | Purpose | Publisher | Consumer |
|---------|---------|-----------|----------|
| `agent.memory.{agent_id}` | Agent telemetry | All agents | arifOS → L3/L5 |
| `agent.claim.{task_id}` | Task ownership claim | Router | All agents |
| `agent.results.{task_id}` | Task results | Worker agent | Router / arifOS |

---

## Verification Checklist

Run this to verify every scaffold is reachable:

```bash
# 1. Capability Index
cd /root/arifOS && PYTHONPATH=core python3 -c "from capability_index.store import CapabilityStore; print('Tools indexed:', CapabilityStore().count())"

# 2. Playwright MCP syntax
cd /root/playwright-mcp && python3 -m py_compile server.py && echo "Playwright OK"

# 3. NATS stream
nats stream info agent_memory 2>/dev/null && echo "NATS OK" || echo "NATS stream missing"

# 4. Evals
cd /root/arifOS && PYTHONPATH=core python3 -m pytest evals/ -q

# 5. All agent configs valid
python3 -m json.tool /root/.kimi/mcp.json > /dev/null && echo "Kimi config valid"
python3 -m json.tool /root/.claude/settings.json > /dev/null && echo "Claude config valid"
python3 -m json.tool /root/.copilot/mcp-config.json > /dev/null && echo "Copilot config valid"
```

---

## Troubleshooting

**Q: Agent says MCP server not found**
A: Check that the command path uses `/root/arifOS/.venv/bin/python` (the venv with qdrant-client + sentence-transformers installed).

**Q: Capability index returns empty results**
A: Re-seed: `cd /root/arifOS && PYTHONPATH=core python3 scripts/seed_capability_index.py`

**Q: NATS stream missing**
A: Re-create: `cd /root/arifOS && python3 scripts/init_agent_memory_stream.py`

**Q: Playwright browser fails to launch**
A: Install browsers: `/root/arifOS/.venv/bin/playwright install chromium`

---

## Sovereignty Note

These scaffolds are **additive and reversible**. No running service was restarted. No git commits were made. No API keys were exposed. Each agent config was surgically edited — back up your originals if you want to rollback.

**Arif's veto is absolute.** If any of these integrations conflict with your workflow, say the word and I'll revert.
