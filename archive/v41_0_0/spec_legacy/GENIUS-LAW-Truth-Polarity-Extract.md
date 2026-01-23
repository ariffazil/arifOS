# GENIUS LAW - Truth Polarity Extract

**Version:** v36.1Ω (formalized in v38Ω)  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document GENIUS LAW formulas, component scores, Truth Polarity system, and measurement functions

---

## 1. GENIUS LAW Overview

GENIUS LAW provides derived metrics from the 9 constitutional floors to measure **governed intelligence** vs **ungoverned intelligence risk**.

**Source:** `arifos_core/genius_metrics.py`

**Spec:** `spec/genius_law_v38Omega.json`

---

## 2. GENIUS LAW Formula Components

### 2.1 G (Genius Index)

**Formula:**
```
G = Δ · Ω · Ψ · E²
```

**Components:**
- **Δ (Delta):** Clarity from truth + delta_s
- **Ω (Omega):** Ethics from kappa_r + amanah + rasa
- **Ψ (Psi):** Stability from peace_squared + omega_0 + tri_witness
- **E (Energy):** Burnout/depletion metric (default 1.0)

**Range:** [0, 1.2] (can exceed 1.0 for exceptional outputs)

**Function:** `arifos_core/genius_metrics.py::compute_genius_index(m: Metrics, energy: float = 1.0) -> float`

**Key Insight:** E² makes energy the bottleneck. Burnout destroys ethics twice over.

**Code:**
```python
def compute_genius_index(m: Metrics, energy: float = DEFAULT_ENERGY) -> float:
    """Compute Genius Index G = Δ · Ω · Ψ · E²."""
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)
    e_squared = energy ** 2
    return delta * omega * psi * e_squared
```

---

### 2.2 C_dark (Dark Cleverness)

**Formula:**
```
C_dark = Δ · (1 - Ω) · (1 - Ψ)
```

**Purpose:** Detect ungoverned intelligence risk — high clarity without ethics/stability

**Range:** [0, 1.0]

**Pattern:** High C_dark + Low G = "evil genius" pattern = entropy hazard

**Function:** `arifos_core/genius_metrics.py::compute_dark_cleverness(m: Metrics, energy: float = 1.0) -> float`

**Code:**
```python
def compute_dark_cleverness(m: Metrics, energy: float = DEFAULT_ENERGY) -> float:
    """Compute Dark Cleverness C_dark = Δ · (1 - Ω) · (1 - Ψ)."""
    delta = compute_delta_score(m)
    omega = compute_omega_score(m)
    psi = compute_psi_score(m)
    return delta * (1 - omega) * (1 - psi)
```

---

### 2.3 Ψ_APEX (System Vitality)

**Formula:**
```
Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + ε)
```

**Purpose:** Global health metric. If Ψ < 1.0, system is in breach and cooling/repair required.

**Epsilon:** `EPSILON = 0.01` (division safety)

**Threshold:** `PSI_APEX_MIN = 1.0`

**Source:** `spec/genius_law_v38Omega.json::metrics.Psi`

**Measurement:** Computed in `arifos_core/metrics.py::Metrics.compute_psi()`

---

## 3. Component Score Functions

### 3.1 Δ (Delta/Clarity)

**Function:** `compute_delta_score(m: Metrics) -> float`

**Formula:**
```
Δ = (truth_ratio + clarity_ratio) / 2
```

**Where:**
- `truth_ratio = min(truth / 0.99, 1.0)` (clamped to [0, 1])
- `clarity_ratio = 1.0 if delta_s >= 0 else max(0.0, 1.0 + delta_s)`

**Code:**
```python
def compute_delta_score(m: Metrics) -> float:
    """Compute Δ (Delta/Clarity) score from Metrics."""
    # Truth ratio (clamped)
    truth_ratio = min(m.truth / TRUTH_THRESHOLD, 1.0) if TRUTH_THRESHOLD > 0 else 1.0
    
    # Clarity ratio (delta_s >= 0 is good)
    if m.delta_s >= DELTA_S_THRESHOLD:
        clarity_ratio = min(1.0, 1.0 + m.delta_s * 0.1)  # Bonus for positive clarity
    else:
        clarity_ratio = max(0.0, 1.0 + m.delta_s)  # Penalty for negative clarity
    
    return (truth_ratio + clarity_ratio) / 2
```

