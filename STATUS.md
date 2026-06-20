# STATUS.md — arifOS Kernel Live State

> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil)
> **Scope:** arifOS kernel only — for federation-wide status see `FEDERATION_STATUS.md`
> **Last probe:** 2026-06-20T07:30 UTC
> **Update:** Run `curl -s http://localhost:8088/health | python3 -m json.tool` and update this file.

---

## 1. Current Health

| Metric | Value | Source |
|--------|-------|--------|
| **Status** | healthy | `/health` |
| **Version** | kanon-1f4f04e | `/health` |
| **Image** | `ghcr.io/ariffazil/arifos:1f4f04e` | `/health` |
| **Git commit** | 1f4f04e (build) / 75b9da9 (live) | `/health` |
| **Runtime drift** | true — container behind HEAD | `/health` |
| **Transport** | streamable-http | `/health` |
| **Deployment source** | ghcr | `/health` |

## 2. Tool Surface

| Metric | Count |
|--------|-------|
| **Canonical tools** | 13 |
| **Operational tools** | 35 |
| **Total MCP-exposed** | 48 |
| **Input schemas published** | 24 |
| **Output schemas published** | 24 |
| **Contract drift** | false |

**13 canonical tools:** `arif_session_init`, `arif_sense_observe`, `arif_evidence_fetch`, `arif_mind_reason`, `arif_heart_critique`, `arif_judge_deliberate`, `arif_forge_execute`, `arif_vault_seal`, `arif_memory_recall`, `arif_kernel_route`, `arif_ops_measure`, `arif_reply_compose`, `arif_gateway_connect`

## 3. Floor Status

| Floor | Name | Type | Status |
|-------|------|------|--------|
| F1 | AMANAH | HARD | active |
| F2 | TRUTH | HARD | active |
| F3 | TRI-WITNESS | DERIVED | active |
| F4 | CLARITY | HARD | active |
| F5 | PEACE² | SOFT | active |
| F6 | EMPATHY | SOFT | active |
| F7 | HUMILITY | HARD | active |
| F8 | GENIUS | DERIVED | active |
| F9 | ANTIHANTU | HARD | active |
| F10 | ONTOLOGY | HARD | active |
| F11 | AUDITABILITY | HARD | active |
| F12 | RESILIENCE | HARD | active |
| F13 | SOVEREIGN | HARD | active |

**All 13 floors active.** ML floors enabled (sentence-transformers/all-MiniLM-L6-v2). Semantic readiness: healthy. Langfuse tracing: ACTIVE.

## 4. Federation Organs (from arifOS perspective)

| Organ | Port | Status | Probe method |
|-------|------|--------|-------------|
| arifOS | 8088 | ✅ ALIVE | in_process_canonical |
| GEOX | 8081 | ✅ ALIVE | http_mcp_probe |
| WEALTH | 18082 | ✅ ALIVE | http_mcp_probe |
| WELL | 18083 | ✅ ALIVE | http_mcp_probe |
| AAA | 3001 | ✅ ALIVE | http_probe |
| A-FORGE | 7071 | ✅ ALIVE | http_probe |

## 5. Recent Milestones

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-06-20 | **Truth unification Phase 1** — `arif_os_attest`, `arif_organ_attest_all`, `hermes_system_status` unified under `arifosmcp_kernel_state` | ✅ DEPLOYED |
| 2026-06-20 | Single truth source: `public.arifosmcp_kernel_state` table created in Supabase | ✅ DEPLOYED |
| 2026-06-20 | Hermes now declares `probe_type: "tcp_connect"`, `tool_count: null` — no more false MCP counts | ✅ DEPLOYED |
| 2026-06-20 | Empty tools + healthy probe → `PARTIAL_DEGRADED` (not `DEGRADED_CLAIM`) | ✅ DEPLOYED |
| 2026-06-14 | MCP Gate v0 deployed; 25/25 benchmarks pass | ✅ |
| 2026-06-14 | Steel Security Layer active (Trivy, Semgrep, Ruff, Gitleaks) | ✅ |

## 6. Open HOLDs

| ID | Item | Severity | Context |
|----|------|----------|---------|
| HOLD-001 | **RLS enforcement** — Row-Level Security on `mcp_servers`, `mcp_policies`, `mcp_projections` | 🔴 HIGH | Phase 1 Step 6. SQL written. Migration ready. Awaiting Arif confirm. |
| HOLD-002 | **Step 7 tests** — 5 truth-unification tests written, blocked by pre-existing `BlastRadius.LOW` import bug in `tool_self_model.py:140` | 🟡 MEDIUM | Tests exist at `tests/test_truth_surface_unification.py`. Cannot run until BlastRadius enum fixed. |

## 7. Infrastructure (on VPS af-forge)

| Service | Port | Status |
|---------|------|--------|
| arifOS kernel (bare metal) | 8088 | active |
| PostgreSQL 16 + pgvector | 5432 | healthy |
| Redis 7 | 6379 | healthy |
| Qdrant | 6333 | healthy |
| FalkorDB (Graphiti L5) | 6380 | healthy |
| NATS + JetStream | 4222 | healthy |
| Prometheus | 9090 | active |
| Grafana | 3000 | active |
| Cloudflare Tunnel | — | 4 QUIC connections |

## 8. Public Endpoints

| Endpoint | Transport | Purpose |
|----------|-----------|---------|
| `https://arifos.arif-fazil.com/mcp` | Cloudflare Tunnel → :8088 | MCP governance surface |
| `https://arifos.arif-fazil.com/health` | Cloudflare Tunnel → :8088 | Machine-readable health |
| `https://arifos.arif-fazil.com/llms.txt` | Cloudflare Tunnel → :8088 | LLM-readable manifest |

---

*DITEMPA BUKAN DIBERI — Status is observed, not assumed.*
