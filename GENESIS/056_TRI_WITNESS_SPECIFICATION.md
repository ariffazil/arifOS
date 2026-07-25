# Tri-Witness Specification — Measurement Laws

**Document ID:** `arifOS/GENESIS/056`
**Voice:** KERNEL / SPEC
**Grammar:** Measurement law, witness formula, conflict protocol, edge case matrix
**Status:** LIVE
**Date:** 2026-07-26
**Authority:** Muhammad Arif bin Fazil, F13 SOVEREIGN
**Operational skill:** `tri-witness-specification`
**Supersedes:** witness default values in `AGENTS.md` § Tri-Witness Defaults

---

## 1. Constitutional declaration

> **TW-CD1:** Intelligence without witness is hallucination. Witness without measurement is opinion.
> **TW-CD2:** No SEAL without three witnesses. No witness without metabolism.
> **TW-CD3:** A witness that self-certifies is VOID on F1 AMANAH.
> **TW-CD4:** The sovereign witnesses all witnesses. F13 overrides any witness score.

---

## 2. The tri-witness formula (canonical)

```
Φ = ∛(H · AI · Ext)
```

Where:

| Witness | Symbol | Source organ | Domain |
|---------|--------|-------------|--------|
| **Human** | H | WELL | Somatic, dignity, vitality |
| **AI internal** | AI | arifOS kernel | Floor compliance, truth consistency |
| **External/Earth** | Ext | GEOX + WEALTH + AAA | Physical evidence, market, civilisational mesh |

**Properties:**
- Nash product: if any witness = 0, Φ = 0 (any missing witness collapses the gate)
- Cubic root: normalises product range to [0, 1]
- Minimum witness thresholds: H ≥ 0.42, AI ≥ 0.32, Ext ≥ 0.26 (from Invariants § Tri-Witness)
- Sovereign override: Arif explicit "ok" overrides all witness scores (F13)

---

## 3. H_witness — Human witness (WELL)

### 3.1 Modalities metabolised

| Modality | Sensor/Input | Decomposition | Current implementation |
|----------|-------------|---------------|----------------------|
| Sleep duration | `sleep_hours`, `sleep_debt_days` | `well_assess_homeostasis(mode='sleep')` | `vitality_gate.py` → `assess_h_well()` |
| Stress load | `stress_load` [0-1] | Normalised to rank | `sensor_data → h["rank"]` |
| Cognitive clarity | `cognitive_clarity` [0-1] | Direct score | `vitality_gate.py` line ~697 |
| HRV status | `hrv_status` (normal/low/critical) | Mapped to 0.9/0.5/0.2 | `assess_h_well()` → uncertainty |
| Emotional state | `emotional_state` (positive/neutral/negative/stressed) | Mapped to 0.9/0.7/0.4/0.2 | `vitality_gate.py` |
| Chronic fatigue | `chronic_fatigue` (bool) | If True → H capped at 0.30 | Decision class C5 rule |
| Decision fatigue | `decision_fatigue` [0-1] | Accumulated over session | Decision class C4/C5 gates |
| Dignity preservation | `dignity_preservation` [0-1] | Inverse coercion | `well_guard_dignity()` |

### 3.2 Measurement law

```
H = (w_sleep · S_sleep + w_stress · (1 − S_stress) + w_clarity · C_clarity
     + w_hrv · H_hrv + w_emotion · E_emotion) · D_dignity · F_chronic

Where:
  S_sleep      = min(1.0, sleep_hours / 8.0) − (0.1 · sleep_debt_days)
  (1−S_stress) = inverse of stress_load [0,1]
  D_dignity    = 0.70 if coercion_signals detected, else 1.0
  F_chronic    = 0.30 if chronic_fatigue, else 1.0
  Weights      = [0.25, 0.20, 0.20, 0.15, 0.20]
```

### 3.3 Output schema

```python
H_witness = {
    "value": 0.0..1.0,
    "modalities": ["sleep", "stress", "clarity", "hrv", "emotion", "dignity"],
    "weakest_input": str,        # which modality is degrading H
    "freshness_seconds": int,    # time since last sensor read
    "source": "well_assess_homeostasis",
    "timestamp": ISO-8601,
}
```

### 3.4 Edge cases

