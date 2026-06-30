# arifOS Agent-First Discovery Surface

> Design spec — maps the five MCP collapse triggers to live arifOS surfaces and proposes the canonical discovery API.
> DITEMPA BUKAN DIBERI.

## 1. The Five Collapse Triggers → arifOS Surfaces

| Collapse Trigger | What Forces Geometry Collapse | arifOS Surface Today | Gap |
|---|---|---|---|
| **1. Tool Contracts** | Strict schemas force valid JSON, no prose | `TOOL_MANIFEST.json` (13 canonical tools) + per-tool `inputSchema`/`outputSchema` | No single endpoint exposes schema + risk tier + floors + epistemic tag together |
| **2. Transport Reality** | Port + protocol prove external world | `:8088/mcp` (Streamable HTTP), `:8088/health` | No machine-readable transport contract (CORS, headers, session rules) |
| **3. Identity Surfaces** | Server slug/version/labels prevent hallucination | `arifos_agent_surface_map.yaml` names the kernel; `server_name` in manifest | No BLAKE3 identity hash or canonical DID endpoint |
| **4. Capability Graph** | Tool/resource/prompt lists bound decision space | `core/capability_index/mcp_server.py` (`capability_search`, `capability_select`) over 97-tool index | Not wired as an MCP resource; not reachable from the main kernel |
| **5. Governance Metadata** | Floors/verdicts/risk classes collapse unsafe paths | Every tool carries `risk_tier`, `floors`, `irreversible`; `arif_judge` renders SEAL/HOLD/VOID | Governance metadata is not exposed in a scrapeable `/.well-known` surface |

## 2. Current State (Verified 2026-06-30)

- `arifos_agent_surface_map.md` / `.yaml` — human + machine surface map (7 tools, 5 resources, agent card).
- `TOOL_MANIFEST.json` — canonical 13-tool index with risk tier, floors, irreversibility, eureka insight.
- `core/capability_index/` — Qdrant-backed 97-tool semantic index (`capability_search`, `capability_select`) using `BAAI/bge-m3`.
- `scripts/mcp_surface_truth_test.py` — 5-surface truth test comparing declared vs runtime vs wire vs session vs auth continuity.
- All 6 federation organs alive (`:8088`, `:7071`, `:3001`, `:8081`, `:18082`, `:18083`).

## 3. Discovery Surface (Zen-aligned with existing canonical surface)

### 3.1 Canonical endpoint already live

| Endpoint | Purpose | Status |
|---|---|---|
| `GET /.well-known/mcp/server.json` | **Already canonical.** Server identity, version, constitution hash, capabilities, aliases, canonical tool map | ✅ LIVE |

**Zen correction:** My initial design proposed new `/.well-known/arifos.json` and `/.well-known/mcp-surface.json` paths. That was redundant. The canonical surface already exists at `/.well-known/mcp/server.json`. Do not fragment it.

### 3.2 Gaps to close

| Gap | Why It Confuses Zero-Context Agents | Proposed Fix |
|---|---|---|
| Internal vs wire tool name mismatch | `TOOL_MANIFEST.json` uses `arif_session_init`; live wire tool is `arif_init` | Add explicit `wire_names` and `alias_map` to `server.json`; update surface truth test to validate wire names |
| No schema link in `server.json` | Agent sees tool list but cannot fetch schemas without MCP `tools/list` | Add `schema_uri` per tool pointing to `/.well-known/mcp/tools/{wire_name}.json` |
| Governance metadata scattered | Floors/verdicts live in docs, not in discovery response | Extend `server.json` with `governance` block: floors, verdict classes, risk tiers |
| Capability index not linked | 97-tool index exists but is not referenced from canonical surface | Add `capability_index_uri` to `server.json` |

### 3.3 MCP Resources (read-only, session optional) — enhance, don't duplicate

| Resource URI | Returns | Complements |
|---|---|---|
| `arifos://mcp/surface-map` | Full surface map (tools + resources + prompts + schemas) | `/.well-known/mcp/server.json` |
| `arifos://discovery/capabilities?q=...` | Semantic search over 97-tool index | `capability_search` stdio-only server |
| `arifos://discovery/governance` | Floors F1-F13, verdict classes, policy gate snapshot | scattered docs |

### 3.4 MCP Tools (discovery-only, no side effects)

| Tool | What It Does | Authority |
|---|---|---|
| `arif_discovery_attest` | Runtime truth test: declared vs wire vs health vs session vs auth | OBSERVE |
| `arif_discovery_resolve` | Intent → ranked tool candidates with reasons (wraps capability_select) | ANALYZE |
| `arif_discovery_governance` | Return floor/verdict/risk metadata for any tool or action | ANALYZE |

