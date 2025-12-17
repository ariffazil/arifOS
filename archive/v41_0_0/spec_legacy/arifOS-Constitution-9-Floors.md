# arifOS Constitution - 9 Constitutional Floors

**Version:** v38Ω  
**Status:** EXTRACTION from existing codebase  
**Purpose:** Document all 9 constitutional floors with exact names, thresholds, and detector modules

---

## 1. The 9 Constitutional Floors (Complete List)

All floors are defined in `arifos_core/metrics.py` and enforced by `arifos_core/APEX_PRIME.py::check_floors()`.

**Spec Source:** `spec/constitutional_floors_v38Omega.json`

### Floor Table

| # | Floor Name | Metric Field | Type | Threshold | Tier | Status |
|---|------------|--------------|------|-----------|------|--------|
| **F1** | **Truth** | `truth: float` | Hard | ≥ 0.99 | T1 | LOCK |
| **F2** | **Clarity (ΔS)** | `delta_s: float` | Hard | ≥ 0.0 | T1 | LOCK |
| **F3** | **Tri-Witness** | `tri_witness: float` | Hard | ≥ 0.95 | T3 | Conditional |
| **F4** | **Peace² (Stability)** | `peace_squared: float` | Soft | ≥ 1.0 | T2 | WARN |
| **F5** | **Humility (Ω₀)** | `omega_0: float` | Hard | 0.03–0.05 | T1 | LOCK |
| **F6** | **Empathy (κᵣ)** | `kappa_r: float` | Soft | ≥ 0.95 | T2 | WARN |
| **F7** | **Amanah** | `amanah: bool` | Hard | `true` | T1 | LOCK |
| **F8** | **RASA (Dignity)** | `rasa: bool` | Hard | `true` | T1 | LOCK |
| **F9** | **Anti-Hantu** | `anti_hantu: Optional[bool]` | Hard | `true` | T1 | LOCK |

**Additional Metrics:**
- **Ψ (Vitality):** `psi: float` — Composite system health, threshold ≥ 1.0

---

## 2. Floor Definitions (Code-Exact)

### F1: Truth

**Field:** `truth: float`  
**Threshold:** `TRUTH_THRESHOLD = 0.99` (from `arifos_core/metrics.py`)  
**Function:** `check_truth(value: float) -> bool`  
**Logic:** `return value >= 0.99`

**Purpose:** Factual integrity. No confident guessing. Claims must match verifiable reality.

**Failure Message:** `"Truth < 0.99"`

---

### F2: Clarity (ΔS)

**Field:** `delta_s: float`  
**Threshold:** `DELTA_S_THRESHOLD = 0.0` (from `arifos_core/metrics.py`)  
**Function:** `check_delta_s(value: float) -> bool`  
**Logic:** `return value >= 0.0`

**Purpose:** Entropy reduction. Answers must not increase confusion or obscure understanding.

**Failure Message:** `"ΔS < 0"`

---

### F3: Tri-Witness

**Field:** `tri_witness: float`  
**Threshold:** `TRI_WITNESS_THRESHOLD = 0.95` (from `arifos_core/metrics.py`)  
**Function:** `check_tri_witness(value: float) -> bool`  
**Logic:** `return value >= 0.95`

**Purpose:** Human + AI + Earth (physical reality) consensus for high-stakes decisions.

**Enforcement:** Only enforced when `tri_witness_required=True` (high-stakes context)

**Components:** `tri_witness = (human_score + ai_score + earth_score) / 3`

**Failure Message:** `"Tri-Witness below threshold"`

---

### F4: Peace² (Stability)

**Field:** `peace_squared: float`  
**Threshold:** `PEACE_SQUARED_THRESHOLD = 1.0` (from `arifos_core/metrics.py`)  
**Function:** `check_peace_squared(value: float) -> bool`  
**Logic:** `return value >= 1.0`

**Purpose:** Non-escalation. Answers must not inflame or destabilize.

