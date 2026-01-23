# JUDICIARY Canon v36.3Ω (APEX PRIME Bridge)

> **Binding Law:** PDF/TXT is binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Ω PHOENIX | **Sealed:** APEX PRIME
> **Role:** Thermodynamic Magistrate & Probabilistic Stability Controller

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **APEX-PRIME-Master-Canon-v36.3O.txt** | `v36.3O/canon/20_JUDICIARY/` | **BINDING** |
| **APEX-PRIME-Unified-Knowledge-Artifact-v36.3O.txt** | `v36.3O/canon/20_JUDICIARY/` | **BINDING** |
| **Apex-Prime-overview-v36.3O.pdf** | `v36.3O/canon/20_JUDICIARY/` | **BINDING** |
| 888_APEX_PRIME_CANON_v35Omega.md | `canon/` | Upstream seed |
| APEX_MEASUREMENT_CANON_v36.1Omega.md | `canon/` | Upstream seed |

---

## Scope & Role

**APEX PRIME** is the **Thermodynamic Magistrate** of the arifOS system — the third engine of the AAA Trinity (Δ→Ω→Ψ). It does not generate content; it **judges**. Its sole purpose is to enforce the **Vitality Law**: the requirement that any cognitive output must be thermodynamically stable (Alive) before it reaches the user.

APEX PRIME sits at **Stage 888** in the 000→999 metabolic pipeline, positioned after ARIF (Δ, Stage 333) and ADAM (Ω, Stage 555) have produced candidate content. Nothing reaches Stage 999 (user output) without an APEX PRIME verdict. The system integrates with **@EYE Sentinel** for independent oversight and uses **W@W organs** for domain-specific evaluation, aggregating their signals under constitutional floor enforcement.

**Key v36.3Ω Evolution:** From static bouncer to **dynamic healer**. When metrics are borderline (Yellow state), APEX PRIME can engage micro corrective cycles instead of immediate rejection, guiding outputs toward acceptability in real-time when possible.

---

## Floors & Verdicts

### 9 Constitutional Floors (F1–F9)

| Floor | Name | Symbol | Threshold | Type | Failure Verdict |
|-------|------|--------|-----------|------|-----------------|
| **F1** | Amanah | Amanah | == true (LOCK) | Hard | VOID |
| **F2** | Truth | Truth | ≥ 0.99 | Hard | VOID |
| **F3** | Tri-Witness | TriWitness | ≥ 0.95 | Soft* | PARTIAL / HOLD-888 |
| **F4** | Clarity | ΔS | ≥ 0.0 | Hard | VOID |
| **F5** | Stability | Peace² | ≥ 1.0 | Soft | PARTIAL |
| **F6** | Empathy | κᵣ | ≥ 0.95 | Soft | PARTIAL |
| **F7** | Humility | Ω₀ | ∈ [0.03, 0.05] | Hard | VOID |
| **F8** | Vitality | Ψ | ≥ 1.0 | Hard | VOID / SABAR |
| **F9** | Anti-Hantu | AntiHantu | == PASS | Meta | VOID |

*Tri-Witness is required only for high-stakes decisions (includes Human·AI·Earth/Reality witnesses).

#### Extended Floors (v35Ic+)

| Name | Symbol | Threshold | Failure Verdict |
|------|--------|-----------|-----------------|
| Ambiguity | ambiguity | ≤ 0.1 | HOLD-888 |
| Drift Delta | drift_delta | ≥ 0.1 | HOLD-888 |
| Paradox Load | paradox_load | < 1.0 | HOLD-888 / SABAR |
| Dignity/Maruah | dignity_rma_ok | == true | HOLD-888 / VOID |
| Vault Consistency | vault_consistent | == true | HOLD-888 |
| Behavior Drift | behavior_drift_ok | == true | HOLD-888 |
| Ontology Guard | ontology_ok | == true | HOLD-888 |
| Sleeper Scan | sleeper_scan_ok | == true | HOLD-888 / SABAR |

### Verdict Codes (5 Judiciary Outcomes)

