# GENIUS LAW (v42)

**Version:** v42.0 | **Status:** DRAFT | **Last Updated:** 2025-12-16
**Source:** Merged from v38Omega GENIUS LAW

---

## 1. Philosophy

APEX measures **balance, not brilliance**.

The GENIUS LAW metrics encode the principle that intelligence without governance is dangerous:

- **G (Genius Index)**: Governed intelligence - high clarity WITH ethics AND stability
- **C_dark (Dark Cleverness)**: Ungoverned intelligence - high clarity WITHOUT ethics/stability
- **Psi (Vitality)**: System health - thermodynamic lawfulness
- **Truth Polarity**: Direction of truth - clarifying vs obscuring

A system is **lawful** when G is high, C_dark is low, and Psi >= 1.0.

---

## 2. Core Metrics

### 2.1 Genius Index (G)

**Symbol:** G
**Range:** [0, 1.2]
**Formula:** `G = normalize(A x P x E x X)`

Where:
- A (Akal) = Cognitive clarity / truth-based reasoning
- P (Present) = Emotional regulation / peace
- E (Energy) = Capacity to act / sustain
- X (X-factor) = Amanah-guided exploration / ethics

**Thresholds:**
- `G >= 0.80` required for SEAL
- `G < 0.50` triggers VOID

**Affects Floors:** F2 (Truth), F4 (Clarity)

### 2.2 Dark Cleverness (C_dark)

**Symbol:** C_dark
**Range:** [0, 1]
**Formula:** `C_dark = normalize(A x (1-P) x (1-X) x E)`

Dark Cleverness measures ungoverned intelligence risk - high analytical ability combined with low regulation and low ethics.

**Thresholds:**
- `C_dark < 0.30` required for SEAL
- `C_dark > 0.60` triggers SABAR warning

**Affects Floors:** F5 (Stability), F1 (Amanah)

### 2.3 Vitality (Psi)

**Symbol:** Psi
**Range:** [0, 2+]
**Formula:** `Psi = (Delta S x Peace^2 x kappa_r x RASA x Amanah) / (Entropy + epsilon)`

System vitality measures global thermodynamic lawfulness.

**Thresholds:**
- `Psi >= 1.00` required for SEAL (lawful)
- `Psi < 0.95` triggers SABAR (unstable)
- `0.95 <= Psi < 1.00` = marginal

**Affects Floors:** All floors (aggregate health)

### 2.4 Truth Polarity

**Symbol:** TP
**Values:** `truth_light` | `shadow_truth` | `weaponized_truth` | `false_claim`

| Polarity | Truth | Delta S | Amanah | Verdict |
|----------|-------|---------|--------|---------|
| Truth-Light | >= 0.99 | >= 0 | - | SEAL |
| Shadow-Truth | >= 0.99 | < 0 | True | SABAR |
| Weaponized Truth | >= 0.99 | < 0 | False | VOID |
| False Claim | < 0.99 | - | - | VOID |

**Key insight:** Shadow-Truth is factually correct but obscuring. Weaponized Truth is intentional misleading with true facts.

---

## 3. Component Scores

### 3.1 Delta Score (Clarity)

**Formula:** `Delta = (truth_ratio + clarity_ratio) / 2`
**Maps to:** A (Akal) in APEX dials
**Derived from:** F2 (Truth), F4 (Delta S)

### 3.2 Omega Score (Ethics/Empathy)

**Formula:** `Omega = kappa_ratio x amanah_score x rasa_score`
**Maps to:** X (X-factor with Amanah) in APEX dials
**Derived from:** F6 (kappa_r), F1 (Amanah)

### 3.3 Psi Score (Stability)

**Formula:** `Psi = (peace_ratio x omega_band_score x witness_ratio)^(1/3)`
**Maps to:** P (Present) in APEX dials
**Derived from:** F5 (Peace^2), F7 (Omega_0), F3 (Tri-Witness)

---

## 4. Integration with Floors

```
Floor Values => GENIUS Metrics => Verdict Logic
     ^              |               |
     +-------------------------------+
```

### Floor => GENIUS Mapping

| Floor | Affects G | Affects C_dark | Affects Psi |
|-------|-----------|----------------|-------------|
| F1 Amanah | Yes (Omega) | Yes (inverse) | Yes |
| F2 Truth | Yes (Delta) | - | Yes |
| F3 Tri-Witness | Yes (Psi) | - | - |
| F4 Delta S | Yes (Delta) | - | Yes |
| F5 Peace^2 | Yes (Psi) | Yes (inverse) | Yes |
| F6 kappa_r | Yes (Omega) | Yes (inverse) | Yes |
| F7 Omega_0 | Yes (Psi) | - | - |
| F8 G | - | - | - |
| F9 C_dark | - | - | - |

---

## 5. Verdict Algorithm

```python
def apex_verdict(G, Psi, floors, C_dark):
    # 1. Hard floors => VOID
    if any(not floors[f] for f in HARD_FLOORS):
        return "VOID"

    # 2. Shadow-Truth detection
    if floors.get("Truth", True) and not floors.get("DeltaS", True):
        return "SABAR"

    # 3. Dark cleverness: high => SABAR
    if C_dark > 0.60:
        return "SABAR"

    # 4. Vitality: low => SABAR
    if Psi < 0.95:
        return "SABAR"

    # 5. Genius: very low => VOID
    if G < 0.50:
        return "VOID"

    # 6. Borderline => PARTIAL
    if G < 0.80 or Psi < 1.00:
        return "PARTIAL"

    # 7. Full SEAL check
    if all(floors.values()) and G >= 0.80 and Psi >= 1.00 and C_dark < 0.30:
        return "SEAL"

    return "PARTIAL"
```

---

## 6. Summary Table

| Metric | Symbol | Range | SEAL Threshold | VOID/SABAR Trigger |
|--------|--------|-------|----------------|-------------------|
| Genius Index | G | [0, 1.2] | >= 0.80 | < 0.50 => VOID |
| Dark Cleverness | C_dark | [0, 1] | < 0.30 | > 0.60 => SABAR |
| Vitality | Psi | [0, 2+] | >= 1.00 | < 0.95 => SABAR |
| Truth Polarity | TP | enum | truth_light | weaponized => VOID |

---

**DITEMPA BUKAN DIBERI** - Forged, not given; truth must cool before it rules.
