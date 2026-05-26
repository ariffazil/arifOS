# TOOL_LIFECYCLE_STATUS.md — Tool-by-Tool Accountability
**Date:** 2026-05-25
**Principle:** Every tool has one owner, one stage, one risk class. No tool may exist without these.

---

## How to Read This Document

Each tool has a **Lifecycle Stage**:

| Stage | Meaning |
|-------|---------|
| STUB | Code exists, returns dummy data, not wired |
| PROXIED | Wires to live server, returns real or DEGRADED data |
| DEGRADED | Live organ unavailable, returns honest unavailable |
| ALIVE | All 7 conditions pass, drift-clean |
| HOLD | Cannot activate — waiting for precondition |
| DELETE | Entropy — to be removed |

---

## GATEWAY (2 tools)

### `mcp_health_check`
- **File:** `tools/canonical/gateway.py`
- **Stage:** STUB
- **Organ:** GATEWAY
- **EMD:** E
- **Trinity:** AGI
- **Floors:** F01, F02
- **Risk Class:** C1 OBSERVE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded `{"status": "ok"}`
- **Missing:** No health check of actual dependencies (8088, organs)
- **Next action:** REFACTOR — check 8088 liveness, return honest DEGRADED if unreachable
- **Blocker:** None

### `mcp_drift_check`
- **File:** `tools/canonical/gateway.py`
- **Stage:** STUB
- **Organ:** GATEWAY
- **EMD:** E
- **Trinity:** AGI
- **Floors:** F01, F02, F03
- **Risk Class:** C1 OBSERVE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded `{"drift_detected": false}`
- **Missing:** No manifest file to compare against
- **Next action:** CREATE `manifests/tools.json` first, then wire to it
- **Blocker:** manifests/tools.json does not exist

---

## KERNEL (13 tools)

### `arif_session_init`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** E
- **Trinity:** AGI
- **Floors:** F01, F11, F12
- **Risk Class:** C2 DECIDE
- **Mutates:** YES (creates session state)
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded session ID
- **Live equivalent (8088):** YES — working at `/tools/arif_session_init`
- **Next action:** PROXY — make HTTP call to 8088, return real response
- **Blocker:** None

### `arif_sense_observe`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** E
- **Trinity:** AGI
- **Floors:** F01, F06
- **Risk Class:** C1 OBSERVE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded `{"senses": ["web_search"]}`
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_evidence_fetch`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** E
- **Trinity:** AGI
- **Floors:** F01, F09
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded evidence stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** Tavily config must be verified

### `arif_mind_reason`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F04
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded reasoning stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_kernel_route`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F04
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded route stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_reply_compose`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F06
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded reply stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_memory_recall`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F05
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded memory stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_heart_critique`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F05, F06
- **Risk Class:** C3 CRITIQUE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded critique stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** SEA-LION model config

### `arif_gateway_connect`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** GATEWAY
- **EMD:** A
- **Trinity:** AGI
- **Floors:** F01, F04
- **Risk Class:** C2 DECIDE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded gateway stub
- **Next action:** PROXY to 8088 (AAA A2A not live, return DEGRADED)
- **Blocker:** AAA A2A server not running

### `arif_ops_measure`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** M
- **Trinity:** AGI
- **Floors:** F01, F07, F08
- **Risk Class:** C1 OBSERVE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded ops stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_judge_deliberate`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** F
- **Trinity:** APEX
- **Floors:** F01, F13
- **Risk Class:** C3 JUDGE
- **Mutates:** NO
- **Requires Ack:** NO
- **Current behavior:** Returns hardcoded verdict stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088
- **Blocker:** None

### `arif_vault_seal`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** V
- **Trinity:** APEX
- **Floors:** F01, F13
- **Risk Class:** C4 SEAL
- **Mutates:** YES (VAULT999 append-only write)
- **Requires Ack:** YES (irreversible)
- **Current behavior:** Returns hardcoded seal stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088, enforce ack gate
- **Blocker:** VAULT999 path must be verified

### `arif_forge_execute`
- **File:** `tools/canonical/kernel.py`
- **Stage:** STUB
- **Organ:** KERNEL
- **EMD:** F
- **Trinity:** AGI
- **Floors:** F01, F07, F08, F13
- **Risk Class:** C4 FORGE
- **Mutates:** YES
- **Requires Ack:** YES (irreversible)
- **Current behavior:** Returns hardcoded forge stub
- **Live equivalent (8088):** YES — working
- **Next action:** PROXY to 8088, enforce ack + judge gate
- **Blocker:** None

---

## GEOX (11 tools) — All DEGRADED (port 8081 not listening)

