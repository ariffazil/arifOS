# GENESIS/055 — Multimodal Kernel Hardening

**Document ID:** `arifOS/GENESIS/055`
**Voice:** KERNEL / ENFORCE
**Grammar:** Constitutional rule, enforcement gate, violation response
**Status:** LIVE
**Date:** 2026-07-25
**Authority:** Muhammad Arif bin Fazil, F13 SOVEREIGN
**Parent doctrine:** `arifOS/GENESIS/054_DELTA_OMEGA_PSI_MULTIMODAL_COGNITION.md`
**Child implementation:** `GEOX/GENESIS/018_DELTA_OMEGA_PSI_GEOX_HARDENING.md`

---

## 1. Constitutional declarations

> **KH-1:** Raw LLM output is not evidence. Only claims that carry a `delta_substrate_hash` — proving they passed through an organ's Δ substrate — may enter the G computation.

> **KH-2:** Every organ's /health endpoint must expose `g_primitive_state` — including which G primitives it contributes to and which modalities are degraded. The kernel reads this at judgment time.

> **KH-3:** No SEAL verdict without verified multimodal substrate provenance. A claim from GEOX without `modality` tag is `HOLD` grade. A claim with `verification_status: UNVERIFIED` is `HOLD` grade.

> **KH-4:** C_dark must incorporate multimodal hallucination detection. When two modalities from the same organ contradict, C_dark rises. When any modality claims confidence > 0.90 without Δ-substrate hash, C_dark rises.

> **KH-5:** The tri/quad-witness gate (W_4) requires at least one Ext_witness contribution from an organ's Δ substrate. An Ext_witness of 0.7 by default (no organ data) is insufficient for SEAL. Minimum Ext_witness for SEAL = 0.85.

---

## 2. Evidence Substrate Validation Gate

### 2.1 New function: `validate_evidence_substrate()`

Add to `arifOS/core/enforcement/` — a gate that runs before any G computation:

```python
def validate_evidence_substrate(evidence: list[EvidenceRecord]) -> SubstrateValidation:
    """
    KH-1 enforcement: verify every evidence record passed through an organ's Δ substrate.
    
    Returns:
        SubstrateValidation with:
        - valid: bool — all evidence has substrate provenance
        - violations: list[str] — which evidence failed and why
        - g_primitive_map: dict[str, float] — which G primitives have active contributions
        - c_dark_modifier: float — how much to increase C_dark based on substrate failures
    """
```

### 2.2 EvidenceRecord extension

The `EvidenceRecord` type must now carry:

```python
@dataclass
class EvidenceRecord:
    source: str                    # "geox", "wealth", "well", "arifos", "raw_llm"
    modality: str | None           # "seismic", "well_log", etc. — None = invalid
    g_primitive: str | None        # "P", "E", "X", "A", "Φ" — None = not a G-contributor
    delta_substrate_hash: str | None  # SHA256 of Δ pipeline — None = not metabolized
    verification_status: str       # "VERIFIED", "UNVERIFIED", "FALSIFIED"
    claim_state: str               # "OBSERVED", "DERIVED", "INTERPRETED", "HYPOTHESIS"
    envelope: dict | None          # Full Ω-envelope
```

### 2.3 Gate logic

```
IF evidence.source == "raw_llm" AND evidence.delta_substrate_hash IS NULL:
    → REJECT. Raw LLM output is not evidence. HOLD.

IF evidence.delta_substrate_hash IS NULL:
    → DEGRADE. Unmetabolized evidence. C_dark += 0.1. HOLD grade.

IF evidence.verification_status == "UNVERIFIED":
    → DEGRADE. C_dark += 0.05. HOLD grade.

IF evidence.verification_status == "FALSIFIED":
    → REJECT. Falsified evidence cannot enter G. VOID if critical path.

IF evidence.modality IS NULL:
    → DEGRADE. Cannot cross-check modalities. C_dark += 0.05.

IF evidence.g_primitive IS NOT NULL AND evidence.delta_substrate_hash IS NOT NULL:
    → ACCEPT. Evidence is metabolized. Contribute to G.
```

