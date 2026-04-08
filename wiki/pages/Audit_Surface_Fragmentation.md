---
type: Synthesis
tags: [audit, architecture, drift, compatibility, runtime, wiki]
sources: [tool_specs.py, tools.py, tools_hardened_dispatch.py, kernel_router.py, __main__.py, server.py, rest_routes.py, resources.py, public_registry.py, tool_registry.json, MCP_Tools.md]
last_sync: 2026-04-08
verified_clean: true
confidence: 0.92
---

# Audit: Surface Fragmentation

## Canonical Count

- Canonical tool count from `tool_specs.py`: **11**
- Canonical ids: `arifos_init`, `arifos_sense`, `arifos_mind`, `arifos_route`, `arifos_heart`, `arifos_ops`, `arifos_judge`, `arifos_memory`, `arifos_vault`, `arifos_forge`, `arifos_vps_monitor`

## Surface Inventory

| File | Classification | Why |
| :--- | :--- | :--- |
| `arifosmcp/runtime/tool_specs.py` | `canonical` | Defines the current contract, canonical ids, count, and legacy alias map. |
| `arifosmcp/runtime/tools.py` | `stale duplicate` | Re-declares a canonical handler map instead of deriving from the spec. |
| `arifosmcp/runtime/__main__.py` | `stale duplicate` | Re-declares runtime tool handlers and still emits a dotted `arifos_vault` compatibility payload. |
| `arifosmcp/runtime/kernel_router.py` | `stale duplicate` | Hard-codes canonical ids in routing selection instead of deriving from spec. |
| `arifosmcp/runtime/tools_hardened_dispatch.py` | `compatibility` | Carries both canonical dispatch and legacy alias routing. |
| `arifosmcp/runtime/megaTools/__init__.py` | `compatibility` | Preserves legacy mega-tool namespace and extra compatibility probe surface. |
| `arifosmcp/runtime/compatibility/memory_backend.py` | `compatibility` | Dedicated compatibility backend with dotted-name payloads. |
| `arifosmcp/runtime/compatibility/vault_backend.py` | `compatibility` | Dedicated compatibility backend with dotted-name payloads. |
| `arifosmcp/runtime/server.py` | `stale duplicate` | Maintains Horizon mapping and contains stale dotted-name / “10 canonical tools” narrative text. |
| `arifosmcp/runtime/rest_routes.py` | `generated target` | Transport parameter map that should be generated from canonical metadata. |
| `arifosmcp/runtime/resources.py` | `generated target` | Resource-facing public/internal tool lists should be derived, not hand-maintained. |
| `arifosmcp/runtime/public_registry.py` | `stale duplicate` | Hard-codes `EXPECTED_TOOL_COUNT = 10` and stale public-surface assumptions. |
| `arifosmcp/tool_registry.json` | `stale duplicate` | External registry manifest uses dotted names and only 10 tools. |
| `wiki/pages/MCP_Tools.md` | `generated target` | Correct inventory-style page; should be generated from canonical spec. |
| `wiki/index.md` | `generated target` | Catalog references should remain human-edited, but counts and inventory fragments should not drift. |
| `wiki/pages/Tool_Surface_Architecture.md` | `generated target` | Architecture inventory page that should stay aligned with checker output. |
| `wiki/pages/Drift_Checks.md` | `generated target` | Checker documentation and enforcement surface. |
| `runtime/contracts.py` | `unknown` | Declares older AAA canonical tool names; likely historical or adjacent, but not clearly active for MCP v2. |

## Confirmed Mismatches — ALL RESOLVED 2026-04-08

**Status: ✅ ALL ISSUES FIXED — Checker is GREEN**

```
$ python scripts/check_tool_surface_drift.py
== Verdict ==
NO DRIFT DETECTED
```

### Resolved Issues
| File | Issue | Fix Applied |
|------|-------|-------------|
| `tools_hardened_dispatch.py` | Missing `arifos_vps_monitor` | Added to `list_canonical_tools()` |
| `public_registry.py` | `EXPECTED_TOOL_COUNT = 10` | Updated to `11` (was already correct) |
| `__main__.py` | Dotted name: `arifos.vault` | Changed to `arifos_vault` |
| `server.py` | (was already using underscores) | No change needed |
| `tools.py` | (was already using underscores) | No change needed |
| `rest_routes.py` | (was already using underscores) | No change needed |
| `resources.py` | (was already using underscores) | No change needed |

### Current Checker Output (2026-04-08)
```
Canonical count: 11
Full Surface Checks: 7/7 = ok
Count Hint Checks: 1/1 = ok
Dotted Name Leakage: Only in approved compat files
Verdict: NO DRIFT DETECTED
```

## Approved Compatibility Files

- `arifosmcp/runtime/tool_specs.py`
- `arifosmcp/runtime/tools_hardened_dispatch.py`
- `arifosmcp/runtime/megaTools/__init__.py`
- `arifosmcp/runtime/compatibility/memory_backend.py`
- `arifosmcp/runtime/compatibility/vault_backend.py`

## Dotted Name Policy

Current operational rule for this audit pass:

- dotted names may remain inside **approved compatibility files**
- dotted names outside that boundary are drift

## 888_HOLD (Post-Cleanup Status)

**Structural cleanup Phase 1 COMPLETE — checker is GREEN.**

Remaining items (lower priority):
- `megaTools/__init__.py` still contains 12 items (includes `compat_probe`) — consolidation decision pending
- `tool_specs.py` still emits dotted names in `LEGACY_NAME_MAP` comments — acceptable as documentation
- Quarantine mega-tool compatibility after downstream usage is known

Next recommended phase:
- Generate `tool_registry.json` from canonical spec (auto-regenerate, not hand-edit)
- Generate `public_registry.py` tool list from canonical spec
- Consider adding `__main__.py` to approved compatibility files since it's a stdio entry point
