# arifOS Federation — Complete MCP Tool Map

> Compiled: 2026-06-04T03:45:00Z
> Live probe: T₁ verified against all four organs

---

## Summary

| Organ | Port | Public Tools | Hidden Aliases | Role |
|-------|------|-------------|----------------|------|
| **arifOS** | 8088 | 13 | — | Constitutional Kernel |
| **WEALTH** | 18082 | 42 | 34 | Capital Intelligence |
| **WELL** | 18083 | 13 | 2 internal diagnostics | Human Readiness |
| **GEOX** | 8081 | 20 | — | Earth Intelligence |
| **TOTAL** | — | **88** | — | — |

---

## arifOS — Constitutional Kernel (13 tools)

| # | Tool | Stage/Lane | Description |
|---|------|------------|-------------|
| 1 | `arif_session_init` | 000 / AGI | Start or resume a governed constitutional session. Call FIRST. |
| 2 | `arif_sense_observe` | 111 / AGI | Search web, ingest URLs, check vitals, map repos. |
| 3 | `arif_evidence_fetch` | 222 / AGI | Fetch and preserve external evidence with citations. |
| 4 | `arif_mind_reason` | 333 / AGI | Multi-step reasoning, planning, reflection. |
| 5 | `arif_heart_critique` | 444 / ASI | Assess ethical risks and human impact before acting. |
| 6 | `arif_kernel_route` | 555 / AGI | Route intent to correct tool or federation organ. |
| 7 | `arif_reply_compose` | 444r / AGI | Compose final response for user. Call LAST. |
| 8 | `arif_memory_recall` | 555m / AGI | Search past sessions, assets, sealed events. |
| 9 | `arif_gateway_connect` | 666g / ASI | Bridge to other federation agents (GEOX, WEALTH, WELL). |
| 10 | `arif_judge_deliberate` | 888 / ASI | Render final constitutional verdict on proposed action. |
| 11 | `arif_vault_seal` | 999 / APEX | Seal verdict to immutable audit ledger (irreversible). |
| 12 | `arif_forge_execute` | 666 / AGI | Execute approved builds, deployments, system changes. |
| 13 | `arif_ops_measure` | 777 / AGI | Check system health, thermodynamic state, resource metrics. |

**Transport:** streamable-http + stdio fallback  
**Registry:** `registry_truth: VERIFIED` | `contract_drift: false`

---

## WEALTH — Capital Intelligence (42 tools)

### Ω-D1: Personal Finance (6)
| Tool | ID | Description |
|------|-----|-------------|
| `wealth_cashflow_track` | Ω-D1-01 | Record a financial transaction. |
| `wealth_cashflow_summary` | Ω-D1-02 | Aggregate transactions by category. |
| `wealth_runway_calculate` | Ω-D1-03 | Months of financial runway. |
| `wealth_net_worth_snapshot` | Ω-D1-04 | Assets minus liabilities. |
| `wealth_epf_project` | Ω-D1-05 | Project EPF accumulation to target age. |
| `wealth_zakat_calculate` | Ω-D1-06 | Malaysian 2.5% zakat above nisab. |

### Ω-D3: Market Data (3)
| Tool | ID | Description |
|------|-----|-------------|
| `wealth_fx_rate` | Ω-D3-01 | Live FX via Frankfurter API. |
| `wealth_commodity_price` | Ω-D3-02 | Approximate commodity market prices. |
| `wealth_macro_indicator` | Ω-D3-03 | GDP, inflation, rates via World Bank API. |

### Ω-SURVIVAL & Capital Physics (11)
| Tool | ID | Description |
|------|-----|-------------|
| `wealth_health_check` | — | Universal health check for federation stability. |
| `wealth_survival_engine` | Ω-SURVIVAL | Unified survival: cashflow, runway, burn, liquidity. |
| `wealth_value_npv` | — | Net Present Value — scalar thermodynamic work potential. |
| `wealth_energy_irr` | — | Internal Rate of Return — energy yield of capital system. |
| `wealth_density_pi` | — | Profitability Index — value density per unit committed. |
| `wealth_time_payback` | — | Payback Period — time to recover committed capital. |
| `wealth_expectation_emv` | — | Expected Monetary Value — probability-weighted outcome. |
| `wealth_probability_monte_carlo` | — | Monte Carlo — stochastic forecast of outcome distribution. |
| `wealth_signal_evoi` | — | Expected Value of Information — point-estimate of signal. |
| `wealth_flow_cashflow` | — | Cash Flow Projection — metabolic liquidity rate. |
| `wealth_velocity_runway` | — | Compound Growth Velocity and Runway — expansion speed. |

