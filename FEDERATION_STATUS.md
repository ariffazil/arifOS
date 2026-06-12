# FEDERATION_STATUS.md — arifOS Federation Live Status

> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-06-12
> **Rule:** All other repo READMEs must point here for live/degraded/disabled status.
> **Contract:** See `FEDERATION_CONTRACT.md` for organ boundaries and invariants.

---

## Federation Organ Status

| Organ | Repo | Port | Status | Tools | Notes |
|-------|------|------|--------|-------|-------|
| **arifOS** (Kernel) | `ariffazil/arifOS` | 8088 | ✅ OPERATIONAL | 13 canonical | F1-F13 active, 888 JUDGE, VAULT999 |
| **AAA** (Cockpit) | `ariffazil/AAA` | 3001 | ✅ OPERATIONAL | — | React 19 + A2A gateway |
| **GEOX** (Earth) | `ariffazil/geox` | 8081 | ✅ OPERATIONAL | 33 canonical | Apache-2.0 licensed |
| **WEALTH** (Capital) | `ariffazil/wealth` | 18082 | ✅ OPERATIONAL | 20 public + 34 hidden | AGPL-3.0 |
| **WELL** (Vitality) | `ariffazil/well` | 18083 | ✅ OPERATIONAL | 17 somatic | REFLECT_ONLY, state EXPIRED |
| **A-FORGE** (Forge) | `ariffazil/A-FORGE` | 7071 | ✅ OPERATIONAL | — | TypeScript execution shell |
| **APEX** (888 Judge) | `ariffazil/apex` | 3002 | ⚠️ LEGACY | — | Decommissioned — deliberation in AAA a2a |
| **OpenClaw** (Gateway) | — | 18789 | ✅ OPERATIONAL | — | A2A mesh gateway |

## Federation Contract Compliance

| Organ | CONTRACT | GENESIS | CONTEXT | RUNBOOK | AGENTS |
|-------|----------|---------|---------|---------|--------|
| arifOS | ✅ | ✅ 000 | ✅ | ✅ | ✅ |
| GEOX | ✅ | ✅ 000-003 | ❌ | ❌ | ✅ |
| WEALTH | ✅ | ❌ | ❌ | ❌ | ✅ |
| WELL | ✅ | ✅ 004-010 | ❌ | ❌ | ✅ |
| A-FORGE | ✅ | ❌ | ❌ | ❌ | ✅ |
| AAA | ✅ | ❌ | ❌ | ❌ | ✅ |

## GENESIS Canon Chain

| Number | Owner | Title |
|--------|-------|-------|
| 000 | arifOS | Kernel Canon |
| 001-002 | arifOS | Reserved (Three Kernels, Sole Witness) |
| 003 | GEOX | Constitutional Alignment |
| 004-010 | WELL | 13-Canon through Persona |
| 011+ | — | Reserved for WEALTH, A-FORGE, AAA |

## Known Gaps

| Issue | Severity | Detail |
|-------|----------|--------|
| Runtime Drift | ⚠️ MEDIUM | arifOS build=52fccbb, live=e799391 — container stale by 4 commits |
| WEALTH raw/CONSTITUTION.md | 🔴 HIGH | Stale "AGI-bot v63" duplicate with wrong floor numbering — needs removal |
| GEOX GENESIS/003 | ⚠️ MEDIUM | Floor numbering uses old F01-F09 mapping — needs realignment to F1-F13 |
| WELL state.json | ⚠️ MEDIUM | truth_status=EXPIRED — F13 sovereign territory |
| APEX decommission | 🟡 LOW | apex-prime.service still running on 3002 for legacy health probe |
| GENESIS/ missing | 🟡 LOW | WEALTH, A-FORGE, AAA still need GENESIS/ stubs |
| CONTEXT/RUNBOOK | 🟡 LOW | Missing from GEOX, WEALTH, WELL, A-FORGE, AAA |

## Infrastructure

| Service | Port | Status |
|---------|------|--------|
| PostgreSQL 16 + pgvector | 5432 | ✅ Running |
| Redis 7 | 6379 | ✅ Running |
| Qdrant | 6333 | ✅ Running |
| FalkorDB (Graphiti L5) | 6380 | ✅ Running |
| Temporal | 7233 | ✅ Running |
| Caddy 2 | 80/443 | ✅ Running |
| Prometheus | 9090 | ✅ Running |
| Grafana | 3000 | ✅ Running |
| NATS + JetStream | 4222 | ✅ Running |
| Cloudflare Tunnel | — | ✅ 4 QUIC connections |

## Ingress (Public Endpoints)

| Site | Via | Backend |
|------|-----|---------|
| `arifos.arif-fazil.com/mcp` | Cloudflare Tunnel | arifOS:8088 |
| `geox.arif-fazil.com/mcp` | Cloudflare Tunnel | GEOX:8081 |
| `wealth.arif-fazil.com/mcp` | Cloudflare Tunnel | WEALTH:18082 |
| `well.arif-fazil.com/mcp` | Cloudflare Tunnel | WELL:18083 |
| `aaa.arif-fazil.com` | Caddy | AAA:3001 |
| `arif-fazil.com` | Caddy | Static site |

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
