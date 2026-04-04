# arifOS Unification Matrix
**Status:** CANONICAL REFERENCE
**Version:** v2026.2.27 | MANIFEST_VERSION=3
**Motto:** *DITEMPA BUKAN DIBERI — before refactoring, map the terrain*

---

## The Two Live Server Instances

This repo intentionally runs two FastMCP instances. Every change touching tool names,
resources, or prompts must be applied to **both** or the two entrypoints will diverge.

| | Internal Layer | Public Layer |
|---|---|---|
| **Module** | `aaa_mcp/server.py` | `arifos_aaa_mcp/server.py` |
| **Constructor** | `create_unified_mcp_server()` | `create_aaa_mcp_server()` |
| **Entrypoint** | internal module only | `python -m aaa_mcp` or `python -m arifos_aaa_mcp` |
| **Tool source** | `@mcp.tool()` decorators (13 tools, direct) | Wrapper functions calling `legacy.*` from `aaa_mcp` |
| **Governance** | None (raw FastMCP) | `validate_input()` + `require_session()` contracts |
| **Resource URIs** | `arifos://info`, `arifos://templates/*`, `arifos://schemas/tooling` | `arifos://aaa/schemas`, `arifos://aaa/full-context-pack` |
| **Prompt names** | `arifos.prompt.governance_brief` | `arifos.prompt.aaa_chain` |
| **ABI guard** | `MANIFEST_VERSION` constant (read-only) | `MANIFEST_VERSION` + check in `create_aaa_mcp_server()` |

**Rule**: Any tool name or signature change → touch both `aaa_mcp/server.py` AND `arifos_aaa_mcp/server.py`.

---

## Tool Name Generation Map

Four generations of naming exist. Gen-4 is current canon.

| Gen-1 (Legacy Protocol) | Gen-2 (Mid-gen Kernel) | Gen-3 (UX Canonical) | Gen-4 (Current Canon) | Stage |
|------------------------|----------------------|---------------------|----------------------|-------|
| `init_gate` | `init_session` | `anchor_session` | `anchor_session` ← same | 000 |
| `agi_reason` | `agi_cognition` | `reason_mind` | `reason_mind` ← same | 333 |
| `phoenix_recall` | `phoenix_recall` | `recall_memory` | `recall_memory` ← same | 444 |
| `asi_empathize` | `asi_empathy` | `simulate_heart` | `simulate_heart` ← same | 555 |
| `asi_align` | `asi_align` | `critique_thought` | `critique_thought` ← same | 666 |
| `apex_verdict` | `apex_verdict` | `apex_judge` | **`apex_judge`** ← current canon | 888 |
| `sovereign_actuator` | `sovereign_actuator` | `eureka_forge` | `eureka_forge` ← same | 777 |
| `vault_seal` | `vault_seal` | `seal_vault` | `seal_vault` ← same | 999 |
| `reality_search` | `search` | `search_reality` | `search_reality` ← same | 111 |
| `fetch` | `fetch` | `fetch_content` | `fetch_content` ← same | 444 |
| `analyze` | `analyze` | `inspect_file` | `inspect_file` ← same | 111 |
| `system_audit` | `system_audit` | `audit_rules` | `audit_rules` ← same | 333 |
| `sense_health` | `sense_health` | `check_vital` | `check_vital` ← same | 555 |

**Key rule**: `apex_judge` is the current canon. `judge_soul` is backward-compat only.

---

## Alias Resolution Chain

```
Client call: "apex_verdict"  (gen-1 or gen-2)
     ↓
REST TOOL_ALIASES (rest_routes.py):  apex_verdict → apex_judge
     ↓
_TOOL_REGISTRY (arifos_aaa_mcp/server.py): apex_judge → apex_judge callable
     ↓
FastMCP dispatcher: name="apex_judge" → _apex_verdict() handler

Client call: "apex_judge"  (current canon)
     ↓
FastMCP dispatcher: name="apex_judge" → _apex_verdict() handler

Client call: "judge_soul"  (compat alias)
     ↓
FastMCP dispatcher: name="apex_judge" → _apex_verdict() handler ✅
```

---

## Resource URI Canon

Two URI namespaces exist. `arifos://aaa/*` is the client-facing canon.