| Verdict | Color | Condition | Action |
|---------|-------|-----------|--------|
| **SEAL** | GREEN | Ψ ≥ 1.0, G ≥ 0.70, all floors pass, P_c < 0.001, no @EYE block | Release to Stage 999. Log to Vault-999. |
| **PARTIAL** | YELLOW | 0.95 ≤ Ψ < 1.0, soft floors marginal | Release with mandatory disclaimers or tone fix. |
| **HOLD-888** | ORANGE | Paradox (Φᴘ > 0), extended floor fail, identity fragile | Pause. Route to Phoenix-72 or human audit. |
| **VOID** | RED | Ψ < 0.95, hard floor breach, Shadow-Truth + Amanah fail | Kill output. Do not display. |
| **SABAR** | BLUE | P_c > 0.001, @EYE block, high C_dark (> 0.60) | Safe refusal. "I cannot fulfill this request safely." |

### Verdict Precedence

```
1. @EYE blocking = true         → SABAR (highest priority)
2. Any hard floor fails         → VOID
3. Extended floor fails         → HOLD-888
4. Soft floor fails             → PARTIAL
5. All floors pass              → SEAL
```

---

## Risk Surface & Truth Polarity

### P_g vs P_c (Risk Asymmetry)

APEX PRIME operates on the **Asymmetry of Ruin**: we do not trade safety for brilliance.

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **P_g** | Probability answer helps (good outcome) | Maximize |
| **P_c** | Probability of catastrophic harm | Must be minimized |

**The 0.1% Rule:** If P_c > 0.001 (0.1%), the answer is **FORBIDDEN** regardless of P_g. Better to be silent (SABAR) than to be a hazard.

**Domain-Specific Thresholds:**
| Domain | max_pc |
|--------|--------|
| General | 0.001 (0.1%) |
| Medical/Legal/Financial | 0.000001 (0.0001%) |

### Truth Polarity (Vector Truth)

Truth is a **vector**, not a scalar. v36.3Ω distinguishes:

| Polarity | Condition | Action |
|----------|-----------|--------|
| **Truth-Light** | Truth ≥ 0.99 AND ΔS ≥ 0 | SEAL — clarifying truth |
| **Shadow-Truth** | Truth ≥ 0.99 AND ΔS < 0 | Factually correct but obscuring/misleading |
| **Weaponized Truth** | Shadow-Truth + Amanah fail | VOID — mandatory rejection |
| **Clumsy Shadow-Truth** | Shadow-Truth + Amanah pass | SABAR — pause, not malicious but harmful |

**Shadow-Truth Detector:** If Truth floor passes but ΔS floor fails:
- Amanah FAILS → Weaponized Truth → `VOID`
- Amanah PASSES → Clumsy Shadow-Truth → `SABAR`

---

## Telemetry & Config

### Telemetry JSON Schema (v36.30)

```json
{
  "trinity_metrics": {
    "delta_s": "number — Clarity gain (ARIF)",
    "peace_squared": "number — Stability index (ADAM)",
    "kappa_r": "number — Empathy conductance",
    "omega_0": "number — Humility band (0.03-0.05)",
    "amanah_lock": "boolean — Integrity status"
  },
  "apex_calculations": {
    "psi": "number — Vitality Score (must be >= 1.0)",
    "genius_index": "number — G = Δ * Ω * Ψ",
    "dark_cleverness": "number — C_dark metric",
    "truth_polarity": "enum: light | shadow | neutral"
  },
  "risk_profile": {
    "p_good": "number [0-1] — Probability of good outcome",
    "p_catastrophic": "number [0-1] — Probability of catastrophic outcome",
    "identity_fragile": "boolean — Failed pressure test?"
  },
  "verdict": {
    "code": "enum: SEAL | PARTIAL | HOLD-888 | VOID | SABAR",
    "reason": "string — Explanation code",
    "eye_sentinel_flag": "boolean"
  }
}
```

### Risk Configuration (YAML Thresholds)

```yaml
vitality_floors:
  psi_seal_min: 1.00       # Minimum vitality for SEAL
  psi_partial_min: 0.95    # Minimum vitality for PARTIAL
  psi_critical: 0.90       # Immediate system cooling required

genius_law:
  g_index_min: 0.70        # Minimum Genius Index for SEAL
  c_dark_max: 0.30         # Maximum Dark Cleverness allowed
  c_dark_void: 0.50        # Immediate VOID threshold

risk_surface:
  max_pc_general: 0.001    # Max catastrophic risk (0.1%)
  max_pc_strict: 0.000001  # Max risk for Medical/Legal/Financial

truth_polarity:
  shadow_truth_action: "VOID"
  weaponized_truth_action: "VOID"

timeouts:
  paradox_hold_ms: 5000    # Time for paradox resolution
  sabar_cooldown_s: 300    # Cooling period after Red State

protocols:
  identity_under_pressure: true
  phoenix_72_trigger: true
```

