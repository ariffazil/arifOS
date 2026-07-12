# PUBLIC SURFACE CANON — arifOS Canonical Surface (SATU PERMUKAAN 2026-07-09 Spine P0)

**Current (2026-07-09 Spine P0):** 12 canonical public verbs (`runtime/public_surface.py:CANONICAL_12`).
`arif_triage` demoted to deprecated wire alias → `arif_init(mode=preflight|triage)`.
Standing rides signed **`sct_v1`** session capability tokens (store = optional cache).

One intent = one public tool (F4 CLARITY / MCP convergence). Kernel is a constitutional switchboard, not a warehouse.

## The 12 Canonical Public Tools (live)

| # | Verb | Stage | Role | Agentic Selection — When to Choose This Tool |
|---|------|-------|------|------------------------------------------------|
| 1 | `arif_init` | 000 | Session anchor | START HERE. Bootstrap + bind identity + mint `session_token` (`sct_v1`). Modes: `init`, `light`, `resume`, `validate`, `canary`, **`preflight`**, **`triage`**. Absorbs canary + triage. |
| 2 | `arif_observe` | 111 | Reality sensing | Ground in reality. Modes: `search`, `fetch`, `ingest`, `compass`, `atlas`, `vitals`. Absorbs fetch as `mode=fetch` (no live aliases). |
| 3 | `arif_think` | 333 | Cognitive engine | Reason, plan, reflect. Internal impl name `arif_mind_reason` is not public. |
| 4 | `arif_route` | 444 | Organ router | Route intent to organ. Modes: `route`, `bridge`. No `arif_triage`/`arif_delegate` aliases. |
| 5 | `arif_bridge_connect` | 444-direct | Direct organ bridge | HIGH path; prefer `arif_route` for default. |
| 6 | `arif_critique` | 555 | Maruah / risk | Ethical risk before irreversible. |
| 7 | `arif_memory` | 555m | Memory governor | Constitutional memory gate. |
| 8 | `arif_judge` | 888 | Constitutional verdict | SEAL/HOLD/SABAR/VOID. Structured returns; SCT standing. |
| 9 | `arif_forge` | 777 | Guarded execution | After SEAL. `arif_act` internal-only (never in `allowed_next_verbs`). Prefer `dry_run`. |
| 10 | `arif_compose` | reply | Response composer | Final human reply LAST. |
| 11 | `arif_seal` | 999 | VAULT999 seal | Immutable ledger. Prefer `verify`/`dry_run` until SOVEREIGN. |
| 12 | `arif_verify` | E1 | SEAL verification gate | Confirms the actor-bound approval path before guarded execution. |

## Metabolic Loop

```
000 → 111 → 333 → 444 → 444-direct → 555 → 555m → 777 → 888 → reply → 999 → E1
init  observe think route bridge       critique memory forge  judge reply  seal  verify
```

One stage = one public verb. Absorbed verbs become modes on their parent tool.

## Absorbed Tools (modes on parent, not separate verbs)

| Absorbed Verb | Parent Tool | Mode | Why Absorbed |
|---------------|------------|------|-------------|
| `arif_canary` | `arif_init` | `mode=canary` | Transport diagnostic belongs at session entry |
| `arif_triage` | `arif_init` / `arif_route` | `mode=triage` | Preflight belongs at session entry or routing |
| `arif_fetch` | `arif_observe` | `mode=fetch` | Evidence fetch is a sensing activity |
## Deprecated Aliases

| Alias | Resolves To |
|-------|------------|
| `arif_session_init` | `arif_init` |
| `arif_gateway_connect` | `arif_route` |
| `arif_forge_execute` | `arif_forge` |
| `arif_heart_critique` | `arif_critique` |
| `arif_evidence_fetch` | `arif_observe(mode=fetch)` |
| `arif_mind_reason` | `arif_think` |
| `arif_reply_compose` | `arif_compose` |
| `arif_sense_observe` | `arif_observe` |
| `arif_memory_recall` | `arif_memory(mode=recall)` |
| `arif_kernel_route` | `arif_route` |
| `arif_runtime_health` | internal-only (kernel runtime telemetry — CPU, mem, disk, topology, drift). Replaces deprecated `arif_measure`. NOT human/machine vitality (WELL owns that). |
| `arif_canary` | `arif_init(mode=canary)` |
| `arif_triage` | `arif_init(mode=triage)` |
| `arif_fetch` | `arif_observe(mode=fetch)` |
| `arif_conformance_report` | `arif_init(mode=canary)` with report |

## Domain-Specific Compute → Owns-Organ

- GEOX-specific compute → GEOX organ (:8081)
- WEALTH-specific compute → WEALTH organ (:18082)
- WELL-specific assessment → WELL organ (:18083)
- A-FORGE build steps → A-FORGE organ (:7071)
- AAA display/UI → AAA organ (:3001)

## Source of Truth

- `arifosmcp/runtime/public_surface.py` : `CANONICAL_12` (12 canonical public verbs)
- `arifosmcp/runtime/sct.py` : signed session capability (`sct_v1`)
- `arifosmcp/constitutional_map.py` : `CANONICAL_TOOLS` (full registry)
- `arifosmcp/resources/schema.py` : `SCHEMA_TEXT` (blueprint resource)
- `static/.well-known/mcp/server.json` : MCP server card

## Legacy Name Migration Guide

All previous "7 canonical", "12 canonical", "13 canonical", `arifos_*`, long SDK aliases
(`arif_session_init`, `arif_gateway_connect`, `arif_forge_execute`, etc), `agi_mind`,
`asi_heart`, `apex_soul`, `apex_judge`, `physics_reality`, `math_estimator`, `code_engine`,
`engineering_memory` are historical/internal only. Public wire (`tools/list`) returns **canonical
public verbs only** (triage = deprecated alias). Standing = `session_token` (`sct_v1`).

See `runtime/public_surface.py` for `BLOCKED_PUBLIC_PREFIXES`, `DEPRECATED_CANARY_CHILDREN`, and alias handling.

**DITEMPA BUKAN DIBERI — one state machine, one standing token, not eleven costumes.**
