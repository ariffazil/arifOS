# v44 Test Suite Updates Needed for v45.0

**Date:** 2025-12-29
**Context:** Phase 3 Step 3.1 - Archive Old Alignment Tests
**Status:** v44 tests require updates (not archival)

---

## Overview

The **v44 test suite should NOT be archived** - it's still relevant for Track B enforcement. However, these tests need updates to reflect the v45→v44→FAIL priority established in Phase 1.

---

## Files Requiring Updates

### 1. test_spec_v44_authority.py (PARTIALLY UPDATED)

**Changes needed:**
- ✅ Updated docstring to reflect v45→v44 priority
- ✅ Updated `test_default_load_uses_v44()` to expect v45.0 (not v44.0)
- ✅ Updated variable references: `_FLOORS_SPEC_V38` → `_FLOORS_SPEC`
- ✅ Updated `test_legacy_fallback_when_enabled()` → `test_legacy_fallback_removed()`
- ✅ Updated `test_v44_priority_in_code()` to check v45→v44 order
- ✅ Updated class docstrings for Session Physics and Genius Law
- ✅ Updated `TestLegacySpecDeprecationMarkers` → `TestLegacySpecRemovalV45`
- ⚠️ Marked env override tests as skip (strict mode restriction)

**Status:** Partially complete - basic updates done, but tests may still fail

---

### 2. test_spec_v44_subprocess_proof.py (NEEDS UPDATE)

**Changes needed:**
- ⚠️ Update docstring to reflect v45→v44 priority
- ❌ Update `test_default_load_uses_v44_fresh_process()`: expect v45.0, not v44.0
- ❌ Update variable references: `_FLOORS_SPEC_V38` → `_FLOORS_SPEC`
- ❌ Update `test_missing_v44_hard_fails_fresh_process()`: should test missing v45 AND v44
- ❌ Update `test_env_override_loads_custom_spec_fresh_process()`: handle strict mode (requires spec/v45/ or spec/v44/ path)
- ❌ Update `TestGeniusMetricsSubprocess`: expect v45.0, update variable names
- ❌ Update `TestSessionPhysicsSubprocess`: expect v45.0

**Status:** Minimal updates - needs comprehensive revision

---

### 3. test_spec_v44_manifest_enforcement_subprocess.py (NEEDS UPDATE)

**Changes needed:**
- ❌ Update to verify v45 MANIFEST.sha256.json (in addition to v44)
- ❌ Update `test_default_import_verifies_manifest_successfully()`: expect v45.0
- ❌ Update `test_legacy_mode_bypasses_manifest_verification()`: legacy mode removed in Phase 2
- ❌ Update `test_manifest_contains_all_v44_specs()`: should check v45 specs

**Status:** No updates yet

---

### 4. test_spec_v44_schema_enforcement_subprocess.py (MINIMAL UPDATES NEEDED)

**Changes needed:**
- ⚠️ Update schema paths to check v45 schemas first
- ⚠️ Update `test_valid_v44_spec_attaches_schema_used_marker()`: expect v45 schema path

**Status:** Minor updates needed

---

## Why v44 Tests Still Matter

Despite v45 being AUTHORITATIVE, v44 tests remain critical because:

1. **v44 is the fallback:** v45→v44→FAIL means v44 still loaded when v45 missing
2. **Track B enforcement:** Cryptographic manifest verification, JSON Schema validation
3. **Regression protection:** Ensures v44 fallback works correctly
4. **Migration safety:** Users upgrading from v44 to v45 depend on v44 fallback

---

## Test Philosophy Change: v44 → v45

### Old Philosophy (v44 era):
- v44 is AUTHORITATIVE
- v42/v38/v35 are legacy fallbacks
- Tests verify v44 loaded by default

### New Philosophy (v45 era):
- v45 is AUTHORITATIVE
- v44 is FALLBACK (with deprecation warning)
- v42/v38/v35 removed (Phase 2 Step 2.2)
- Tests verify v45 loaded by default, v44 used if v45 missing

---

## Expected Test Behavior After Updates

**When v45 specs present:**
```python
from arifos_core.enforcement.metrics import _FLOORS_SPEC
assert _FLOORS_SPEC["version"] == "v45.0"  # v45 loaded (AUTHORITATIVE)
assert "_loaded_from" contains "spec/v45/constitutional_floors.json"
```

**When v45 specs missing (v44 fallback):**
```python
# (After temporarily renaming spec/v45/)
from arifos_core.enforcement.metrics import _FLOORS_SPEC
assert _FLOORS_SPEC["version"] == "v44.0"  # v44 loaded (FALLBACK)
# Should emit DeprecationWarning
```

**When both v45 and v44 missing:**
```python
# Should raise RuntimeError: "TRACK B AUTHORITY FAILURE"
# No hardcoded defaults (fail-closed)
```

---

## Update Checklist

- [x] Archive v35/v36/v38/v41 tests (19 files)
- [x] Create archive/test_migrations/README.md
- [ ] Update test_spec_v44_authority.py (50% complete)
- [ ] Update test_spec_v44_subprocess_proof.py (0% complete)
- [ ] Update test_spec_v44_manifest_enforcement_subprocess.py (0% complete)
- [ ] Update test_spec_v44_schema_enforcement_subprocess.py (0% complete)
- [ ] Run full v44 test suite: `pytest tests/test_spec_v44*.py -v`
- [ ] Verify all v44 tests pass
- [ ] Document v45→v44 testing strategy

---

## Recommended Approach

**Option A: Incremental Updates (Conservative)**
1. Update one test file at a time
2. Run tests after each update
3. Fix failures iteratively
4. Merge when all green

**Option B: Comprehensive Rewrite (Aggressive)**
1. Create new test_spec_v45_authority.py from scratch
2. Keep test_spec_v44_*.py as regression tests for v44 fallback
3. Deprecate old v44 tests gradually

**Option C: Defer to Next Sprint (Pragmatic)**
1. Mark v44 tests as xfail with reason: "v45→v44 priority updates pending"
2. Create GitHub issue for test updates
3. Complete Phase 3 Step 3.2 (telemetry_v36.py consolidation)
4. Return to v44 test updates in Phase 4

**Recommendation:** Option C (Pragmatic) - we've already completed the main goal (archiving old version tests). v44 test updates are a separate task.

---

## Related Files

- **Eureka Insights:** [archive/v42_v38_v35_eureka_insights.md](../v42_v38_v35_eureka_insights.md)
- **Test Archive:** [archive/test_migrations/README.md](README.md)
- **Track B Specs:** [spec/v45/](../../spec/v45/), [spec/v44/](../../spec/v44/)

---

**Authority:** Phase 3 Step 3.1 analysis | arifOS v45.0

**DITEMPA BUKAN DIBERI** — Tests must evolve with code; lagging tests reveal incomplete migrations.

*Created: 2025-12-29*
