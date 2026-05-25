# FEDERATION.md — W@W Intelligence Mesh

**Version:** 2026.05.15
**Sovereign:** Muhammad Arif bin Fazil
**Governance:** arifOS constitutional kernel (F1–F13)
**Principle:** DITEMPA BUKAN DIBERI — Forged, Not Given

---

## Architecture Overview

The federation is four witness planes operating under one constitutional kernel.
arifOS is not a peer — it is the governance layer that all others route through.

```
         ┌─────────────────────┐
         │      ARIF (Sovereign)│
         └──────────┬──────────┘
                    │ F13 veto always retained
         ┌──────────▼──────────┐
         │     arifOS MCP      │  ← Governance kernel. All sessions init here.
         │  Constitutional OS  │    Judge, Vault, Forge, Memory live here.
         └──┬──────┬──────┬───┘
            │      │      │
     ┌──────▼─┐ ┌──▼───┐ ┌▼──────┐
     │  GEOX  │ │WEALTH│ │  WELL │
     │ Earth  │ │Capital│ │Human │
     └────────┘ └──────┘ └───────┘
```

**Rule:** A session initialized on arifOS (arif_session_init) is the authoritative session.
Cross-MCP calls made within that session carry its session_id as governance provenance.
Tools on GEOX/WEALTH/WELL that accept session_id should receive it from the active arifOS session.

---

## MCP 1 — arifOS

| Field | Value |
|---|---|
| Domain | Constitutional Governance |
| Canonical URL | `https://arifos.arif-fazil.com/mcp` |
| Local port | `127.0.0.1:8088` |
| Version | v2026.05.05-SSCT |
| Tools | 13 canonical + 1 daily brief = 14 total |
| Jurisdiction | **Everything.** The only MCP that can judge, seal, forge, and govern. |

### When to call arifOS

Call arifOS **first, always.** It is the session anchor and audit trail.

| Intent | Tool | Stage |
|---|---|---|
| Start any multi-step session | `arif_session_init` | 000 |
| Observe system state, fetch web, search | `arif_sense_observe` | 111 |
| Retrieve verified external evidence | `arif_evidence_fetch` | 222 |
| Reason over a complex problem | `arif_mind_reason` | 333 |
| Route a task to the right organ | `arif_kernel_route` | 444 |
| Compose a final reply for Arif | `arif_reply_compose` | 444r |
| Query session memory / Qdrant store | `arif_memory_recall` | 555 |
| Ethical / constitutional critique | `arif_heart_critique` | 666 |
| Bridge to GEOX/WEALTH/WELL agents | `arif_gateway_connect` | 666 |
| Build code, scripts, artifacts | `arif_forge_execute` | 010 |
| System health + thermodynamic metrics | `arif_ops_measure` | 777 |
| Final verdict on any candidate action | `arif_judge_deliberate` | 888 |
| Seal outcome to VAULT999 ledger | `arif_vault_seal` | 999 |
| Morning intelligence brief | `arif_daily_intelligence_brief` | — |

### Do NOT call arifOS for

- Raw geological data analysis → use GEOX
- EMV/NPV/capital allocation calculations → use WEALTH
- Arif's biological/cognitive state assessment → use WELL
- As a substitute for domain-specific reasoning that GEOX/WEALTH/WELL own

---

## MCP 2 — GEOX

| Field | Value |
|---|---|
| Domain | Earth & Geoscience Intelligence |
| Canonical URL | `https://geox.arif-fazil.com/mcp` |
| Local port | `127.0.0.1:18081` |
| Image | `ghcr.io/ariffazil/geox:dd4120c0` |
| Tools | 21 tools (excluding health check) |
| Jurisdiction | Subsurface data, seismic, well logs, stratigraphy, prospect evaluation |

### When to call GEOX

| Intent | Tool | One-line routing hint |
|---|---|---|
| Ingest well / seismic data bundle | `geox_data_ingest_bundle` | Call this when loading raw LAS, SEG-Y, or tabular subsurface data |
| QC ingested data | `geox_data_qc_bundle` | Call this after ingest to validate data quality before analysis |
| Generate subsurface candidates | `geox_subsurface_generate_candidates` | Call this to propose drillable targets from basin context |
| Verify candidate integrity | `geox_subsurface_verify_integrity` | Call this before judge — verifies candidate passes PhysicsGuard |
| Analyze seismic volume | `geox_seismic_analyze_volume` | Call this for AVO, amplitude, attribute extraction from seismic |
| Correlate seismic sections | `geox_section_interpret_correlation` | Call this for cross-section correlation and stratigraphic picks |
| Map context and scene | `geox_map_context_scene` | Call this for spatial context, basin map generation |
| 4D time-lapse analysis | `geox_time4d_analyze_system` | Call this for reservoir surveillance and production-related 4D |
| Evaluate a prospect | `geox_prospect_evaluate` | Call this for P10/P50/P90 resource estimation and risk factors |
| Preview prospect judge | `geox_prospect_judge_preview` | Call this before sealing — dry-run of the verdict |
| Seal prospect judgment | `geox_prospect_judge_seal` | Call this to commit a prospect verdict to ledger |
| Cross-domain evidence summary | `geox_evidence_summarize_cross` | Call this to synthesize seismic + well + production evidence into one package |
| Registry status | `geox_system_registry_status` | Call this to check GEOX system health and data catalog state |
| Audit history | `geox_history_audit` | Call this to review past interpretations and decisions |
| DST ingest test | `geox_dst_ingest_test` | Call this for drill stem test data ingestion validation |
| GR bin computation | `geox_well_compute_gr_bins` | Call this for gamma ray log binning and lithofacies prep |
| Well package build | `geox_well_build_packages` | Call this to package all well data (LAS + header + QC) for export |
| Sequential stratigraphy inference | `geox_well_infer_seq_strat` | Call this to interpret systems tracts and sequence boundaries from logs |
| Well sequence analysis | `geox_well_analyze_sequence` | Call this for depositional sequence analysis from well data |
| Stratigraphy pipeline run | `geox_stratigraphy_run_pipeline` | Call this to execute the full stratigraphic interpretation pipeline |
| Stratigraphy config preview | `geox_stratigraphy_preview_config` | Call this before running pipeline to validate config parameters |

