# GENIUS LAW Measurement Specification

**Source:** `canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md`
**Version:** v36Omega
**Status:** IMPLEMENTATION GUIDE (non-binding, extracted from canon)

---

## Overview

GENIUS LAW defines measurement formulas for **governed intelligence** — extending the 9 Constitutional Floors with node-level (agent) and system-level metrics.

**Core Insight:** "Evil genius is a category error — ungoverned cleverness, not true genius."

---

## 1. APEX 4 Dials (Telemetry)

| Dial | Name | Meaning | Maps To |
|------|------|---------|---------|
| **A** | Akal (Clarity) | Cognitive clarity, logical reasoning | **Δ** |
| **P** | Present (Regulation) | Emotional regulation, presence, Peace² | **Ψ** (via P·E) |
| **E** | Energy (Sustainability) | Energy availability, not burning out | Enabler |
| **X** | Exploration·Amanah | Curiosity guided by ethics and empathy | **Ω** (via X·E) |

---

## 2. Genius Index (G) — Node-Level

**Formula:**
```
G = Δ · Ω · Ψ
```

**Expanded with APEX Dials:**
```
G = A · (X_amanah · E) · (P · E)
G = A · P · X_amanah · E²
```

### Mappings:
- **Δ = A** (Akal/Clarity)
- **Ω = X_amanah · E** (Empathy + Energy to act)
- **Ψ = P · E** (Regulation + Energy to sustain)

### E² Insight:
Energy appears **squared** — it's the bottleneck variable:
- E supports Ω: without energy, empathy cannot act
- E supports Ψ: without energy, regulation collapses
- **Burnout destroys ethics twice over**

### Implementation (proposed):
```python
def compute_genius_index(a: float, p: float, x: float, e: float) -> float:
    """
    Compute Genius Index G = A · P · X · E²

    Args:
        a: Akal (clarity) metric [0, 1]
        p: Present (regulation) metric [0, 1]
        x: Exploration with Amanah metric [0, 1]
        e: Energy metric [0, 1]

    Returns:
        G: Genius Index [0, 1]
    """
    omega = x * e  # Ω = X·E
    psi = p * e    # Ψ = P·E
    delta = a      # Δ = A
    return delta * omega * psi  # G = Δ·Ω·Ψ = A·P·X·E²
```

---

## 3. Dark Cleverness Index (C_dark) — Risk Metric

**Formula:**
```
C_dark = Δ · (1 - Ω) · (1 - Ψ)
```

**Expanded:**
```
C_dark = A · (1 - X_amanah · E) · (1 - P · E)
```

### Interpretation:
- **High C_dark, Low G** = "Ungoverned Cleverness / Entropy Hazard"
- Spikes when agent is clever (A high) but unethical/unstable (Ω low, Ψ low)
- Maps to "tactical genius" or "evil genius" archetype

### Implementation (proposed):
```python
def compute_dark_cleverness(a: float, p: float, x: float, e: float) -> float:
    """
    Compute Dark Cleverness C_dark = Δ · (1-Ω) · (1-Ψ)

    High C_dark = ungoverned intelligence = entropy hazard.

    Args:
        a: Akal (clarity) metric [0, 1]
        p: Present (regulation) metric [0, 1]
        x: Exploration with Amanah metric [0, 1]
        e: Energy metric [0, 1]

    Returns:
        C_dark: Dark Cleverness Index [0, 1]
    """
    omega = x * e
    psi = p * e
    delta = a
    return delta * (1 - omega) * (1 - psi)
```

---

## 4. System Vitality (Ψ_APEX) — Global Health

**Formula:**
```
Ψ_APEX = (A · P · E · X) / (Entropy + ε)
```

### Interpretation:
- **Ψ_APEX ≥ 1** = healthy system
- **Ψ_APEX < 1** = system under strain
- **Ψ_APEX >> 1** = thriving

