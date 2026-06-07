# tool_registry_v2.v1-DEPRECATED-2026-06-07.json — Purpose Label (Ω — 2026-06-07)

> **Role:** DEPRECATED v1 — obsolete arifOS working roadmap (pre-naming-convention-change)
>
> **Deprecated:** 2026-06-07 (replaced by canonical `tool_registry.json`)
>
> **Tool count:** 79 (26 marked LIVE — all obsolete names, see analysis below)
>
> **Used by:** A-FORGE `/api/repo-steward/registry-trinity` (working_roadmap role — slot now empty)

## Why Deprecated

The v1 file tracked an earlier organ structure where:
- arifOS tools were double-prefixed: `arifos_arifos_init`, `arifos_arifos_heart`, etc.
- WEALTH organ tools (`wealth_*`) were tracked inside the arifOS registry (wrong layer)
- Legacy aliases were preserved: `mcp_health_check`, `vault_query`, `vault_write`

After the naming-convention change (canonical uses `arif_*` prefix, single level), NONE of the 13 canonical tool names appear in this v1 file. The 26 LIVE entries are 100% obsolete names.

**This is NOT "13 retired tools."** It is a complete naming-convention change that the v1 file never reflected.

## Deprecation Path

- 2026-06-07: `tool_registry_v2.json` (this file) → `archive/legacy/tool_registry_v2.v1-DEPRECATED-2026-06-07.json`
- 2026-06-07: `tool_registry.json` (canonical) → remains source of truth, regenerated from `arifOS.arifosmcp.constitutional_map.CANONICAL_TOOLS`
- Future: if a v2 working roadmap is needed, it should be regenerated from canonical's `arif_*` names + a fresh HOLD/FORGED set, not patched from this v1.

## What's Preserved

- All 79 entries (with tier, stage, floor_gates, descriptions)
- The 26 LIVE entries' audit trail (when they were marked LIVE)
- The 23 HOLD + 30 FORGED entries (historical roadmap)

## What NOT to do

- ❌ Do not import from this file
- ❌ Do not regenerate `tool_registry.json` from this file
- ❌ Do not move this file out of `archive/legacy/`

DITEMPA BUKAN DIBERI.
