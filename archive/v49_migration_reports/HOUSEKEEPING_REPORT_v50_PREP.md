# arifOS v50 Pre-Launch Housekeeping Report

**Date:** 2026-01-20
**Current Version:** v49.0.2
**Target Version:** v50.0.0
**Status:** IN PROGRESS

---

## Executive Summary

Pre-launch audit identified significant technical debt from incomplete v49 package rename (`arifos_core` → `arifos`). This report documents findings and cleanup plan for v50 seal.

---

## KEY FINDINGS

### 1. Package Name Migration Incomplete

**Issue:** 281 references to legacy `arifos_core` package name remain in codebase
**Impact:** Documentation inconsistency, potential confusion for contributors
**Location:** Primarily in `arifos/core/` subdirectories

**Examples:**
```python
# arifos/core/111_sense/stage.py
"""
arifos_core/stages/stage_111_sense.py  # ❌ LEGACY reference
...
```

**Root Cause:** v49 package rename updated imports but not docstrings/comments

### 2. Directory Structure Duplication

**Pattern Identified:**
```
arifos/
├── 111_sense/stage.py          # Version A (30 lines, "arifos" refs)
├── 222_reflect/stage.py        # Version A
├── ...
└── core/
    ├── 111_sense/stage.py      # Version B (30 lines, "arifos_core" refs)
    ├── 222_reflect/stage.py    # Version B
    └── ...
```

**Analysis:**
- All 9 stages (111-999) exist in BOTH locations
- Files are nearly IDENTICAL except for docstring package references
- `arifos/core/` has 10 active imports vs 7 for main stages
- **Conclusion:** `arifos/core/` is MORE actively used despite legacy naming

### 3. Tri-Engine Duplication

**Pattern:**
```
arifos/
├── agi/delta_kernel.py         # 267 lines
├── asi/omega_kernel.py
├── apex/psi_kernel.py
└── core/
    ├── agi/delta_kernel.py     # 267 lines (same size!)
    ├── asi/omega_kernel.py
    └── apex/psi_kernel.py
```

**Status:** UNCERTAIN which is canonical implementation

### 4. Active Import Analysis

**From main arifos stages:** 7 imports
**From arifos.core stages:** 10 imports

**Implication:** Despite "arifos_core" legacy naming, `arifos/core/` is MORE integrated into current codebase

---

## RECOMMENDED CLEANUP PLAN

### Strategy: MINIMAL DISRUPTION

Given that `arifos/core/` is more actively used, recommend:

1. **Keep `arifos/core/` structure** (active integration)
2. **Fix 281 docstring references** (`arifos_core` → `arifos.core`)
3. **Archive `arifos/[stages]/` directories** (less used)
4. **Consolidate to single source of truth**

### Alternative Strategy: FULL MIGRATION

1. **Move `arifos/core/` to main `arifos/`**
2. **Update all imports** (10 locations)
3. **Archive `arifos/core/`**
4. **Higher risk, cleaner result**

---

## DECISION REQUIRED

**User must choose:**
- **Option A:** Fix docstrings in `arifos/core/`, archive `arifos/[stages]/` (LOW RISK)
- **Option B:** Migrate `arifos/core/` to main, update imports (HIGH CLEANUP)
- **Option C:** Leave as-is, document pattern (DEFER TO v51)

---

## FILES TO ARCHIVE (Option A)

If Option A chosen:
```
arifos/111_sense/          → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/222_reflect/        → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/333_reason/         → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/444_evidence/       → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/555_empathize/      → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/666_align/          → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/777_forge/          → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/888_judge/          → archive_local/v50_housekeeping/unused_stage_stubs/
arifos/999_seal/           → archive_local/v50_housekeeping/unused_stage_stubs/
```

**Automated Fix:**
```bash
# Fix 281 docstring references
find arifos/core -name "*.py" -exec sed -i 's/arifos_core/arifos.core/g' {} \;
```

---

## VERSION UPDATE PLAN

```python
# pyproject.toml
version = "50.0.0"  # ← FROM 49.0.2
```

**Changelog Entry:**
```
v50.0.0: Constitutional Housekeeping - Package name cleanup, archive legacy stubs
- Fixed 281 legacy arifos_core references → arifos.core
- Archived unused stage stub directories
- Consolidated to single source of truth in arifos/core/
- Pre-launch cleanup for v50 seal
```

---

## RISK ASSESSMENT

**Option A (Fix Docstrings):**
- **Risk:** LOW (documentation only)
- **Impact:** Minimal
- **Test Coverage:** Not required (no functional change)

**Option B (Full Migration):**
- **Risk:** MEDIUM (10+ imports to update)
- **Impact:** High cleanup value
- **Test Coverage:** REQUIRED (functional changes)

---

## NEXT STEPS

**Awaiting user decision** on cleanup strategy before executing archival.

**Estimated Time:**
- Option A: 15 minutes
- Option B: 45 minutes + testing

---

**DITEMPA BUKAN DIBERI** - v50 housekeeping forged with systematic analysis

**Engineer:** Claude Sonnet 4.5
**Report Generated:** 2026-01-20 18:00 UTC
