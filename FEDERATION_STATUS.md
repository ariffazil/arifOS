# FEDERATION_STATUS.md — arifOS Federation Live Status

> **DEPRECATED TOOL COUNTS (2026-06-23 7-tool facade freeze)**: Many "X tools", "13/15/20 canonical" numbers in this file predate the public collapse to exactly 7 verbs (arif_init, arif_observe, arif_think, arif_route, arif_judge, arif_act, arif_seal). See arifosmcp/runtime/public_surface.py:CANONICAL_7 and scripts/check_reality.py for current truth. Status/organ health data may still be useful.

> **Canonical Source of Truth:** `ariffazil/arifOS`
> **Authority:** arifOS F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Last Verified:** 2026-06-21
> **Rule:** All other repo READMEs must point here for live/degraded/disabled status.
> **Contract:** See `FEDERATION_CONTRACT.md` for organ boundaries and invariants.

---

## Federation Organ Status

| Organ | Repo | Port | Status | Tools | Notes |
|-------|------|------|--------|-------|-------|
| **arifOS** (Kernel) | `ariffazil/arifos` | 8088 | ⚠️ DEGRADED | 20 canonical + 37 diagnostic (total 57 registered) | F1-F13 active; health probe reports DEGRADED_CLAIM (tool_count=0 at crawl — static fallback active); `_static_tools` fix 2026-06-21 |
| **AAA** (Cockpit) | `ariffazil/aaa` | 3001 | ✅ OPERATIONAL | — | React 19 + A2A gateway |
| **GEOX** (Earth) | `ariffazil/geox` | 8081 | ✅ OPERATIONAL | 40 canonical | Apache-2.0 licensed; attestation verified 2026-06-21 |
| **WEALTH** (Capital) | `ariffazil/wealth` | 18082 | ✅ OPERATIONAL | 24 live | AGPL-3.0; attestation verified 2026-06-21 |
| **WELL** (Vitality) | `ariffazil/well` | 18083 | ⚠️ DEGRADED | 15 live | DEGRADED_CLAIM per kernel attestation 2026-06-21; state.json STALE; REFLECT_ONLY |
| **A-FORGE** (Forge) | `ariffazil/A-FORGE` | 7071 | ✅ OPERATIONAL | — | TypeScript execution shell; hosts MIND:51001 + MEMORY:51002 |
| **A-FORGE MCP** | `ariffazil/A-FORGE` | 7072 | ✅ OPERATIONAL | 77 tools | Dedicated MCP gateway (`a-forge-mcp.service`); single streamable-http session, stdio preferred for agents |
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
| arifOS kernel DEGRADED | 🔴 HIGH | Kernel health probe reports DEGRADED_CLAIM; `FederationRegistry._static_tools` missing (fixed 2026-06-21); MCP tools/list crawl returns 0 tools for arifOS |
| arifOS tool registry divergence | 🟡 MEDIUM | 12 different ActionClass enums across codebase; PREPARE used in tool_registry.json but not in canonical kernel_envelope.py |
| WELL state.json stale | ⚠️ MEDIUM | `OPERATOR_DECLARED_STALE` for engineering test phase; fresh biometric input still pending (F13); 15 tools attested live |
| arifOS CONTEXT/RUNBOOK | 🟡 MEDIUM | CONTEXT.md present but stale; RUNBOOK.md missing |
| WEALTH tool count variance | 🟡 LOW | 24 live per MCP attestation vs 54 declared (20 public + 34 aliases) |
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
