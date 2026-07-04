# PUBLIC SURFACE CANON — arifOS 12-Tool Facade

**F13 SOVEREIGN RATIFIED 2026-07-04: Canonical public surface frozen to exactly 12 verbs.**
(YELLOW-band trim. Prior freeze was 7 verbs on 2026-06-23.)

One intent = one public tool (F4 CLARITY). The Kernel is a constitutional switchboard, not a warehouse.

## The 12 Canonical Public Tools

| Verb | Stage | Role | Agentic Selection — When to Choose This Tool |
|------|-------|------|------------------------------------------------|
| `arif_init` | 000 | Session anchor | START HERE. Bootstrap session + bind actor identity. Precedes all other calls. |
| `arif_canary` | 000c | Transport probe | Multimode diagnostic — 6 modes: `ping`, `schema_echo`, `version_echo`, `transport_echo`, `initialize_probe`, `conformance_report`. One diagnostic door. |
| `arif_triage` | 000t | Status + preflight | Session status, priority, preflight. Use when you have a live session and want to know the next safe action. |
| `arif_observe` | 111 | Sensing observation | Ground in reality. Broad sense/search/environment — web search, vitals, repo map. |
| `arif_fetch` | 111f | External evidence | Fetch a specific URL/source and verify external evidence with provenance tags. |
| `arif_think` | 333 | Reasoning draft | Reason under uncertainty — analyze, plan, critique, metabolize. |
| `arif_critique` | 666 | Maruah / risk check | Pre-judge ethical + consequence critique. Use before irreversible actions or decisions affecting dignity. |
| `arif_route` | 444 | Organ router | Route to correct organ/tool. Bridge when intent→tool mapping is uncertain. |
| `arif_bridge_connect` | 555b | Direct organ bridge | Low-level direct organ tool call. Bypasses triage — caller must specify organ + tool_name. |
| `arif_judge` | 888 | Constitutional verdict | Render `SEAL_CANDIDATE` / `HOLD` / `SABAR` / `VOID`. The Kernel judges; it does not seal. |
| `arif_forge` | 900 | Guarded execution | Execute only after a `SEAL_CANDIDATE` from `arif_judge`. Verdict-Gated Action Bus. `arif_act` retained internally as alias. |
| `arif_compose` | 444r | Response composer | Governed final reply wire. Call LAST after reasoning + judgment complete. |

## What the Kernel is NOT (Removed from Public Surface)

The 2026-07-04 trim removed from the public wire — **compatibility location = chatgpt_adapter, never arifOS_kernel_core** — see `forge_work/YELLOW-KERNEL-TRIM-12.md`:

### Aliases → resolve to canonical
- `arif_session_init` → `arif_init`
- `arif_gateway_connect` → `arif_route` (or `arif_bridge_connect`)
- `arif_forge_execute` → `arif_forge`
- `arif_heart_critique` → `arif_critique`
- `arif_evidence_fetch` → `arif_fetch`
- `arif_mind_reason` → `arif_think`
- `arif_reply_compose` → `arif_compose`
- `arif_sense_observe` → `arif_observe`

### Fake-seal / vault / poetry → VAULT999 owns, not Kernel
- `arif_seal` → legacy handler; **VAULT999 owns the actual receipt seal.** `arif_judge` can return `SEAL_CANDIDATE`.
- `arif_vault_seal` → VAULT999 owns.
- `hermes_vault_query` / `arif_vault_query` → archive organ query (already internal-only).
- `arif_explore` → overlaps with `arif_observe` + `arif_fetch`; deleted.
- `arif_measure` → organ-only; deleted from Kernel.

### Memory → archive/receipts
- `arif_memory` → use `VAULT999` (durable truth) / `A_ARCHIVE` (logs) / session state. Kernel doesn't remember; it references receipts.
- `arif_memory_recall` → deprecated alias of `arif_memory`; both internal.

### Duplicate conformance entrypoints
- `arif_conformance_report` → use `arif_canary(mode="conformance_report")`. One diagnostic door.

### Domain-specific compute → owns-organ
- GEOX-specific compute → GEOX organ
- WEALTH-specific compute → WEALTH organ
- WELL-specific assessment → WELL organ
- A-FORGE build steps → A-FORGE organ
- AAA display/UI → AAA organ

## Source of Truth

- `arifosmcp/runtime/public_surface.py` : `CANONICAL_12` (canonical), `CANONICAL_7`/`CANONICAL_13` (deprecated aliases)
- `arifosmcp/constitutional_map.py` : `CORE_TWELVE` + `_PUBLIC_12`
- `arifosmcp/tool_registry.json` : machine manifest (`canonical_order` = 12)
- `static/.well-known/mcp/server.json` : MCP server card declaring 12

## Legacy Names

All previous "7 canonical", "13/16 canonical", `arifos_*`, long SDK aliases (`arif_session_init`, `arif_gateway_connect`, `arif_forge_execute`, etc), `agi_mind`, `asi_heart`, `apex_soul`, `apex_judge`, `physics_reality`, `math_estimator`, `code_engine`, `engineering_memory` are historical/internal only. Public wire (`tools/list`) returns **only** the 12.

See `runtime/public_surface.py` for `BLOCKED_PUBLIC_PREFIXES`, `DEPRECATED_CANARY_CHILDREN`, and alias handling.

**DITEMPA BUKAN DIBERI — 12 is the surface, and the Kernel becomes powerful when it stops being impressive.**
