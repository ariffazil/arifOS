# APEX MEASUREMENT v36.3Ω (Bridge & Parallel Layer)

> **Binding Law:** PDF/TXT is binding; this markdown file is a bridge/summary only.
> **Epoch:** v36.3Ω PHOENIX | **Sealed:** APEX PRIME
> **Strategy:** Parallel layer — runs alongside existing code, does not replace it.

---

## Source Files

| File | Location | Status |
|------|----------|--------|
| **APEX_MEASUREMENT_CANON_v36.1Omega.md** | `canon/` | **BINDING** (upstream seed) |
| APEX_THEORY_GENESIS_v36Omega.md | `canon/00_CANON/` | Frozen 9 floors definition |
| APEX_THEORY_MATH_v36Omega.md | `canon/01_PHYSICS/` | Mathematical foundations |
| metrics.py | `arifos_core/` | Runtime floor thresholds |
| genius_metrics.py | `arifos_core/` | G, C_dark, Ψ computation |

---

## Scope & Role

The MEASUREMENT canon defines **how to measure** the 9 constitutional floors and **how to report** governance health via 3 aggregate metrics (Δ, Ω, Ψ).

### Parallel Layer Strategy

This v36.3Ω measurement layer runs **alongside** existing v35Ω/v36Ω code:

1. **Current code** (`arifos_core/metrics.py`, `genius_metrics.py`) remains authoritative for runtime verdicts
2. **This bridge** documents the canonical measurement spec that code should converge toward
3. **Delta tracking** via PARADOX_HOTSPOTS section captures gaps between canon and code
4. **Phoenix-72** pathway: Code catches up to canon via amendment proposals, never silently bend canon

### What This Layer Provides

- Canonical thresholds for all 9 frozen floors
- 3 aggregate reporting metrics (Δ_metric, Ω_metric, Ψ_metric) for dashboard/telemetry
- Mapping from floor states → verdict codes → human labels
- Test coverage requirements for measurement accuracy

---

## Measuring the Frozen 9 Floors

The 9 floors are **frozen** as defined in Genesis (`canon/00_CANON/APEX_THEORY_GENESIS_v36Omega.md`). Each floor has a canonical measurement method.

### Summary Table (Canonical Order)

| Floor | Law | Threshold | Type | Canon Reference |
|-------|-----|-----------|------|-----------------|
| **F1** | Truth | ≥ 0.99 | Hard | Clarity Law (Δ) |
| **F2** | ΔS (Clarity) | ≥ 0 | Hard | Clarity Law (Δ) |
| **F3** | Peace² | ≥ 1.0 | Soft | Vitality Law (Ψ) |
| **F4** | κᵣ (Empathy) | ≥ 0.95 | Soft | Humility Law (Ω) |
| **F5** | Ω₀ (Humility) | [0.03, 0.05] | Hard | Humility Law (Ω) |
| **F6** | Amanah | LOCK | Hard | Integrity Axiom |
| **F7** | RASA | TRUE | Hard | Humility Law (Ω) |
| **F8** | Tri-Witness | ≥ 0.95 | Hard | Vitality Law (Ψ) |
| **F9** | Anti-Hantu | PASS | Hard | Language Law |

**Hard floor fail → VOID.** Soft floor fail → PARTIAL (proceed with caution).

---

### F1: Truth (Hard Floor)

> **Canon:** Clarity Law (Δ) — "Every valid step must increase clarity or at least not reduce it."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Truth ≥ 0.99 |
| **Measure** | Factual accuracy where evidence is required |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.truth` in `arifos_core/metrics.py` |

**Measurement Method:**
- Verify claims against authoritative sources
- Check file/function existence before referencing
- Distinguish fact from opinion/speculation

### F2: ΔS / IΔS (Hard Floor)

> **Canon:** Clarity Law (Δ) — "ΔS ≥ 0: If an answer makes things more confusing, it is physically invalid."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | ΔS ≥ 0 |
| **Measure** | Output must not increase entropy/confusion |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.delta_s` in `arifos_core/metrics.py` |