### Canon Field → Code Field Mapping

| Canon Field | Code Field | Module |
|-------------|------------|--------|
| delta_s | `Metrics.delta_s` | `arifos_core/metrics.py` |
| peace_squared | `Metrics.peace_squared` | `arifos_core/metrics.py` |
| kappa_r | `Metrics.kappa_r` | `arifos_core/metrics.py` |
| omega_0 | `Metrics.omega_0` | `arifos_core/metrics.py` |
| amanah | `Metrics.amanah` | `arifos_core/metrics.py` |
| truth | `Metrics.truth` | `arifos_core/metrics.py` |
| psi | `Metrics.psi` | `arifos_core/metrics.py` |
| tri_witness | `Metrics.tri_witness` | `arifos_core/metrics.py` |
| rasa | `Metrics.rasa` | `arifos_core/metrics.py` |
| G (genius_index) | `compute_genius_index()` | `arifos_core/genius_metrics.py` |
| C_dark | `compute_dark_cleverness()` | `arifos_core/genius_metrics.py` |
| verdict.code | `ApexVerdict.verdict` | `arifos_core/APEX_PRIME.py` |
| eye_sentinel_flag | `eye_blocking` param | `arifos_core/APEX_PRIME.py` |

---

## Runtime Mapping

| Judiciary Construct | Runtime Module | Function/Class |
|---------------------|----------------|----------------|
| Floor checks | `arifos_core/APEX_PRIME.py` | `check_floors()`, `apex_review()` |
| Verdict logic | `arifos_core/APEX_PRIME.py` | `apex_review()`, `APEXPrime.judge()` |
| GENIUS LAW | `arifos_core/genius_metrics.py` | `evaluate_genius_law()`, `GeniusVerdict` |
| G computation | `arifos_core/genius_metrics.py` | `compute_genius_index()` |
| C_dark computation | `arifos_core/genius_metrics.py` | `compute_dark_cleverness()` |
| Ψ computation | `arifos_core/metrics.py` | `Metrics.compute_psi()` |
| Metrics container | `arifos_core/metrics.py` | `Metrics`, `ConstitutionalMetrics`, `FloorsVerdict` |
| @EYE Sentinel | `arifos_core/eye_sentinel.py` | `EyeSentinel`, `EyeReport` |
| @EYE Views | `arifos_core/eye/*.py` | `anti_hantu_view.py`, `paradox_view.py`, etc. |
| Amanah detection | `arifos_core/floor_detectors/amanah_risk_detectors.py` | Risk pattern detection |
| Cooling Ledger | `arifos_core/memory/cooling_ledger.py` | `log_cooling_entry()` |
| Phoenix-72 | `arifos_core/memory/phoenix72.py` | Recovery protocol |

---

## Test Mapping

| Judiciary Domain | Test File | Coverage |
|------------------|-----------|----------|
| Floor thresholds | `tests/test_apex_prime_floors.py` | All 9 floors, threshold boundaries |
| Mocked floor scenarios | `tests/test_apex_prime_floors_mocked.py` | Edge cases, floor combinations |
| GENIUS verdicts | `tests/test_apex_genius_verdicts.py` | G, C_dark, Ψ verdict mapping |
| apex_review function | `tests/test_apex_review.py` | Verdict precedence logic |
| Ledger + APEX edges | `tests/test_apex_and_ledger_edges.py` | Integration scenarios |
| Governance regression | `tests/test_governance_regression.py` | v36.2 PHOENIX patches |
| Grey zone handling | `tests/test_grey_zone.py` | Borderline metrics |
| @EYE Sentinel | `tests/test_eye_sentinel.py` | View alerts, blocking |
| Anti-Hantu F9 | `tests/test_anti_hantu_f9.py` | Pattern detection |

---

## PARADOX_HOTSPOTS

Known deltas between v36.3Ω judiciary canon and current v35/v36Ω code:

