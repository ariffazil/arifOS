# PHOENIX-72 Status

## Verdict
**HOLD / PLANNED** — Current surface is PHOENIX-13 (canonical kernel). PHOENIX-72 is the future federated organ surface, not the current active state.

## Architecture Clarification

```
Current active system = PHONEIX-13 (kernel)
Future arifos_mcp    = federation gateway + organ connections
```

### Current Active arifosmcp (port 8088)
- **Identity:** Brainstem / kernel / control layer
- **Tool count:** 13 canonical kernel tools
- **Purpose:** Session, observe, reason, critique, route, judge, vault, forge gates
- **Tool registry status:** healthy ✅
- **Organ connections:** GEOX/WEALTH/WELL are separate MCP servers, not proxies

### Future arifos_mcp (migration target)
- **Identity:** Clean MCP gateway + federation layer
- **Purpose:** "I can route to specialist organs safely" — agentic federation gateway
- **Structure:**
  - `arifos_mcp/` = kernel + providers/geox.py + providers/wealth.py + providers/well.py
  - `geox_mcp/` = subsurface intelligence MCP
  - `wealth_mcp/` = capital/valuation MCP
  - `well_mcp/` = vitality/dignity MCP
- **Tool count target:** 13 kernel + organ tools via providers/proxy mounting

## Live Service Verification (2026-05-25)

| Service | Port | Public Endpoint | Status |
|---------|------|----------------|--------|
| arifOS kernel | 8088 | arifos.arif-fazil.com | ✅ healthy |
| GEOX organ | 18081 | geox.arif-fazil.com | ✅ ok |
| WEALTH organ | 18082 | wealth.arif-fazil.com | ✅ healthy |
| WELL organ | none | well.arif-fazil.com | ⛔ 525 (intentional) |

## Current MCP Tool Surface (PHONEIX-13)

**13 canonical kernel tools:**
```
arif_session_init    — 000 INIT
arif_sense_observe  — 111 SENSE
arif_evidence_fetch — 222 EVIDENCE
arif_mind_reason   — 333 MIND
arif_heart_critique — 666 HEART
arif_kernel_route   — 444 KERNEL
arif_reply_compose  — 444r REPLY
arif_memory_recall  — 555 MEM
arif_gateway_connect — 666g GATE
arif_judge_deliberate — 888 JUDGE
arif_vault_seal     — 999 VAULT
arif_forge_execute  — 010 FORGE
arif_ops_measure    — 777 OPS
```

**4 resources:** Constitutional Doctrine, System Vitals, Complete Blueprint, Execution Bridge.

**8 prompts:** arif_system, arif_judge, arif_init, rsi, ortho, epistemic, governance, entropy.

## Domain Organ Surfaces

| Organ | Tool Count | Port | Notes |
|-------|-----------|------|-------|
| GEOX MCP | 21+ (geoscience) | 18081 | Well log, seismic, petrophysics, DST, prospect |
| WEALTH MCP | 33+ (capital) | 18082 | NPV, IRR, cashflow, inequality, capital flow |
| WELL MCP | 30+ (vitality) | none | Disabled until real service exists |

## PHOENIX-72 vs PHONEIX-13

| Dimension | PHONEIX-13 (current) | PHOENIX-72 (future) |
|-----------|----------------------|---------------------|
| Tool count | 13 | 13 kernel + organ tools |
| Character | Kernel/control layer | Kernel + federation gateway |
| Organ connection | Separate MCP servers | providers/geox.py + wealth.py + well.py |
| Main purpose | Governed reasoning, routing, judgment | Clean gateway routing to specialist organs |
| Drift status | runtime_drift=true (container vs repo) | Not yet deployed |

## Drift Status
- `runtime_drift: true` — container image (967d8e3) differs from live git HEAD (ed5cf7f)
- Container needs rebuild to sync build_commit with live_commit
- Tool registry healthy at 13 ✅

## Completion Gate (PHOENIX-72)

PHOENIX-72 requires:
1. arifos_mcp deployed as active gateway (not arifosmcp)
2. `providers/geox.py`, `providers/wealth.py`, `providers/well.py` wired
3. Domain organ MCP tools accessible via providers or FastMCP proxy mounting
4. `mcp_drift_check` enforced at startup
5. `v72.0.0` tag cut

## Untracked Directory Decisions

| Directory | Decision | Reason |
|----------|----------|--------|
| `arifOS_LEGACY/` | DELETE | No active content; informational marker only |
| `arifOS_QUARANTINED_20260524/` | PRESERVE | Requires 888_HOLD per README |
| `arifos_mcp/` | KEEP planning docs | Contains PHOENIX-72 GAP_MATRIX and migration docs; source tree may be dead-end |
| `arifOS_LEGACY/README.md` | DELETE | FROZEN reference only, no unique value |

## Notes
- Current active surface is PHONEIX-13, not PHOENIX-72
- GEOX/WEALTH/WELL are separate MCP servers (federation, not monolith)
- arifos_mcp = future clean gateway target
- arifosmcp = current live kernel on port 8088
