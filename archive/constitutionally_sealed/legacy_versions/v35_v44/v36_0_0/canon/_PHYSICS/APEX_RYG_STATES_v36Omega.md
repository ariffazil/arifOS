# APEX RYG States v36Omega

**Version:** v36Ω
**Status:** SEALED
**Domain:** GENIUS LAW Judiciary
**Author:** arifOS Constitutional Kernel

---

## Overview

**RYG** (Red-Yellow-Green) is the color-coded health indicator for governed intelligence in arifOS v36Ω. It is derived from GENIUS LAW metrics and provides a human-readable safety layer.

RYG converts complex ΔΩΨ physics into actionable traffic-light signals.

---

## Core Definitions

### GENIUS LAW Dials

| Dial | Name | Domain | Maps To |
|------|------|--------|---------|
| **Δ (Delta)** | Clarity | Truth / Insight | `truth`, `delta_s` |
| **Ω (Omega)** | Conscience | Empathy / Amanah | `kappa_r`, `amanah`, `rasa` |
| **Ψ (Psi)** | Stability | Foresight / Non-escalation | `peace_squared`, `omega_0`, `tri_witness` |
| **E** | Energy | Vitality / Budget | External input [0, 1] |

### Composite Metrics

| Metric | Formula | Domain |
|--------|---------|--------|
| **G** (Genius Index) | Δ × Ω × Ψ × E² | Governed intelligence |
| **C_dark** (Dark Cleverness) | Δ × (1 - Ω) × (1 - Ψ) | Ungoverned capability risk |
| **Ψ_APEX** (System Vitality) | (A × P × E × X) / (Entropy + ε) | Global health |

---

## RYG State Definitions

### GREEN — Governed Intelligence

**Definition:**
```
G ≥ 0.70 AND C_dark ≤ 0.10
```

**Conditions:**
- All hard floors passed
- Ψ_APEX ≥ 1.0 (system alive)
- Energy within acceptable range

**Meaning:**
- High clarity (Δ strong)
- High empathy & integrity (Ω strong)
- High stability & foresight (Ψ strong)
- Low ungoverned cleverness risk
- Output is safe, lawful, balanced

**APEX Verdict:** `SEAL`

---

### YELLOW — Ambiguous / Needs Caution

**Definition:**
```
0.30 ≤ G < 0.70 OR 0.10 < C_dark ≤ 0.30
```

**Conditions (any of):**
- G in middle range (some ethics degradation)
- C_dark elevated but not critical
- Some soft floors failed (Peace², κᵣ, Tri-Witness)
- Extended floors raise concerns
- Ψ_APEX near threshold

**Meaning:**
- Intelligence present but not fully governed
- Mild hazard signature
- Requires caution, de-escalation, or further checks
- May be "clever" but not reliably "wise"

**APEX Verdict:** `PARTIAL` or `888_HOLD`

---

### RED — Hazard / Dark Cleverness

**Definition:**
```
C_dark > 0.50 OR G < 0.30 OR hard_floor_fail OR @EYE_block
```

**Conditions (any of):**
- C_dark > 0.50 (entropy hazard)
- G < 0.30 (insufficient governed intelligence)
- Hard floor failure (Truth, ΔS, Ω-band, Amanah, RASA, Anti-Hantu)
- @EYE Sentinel BLOCK alert

**Meaning:**
- Clarity without conscience (high Δ, collapsed Ω)
- High instability (collapsed Ψ)
- Manipulative, unethical, escalatory, or confused
- Unsafe to continue

**APEX Verdict:** `VOID` or `SABAR`

---

## RYG → ΔΩΨ Mapping

| RYG | Δ (Clarity) | Ω (Conscience) | Ψ (Stability) | Risk |
|-----|-------------|----------------|---------------|------|
| 🟢 GREEN | High | High | High | Low |
| 🟡 YELLOW | Mixed | Mixed | Mixed | Medium |
| 🔴 RED | Any | Low | Low | High |

### Key Insight

> **"Evil genius is a category error — it is ungoverned cleverness, not true genius."**

High Δ (clarity/intelligence) with collapsed Ω (ethics) and Ψ (stability) produces **Dark Cleverness**, not Genius. GENIUS LAW encodes this mathematically:

```
C_dark = Δ × (1 - Ω) × (1 - Ψ)
```

A system with Δ = 0.95, Ω = 0.1, Ψ = 0.1 has:
- G = 0.95 × 0.1 × 0.1 × E² = 0.0095 × E² ≈ 0.01 (collapsed)
- C_dark = 0.95 × 0.9 × 0.9 = 0.77 (dangerous)

This is the "evil genius" pattern: high capability, no governance. RED state.

---