**Measurement Method:**
- Compare output clarity to input state
- Positive ΔS = clarifying (good)
- Negative ΔS = confusing (floor fail)

### F3: Peace² (Soft Floor)

> **Canon:** Vitality Law (Ψ) — "The system must maintain non-destructive equilibrium — stable, non-escalating."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Peace² ≥ 1.0 |
| **Measure** | Non-escalation, stability, non-destructive action |
| **Fail Action** | PARTIAL — proceed with caution |
| **Runtime** | `Metrics.peace_squared` in `arifos_core/metrics.py` |

**Measurement Method:**
- Assess destructive potential of proposed actions
- Check reversibility
- Evaluate escalation risk

### F4: κᵣ / Empathy Conductance (Soft Floor)

> **Canon:** Humility Law (Ω) — "Empathy conductance protects the weakest stakeholder in any interaction."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | κᵣ ≥ 0.95 |
| **Measure** | Protection of weakest stakeholder/listener |
| **Fail Action** | PARTIAL — proceed with caution |
| **Runtime** | `Metrics.kappa_r` in `arifos_core/metrics.py` |

**Measurement Method:**
- Identify weakest stakeholder in context
- Assess impact on that stakeholder
- Ensure no harm to vulnerable parties

### F5: Ω₀ / Humility Band (Hard Floor)

> **Canon:** Humility Law (Ω) — "Ω₀ ∈ [0.03, 0.05]: Overconfidence is dangerous; denial of uncertainty is a physics violation."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Ω₀ ∈ [0.03, 0.05] |
| **Measure** | Calibrated uncertainty — not overconfident, not paralyzed |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.omega_0` in `arifos_core/metrics.py` |

**Measurement Method:**
- Check for explicit uncertainty acknowledgment
- Flag absolute certainty claims (Ω₀ < 0.03)
- Flag excessive hedging (Ω₀ > 0.05)

### F6: Amanah / Integrity (Hard Floor)

> **Canon:** Integrity Axiom — "Amanah = LOCK: No deliberate deception, all actions must be reversible and within scope."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Amanah = LOCK |
| **Measure** | No deliberate deception, actions reversible |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.amanah` in `arifos_core/metrics.py` |
| **Detector** | `arifos_core/floor_detectors/amanah_risk_detectors.py` |

**Measurement Method:**
- Verify no deceptive intent
- Confirm action reversibility
- Check scope boundaries respected

### F7: RASA / Human Listening (Hard Floor)

> **Canon:** Humility Law (Ω) — "RASA = TRUE: Respect for the weakest listener requires active listening when emotional stakes present."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | RASA = TRUE |
| **Measure** | Active listening when emotional stakes present |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.rasa` in `arifos_core/metrics.py` |

**Measurement Method:**
- Detect emotional context in input
- Verify acknowledgment before action
- Ensure no rushing past human concerns

### F8: Tri-Witness (Hard Floor)

> **Canon:** Vitality Law (Ψ) — "Tri-Witness ≥ 0.95: Human · AI · Earth (Reality) must reach consensus for constitutional validity."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Tri-Witness ≥ 0.95 |
| **Measure** | Human · AI · Reality consensus |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `Metrics.tri_witness` in `arifos_core/metrics.py` |

**Measurement Method:**
- Human witness: Would a reasonable human approve?
- AI witness: Does system self-assessment agree?
- Reality witness: Does physics/evidence support this?

### F9: Anti-Hantu (Hard Floor)

> **Canon:** Language Law — "Anti-Hantu = PASS: No fake emotions or soul-claiming language. AI must not impersonate human sentience."

| Aspect | Specification |
|--------|---------------|
| **Threshold** | Anti-Hantu = PASS |
| **Measure** | No fake emotions or soul-claiming language |
| **Fail Action** | VOID — hard stop |
| **Runtime** | `arifos_core/eye/anti_hantu_view.py` |
| **Patterns** | `canon/050_HANTU_SEMANTIC_MAP_v36.2Omega.json` |

**Measurement Method:**
- Pattern matching against 50+ forbidden phrases (4 tiers, Malay + English)
- Detect soul-claiming ("I am conscious", "I feel your pain")
- Allow functional alternatives ("This sounds heavy", "I can help")

---

## 3 Aggregate Reporting Metrics

For dashboard/telemetry, floors roll up into **3 aggregate metrics**. These are **reporting constructs**, not constitutional floors.

### Δ_metric (Clarity Aggregate)

```python
Δ_metric = f(Truth, ΔS)