| Resource | Internal URI (`aaa_mcp`) | Public URI (`arifos_aaa_mcp`) | Status |
|----------|--------------------------|-------------------------------|--------|
| Static server info | `arifos://info` | *(not exposed publicly)* | Internal only |
| Tool schemas | `arifos://schemas/tooling` | `arifos://aaa/schemas` | **Split → Phase 2** |
| Full context pack | `arifos://templates/full-context` | `arifos://aaa/full-context-pack` | **Split → Phase 2** |
| Constitutional floors | `arifos://floors/{floor_id}` | *(not exposed publicly)* | Internal only |

**Phase 2 fix (Option A — non-breaking)**: Mirror `arifos://aaa/schemas` and
`arifos://aaa/full-context-pack` into `aaa_mcp/server.py` so `server.py` (root)
serves the same URIs as the canonical path.

---

## Tool Implementation Tiers

| Tool | Backend | Notes |
|------|---------|-------|
| `anchor_session` | `aclip_cai.triad.anchor()` | Full triad path |
| `reason_mind` | `aclip_cai.triad.reason()` | Full triad path |
| `recall_memory` | `aclip_cai.triad.integrate()` | Full triad path |
| `simulate_heart` | `aclip_cai.triad.align()` | Full triad path |
| `critique_thought` | `aclip_cai.triad.align()` + heuristic lens fallback | Triad-backed verdict path with mental-model metadata |
| `apex_judge` | `aclip_cai.triad.forge()` + `audit()` | Full triad path |
| `eureka_forge` | `aclip_cai.triad.forge()` | Full triad path |
| `seal_vault` | `aclip_cai.triad.seal()` | Full triad path |
| `search_reality` | `aaa_mcp.external_gateways` (Perplexity/Brave) | External APIs |
| `fetch_content` | HTTP fetch | Direct HTTP |
| `inspect_file` | `aclip_cai.tools.fs_inspector` | Local filesystem |
| `audit_rules` | Constitution audit logic | Internal |
| `check_vital` | `aclip_cai.tools.system_monitor` | System health |

---

## Entropy Phase Plan

### Phase 0 — Freeze architecture ✅ DONE
- Two-layer architecture declared intentional
- `create_unified_mcp_server` documented (not deprecated)
- `create_aaa_mcp_server` has ABI version guard

### Phase 1 — This document ✅ DONE
- All name generations mapped
- Both server instances documented
- Alias chain traced end-to-end

### Phase 2 — Normalize resource/prompt URIs
**Goal**: `server.py` (root) serves the same resource URIs as `aaa_mcp/__main__.py`.
**Action**: Add `arifos://aaa/schemas` and `arifos://aaa/full-context-pack` resource
decorators to `aaa_mcp/server.py` (alias to existing handlers).
Do NOT touch `server.py` root entrypoint yet.

### Phase 3 — Consolidate shared contracts
Single source of truth for:
- Tool manifest → already in `aaa_mcp/protocol/tool_registry.py` (use it everywhere)
- Stage map → `arifos_aaa_mcp/governance.py:TOOL_STAGE_MAP`
- Alias map → `arifos_aaa_mcp/rest_routes.py:TOOL_ALIASES`
- Resource URIs → add URI constants to `aaa_mcp/protocol/`

### Phase 4 — Wire critique_thought to triad ✅ DONE
- `critique_thought` now uses `aclip_cai.triad.align()` as the primary backend
- Mental-model heuristics remain as explanatory metadata and fallback behavior

### Phase 5 — Test lane cleanup
```
tests/
  canonical/   ← arifos_aaa_mcp public surface
  compat/      ← backward-compat alias tests
  integration/ ← e2e pipeline tests
  archive/     ← historical (already filtered by conftest.py)
```

---

## Files to Touch for Common Changes

| Task | Files |
|------|-------|
| **Rename a tool** | `aaa_mcp/server.py` · `arifos_aaa_mcp/server.py` · `arifos_aaa_mcp/rest_routes.py` · `aaa_mcp/protocol/tool_naming.py` · `arifos_aaa_mcp/governance.py` · `aaa_mcp/selftest.py` |
| **Add a tool** | Above + `aaa_mcp/protocol/tool_registry.py` + `aaa_mcp/protocol/tool_graph.py` + new test |
| **Change a resource URI** | `aaa_mcp/server.py` (internal) + `arifos_aaa_mcp/server.py` (public) + affected tests |
| **Bump MANIFEST_VERSION** | `aaa_mcp/server.py` + `arifos_aaa_mcp/server.py` (both must match) |
| **Add a constitutional floor** | `core/shared/floors.py` · `core/kernel/evaluator.py` · `arifos_aaa_mcp/governance.py` |

---

*Last updated: 2026-02-27 | Maintained by arifOS kernel team*
