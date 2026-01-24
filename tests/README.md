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

### Package-Level Tests (`arifos/`)

| Directory | Description |
|-----------|-------------|
| `arifos/tests/` | Core v50+ tests (metabolizer, trinity_server, floor_validators) |
| `arifos/clip/tests/` | CLI interface tests (000-999 metabolic pipeline commands) |

### Root Test Suite (`tests/`)

| Directory | Tests | Constitutional Floor | Description |
|-----------|-------|---------------------|-------------|
| `constitutional/` | 7 | F1-F13 | Floor boundary testing, threshold validation |
| `core/` | 13 | F4, F7 | Brain (BrainLoom) & physics (thermodynamics) |
| `enforcement/` | 3 | F4, F6, F9 | Floor enforcement logic, metrics validation |
| `eval/` | 5 | F2, F8 | Evaluation pipelines, scoring mechanisms |
| `evidence/` | 2 | F8 | Evidence pack assembly, conflict routing |
| `governance/` | 3 | F3, F11 | Merkle ledger, cryptographic proofs |
| `integration/` | 8 | All | Full 000→999 pipeline scenarios |
| `judiciary/` | 3 | F8, F11, F12 | Semantic firewall, witness council |
| `legacy/` | 4 | N/A | Deprecated pre-v49 tests (migration pending) |
| `mcp/` | 172 | All | Trinity Tools (000_init, agi_genius, asi_act, apex_judge, 999_vault) |
| `memory/` | 6 | F1 | 5-layer memory hierarchy, cooling ledger |
| `spec/` | 4 | F2, F10 | Spec loading, Sealion bindings |
| `temporal/` | 3 | F2 | Freshness decay, temporal intelligence |
| `test_integration/` | 2 | F11 | Command authority override logic |
| `trinity/` | 7 | F3, F8 | Trinity engine (AGI·ASI·APEX), FAG protocol |
| `unit/` | 3 | N/A | API, L7 memory, MCP server unit tests |
| `validation/` | 3 | All | Final validation, red team adversarial prompts |
| `waw/` | 0 | N/A | WAW protocol (placeholder, pending implementation) |

**Total:** 18 subdirectories | Each has its own README.md with detailed documentation

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