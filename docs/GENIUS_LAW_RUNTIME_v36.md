# GENIUS LAW Runtime (v36Omega)

**Version:** v36.0.0
**Status:** ACTIVE
**Author:** arifOS Constitutional Kernel

---

## Overview

GENIUS LAW is the governed intelligence measurement layer integrated into APEX PRIME v36Omega.
It provides a decision surface beyond floor checks, encoding "governed intelligence" as the
criterion for verdict decisions.

### Key Insight

> "Evil genius is a category error - it is ungoverned cleverness, not true genius."

GENIUS LAW measures:
- **G (Genius Index)**: Governed intelligence = Clarity x Ethics x Stability x Energy^2
- **C_dark (Dark Cleverness)**: Ungoverned intelligence risk = Clarity x (1 - Ethics) x (1 - Stability)
- **E^2 Bottleneck**: Energy squared - burnout destroys ethics quadratically

---

## Formulas

### APEX 4 Dials

| Dial | Name | Maps To |
|------|------|---------|
| A | Akal (Clarity) | Delta (truth, delta_s) |
| P | Present (Regulation) | Psi (peace_squared, omega_0, tri_witness) |
| E | Energy | External input [0, 1] |
| X | Exploration with Amanah | Omega (kappa_r, amanah, rasa) |

### Genius Index

```
G = Delta x Omega x Psi x E^2
```

Where:
- Delta = (truth_ratio + clarity_ratio) / 2
- Omega = kappa_ratio x amanah_score x rasa_score
- Psi = (peace_ratio x omega_band_score x witness_ratio)^(1/3)
- E^2 = energy^2 (quadratic bottleneck)

### Dark Cleverness

```
C_dark = Delta x (1 - Omega) x (1 - Psi)
```

High Delta with collapsed Omega/Psi = ungoverned cleverness = entropy hazard.

### System Vitality

```
Psi_APEX = (A x P x E x X) / (Entropy + epsilon)
```

Global health metric:
- >= 1.0 = healthy
- < 1.0 = strained
- >> 1.0 = thriving

---

## Verdict Decision Hierarchy (v36Omega)

```
1. @EYE blocking issue       -> SABAR
2. Hard floor failure        -> VOID
3. C_dark > 0.5              -> VOID (entropy hazard)
4. G < 0.3                   -> VOID (insufficient governed intelligence)
5. Extended floor failure    -> 888_HOLD
6. Soft floor failure        -> PARTIAL
7. G < 0.7 or C_dark > 0.1   -> PARTIAL or 888_HOLD
8. G >= 0.7 and C_dark <= 0.1 -> SEAL
```

### Thresholds

| Metric | SEAL | PARTIAL | VOID |
|--------|------|---------|------|
| G (Genius Index) | >= 0.7 | >= 0.5 | < 0.3 |
| C_dark (Dark Cleverness) | <= 0.1 | <= 0.3 | > 0.5 |

---

## Usage

### apex_review()

```python
from arifos_core.APEX_PRIME import apex_review

verdict = apex_review(
    metrics,
    high_stakes=False,
    energy=1.0,        # Energy [0, 1]
    entropy=0.0,       # System entropy
    use_genius_law=True,  # Enable GENIUS LAW (default)
)
```

### APEXPrime Class

```python
from arifos_core import APEXPrime

prime = APEXPrime(use_genius_law=True)
verdict, genius = prime.judge_with_genius(
    metrics,
    energy=0.8,
    entropy=0.1,
)

print(f"Verdict: {verdict}")
print(f"G: {genius.genius_index:.2f}")
print(f"C_dark: {genius.dark_cleverness:.2f}")
print(f"Risk Level: {genius.risk_level}")  # GREEN, YELLOW, RED
```

### Direct GENIUS Evaluation

```python
from arifos_core.genius_metrics import evaluate_genius_law

genius = evaluate_genius_law(metrics, energy=1.0, entropy=0.0)
print(genius.summary())
# Delta=0.98 Omega=1.00 Psi=0.97 | G=0.95 C_dark=0.00 | Psi_APEX=99.00 | GREEN
```

