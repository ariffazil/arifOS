# telemetry_v36.py Consolidation Archive

**Archive Date:** 2025-12-29
**Phase:** Phase 3 Step 3.2 (Consolidate telemetry_v36.py)
**Reason:** Unused builder module with incorrect imports - consolidated into telemetry.py

---

## What Was Archived

**telemetry_v36.py** (595 lines, 20KB)
- v36.3Ω-era telemetry entry builder functions
- Never actually used in active codebase
- Only referenced by archived test file

---

## Analysis: Why telemetry_v36.py Was Unused

### Incorrect Imports in Active Code

**L6_SEALION/integrations/sealion/judge.py (line 46):**
```python
from arifos_core.utils.telemetry_v36 import telemetry as _telemetry  # ← This fails!
```

**Problem:** telemetry_v36.py exports builder functions, NOT a `telemetry` singleton.

**What exists in telemetry_v36.py:**
- `build_telemetry_entry_v36()` - function
- `build_floor_metrics_v36()` - function
- `build_verdict_v36()` - function
- NO `telemetry` object

**What should have been imported:**
```python
from arifos_core.utils.telemetry import telemetry as _telemetry  # ← Correct
```

---

## Actual vs Intended Usage

### Intended Design (v36.3Ω era)

**Two-layer architecture:**
1. **telemetry_v36.py** - Low-level builders (spec-compliant entry dictionaries)
2. **telemetry.py** - High-level logger (JSONL file writer with `telemetry` singleton)

**Intended workflow:**
```python
from arifos_core.utils.telemetry_v36 import build_telemetry_entry_v36
from arifos_core.utils.telemetry import telemetry

# Build spec-compliant entry
entry = build_telemetry_entry_v36(
    query="What is AI?",
    response="AI is artificial intelligence...",
    floor_metrics={"truth": 0.99, "delta_s": 0.5},
    floor_results={"F1": True, "F2": True},
    verdict_code="SEAL",
)

# Log to JSONL file
telemetry.log_custom_event(entry)
```

### Actual Reality (v45.0)

**Single-layer architecture:**
- **telemetry.py** only - Lightweight JSONL logger with preview-based events
- Builder functions NEVER called
- Two separate implementations:
  - zkpc_runtime.py builds cooling ledger entries (similar role to v36 builders)
  - telemetry.py logs lightweight preview events (different schema)

**Why builders were bypassed:**
- zkpc_runtime took over spec-compliant entry building
- telemetry.py remained lightweight (preview-only)
- No code path actually called telemetry_v36 builders

---

## Functions Archived

### Hash Utilities
- `_sha256_hex()` - SHA-256 hash generator (HOTSPOT 7)

### Builders (HOTSPOT 8: Floor Structure)
- `build_floor_metrics_v36()` - Floor metrics dict
- `build_floor_results_v36()` - Floor pass/fail results dict

### Verdict Builder (HOTSPOT 9)
- `build_verdict_v36()` - Structured verdict with violations

### Aggregate Builders
- `build_aggregate_metrics_v36()` - G, C_dark, Psi metrics
- `build_truth_polarity_v36()` - Light/Shadow/Weaponized truth
- `build_cce_audits_v36()` - Delta/Omega/Psi/Phi audits
- `build_waw_signals_v36()` - W@W Federation votes
- `build_audit_trail_v36()` - Hash-chain integrity fields

### Main Entry Builder
- `build_telemetry_entry_v36()` - Complete v36.3Ω-compliant entry

### Derivation Utilities
- `derive_violations_from_floors()` - Extract violations from results
- `derive_verdict_code()` - Derive verdict from violations

---

## Constants Archived

- `VERSION = "v36.3Omega"`
- `HARD_FLOORS = {"F1", "F2", "F5", "F6", "F7", "F9"}`
- `SOFT_FLOORS = {"F3", "F4", "F8"}`
- `FLOOR_METRIC_MAP` - Metric name → Floor ID mapping
- `VALID_VERDICT_CODES = {"SEAL", "PARTIAL", "HOLD_888", "SABAR", "VOID"}`
- `VALID_STAKES = {"low", "medium", "high", "critical"}`
- `VALID_PIPELINE_PATHS = {"CLASS_A", "CLASS_B"}`

---

## Spec Alignment Context

### v36.3Ω Spec (HOTSPOTs Closed)

**Spec Location:** `archive/versions/v36_3_omega/v36.3O/spec/apex_prime_telemetry_v36.3O.json`

**HOTSPOT 7:** query_hash/response_hash (SHA-256)
- ✅ Implemented via `_sha256_hex()`
- **Reality:** zkpc_runtime uses SHA-256, not telemetry_v36

**HOTSPOT 8:** floor_metrics{} + floor_results{} split structure
- ✅ Implemented via `build_floor_metrics_v36()` and `build_floor_results_v36()`
- **Reality:** zkpc_runtime builds this directly, not via telemetry_v36