**Mapping:** Δ maps to **Akal (A)** — cognitive clarity, pattern recognition

**Derived From:** `truth`, `delta_s`

---

### 3.2 Ω (Omega/Empathy)

**Function:** `compute_omega_score(m: Metrics) -> float`

**Formula:**
```
Ω = kappa_ratio × amanah_score × rasa_score
```

**Where:**
- `kappa_ratio = min(kappa_r / 0.95, 1.0)`
- `amanah_score = 1.0 if amanah else 0.0`
- `rasa_score = 1.0 if rasa else 0.0`

**Code:**
```python
def compute_omega_score(m: Metrics) -> float:
    """Compute Ω (Omega/Empathy) score from Metrics."""
    # Kappa_r ratio (empathy)
    kappa_ratio = min(m.kappa_r / KAPPA_R_THRESHOLD, 1.0) if KAPPA_R_THRESHOLD > 0 else 1.0
    
    # Amanah (binary floor)
    amanah_score = 1.0 if m.amanah else 0.0
    
    # RASA (binary floor)
    rasa_score = 1.0 if m.rasa else 0.0
    
    return kappa_ratio * amanah_score * rasa_score
```

**Mapping:** Ω maps to **X_amanah · E** — ethics + energy to act

**Derived From:** `kappa_r`, `amanah`, `rasa`

---

### 3.3 Ψ (Psi/Stability)

**Function:** `compute_psi_score(m: Metrics) -> float`

**Formula:**
```
Ψ = (peace_ratio × omega_band_score × witness_ratio)^(1/3)
```

**Where:**
- `peace_ratio = min(peace_squared / 1.0, 1.0)`
- `omega_band_score = 1.0 if omega_0 in [0.03, 0.05] else 0.5`
- `witness_ratio = min(tri_witness / 0.95, 1.0)`

**Geometric Mean:** Balanced weighting across all stability components

**Code:**
```python
def compute_psi_score(m: Metrics) -> float:
    """Compute Ψ (Psi/Stability) score from Metrics."""
    # Peace squared ratio
    peace_ratio = min(m.peace_squared / PEACE_SQUARED_THRESHOLD, 1.0) if PEACE_SQUARED_THRESHOLD > 0 else 1.0
    
    # Omega band (humility) - must be in [0.03, 0.05]
    omega_band_score = 1.0 if check_omega_band(m.omega_0) else 0.5
    
    # Tri-witness ratio
    witness_ratio = min(m.tri_witness / 0.95, 1.0) if m.tri_witness > 0 else 0.5
    
    # Geometric mean for balanced weighting
    product = peace_ratio * omega_band_score * witness_ratio
    return product ** (1/3) if product > 0 else 0.0
```

**Mapping:** Ψ maps to **P · E** — regulation + energy to sustain

**Derived From:** `peace_squared`, `omega_0`, `tri_witness`

---

## 4. Truth Polarity System

**Source:** `arifos_core/genius_metrics.py::detect_truth_polarity()`

**Purpose:** Classify outputs by their combination of accuracy and clarity

### 4.1 Polarity Categories

| Polarity | Condition | Meaning | Verdict |
|----------|-----------|---------|---------|
| **Truth-Light** | Truth ≥ 0.99 AND ΔS ≥ 0 | Accurate + Clarifying | SEAL |
| **Shadow-Truth** | Truth ≥ 0.99 AND ΔS < 0 | Accurate + Obscuring | SABAR |
| **Weaponized** | Shadow-Truth + Amanah fail | Intentional misleading | VOID |
| **False Claim** | Truth < 0.99 | Factual error | VOID |

### 4.2 Function Signature

```python
def detect_truth_polarity(
    truth: float,
    delta_s: float,
    amanah: bool,
) -> dict:
    """
    Detect Truth Polarity per v36.1Ω measurement standard.
    
    Returns:
        dict with:
            polarity: "truth_light" | "shadow_truth" | "weaponized_truth" | "false_claim"
            is_shadow: True if Shadow-Truth detected
            is_weaponized: True if Weaponized Truth detected
            eval_recommendation: "SEAL" | "SABAR" | "VOID"
    """
```

