# arifOS 13-Tool Canonical Manifest v1.0.0

**Status:** SEALED — 2026-04-19  
**Author:** Arif Fazil — Human Architect, Seri Kembangan, MY  
**Version:** 1.0.0  
**Constitutional basis:** F1–F13 · Trinity ΔΩΨ · 000–999 Pipeline  
**Consolidation:** 44 tools → 13 canonical tools (zero capability loss)

---

## Executive Summary

This manifest is the canonical source of truth for the arifOS 13-tool consolidation. It collapses 44 individual tools into 13 governed tools organised across four axes: Constitutional Primordials, Infrastructure Organs, Computation Engines, and Reality Oracles. Every original capability is preserved. The merge respects constitutional physics, maintains orthogonality, and eliminates agent routing ambiguity.

Migration note: existing integrations using old tool names (e.g. `V_npv_evaluate`, `T_petrophysics_compute`) must be migrated via shim layer before hard cutover. See Section V.

---

## I. Constitutional Primordials (5 tools)

These five tools are the metabolic invariants. They cannot be merged further — each represents a distinct pipeline stage in the 000→999 constitutional pipeline. Separation of powers is enforced by design.

### 1. `arifos_init`

| Field | Value |
|---|---|
| Axis | constitutional |
| Role | session_bootstrap |
| Pipeline stage | 000 INIT |
| Invariant | Must run first — all governed tools require active session |

**Description:** Opens a governed session, binds actor identity via JWT or equivalent, issues session token, performs initial safety and intent classification scan.

**Inputs:** `identity_token`, `client_metadata`, `raw_intent`  
**Outputs:** `session_id`, `safety_profile`, `initial_intent_class`

---

### 2. `arifos_sense`

| Field | Value |
|---|---|
| Axis | constitutional |
| Role | reality_grounding |
| Pipeline stage | 111 SENSE |
| Invariant | All claims must pass through grounding before reasoning |

**Description:** 8-stage grounding pipeline: PARSE → CLASSIFY → DECIDE → PLAN → RETRIEVE → NORMALIZE → GATE → HANDOFF. Live web and data access is gated by truth classification — invariants use offline reasoning; time-sensitive facts trigger live retrieval; ambiguous queries HOLD for narrowing.

**Inputs:** `session_id`, `query`, `context_hint`  
**Outputs:** `grounded_scene`, `evidence_bundle`, `truth_class`, `retrieval_plan`

---

### 3. `arifos_mind`

| Field | Value |
|---|---|
| Axis | constitutional |
| Role | structured_reasoning |
| Pipeline stage | 333 MIND |
| Modes | `reason`, `sequential`, `step`, `branch`, `merge`, `review` |

**Description:** Runs the full sense→mind→heart→judge reasoning pipeline. Supports sequential constitutional thinking with branching and merging. Produces a narrow `decision_packet` for the operator and a full `audit_packet` for the vault.

**Inputs:** `session_id`, `grounded_scene`, `reasoning_goal`  
**Outputs:** `reasoning_graph`, `candidate_plans`, `audit_packet`

---

### 4. `arifos_heart`

| Field | Value |
|---|---|
| Axis | constitutional |
| Role | red_team |
| Pipeline stage | 666 HEART |
| Floors checked | F5 Peace · F6 Maruah · F9 Anti-Hantu |

**Description:** Red-teams candidate plans and proposals. Simulates downstream consequences, evaluates against constitutional floors, and identifies failure modes before execution is authorised.

**Inputs:** `session_id`, `candidate_plans`, `impact_scope`  
**Outputs:** `risk_assessment`, `failure_modes`, `mitigations`

---

### 5. `arifos_judge`

| Field | Value |
|---|---|
| Axis | constitutional |
| Role | final_verdict |
| Pipeline stage | 888–999 JUDGE→SEAL |
| Invariant | Required before any execution via arifos_forge |
| Verdicts | SEAL · PARTIAL · HOLD · VOID |

**Description:** Issues the final constitutional verdict. No action may proceed to execution without a SEAL from this tool. Accepts probabilistic domain evidence, accounts for disagreement spread and timing risk.

**Inputs:** `session_id`, `reasoning_graph`, `risk_assessment`, `mitigations`  
**Outputs:** `verdict`, `verdict_rationale`, `allowed_actions`, `constraints`, `g_star_score`