**HOTSPOT 9:** Structured verdict object with code/violations
- ✅ Implemented via `build_verdict_v36()`
- **Reality:** apex_prime.py builds Verdict dataclass, not telemetry_v36

---

## Why Consolidation = Deletion

**No consolidation needed** because:
1. **No active usage:** Builder functions never called
2. **Wrong abstraction:** zkpc_runtime builds cooling ledger entries directly
3. **Diverged specs:** telemetry.py uses lightweight preview schema, NOT v36.3Ω spec
4. **Import errors:** Only import was incorrect (tried to import non-existent `telemetry` object)

**Outcome:**
- Archive telemetry_v36.py for historical reference
- Fix incorrect imports (judge.py line 46, telemetry.py docstring line 37)
- NO code moved to telemetry.py (different purposes, no overlap)

---

## Changes Made (Phase 3 Step 3.2)

### 1. Fixed Incorrect Import in judge.py
```python
# BEFORE (line 46):
from arifos_core.utils.telemetry_v36 import telemetry as _telemetry  # ← ImportError!

# AFTER:
from arifos_core.utils.telemetry import telemetry as _telemetry  # ← Correct
```

### 2. Fixed Docstring Typo in telemetry.py
```python
# BEFORE (line 37):
from arifos_core.utils.telemetry_v36 import telemetry  # ← Wrong module

# AFTER:
from arifos_core.utils.telemetry import telemetry  # ← Correct
```

### 3. Archived telemetry_v36.py
- Moved from: `arifos_core/utils/telemetry_v36.py`
- Moved to: `archive/telemetry_v36_consolidation/telemetry_v36.py`
- Test file already archived: `archive/test_migrations/test_telemetry_v36_spec_alignment.py`

---

## Restoration Procedure

**To restore telemetry_v36.py (if needed for historical research):**

```bash
# From repo root
cp archive/telemetry_v36_consolidation/telemetry_v36.py arifos_core/utils/

# Restore test file
cp archive/test_migrations/test_telemetry_v36_spec_alignment.py tests/

# Run tests
pytest tests/test_telemetry_v36_spec_alignment.py -v
```

**Note:** Restoration will NOT fix the import errors - judge.py and telemetry.py were importing incorrectly.

---

## Entropy Metrics

**Before Phase 3 Step 3.2:**
- arifos_core/utils/telemetry_v36.py: 595 lines (20KB)
- Incorrect imports: 2 (judge.py, telemetry.py docstring)
- Active usage: 0 call sites

**After Phase 3 Step 3.2:**
- telemetry_v36.py archived
- Incorrect imports fixed: 2 → 0
- Code entropy reduction: 595 lines removed from active codebase
- Documentation preservation: 100% (this README + archived source)

---

## Related Files

- **Archived Source:** [telemetry_v36.py](telemetry_v36.py) - Full v36.3Ω builder implementation
- **Archived Test:** [../test_migrations/test_telemetry_v36_spec_alignment.py](../test_migrations/test_telemetry_v36_spec_alignment.py)
- **Active Telemetry:** [arifos_core/utils/telemetry.py](../../arifos_core/utils/telemetry.py) - Current JSONL logger
- **Spec Builder:** [arifos_core/governance/zkpc_runtime.py](../../arifos_core/governance/zkpc_runtime.py) - Cooling ledger entry builder

---

## Eureka Insights

### Insight 1: Import Errors Can Hide Dead Code
The incorrect import in judge.py meant telemetry_v36 was never actually loaded, even though it appeared to be "used." Static analysis (grep) found references, but runtime analysis would show ImportError.

### Insight 2: Two-Layer Abstraction Collapsed
The intended v36.3Ω design had builders (telemetry_v36) + logger (telemetry). In practice, zkpc_runtime became the builder, telemetry stayed lightweight. The middle layer (telemetry_v36) became vestigial.

### Insight 3: Spec Alignment ≠ Code Usage
telemetry_v36.py was marked "FULL alignment (closes HOTSPOTs 7, 8, 9)" in its docstring, but ZERO code actually used it. Spec-aligned code is worthless if not called.

### Insight 4: Version Tags in Filenames Create Debt
`telemetry_v36.py` name implied it was the "v36 version" of telemetry, but v45 still referenced it. Should have been `telemetry_builders.py` (no version tag) if it was meant to be timeless.

---

**Authority:** Phase 3 Step 3.2 per plan file `C:\Users\User\.claude\plans\lovely-nibbling-owl.md`

**DITEMPA BUKAN DIBERI** — Dead code should be honored with archival, not silently deleted.

*Created: 2025-12-29 | arifOS v45.0 | Phase 3 Step 3.2 Complete*
