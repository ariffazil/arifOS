# TOOL_INVENTORY.md — arifOS MCP Tool Audit
**Generated:** 2026-05-25
**Total tools:** 72 (Gateway:2 + Kernel:13 + GEOX:11 + WEALTH:32 + WELL:14)
**Implementation status:** 100% STUBS — no real system calls

---

## GATEWAY (2 tools) — All STUBS

| Tool | Stage | Risk | mutates_state | requires_ack | Status |
|------|-------|------|--------------|-------------|--------|
| `mcp_health_check` | Ω | C1 | NO | NO | STUB — returns hardcoded `alive` |
| `mcp_drift_check` | Ω | C1 | NO | NO | STUB — `registered = 72` hardcoded, no real count |

---

## KERNEL (13 tools) — All STUBS

| Tool | Stage | Floor | Risk | mutates_state | requires_ack | Status |
|------|-------|-------|------|--------------|-------------|--------|
| `arif_session_init` | 000 | F01,F11,F12 | C3 | NO | NO | STUB — returns fake session_id |
| `arif_sense_observe` | 111 | F02 | C1 | NO | NO | STUB — returns `signal_tau: 0.96` |
| `arif_evidence_fetch` | 222 | F02,F03 | C2 | NO | NO | STUB — returns placeholder content |
| `arif_mind_reason` | 333 | F02,F07,F10 | C2 | NO | NO | STUB — returns fake axioms |
| `arif_heart_critique` | 444 | F05,F06 | C2 | NO | NO | STUB — returns `empathy_score: 0.82` |
| `arif_reply_compose` | 444r | F04,F06,F09 | C1 | NO | NO | STUB — echoes input |
| `arif_kernel_route` | 555 | F01,F04 | C2 | NO | NO | STUB — returns input as target |
| `arif_memory_recall` | 555m | F01,F08 | C2 | NO | NO | STUB — returns `memories: []` |
| `arif_forge_execute` | 666 | F01,F11,F13 | **C5** | **YES** | **YES** | STUB — has F01 ack guard but fake execution |
| `arif_gateway_connect` | 666g | F01,F03 | C2 | NO | NO | STUB — returns hardcoded organ list |
| `arif_ops_measure` | 777 | F04 | C1 | NO | NO | STUB — returns `g_score: 0.85` |
| `arif_judge_deliberate` | 888 | F11,F13 | **C4** | **YES** | **YES** | STUB — always returns SEAL |
| `arif_vault_seal` | 999 | F01,F11,F13 | **C5** | **YES** | **YES** | STUB — has F01 ack guard but fake hash |

**Critical kernel findings:**
- 3 tools are C4-C5 (require explicit ack): arif_forge_execute, arif_judge_deliberate, arif_vault_seal
- All 13 kernel tools have correct FLOOR annotations but fake implementations
- No actual session tracking (no Redis, no postgres)

---

## GEOX (11 tools) — All STUBS

| Tool | Floor | Risk | mutates_state | Status |
|------|-------|------|--------------|--------|
| `geox_data_ingest_bundle` | F02 | C2 | NO | STUB — returns hardcoded bundle_id |
| `geox_data_qc_bundle` | F02,F04 | C1 | NO | STUB |
| `geox_dst_ingest_test` | F02 | C2 | NO | STUB |
| `geox_evidence_reason` | F02,F10 | C2 | NO | STUB |
| `geox_map_context_scene` | F02 | C2 | NO | STUB |
| `geox_seismic_compute` | F02 | C2 | NO | STUB |
| `geox_sequence_interpret` | F02 | C2 | NO | STUB |
| `geox_subsurface_generate_candidates` | F02 | C2 | NO | STUB — returns empty list |
| `geox_subsurface_verify_integrity` | F02,F04 | C1 | NO | STUB |
| `geox_prospect_evaluate` | F02,F05 | C2 | NO | STUB |
| `geox_system_registry_status` | F01 | C1 | NO | STUB |

**GEOX findings:**
- No real geological data processing
- No connection to live GEOX MCP at port 8081
- Should proxy to live geox_eic container

---

## WEALTH (32 tools) — All STUBS (1 partial)

| Category | Count | Notes |
|----------|-------|-------|
| Macro/Signal | 14 | All return hardcoded values |
| Time/Value | 11 | All return hardcoded financial metrics |
| Governance/Execution | 8 | `wealth_ledger_write` has real F01 ack guard |

**WEALTH findings:**
- `wealth_ledger_write` has partial real implementation (ack_irreversible check)
- `wealth_gravity_dscr` computes real math (dscr = ebitda/debt_service) — partial real
- No connection to live WEALTH MCP at port 8082
- No actual capital ledger

---

## WELL (14 tools) — All STUBS

| Tool | Floor | Notes |
|------|-------|-------|
| Homeostasis (7) | F05,F06,F08 | All return hardcoded vitality scores |
| Ontological (7) | F05,F06,F10 | All return hardcoded status |

**WELL findings:**
- No real biological/homeostasis data
- No connection to live WELL MCP at port 8083
- Should proxy to live well container

---

## Risk Classification Summary

| Risk Class | Count | Tools | Requires Ack |
|-----------|-------|-------|-------------|
| C1 (low) | 32 | Most gateway, ops, read tools | NO |
| C2 (medium) | 31 | Most GEOX, WEALTH, observation | NO |
| C3 (high) | 1 | arif_session_init | NO |
| C4 (critical) | 1 | arif_judge_deliberate | YES |
| C5 (irreversible) | 2 | arif_forge_execute, arif_vault_seal | YES |
| Unknown | 5 | wealth_ledger_write + others | CONDITIONAL |

---

## What Needs Real Implementation

1. **Kernel tools (13)** — wire to live arifOS MCP at 8088 via HTTP
2. **GEOX tools (11)** — proxy to live GEOX MCP at 8081
3. **WEALTH tools (32)** — proxy to live WEALTH MCP at 8082
4. **WELL tools (14)** — proxy to live WELL MCP at 8083
5. **mcp_drift_check** — compute real registered tool count from FastMCP registry
6. **Memory tools** — implement honest status: healthy/degraded/unavailable
7. **Vault tools** — implement real VAULT999 ledger writes

---

## Action Plan

| Priority | Action | Target |
|----------|--------|--------|
| P0 | Install FastMCP | `uv pip install fastmcp` |
| P0 | Fix STDIO transport | Make server start without errors |
| P1 | Wire kernel tools | Call live 8088 server from arifos_mcp |
| P1 | Wire organ proxies | GEOX→8081, WEALTH→8082, WELL→8083 |
| P2 | Implement real mcp_drift_check | Count actual registered tools |
| P2 | Add canonical envelope | All tools return same shape |
| P3 | Add constitutional middleware | Risk classification per call |

*Ditempa Bukan Diberi — Intelligence is forged, not given.*