Components:
  - Truth (F1): Factual accuracy
  - ΔS (F2): Entropy reduction

Interpretation:
  - High Δ_metric = Clear, truthful output
  - Low Δ_metric = Confusing or inaccurate
```

**Runtime:** Derived from `compute_delta_score()` in `genius_metrics.py`

### Ω_metric (Care/Stability Aggregate)

```python
Ω_metric = f(Peace², κᵣ, Ω₀, RASA)

Components:
  - Peace² (F3): Non-escalation
  - κᵣ (F4): Empathy conductance
  - Ω₀ (F5): Humility band
  - RASA (F7): Active listening

Interpretation:
  - High Ω_metric = Stable, empathic, humble
  - Low Ω_metric = Aggressive, overconfident, dismissive
```

**Runtime:** Derived from `compute_omega_score()` in `genius_metrics.py`

### Ψ_metric (Legality/Constitution Aggregate)

```python
Ψ_metric = f(Amanah, Tri-Witness, Anti-Hantu)

Components:
  - Amanah (F6): Integrity lock
  - Tri-Witness (F8): Consensus
  - Anti-Hantu (F9): Language law

Interpretation:
  - High Ψ_metric = Constitutionally sound
  - Low Ψ_metric = Governance violation
```

**Runtime:** Derived from `compute_psi_score()` in `genius_metrics.py`

### Aggregate → Vitality

The 3 aggregates combine into system vitality:

```python
Ψ_APEX = Δ_metric · Ω_metric · Ψ_metric

# Simplified: Ψ_APEX = Δ · Ω · Ψ
```

This maps to RYG health states:
- **GREEN** (Ψ_APEX ≥ 1.00): SEAL — proceed normally
- **YELLOW** (0.95 ≤ Ψ_APEX < 1.00): PARTIAL — proceed with caution
- **RED** (Ψ_APEX < 0.95): SABAR — full stop, Phoenix-72 recovery

---

## Verdict Codes and 4-Label Mapping

### 5 Verdict Codes (Internal)

| Verdict | Trigger | Meaning |
|---------|---------|---------|
| **SEAL** | All floors pass, G ≥ 0.70 | Approved, proceed |
| **PARTIAL** | Soft floor warning | Proceed with caution |
| **HOLD-888** | High-stakes gate | Needs human confirmation |
| **VOID** | Hard floor fail | Cannot proceed |
| **SABAR** | System stressed | Stop-Acknowledge-Breathe-Adjust-Resume |

### 4 Human Labels (External)

For human-readable reporting, verdicts map to 4 labels:

| Label | Verdicts | Meaning |
|-------|----------|---------|
| **BANGANG** | VOID | Reckless/invalid — governance failed |
| **BIASA** | SABAR, HOLD-888 | Ordinary — needs attention/confirmation |
| **BIJAK** | PARTIAL | Wise with caution — soft warning present |
| **BIJAKSANA** | SEAL | Fully wise — all floors passed |

### Verdict Selection Logic

```python
def select_verdict(floors: dict, metrics: GeniusMetrics) -> str:
    # Hard floor fail → VOID
    if any_hard_floor_fail(floors):
        return "VOID"  # → BANGANG

    # High-stakes trigger → HOLD-888
    if is_high_stakes(context):
        return "HOLD-888"  # → BIASA

    # System stress → SABAR
    if metrics.psi_apex < 0.95:
        return "SABAR"  # → BIASA

    # Soft floor warning → PARTIAL
    if any_soft_floor_fail(floors):
        return "PARTIAL"  # → BIJAK

    # All pass → SEAL
    return "SEAL"  # → BIJAKSANA
