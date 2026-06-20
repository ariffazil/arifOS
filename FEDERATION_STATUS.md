# FEDERATION_STATUS.md — arifOS Federation Live Status

> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-06-20
> **Rule:** All other repo READMEs must point here for live/degraded/disabled status.
> **Contract:** See `FEDERATION_CONTRACT.md` for organ boundaries and invariants.

---

## Federation Organ Status

| Organ | Repo | Port | Status | Tools | Notes |
|-------|------|------|--------|-------|-------|
| **arifOS** (Kernel) | `ariffazil/arifos` | 8088 | ✅ OPERATIONAL | 13 canonical + 35 operational | F1-F13 active, 888 JUDGE, VAULT999; truth unification Phase 1 deployed 2026-06-20 |
| **AAA** (Cockpit) | `ariffazil/aaa` | 3001 | ✅ OPERATIONAL | — | React 19 + A2A gateway |
| **GEOX** (Earth) | `ariffazil/geox` | 8081 | ✅ OPERATIONAL | 40 canonical | Apache-2.0 licensed |
| **WEALTH** (Capital) | `ariffazil/wealth` | 18082 | ✅ OPERATIONAL | 20 public + 34 hidden aliases | AGPL-3.0 |
| **WELL** (Vitality) | `ariffazil/well` | 18083 | ✅ OPERATIONAL | 17 somatic | REFLECT_ONLY |
| **A-FORGE** (Forge) | `ariffazil/A-FORGE` | 7071 | ✅ OPERATIONAL | — | TypeScript execution shell; hosts MIND:51001 + MEMORY:51002 |
| **APEX** (888 Judge) | `ariffazil/apex` | 3002 | ⚠️ LEGACY | — | Legacy health probe — deliberation moved to AAA a2a-server |
| **OpenClaw** (Gateway) | — | 18789 | ✅ OPERATIONAL | — | A2A mesh gateway |

## Federation Contract Compliance

| Organ | CONTRACT | GENESIS | CONTEXT | RUNBOOK | AGENTS |
|-------|----------|---------|---------|---------|--------|
| arifOS | ✅ | ✅ 000 | ❌ | ❌ | ✅ |
| GEOX | ✅ | ✅ 000-009 | ✅ | ✅ | ✅ |
| WEALTH | ✅ | ✅ 011 | ✅ | ✅ | ✅ |
| WELL | ✅ | ✅ 004-010 | ✅ | ✅ | ✅ |
| A-FORGE | ✅ | ✅ symlink | ✅ | ✅ | ✅ |
| AAA | ✅ | ✅ 013 | ✅ | ✅ | ✅ |

## GENESIS Canon Chain

| Number | Owner | Title |
|--------|-------|-------|
| 000 | arifOS | Kernel Canon |
| 001-002 | arifOS | Reserved (Three Kernels, Sole Witness) |
| 003 | GEOX | Constitutional Alignment |
| 004-010 | WELL | 13-Canon through Persona |
| 011 | WEALTH | Capital Mandate |
| 013 | AAA | Cockpit Mandate |
| A-FORGE | A-FORGE | Symlink to `/root/arifOS/GENESIS/000_KERNEL_CANON.md` |

## Known Gaps

| Issue | Severity | Detail |
|-------|----------|--------|
| Runtime Drift | ✅ RESOLVED | build and live stamps aligned after 2026-06-12 deploy |
| WEALTH stale constitution | ✅ RESOLVED | `raw/CONSTITUTION.md` and `archive/AAA_FEDERATION_CONSTITUTION.md` removed; canonical link added |
| GEOX GENESIS/003 | ✅ RESOLVED | Verified aligned to F1–F13; SOT-MANIFEST header added |
| arifOS CONTEXT/RUNBOOK | 🟡 MEDIUM | CONTEXT.md present but stale (2026-06-16); RUNBOOK.md missing |
| arifOS RLS enforcement | 🔴 HIGH | Phase 1 Step 6 — RLS on mcp_servers/policies/projections at 888_HOLD awaiting Arif confirm |
| arifOS test suite (Phase 1 Step 7) | 🟡 MEDIUM | 5 truth-unification tests written, blocked by pre-existing BlastRadius.LOW import bug |
| WELL state.json | ⚠️ MEDIUM | `OPERATOR_DECLARED_STALE` for engineering test phase; fresh biometric input still pending (F13) |
| APEX decommission | 🟡 LOW | `apex-prime.service` still running on 3002 for legacy health probe; marked legacy-only |
| A-FORGE lease gate | 🔴 HIGH | Leases self-issued by A-FORGE; must be kernel-issued — T4 in progress |

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
