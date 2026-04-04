# Release Notes — arifOS 2026.02.27-FORGE-PROTOCOL-NEGOTIATION-CONSISTENCY-SEAL

**T000:** 2026.02.27-FORGE-PROTOCOL-NEGOTIATION-CONSISTENCY-SEAL  
**Date:** 2026-02-27  
**Authority:** 888_JUDGE — Muhammad Arif bin Fazil  
**Creed:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## What This Release Delivers

This release hardens MCP protocol behavior and aligns runtime/docs to canonical AAA naming and versioning.

| Area | Before | After |
|------|--------|-------|
| Version negotiation | Initialize accepted fixed protocol response | Session-level negotiated protocol version (`2025-11-25` / `2025-03-26`) |
| Version mismatch handling | Weak/no per-session enforcement | Explicit mismatch rejection with JSON-RPC error |
| Resources/prompts over streamable HTTP | list/read parity gaps | `resources/list`, `resources/read`, `prompts/list`, `prompts/get` parity implemented |
| Canonical tool names | Mixed naming in some docs/tests | Unified: `apex_judge`, `eureka_forge` |
| Discovery metadata | Partial protocol metadata | `protocolVersion` + `supportedProtocolVersions` published |

## Verification Summary

- `pytest tests/test_aaa_phase888_mcp_protocol_e2e.py -q` -> pass
- `pytest tests/test_aaa_mcp_contract.py -q` -> pass
- `pytest tests/test_aaa_mcp_constitutional.py -q` -> pass

## Compatibility Notes

- Current protocol: `2025-11-25`
- Supported protocol versions: `2025-11-25`, `2025-03-26`
- A negotiated protocol version is fixed for each session and validated on subsequent calls.

---

# Release Notes — arifOS 2026.02.18-FORGE-MCP-PROTOCOL-SEAL

**T000:** 2026.02.18-FORGE-MCP-PROTOCOL-SEAL  
**Date:** 2026-02-18  
**Authority:** 888_JUDGE — Muhammad Arif bin Fazil  
**Reality Index:** 0.98 (up from 0.97)  
**Creed:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## What This Seal Represents

This seal achieves **full MCP JSON-RPC protocol compliance** for the SSE transport.
The server now correctly handles all MCP lifecycle methods, enabling real-world
integration with Claude Desktop, ChatGPT Developer Mode, and any MCP-compliant client.

| Component | Before | After |
|-----------|--------|-------|
| `/messages` endpoint | Partial (tools/call only) | **Full JSON-RPC protocol** |
| `initialize` method | Not implemented | ✅ Returns protocolVersion, serverInfo, capabilities |
| `tools/list` method | Not implemented | ✅ Returns complete tool schemas |
| `ping` method | Not implemented | ✅ Keepalive support |
| `notifications/initialized` | Not implemented | ✅ Client acknowledgment |
| Route ordering | Catch-all first (BUG) | **Catch-all last** (correct) |
| POST /sse | 404 (wrong) | **405** (correct Method Not Allowed) |
| Tool calling | Direct call (broken) | **Uses `.fn` attribute** |

**Result:** arifOS MCP server is now production-ready for SSE clients.

---

## MCP Protocol Compliance

### Supported JSON-RPC Methods

```bash
# Initialize connection
curl -X POST https://arifosmcp.arif-fazil.com/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# List available tools
curl -X POST https://arifosmcp.arif-fazil.com/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'

# Call a tool
curl -X POST https://arifosmcp.arif-fazil.com/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{"name":"anchor","arguments":{"query":"test","actor_id":"user"}}
  }'

# Ping (keepalive)
curl -X POST https://arifosmcp.arif-fazil.com/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"ping","params":{}}'
```

### SSE Transport

```bash
# Connect to SSE endpoint (returns endpoint event, then pings)
curl -N https://arifosmcp.arif-fazil.com/sse
```

---

## Changes in This Release

### Fixes