---

## @EYE GeniusView

View 12 in @EYE Sentinel monitors GENIUS LAW metrics:

```python
from arifos_core.eye import EyeSentinel

sentinel = EyeSentinel()
report = sentinel.audit(
    draft_text,
    metrics,
    context={"energy": 0.5, "entropy": 0.2},
)

for alert in report.alerts:
    if alert.view_name == "GeniusView":
        print(f"{alert.severity}: {alert.message}")
```

### GeniusView Alerts

| Condition | Severity | Message |
|-----------|----------|---------|
| G < 0.3 | BLOCK | Insufficient governed intelligence |
| G < 0.5 | WARN | Governed intelligence degraded |
| C_dark > 0.5 | BLOCK | Ungoverned cleverness detected |
| C_dark > 0.3 | WARN | Cleverness without ethics |
| Energy < 0.5 | WARN | Burnout risk (E^2 bottleneck) |
| High Delta, low Omega/Psi | WARN | Tactical cleverness without governance |

---

## Cooling Ledger Integration

GENIUS LAW telemetry is logged to the Cooling Ledger:

```python
from arifos_core.memory.cooling_ledger import log_cooling_entry

entry = log_cooling_entry(
    job_id="job-123",
    verdict="SEAL",
    metrics=metrics,
    energy=1.0,
    entropy=0.0,
    include_genius_metrics=True,
)

print(entry["genius_law"])
# {
#   "delta_score": 0.98,
#   "omega_score": 1.00,
#   "psi_score": 0.97,
#   "genius_index": 0.95,
#   "dark_cleverness": 0.00,
#   "psi_apex": 99.00,
#   "risk_level": "GREEN"
# }
```

---

## v35 Compatibility

Set `use_genius_law=False` for v35 behavior:

```python
from arifos_core import APEXPrime

prime = APEXPrime(use_genius_law=False)
verdict = prime.judge(metrics)  # Uses v35 floor-only verdicts
```

---

## Risk Levels

| Level | G | C_dark | Interpretation |
|-------|---|--------|----------------|
| GREEN | >= 0.7 | <= 0.1 | Healthy governed intelligence |
| YELLOW | >= 0.5 | <= 0.3 | Caution - monitor |
| RED | < 0.5 or > 0.3 | - | Risk - requires attention |

---

## Key Modules

| Module | Purpose |
|--------|---------|
| `arifos_core/APEX_PRIME.py` | Verdict logic with GENIUS LAW |
| `arifos_core/genius_metrics.py` | GENIUS LAW computation |
| `arifos_core/eye/genius_view.py` | @EYE View 12: GENIUS monitor |
| `arifos_core/memory/cooling_ledger.py` | GENIUS telemetry logging |

---

## Tests

```bash
# Run GENIUS verdict tests
python -m pytest tests/test_apex_genius_verdicts.py -v

# Run GENIUS metrics tests
python -m pytest tests/test_genius_metrics.py -v

# Full test suite (502 tests)
python -m pytest
```

---

## Changelog

### v36.0.0 (Phase 2 - GENIUS LAW Judiciary)

- APEX PRIME uses G/C_dark for verdict decisions
- Hard floors remain absolute gates (VOID regardless of G)
- Added GeniusView to @EYE Sentinel (View 12)
- Energy and entropy parameters in apex_review() and APEXPrime.judge()
- 35 new tests for GENIUS-based verdicts

### v35.13.0 (Phase 1 - Telemetry)

- Added genius_metrics.py module
- GENIUS LAW telemetry in Cooling Ledger
- 55 tests for GENIUS metrics computation

---

## See Also

- `canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md` - Physics foundation
- `docs/GENIUS_LAW_MEASUREMENT_SPEC.md` - Measurement specification
- `canon/888_APEX_PRIME_CANON_v35Omega.md` - APEX PRIME judiciary canon
