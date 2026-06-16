# CONTEXT.md — arifOS (Constitutional Kernel)

> **Organ:** arifOS | **Port:** 8088 / 18081 | **Repo:** `ariffazil/arifos`
> **Authority:** F13 SOVEREIGN (Muhammad Arif Fazil)
> **Last Updated:** 2026-06-16

## Live State

- **Service:** `arifos.service` (MCP, port 8088) + `arifosd.service` (A2A, port 18081)
- **Health:** `http://127.0.0.1:8088/health`
- **Release:** `v2026.05.05-SSCT` / commit `57aa743`
- **Tools:** 13 canonical constitutional tools + 26 operational MCP tools (39 exposed via MCP)
- **Floors:** F1–F13 active
- **Transport:** `streamable-http`
- **Registry truth:** `VERIFIED`

## Federation Role

arifOS is the constitutional kernel. It does not execute domain logic; it judges whether an agent or organ may act.

```text
Arif (F13) → arifOS (judges) → domain organs (evidence) → AAA (display)
  → arifOS SEAL → A-FORGE (executes) → HERMES verify → VAULT999 seal
```

## Current Focus

- T0 Canon Cleanup — align constitution references, remove stale duplicates.
- T4 A-FORGE Lease Gate — ensure A-FORGE cannot mutate without an arifOS-issued lease/judge seal.

## Active Alerts

| Alert | Status | Owner | Note |
|-------|--------|-------|------|
| WELL stale biometric state | `WELL_HOLD` / `INSUFFICIENT_DATA` | F13 | Declared stale for engineering test phase; fresh input pending. |
| APEX legacy service | `legacy-only` | arifOS/AAA | Deliberation moved to AAA a2a-server; service kept for observability. |
| A-FORGE self-issued leases | `T4_IN_PROGRESS` | A-FORGE | Lease authority must come from arifOS, not A-FORGE. |
| VPS load | `CAUTION` | Ops | 15m load ~13 on 8-core; time deploys carefully. |

## Canonical Pointers

- **Constitution:** `static/arifos/theory/000/000_CONSTITUTION.md`
- **Federation contract:** `FEDERATION_CONTRACT.md`
- **Live status:** `FEDERATION_STATUS.md`
- **Operations:** `RUNBOOK.md`
- **Agent landing protocol:** `AGENTS.md`
