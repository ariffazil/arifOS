---
type: Synthesis
tier: 50_AUDITS
strand:
- operations
audience:
- engineers
difficulty: intermediate
prerequisites:
- Tool_Surface_Architecture
tags:
- audit
- architecture
- drift
- compatibility
- runtime
- wiki
sources:
- tool_specs.py
- tools.py
- tools_hardened_dispatch.py
- kernel_router.py
- __main__.py
- server.py
- rest_routes.py
- resources.py
- public_registry.py
- tool_registry.json
- MCP_Tools.md
- check_tool_surface_drift.py
last_sync: '2026-04-10'
confidence: 0.96
verified_clean: true
---

# Audit: Surface Fragmentation

## Canonical Count

- Canonical tool count from `tool_specs.py`: **11**
- Canonical ids: `arifos_init`, `arifos_sense`, `arifos_mind`, `arifos_route`, `arifos_heart`, `arifos_ops`, `arifos_judge`, `arifos_memory`, `arifos_vault`, `arifos_forge`, `arifos_vps_monitor`

## Surface Inventory

| File | Classification | Why |
| :--- | :--- | :--- |
| `arifosmcp/runtime/tool_specs.py` | `canonical` | Defines the current contract, canonical ids, canonical count, and legacy alias registry. |
| `arifosmcp/runtime/tools.py` | `stale duplicate` | Still declares runtime handlers directly instead of deriving from the canonical spec. |
| `arifosmcp/runtime/__main__.py` | `stale duplicate` | Stdio entrypoint still carries explicit runtime payload handling even though it is now canonically aligned. |
| `arifosmcp/runtime/kernel_router.py` | `stale duplicate` | Hard-codes canonical ids in routing selection instead of deriving from shared metadata. |
| `arifosmcp/runtime/tools_hardened_dispatch.py` | `compatibility` | Carries canonical dispatch plus legacy alias routing. |
| `arifosmcp/runtime/megaTools/__init__.py` | `compatibility` | Preserves legacy mega-tool namespace and compatibility probe surface. |
| `arifosmcp/runtime/compatibility/memory_backend.py` | `compatibility` | Dedicated compatibility backend with legacy payloads. |
| `arifosmcp/runtime/compatibility/vault_backend.py` | `compatibility` | Dedicated compatibility backend with legacy payloads. |
| `arifosmcp/runtime/server.py` | `stale duplicate` | Maintains transport/runtime narratives that should eventually derive from canonical metadata. |
| `arifosmcp/runtime/rest_routes.py` | `generated target` | Transport surface that should be generated from canonical metadata. |
| `arifosmcp/runtime/resources.py` | `generated target` | Resource-facing tool inventory should be derived from canonical metadata. |
| `arifosmcp/runtime/public_registry.py` | `generated target` | Public registry surface now matches canonical count and should remain generated. |
| `arifosmcp/tool_registry.json` | `generated target` | External registry manifest now matches canonical 11-tool set and should remain generated. |
| `wiki/pages/MCP_Tools.md` | `generated target` | Inventory page should remain aligned to canonical spec output. |
| `wiki/index.md` | `generated target` | Human catalog with machine-sensitive counts and inventory references. |
| `wiki/pages/Tool_Surface_Architecture.md` | `generated target` | Architecture inventory page that should stay aligned with checker output. |
| `wiki/pages/Drift_Checks.md` | `generated target` | Checker documentation and enforcement surface. |
| `runtime/contracts.py` | `unknown` | Declares older AAA canonical names; adjacent to MCP v2 but not clearly authoritative for current tool surface. |

## Live Checker Result (2026-04-08)

```bash
python scripts/check_tool_surface_drift.py
```

```text
== Verdict ==
NO DRIFT DETECTED
```

## What Was Resolved

| Surface | Resolution |
| :--- | :--- |
| `arifosmcp/tool_registry.json` | Now matches the canonical 11-tool set, including `arifos_vps_monitor`. |
| `arifosmcp/runtime/public_registry.py` | Now checks against canonical count `11`. |
| `arifosmcp/runtime/tools_hardened_dispatch.py` | Now surfaces all 11 canonical tools. |
| `arifosmcp/runtime/resources.py` | No longer leaks a dotted tool example outside compatibility scope. |
| `arifosmcp/runtime/tools.py` | Narrative dotted tool references normalized to canonical underscore ids. |
| `arifosmcp/runtime/server.py` | Narrative dotted tool references normalized to canonical underscore ids. |
| `arifosmcp/runtime/__main__.py` | Stdio compatibility payload now uses `arifos_vault`. |

## Approved Compatibility Files

- `arifosmcp/runtime/tool_specs.py`
- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `arifosmcp/runtime/megaTools/__init__.py`
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`

## Dotted Name Policy

- dotted names may remain inside **approved compatibility files**
- dotted names outside that boundary are drift
- current checker result confirms that the boundary is respected

## 888_HOLD

The checker is green, but structural cleanup is **not finished**:

- `tools.py`, `__main__.py`, `kernel_router.py`, and `server.py` still duplicate canonical knowledge instead of deriving from `tool_specs.py`
- `megaTools/__init__.py` still acts as a broad compatibility surface and should not be collapsed without downstream validation
- archive and namespace cleanup remain `888_HOLD` until generation and compatibility isolation are complete
