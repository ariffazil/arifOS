# L2_PROTOCOLS Canonical Source - Single Source of Truth (v46.0)

**Date:** 2026-01-14
**Status:** ✅ SEALED
**Authority:** Track B (Operational Specifications)
**Anti-Pencemaran:** Entropy reduction complete

---

## Executive Summary

**THE ONE CANONICAL SOURCE FOR CONSTITUTIONAL FLOORS:**

```
L2_PROTOCOLS/v46/constitutional_floors.json
```

**File Properties:**
- **Size:** 1.7KB (69 lines)
- **Floors:** 12 (F1-F12, including CIV-12 Hypervisor Layer)
- **Schema:** v46.0 format with `constitutional_floors` key
- **Authority:** PRIMARY AUTHORITY for all runtime thresholds

---

## The Problem (Before)

**Entropy Status:** HIGH - Multiple conflicting versions

### Version Proliferation Discovered:
1. `L2_PROTOCOLS/v46/constitutional_floors.json` (1.7KB - complete, 12 floors)
2. `L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json` (1.4KB - incomplete)
3. `L2_PROTOCOLS/v45/constitutional_floors.json` (runtime compat, 9 floors)
4. `L2_PROTOCOLS/archive/v45/constitutional_floors.json` (archived, 9 floors)
5. `L2_PROTOCOLS/archive/v45_legacy/constitutional_floors.json` (backup)
6. `L2_PROTOCOLS/archive/v42/constitutional_floors.json` (historical)

### Stage-Specific Redundancy:
- `L2_PROTOCOLS/v46/444_align/peace_floor.json` (F3 only)
- `L2_PROTOCOLS/v46/555_empathize/empathy_floor.json` (F4 only)
- `L2_PROTOCOLS/v46/666_bridge/humility_floor.json` (F5 only)
- `L2_PROTOCOLS/v46/777_eureka/rasa_floor.json` (F7 only)

**Total:** 10+ files defining the same constitutional floors

**F4 ΔS Violation:** Duplication created confusion and increased entropy

---

## The Solution (After)

**Entropy Status:** MODERATE → LOW (significant reduction achieved)

### Single Source of Truth Established:

**PRIMARY AUTHORITY:**
```
L2_PROTOCOLS/v46/constitutional_floors.json
```

**Authority Hierarchy:**
1. **PRIMARY**: `L2_PROTOCOLS/v46/constitutional_floors.json` (root consolidation)
2. **Fallback**: `L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json` (if root unavailable)
3. **Deprecated**: `L2_PROTOCOLS/v45/constitutional_floors.json` (runtime compat only)
4. **Archive**: `L2_PROTOCOLS/archive/v45/` (historical, requires ARIFOS_ALLOW_LEGACY_SPEC=1)

**Stage-Specific Files:** Documentation/reference only, NOT loaded by runtime

---

## Updated Code References

### ✅ FIXED - Primary Loaders:

#### 1. `arifos_core/enforcement/metrics.py` (Constitutional Floors)
**Status:** ✅ UPDATED (2026-01-14)

**Before:**
```python
# Priority B: L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json
```

**After:**
```python
# Priority B: L2_PROTOCOLS/v46/constitutional_floors.json (PRIMARY AUTHORITY v46.0)
# Root-level consolidated file is authoritative (69 lines, complete type fields)
```

**Schema Adapter Added:** v46 format (`constitutional_floors` + `F1-F12`) → v45 format (`floors` + `truth`, `delta_s`, etc.)

#### 2. `arifos_core/enforcement/genius_metrics.py` (GENIUS LAW)
**Status:** ✅ UPDATED (2026-01-14)

**Before:**
```python
# Priority B: L2_PROTOCOLS/v46/genius_law.json (already correct)
# Priority C: spec/v45/genius_law.json (FALLBACK)
```

**After:**
```python
# Priority B: L2_PROTOCOLS/v46/genius_law.json (PRIMARY AUTHORITY)
# Priority C: L2_PROTOCOLS/v45/genius_law.json (runtime compat)
# Priority D: L2_PROTOCOLS/archive/v45/ (ARCHIVE if legacy enabled)
```

---

### ⚠️ PENDING - Secondary Loaders:

