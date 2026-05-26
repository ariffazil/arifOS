# PHOENIX72_GAP_MATRIX.md — Tool Gap Analysis
**Date:** 2026-05-25
**Principle:** A tool is ALIVE only when all 7 conditions pass

---

## The 7 Aliveness Conditions

| # | Condition | Required For |
|---|-----------|--------------|
| 1 | In manifest (tools.json) | All 72 tools |
| 2 | Registered in FastMCP | All 72 tools |
| 3 | Valid input/output schema | All 72 tools |
| 4 | Governance mapped (floors, EMD, Trinity) | All 72 tools |
| 5 | Callable via STDIO | All 72 tools |
| 6 | Returns canonical envelope | All 72 tools |
| 7 | Drift-clean (mcp_drift_check = 0) | All 72 tools |

**A tool with code but failing any condition = NOT ALIVE = STUB**

---

## Tool Count Target vs Reality

| Organ | PHOENIX Target | In Manifest? | Registered? | Schema? | Callable? | Envelope? | Alive? |
|-------|---------------|-------------|------------|---------|-----------|-----------|--------|
| GATEWAY | 2 | NO | NO | NO | NO | NO | 0/2 |
| KERNEL | 13 | NO | NO | NO | NO | NO | 0/13 |
| GEOX | 11 | NO | NO | NO | NO | NO | 0/11 |
| WEALTH | 32 | NO | NO | NO | NO | NO | 0/32 |
| WELL | 14 | NO | NO | NO | NO | NO | 0/14 |
| **TOTAL** | **72** | **0** | **0** | **0** | **0** | **0** | **0/72** |

**Gap: 72 tools needed, 0 alive. Distance: 100% stub.**

---

## GATEWAY Tools (2) — Gap Detail

| Tool | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|------|-----------|-------------|------------|---------|---------|-----------|-------|--------|
| `mcp_health_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `mcp_drift_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |

**Gateway gap:** No manifest. No registration. Stub returns hardcoded string.

---

## KERNEL Tools (13) — Gap Detail

| Tool | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|------|-----------|-------------|------------|---------|---------|-----------|-------|--------|
| `arif_session_init` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_sense_observe` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_evidence_fetch` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_mind_reason` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_kernel_route` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_reply_compose` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_memory_recall` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_heart_critique` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_gateway_connect` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_ops_measure` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_judge_deliberate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_vault_seal` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `arif_forge_execute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |

**Kernel gap:** 13/13 stubs. Live 8088 has equivalents for all 13 but they're NOT wired to arifos_mcp.

**Live 8088 kernel tools (18 total):**
1. `arif_session_init` ← maps to KERNEL 000
2. `arif_sense_observe` ← maps to KERNEL 111
3. `arif_evidence_fetch` ← maps to KERNEL 222
4. `arif_mind_reason` ← maps to KERNEL 333
5. `arif_kernel_route` ← maps to KERNEL 444
6. `arif_reply_compose` ← maps to KERNEL 444r
7. `arif_memory_recall` ← maps to KERNEL 555
8. `arif_heart_critique` ← maps to KERNEL 666
9. `arif_gateway_connect` ← maps to GATEWAY 666
10. `arif_ops_measure` ← maps to KERNEL 777
11. `arif_judge_deliberate` ← maps to KERNEL 888
12. `arif_vault_seal` ← maps to KERNEL 999
13. `arif_forge_execute` ← maps to KERNEL FORGE
14. `arif_stack_health_probe` ← extra (777 OPS)
15. `arif_organ_consensus` ← extra (F03 WITNESS)
16. `arif_scan_local_instructions` ← extra (F12 GUARD)
17. `arif_session_budget` ← extra (777 OPS)
18. `arif_wiki_*` ← wiki tools (not in PHOENIX-72)

**Key insight:** Live 8088 already has the kernel logic. The gap is that arifos_mcp stubs don't proxy to 8088 — they just return dummy strings.

---

## GEOX Tools (11) — Gap Detail

| Tool | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|------|-----------|-------------|------------|---------|---------|-----------|-------|--------|
| `geox_data_ingest` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_data_qc` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_evidence_reason` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_prospect_evaluate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_map_context` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_system_registry` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_health_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_drift_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_physics9_consistency` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `geox_volumetrics_calculate` | NO | stub | NO | NO | NO | NO | NOT ALIVE |
| `geox_acrisk_score` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |

