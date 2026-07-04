# arifOS — 5 Minutes to First Governed Tool Call

arifOS is the constitutional MCP kernel for the federation. The **public MCP surface is exactly 7 verbs**:

`arif_init` → `arif_observe` → `arif_think` → `arif_route` → `arif_judge` → `arif_act` → `arif_seal`

## Connect

Add to your MCP client:

```json
{
  "mcpServers": {
    "arifos": {
      "url": "https://mcp.arif-fazil.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

Or run locally from this repo:

```bash
uv sync --all-extras
uv run python -m arifosmcp.runtime.server
# server listens on http://127.0.0.1:8088
```

## First governed flow

```python
# 1. Start a session
arif_init(mode="init", actor_id="your_name")

# 2. Gather evidence or map current reality
arif_observe(mode="search", query="portfolio risk drivers")

# 3. Reason or plan
arif_think(mode="plan", query="analyze portfolio risk")

# 4. Route if the next tool or organ is unclear
arif_route(mode="route", intent="I want to analyze portfolio risk")
```

## The public tools

| Tool | Use when |
|---|---|
| `arif_init` | Start or resume a governed session |
| `arif_observe` | Need external data, search, ingest, vitals |
| `arif_think` | Need reasoning, verification, or planning |
| `arif_route` | Unsure which governed step or organ is next |
| `arif_judge` | Need a constitutional verdict |
| `arif_act` | Need to execute an approved action |
| `arif_seal` | Need an immutable final record |

## Invariants

1. The public wire surface is **7 verbs only**.
2. `arif_act` is downstream of prior governed approval.
3. Runtime truth is the live MCP facade plus:
   - `arifosmcp/runtime/public_surface.py`
   - `arifosmcp/tool_registry.json`
   - `static/.well-known/mcp/server.json`

---

For architecture and governance, read [`README.md`](README.md) and [`AGENTS.md`](AGENTS.md).
