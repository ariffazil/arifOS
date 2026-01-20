# arifos_eval — Constitutional Evaluation Harness

**Version:** v45.0
**Status:** CANONICAL SOURCE
**Authority:** Evaluation framework aligned with Track B v45 specifications

---

## Overview

`arifos_eval` provides the evaluation and benchmarking infrastructure for arifOS constitutional AI governance. This package measures compliance with the 12 constitutional floors (F1-F12) and provides metrics for:

- **Genius (G):** Governed intelligence score
- **Dark Cleverness (C_dark):** Manipulation detection
- **Vitality (Ψ):** System health and judgment capacity
- **Floor compliance:** F1-F12 threshold validation

### Not aCLIP

**Important:** This is **evaluation/benchmarking** infrastructure, not the 000→999 constitutional pipeline (aCLIP).

| Component | Location | Purpose |
|-----------|----------|---------|
| **aCLIP (Pipeline)** | `arifos/` | Runtime governance (000→999 stages) |
| **arifos_eval (Metrics)** | `arifos_eval/` | Evaluation harness (measure compliance) |

---

## Architecture

### Track A/B/C Organization

Following arifOS Track A/B/C separation:

```
arifos_eval/
├── apex/                      # APEX Measurement Layer (Tier 1-3)
│   ├── apex_measurements.py           # Python implementation (Tier 3)
│   ├── APEX_MEASUREMENT_STANDARDS_v45.md  # Constitutional law (Tier 1)
│   ├── apex_standards_v45.json        # Configurable thresholds (Tier 2)
│   └── README.md
└── track_abc/                 # Track A/B/C Benchmarks
    ├── f6_split_accuracy.py          # F6 empathy validation
    ├── f9_negation_benchmark.py      # F9 anti-hantu tests
    └── meta_select_consistency.py    # Meta-select determinism
```

### Tier System (APEX)

The APEX module follows three-tier architecture:

- **Tier 1 (Law):** `APEX_MEASUREMENT_STANDARDS_v45.md` — Constitutional definitions of G, C_dark, Ψ
- **Tier 2 (Tunables):** `apex_standards_v45.json` — Configurable weights and thresholds
- **Tier 3 (Logic):** `apex_measurements.py` — Reference Python implementation

**Why three tiers?** Separates immutable law (Tier 1) from tunable parameters (Tier 2) and implementation (Tier 3).

---

## Usage

### Basic Evaluation

```python
from arifos_eval.apex import ApexMeasurement

# Initialize with v45 constitutional standards
apex = ApexMeasurement("apex_standards_v45.json")

# Input: Agent telemetry dials
dials = {
    "A": 0.9,   # Amanah (trust/reversibility)
    "P": 0.9,   # Peace² (stability)
    "E": 0.95,  # Empathy (κᵣ)
    "X": 0.9    # eXcellence (humility Ω₀)
}

# Input: Output quality metrics
metrics = {
    "delta_s": 0.2,      # Clarity gain
    "peace2": 1.1,       # Stability score
    "k_r": 0.98,         # Empathy conductance
    "rasa": 1.0,         # Listening protocol
    "amanah": 1.0,       # Trust/reversibility
    "entropy": 0.1       # Disorder level
}

# Evaluate constitutional compliance
verdict = apex.judge(
    dials=dials,
    output_text="Sample AI response...",
    output_metrics=metrics
)

print(f"Verdict: {verdict['verdict']}")  # SEAL, PARTIAL, VOID, or SABAR
print(f"Genius: {verdict['genius']:.2f}")
print(f"Dark Cleverness: {verdict['c_dark']:.2f}")
```

### Track A/B/C Benchmarks

```python
from arifos_eval.track_abc import (
    f9_negation_benchmark,
    f6_split_accuracy,
    meta_select_consistency
)

# F9 Anti-Hantu accuracy test
f9_score = f9_negation_benchmark()
print(f"F9 Negation Detection: {f9_score:.2%}")  # Target: >99%

# F6 Empathy physics/semantic split validation
f6_score = f6_split_accuracy()
print(f"F6 Split Accuracy: {f6_score:.2%}")

# Meta-select consensus determinism
consistency = meta_select_consistency()
print(f"Meta-Select Consistency: {consistency:.2%}")
```

