# arifOS — 5 Minutes to First Governed Tool Call

arifOS is an MCP server that adds **three guarantees** to any AI tool call:
1. Every action is traced (you can audit what happened)
2. Irreversible actions require explicit acknowledgment
3. Hallucinated tool calls are flagged, not silently wrong

## Connect (30 seconds)

Add to your `claude_desktop_config.json` or MCP client:
```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://mcp.arif-fazil.com/mcp",
      "transport": "http"
    }
  }
}
```

Or run locally:
```bash
pip install arifosmcp
python -m arifosmcp.runtime.__main__
# Serving on http://localhost:8088
```

## First tool call (60 seconds)

```python
# 1. Start a session
arif_init(actor_id="your_name", mode="light")
# Returns: session_id, authority_level, next_tool

# 2. Route any intent
arif_route(intent="I want to analyze portfolio risk")
# Returns: → WEALTH organ, port 18082, tool_prefix="wealth_"

# 3. Done — you have a governed session
```

## What you gain vs. plain MCP

| Capability | Plain MCP | arifOS |
|---|---|---|
| Tool call audit trail | No | Yes (every call) |
| Irreversible action gate | No | Yes (ack required) |
| Hallucination detection | No | Yes (F9 floor) |
| Denial with remediation | Error | HOLD + fix steps |
| Cross-agent routing | Manual | arif_route |

## The 7 tools (all you need)

| Tool | When to use |
|---|---|
| `arif_init` | Start here. Always first. |
| `arif_observe` | Need external data / search |
| `arif_think` | Complex reasoning / planning |
| `arif_route` | Unsure which tool/organ to use |
| `arif_judge` | Before irreversible action |
| `arif_act` | Execute (requires prior judge SEAL) |
| `arif_seal` | Permanent record to audit log |

## Debug: "I got HOLD, now what?"

Every HOLD returns `next_safe_action`. Follow it.

```json
{
  "status": "HOLD",
  "reason": "Irreversible action without acknowledgment",
  "next_safe_action": "Set ack_irreversible=true and retry",
  "violated_laws": ["F1"]
}
```

Common HOLDs:
- `F1` — set `ack_irreversible=true`
- `F11` — call `arif_init` first
- `F13` — action requires human approval

## Latency (measured, p50/p95)

| Tool | p50 | p95 |
|---|---|---|
| arif_init (light) | ~200ms | ~400ms |
| arif_route | ~50ms | ~120ms |
| arif_think | ~800ms | ~2000ms |
| arif_judge | ~300ms | ~600ms |

*Measured on local VPS. Cloud may vary.*

## Three invariants — if these hold, everything works

1. **Every session has an actor** → `arif_init` binds it
2. **Every tool has a contract** → `contracts/tools.yaml` defines it
3. **Every response is OK or HOLD** → `_ok()` / `_hold()` enforce it

---

For deeper architecture: [AGENTS.md](AGENTS.md) | [contracts/tools.yaml](contracts/tools.yaml)