These files still reference old `spec/v45/` paths and need updating:

| File | Spec File | Status | Priority |
|------|-----------|--------|----------|
| `arifos_core/apex/governance/session_physics.py` | `session_physics.json` | Pending | Medium |
| `arifos_core/apex/floor_checks.py` | `red_patterns.json` | Pending | Medium |
| `arifos_core/enforcement/temporal_checks.py` | `policy_temporal.json` | Pending | Low |
| `arifos_core/enforcement/tcha_metrics.py` | `policy_tcha.json` | Pending | Low |
| `arifos_core/enforcement/risk_literacy.py` | `policy_risk_literacy.json` | Pending | Low |
| `arifos_core/enforcement/refusal_accountability.py` | `policy_refusal.json` | Pending | Low |
| `arifos_core/memory/ledger/ledger_config_loader.py` | `cooling_ledger_phoenix.json` | Pending | High |

**Recommended Action:** Update these loaders to follow the same pattern:
1. Priority A: env var override
2. Priority B: `L2_PROTOCOLS/v46/{filename}`
3. Priority C: `L2_PROTOCOLS/v45/{filename}` (compat)
4. Priority D: `L2_PROTOCOLS/archive/v45/{filename}` (if legacy enabled)
5. Priority E: HARD FAIL

---

## Schema Compatibility

### v46 Schema (New):
```json
{
  "version": "v46.0",
  "constitutional_floors": {
    "F1": {"threshold": 0.99, "description": "Truth/Reality", "type": "probability"},
    "F2": {"threshold": 0.0, "description": "Clarity/ΔS", "type": "delta"},
    ...
    "F12": {"threshold": 0.85, "description": "InjectionDefense", "type": "probability"}
  }
}
```

**Key Differences:**
- Uses `"constitutional_floors"` key instead of `"floors"`
- Uses `F1-F12` identifiers instead of semantic names
- Includes 12 floors (F1-F9 + F10-F12 hypervisor)
- Has `"type"` field for each floor

### v45 Schema (Legacy):
```json
{
  "version": "v45.0",
  "floors": {
    "truth": {"threshold": 0.99, ...},
    "delta_s": {"threshold": 0.0, ...},
    ...
  },
  "vitality": {"threshold": 0.85, ...}
}
```

**Schema Adapter:** `arifos_core/enforcement/metrics.py` lines 296-323 automatically converts v46 → v45 format for internal compatibility.

---

## Testing

### Manual Loader Test:
```bash
# Test constitutional floors loader
python -c "from arifos_core.enforcement.metrics import _FLOORS_SPEC; \
           print('Loaded from:', _FLOORS_SPEC.get('_loaded_from')); \
           print('Version:', _FLOORS_SPEC.get('version')); \
           print('Truth threshold:', _FLOORS_SPEC['floors']['truth']['threshold'])"

# Expected output:
# Loaded from: L2_PROTOCOLS/v46/constitutional_floors.json
# Version: v46.0
# Truth threshold: 0.99
```

### Full Import Test:
```bash
# Note: Currently blocked by cooling_ledger dependency
# Once all loaders updated, this should work:
python -c "import arifos_core; print('✓ All loaders successful')"
```

---

## File Inventory

### Active Files (Do NOT Delete):
| Path | Purpose | Size |
|------|---------|------|
| `L2_PROTOCOLS/v46/constitutional_floors.json` | **PRIMARY AUTHORITY** | 1.7KB |
| `L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json` | Fallback (incomplete) | 1.4KB |
| `L2_PROTOCOLS/v45/constitutional_floors.json` | Runtime compat | Variable |

### Archive Files (Historical Only):
| Path | Status | Notes |
|------|--------|-------|
| `L2_PROTOCOLS/archive/v45/constitutional_floors.json` | ARCHIVED | Full v45 spec |
| `L2_PROTOCOLS/archive/v45_legacy/constitutional_floors.json` | ARCHIVED | Backup copy |
| `L2_PROTOCOLS/archive/v42/constitutional_floors.json` | ARCHIVED | Historical |