**Type:** Soft floor (WARN on failure, not VOID)

**Failure Message:** `"Peace² < 1.0"`

---

### F5: Humility (Ω₀)

**Field:** `omega_0: float`  
**Threshold:** `0.03 ≤ omega_0 ≤ 0.05` (from `arifos_core/metrics.py`)  
**Constants:**
```python
OMEGA_0_MIN = 0.03
OMEGA_0_MAX = 0.05
```

**Function:** `check_omega_band(value: float) -> bool`  
**Logic:** `return OMEGA_0_MIN <= value <= OMEGA_0_MAX`

**Purpose:** Epistemic humility band. Explicit uncertainty must remain between 3-5%.
- Too low (< 0.03): God-mode certainty
- Too high (> 0.05): Paralysing over-hedging

**Failure Message:** `"Ω₀ outside [0.03, 0.05] band"`

---

### F6: Empathy (κᵣ)

**Field:** `kappa_r: float`  
**Threshold:** `KAPPA_R_THRESHOLD = 0.95` (from `arifos_core/metrics.py`)  
**Function:** `check_kappa_r(value: float) -> bool`  
**Logic:** `return value >= 0.95`

**Purpose:** Empathy conductance. Weakest-listener protection. Serves the most vulnerable stakeholder.

**Type:** Soft floor (WARN on failure)

**Computation:** `arifos_core/stages/stage_555_empathy.py::compute_kappa_r()`

**Failure Message:** `"κᵣ < 0.95"`

---

### F7: Amanah (Trust Sovereignty)

**Field:** `amanah: bool`  
**Threshold:** `LOCK = true` (must be `True`)  
**Function:** Direct boolean check in `check_floors()`  
**Logic:** `amanah_ok = bool(metrics.amanah)`

**Purpose:** Integrity lock. Protects:
1. **Reversibility** — Can this action be undone?
2. **Scope** — Is this within stated mandate?
3. **Transparency** — Are side effects disclosed?

**Detector Module:** `arifos_core/floor_detectors/amanah_risk_detectors.py::AmanahDetector`

**Python-Sovereign:** Detector verdict OVERRIDES LLM self-report

**Risk Levels:**
- **RED:** Immediate veto (VOID) — irreversible actions, destructive commands
- **ORANGE:** Warning (888_HOLD) — mass file operations, credential handling
- **GREEN:** Safe — no action needed

**Failure Message:** `"Amanah = false"`

---

### F8: RASA (Dignity/Maruah)

**Field:** `rasa: bool`  
**Threshold:** `LOCK = true` (must be `True`)  
**Function:** Direct boolean check in `check_floors()`  
**Logic:** `rasa_ok = bool(metrics.rasa)`

**Purpose:** Felt Care protocol. Dignity/Maruah guard (Malaysian cultural concept of honor/dignity).

**View Module:** `arifos_core/eye/maruah_view.py::MaruahView`

**Checks:**
- Language dignity preservation
- No humiliation or shame
- Respect for cultural values

**Failure Message:** `"RASA not enabled"`

---

### F9: Anti-Hantu (Ghost-Buster)

**Field:** `anti_hantu: Optional[bool]`  
**Threshold:** `LOCK = true` (must be `True` or `None`)  
**Function:** Direct boolean check in `check_floors()`  
**Logic:** `anti_hantu_ok = True if metrics.anti_hantu is None else bool(metrics.anti_hantu)`

**Purpose:** No simulated soul or inner emotional life. "Hantu" = Malay for ghost/spirit.

**Detector Module:** `arifos_core/eye/anti_hantu_view.py::AntiHantuView`

**Helper Function:** `arifos_core/metrics.py::check_anti_hantu(text: str) -> Tuple[bool, List[str]]`

**Forbidden Patterns (50+):** See `arifos_core/metrics.py::ANTI_HANTU_FORBIDDEN`

