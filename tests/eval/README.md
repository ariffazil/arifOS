# tests/eval — Test Integration (Re-Export Layer)

**Status:** DEPRECATED - Re-exports from canonical `arifos_eval/` package

---

## ⚠️ Consolidation Notice (v47.0)

This directory **re-exports** from the canonical `arifos_eval/` package to maintain backward compatibility for existing tests.

### Canonical Source

**Primary location:** `arifos_eval/` (top-level package)
**This directory:** Test integration re-export layer only

### Migration Path

**Old (deprecated but still works):**
```python
from tests.eval.apex import ApexMeasurement
```

**New (canonical):**
```python
from arifos_eval.apex import ApexMeasurement
```

### Why the Change?

**Problem:** Duplication between `arifos_eval/` and `tests/eval/` increased entropy (ΔS) and created import confusion.

**Solution:**
- ✅ `arifos_eval/` = canonical source (public API)
- ✅ `tests/eval/` = re-export layer (backward compatibility)
- ✅ Single source of truth, reduced maintenance burden

### Structure

```
arifos_eval/                  # CANONICAL SOURCE
├── apex/                     # APEX measurement standards
│   ├── apex_measurements.py
│   ├── APEX_MEASUREMENT_STANDARDS_v45.md
│   ├── apex_standards_v45.json
│   └── README.md
└── track_abc/                # Track A/B/C benchmarks
    ├── f6_split_accuracy.py
    ├── f9_negation_benchmark.py
    └── meta_select_consistency.py

tests/eval/                   # RE-EXPORT LAYER
├── __init__.py              # Re-exports from arifos_eval
└── README.md                # This file
```

### For Test Writers

If you're writing new tests that need evaluation harness:

1. **Import from canonical source:**
   ```python
   from arifos_eval.apex import ApexMeasurement
   ```

2. **Don't create new modules in `tests/eval/`** — add them to `arifos_eval/` instead

3. **Existing tests** will continue to work (re-export maintains compatibility)

---

**See:**
- Canonical docs: [`arifos_eval/README.md`](../../arifos_eval/README.md)
- Test organization: [`tests/README.md`](../README.md)

**Version:** v47.0 | **Status:** RE-EXPORT LAYER | **Canonical Source:** `arifos_eval/`