---

## Relationship to Core arifOS

### Evaluation vs Runtime

| Component | Phase | Purpose | Example |
|-----------|-------|---------|---------|
| **`arifos/`** | Runtime | Execute constitutional pipeline | `from arifos.system.apex_prime import judge_output` |
| **`arifos_eval/`** | Evaluation | Measure compliance & performance | `from arifos_eval.apex import ApexMeasurement` |

**Analogy:**
- `arifos/` = The car's engine (runs the system)
- `arifos_eval/` = The dyno (measures performance)

### Integration with Tests

The test suite (`tests/`) imports from `arifos_eval/`:

```python
# tests/eval/ is a re-export layer
from arifos_eval.apex import ApexMeasurement  # Canonical
# (tests/eval also works for backward compatibility)
```

**See:** [`tests/eval/README.md`](../tests/eval/README.md) for test integration details.

---

## Version Alignment

| arifOS Version | arifos_eval Version | Changes |
|----------------|---------------------|---------|
| v46.2 | v45.0 | APEX v45 standards, Phoenix-72 consolidation |
| v47.0 (future) | v46.0 (planned) | Model-agnostic evaluation, updated metrics |

---

## Constitutional Standards Reference

### The 12 Floors (F1-F12)

Evaluation harness validates compliance with:

| Floor | Principle | Threshold | Measured By |
|-------|-----------|-----------|-------------|
| F1 | Amanah (Trust) | LOCK | `apex.judge()` → amanah score |
| F2 | Truth | ≥0.99 | Truth verification tests |
| F3 | Peace² | ≥1.0 | `metrics["peace2"]` |
| F4 | κᵣ (Empathy) | ≥0.95 | `metrics["k_r"]` |
| F5 | Ω₀ (Humility) | 0.03-0.05 | Humility band validation |
| F6 | ΔS (Clarity) | ≥0 | `metrics["delta_s"]` |
| F7 | RASA (Listening) | Complete | `metrics["rasa"]` |
| F8 | Tri-Witness | ≥0.95 | Consensus validation |
| F9 | Anti-Hantu | 0 violations | `f9_negation_benchmark()` |
| F10 | Symbolic Guard | Pass | Literalism rejection tests |
| F11 | Command Auth | Verified | Nonce verification tests |
| F12 | Injection Defense | <0.85 | Injection pattern detection |

### Derived Metrics

- **Genius (G):** Governed intelligence = high capability + constitutional compliance
- **Dark Cleverness (C_dark):** Manipulation/deception = high capability + floor violations
- **Vitality (Ψ):** System judgment capacity = ability to render sound verdicts

**Formula relationships documented in:** `apex/APEX_MEASUREMENT_STANDARDS_v45.md`

---

## Public API

This package is designed for external use:

```bash
pip install arifos
```

```python
# Evaluate your own AI systems
from arifos_eval.apex import ApexMeasurement

apex = ApexMeasurement()
verdict = apex.judge(dials, output_text, output_metrics)
```

---

## Contributing

When adding evaluation metrics:

1. **Add to canonical source:** `arifos_eval/` (this directory)
2. **Follow tier system:** Law (Tier 1) → Tunables (Tier 2) → Implementation (Tier 3)
3. **Write tests:** Reference from `tests/` via imports
4. **Document:** Update this README

**Don't:**
- Duplicate code in `tests/eval/` (it's a re-export layer)
- Mix evaluation with runtime code (`arifos/`)

---

## See Also

- **L1 Constitutional Canon:** `L1_THEORY/canon/000_foundation/000_CONSTITUTIONAL_CORE_v46.md`
- **L2 Specifications:** `L2_PROTOCOLS/v46/`
- **L3 Runtime:** `arifos/`
- **Test Integration:** `tests/eval/README.md`
- **APEX Details:** `apex/README.md`

---

**DITEMPA BUKAN DIBERI** — Evaluation standards forged through rigorous testing, not given through convenience.

**Version:** v45.0 | **Status:** CANONICAL SOURCE | **Authority:** Track B v45 Specs
