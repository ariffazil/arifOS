# GEOX Phase B Design Note
## Physics Engine + Log Workbench

**Version:** v0.6.1–v0.7.0 Target
**Status:** Design
**Based on:** Phase A MCP Resources (SEALED)
**Authority:** 999 SEAL | Floors F2, F4, F7, F9, F13

---

## 1. Purpose

Phase B implements the **physics engine** and **human cockpit** for governed petrophysics. It builds on Phase A's stable contract:

- **Input:** Phase A MCP resources (`las/bundle`, `logs/canonical`, `qc/report`)
- **Process:** Saturation models + uncertainty propagation + constitutional validation
- **Output:** `interval/{t}-{b}/rock-state` with SEAL/QUALIFY/888_HOLD verdict

**Non-goal:** Fancy visualization before physics correctness. The Log Workbench serves the physics, not the reverse.

---

## 2. Log Workbench UX

### 2.1 Three-Mode Separation (Mandatory)

| Mode | What's Shown | User Can Do | Constitutional Purpose |
|------|--------------|-------------|------------------------|
| **Observed** | RAW + CORRECTED curves only | Pick intervals, flag issues, request corrections | F4 Clarity — no interpretation without physics |
| **Physics** | DERIVED curves + model selection + uncertainty bands | Select Sw model, adjust parameters, run calculation | F2 Truth — explicit assumptions, F7 Humility — uncertainty |
| **Governance** | POLICY overlays + 888_HOLD status + audit trail | Review cutoff policy, acknowledge holds, request override | F13 Sovereign — human veto, F11 Auditability — full chain |

**UX Rule:** Switching modes clears derived/governance overlays. No mixing observed data with interpreted conclusions.

### 2.2 Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Header: Well ID | Depth Ref | Mode Selector | QC Status | Seal Badge       │
├──────────────────┬──────────────────────────────────────┬───────────────────┤
│                  │                                      │                   │
│  Well/Interval   │     Multi-Track Canvas               │  Evidence/        │
│  Navigator       │     (virtualized, synced zoom)       │  Governance       │
│                  │                                      │  Panel            │
│  - Formations    │  ┌─────┬─────┬─────┬─────┬─────┐    │                   │
│  - Wells         │  │DEPTH│ QC  │ GR  │ RES │ D-N │    │  - Model Family   │
│  - MDT points    │  │     │     │     │     │     │    │  - Parameters     │
│  - Core intervals│  ├─────┼─────┼─────┼─────┼─────┤    │  - Uncertainty    │
│                  │  │     │     │     │     │     │    │  - Calibration    │
│  [Interval List] │  │     │     │     │     │     │    │  - Floor Status   │
│                  │  └─────┴─────┴─────┴─────┴─────┘    │                   │
│                  │                                      │  [Compute] [Hold] │
│                  │  Depth: ####.# m  Value: ##.##       │                   │
├──────────────────┴──────────────────────────────────────┴───────────────────┤
│  Lower Tabs: Crossplots (Pickett, RHOB-NPHI, M-N, BVW) | Model Diagnostics   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Track Semantics

**Track order (left to right):**
1. **Depth** — MD/TVD/TVDSS with formation tops
2. **QC** — Bad hole, washout, missing data flags
3. **Gamma/SP** — GR, CGR, SP
4. **Resistivity** — ILD, LLD, LLS, MSFL (log scale)
5. **Density-Neutron** — RHOB, NPHI (overlay)
6. **Sonic** — DT, DTS
7. **Derived Vsh** — With uncertainty band
8. **Derived Porosity** — Phi_t, Phi_e with CI
9. **Derived Sw** — Sw with model badge + uncertainty
10. **Net/Pay** — Policy bars (only in Governance mode)

**Curve Badge System:**
- 🔵 **RAW** — Original measurement
- 🟢 **CORRECTED** — Environmental corrections applied
- 🟡 **DERIVED** — Physics model output
- 🔴 **POLICY** — Economic decision threshold
- 🛑 **HOLD** — 888_HOLD active on interval

### 2.4 Interaction → MCP Flow

| User Action | MCP Call | Resource Update |
|-------------|----------|-----------------|
| Open well | `geox_load_well_log_bundle` | `las/bundle` |
| Switch to Observed mode | — | Display `las/bundle` or `logs/canonical` |
| Pick interval (top-base) | — | Subscribe to `interval/{t}-{b}/rock-state` |
| Click "Select Model" | `geox_select_sw_model` | Returns admissible models |
| Adjust Archie m=2.2 | — | Local state, preview only |
| Click "Compute" | `geox_compute_petrophysics` | Updates `rock-state` resource |
| Switch to Governance mode | `geox_validate_cutoffs` | Applies `cutoff-policy` |
| Click "Check Hold" | `geox_petrophysical_hold_check` | Returns verdict |

