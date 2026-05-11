# PUBLIC_SURFACE_CANON.md — arifOS MCP Public API Contract

> **Status:** SEALED — Canonical 13 + 2 probes
> **Version:** 2026.04.30-KANON
> **Live Endpoint:** `https://mcp.arif-fazil.com/mcp` (streamable-http)
> **Health:** `https://mcp.arif-fazil.com/health`

---

## The One Rule

> **All public integrations MUST use `arif_*` tool names only.**
> `arifos_*` names are internal implementation engines.
> Legacy names (`init_anchor`, `agi_mind`, `apex_soul`, etc.) are historical artifacts.

---

## Canonical 13 Tools

These are the only tools exposed on the default public discovery surface.

| # | Tool Name | Stage | Modes | Role |
|---|-----------|-------|-------|------|
| 1 | `arif_session_init` | 000_INIT | `init`, `resume`, `validate`, `epoch_open`, `epoch_seal` | Session anchor + identity binding |
| 2 | `arif_sense_observe` | 111_SENSE | `search`, `ingest`, `compass`, `atlas`, `entropy_dS`, `vitals` | Reality grounding |
| 3 | `arif_evidence_fetch` | 111_SENSE | `fetch` | Evidence-preserving web ingestion |
| 4 | `arif_mind_reason` | 333_MIND | `reason`, `reflect`, `verify`, `critique`, `debate`, `socratic`, `plan`, `plan_review`, `plan_ready`, `axioms` | Constitutional reasoning |
| 5 | `arif_kernel_route` | 444_KERNEL | `route`, `stage`, `lane`, `list`, `status` | Metabolic orchestration |
| 6 | `arif_reply_compose` | 444r_REPLY | `compose` | Message composition |
| 7 | `arif_memory_recall` | 555_MEMORY | `recall`, `store`, `get`, `list`, `prune`, `search`, `context`, `dry_run` | Vector + associative memory |
| 8 | `arif_heart_critique` | 666_HEART | `critique`, `simulate`, `empathize`, `redteam`, `maruah`, `deescalate`, `summary` | Ethical risk assessment |
| 9 | `arif_gateway_connect` | 666g_GATEWAY | `route`, `discover`, `handshake`, `relay` | Cross-agent federation |
| 10 | `arif_ops_measure` | 777_OPS | `health`, `vitals`, `cost`, `predict` | Thermodynamic telemetry |
| 11 | `arif_judge_deliberate` | 888_JUDGE | `judge`, `compare`, `history`, `explain` | Constitutional arbitration |
| 12 | `arif_vault_seal` | 999_VAULT | `seal`, `verify`, `chain`, `list`, `dry_run` | Immutable ledger anchoring |
| 13 | `arif_forge_execute` | 010_FORGE | `engineer`, `query`, `write`, `generate`, `commit`, `recall`, `dry_run` | Metabolic execution |

### Diagnostic / Probe Tools

| Tool | Purpose |
|------|---------|
| `arif_ping` | Lightweight health probe (no session required) |
| `echo` | Echo message (debug only, disabled in production) |

---

## Golden Path

```
arif_session_init
    → arif_sense_observe / arif_evidence_fetch
    → arif_mind_reason
    → arif_heart_critique
    → arif_judge_deliberate
    → arif_vault_seal
```

`arif_forge_execute` may only run after a `SEAL` verdict from `arif_judge_deliberate`.

---

## MCP Call Examples

### Initialize Session
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "arif_session_init",
    "arguments": {
      "mode": "init",
      "actor_id": "arif"
    }
  }
}
```

### Sense (Grounded Search)
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "arif_sense_observe",
    "arguments": {
      "mode": "search",
      "query": "constitutional AI governance frameworks",
      "actor_id": "arif"
    }
  }
}
```

