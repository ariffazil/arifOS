# arifOS Constitutional Test Suite (v50.5.4)

**Authority:** 888 Judge
**Status:** PRODUCTION
**Coverage Target:** 100% of `arifos/` (Core Sovereign Runtime)

---

## 🧪 Philosophy: Testing as Governance

In arifOS, testing is not just about code correctness; it is about **Constitutional Integrity**.
We do not just test if a function returns `True`. We test if:
1.  **F1 Amanah:** The action is reversible and auditable.
2.  **F2 Truth:** The confidence score meets the ≥0.99 threshold.
3.  **F4 Clarity:** Entropy (ΔS) decreases after processing.
4.  **Structure:** The 000-999 Metabolic Loop is respected.

**"Ditempa Bukan Diberi"** — Stability is forged through rigorous testing.

---

## 🚀 Quick Start

### Run All Tests
```bash
pytest
```

### Run by Category (Markers)
```bash
# Constitutional Floors (F1-F13)
pytest -m constitutional

# Core Logic (Metabolizer, Engines)
pytest -m unit

# Integration (Full Pipeline)
pytest -m integration

# Body API (FastAPI)
pytest -m api
```

### Run Specific Floor Checks
```bash
pytest -m f1   # Amanah
pytest -m f2   # Truth
pytest -m f6   # Empathy
pytest -m f12  # Injection Defense
```

---

## 📂 Test Organization

The suite is split into two domains:

1.  **`arifos/tests/`** (The New Core):
    *   Tests for the v50+ package structure.
    *   Focuses on `metabolizer.py`, `trinity_server.py`, and `floor_validators.py`.
    *   **Strict Type Checking:** Enforced.

2.  **`tests/`** (The Legacy & Integration Suite):
    *   **`core/`**: Deep physics testing (entropy, thermodynamics).
    *   **`mcp/`**: Testing the 5 Trinity Tools (`000_init`, `agi_genius`, etc.).
    *   **`constitutional/`**: Specialized boundary testing for F1-F13.
    *   **`integration/`**: End-to-end scenarios (e.g., "User asks to delete file").

---

## ⚙️ Environment & Configuration

Tests run with specific environment variables (set in `conftest.py`):

*   `ARIFOS_PHYSICS_DISABLED=1`: Disables heavy thermodynamic calculations for unit tests to speed up execution.
*   `ARIFOS_ALLOW_LEGACY_SPEC=1`: Bypasses strict cryptographic manifest checks for test files.

**To run with Full Physics:**
```bash
# Linux/Mac
ARIFOS_PHYSICS_DISABLED=0 pytest

# Windows (PowerShell)
$env:ARIFOS_PHYSICS_DISABLED="0"; pytest
```

---

## 📊 Coverage Goals

We track coverage for the **Sovereign Core** (`arifos/`).

```bash
# Generate HTML report
pytest --cov=arifos --cov-report=html
```

*   **Current Baseline:** 100% for new v50 modules.
*   **Target:** 70% Global Coverage by Q2 2026.

---

## 🛠️ Debugging

If a test fails with **`ConstitutionalViolationError`**:
1.  The code logic might be correct, but it violated a **Floor**.
2.  Check the `floor_scores` in the output.
3.  Did it fail **F2 Truth** (< 0.99)?
4.  Did it fail **F4 Clarity** (ΔS > 0)?

**Fix the Governance, not just the Code.**