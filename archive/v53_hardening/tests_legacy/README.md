# Legacy Tests (Archived)

**Status:** SKIPPED BY DEFAULT
**Purpose:** Reference for deprecated APIs

---

## Overview

This directory contains **71 archived test files** that reference obsolete APIs from pre-v50 arifOS versions. These tests are automatically skipped by pytest via `conftest.py`.

---

## Why Tests Were Moved Here

Tests were archived for one of these reasons:

| Reason | Examples |
|--------|----------|
| Missing modules (`arifos.core.mcp`, `arifos.stage_000_void`) | `test_mcp_*.py`, `test_epoch_comparison.py` |
| Wrong function signatures (API changed) | `test_apex_prime_floors*.py`, `test_f6_empathy_split.py` |
| Missing classes (`InjectionGuard.detect`, `ClipboardManager`) | `test_e2e_full_pipeline_real_servers.py` |
| Threshold/scoring changes | `test_f9_negation_aware_v1.py` |
| Physics model discrepancies | `test_mother_earth_equations.py` |

---

## Running Legacy Tests (Not Recommended)

Legacy tests are skipped by `conftest.py`. To run them explicitly:

```bash
# Remove or bypass conftest.py
mv tests/legacy/conftest.py tests/legacy/conftest.py.bak
pytest tests/legacy/ -v

# Restore after testing
mv tests/legacy/conftest.py.bak tests/legacy/conftest.py
```

---

## Migration Path

If you need to resurrect a legacy test:

1. **Check the module imports** - Update to current arifOS v50+ paths
2. **Check function signatures** - Use `python -c "from module import func; help(func)"`
3. **Check floor numbers** - F1-F13 names changed in v50 (e.g., F3 Stability → F3 Tri-Witness)
4. **Update assertions** - Verdict thresholds may have changed

---

## Files Archived (2026-01-23)

Moved during test alignment cleanup from:
- `tests/` root (root-level duplicates and broken tests)
- `tests/constitutional/` (broken e2e and pipeline tests)
- `tests/core/` (apex_prime_floors, floor_scoring)
- `tests/enforcement/` (f6_empathy_split, f9_negation)
- `tests/integration/` (migration API, vault999)
- `tests/memory/` (memory_trinity, phoenix72)
- `tests/spec/` (sealion_spec_binding)
- `tests/trinity/` (trinity_core, fag_write)
- `tests/unit/` (mcp_server, l7_memory, api_app)
- `tests/validation/` (mother_earth_equations)

---

**Status:** ARCHIVED
**DITEMPA BUKAN DIBERI**
