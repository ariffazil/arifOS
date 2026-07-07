# PUBLIC SURFACE CANON — arifOS 10-Tool Canonical Surface

**CANONICAL-10 (2026-07-07): 9-stage metabolic loop + constitutional memory governor.**
Consolidated from the prior 12-verb surface (2026-07-04) by absorbing 4 verbs into modes
on their parent tools, and promoting 2 tools (arif_memory, arif_seal) to canonical.

One intent = one public tool (F4 CLARITY). The Kernel is a constitutional switchboard, not a warehouse.

## The 10 Canonical Public Tools

| # | Verb | Stage | Role | Agentic Selection — When to Choose This Tool |
|---|------|-------|------|------------------------------------------------|
| 1 | `arif_init` | 000 | Session anchor | START HERE. Bootstrap session + bind actor identity. Modes: `init`, `resume`, `validate`, `canary`, `preflight`, `triage`. Absorbs `arif_canary` + `arif_triage` as modes. |
| 2 | `arif_observe` | 111 | Reality sensing | Ground in reality. Web search, URL fetch, vitals, repo map. Modes: `search`, `fetch`, `ingest`, `compass`, `atlas`, `entropy_dS`, `vitals`. Absorbs `arif_fetch` as `mode=fetch`. |
| 3 | `arif_think` | 333 | Cognitive engine | Reason, plan, reflect, critique, metabolize. Modes: `reason`, `reflect`, `verify`, `axioms`, `plan`, `plan_review`, `plan_approve`, `refactor_plan`, `metabolize`, `simulate`. |
| 4 | `arif_route` | 444 | Organ router | Route intent to correct federation organ. Modes: `route`, `bridge`. Absorbs `arif_bridge_connect` as `mode=bridge`. |
| 5 | `arif_critique` | 555 | Maruah / risk | Ethical risk + human impact assessment before irreversible actions. Modes: `critique`, `redteam`, `maruah`, `shadow`, `deescalate`, `empathy`. |
| 6 | `arif_memory` | 555m | Memory governor | Constitutional memory gate (F1/F2/F4/F9/F11/F13). Memory writes are J-space mutations that shape future reasoning. Modes: `recall`, `inspect`, `attest`, `remember`, `promote`, `revise`, `forget`, `audit`. |
| 7 | `arif_judge` | 666 | Constitutional verdict | Render `SEAL_CANDIDATE` / `HOLD` / `SABAR` / `VOID`. The Kernel judges; it does not seal. Modes: `judge`, `compare`, `history`, `explain`, `floor_status`, `witness_consensus`. |
| 8 | `arif_forge` | 777 | Guarded execution | Execute only after a `SEAL_CANDIDATE` from `arif_judge`. Modes: `engineer`, `query`, `write`, `generate`, `commit`, `recall`, `dry_run`. `arif_act` retained as internal alias. |
| 9 | `arif_compose` | 888 | Response composer | Governed final reply wire. Call LAST after reasoning + judgment complete. Modes: `compose`, `summarize`, `cite`, `tone_shift`, `style`, `format`, `nudge`, `repo_answer`. |
| 10 | `arif_seal` | 999 | VAULT999 seal | Immutable ledger append (irreversible). Modes: `seal`, `verify`, `ledger`, `changelog`, `audit`, `dry_run`. |

## Metabolic Loop

```
000 → 111 → 333 → 444 → 555 → 555m → 666 → 777 → 888 → 999
init  observe think route critique memory judge  forge  compose seal
```

One stage = one public verb. Absorbed verbs become modes on their parent tool.

## Absorbed Tools (modes on parent, not separate verbs)

| Absorbed Verb | Parent Tool | Mode | Why Absorbed |
|---------------|------------|------|-------------|
| `arif_canary` | `arif_init` | `mode=canary` | Transport diagnostic belongs at session entry |
| `arif_triage` | `arif_init` / `arif_route` | `mode=triage` | Preflight belongs at session entry or routing |
| `arif_fetch` | `arif_observe` | `mode=fetch` | Evidence fetch is a sensing activity |
| `arif_bridge_connect` | `arif_route` | `mode=bridge` | Direct organ call is a routing decision |

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
| `arif_measure` | internal-only (organ health via arif_observe(mode=vitals)) |
| `arif_canary` | `arif_init(mode=canary)` |
| `arif_triage` | `arif_init(mode=triage)` |
| `arif_fetch` | `arif_observe(mode=fetch)` |
| `arif_bridge_connect` | `arif_route(mode=bridge)` |
| `arif_conformance_report` | `arif_init(mode=canary)` with report |

## Domain-Specific Compute → Owns-Organ

- GEOX-specific compute → GEOX organ (:8081)
- WEALTH-specific compute → WEALTH organ (:18082)
- WELL-specific assessment → WELL organ (:18083)
- A-FORGE build steps → A-FORGE organ (:7071)
- AAA display/UI → AAA organ (:3001)

## Source of Truth

- `arifosmcp/runtime/public_surface.py` : `CANONICAL_9` (canonical — 10 tools)
- `arifosmcp/constitutional_map.py` : `CANONICAL_TOOLS` (full registry)
- `arifosmcp/resources/schema.py` : `SCHEMA_TEXT` (blueprint resource)
- `static/.well-known/mcp/server.json` : MCP server card

## Legacy Names

All previous "7 canonical", "12 canonical", "13 canonical", `arifos_*`, long SDK aliases
(`arif_session_init`, `arif_gateway_connect`, `arif_forge_execute`, etc), `agi_mind`,
`asi_heart`, `apex_soul`, `apex_judge`, `physics_reality`, `math_estimator`, `code_engine`,
`engineering_memory` are historical/internal only. Public wire (`tools/list`) returns **only** the 10.

See `runtime/public_surface.py` for `BLOCKED_PUBLIC_PREFIXES`, `DEPRECATED_CANARY_CHILDREN`, and alias handling.

**DITEMPA BUKAN DIBERI — 10 is the surface, and the Kernel becomes powerful when it stops being impressive.**