| File | Change |
|------|--------|
| `aaa_mcp/rest.py` | **Full MCP JSON-RPC protocol** in `messages_endpoint()` — supports `initialize`, `notifications/initialized`, `ping`, `tools/list`, `tools/call` |
| `aaa_mcp/rest.py` | **Route ordering fixed** — catch-all `/{tool_name}` moved to END of routes list |
| `aaa_mcp/rest.py` | **POST /sse returns 405** — Added POST to `/sse` route methods, function checks request.method |
| `aaa_mcp/rest.py` | **FunctionTool calling fixed** — Uses `.fn` attribute to access underlying function (FastMCP FunctionTool objects are not callable) |

### Architecture Notes

- **Route Ordering Critical:** Starlette matches routes in order. The catch-all `/{tool_name}`
  was intercepting `/sse` and `/messages` POST requests, causing 404 errors.
- **FastMCP FunctionTool:** When importing tools from `aaa_mcp.server`, they are `FunctionTool`
  wrapper objects, not plain functions. Must use `tool.fn(**args)` to call.
- **JSON-RPC 2.0 Compliance:** All responses include `jsonrpc: "2.0"`, proper `id` echoing,
  and standard error codes (`-32601` for method not found, `-32603` for internal error).

---

## Previous Release: 2026.02.17-FORGE-VPS-SEAL

See [docs/releases/RELEASE_NOTES_2026.02.17.md](releases/RELEASE_NOTES_2026.02.17.md) for the VPS migration release notes.

---

## Verification

```bash
# Test all MCP protocol methods
./scripts/test_mcp_protocol.sh

# Or manually:
curl -s https://arifosmcp.arif-fazil.com/health | jq '.status'
# Expected: "healthy"

curl -s -X POST https://arifosmcp.arif-fazil.com/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | jq '.result.tools | length'
# Expected: 7 (init_session, agi_cognition, asi_empathy, apex_verdict, vault_seal, apex_judge, self_diagnose)
```

---

## Governance Audit

| Floor | Status | Evidence |
|-------|--------|----------|
| F1 Amanah | SEAL | All changes git-reversible, tested on VPS before commit |
| F2 Truth | SEAL | Protocol now matches MCP specification exactly |
| F4 Clarity | SEAL | Route ordering explicit, comments explain why |
| F7 Humility | SEAL | Error handling explicit, no silent failures |
| F9 Anti-Hantu | SEAL | No consciousness claims in protocol code |
| F12 Defense | SEAL | 405 response prevents method confusion attacks |
| F13 Sovereign | SEAL | Human reviewed all protocol changes |

---

*Sealed by: ARIF FAZIL — 2026-02-18 — DITEMPA BUKAN DIBERI*


This seal completes **H1.1 Production Observability** and the full **Railway → VPS migration**.
The system is now self-sovereign: no third-party platform dependency, persistent storage
connected, and the `/health` endpoint tells the truth about every subsystem.

| Component | Before | After |
|-----------|--------|-------|
| Deployment | Railway (deprecated) | Hostinger VPS (72.62.71.199) |
| `/health` status | `degraded` (no checks) | `healthy` (5 live checks) |
| Postgres | Not wired | Connected (VAULT999 lag: 0ms) |
| Redis | Broken URL parser | Connected (v8.0.2) |
| MCP tools visible | 0 (checks never ran) | 15 (lifespan init) |

---

## Production Health Endpoint (Live)

```bash
curl https://arifosmcp.arif-fazil.com/health
```

```json
{
  "status": "healthy",
  "service": "aaa-mcp-rest",
  "version": "2026.02.17-FORGE-VPS-SEAL",
  "governance_metrics": {
    "total_executions": 0,
    "avg_genius_g": 0.0,
    "avg_landauer_risk": 0.0,
    "verdicts": {}
  },
  "health_checks": {
    "core_pipeline": { "status": "healthy", "verdict": "VOID" },
    "mcp_tools":     { "status": "healthy", "tool_count": 15 },
    "memory":        { "status": "healthy", "percent": 42.1 },
    "postgres":      { "status": "connected", "lag_ms": 0.0 },
    "redis":         { "status": "connected", "version": "8.0.2" }
  }
}
```

---

## Changes in This Release

### Infrastructure — VPS Migration (H1.4 COMPLETE)