---

## II. Governed Infrastructure Organs (3 tools)

These three tools merge routing, memory, and audit into governed infrastructure organs. They support the constitutional spine but do not replace it.

### 6. `arifos_kernel`

| Field | Value |
|---|---|
| Axis | infrastructure |
| Role | router · risk · orthogonality |
| Merged from | `arifos_kernel` + `arifos_gateway` + `arifos_ops` |
| Orthogonality target | Ω_ortho ≥ 0.95 |

**Description:** Unified routing, risk classification, and orthogonality enforcement. Routes requests to the correct computation or oracle tool. Enforces AGI/ASI lane separation. Computes thermodynamic operation cost via Landauer gate estimation. Blocks requests that would cause physics collapse, governance collapse, or ontology collapse. Self-exclusion guard: `arifos_kernel` is excluded from its own correlation matrix.

**Modes:** `route`, `orthogonality_check`, `ops_cost`, `status`  
**Inputs:** `session_id`, `task_spec`, `risk_profile`, `tool_trace`  
**Outputs:** `selected_tool`, `route_plan`, `ops_cost_estimate`, `orthogonality_status`

---

### 7. `arifos_memory`

| Field | Value |
|---|---|
| Axis | infrastructure |
| Role | governed_memory · skill_registry |
| Merged from | `arifos_memory` + `M_skill_discovery` + `M_skill_metadata` |

**Description:** Semantic vector memory and skill registry in a single context retrieval organ. Stores and retrieves governed engineering context. Searches available skills by keyword or domain. Returns detailed skill metadata on request. Supports asset-scoped GEOX memory.

**Modes:** `store`, `retrieve`, `search_skills`, `get_skill_metadata`, `asset_store`, `asset_query`  
**Inputs:** `session_id`, `mode`, `query`, `content`, `tags`, `asset_id`  
**Outputs:** `memory_handle`, `retrieved_items`, `skill_list`, `skill_metadata`

---

### 8. `arifos_vault`

| Field | Value |
|---|---|
| Axis | infrastructure |
| Role | immutable_ledger · state_recording · audit |
| Merged from | `arifos_vault` + `E_well_anchor` + `M_metabolic_monitor` + `P_vault_ledger_read` |
| Backend | Supabase MerkleV3 · dual-write enabled |

**Description:** Immutable Merkle-hashed audit ledger and state recording organ. Appends verdict records, queries ledger history, anchors WELL biological state, reads metabolic monitor dashboard (F1–F13 + ΔS + Peace² + Ω₀). Builds BLS seal card from ledger.

**Modes:** `append_verdict`, `read_ledger`, `anchor_well_state`, `read_metabolic_state`, `build_seal_card`  
**Inputs:** `session_id`, `mode`, `record_payload`, `verdict`, `since`, `until`  
**Outputs:** `ledger_entry_id`, `ledger_view`, `anchor_id`, `metabolic_snapshot`, `seal_card`

---

## III. Computation & Valuation Engines (3 tools)

All T* and V* tools collapse into three domain-orthogonal engines. Each engine is physics-grounded and operates under constitutional session context.

### 9. `arifos_compute_physics`

| Field | Value |
|---|---|
| Axis | computation |
| Role | physics_engine |
| Merged from | `T_petrophysics_compute` + `T_stratigraphy_correlate` + `T_geometry_build` + `T_math_monte_carlo` + `T_math_entropy_audit` |

**Description:** Physics-grounded numerical computation engine. Covers subsurface earth science (petrophysics, stratigraphy, geometry) and stochastic/information-theoretic mathematics (Monte Carlo, entropy audit). All results carry uncertainty metrics.

**Modes:** `petrophysics`, `stratigraphy_correlate`, `geometry_build`, `monte_carlo`, `entropy_audit`  
**Inputs:** `session_id`, `mode`, `model_spec`, `input_data`, `iterations`  
**Outputs:** `physics_results`, `uncertainty_metrics`, `p10_p50_p90`, `audit_flags`

---

### 10. `arifos_compute_finance`