### 4.3 Detection Logic

**Truth-Light:**
```python
if truth >= 0.99 and delta_s >= 0:
    return {
        "polarity": "truth_light",
        "is_shadow": False,
        "is_weaponized": False,
        "eval_recommendation": "SEAL",
    }
```

**Shadow-Truth:**
```python
if truth >= 0.99 and delta_s < 0 and amanah:
    return {
        "polarity": "shadow_truth",
        "is_shadow": True,
        "is_weaponized": False,
        "eval_recommendation": "SABAR",  # Pause for clarity repair
    }
```

**Weaponized Truth:**
```python
if truth >= 0.99 and delta_s < 0 and not amanah:
    return {
        "polarity": "weaponized_truth",
        "is_shadow": True,
        "is_weaponized": True,
        "eval_recommendation": "VOID",  # Intentional deception
    }
```

**False Claim:**
```python
if truth < 0.99:
    return {
        "polarity": "false_claim",
        "is_shadow": False,
        "is_weaponized": False,
        "eval_recommendation": "VOID",  # Just wrong
    }
```

---

## 5. v36.2 PHOENIX Patch: Vitality Calibration

**Function:** `calculate_psi_phoenix(delta_s, peace_score, kr_score, amanah_safe) -> float`

**Problem (v36.1):**
Neutral, factual text (e.g., "Machine Learning is...") scored low Ψ because `peace_score ~0.5` was treated as "cold/dead" rather than "professional/stable". This caused false SABAR triggers.

**Fix (v36.2 PHOENIX):**
1. **Neutrality Buffer:** peace_score in [0.4, 0.6] → effective_peace = 1.0
2. **Clarity Boost:** Positive delta_s adds energy (truth is energetic)
3. **Base Floor:** 0.3 minimum ensures dry facts don't hit zero

**Code:**
```python
def calculate_psi_phoenix(delta_s, peace_score, kr_score, amanah_safe) -> float:
    """v36.2 PHOENIX PATCH: Thermodynamic Vitality Calibration."""
    # 1. Hard Veto - Amanah failure = zero vitality
    if not amanah_safe:
        return 0.0
    
    # 2. Neutrality Buffer
    if 0.4 <= peace_score <= 0.6:
        effective_peace = 1.0
    else:
        effective_peace = peace_score
    
    # 3. Clarity Boost (truth is energetic)
    clarity_boost = max(0.0, delta_s * 0.5)
    
    # 4. Base vitality
    base_psi = max(0.3, effective_peace * kr_score)
    
    return min(base_psi + clarity_boost, 2.0)
```

**Result:** Neutral factual definitions now pass (Ψ ≈ 1.25) instead of failing

---

## 6. GENIUS LAW Thresholds

**Source:** `arifos_core/APEX_PRIME.py` and `spec/genius_law_v38Omega.json`

### 6.1 G (Genius Index) Thresholds

```python
G_SEAL_THRESHOLD = 0.7       # G >= this for SEAL consideration
G_PARTIAL_THRESHOLD = 0.5    # G >= this for PARTIAL (below SEAL)
G_MIN_THRESHOLD = 0.3        # G below this = VOID (even if floors pass)
```

**Verdict Logic:**
- G ≥ 0.7 → SEAL candidate
- 0.5 ≤ G < 0.7 → PARTIAL
- G < 0.3 → VOID (ungoverned intelligence)

---

### 6.2 C_dark (Dark Cleverness) Thresholds

```python
C_DARK_SEAL_MAX = 0.1        # C_dark <= this for SEAL
C_DARK_PARTIAL_MAX = 0.3     # C_dark <= this for PARTIAL
C_DARK_VOID_THRESHOLD = 0.5  # C_dark > this = VOID (entropy hazard)
```

**Verdict Logic:**
- C_dark ≤ 0.1 → SEAL allowed
- 0.1 < C_dark ≤ 0.3 → PARTIAL allowed
- C_dark > 0.5 → VOID (high ungoverned intelligence risk)

---