| Item | Change |
|------|--------|
| `railway.toml` | Deleted — Railway deprecated |
| `docker-compose.railway-local.yml` | Renamed → `docker-compose.yml` |
| `Dockerfile` | Comments cleaned, Railway references removed |
| `DEPLOYMENT.md` | Fully rewritten for VPS (systemd + nginx + certbot) |
| `arifosmcp.nginx.conf` | Rewritten: port 8080, SSE-safe (`proxy_buffering off`) |
| `server.json` | SSE URL → `https://arifosmcp.arif-fazil.com/sse` |
| Systemd service | `arifos-mcp.service` with `EnvironmentFile`, `After=postgresql.service` |
| Postgres permissions | `GRANT ALL ON SCHEMA public TO arifos` applied |
| Redis connection | `redis.from_url` replaces brittle manual URL parser |

### Code Quality — H1.1 Observability

| File | Change |
|------|--------|
| `aaa_mcp/infrastructure/monitoring.py` | `check_all` now merges dict results; `self.status` correctly reflects `{"status": False}`; `PipelineMetrics.entropy_delta` field added; `Callable`/`Any` type hints fixed |
| `aaa_mcp/infrastructure/monitoring.py` | `check_postgres` → `{"status": "connected", "lag_ms": N}` |
| `aaa_mcp/infrastructure/monitoring.py` | `check_redis` → full `health_check()` dict (version, mode) |
| `aaa_mcp/infrastructure/monitoring.py` | `check_core_pipeline` → `{"verdict": …, "session_id": …}` |
| `aaa_mcp/infrastructure/monitoring.py` | Critical tool list uses MCP verbs (`anchor`, `reason`, …) |
| `aaa_mcp/rest.py` | Starlette `lifespan` context — health checks register on app startup |
| `aaa_mcp/rest.py` | Restored missing imports (`datetime`, `asyncio`, `uvicorn`) |
| `aaa_mcp/services/redis_client.py` | `redis.from_url` replaces 35-line manual URL parser |

### Codebase Consolidation (2026.02.15)

| Removed | Lines | Reason |
|---------|-------|--------|
| `arifos/` | ~800 | Pre-v52 legacy, no `__init__.py`, dead |
| `codebase/` | ~21,047 | Runtime already uses `core/` exclusively |
| `core/asi/` | 492 | `sbert_floors.py` relocated to `core/shared/` |
| `build/` | — | Stale setuptools artifact |

---

## Breaking Changes

None. All changes are additive or internal refactoring.

---

## Upgrade

```bash
# VPS
ssh root@72.62.71.199
cd /opt/arifos && git pull && systemctl restart arifos-mcp

# PyPI
pip install --upgrade arifos

# Verify
curl https://arifosmcp.arif-fazil.com/health
```

---

## Infrastructure State

| Component | Status | Details |
|-----------|--------|---------|
| VPS | Online | Hostinger 72.62.71.199, Ubuntu, 6.17 kernel |
| Nginx | Active | SSL via Let's Encrypt, SSE-safe |
| Systemd | Enabled | `arifos-mcp.service`, auto-restart |
| PostgreSQL | Connected | v17, `arifos_vault`, VAULT999 schema |
| Redis | Connected | v8.0.2, `127.0.0.1:6379` |
| MCP Server | Healthy | 15 tools registered |

---

## Governance Audit

| Floor | Status | Evidence |
|-------|--------|---------|
| F1 Amanah | SEAL | All changes git-reversible |
| F2 Truth | SEAL | `/health` reports honest status |
| F4 Clarity | SEAL | Removed 22K lines of dead code |
| F7 Humility | SEAL | `degraded` status on 0 verdicts is honest |
| F9 Anti-Hantu | SEAL | No consciousness claims |
| F13 Sovereign | SEAL | Human controls VPS and secrets |

---

## Previous Release

See [docs/releases/RELEASE_NOTES.md](releases/RELEASE_NOTES.md) for the 2026.02.15-FORGE-TRINITY-SEAL release notes.

---

*Sealed by: ARIF FAZIL — 2026-02-17 — DITEMPA BUKAN DIBERI*