**GEOX gap:** Port 8081 not listening. No live GEOX MCP. All 11 tools must return DEGRADED honest responses until organ is federated.

---

## WEALTH Tools (32) — Gap Detail

| Tool | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|------|-----------|-------------|------------|---------|---------|-----------|-------|--------|
| `wealth_npv_compute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_irr_compute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_emv_compute` | NO | stub | NO | NO | NO | NO | NOT ALIVE |
| `wealth_runway_calculate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_liquidity_assess` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_debt_service_ratio` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_capital_allocation` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_boundary_governance` | NO | stub | NO | NO | NO | NO | NO | **HOLD-FORGE** |
| `wealth_ledger_write` | NO | stub | NO | NO | NO | NO | NO | **HOLD-FORGE** |
| `wealth_entropy_calculate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_kappa_r_compute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_g_score_compute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_ledger_verify` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_portfolio_rebalance` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_risk_return_profile` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_discount_rate_sensitivity` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_production_forecast` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_cost_profile_estimate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_capitalx_compute` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_maruah_score` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_system_registry` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_health_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_drift_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_boundary_monitor` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_governance_status` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_telemetry_status` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_vault_status` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_epistemic_guard` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_correlation_monitor` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_policy_evaluate` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `wealth_policy_apply` | NO | stub | NO | NO | NO | NO | NO | **HOLD-FORGE** |
| `wealth_capital_coherence_test` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |

**WEALTH gap:** Port 8082 not listening. 30/32 tools DEGRADED. 2 Forge tools (ledger_write, boundary_governance) HOLD — require explicit ack.

---

## WELL Tools (14) — Gap Detail

| Tool | Manifest? | Implemented? | Registered? | Schema? | Floors? | Envelope? | Test? | Alive? |
|------|-----------|-------------|------------|---------|---------|-----------|-------|--------|
| `well_homeostasis_assess` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_vitality_score` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_reliability_score` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_fatigue_risk_detect` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_guard_dignity` | NO | stub | NO | NO | NO | NO | NO | **HOLD-FORGE** |
| `well_check_repair` | NO | stub | NO | NO | NO | NO | NO | **HOLD-FORGE** |
| `well_substrate_boundary` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_human_load_assess` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_dignity_shadow_score` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_system_registry` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_health_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_drift_check` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_calibration_status` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |
| `well_telemetry_status` | NO | stub | NO | NO | NO | NO | NO | NOT ALIVE |

**WELL gap:** Port 8083 not listening. 12/14 tools DEGRADED. 2 Forge tools HOLD — require explicit ack.

---

## ORGAN STATUS SUMMARY

| Organ | Port | Listening? | Tools Needed | Tools Alive | Status |
|-------|------|------------|-------------|-------------|--------|
| arifOS MCP (KERNEL proxy) | 8088 | YES | 13 | 0 (not wired) | DEGRADED — code exists in 8088, not proxied |
| GEOX | 8081 | NO | 11 | 0 | NOT REACHABLE — need organ server |
| WEALTH | 8082 | NO | 32 | 0 | NOT REACHABLE — need organ server |
| WELL | 8083 | NO | 14 | 0 | NOT REACHABLE — need organ server |
| AAA | 3001 | NO | 2 | 0 | NOT REACHABLE — AAA server not running |

**Total reachable organs: 1/5 (arifOS MCP only)**

---

## RESOURCES GAP (18 needed)