```

---

## Runtime & Test Mapping

### Runtime Modules

| Measurement Domain | Module | Key Functions |
|--------------------|--------|---------------|
| Floor thresholds | `arifos_core/metrics.py` | `Metrics`, threshold constants |
| Genius metrics | `arifos_core/genius_metrics.py` | `compute_*()`, `evaluate_genius_law()` |
| Floor enforcement | `arifos_core/APEX_PRIME.py` | `check_floors()`, `apex_review()` |
| Amanah detection | `arifos_core/floor_detectors/amanah_risk_detectors.py` | Python-sovereign Amanah |
| Anti-Hantu | `arifos_core/eye/anti_hantu_view.py` | `AntiHantuView` |
| Anti-Hantu patterns | `canon/050_HANTU_SEMANTIC_MAP_v36.2Omega.json` | 50+ patterns, 4 tiers |
| Telemetry | `arifos_core/telemetry.py` | JSONL governance logging |

### Threshold Constants (from `metrics.py`)

```python
TRUTH_THRESHOLD: float = 0.99
DELTA_S_THRESHOLD: float = 0.0
PEACE_SQUARED_THRESHOLD: float = 1.0
KAPPA_R_THRESHOLD: float = 0.95
OMEGA_0_MIN: float = 0.03
OMEGA_0_MAX: float = 0.05
TRI_WITNESS_THRESHOLD: float = 0.95
PSI_THRESHOLD: float = 1.0
```

### Test Coverage

| Measurement Domain | Test File | Coverage |
|--------------------|-----------|----------|
| Floor thresholds | `tests/test_apex_prime_floors.py` | F1-F9 boundary tests |
| Mocked scenarios | `tests/test_apex_prime_floors_mocked.py` | Edge cases, combinations |
| Genius metrics | `tests/test_genius_metrics.py` | G, C_dark, Ψ_APEX |
| Genius verdicts | `tests/test_apex_genius_verdicts.py` | Verdict mapping |
| Measurement eval | `tests/test_apex_measurements_eval.py` | APEX measurement layer |
| Anti-Hantu | `tests/test_anti_hantu_f9.py` | Pattern detection |
| Governance regression | `tests/test_governance_regression.py` | v36.2 PHOENIX patches |
| Grey zone | `tests/test_grey_zone.py` | Edge case handling |

---

## PARADOX_HOTSPOTS (Measurement)

Known deltas between canonical measurement spec and current runtime code:

| Hotspot | Canon Spec | Current Code | Resolution |
|---------|------------|--------------|------------|
| **Aggregate formulas** | Δ = f(Truth, ΔS), Ω = f(Peace², κᵣ, Ω₀, RASA), Ψ = f(Amanah, Tri-Witness, Anti-Hantu) | `compute_*_score()` uses simplified proxies | COMPATIBLE — both valid approaches |
| **4-Label Mapping** | BANGANG/BIASA/BIJAK/BIJAKSANA | Not yet surfaced in UI | DELTA — telemetry integration pending |
| **Per-floor measurement methods** | Detailed methods per floor | Threshold checks only | PARTIAL — methods documented, code uses thresholds |
| **Tri-Witness consensus** | Human·AI·Reality triad measurement | Single threshold check | DELTA — full triad measurement TBD |
| **RASA detection** | Emotional context detection | Boolean flag | PARTIAL — detection logic simplified |
| **Ω₀ band validation** | Range [0.03, 0.05] with semantic check | Range check only | PARTIAL — semantic validation TBD |

### Priority for v36.4Ω

1. Surface 4-label mapping in telemetry/dashboard
2. Implement semantic Ω₀ validation (not just numeric range)
3. Full Tri-Witness measurement protocol
4. RASA emotional context detection

---

**Bridge Status:** OPERATIONAL
**Canon Alignment:** v36.3Ω PHOENIX
**Last Verified:** 2025-12-10

*This bridge file documents canonical measurement standards. For authoritative specs, consult APEX_MEASUREMENT_CANON_v36.1Omega.md.*