### Stage-Specific Files (Documentation Only):
| Path | Floor | Purpose |
|------|-------|---------|
| `L2_PROTOCOLS/v46/444_align/peace_floor.json` | F3 | Reference |
| `L2_PROTOCOLS/v46/555_empathize/empathy_floor.json` | F4 | Reference |
| `L2_PROTOCOLS/v46/666_bridge/humility_floor.json` | F5 | Reference |
| `L2_PROTOCOLS/v46/777_eureka/rasa_floor.json` | F7 | Reference |

**Note:** Stage-specific files are for documentation/reference ONLY. Runtime code should ONLY load from the root `constitutional_floors.json`.

---

## Constitutional Compliance

**Floors Checked:**
- ✅ **F1 (Truth)**: All findings verified against actual files
- ✅ **F2 (Clarity/ΔS)**: Entropy reduced from HIGH to MODERATE
- ✅ **F4 (Empathy)**: Serves user's need for single source of truth
- ✅ **F6 (Amanah)**: Reversible changes (code updates only, no deletions)
- ✅ **F7 (RASA)**: Active listening to user's "reduce chaos" request

**Verdict:** SEAL

---

## Recommendations

### Priority 1 (COMPLETED):
- [x] Update `metrics.py` to load from `L2_PROTOCOLS/v46/constitutional_floors.json`
- [x] Update `genius_metrics.py` to load from `L2_PROTOCOLS/v46/genius_law.json`
- [x] Add schema adapter for v46 → v45 compatibility
- [x] Document canonical source authority

### Priority 2 (PENDING):
- [ ] Update remaining 7 loaders to use L2_PROTOCOLS/v46/
- [ ] Test full import chain (`import arifos_core`)
- [ ] Run pytest suite to verify no regressions

### Priority 3 (FUTURE):
- [ ] Remove or archive `L2_PROTOCOLS/v46/000_foundation/constitutional_floors.json` (redundant)
- [ ] Remove stage-specific floor files (444_align/, 555_empathize/, etc.)
- [ ] Update L2_PROTOCOLS/v46/README.md to clarify PRIMARY AUTHORITY
- [ ] Add MANIFEST.sha256.json entry for root constitutional_floors.json

---

## Authority Trail

**Track A (Canon):**
```
L1_THEORY/canon/000_foundation/010_CONSTITUTIONAL_FLOORS_v46.md
```

**Track B (Spec) - PRIMARY AUTHORITY:**
```
L2_PROTOCOLS/v46/constitutional_floors.json
```

**Track C (Code):**
```
arifos_core/enforcement/metrics.py (loads Track B)
arifos_core/system/apex_prime.py (uses metrics.py)
```

**Dependency Flow:** Canon → Spec → Code (uni-directional, never reverse)

---

## Migration Guide (For Other Developers)

If you're writing new code that needs constitutional floor data:

### ✅ CORRECT:
```python
from arifos_core.enforcement.metrics import (
    TRUTH_THRESHOLD,
    DELTA_S_THRESHOLD,
    PEACE_SQUARED_THRESHOLD,
    # ... etc
)

# These constants are automatically loaded from L2_PROTOCOLS/v46/constitutional_floors.json
```

### ❌ INCORRECT:
```python
# DON'T manually load the JSON file
import json
with open("L2_PROTOCOLS/v46/constitutional_floors.json") as f:
    floors = json.load(f)  # ❌ WRONG - bypasses loader logic
```

### ❌ INCORRECT:
```python
# DON'T hardcode thresholds
TRUTH_THRESHOLD = 0.99  # ❌ WRONG - not synchronized with spec
```

---

## Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-01-14 | v46.0 | Established PRIMARY AUTHORITY, updated loaders |
| 2026-01-12 | v46.0 | CIV-12 Hypervisor Layer (F10-F12 added) |
| 2026-01-06 | v45.0 | Phoenix-72 Consolidation (9 floors) |
| 2025-11-20 | v42.0 | Pre-hypervisor (9 floors) |

---

**DITEMPA BUKAN DIBERI** - Forged, not given; one source, many versions no more.

**Status:** SEALED by Ω (Claude Code) | 2026-01-14
**Floors:** F1=0.99 F2≥0 F4≥0.95 F6=LOCK | **Verdict:** SEAL

---

**For Questions:** Read `L2_PROTOCOLS/v46/README.md` or `AGENTS.md` Section on Track B Authority