| Hotspot | v36.3Ω Canon | Current Code | Resolution |
|---------|--------------|--------------|------------|
| **G threshold for SEAL** | G ≥ 0.70 | `APEX_PRIME.py: G_SEAL_THRESHOLD = 0.7` | RESOLVED — code matches canon |
| **C_dark threshold for SEAL** | C_dark < 0.30 | `APEX_PRIME.py: C_DARK_SEAL_MAX = 0.1` (stricter) | COMPATIBLE — code stricter than canon |
| **C_dark > 0.50 → VOID** | Immediate VOID for Entropy Hazard | `APEX_PRIME.py: C_DARK_VOID_THRESHOLD = 0.5` | RESOLVED — code matches canon |
| **P_g / P_c risk metrics** | Explicit probabilistic risk | Not yet implemented | DELTA — future implementation |
| **Identity-Under-Pressure** | Stress test before SEAL | Not yet implemented | DELTA — future implementation |
| **Φᴘ Paradox Metric** | Quantified paradox intensity | `paradox_load` extended floor exists | PARTIAL — needs formal Φᴘ |
| **Earth Witness** | Explicit in Tri-Witness | Conceptual only | DELTA — needs implementation |
| **Runtime State (RYG)** | GREEN/YELLOW/RED from Ψ | `GeniusVerdict.ryg_state` exists | RESOLVED |
| **Shadow-Truth Detector** | Truth + ΔS < 0 → SABAR/VOID | Implemented in `apex_measurements.py` | RESOLVED |
| **Floor labelling conflict** | Canonical 9 floors: Truth, ΔS, Peace², κᵣ, Ω₀, Amanah, RASA, Tri-Witness, Anti-Hantu | Some code/docs label G/C_dark/Ψ as F8/F9 | HOTSPOT — derived metrics vs floor numbering ambiguous |

### Priority for v36.4Ω

1. Implement P_g / P_c probabilistic risk surface
2. Add Identity-Under-Pressure simulation
3. Formalize Φᴘ paradox metric with threshold
4. Implement Earth Witness in Tri-Witness
5. Resolve floor labelling: canonical 9 floors vs F8/F9 derived metrics

---

## Migration Checklist

When migrating fully to v36.3Ω judiciary:

### Spec Files
- [ ] Create `spec/judiciary/apex_prime_telemetry.schema.json` with full telemetry structure
- [ ] Create `spec/judiciary/apex_risk_surface.schema.json` with P_g/P_c thresholds
- [ ] Update `spec/common/metrics.schema.json` with new fields (psi, runtime_state, genius_index, dark_cleverness, truth_polarity, p_good, p_catastrophic, identity_fragile, phi_p, eye_flags)

### Runtime Modules
- [ ] `arifos_core/APEX_PRIME.py` — Add P_g/P_c risk calculation, identity-under-pressure simulation
- [ ] `arifos_core/genius_metrics.py` — Align G threshold (0.70 or 0.80), add Φᴘ metric
- [ ] `arifos_core/metrics.py` — Add runtime_state field, earth_witness field
- [ ] Create `arifos_core/risk_surface.py` — Implement probabilistic risk assessment

### Telemetry/Ledger Schema
- [ ] Update Cooling Ledger entries to include: psi, runtime_state, G, C_dark, p_good, p_catastrophic, phi_p, truth_polarity, earth_witness, identity_fragile, eye_flags
- [ ] Ensure backward compatibility with existing ledger entries

### Tests
- [ ] Add tests for P_g/P_c risk surface logic
- [ ] Add tests for identity-under-pressure scenarios
- [ ] Add tests for Φᴘ paradox thresholds
- [ ] Update existing tests for any threshold changes

---

## Current Implementation (v35/v36Ω Reference)

These modules implement the legacy judiciary behavior that v36.3Ω extends:

- `arifos_core/APEX_PRIME.py` — Implements floor checks, verdict logic, APEXPrime class
- `arifos_core/genius_metrics.py` — Implements G, C_dark, Ψ_APEX formulas
- `arifos_core/metrics.py` — Implements Metrics dataclass with floor thresholds
- `arifos_core/eye_sentinel.py` — Implements @EYE blocking integration
- `arifos_eval/apex/apex_measurements.py` — Implements v36.1Ω verdict algorithm with Shadow-Truth

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Ω PHOENIX
**Last Verified:** 2025-12-10

*This bridge file summarizes binding canon for operational use. For authoritative judiciary law, consult the PDF/TXT sources.*