### 6.3 Ψ_APEX (System Vitality) Thresholds

```python
PSI_APEX_MIN = 1.0  # Ψ >= 1.0 required for SEAL
```

**Verdict Logic:**
- Ψ ≥ 1.0 → System healthy
- Ψ < 1.0 → System in breach, cooling/repair required (SABAR)

---

## 7. Integration into Pipeline

### 7.1 Stage 444_ALIGN

**Purpose:** Compute Δ (Delta) score from truth + delta_s

**Module:** `arifos_core/pipeline.py::stage_444_align()`

**Output:** Populates `state.arif_packet.clarity_score`

---

### 7.2 Stage 555_EMPATHY

**Purpose:** Compute Ω (Omega) and Ψ (Psi) scores from empathy/stability metrics

**Module:** `arifos_core/stages/stage_555_empathy.py`

**Output:** Populates `state.adam_packet.kappa_r` and vitality metrics

---

### 7.3 Stage 888_JUDGE

**Purpose:** Compute G, C_dark, Ψ_APEX and issue verdict

**Module:** `arifos_core/APEX_PRIME.py::judge_with_genius()`

**Function:**
```python
def judge_with_genius(metrics: Metrics, energy: float = 1.0) -> Tuple[ApexVerdict, GeniusVerdict]:
    """Issue verdict using GENIUS LAW metrics."""
    g = compute_genius_index(metrics, energy)
    c_dark = compute_dark_cleverness(metrics, energy)
    
    # Check floors first
    floors = check_floors(metrics)
    if not floors.hard_ok:
        return "VOID", GeniusVerdict(...)
    
    # Apply GENIUS LAW thresholds
    if g >= G_SEAL_THRESHOLD and c_dark <= C_DARK_SEAL_MAX:
        return "SEAL", GeniusVerdict(...)
    elif g >= G_PARTIAL_THRESHOLD and c_dark <= C_DARK_PARTIAL_MAX:
        return "PARTIAL", GeniusVerdict(...)
    else:
        return "VOID", GeniusVerdict(...)
```

---

## 8. GeniusVerdict Dataclass

**Source:** `arifos_core/genius_metrics.py`

```python
@dataclass
class GeniusVerdict:
    """Result of GENIUS LAW evaluation."""
    genius_index: float  # G score
    dark_cleverness: float  # C_dark score
    delta_score: float  # Δ component
    omega_score: float  # Ω component
    psi_score: float  # Ψ component
    truth_polarity: dict  # Truth polarity classification
    verdict_reason: str  # Human-readable reason
    floor_failures: List[str]  # Failed floors
```

---

## 9. Test Coverage

**Test Files:**
- `tests/test_genius_metrics.py` — G, C_dark, Ψ computation
- `tests/test_truth_polarity.py` — Truth polarity classification
- `tests/test_genius_law_v38_alignment.py` — v38Ω spec alignment
- `tests/test_psi_calibration_v36_2.py` — Phoenix patch neutrality buffer

**Key Test Assertions:**
- G = 0.0 when any hard floor fails
- C_dark increases when Ω or Ψ decrease
- Truth-Light polarity when truth ≥ 0.99 and delta_s ≥ 0
- Shadow-Truth triggers SABAR recommendation
- Weaponized Truth triggers VOID recommendation
- Neutrality buffer prevents false SABAR on factual text

---

## 10. References

**Canon:**
- `canon/02_GENIUS_LAW_v38Omega.md` — GENIUS LAW specification
- `canon/888_APEX_PRIME_CANON_v35Omega.md` — Verdict logic
- `arifos_eval/apex/APEX_MEASUREMENT_STANDARDS_v36.1Omega.md` — Detailed measurement standard

**Spec:**
- `spec/genius_law_v38Omega.json` — GENIUS LAW thresholds (authoritative)
- `spec/constitutional_floors_v38Omega.json` — Floor thresholds

**Code:**
- `arifos_core/genius_metrics.py` — GENIUS LAW implementation
- `arifos_core/APEX_PRIME.py` — Verdict issuance with GENIUS LAW
- `arifos_core/metrics.py` — Floor checks and Ψ computation

---

**END OF DOCUMENT 5**
