# PUBLIC SURFACE CANON — arifOS 7-Tool Facade

**F13 SOVEREIGN RATIFIED 2026-06-23: Canonical public surface frozen to exactly 7 verbs.**

One intent = one public tool (F4 CLARITY).

## Legacy Name Migration Guide
All "13/16 canonical", arifos_*, agi_mind, asi_heart, apex_*, physics_reality, math_estimator etc are historical/internal only (see 7-tool freeze note). Not on public surface.

## The 7 Canonical Public Tools

| Verb | Stage | Purpose |
|------|-------|---------|
| arif_init | 000 | Bootstrap governed session + bind actor/geometry. CALL FIRST. |
| arif_observe | 111 | Ground in reality, evidence, search, vitals. |
| arif_think | 333 | Instrumental reasoning under uncertainty, plan, critique. |
| arif_route | 555 | Route to correct organ / capability (federation). |
| arif_judge | 888 | Constitutional verdict (floors, HOLD/SEAL/VOID/SABAR). |
| arif_act | 900 | Execute only after valid prior SEAL (gated). |
| arif_seal | 999 | Immutable VAULT999 ledger anchor. |

## Source of Truth

- `arifosmcp/runtime/public_surface.py` : `CANONICAL_7`
- `arifosmcp/constitutional_map.py` : full registry + specs
- `arifosmcp/tool_registry.json` : machine manifest (canonical_order = 7)
- `static/.well-known/mcp/server.json` : MCP server card declaring 7

## Legacy Names

All previous "13 canonical", "arifos_*", long SDK aliases (arif_session_init etc), agi_mind/asi_heart etc are **internal dispatch only** or historical. Public wire (tools/list) returns **only** the 7.

See runtime/public_surface.py for BLOCKED_PUBLIC_PREFIXES and alias handling.

**DITEMPA BUKAN DIBERI — 7 is the surface.**

## Legacy Name Migration Guide

The following are historical / internal-only aliases and are NOT on the public surface:

- agi_mind, asi_heart, apex_soul, apex_judge, physics_reality, math_estimator, code_engine, engineering_memory, arifOS_kernel, arifos_kernel, init_anchor, vault_ledger, and all arifos_* , long SDK names (arif_session_init etc).

They may appear in docs for archaeology but are not part of canonical_order or public tools/list.

## Migration Note

Prior 13-tool surface (pre 2026-06-23) is deprecated. All agents must use the 7-verb facade for public interaction.

Full details and affordance in `runtime/public_surface.py` and AGENTS.md.