### Judge (Dry Run)
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "arif_judge_deliberate",
    "arguments": {
      "mode": "dry_run",
      "candidate": "deploy updated kernel to production",
      "actor_id": "arif"
    }
  }
}
```

---

## Transport Details

| Property | Value |
|----------|-------|
| Protocol | MCP 2025-03-26 |
| Transport | streamable-http (FastMCP 3.2+) |
| Endpoint | `POST /mcp` |
| Required Headers | `Accept: application/json, text/event-stream`, `mcp-session-id: <uuid>` |
| Health | `GET /health` |
| Metadata | `GET /.well-known/mcp/server.json` |

**Note:** STDIO transport was removed in KANON to eliminate stdin/stdout attack surface.

---

## Legacy Name Migration Guide

| Legacy Name | Current Canonical Name |
|-------------|------------------------|
| `arifos_init` | `arif_session_init` |
| `arifos_sense` | `arif_sense_observe` |
| `arifos_mind` | `arif_mind_reason` |
| `arifos_kernel` | `arif_kernel_route` |
| `arifos_heart` | `arif_heart_critique` |
| `arifos_ops` | `arif_ops_measure` |
| `arifos_judge` | `arif_judge_deliberate` |
| `arifos_memory` | `arif_memory_recall` |
| `arifos_vault` | `arif_vault_seal` |
| `arifos_forge` | `arif_forge_execute` |
| `arifos_gateway` | `arif_gateway_connect` |
| `init_anchor` | `arif_session_init` |
| `agi_mind` | `arif_mind_reason` |
| `asi_heart` | `arif_heart_critique` |
| `apex_soul` / `apex_judge` | `arif_judge_deliberate` |
| `vault_ledger` | `arif_vault_seal` |
| `physics_reality` | `arif_sense_observe` |
| `math_estimator` | `arif_ops_measure` |

---

## Source of Truth Hierarchy

1. **Live runtime:** `/health` and `/tools` on the deployed server
2. **Registry file:** `arifosmcp/tool_registry.json`
3. **Public contract:** `PUBLIC_SURFACE_CANON.md` (this file)
4. **Code:** `arifosmcp/runtime/tools.py` (canonical handlers)

If any of these disagree, **live runtime wins** on behavior, **this document wins** on intent.

---

## Response Contract (v2026.05.02 — Post-Partial-SEAL Patch)

This section records the stabilized behavioral guarantees added in the v2026.05.02 patch.

### `nine_signal` Guarantee

All tool responses — including `HOLD`, `SEAL`, `SABAR`, and `VOID` — carry a `nine_signal` block:

```json
"nine_signal": {
  "delta":  "KUKUH" | "GANTUNG",
  "psi":    "DITERIMA" | "GANTUNG",
  "omega":  "BIJAK" | "SESAT",
  "overall": "SELAMAT" | "RETAK" | "SABAR"
}
```

- **Success (OK/SEAL):** `delta=KUKUH`, `psi=DITERIMA`, `omega=BIJAK`, `overall=SELAMAT`
- **Halt (HOLD/VOID):** `delta=GANTUNG`, `psi=GANTUNG`, `omega=SESAT`, `overall=RETAK`
- **Conditional (SABAR):** `delta=GANTUNG`, `psi=GANTUNG`, `omega=BIJAK`, `overall=SABAR`

This applies to all 13 canonical tools. Any tool returning without this block should be treated as a kernel anomaly.

### `reversibility_state` on `arif_judge_deliberate`

Every `SEAL` verdict from `arif_judge_deliberate` includes an actively-populated `reversibility_state`:

```json
"reversibility_state": {
  "state":               "REVERSIBLE" | "IRREVERSIBLE" | "CATASTROPHIC",
  "requires_human_seal": true | false,
  "external_effect":    true | false,
  "vault_committed":    true | false
}
```

- **Derivation:** `state` is mapped from the threat-derived `IrreversibilityLevel` (NONE→REVERSIBLE, LOW→SEMI_IRREVERSIBLE, HIGH→IRREVERSIBLE, CRITICAL→CATASTROPHIC). It is **not** hardcoded to `irreversible`.
- **No contradiction rule:** `judge_contract.irreversibility_level` and `reversibility_state.state` must agree. A verdict with `irreversibility_level=irreversible` must have `state=IRREVERSIBLE`.

### `arif_forge_execute` F11 Exemption for Read-Only Modes

`query`, `recall`, and `dry_run` modes of `arif_forge_execute` are classified as **read-only** and do not trigger F11 AUTH even when `session_id` and `actor_id` are absent. These modes:

- Carry `nine_signal` on both OK and HOLD paths
- Do NOT mutate state or write to the ledger
- Remain under F02/F03/F04/F12 (truth, witness, clarity, injection) — those floors are never bypassed

`engineer`, `write`, `generate`, and `commit` modes retain full F11 AUTH enforcement.

### Regression Tests

| File | What It Tests |
|------|---------------|
| `tests/runtime/test_judge_reversibility.py` | No irreconcilable `irreversibility_level` vs `reversibility_state`; `nine_signal` on SEAL |
| `tests/runtime/test_forge_ninesignal.py` | `nine_signal` on all FORGE modes including engineer HOLD; no F11 on query/recall/dry_run |
| `tests/runtime/test_memory_asyncpg.py` | `asyncpg` importable; `arif_memory_recall` no ImportError; `nine_signal` present |

---

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
9 SEAL ALIVE*
�� 999 SEAL ALIVE*