| Field | Value |
|---|---|
| Axis | computation |
| Role | finance_engine |
| Merged from | `V_npv_evaluate` + `T_math_irr_compute` + `V_emv_evaluate` + `V_dscr_evaluate` + `V_payback_evaluate` + `V_profitability_index` + `V_allocation_rank` + `T_growth_runway_compute` + `V_agent_budget_optimize` + `V_personal_decision_rank` |

**Description:** Full financial valuation and decision engine. Covers discounted cash flow analysis, probabilistic valuation, debt coverage, portfolio ranking, budget optimisation, and personal decision analysis. Outputs include sensitivity analysis and entropy-flagged warnings on ambiguous cash flows.

**Modes:** `npv`, `irr`, `mirr`, `emv`, `dscr`, `payback`, `profitability_index`, `allocation_rank`, `growth_runway`, `budget_optimize`, `personal_decision_rank`  
**Inputs:** `session_id`, `mode`, `cash_flows`, `discount_rate`, `initial_investment`, `probabilities`, `outcomes`, `constraints`, `candidates`, `tasks`, `resources`  
**Outputs:** `finance_metrics`, `ranking`, `sensitivity_analysis`, `warnings`, `payback_period`

---

### 11. `arifos_compute_civilization`

| Field | Value |
|---|---|
| Axis | computation |
| Role | civilization_engine |
| Merged from | `V_civilization_sustainability` + `M_game_theory_solve` + `M_cross_evidence_synthesize` |

**Description:** Long-horizon civilisation, sustainability, and multi-agent strategic modelling. Covers sustainability path analysis, macro-energy-carbon trajectories, game-theoretic allocation (LP, Shapley, Nash), and causal scene synthesis for JUDGE. Operates at civilisational scale.

**Modes:** `sustainability_path`, `macro_energy_carbon`, `scenario_compare`, `game_theory`, `cross_evidence_synthesize`  
**Inputs:** `session_id`, `mode`, `current_state`, `scenario_definitions`, `agents`, `payoff_matrix`, `scene_id`  
**Outputs:** `path_trajectories`, `sustainability_scores`, `tradeoff_surfaces`, `game_solution`, `causal_scene`

---

## IV. Reality Oracles (2 tools)

All P* tools collapse into two clean oracles: biological telemetry and external world data. Orthogonal domains, no cross-contamination.

### 12. `arifos_oracle_bio`

| Field | Value |
|---|---|
| Axis | oracle |
| Role | biology_telemetry |
| Merged from | `P_well_state_read` + `P_well_readiness_check` + `P_well_floor_scan` + `E_well_log` |

**Description:** Biological telemetry and readiness oracle. Reads WELL state, checks biological readiness for high-stakes decisions, scans all W-Floor dimensions (sleep, stress, cognitive load), and logs telemetry updates. The readiness verdict feeds directly into `arifos_judge` — a low readiness score can trigger a HOLD on critical decisions.

**Modes:** `snapshot_read`, `readiness_check`, `floor_scan`, `log_update`  
**Inputs:** `session_id`, `mode`, `bio_payload`, `dimensions`  
**Outputs:** `well_snapshot`, `readiness_score`, `floor_state`, `log_id`, `readiness_verdict`

---

### 13. `arifos_oracle_world`

| Field | Value |
|---|---|
| Axis | oracle |
| Role | world_data |
| Merged from | `P_geox_scene_load` + `P_geox_skills_query` + `P_wealth_snapshot_fetch` + `P_wealth_series_fetch` + `P_wealth_vintage_fetch` |

**Description:** External world data oracle. Loads seismic, well, and volume data into witness context. Queries GEOX skill registry. Fetches cross-source macro, energy, and carbon snapshots by geography. Retrieves live FRED/World Bank/EIA time series and specific vintage data for real-as-of analysis.

**Modes:** `geox_scene_load`, `geox_skills_query`, `macro_snapshot`, `series_fetch`, `series_vintage_fetch`  
**Inputs:** `session_id`, `mode`, `query`, `scene_type`, `path`, `geography`, `source`, `series_id`, `vintage_date`  
**Outputs:** `geox_scene`, `geox_skill_list`, `macro_snapshot`, `time_series`, `vintage_series`

---

## V. Migration Plan — 44 → 13

### Shim Layer (Transition Window)

Register old tool names as thin shims calling new tools. Keep shims live until zero calls hit old names in logs.