### Ω-WEALTH: Physics-Economic Organs (11)
| Tool | ID | Description |
|------|-----|-------------|
| `wealth_gravity_dscr` | Ω-WEALTH-07 | Debt Service Coverage Ratio — gravitational load on capital. |
| `wealth_mass_networth` | Ω-WEALTH-06 | Net Worth — accumulated balance sheet mass. |
| `wealth_entropy_audit` | — | Structural and narrative entropy coefficients for SOE/NOC. |
| `wealth_governance_verdict` | — | Final Allocation Verdict — sovereign governance recommendation. |
| `wealth_preference_rank` | — | Personal Utility Ranking — preference ordering under constraints. |
| `wealth_agent_path` | — | Sovereign Intent Router — L1/L2 physics-economic paths. |
| `wealth_ledger_query` | — | Ledger Read — query immutable governance ledger. |
| `wealth_ledger_write` | — | Ledger Append — irreversible state transition to VAULT999. |
| `wealth_conservation_capital` | Ω-WEALTH-01 | Conservation — capital stock reality. |
| `wealth_flow_liquidity` | Ω-WEALTH-02 | Flow — liquidity movement. |
| `wealth_gradient_price` | Ω-WEALTH-03 | Gradient — price pressure, spread, mispricing detection. |
| `wealth_entropy_risk` | Ω-WEALTH-04 | Entropy — uncertainty, dispersion, tail risk, disorder. |
| `wealth_energy_productivity` | Ω-WEALTH-05 | Energy — output per input, productivity, capital efficiency. |
| `wealth_time_discount` | Ω-WEALTH-06 | Time — NPV, IRR, payback, compounding, decay. |
| `wealth_inertia_leverage` | Ω-WEALTH-07 | Inertia — resistance to change, leverage stress, fragility. |
| `wealth_field_macro` | Ω-WEALTH-08 | Field — macro environment (rates, FX, energy, carbon, regime). |
| `wealth_signal_information` | Ω-WEALTH-09 | Signal — information value, evidence quality, schema validity. |
| `wealth_game_coordination` | Ω-WEALTH-10 | Game — multi-agent incentives, bargaining, coordination. |
| `wealth_boundary_governance` | Ω-WEALTH-11 | Boundary — constitutional floors, maruah, stewardship, constraint. |
| `wealth_system_registry_status` | — | Registry truth diagnostic — intended, registered, alias surfaces. |
| `wealth_omni_wisdom` | Ω-WEALTH-OMNI | Unified capital intelligence — synthesis + deal + hysteresis. |
| `wealth_inequality_kernel` | Ω-WEALTH-IEQ-00 | Inequality Kernel — unified diagnosis across 5 inequality dimensions. |

**Transport:** streamable-http  
**Registry:** `registry_truth: PASS` | `public_surface_count: 42` | `hidden_alias_count: 34`

---

## WELL — Human Readiness (13 live MCP tools)

| # | Tool | Ω Code | Description |
|---|------|--------|-------------|
| 1 | `mcp_health_check` | — | DEPRECATED alias for `well_assess_reliability(mode='health')`. |
| 2 | `well_classify_substrate` | Ω-WELL-01 | Substrate classification and boundary sensing. |
| 3 | `well_trace_lineage` | Ω-WELL-02 | Memory, trend, ledger, and vault chain tracing. |
| 4 | `well_detect_boundary` | Ω-WELL-03 | Boundary detection across membrane, body, machine, federation. |
| 5 | `well_measure_gradient` | Ω-WELL-04 | Measure chemical, energy, pressure, attention, compute gradients. |
| 6 | `well_assess_metabolism` | Ω-WELL-05 | Assess biological metabolism and system throughput across substrates. |
| 7 | `well_assess_homeostasis` | Ω-WELL-06 | Assess regulation, stability, empathic balance under change. |
| 8 | `well_check_repair` | Ω-WELL-07 | Check repair, recovery, resilience, forge cycle integrity. |
| 9 | `well_validate_vitality` | Ω-WELL-08 | Validate vitality, readiness, and NIAT. |
| 10 | `well_assess_livelihood` | Ω-WELL-09 | Assess human wellness, role, dignity, support, and meaning. |
| 11 | `well_assess_reliability` | Ω-WELL-10 | Assess machine, tool, institution, operational reliability. |
| 12 | `well_compute_metabolic_flux` | Ω-WELL-10b | Compute metabolic_flux — unified thermodynamic entropy rate. |
| 13 | `well_guard_dignity` | Ω-WELL-12 | Guard soul, personhood, meaning, and symbolic boundaries. |