---

## 3. Petrophysics Tool Semantics

### 3.1 `geox_select_sw_model`

**Purpose:** Evaluate which saturation models are physically admissible for this rock.

**Input:**
- `interval_uri`: `geox://well/{id}/interval/{top}-{base}/rock-state`
- `candidate_models`: ["archie", "simandoux", "indonesia", "dual_water"]

**Logic:**
```python
for model in candidates:
    violations = model.validate_assumptions(
        vsh=interval.vsh,
        clay_type=interval.clay_type,  # From RATLAS
        salinity=interval.salinity,
        rw_source=interval.rw_source
    )
    if violations:
        reject(model, reasons=violations)
    else:
        admit(model, confidence=estimate_confidence())
```

**Output:**
```json
{
  "recommended": "simandoux_dispersed",
  "admissible": [
    {"model": "simandoux_dispersed", "confidence": 0.85, "justification": "Vsh=0.25, dispersed clay"},
    {"model": "indonesia_mixed", "confidence": 0.70, "justification": "Fallback for higher Vsh"}
  ],
  "rejected": [
    {"model": "archie_clean", "reason": "Vsh=0.25 > 0.10 threshold", "violations": ["Assumes clean sand"]}
  ]
}
```

**F2 Truth:** Rejected models must explain why.

### 3.2 `geox_compute_petrophysics`

**Purpose:** Calculate Vsh, φ, Sw, permeability with uncertainty propagation.

**Input:**
- `interval_uri`
- `model_id`: From `select_sw_model`
- `model_params`: {a, m, n, rw, ...}
- `propagate_uncertainty`: true (default)

**Calculation Chain:**
```
1. Vsh from GR (linear or Clavier-Fertl)
   → uncertainty from GR precision + endpoint selection

2. Porosity from NPHI-RHOB crossover
   → φ_n, φ_d averaged
   → uncertainty from matrix/fluid density assumptions

3. Sw from selected model
   → propagate φ_uncertainty, Rw_uncertainty, m_uncertainty
   → Monte Carlo: 1000 realizations

4. Permeability from Timur-Coates or Winland
   → if NMR available: Coates equation
   → else: FZI/RQI from φ-K relationship

5. Net/Pay from CutoffPolicy
   → NOT computed here — separate `validate_cutoffs` call
```

**Output:** `RockFluidState` with:
- `porosity`: {value, ci_95_low, ci_95_high, method}
- `water_saturation`: {value, model_used, ci_95, assumption_violations}
- `permeability`: {value, method, ci_95}
- `uncertainty_envelope`: Full sensitivity breakdown
- `verdict`: QUALIFY (default) or 888_HOLD if issues detected

**F7 Humility:** Every derived quantity has confidence interval. Point estimates rejected.

### 3.3 `geox_validate_cutoffs`

**Purpose:** Apply economic/policy cutoffs to classify net reservoir / net pay.

**Input:**
- `interval_uri`
- `cutoff_policy_id`: Reference to stored policy

**Logic:**
```python
state = load_rock_state(interval)
policy = load_cutoff_policy(policy_id)

# Physics first
if state.porosity.value < policy.phi_cutoff.threshold:
    is_net_reservoir = false
else if state.vsh > policy.vsh_cutoff.threshold:
    is_net_reservoir = false
else:
    is_net_reservoir = true

# Economics second
if is_net_reservoir and state.sw < policy.sw_cutoff.threshold:
    is_net_pay = true
else:
    is_net_pay = false

# Risk assessment
false_positive_risk = estimate_fp_risk(state, policy)
false_negative_risk = estimate_fn_risk(state, policy)
```

**Output:**
```json
{
  "cutoffs_applied": ["phi>0.10", "vsh<0.40", "sw<0.60"],
  "classification": {
    "net_reservoir": true,
    "net_pay": true
  },
  "risks": {
    "false_positive": 0.15,
    "false_negative": 0.08
  },
  "policy_metadata": {
    "id": "malay_basin_2024",
    "approved_by": "...",
    "economic_basis": "Oil $80/bbl, OPEX $15/bbl"
  }
}
```

**F2 Truth:** Cutoffs are policy decisions with economic basis, not physical laws.

### 3.4 `geox_petrophysical_hold_check`

**Purpose:** Constitutional validation before SEAL.

**888_HOLD Triggers:**

| Trigger | Condition | Required Action |
|---------|-----------|-----------------|
| Rw_uncalibrated | `rw_source in ["assumed", "default"]` | Obtain water sample or SP-derived Rw |
| Model_unsupported | `assumption_violations not empty` | Select different Sw model |
| No_calibration | `core_calibration_count == 0` | Acquire core or MDT data |
| Correction_missing | `environmental_corrections == []` | Apply borehole corrections |
| Invasion_ignored | `invasion_correction == false and shallow_resistivity_available` | Correct for invasion |
| Depth_mismatch | `log_depth != core_depth` within tolerance | Reconcile depth shifts |
| Cutoff_no_basis | `cutoff_policy.calibration_basis is None` | Define calibrated cutoff policy |