| Old Tool Name(s) | New Tool | Mode |
|---|---|---|
| `V_npv_evaluate` | `arifos_compute_finance` | `npv` |
| `T_math_irr_compute` | `arifos_compute_finance` | `irr` / `mirr` |
| `V_emv_evaluate` | `arifos_compute_finance` | `emv` |
| `V_dscr_evaluate` | `arifos_compute_finance` | `dscr` |
| `V_payback_evaluate` | `arifos_compute_finance` | `payback` |
| `V_profitability_index` | `arifos_compute_finance` | `profitability_index` |
| `V_allocation_rank` | `arifos_compute_finance` | `allocation_rank` |
| `T_growth_runway_compute` | `arifos_compute_finance` | `growth_runway` |
| `V_agent_budget_optimize` | `arifos_compute_finance` | `budget_optimize` |
| `V_personal_decision_rank` | `arifos_compute_finance` | `personal_decision_rank` |
| `T_petrophysics_compute` | `arifos_compute_physics` | `petrophysics` |
| `T_stratigraphy_correlate` | `arifos_compute_physics` | `stratigraphy_correlate` |
| `T_geometry_build` | `arifos_compute_physics` | `geometry_build` |
| `T_math_monte_carlo` | `arifos_compute_physics` | `monte_carlo` |
| `T_math_entropy_audit` | `arifos_compute_physics` | `entropy_audit` |
| `V_civilization_sustainability` | `arifos_compute_civilization` | `sustainability_path` |
| `M_game_theory_solve` | `arifos_compute_civilization` | `game_theory` |
| `M_cross_evidence_synthesize` | `arifos_compute_civilization` | `cross_evidence_synthesize` |
| `P_well_state_read` | `arifos_oracle_bio` | `snapshot_read` |
| `P_well_readiness_check` | `arifos_oracle_bio` | `readiness_check` |
| `P_well_floor_scan` | `arifos_oracle_bio` | `floor_scan` |
| `E_well_log` | `arifos_oracle_bio` | `log_update` |
| `E_well_anchor` | `arifos_vault` | `anchor_well_state` |
| `P_geox_scene_load` | `arifos_oracle_world` | `geox_scene_load` |
| `P_geox_skills_query` | `arifos_oracle_world` | `geox_skills_query` |
| `P_wealth_snapshot_fetch` | `arifos_oracle_world` | `macro_snapshot` |
| `P_wealth_series_fetch` | `arifos_oracle_world` | `series_fetch` |
| `P_wealth_vintage_fetch` | `arifos_oracle_world` | `series_vintage_fetch` |
| `arifos_gateway` | `arifos_kernel` | `orthogonality_check` |
| `arifos_ops` | `arifos_kernel` | `ops_cost` |
| `M_skill_discovery` | `arifos_memory` | `search_skills` |
| `M_skill_metadata` | `arifos_memory` | `get_skill_metadata` |
| `M_metabolic_monitor` | `arifos_vault` | `read_metabolic_state` |
| `P_vault_ledger_read` | `arifos_vault` | `read_ledger` |
| `arifos_monitor_metabolism` | `arifos_vault` | `read_metabolic_state` |

### Cutover Steps

1. Deploy shim layer alongside existing 44 tools
2. Update AgentZero tool registry to 13 canonical names
3. Monitor logs for 48 hours — confirm zero hits on old names
4. Remove shim layer
5. Tag release as `v2026-13tool-canonical`

---

## VI. Summary

| Axis | Tools | Count |
|---|---|---|
| Constitutional Primordials | init · sense · mind · heart · judge | 5 |
| Infrastructure Organs | kernel · memory · vault | 3 |
| Computation Engines | physics · finance · civilization | 3 |
| Reality Oracles | bio · world | 2 |
| **TOTAL** | | **13** |

**Constitutional guarantees preserved:**
- F1–F13 all floors enforced
- Trinity ΔΩΨ intact
- 000→999 pipeline preserved
- VAULT999 MerkleV3 audit trail unbroken
- Orthogonality guard self-exclusion active
- Human sovereign veto (F13) unaffected
- Zero capability loss from consolidation

---

*Forged by Arif Fazil · Seri Kembangan, MY · April 2026*  
*DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