**Internal diagnostics (not in MCP `tools/list`):** `well_system_registry_status`, `well_registry_status`  
**Transport:** streamable-http  
**State:** biometric state stale (~843h), `truth_status: EXPIRED`, `freshness_band: STALE`

---

## GEOX — Earth Intelligence (20 tools)

### Claims & Evidence (3)
| Tool | Description |
|------|-------------|
| `geox_claim_create` | Create structured Earth interpretation claim with full provenance chain. |
| `geox_claim_challenge` | Challenge existing interpretation claim with alternative. |
| `geox_claim_seal` | Submit validated claim to arifOS for Vault999 sealing. |

### Data Ingestion & QC (4)
| Tool | Description |
|------|-------------|
| `geox_data_ingest_bundle` | Lazy ingestion for LAS, CSV, Parquet, SEG-Y, structural payloads. |
| `geox_data_qc_bundle` | Real QC: depth monotonicity, null %, physical range checks. |
| `geox_las_inspect` | Inspect LAS metadata and curve headers against Earth schemas. |
| `geox_tops_inspect` | Inspect well tops table metadata against Earth schemas. |

### Seismic (3)
| Tool | Description |
|------|-------------|
| `geox_seismic_compute` | Unified seismic physics engine. |
| `geox_seismic_inspect` | Inspect seismic metadata against Earth schemas. |
| `geox_seismic_segy_inspect` | Inspect SEG-Y binary header metadata before ingestion. |

### Subsurface & Stratigraphy (3)
| Tool | Description |
|------|-------------|
| `geox_subsurface_generate_candidates` | Generate ensemble subsurface outputs with residuals. |
| `geox_subsurface_verify_integrity` | Enforce Physics9 boundary limits, detect structural paradoxes. |
| `geox_sequence_interpret` | Unified sequence stratigraphy engine. |

### Well & Deviation (3)
| Tool | Description |
|------|-------------|
| `geox_deviation_survey_inspect` | Inspect deviation survey metadata against Earth schemas. |
| `geox_dst_ingest_test` | Structured DST ingestion with derived metrics and flags. |
| `geox_map_context_scene` | Spatial bbox context, CRS checks, causal scene rendering. |

### Evaluation & Evidence (2)
| Tool | Description |
|------|-------------|
| `geox_prospect_evaluate` | Integrated prospect evaluation (Volumetrics, POS, EVOI). |
| `geox_evidence_attach` | Attach evidence artifact to existing claim. |
| `geox_evidence_reason` | Unified evidence synthesis, abduction, contradiction engine. |

### Governance (1)
| Tool | Description |
|------|-------------|
| `geox_system_registry_status` | Discovery of canonical tools, health, contract epoch. |

**Transport:** streamable-http  
**Registry:** `registry_truth: VERIFIED` | `tool_count: 20` | Floors F1–F13 active

---

## Cross-Federation Tool Relationships

```
arifOS (Constitutional Kernel)
├── SENSE → routes to WEALTH/GEOX/WELL via gateway_connect
├── REASON → internal multi-step planning
├── JUDGE → renders SEAL/HOLD/STOP verdicts
├── VAULT → writes to VAULT999 (all organs seal here)
├── FORGE → deploys/restarts organs
└── OPS → health probes all 6 federation nodes

WEALTH (Capital) ──evidence-only──► arifOS JUDGE
WELL (Vitality) ───reflect-only───► arifOS JUDGE
GEOX (Earth) ─────evidence-only──► arifOS JUDGE
```

---

## Known Gaps & Notes

1. **WEALTH hidden aliases (34):** Not listed on public surface. Accessed via internal routing or `wealth_system_registry_status` probe.
2. **WELL biometric state stale:** `state_age_hours: 843.6`. Human-injection required for accurate readiness assessment.
3. **GEOX sequence tools:** `geox_well_compute_gr_bins`, `geox_well_build_packages`, `geox_well_infer_seq_strat`, `geox_well_analyze_sequence` are registered inside dimension-native modules but NOT in `CANONICAL_PUBLIC_TOOLS`. They may be accessible via separate MCP app endpoints.
4. **arifOS unified MCP (mcp_tools.py):** Additional per-agent MCP surfaces exist (`arifos_oracle_bio`, `arifos_compute_physics`, `arifos_compute_finance`, `arifos_compute_civilization`, `arifos_oracle_world`, `arifos_compute_physics`) but are not mounted on port 8088. They run as separate FastMCP instances or are awaiting federation routing.

---

*DITEMPA BUKAN DIBERI — Intelligence is forged, not given.*