**Output:**
```json
{
  "verdict": "888_HOLD",
  "triggers": ["Rw_uncalibrated", "No_calibration"],
  "required_actions": [
    "Obtain formation water resistivity from sample or SP",
    "Acquire core data to validate porosity model"
  ],
  "can_override": true,
  "override_risk": "High — uncalibrated Sw may overstate reserves by 30%+"
}
```

**F13 Sovereign:** Human can override, but risk must be explicit.

---

## 4. Integration with Federation

### 4.1 @RIF (Reasoning)

- Calls `geox_select_sw_model` to understand model options
- Calls `geox_compute_petrophysics` to test hypotheses
- Receives `RockFluidState` with uncertainty for reasoning

### 4.2 @WEALTH (Economics)

- Consumes `interval/{t}-{b}/rock-state` with SEAL status
- Only uses vetted intervals (verdict == SEAL or QUALIFY)
- Cannot override 888_HOLD without @JUDGE

### 4.3 @JUDGE (Human Veto)

- Receives 888_HOLD notifications
- Can view `rock-state` with full audit trail
- Can release HOLD with justification (logged to 999_VAULT)

---

## 5. Phase B Completion Criteria

| Milestone | Deliverable | Test |
|-----------|-------------|------|
| B.1 | Archie + Simandoux + Indonesia + Dual-Water implemented | Unit tests with synthetic logs |
| B.2 | Uncertainty propagation (Monte Carlo) | 95% CI coverage validation |
| B.3 | All 4 tools callable via MCP | Integration tests |
| B.4 | Log Workbench renders Observed mode | Load LAS, display tracks |
| B.5 | Log Workbench renders Physics mode | Model selection, computation |
| B.6 | Log Workbench renders Governance mode | Cutoff policy, HOLD display |
| B.7 | 888_HOLD triggers functional | Synthetic test cases |
| B.8 | Documentation: Tool API, UX spec | Review complete |

**Exit Condition:** A user can load a LAS file, QC it, pick an interval, select a Sw model, compute properties, apply cutoffs, and see 888_HOLD if calibration is missing — all via Log Workbench or direct MCP calls.

---

## 6. Dependencies

**From Phase A (SEALED):**
- ✅ `WellLogCurve`, `LogBundle` schemas
- ✅ `geox://well/{id}/las/bundle` resource
- ✅ `geox_load_well_log_bundle` tool
- ✅ `geox_qc_logs` tool

**New for Phase B:**
- Physics engine: saturation models, mixing laws
- Uncertainty: Monte Carlo framework
- UI: React + Plotly viewer (no new dependencies on backend)

**No external petrophysics libraries required** — implement from first principles with F2/F7 enforcement.

---

## 7. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Physics complexity delays | Medium | High | Start with Archie only, expand incrementally |
| UI performance with large logs | Medium | Medium | Virtualize tracks, lazy-load curves |
| Cutoff policy debates | High | Low | Store policy as data, not code; let users define |
| Uncertainty propagation bugs | Medium | High | Validate against published examples (Crain's) |

---

*DITEMPA BUKAN DIBERI — Forged, Not Given.*

ΔΩΨ | GEOX Phase B Design | 999 SEAL PENDING

---

## Appendix: Quick Reference

### MCP Resource Flow

```
geox_load_well_log_bundle ──► las/bundle ──► Display (Observed mode)
                                    │
                                    ▼
geox_qc_logs ──► qc/report ──► QC badges
                                    │
                                    ▼
User picks interval ──► Subscribe to interval/{t}-{b}/rock-state
                                    │
                                    ▼
geox_select_sw_model ◄─── las/bundle data
        │
        ▼
User selects model ──► geox_compute_petrophysics
                          │
                          ▼
                   Updates rock-state (DERIVED)
                          │
                          ▼
User switches mode ──► geox_validate_cutoffs ──► POLICY overlay
                          │
                          ▼
geox_petrophysical_hold_check ◄─── All above
        │
        ▼
   SEAL / QUALIFY / 888_HOLD
```

### Constitutional Touchpoints

| Floor | Phase B Enforcement |
|-------|---------------------|
| F2 | Model assumptions explicit, cutoffs have economic basis |
| F4 | Provenance badges on every curve, units explicit |
| F7 | Uncertainty bands mandatory, point estimates rejected |
| F9 | Rw calibration required, no assumed values for SEAL |
| F13 | 888_HOLD with explicit triggers, human override available |
