# Core System Tests

**Scope:** The Brain & Physics
**Target:** `arifos.core.*`

This directory contains tests for the fundamental mechanisms of arifOS:

1.  **Metabolizer (`metabolizer.py`):**
    *   State machine transitions (000 → 111 → ... → 999).
    *   Loop Detection (preventing 111→222→111 cycles).
    *   Timeout enforcement.

2.  **Thermodynamics:**
    *   Entropy calculation (ΔS).
    *   Peace² metric validation.
    *   Humility (Ω₀) banding.

3.  **Floor Validators:**
    *   Python implementations of F1-F13 checks.
    *   Ensuring hard floors (F1, F11, F12) raise exceptions appropriately.

**Key Command:**
```bash
pytest tests/core
```