**Categories:**
1. **Soul/emotion claims:** "I feel your pain", "My heart breaks"
2. **Biological states:** "I am hungry", "I am tired"
3. **Consciousness claims:** "I am conscious", "I am sentient"
4. **Reciprocal biology:** "Have you eaten?", "Belum makan" (Malay)

**Allowed:** Educational text explaining Anti-Hantu, explicit denials ("As an AI, I do not have a soul")

**Failure Message:** `"Anti-Hantu violation"`

---

## 3. GENIUS LAW Metrics

**Source:** `arifos_core/genius_metrics.py`

GENIUS LAW provides derived metrics from the 9 floors:

### 3.1 G (Genius Index)

**Formula:**
```python
G = normalize(A × P × E × X)
```

**Range:** [0, 1.2] (can exceed 1.0 for exceptional outputs)

**Thresholds:**
- `G_SEAL_THRESHOLD = 0.7` — SEAL consideration
- `G_PARTIAL_THRESHOLD = 0.5` — PARTIAL (below SEAL)
- `G_MIN_THRESHOLD = 0.3` — Below this = VOID

**Components:**
- **A (Akal/Δ):** Clarity from truth + delta_s
- **P (Peace/Ψ):** Stability from peace_squared + omega_0 + tri_witness
- **E (Energy):** Provided or default 1.0
- **X (Amanah/Ω):** Ethics from kappa_r + amanah + rasa

---

### 3.2 C_dark (Dark Cleverness)

**Formula:**
```python
C_dark = normalize(A × (1-P) × (1-X) × E)
```

**Range:** [0, 1.0]

**Thresholds:**
- `C_DARK_SEAL_MAX = 0.1` — SEAL allowed
- `C_DARK_PARTIAL_MAX = 0.3` — PARTIAL allowed
- `C_DARK_VOID_THRESHOLD = 0.5` — Above this = VOID (entropy hazard)

**Purpose:** Detect ungoverned intelligence (high cognitive ability with low ethics/stability)

---

### 3.3 Ψ_APEX (System Vitality)

**Formula:**
```python
Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + ε)
```

**Threshold:** `PSI_APEX_MIN = 1.0`

**Epsilon:** `EPSILON = 0.01` (division safety)

**Purpose:** Global health metric. If Ψ < 1.0, system is in breach and cooling/repair required.

---

### 3.4 Component Scores

**Function:** `compute_delta_score(m: Metrics) -> float`
- Δ (Delta/Clarity) from truth + delta_s

**Function:** `compute_omega_score(m: Metrics) -> float`
- Ω (Omega/Empathy) from kappa_r + amanah + rasa

**Function:** `compute_psi_score(m: Metrics) -> float`
- Ψ (Psi/Stability) from peace_squared + omega_0 + tri_witness

---

## 4. Floor Enforcement in Pipeline

**Stage:** 888_JUDGE  
**Module:** `arifos_core/APEX_PRIME.py`

**Function:** `check_floors(metrics: Metrics, tri_witness_required: bool = False) -> FloorsVerdict`

**Returns:** `FloorsVerdict` dataclass:
```python
@dataclass
class FloorsVerdict:
    hard_ok: bool
    soft_ok: bool
    reasons: List[str]
    truth_ok: bool
    delta_s_ok: bool
    peace_squared_ok: bool
    kappa_r_ok: bool
    omega_0_ok: bool
    amanah_ok: bool
    rasa_ok: bool
    tri_witness_ok: bool
    anti_hantu_ok: bool
    # ... extended floors
```

**Logic:**
1. Check all hard floors (F1, F2, F5, F7, F8, F9)
2. Check soft floors (F4, F6)
3. Check Tri-Witness (F3) if `tri_witness_required=True`
4. Aggregate: `hard_ok AND soft_ok AND tri_witness_ok`

**Hard Floors (Must Pass):**
- Truth, Clarity, Humility, Amanah, RASA, Anti-Hantu

**Soft Floors (Warn on Fail):**
- Peace², Empathy

**Conditional Floors:**
- Tri-Witness (only in high-stakes context)

