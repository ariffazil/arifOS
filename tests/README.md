# arifOS Test Suite

**Current:** ~110 test files (organized), ~2000+ test cases
**Coverage:** Core constitutional enforcement, MCP pipeline, Trinity governance, Session physics
**Organization:** Logical subdirectories by feature area (v46 reorganization)

---

## 📂 Test Organization (REORGANIZED 2026-01-10)

Tests are now organized into logical subdirectories:

```
tests/
├── core/           # 9 files - APEX, floors, GENIUS LAW
├── mcp/            # 14 files - 000→999 pipeline stages
├── trinity/        # 7 files - Trinity governance, FAG
├── waw/            # 7 files - W@W federation
├── memory/         # 15 files - Ledger, Phoenix-72
├── spec/           # Spec enforcement tests
├── integration/    # Cross-component tests
├── unit/           # Isolated unit tests
├── enforcement/    # Floor enforcement tests
├── governance/     # Governance tests
├── temporal/       # Time-based tests
└── [~58 misc]      # Root-level tests (to be categorized)
```

---
### Core Constitutional Tests
**Directory:** `tests/` (will be moved to `tests/core/` in future)
**Purpose:** Validate F1-F9 constitutional floors

| Test Category | Key Files | What It Tests |
|---------------|-----------|---------------|
| **APEX Prime** | `test_apex_prime_floors.py`, `test_apex_genius_verdicts.py` | Core verdict logic (SEAL/VOID/SABAR) |
| **Floor Enforcement** | `test_law_truth_threshold_enforcement.py` | F1-F9 threshold validation |
| **GENIUS LAW** | `test_genius_metrics.py` | G, C_dark, Ψ calculations |
| **Session Physics** | `test_session_physics.py`, `test_tearframe_integration.py` | TEARFRAME v44 physics |

### MCP Pipeline Tests
**Pattern:** `test_mcp_*.py`
**Purpose:** Validate 000→999 arifOS pipeline stages

| Stage | Test File | What It Tests |
|-------|-----------|---------------|
| 000 | `test_mcp_000_reset.py` | Session initialization |
| 111 | `test_mcp_111_sense.py` | Context sensing |
| 222 | `test_mcp_222_reflect.py` | Reflection stage |
| 444 | `test_mcp_444_evidence.py` | Evidence collection |
| 555 | `test_mcp_555_empathize.py` | Empathy check (F6) |
| 666 | `test_mcp_666_align.py` | Constitutional alignment |
| 777 | `test_mcp_777_forge.py` | Action forging |
| 888 | `test_mcp_888_judge.py` | APEX judgment |
| 999 | `test_mcp_999_seal.py` | Verdict sealing |

### Trinity & Governance Tests
**Pattern:** `test_trinity*.py`, `test_fag*.py`
**Purpose:** Multi-agent coordination, autonomous governance

- `test_trinity.py` — Tri-witness protocol
- `test_trinity_core.py` — Core Trinity logic
- `test_fag.py` — Full Autonomy Governance
- `test_fag_hardening.py` — FAG safety boundaries

### Memory & Ledger Tests
**Pattern:** `test_cooling_ledger*.py`, `test_ledger*.py`, `test_memory*.py`
**Purpose:** State persistence, audit trails, Phoenix-72

- `test_cooling_ledger_integrity.py` — Ledger integrity checks
- `test_ledger_cryptography.py` — Cryptographic verification
- `test_memory_trinity.py` — Memory band coordination

### W@W Federation Tests
**Pattern:** `test_waw_*.py`
**Purpose:** Witness@Work multi-model federation

- `test_waw_organs.py` — Federation organs (LAW, GEOX, WELL, RIF)
- `test_waw_apex_escalation.py` — Cross-witness escalation
- `test_waw_*_signals.py` — Individual organ signal tests

### Spec & Configuration Tests
**Directory:** `tests/spec/`
**Purpose:** Track B (tunable thresholds) enforcement

- `test_spec_v44_authority.py` — Single runtime authority
- `test_spec_loader_unified.py` — Spec loading logic
- `test_runtime_manifest.py` — Manifest integrity

---

## 🚀 Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Category
```bash
# Core constitutional
pytest tests/test_apex*.py tests/test_genius*.py tests/test_law*.py

# MCP pipeline
pytest tests/test_mcp_*.py

# Trinity
pytest tests/test_trinity*.py tests/test_fag*.py

# Memory & Ledger
pytest tests/test_*ledger*.py tests/test_memory*.py

# W@W Federation
pytest tests/test_waw_*.py

# Spec enforcement
pytest tests/spec/
```