### 3.4 Response Shape (`arif_discovery_surface`)

```json
{
  "server": {
    "name": "arifOS Kernel",
    "slug": "arifos",
    "version": "v2026.05.05",
    "constitution_hash": "arifos-constitution-v2026.05.05-SSCT",
    "identity_hash": "blake3:...",
    "transport": {
      "protocol": "Streamable HTTP",
      "endpoint": "http://localhost:8088/mcp",
      "headers": ["MCP-Protocol-Version", "MCP-Session-Id", "Origin"],
      "session_idle_timeout_s": 1800,
      "session_max_age_s": 86400
    }
  },
  "organs": [
    {"name": "GEOX", "port": 8081, "role": "earth intelligence", "status": "live"},
    {"name": "WEALTH", "port": 18082, "role": "capital intelligence", "status": "live"},
    {"name": "WELL", "port": 18083, "role": "human readiness", "status": "live"},
    {"name": "A-FORGE", "port": 7071, "role": "execution shell", "status": "live"},
    {"name": "AAA", "port": 3001, "role": "control plane", "status": "live"}
  ],
  "tools": [
    {
      "name": "arif_session_init",
      "server": "arifos",
      "description": "000_INIT: Session bootstrap + identity binding...",
      "risk_tier": "medium",
      "irreversible": false,
      "floors": ["L01", "L11", "L12"],
      "epistemic_tag": "CLAIM",
      "input_schema": {...},
      "output_schema": {...},
      "category": "canonical"
    }
  ],
  "resources": [...],
  "prompts": [...],
  "verified_at": "2026-06-30T14:42:41Z",
  "ttl_seconds": 60
}
```

## 4. Zen Implementation Path

1. **Enhance `/.well-known/mcp/server.json`** (don't replace): add `wire_names`, `alias_map`, `schema_uri`, `governance` block, `capability_index_uri`.
2. **Fix `mcp_surface_truth_test.py`** to use wire tool names — ✅ DONE 2026-06-30.
3. **Add per-tool schema endpoint**: `GET /.well-known/mcp/tools/{wire_name}.json` returning input/output schema.
4. **Promote `core/capability_index/`** to expose semantic search via HTTP or MCP resource `arifos://discovery/capabilities`.
5. **Add `arif_discovery_*` tools** only where `server.json` + `tools/list` are insufficient.
6. **Redeploy** to clear `runtime_drift=TRUE`.
7. **Update `arifos_agent_surface_map.yaml`** to point to `/.well-known/mcp/server.json` as canonical.

## 5. Design Principles

- **Boring descriptions**: tool/resource descriptions are plain action-oriented prompts, zero poetry.
- **Strict schemas**: every discovery tool uses `.strict()` / `additionalProperties: false`.
- **Freshness**: every response carries `verified_at` and `ttl_seconds`.
- **No mutation**: discovery surface is read-only; mutations still route through `arif_judge` → `arif_act`.
- **Agent-first**: a single `arif_discovery_surface` call gives an agent everything it needs to stop guessing.

## 6. Live Zen Result (2026-06-30)

- Before fix: `mcp_surface_truth_test.py` → `FAIL` (session auth continuity).
- Root cause: test used internal tool names (`arif_session_init`, `arif_kernel_health`, `arif_kernel_route`) instead of wire names (`arif_init`, `arif_observe`, `arif_route`).
- After fix: test → `PASS with WARNINGS` (only `runtime_drift=TRUE` remains, requiring redeploy).
- New contradiction removed: test script now aligned with canonical public facade.

## 7. Evidence

- `/root/arifOS/.well-known/mcp/server.json` — existing canonical discovery surface (LIVE)
- `/root/arifOS/arifos_agent_surface_map.md` — existing surface map
- `/root/arifOS/arifos_agent_surface_map.yaml` — machine-readable surface map
- `/root/arifOS/TOOL_MANIFEST.json` — canonical tool index
- `/root/arifOS/core/capability_index/mcp_server.py` — semantic capability index
- `/root/arifOS/core/capability_index/models.py` — `CapabilityRecord` schema
- `/root/arifOS/core/capability_index/store.py` — Qdrant-backed store
- `/root/arifOS/scripts/mcp_surface_truth_test.py` — 5-surface truth test (patched)
- All 6 organs alive at session start (reality check passed)

---

*Forged: 2026-06-30 by OpenCode / A-FORGE*
*Authority: OBSERVE_ONLY design artifact — implementation requires 888_JUDGE SEAL*