### Do NOT call GEOX for

- Economic evaluation of a prospect → route to WEALTH after GEOX gives resource volumes
- Arif's decision to drill or not → route to arifOS `arif_judge_deliberate`
- Storing outcomes to permanent ledger → route to arifOS `arif_vault_seal`
- Any action requiring F1–F13 enforcement → arifOS governs, GEOX provides domain data

### GEOX ↔ arifOS handoff pattern

```
1. arif_session_init (arifOS)          → get session_id
2. geox_data_ingest_bundle (GEOX)      → session_id passed as provenance
3. geox_prospect_evaluate (GEOX)       → produces domain_evidence bundle
4. arif_judge_deliberate (arifOS)      → receives domain_evidence from GEOX, renders verdict
5. arif_vault_seal (arifOS)            → seals verdict to VAULT999
```

---

## MCP 3 — WEALTH

| Field | Value |
|---|---|
| Domain | Capital & Financial Intelligence |
| Canonical URL | `https://wealth.arif-fazil.com/mcp` ← **authoritative** |
| Dead URL | `https://wealth.fastmcp.app` ← **deprecated, do not use** |
| Local port | `127.0.0.1:18082` |
| Version | wealth-mcp 2026.05.02 |
| Tools | 12 tools (excluding health/registry) |
| Jurisdiction | EMV, NPV, capital flows, risk pricing, game theory, macro field economics |

### When to call WEALTH

| Intent | Tool | One-line routing hint |
|---|---|---|
| Capital conservation / stock assessment | `wealth_conservation_capital` | Call this to assess capital preservation capacity and stock-flow balance |
| Liquidity and cash flow | `wealth_flow_liquidity` | Call this for working capital, liquidity ratios, cash runway analysis |
| Price signal / gradient analysis | `wealth_gradient_price` | Call this for price sensitivity, gradient pricing, and value slope analysis |
| Risk entropy assessment | `wealth_entropy_risk` | Call this to quantify uncertainty and information entropy in financial positions |
| Energy-to-value productivity | `wealth_energy_productivity` | Call this for EROI, CapEx/OpEx efficiency, and energy productivity metrics |
| Time discounting / NPV | `wealth_time_discount` | Call this for DCF, NPV, IRR, and time-preference valuations |
| Leverage and inertia | `wealth_inertia_leverage` | Call this for debt structure, leverage ratios, and financial inertia analysis |
| Macro field context | `wealth_field_macro` | Call this for macroeconomic context: cycles, sector positioning, field dynamics |
| Information signal quality | `wealth_signal_information` | Call this to assess data quality, market signal clarity, and noise reduction |
| Game theory / coordination | `wealth_game_coordination` | Call this for multi-party negotiations, Nash equilibria, stakeholder dynamics |
| Boundary and governance | `wealth_boundary_governance` | Call this for regulatory, governance, and boundary risk assessment |
| Hysteresis ledger | `wealth_hysteresis_ledger` | Call this to track path-dependent effects — past decisions shaping current state |

### Do NOT call WEALTH for

- Generating the underlying resource volumes → GEOX owns that; WEALTH prices what GEOX produces
- Arif's binary go/no-go decision → route to arifOS `arif_judge_deliberate`
- Human wellbeing or ergonomic risk → route to WELL
- Canonical URL is `wealth.arif-fazil.com` — `wealth.fastmcp.app` is dead, ignore it

### WEALTH ↔ GEOX ↔ arifOS handoff pattern

```
1. arif_session_init (arifOS)                   → session anchor
2. geox_prospect_evaluate (GEOX)                → produces P10/P50/P90 volumes + risk
3. wealth_time_discount (WEALTH)                → NPV/EMV from GEOX volumes
4. wealth_entropy_risk (WEALTH)                 → quantify financial uncertainty
5. arif_judge_deliberate (arifOS)               → full verdict: geology + economics
6. arif_vault_seal (arifOS)                     → seal to ledger
```

---