### Run Specific Floor
```bash
# F1 (Amanah/Truth)
pytest -k "truth or amanah"

# F4 (Clarity/Entropy)
pytest -k "entropy or delta"

# F6 (Empathy)
pytest -k "empathy or kappa"
```

### Run with Coverage
```bash
pytest --cov=arifos_core --cov-report=html
```

---

## 🔍 Test Categories Explained

### Unit Tests
**Directory:** `tests/unit/`
**Scope:** Single function/class in isolation
**Examples:** `test_api_app.py` (API contracts)

### Integration Tests
**Directory:** `tests/integration/`, `tests/enforcement/`, `tests/governance/`
**Scope:** Multiple components working together
**Examples:** `test_pipeline_routing.py` (full pipeline flow)

### Validation Tests
**Directory:** `tests/validation/`
**Scope:** End-to-end constitutional compliance
**Examples:** Real-world scenario validation

---

## 📋 Test File Naming Convention

| Pattern | Purpose | Example |
|---------|---------|---------|
| `test_*.py` | Standard test | `test_apex_prime_floors.py` |
| `test_*_mocked.py` | Mock version | `test_apex_prime_floors_mocked.py` |
| `test_*_integration.py` | Integration test | `test_mcp_integration_phase3.py` |
| `test_*_v3X.py` | Legacy version | `test_memory_enforcement_v37.py` (archived) |

---

## ⏭️ Skipped Tests

Some tests are conditionally skipped based on dependencies:

```python
@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not installed")
@pytest.mark.skipif(not AMANAH_AVAILABLE, reason="AMANAH_DETECTOR not available")
@pytest.mark.skipif(not APEX_AVAILABLE, reason="ApexMeasurement not available")
```

**This is expected** — these tests run when optional dependencies are installed.

---

## 🏗️ Future Test Organization (Planned)

```
tests/
├── README.md (this file)
├── core/              # apex, floors, genius
├── mcp/               # test_mcp_*.py
├── trinity/           # test_trinity*.py, test_fag*.py
├── waw/               # test_waw_*.py
├── memory/            # test_*ledger*.py, test_memory*.py
├── spec/              # Already exists
├── integration/       # Already exists
├── unit/              # Already exists
└── archive/           # Legacy v37, v39 tests
    ├── v37/
    └── v39/
```

**Status:** Planned for future session (high effort)

---

## 🧪 Writing New Tests

### Test Template
```python
import pytest
from arifos_core.system.apex_prime import apex_review, Verdict

def test_my_feature():
    """Test that my feature does X."""
    # Arrange
    metrics = {...}

    # Act
    verdict = apex_review(metrics=metrics)

    # Assert
    assert verdict.verdict == Verdict.SEAL
    assert verdict.pulse >= 1.0
```

### Constitutional Test Template
```python
def test_f4_clarity_enforcement():
    """Verify F4 (ΔS Clarity) threshold enforcement."""
    # Below threshold → SEAL
    result = apex_review(metrics={"delta_s": 0.5})
    assert result.is_approved()

    # Above threshold → SABAR/VOID
    result = apex_review(metrics={"delta_s": -0.5})
    assert not result.is_approved()
```

---

## 📚 Related Documentation

- **Constitutional Floors:** `L1_THEORY/canon/00_MASTER_INDEX_v45.md`
- **APEX Prime:** `docs/APEX_PRIME_API.md`
- **MCP Pipeline:** `docs/MCP_PIPELINE_GUIDE.md`
- **Trinity:** `AGENTS.md` Section 1.0

---

## 🐛 Debugging Failed Tests

### Common Issues

**Issue:** `ImportError: cannot import name 'X'`
**Fix:** Check if imports match v46 8-folder structure

**Issue:** `KeyError: 'floor_name'`
**Fix:** Ensure `spec/v45/constitutional_floors.json` is loaded

**Issue:** `AssertionError: Expected SEAL, got VOID`
**Fix:** Check metrics meet all F1-F9 thresholds

### Debug Commands
```bash
# Run single test with verbose output
pytest -vv tests/test_apex_prime_floors.py::test_seal_verdict

# Show print statements
pytest -s tests/test_my_test.py

# Drop into debugger on failure
pytest --pdb tests/test_my_test.py
```

---

**Last Updated:** 2026-01-10
**Test Count:** ~113 files, ~2000+ cases
**Coverage:** ~85% of arifos_core

**DITEMPA BUKAN DIBERI** — Tests are forged through rigor, not given.