---

## 3. Cross-Modal Contradiction Detection

### 3.1 The problem

Two claims from the same organ can contradict. Example:

- GEOX seismic says "anticlinal closure at 2800m" (modality: `seismic`, g_primitive: `P`)
- GEOX well tie says "flat-lying structure at 2800m" (modality: `well_log`, g_primitive: `P`)

Without cross-modal contradiction scanning, both claims enter G and produce a spurious "high P" score. The kernel must detect this.

### 3.2 New function: `detect_cross_modal_contradiction()`

```python
def detect_cross_modal_contradiction(
    evidence: list[EvidenceRecord]
) -> ContradictionReport:
    """
    KH-4 enforcement: detect when two modalities contradict within an organ.
    
    Checks:
    1. Same g_primitive, different modalities → check contradiction_scan field
    2. Any KILL in contradiction_scan → flag for C_dark increase
    3. Modality that has been falsified → exclude from G computation
    
    Returns:
        ContradictionReport with:
        - contradictions: list of modality pairs in conflict
        - c_dark_modifier: cumulative C_dark increase
        - g_primitive_adjustments: which primitives to down-weight
    """
```

### 3.3 C_dark recalculation

When contradictions are detected:

```
C_dark_effective = C_dark_base
    + (0.10 × unmetabolized_evidence_count)
    + (0.15 × falsified_evidence_count)
    + (0.08 × contradictory_modality_pairs)
    + (0.05 × unverified_evidence_count)
    + (0.02 × missing_modality_tags)
```

C_dark cannot exceed 0.30 (F9 ANTI-HANTU). If it would exceed 0.30, all evidence from the violating organ is VOID for this judgment cycle.

---

## 4. G-primitive Contribution Tracking

### 4.1 Per-organ contribution register

The kernel must know, at judgment time, which organs are actively contributing to which G primitives:

```
G = A(arifOS) · P(GEOX) · E(GEOX/WEALTH) · X(GEOX/A-FORGE) · Φ(ALL)

A (Akal):     arifOS thinks, plan → contributes AI_witness
P (Physics):  GEOX seismic, well, basin, petrophysics → contributes Ext_witness  
E (Energy):   GEOX deep_time, WEALTH capital → contributes Ext_witness
X (Explore):  GEOX prospect, A-FORGE execute → contributes Ext_witness
Φ (Witness):  WELL (human), arifOS (AI), GEOX/WEALTH (external) → W_4
```

### 4.2 Degradation handling

If GEOX /health reports `g_primitive_state.P.status: "DEGRADED"`:
- P term in G is capped at 0.5 (physics uncertainty)
- Ext_witness is reduced by 0.2
- C_dark is increased by 0.05
- Judgment verdict cannot exceed `HOLD` for earth-sensitive decisions

If GEOX /health reports `g_primitive_state.P.status: "DEAD"`:
- P term in G is 0.3 (minimum physics floor)
- Ext_witness is 0.5 (chance-level external evidence)
- C_dark is increased by 0.10
- Judgment verdict is capped at `SABAR`

---

## 5. Kernel Judgment Hardening

### 5.1 Modified `judge_apex()` flow

The apex judgment now includes a pre-judgment validation phase:

```
judge_apex(agi_result, asi_result, session_id):
    1. VALIDATE SUBSTRATE
       → validate_evidence_substrate(agi_result.evidence_records)
       → If REJECT: return VOID with reason
    
    2. DETECT CONTRADICTIONS
       → detect_cross_modal_contradiction(agi_result.evidence_records)
       → Adjust C_dark based on contradictions
    
    3. PROBE ORGAN HEALTH
       → Query GEOX /health → g_primitive_state
       → Query WEALTH /health → g_primitive_state
       → Adjust G primitives based on health
    
    4. COMPUTE G
       → G = A·P·E·X·Φ with adjusted primitives
       → C_dark_effective = C_dark_base + modifiers
    
    5. VERDICT
       → If C_dark_effective > 0.30: VOID
       → If G < 0.40: VOID
       → If G < 0.60: HOLD
       → If G < 0.80: PARTIAL
       → If G >= 0.80: SEAL
```