## MCP 4 — WELL

| Field | Value |
|---|---|
| Domain | Human & Substrate Vitality |
| Canonical URL | `https://well.arif-fazil.com/mcp` |
| Local port | `127.0.0.1:8083` |
| Version | 2026.05.12-ΩWELL+GWELL+FEDERATION |
| Tools | 11 tools (excluding health check) |
| Jurisdiction | Arif's biological state, cognitive load, substrate classification, machine/governance reliability |
| Authority | **REFLECT_ONLY** — WELL holds a mirror, never a veto |

### When to call WELL

| Intent | Tool | One-line routing hint |
|---|---|---|
| Classify any substrate (human, machine, institution) | `well_classify_substrate` | Call this first whenever the subject of assessment is unclear — what IS this thing? |
| Recall past state / trace patterns | `well_trace_lineage` | Call this to review history, trends, and vault chain for continuity |
| Detect operating boundary | `well_detect_boundary` | Call this to assess whether Arif or a system is near its limit |
| Measure gradient / evidence quality | `well_measure_gradient` | Call this to check how fresh and reliable the input evidence is |
| Assess biological metabolism | `well_assess_metabolism` | Call this to evaluate Arif's energy, duty load, and cognitive capacity |
| Assess homeostasis / stability | `well_assess_homeostasis` | Call this to check balance, regulation, and stress/coercion signals |
| Check repair / forge readiness | `well_check_repair` | Call this before a high-intensity forge session to verify Arif is ready |
| Validate vitality and readiness | `well_validate_vitality` | Call this before any consequential decision — is Arif in state to decide? |
| Assess livelihood and dignity | `well_assess_livelihood` | Call this for role clarity, purpose alignment, and dignity preservation checks |
| Assess machine/tool reliability | `well_assess_reliability` | Call this to check system health, tool integrity, and operational reliability |
| Compute metabolic flux | `well_compute_metabolic_flux` | Call this to get unified thermodynamic entropy rate across human + machine |

### WELL vs arifOS ops_measure — the boundary

| Question | Which tool | Why |
|---|---|---|
| Is the VPS CPU/RAM healthy? | `arif_ops_measure` (arifOS) | Machine hardware metrics |
| Is arifOS's reasoning thermodynamically stable? | `arif_ops_measure` (arifOS) | System g_score, entropy delta, Ω |
| Is Arif cognitively ready to make a decision? | `well_validate_vitality` (WELL) | Human biological/cognitive state |
| Is Arif near burnout or cognitive overload? | `well_detect_boundary` (WELL) | Human substrate boundary detection |
| What is the combined human+machine entropy? | `well_compute_metabolic_flux` (WELL) | Cross-substrate unified flux |

**One-line rule:** `arif_ops_measure` owns the machine. `well_*` owns the human.

### Do NOT call WELL for

- Geological, financial, or code decisions → GEOX / WEALTH / arifOS
- Storing outcomes → WELL is read-only + reflect-only. Route to arifOS `arif_vault_seal`
- Overriding Arif's sovereign judgment → WELL reflects, Arif decides

---

## Cross-MCP Routing Rules

### Rule 1: Session provenance
Always init on arifOS first. Pass `session_id` to every cross-MCP call that accepts it.
This is how all calls trace back to a single governance anchor.

### Rule 2: Domain data vs. judgment
- GEOX / WEALTH / WELL = **domain data producers**
- arifOS = **judgment engine and ledger**
- Never ask a domain MCP to judge. Never ask arifOS to interpret a seismic section.

### Rule 3: The dead endpoint
`wealth.fastmcp.app` — **do not call this.** It is deprecated.
Canonical WEALTH URL is `https://wealth.arif-fazil.com/mcp`.

### Rule 4: WELL's authority ceiling
WELL can flag a concern. WELL cannot block an action.
Arif's sovereign override (F13) is always above WELL's output.

### Rule 5: Verdict and seal always on arifOS
No matter which MCPs contributed, the final verdict (`arif_judge_deliberate`) and
the permanent record (`arif_vault_seal`) always run on arifOS. This is non-negotiable.

---

## Intent → MCP Routing Matrix

| Intent type | Primary MCP | Support MCP |
|---|---|---|
| Session management, audit trail | arifOS | — |
| Seismic interpretation | GEOX | — |
| Well log analysis | GEOX | — |
| Prospect resource estimation | GEOX | — |
| Economic evaluation (EMV/NPV) | WEALTH | GEOX (volumes) |
| Capital allocation / leverage | WEALTH | — |
| Arif's cognitive/biological readiness | WELL | — |
| Machine/system reliability check | WELL + arifOS ops_measure | — |
| Cross-domain intelligence synthesis | arifOS (daily brief) | GEOX + WEALTH + WELL |
| Ethical / constitutional critique | arifOS (heart) | — |
| Final go/no-go decision | arifOS (judge) | GEOX + WEALTH (evidence) |
| Permanent record / audit | arifOS (vault) | — |

---

## Version History

| Date | Change |
|---|---|
| 2026-05-15 | Initial forge — driven by HEART critique on civilizational deployment gaps |
