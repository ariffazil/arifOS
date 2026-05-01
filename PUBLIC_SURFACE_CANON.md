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
| 4 | `arif_mind_reason` | 333_MIND | `reason`, `reflect`, `verify`, `critique`, `debate`, `socratic`, `plan`, `plan_review`, `plan_approve`, `axioms` | Constitutional reasoning |
| 5 | `arif_kernel_route` | 444_KERNEL | `route`, `stage`, `lane`, `list`, `status` | Metabolic orchestration |
| 6 | `arif_reply_compose` | 444r_REPLY | `compose` | Message composition |
| 7 | `arif_memory_recall` | 555_MEMORY | `recall`, `store`, `get`, `list`, `prune`, `search`, `context`, `dry_run` | Vector + associative memory |
| 8 | `arif_heart_critique` | 666_HEART | `critique`, `simulate`, `empathize`, `redteam`, `maruah`, `deescalate`, `summary` | Ethical risk assessment |
| 9 | `arif_gateway_connect` | 666_GATEWAY | `route`, `discover`, `handshake`, `relay` | Cross-agent federation |
| 10 | `arif_ops_measure` | 777_OPS | `health`, `vitals`, `cost`, `predict` | Thermodynamic telemetry |
| 11 | `arif_judge_deliberate` | 888_JUDGE | `judge`, `compare`, `history`, `explain` | Constitutional arbitration |
| 12 | `arif_vault_seal` | 999_VAULT | `seal`, `verify`, `chain`, `list` | Immutable ledger anchoring |
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

*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