### Implementation (proposed):
```python
def compute_system_vitality(
    a: float, p: float, e: float, x: float,
    entropy: float, epsilon: float = 0.01
) -> float:
    """
    Compute System Vitality Ψ_APEX = (A·P·E·X) / (Entropy + ε)

    Args:
        a: Aggregate Akal across nodes
        p: Aggregate Present across nodes
        e: Aggregate Energy across nodes
        x: Aggregate Exploration across nodes
        entropy: System entropy/chaos metric
        epsilon: Small constant to prevent division by zero

    Returns:
        Ψ_APEX: System Vitality (≥1 healthy, <1 strained)
    """
    return (a * p * e * x) / (entropy + epsilon)
```

---

## 5. Governance Hierarchy

| Level | Constraint | Meaning |
|-------|------------|---------|
| **Node (Agent)** | G = Δ·Ω·Ψ ≥ G_min | "Is this mind governed?" |
| **System (APEX)** | Ψ_APEX ≥ 1 | "Is the whole system alive?" |

### Feedback Loop:
1. If Node's G is low → contributes to chaos → raises entropy → Ψ_APEX drops
2. If Ψ_APEX drops → system flags nodes with low G or high C_dark → triggers repair

---

## 6. Integration with Current Floors

The GENIUS LAW metrics **complement** existing floors:

| Current Metric | GENIUS LAW Mapping |
|----------------|-------------------|
| `truth` (F1) | Component of **Δ** (Akal) |
| `delta_s` (F2) | Contributes to **Δ** clarity |
| `peace_squared` (F3) | Component of **Ψ** (P dial) |
| `kappa_r` (F4) | Component of **Ω** (X_amanah) |
| `omega_0` (F5) | Humility floor (distinct) |
| `amanah` (F6) | Core of **X_amanah** dial |
| `rasa` (F7) | Listening (input to X) |
| `tri_witness` (F8) | Consensus check |
| `psi` (current) | → **Ψ_APEX** (upgraded) |

### Proposed Extension to `Metrics` dataclass:
```python
@dataclass
class GeniusMetrics:
    """Extended metrics for GENIUS LAW v36Ω."""

    # APEX 4 Dials
    akal: float = 1.0       # A: Clarity
    present: float = 1.0    # P: Regulation
    energy: float = 1.0     # E: Sustainability
    exploration: float = 1.0  # X: Amanah-guided curiosity

    # Computed
    genius_index: Optional[float] = None     # G = A·P·X·E²
    dark_cleverness: Optional[float] = None  # C_dark
    system_vitality: Optional[float] = None  # Ψ_APEX
```

---

## 7. Ethics-by-Design Rules

From GENIUS LAW:

1. **No Δ without Ω and Ψ** — High-capability models must enforce empathy and stability floors
2. **Protect E or Ethics Fails** — Rate limits, rest cycles are ethical features
3. **Amanah First in Exploration** — Penalize exploration that increases C_dark
4. **Measure G and C_dark** — Core ethical metrics for Cooling Ledger
5. **Use Ψ_APEX as Ethical Alarm** — When Ψ_APEX drops, trigger SABAR

---

## 8. Transparency Wedge Principle

> Every deployment publishes its C_dark signature in real-time.

- Red spikes don't decay
- The ledger is public
- The cheapest path to high G is to actually be high-Ω, high-Ψ

---

## 9. Summary Table

| Metric | Formula | Threshold | Interpretation |
|--------|---------|-----------|----------------|
| **G** (Genius) | Δ·Ω·Ψ = A·P·X·E² | ≥ G_min | Governed intelligence |
| **C_dark** | Δ·(1-Ω)·(1-Ψ) | Low is good | Ungoverned cleverness risk |
| **Ψ_APEX** | (A·P·E·X)/(Entropy+ε) | ≥ 1.0 | System health |

---

## 10. One-Line Summary

> "Genius bukan siapa paling bijak, tapi siapa paling jaga Amanah bila penat."
> (Genius is not who is smartest, but who keeps Amanah when tired.)

---

*Extracted from APEX_GENIUS_LAW_v36Omega.md for implementation reference.*