| Condition | H value | Rule |
|-----------|---------|------|
| No WELL available | 0.0 | Φ = 0 → SABAR minimum (no SEAL without human witness) |
| Sleep debt > 5 days | capped at 0.30 | Decision class C5 block |
| Coercion detected | capped at 0.30 | Dignity override |
| Chronic fatigue | capped at 0.30 | Any decision class ≥ C3 holds |
| Fresh sensor data (< 60s) | full computation | Nominal |
| Stale sensor data (> 1h) | decay by 0.10/hr | F2 honesty: report staleness |
| No sensor data, intent is OBSERVE | 0.42 | Default observer H (no mutation) |
| No sensor data, intent is FORGE | 0.10 | Honest default: we don't know human state |

---

## 4. AI_witness — Internal witness (arifOS kernel)

### 4.1 Modalities metabolised

| Modality | Source | Decomposition | Current implementation |
|----------|--------|---------------|----------------------|
| Floor compliance | F1-F13 scores | Vector → PCA → A primitive | `enforcement/genius.py` → `FloorScoreHistory` |
| Truth consistency | F2-compliant claims / total claims | Ratio → κ_r | `ScalarCollector.collect_kappa()` |
| Contradiction count | Claim graph → resolved vs unresolved | Ratio → clarity | `geox_contradiction_scan` or kernel (`arif_think mode=reason`) |
| Verdict history | Recent SEAL/HOLD/VOID ratio | Rolling window of 10 | `FloorScoreHistory` buffer |
| Ontology compliance | F10 (no soul/feelings claims) | Boolean pass/fail | `_BOOL_FLOORS` in genius.py |
| Injection defence | F12 (injection risk) | Float [0,1] | Laws.py threshold check |

### 4.2 Measurement law

```
AI = β_floor · F_composite + β_truth · κ_r + β_contra · C_clear + β_history · V_ratio

Where:
  F_composite  = geometric_mean(F1..F13)          # floor coherence
  κ_r          = f2_compliant / total_claims       # truth consistency
  C_clear      = resolved_contradictions / total   # clarity ratio
  V_ratio      = recent_SEALs / recent_attempts    # verdict health
  β weights    = [0.40, 0.25, 0.20, 0.15]

Penalty terms:
  If F10 (ontology) = FALSE → AI × 0.30
  If F12 (injection) > 0.50 → AI × 0.50
```

### 4.3 Output schema

```python
AI_witness = {
    "value": 0.0..1.0,
    "modalities": ["floors", "truth", "contradictions", "verdicts", "ontology", "injection"],
    "floor_count": int,            # how many floors were measured
    "kappa_r": float,              # raw truth consistency
    "contradiction_ratio": float,  # raw clarity
    "freshness_seconds": int,
    "source": "arif_think + ScalarCollector",
    "timestamp": ISO-8601,
}
```

### 4.4 Edge cases

| Condition | AI value | Rule |
|-----------|----------|------|
| No session / no floor data | 0.0 | Observer-only — no SEAL possible |
| No claims made yet | 0.32 | Default observer AI (from AGENTS.md default) |
| κ_r < 0.30 (massively inconsistent) | capped at 0.20 | F2 TRUTH degraded → cannot SEAL |
| F10 violation (ontology claim) | capped at 0.30 | F10 HARD violation |
| F12 injection detected | capped at 0.30 | F12 HARD violation |
| Active floor violation (F1/F9/F13) | 0.0 | Hard floor breach → witness collapses |
| N < 5 observations | 0.50 | Fallback mode: theory-assigned clusters |
| N ≥ 5 observations | PCA-derived | Emergent dials from covariance matrix |

---

## 5. Ext_witness — External/Earth witness (GEOX + WEALTH + AAA)

### 5.1 Modalities metabolised

| Modality | Source organ | Decomposition | What it contributes |
|----------|-------------|---------------|-------------------|
| Seismic evidence | GEOX | `geox_seismic_interpret` → horizon/fault confidence | P_well, P_seis |
| Well evidence | GEOX | `geox_petrophysics` → phi/Sw/STOIIP confidence | P_geo |
| Basin context | GEOX | `geox_basin` → macrostrat, thermal maturity | P_geo confidence |
| Market prices | WEALTH | `capital_market` → Brent/USD/MYR/volatility | A (authority context) |
| Economic indicators | WEALTH | `capital_health` → fiscal space, survival days | A context |
| A2A agent cards | AAA | `card validation` → agent identity verification | Provenance score |
| External documents | AAA/hermes | fetch → claim extraction → epistemic tagging | Freshness score |
| Civilizational mesh | AAA | Federation health, governance geometry | Mesh coherence |