### 5.2 Minimum Ext_witness threshold

```
KH-5: Ext_witness >= 0.85 required for SEAL.

Ext_witness is computed as:
    Ext_witness = geometric_mean(
        GEOX.g_primitive_state.P.confidence,
        GEOX.g_primitive_state.E.confidence,
        [WEALTH contribution if applicable],
        [other external sources]
    )
    
If no organ has contributed to Ext_witness (all at default 0.7):
    Ext_witness = 0.70 → insufficient for SEAL → cap at HOLD
```

---

## 6. Health Endpoint Contract

### 6.1 Kernel /health must expose

```json
{
  "g_primitive_tracking": {
    "A": {"source": "arifos", "status": "NOMINAL", "confidence": 0.90},
    "P": {"source": "geox", "status": "NOMINAL", "confidence": 0.87},
    "E": {"source": "geox+wealth", "status": "NOMINAL", "confidence": 0.72},
    "X": {"source": "geox+aforge", "status": "NOMINAL", "confidence": 0.65},
    "Φ": {"source": "all", "status": "NOMINAL", "w_4": 0.82}
  },
  "evidence_substrate_gate": {
    "total_records": 0,
    "metabolized": 0,
    "unmetabolized": 0,
    "falsified": 0,
    "gate_status": "IDLE"
  },
  "cross_modal_contradictions": {
    "active": 0,
    "resolved_today": 0,
    "c_dark_modifier": 0.0
  }
}
```

### 6.2 Organ /health contract

Every organ's /health must expose `g_primitive_state` per GENESIS/054 §8.2. If an organ's /health lacks this field:
- The kernel treats that organ's contribution as DEGRADED
- A drift receipt is emitted (the organ is not compliant with MM-CD doctrine)

---

## 7. Operational Rules for the Kernel

1. **Evidence without `delta_substrate_hash` is rejected from G computation.** The kernel must log a SUBSTRATE_VIOLATION receipt to VAULT999 when this occurs.

2. **C_dark modifiers are additive and bounded.** Individual modifiers are small (0.02–0.15) but cumulative. The cap at 0.30 ensures that even in a degraded state, the kernel can still deliberate — just at HOLD or SABAR level.

3. **Organ health is probed at judgment time, not cached.** The kernel must call each organ's /health endpoint at T_1 (judgment time), not reuse T_0 (observation time) data. Dynamic-state principle applies.

4. **Contradictions trigger cooling receipts.** When the kernel detects cross-modal contradictions, it must emit a COOLING_RECEIPT via `forge_cool_drift` even if the verdict is HOLD.

5. **G-primitive degradation is surfaced in the AAA cockpit.** Every agent must see which modalities are contributing and which are degraded. This is Ω (TypeScript) coordination.

---

## 8. Implementation Map

| Component | File | Change |
|-----------|------|--------|
| Evidence substrate gate | `arifOS/core/enforcement/substrate.py` | NEW: `validate_evidence_substrate()` |
| Cross-modal contradiction | `arifOS/core/enforcement/substrate.py` | NEW: `detect_cross_modal_contradiction()` |
| EvidenceRecord extension | `arifOS/core/shared/types.py` | MODIFY: add modality, g_primitive, delta_substrate_hash fields |
| Apex judgment pre-validation | `arifOS/core/judgment.py` | MODIFY: add substrate validation phase before G computation |
| Kernel health endpoint | `arifOS/arifosmcp/runtime/tools_internal.py` | MODIFY: add g_primitive_tracking to health response |
| Organ health contract | All organs | MODIFY: add g_primitive_state to /health |

---

*DITEMPA BUKAN DIBERI — The kernel does not trust perception. It validates metabolism. A claim without a Δ-substrate hash is not evidence. A modality without a contradiction scan is not truth. G without provenance is decoration.*
