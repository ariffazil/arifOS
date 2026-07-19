# arifOS — 5 Minutes to First Governed Tool Call

arifOS is the constitutional MCP kernel for the federation. The **public MCP surface is 12 canonical verbs** (Spine P0 — 2026-07-10):

`arif_init` → `arif_observe` → `arif_think` → `arif_route` → `arif_bridge_connect` → `arif_critique` → `arif_memory` → `arif_judge` → `arif_forge` → `arif_compose` → `arif_seal` → `arif_verify`

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

Microsoft 365 / Teams path:

Preferred when your Teams/Copilot surface is backed by Copilot Studio MCP onboarding:

```text
Server URL: https://mcp.arif-fazil.com/mcp
Transport: streamable-http
```

Bridge scaffold fallback when direct MCP onboarding is blocked or you need an OpenAPI/REST adapter:

```bash
set ARIFOS_M365_UPSTREAM_URL=https://mcp.arif-fazil.com/mcp
uv run arifos-teams-bridge
# bridge listens on http://127.0.0.1:8091 and exposes OpenAPI/REST routes
```

Windows bootstrap for this machine:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local_agent_connectivity.ps1 -InstallDeps
```

Blessed client template:

```text
CONFIG\mcp-clients.local.json
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

# 5. Get a constitutional verdict before any action
arif_judge(actor="your_name", intent="analyze portfolio", ...)  # returns SEAL / HOLD / SABAR / VOID

# 6. Execute after SEAL
arif_forge(mode="engineer", ...)  # only after judge SEAL

# 7. Seal the result for the immutable ledger
arif_seal(mode="seal", payload="...", ack_irreversible=True)
```

## The 12 Canonical Public Tools

| # | Tool | Stage | Use When |
|---|------|-------|----------|
| 1 | `arif_init` | 000 | Start or resume a governed session |
| 2 | `arif_observe` | 111 | Need external data, search, ingest, vitals |
| 3 | `arif_think` | 333 | Need reasoning, verification, or planning |
| 4 | `arif_route` | 444 | Unsure which governed step or organ is next |
| 5 | `arif_bridge_connect` | 444-direct | Direct call to a known organ (HIGH auth) |
| 6 | `arif_critique` | 555 | Maruah / risk / ethical stress-test before irreversible action |
| 7 | `arif_memory` | 555m | Constitutional memory: recall, remember, promote |
| 8 | `arif_judge` | 888 | Need a constitutional verdict (SEAL/HOLD/SABAR/VOID) |
| 9 | `arif_forge` | 777 | Execute an approved action (requires prior SEAL) |
| 10 | `arif_compose` | reply | Format final human-facing response. Call LAST. |
| 11 | `arif_seal` | 999 | Immutable VAULT999 record |
| 12 | `arif_verify` | E1 | JITU pre-execution gate — SEAL token check for IRREVERSIBLE shell |

**Demoted / internal:** `arif_triage` → `arif_init(mode=preflight|triage)`; `arif_act` → `arif_forge`; `arif_fetch` → `arif_observe(mode=fetch)`.

## Invariants

1. The public wire surface is **12 verbs only** (Spine P0 — SATU PERMUKAAN).
2. `arif_forge` is downstream of `arif_judge` SEAL — no action skips judgment.
3. No organ self-authorizes. A-FORGE executes; arifOS judges.
4. Pass `session_token` every hop — do not re-interrogate store-only `session_id`.
5. Runtime truth is the live MCP facade plus:
   - `arifosmcp/runtime/public_surface.py`
   - `arifosmcp/tool_registry.json`
   - `static/.well-known/mcp/server.json`

---

For architecture and governance, read [`README.md`](README.md) and [`AGENTS.md`](AGENTS.md).
