# FEDERATION_STATUS.md — arifOS Federation Live Status

> **DEPRECATED TOOL COUNTS (2026-06-23 7-tool facade freeze)**: Many "X tools", "13/15/20 canonical" numbers in this file predate the public collapse to exactly 7 verbs (arif_init, arif_observe, arif_think, arif_route, arif_judge, arif_act, arif_seal). See arifosmcp/runtime/public_surface.py:CANONICAL_7 and scripts/check_reality.py for current truth. Status/organ health data may still be useful.

> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-07-01
> **Valid Until:** 2026-07-31
> **Rule:** All other repo READMEs must point here for live/degraded/disabled status.
> **Contract:** See `FEDERATION_CONTRACT.md` for organ boundaries and invariants.

---

## Federation Organ Status

| Organ | Repo | Port | Status | Tools | Notes |
|-------|------|------|--------|-------|-------|
| **arifOS** (Kernel) | `ariffazil/arifos` | 8088 | ✅ OPERATIONAL | 17 canonical + 41 diagnostic = 58 declared; 7 public verbs; 48 via MCP | F1-F13 active; `/health` healthy; version `kanon-1bcf22d` |
| **AAA** (Cockpit) | `ariffazil/aaa` | 3001 | ✅ OPERATIONAL | — | React 19 + A2A gateway |
| **GEOX** (Earth) | `ariffazil/geox` | 8081 | ✅ OPERATIONAL | 31 canonical | Apache-2.0 licensed; attestation verified 2026-07-01 |
| **WEALTH** (Capital) | `ariffazil/wealth` | 18082 | ✅ OPERATIONAL | 32 live | AGPL-3.0; attestation verified 2026-07-01 |
| **WELL** (Vitality) | `ariffazil/well` | 18083 | ✅ OPERATIONAL | 22 live | `/health` healthy; state_age_hours 9.5; REFLECT_ONLY |
| **A-FORGE** (Forge) | `ariffazil/A-FORGE` | 7071 | ✅ OPERATIONAL | — | TypeScript execution shell; hosts MIND:51001 + MEMORY:51002 |
| **A-FORGE MCP** | `ariffazil/A-FORGE` | 7072 | ✅ OPERATIONAL | 72 tools | Dedicated MCP gateway (`a-forge-mcp.service`); single streamable-http session, stdio preferred for agents |
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
| arifOS tool registry divergence | 🟡 MEDIUM | 12 different ActionClass enums across codebase; PREPARE used in tool_registry.json but not in canonical kernel_envelope.py |
| A-FORGE lease gate | 🔴 HIGH | Leases self-issued by A-FORGE; must be kernel-issued — T4 in progress |
| APEX decommission | 🟡 LOW | `apex-prime.service` still running on 3002 for legacy health probe; marked legacy-only |
| arifOS CONTEXT.md | 🟡 LOW | `CONTEXT.md` referenced by `RUNBOOK.md` but missing from `/root/arifOS`; live state lives in `/root/CONTEXT.md` |

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
| `mcp.arif-fazil.com/mcp` | Cloudflare Tunnel | arifOS:8088 |
| `geox.arif-fazil.com/mcp` | Cloudflare Tunnel | GEOX:8081 |
| `wealth.arif-fazil.com/mcp` | Cloudflare Tunnel | WEALTH:18082 |
| `well.arif-fazil.com/mcp` | Cloudflare Tunnel | WELL:18083 |
| `aaa.arif-fazil.com` | Caddy | AAA:3001 |
| `arif-fazil.com` | Caddy | Static site |

---

**DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**