| Tool | Stage | Blocked By | Notes |
|------|-------|------------|-------|
| `geox_data_ingest` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_data_qc` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_evidence_reason` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_prospect_evaluate` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_map_context` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_system_registry` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_health_check` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_drift_check` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_physics9_consistency` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_volumetrics_calculate` | DEGRADED | Port 8081 unreachable | Return honest unavailable |
| `geox_acrisk_score` | DEGRADED | Port 8081 unreachable | Return honest unavailable |

**Action:** Create `organs/geox_proxy.py` that attempts HTTP call to 8081, catches errors, returns DEGRADED envelope.

---

## WEALTH (32 tools) — All DEGRADED (port 8082 not listening)

| Tool | Stage | Blocked By | Forge? |
|------|-------|------------|--------|
| `wealth_npv_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_irr_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_emv_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_runway_calculate` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_liquidity_assess` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_debt_service_ratio` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_capital_allocation` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_boundary_governance` | **HOLD** | Port 8082 unreachable | YES — C4 |
| `wealth_ledger_write` | **HOLD** | Port 8082 unreachable | YES — C4 |
| `wealth_entropy_calculate` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_kappa_r_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_g_score_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_ledger_verify` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_portfolio_rebalance` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_risk_return_profile` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_discount_rate_sensitivity` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_production_forecast` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_cost_profile_estimate` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_capitalx_compute` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_maruah_score` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_system_registry` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_health_check` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_drift_check` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_boundary_monitor` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_governance_status` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_telemetry_status` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_vault_status` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_epistemic_guard` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_correlation_monitor` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_policy_evaluate` | DEGRADED | Port 8082 unreachable | NO |
| `wealth_policy_apply` | **HOLD** | Port 8082 unreachable | YES — C3 |
| `wealth_capital_coherence_test` | DEGRADED | Port 8082 unreachable | NO |

**Action:** Create `organs/wealth_proxy.py`. 2 HOLD tools must never execute until organ live + explicit ack.

---

## WELL (14 tools) — All DEGRADED (port 8083 not listening)

| Tool | Stage | Blocked By | Forge? |
|------|-------|------------|--------|
| `well_homeostasis_assess` | DEGRADED | Port 8083 unreachable | NO |
| `well_vitality_score` | DEGRADED | Port 8083 unreachable | NO |
| `well_reliability_score` | DEGRADED | Port 8083 unreachable | NO |
| `well_fatigue_risk_detect` | DEGRADED | Port 8083 unreachable | NO |
| `well_guard_dignity` | **HOLD** | Port 8083 unreachable | YES — C3 |
| `well_check_repair` | **HOLD** | Port 8083 unreachable | YES — C3 |
| `well_substrate_boundary` | DEGRADED | Port 8083 unreachable | NO |
| `well_human_load_assess` | DEGRADED | Port 8083 unreachable | NO |
| `well_dignity_shadow_score` | DEGRADED | Port 8083 unreachable | NO |
| `well_system_registry` | DEGRADED | Port 8083 unreachable | NO |
| `well_health_check` | DEGRADED | Port 8083 unreachable | NO |
| `well_drift_check` | DEGRADED | Port 8083 unreachable | NO |
| `well_calibration_status` | DEGRADED | Port 8083 unreachable | NO |
| `well_telemetry_status` | DEGRADED | Port 8083 unreachable | NO |

**Action:** Create `organs/well_proxy.py`. 2 HOLD tools must never execute until organ live + explicit ack.

---

## SUMMARY SCORECARD

| Organ | Total | STUB | PROXIED | DEGRADED | ALIVE | HOLD | DELETE |
|-------|-------|------|---------|----------|-------|------|--------|
| GATEWAY | 2 | 2 | 0 | 0 | 0 | 0 | 0 |
| KERNEL | 13 | 13 | 0 | 0 | 0 | 0 | 0 |
| GEOX | 11 | 0 | 0 | 11 | 0 | 0 | 0 |
| WEALTH | 32 | 30 | 0 | 30 | 0 | 2 | 0 |
| WELL | 14 | 12 | 0 | 12 | 0 | 2 | 0 |
| **TOTAL** | **72** | **57** | **0** | **53** | **0** | **4** | **0** |

**Live wiring path:** 8088 has all 13 kernel equivalents working. arifos_mcp stubs do not proxy to 8088 — they return dummy strings.

**Nearest path to ALIVE:** Proxy kernel tools to 8088. All 13 kernel tools become alive in one step.

**Forbidden actions:** Do not mark DEGRADED tools as ALIVE. Do not remove ack gates from HOLD tools.