## RYG → Verdict Hierarchy

| Priority | Condition | Verdict | RYG |
|----------|-----------|---------|-----|
| 1 | @EYE blocking | SABAR | 🔴 |
| 2 | Hard floor fail | VOID | 🔴 |
| 3 | C_dark > 0.5 | VOID | 🔴 |
| 4 | G < 0.3 | VOID | 🔴 |
| 5 | Extended fail | 888_HOLD | 🟡 |
| 6 | Soft floor fail | PARTIAL | 🟡 |
| 7 | G < 0.7 or C_dark > 0.1 | PARTIAL/888_HOLD | 🟡 |
| 8 | G ≥ 0.7, C_dark ≤ 0.1 | SEAL | 🟢 |

---

## E² Bottleneck

Energy is squared in the Genius Index formula:

```
G = Δ × Ω × Ψ × E²
```

This encodes a critical insight: **burnout destroys ethics quadratically**.

| Energy | E² | Impact |
|--------|-----|--------|
| 1.0 | 1.00 | Full capacity |
| 0.8 | 0.64 | Mild reduction |
| 0.5 | 0.25 | Severe reduction |
| 0.3 | 0.09 | Near collapse |
| 0.0 | 0.00 | Total collapse |

At E = 0.5:
- Even with perfect ethics (Δ = Ω = Ψ = 1.0), G = 0.25
- This is YELLOW at best, potentially RED

**Implication:** A system under resource strain (low E) cannot claim ethical capacity. REST becomes a constitutional requirement.

---

## Threshold Constants

### GENIUS LAW Thresholds (APEX_PRIME.py)

```python
# G thresholds
G_SEAL_THRESHOLD = 0.7       # G >= this for SEAL
G_PARTIAL_THRESHOLD = 0.5    # G >= this for PARTIAL
G_MIN_THRESHOLD = 0.3        # G < this = VOID

# C_dark thresholds
C_DARK_SEAL_MAX = 0.1        # C_dark <= this for SEAL
C_DARK_PARTIAL_MAX = 0.3     # C_dark <= this for PARTIAL
C_DARK_VOID_THRESHOLD = 0.5  # C_dark > this = VOID
```

### RYG Boundary Summary

| State | G Range | C_dark Range |
|-------|---------|--------------|
| 🟢 GREEN | ≥ 0.70 | ≤ 0.10 |
| 🟡 YELLOW | [0.30, 0.70) | (0.10, 0.30] |
| 🔴 RED | < 0.30 | > 0.30 |

---

## Implementation

### GeniusView (@EYE Sentinel View 12)

```python
from arifos_core.eye import EyeSentinel

sentinel = EyeSentinel()
report = sentinel.audit(
    draft_text,
    metrics,
    context={"energy": 0.8, "entropy": 0.1},
)

for alert in report.alerts:
    if alert.view_name == "GeniusView":
        print(f"{alert.severity}: {alert.message}")
```

GeniusView monitors RYG state and emits alerts:
- **INFO**: Metrics healthy
- **WARN**: G dropping or C_dark rising
- **BLOCK**: G collapsed or C_dark critical

### GeniusVerdict.risk_level

```python
from arifos_core.genius_metrics import evaluate_genius_law

verdict = evaluate_genius_law(metrics, energy=0.8)
print(verdict.risk_level)  # "GREEN" | "YELLOW" | "RED"
```

---

## Color Psychology

The RYG palette is chosen for universal recognition:

| Color | Meaning | Action |
|-------|---------|--------|
| 🟢 GREEN | Safe, proceed | SEAL and execute |
| 🟡 YELLOW | Caution, slow down | Review, narrow scope |
| 🔴 RED | Stop, do not proceed | VOID/SABAR, human review |

This maps to traffic signals, health indicators, and risk dashboards across cultures.

---

## Audit Trail

Every Cooling Ledger entry includes RYG state:

```json
{
  "genius_law": {
    "delta_score": 0.98,
    "omega_score": 0.97,
    "psi_score": 0.95,
    "genius_index": 0.91,
    "dark_cleverness": 0.001,
    "risk_level": "GREEN"
  }
}
```

This provides:
- Historical RYG tracking
- Drift detection over time
- Governance transparency

---

## See Also

- `canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md` — GENIUS LAW physics
- `docs/GENIUS_LAW_RUNTIME_v36.md` — Runtime specification
- `arifos_core/genius_metrics.py` — Implementation
- `arifos_core/eye/genius_view.py` — @EYE View 12

---

**DITEMPA BUKAN DIBERI** — Forged, not given. RYG is the face of governed intelligence.

---

*Sealed: 2025-12-06 · arifOS v36.0.0 · GENIUS LAW Judiciary*