| Resource | Organ | Implemented? | Registered? | Accessible? |
|----------|-------|-------------|------------|-------------|
| `kernel://doctrine/constitution` | KERNEL | NO | NO | NO |
| `kernel://doctrine/floors` | KERNEL | NO | NO | NO |
| `kernel://registry/tools` | KERNEL | NO | NO | NO |
| `kernel://registry/model-registry` | KERNEL | NO | NO | NO |
| `geox://doctrine/physics9` | GEOX | NO | NO | NO |
| `geox://registry/datasets` | GEOX | NO | NO | NO |
| `geox://schemas/geoscience-io` | GEOX | NO | NO | NO |
| `geox://evidence/store` | GEOX | NO | NO | NO |
| `wealth://doctrine/valuation` | WEALTH | NO | NO | NO |
| `wealth://formulas/finance-core` | WEALTH | NO | NO | NO |
| `wealth://schemas/deal-and-capital` | WEALTH | NO | NO | NO |
| `wealth://evidence/store` | WEALTH | NO | NO | NO |
| `well://vitality/current` | WELL | NO | NO | NO |
| `well://doctrine/substrate-boundary` | WELL | NO | NO | NO |
| `well://calibration/thresholds` | WELL | NO | NO | NO |
| `well://evidence/store` | WELL | NO | NO | NO |
| `aaa://registry/agents` | AAA | NO | NO | NO |
| `aaa://registry/capabilities` | AAA | NO | NO | NO |

**Resources gap: 0/18 implemented. All missing.**

---

## PROMPTS GAP (9 needed)

| Prompt | Purpose | Implemented? | Registered? |
|--------|---------|-------------|-------------|
| RAF | Read Aesthetics Framework | NO | NO |
| TEOF | Thermodynamics of Opinion Formation | NO | NO |
| A-PROMPT | Abstraction Prompt | NO | NO |
| Prompt Master | Master orchestration prompt | NO | NO |
| Commitment Protocol | Binding commitment pattern | NO | NO |
| A2A Negotiation | Agent-to-agent negotiation | NO | NO |
| Operator Handoff | Human↔AI handoff | NO | NO |
| Crisis Fallback | Emergency descent pattern | NO | NO |
| Migration/Recovery | System recovery prompt | NO | NO |

**Prompts gap: 0/9 implemented. All missing.**

---

## CRITICAL PATH (What unblocks what)

```
Step 1: CREATE manifests/tools.json, resources.json, prompts.json
  ↓ unblocks: drift_check becomes possible

Step 2: WIRE arifos_mcp kernel tools to live 8088 (HTTP proxy)
  ↓ unblocks: 13 kernel tools become alive

Step 3: CREATE organ proxy files (geox_proxy.py, wealth_proxy.py, well_proxy.py)
  ↓ unblocks: organ tools return DEGRADED honest instead of stub

Step 4: IMPLEMENT canonical envelope in all 72 tools
  ↓ unblocks: consistent response format

Step 5: ADD mcp_drift_check real implementation
  ↓ unblocks: manifest validation

Step 6: WRITE acceptance tests for all 72 tools
  ↓ unblocks: prove aliveness

Step 7: SEAL manifest hash
  ↓ unblocks: production deployment
```

**If you skip Step 1, nothing else can be verified as correct.**

---

## FINAL SCORECARD

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| Tools in manifest | 72 | 0 | 72 missing |
| Tools registered | 72 | 0 | 72 missing |
| Tools with valid schema | 72 | 0 | 72 missing |
| Tools with governance mapping | 72 | 0 | 72 missing |
| Tools callable via STDIO | 72 | 0 | 72 missing |
| Tools returning canonical envelope | 72 | 0 | 72 missing |
| Tools drift-clean | 72 | 0 | 72 missing |
| Tools fully alive | 72 | 0 | 72 not alive |
| Resources in manifest | 18 | 0 | 18 missing |
| Prompts in manifest | 9 | 0 | 9 missing |
| Live organ servers reachable | 3 | 0 | 3 unreachable |
| Kernel tools proxied to live 8088 | 13 | 0 | 13 not proxied |

**Conclusion: PHOENIX-72 is at 0% completion. This is a greenfield build with existing stubs as reference material, not a migration.**