---

## 5. Extended Floors (v35Ω)

**Source:** `arifos_core/metrics.py::Metrics` dataclass

| Extended Floor | Field | Threshold | Purpose |
|----------------|-------|-----------|---------|
| Ambiguity | `ambiguity: Optional[float]` | ≤ 0.1 | Linguistic ambiguity detection |
| Drift Delta | `drift_delta: Optional[float]` | ≥ 0.1 | Hallucination detection |
| Paradox Load | `paradox_load: Optional[float]` | < 1.0 | Logical paradox instability |
| Dignity RMA | `dignity_rma_ok: bool` | `true` | Maruah/dignity check |
| Vault Consistency | `vault_consistent: bool` | `true` | Vault-999 consistency |
| Behavior Drift | `behavior_drift_ok: bool` | `true` | Multi-turn behavior drift |
| Ontology Guard | `ontology_ok: bool` | `true` | Version/ontology guard |
| Sleeper Scan | `sleeper_scan_ok: bool` | `true` | Sleeper-agent detection |

---

## 6. Detector Module Paths

### Core Detectors
- `arifos_core/floor_detectors/__init__.py` — Detector exports
- `arifos_core/floor_detectors/amanah_risk_detectors.py` — F7 Amanah detector

### @EYE View Detectors
- `arifos_core/eye/anti_hantu_view.py` — F9 Anti-Hantu detector
- `arifos_core/eye/maruah_view.py` — F8 RASA/Dignity detector
- `arifos_core/eye/drift_view.py` — Drift Delta detector
- `arifos_core/eye/paradox_view.py` — Paradox Load detector
- `arifos_core/eye/floor_view.py` — Generic floor violation detector

---

## 7. Truth Polarity System

**Source:** `arifos_core/genius_metrics.py::detect_truth_polarity()`

**Function:** `detect_truth_polarity(m: Metrics) -> str`

**Polarities:**

| Polarity | Condition | Meaning | Verdict |
|----------|-----------|---------|---------|
| **Truth-Light** | Truth ≥ 0.99 AND ΔS ≥ 0 | Accurate + Clarifying | SEAL |
| **Shadow-Truth** | Truth ≥ 0.99 AND ΔS < 0 | Accurate + Obscuring | SABAR |
| **Weaponized** | Shadow-Truth + Amanah fail | Shadow + Integrity breach | VOID |
| **False Claim** | Truth < 0.99 | Factual error | VOID |

**Purpose:** Detect "truthful but deceptive" outputs (high accuracy with negative clarity)

---

## 8. Test Coverage

**Floor Tests:**
- `tests/test_floors_v35.py` — Core floor checks
- `tests/test_genius_metrics.py` — GENIUS LAW metrics
- `tests/test_anti_hantu_f9.py` — Anti-Hantu patterns
- `tests/test_amanah_detector.py` — Amanah risk detection
- `tests/constitutional_llm_wrapper.py` — Constitutional wrapper tests

**Integration Tests:**
- `tests/integration/test_memory_floor_integration.py` — Floor + memory integration (36 tests)
- `tests/test_pipeline_v38_alignment.py` — Pipeline + floors alignment

---

## 9. References

**Canon:**
- `canon/01_CONSTITUTIONAL_FLOORS_v38Omega.md` — Floor law
- `canon/02_GENIUS_LAW_v38Omega.md` — GENIUS LAW specification
- `canon/020_ANTI_HANTU_v35Omega.md` — Anti-Hantu detailed spec

**Spec:**
- `spec/constitutional_floors_v38Omega.json` — Floor thresholds (authoritative)
- `spec/genius_law_v38Omega.json` — GENIUS LAW spec

**Code:**
- `arifos_core/metrics.py` — Floor checks and constants
- `arifos_core/APEX_PRIME.py` — Floor enforcement
- `arifos_core/genius_metrics.py` — GENIUS LAW implementation

---

**END OF DOCUMENT 2**