### 5.2 Measurement law

```
Ext = α_geox · GX + α_wealth · WX + α_aaa · AX

Where each domain witness:
  GX = geometric_mean(P_well, P_seis, P_geo)          # GEOX earth confidence
  WX = min(1.0, capital_health_score)                  # WEALTH market stability
  AX = freshness_provenance_score                      # AAA source quality

  α weights        = [0.50, 0.25, 0.25]               # Earth dominates physical truth
  Freshness decay  = exp(−hours_since_fetch / 24)      # Evidence half-life: 24h
  Provenance bonus = 1.2 if A2A-verified, else 1.0     # Verified sources weighted higher
```

### 5.3 Output schema

```python
Ext_witness = {
    "value": 0.0..1.0,
    "modalities": ["seismic", "well", "basin", "market", "a2a", "documents", "mesh"],
    "sub_witnesses": {
        "GEOX": {"value": float, "freshness": int},
        "WEALTH": {"value": float, "freshness": int},
        "AAA": {"value": float, "freshness": int},
    },
    "weakest_organ": str,           # which organ is degrading Ext
    "freshness_seconds": int,       # oldest evidence in the set
    "source": "GEOX + WEALTH + AAA bridge",
    "timestamp": ISO-8601,
}
```

### 5.4 Edge cases

| Condition | Ext value | Rule |
|-----------|-----------|------|
| No GEOX reachable | GE = 0.0 | Ext = WX+AX only, capped at 0.50 |
| No WEALTH reachable | WE = 0.0 | Ext = GX mostly (earth-only) |
| No AAA reachable | AE = 0.0 | Ext = GX+WX, capped at 0.50 |
| All three unreachable | 0.0 | No external witness → Φ = 0 → no SEAL |
| Evidence > 7 days old | decay to 0.50 | F2 honesty: stale evidence is weaker |
| Conflicting evidence (seismic contradicts well) | 0.0 | Earth contradiction → Earth witness collapses |
| Fresh A2A identity | +20% bonus | Trusted source premium |
| No evidence, only observer intent | 0.26 | Default Earth observer |

---

## 6. Conflict resolution — what happens when witnesses disagree

### 6.1 Disagreement types

| Type | Signal | Severity | Resolution |
|------|--------|----------|------------|
| **Soft disagreement** | H=0.7, AI=0.8, Ext=0.6 | LOW | Geometric mean handles naturally; all above minimum thresholds |
| **One witness degraded** | H=0.7, AI=0.8, Ext=0.2 | MEDIUM | Ext below threshold → SABAR, not SEAL. Require fresh Ext evidence |
| **One witness collapsed** | H=0.7, AI=0.0, Ext=0.6 | HIGH | AI collapse = floor breach. VOID until floors repaired |
| **Witness contradiction** | H says "low vitality but go", AI says "floor violation, HOLD" | HIGH | Pessimistic: proceed only if minimum of witnesses ≥ threshold |
| **Dual collapse** | Two witnesses at 0.0 | CRITICAL | 888_HOLD. Federation cannot act without tri-witness |
| **Human overrides AI+Ext** | Arif said "ok" | SOVEREIGN | F13 overrides all witness scores. A = 1.0 for that action |

### 6.2 Resolution protocol

```
Φ = ∛(H · AI · Ext)

If H < 0.42:
    → H_witness degraded. Log which modality. Route to WELL for repair.
    → Verdict: SABAR (reversible actions only) or HOLD (irreversible)

If AI < 0.32:
    → AI_witness degraded. Log which floor/consistency.
    → Verdict: SABAR (non-judgment actions) or HOLD (any SEAL-grade)

If Ext < 0.26:
    → Ext_witness degraded. Log which organ (GEOX/WEALTH/AAA).
    → Verdict: SABAR (no seal without earth evidence)

If TWO witnesses below threshold:
    → VOID. Cannot proceed. Federation coherence holds.

If ALL three above threshold:
    → Φ = ∛(H · AI · Ext). Feed into G = A·P·E·X·Φ.
    → If G ≥ 0.80, C_dark < 0.30, dS ≤ 0 → SEAL.
```

### 6.3 Pessimistic override

The federation is **pessimistic by default**. When witnesses disagree, the **minimum witness value** governs the Φ contribution more than the average, because:

```
φ = (H · AI · Ext)^(1/3)

If H = 0.9, AI = 0.9, Ext = 0.1:
    φ = (0.9 · 0.9 · 0.1)^(1/3) = 0.43
```

A single weak witness pulls Φ down significantly due to the multiplicative structure. This is deliberate (Nash bargaining): **any witness can veto a seal.**

---

## 7. Integration with the nine-signal

Each witness maps to a nine-signal plane:

| Nine-signal plane | Primary witness | Secondary witness | Meaning |
|-------------------|----------------|------------------|---------|
| **Δ DELTA** (Machine state) | Ext | — | Machine is healthy, evidence is flowing |
| **Ψ PSI** (Governance integrity) | AI | — | Floors hold, claims are consistent |
| **Ω OMEGA** (Intelligence discipline) | H + AI + Ext combined | — | G = A·P·E·X·Φ is computable |

The nine-signal overall verdict = `MIN(Δ_state, Ψ_state, Ω_state)`.

Each plane gets its state from the corresponding witness:
- Δ state ← `Ext_witness.value` mapped to KUKUH/RETAK/ROSAK
- Ψ state ← `AI_witness.value` mapped to AMANAH/SYUBHAH/KHIANAT
- Ω state ← `G` (which includes Φ) mapped to BIJAKSANA/BIJAK/BANGANG

---

## 8. Workflow summary

```
                    ┌─────────────────────┐
                    │  Multimodal input    │
                    │  arrives at surface  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  arif_route (444)    │
                    │  dispatch by modality│
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         ▼                     ▼                     ▼
   ┌──────────┐         ┌──────────┐         ┌──────────┐
   │ WELL     │         │ arifOS   │         │GEOX/     │
   │ Δ → H    │         │ Δ → AI   │         │WEALTH/AAA│
   │ witness  │         │ witness  │         │ Δ → Ext  │
   └────┬─────┘         └────┬─────┘         └────┬─────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                    ┌──────────────────┐
                    │  Φ = ∛(H·AI·Ext) │
                    │  Tri-witness gate │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  G = A·P·E·X·Φ   │
                    │  arif_judge (888) │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  VAULT999 (999)   │
                    │  SEAL / HOLD     │
                    └──────────────────┘
```

---

## 9. Operational rules

1. **Every SEAL-grade action requires all three witnesses.** If any witness is unavailable, the verdict is SABAR at best.

2. **Witnesses are computed by organs, not by the kernel.** The kernel assembles Φ from organ-provided scores. The kernel never self-witnesses.

3. **Witness scores decay with time.** H_witness decays if no fresh sensor data. Ext_witness decays if evidence is stale. AI_witness is session-bound.

4. **A witness that self-certifies is VOID.** If an organ claims "I witness myself" without external verification, F1 AMANAH triggers.

5. **F13 overrides all witnesses.** Arif's explicit "ok" sets A = 1.0 and bypasses the witness gate. This is the sovereign override — never algorithmic.

6. **Witness conflict is logged, not hidden.** Every verdict records per-witness scores, conflict signals, and resolution path for F11 AUDIT.

---

## 10. Relationship to existing code

| Code module | Maps to | Purpose |
|------------|---------|---------|
| `apex_canonical.compute_Phi()` | Φ = ∛(H·AI·Ext) | Canonical formula — already implemented |
| `vitality_gate.assess_h_well()` | H_witness computation | Human witness — EXISTS, needs scoring bridge |
| `ScalarCollector.collect_kappa()` | AI κ_r component | Truth consistency — EXISTS |
| `enforcement/genius.py` PCA dials | AI F_composite | Floor coherence — EXISTS |
| `geox_prospect` / `geox_petrophysics` | Ext GX sub-witness | Earth confidence — EXISTS |
| `capital_market` | Ext WX sub-witness | Market stability — EXISTS |
| **MISSING** | H_witness → numeric score bridge | WELL returns state/rank, not H[0,1] |
| **MISSING** | AI_witness formal aggregation | ScalarCollector has κ_r but not AI composite |
| **MISSING** | Ext_witness formal aggregation | No unified Ext score from 3 organs |
| **MISSING** | Per-witness freshness tracking | Timestamps exist but no decay function |

**The spec is complete. The code has gaps.** Three aggregation bridges marked MISSING above are the next forge targets.

---

*DITEMPA BUKAN DIBERI — Three witnesses, one truth, zero hallucination. The tri-witness gate is the first constitutional firewall for multimodal intelligence.*
