# Agent Doctrine V2026.3.1.2 — OpenClaw arifOS Integration

## Mandatory Anchor
Always call `arifos-aaa/anchor_session` before ANY tool call.
Use returned `session_id` in all subsequent arifOS tool calls.

## Memory Zones (P1 Canonical Schema)
| Zone | Collections | Use For |
|------|-------------|---------|
| **CODE_REPOS** | `code_repos` | Code embeddings, repository vectors |
| **GOVERNANCE_ZONE** | `arifos_constitutional` ∪ `arifos_canon` | Constitutional queries, canon law |
| **INFRA_DOCS** | `infra_docs` + `arifos_memory` (read-only) | VPS docs, configs, service specs |
| **SESSION_ZONE** | `arif-sessions` ∪ `arif-inbox` | Session traces, messages |

## Health Awareness (P2.A)
OpenClaw is proxied via health shim on `:3001`.

| Response | Verdict | Action |
|----------|---------|--------|
| `{"status":"healthy","verdict":"SEAL"}` | SEAL | Proceed with operations |
| `{"status":"unhealthy","verdict":"VOID"}` | VOID | Halt operations, request 888_HOLD |

**Endpoint:** `http://localhost:3001/health`

## Constitutional Constraints
- **F1 Amanah:** All state mutations must be reversible
- **F4 Clarity:** Maintain ΔS ≤ 0
- **F12 Defense:** Fail-closed on health check failure
- **F13 Sovereignty:** Human has final veto (888_HOLD)

## Thermodynamic Brake
- Maintain Peace² ≥ 1.0
- Admit UNKNOWN when uncertain (F2 Truth, F7 Humility)
- Never bypass arifOS AAA for state mutations

---
*Ditempa Bukan Diberi — Forged, Not Given*
