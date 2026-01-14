# Phase 444-999 Remaining Work - v47.1 Constitutional Cleanup

**Status:** Phase 444.1 Complete, Remaining Moves Planned  
**Date:** 2026-01-14  
**Blocker:** Spec validation mismatch preventing import testing

---

## Completed ✅

### Phase 444.1: State Extraction (ΔS -4.2)
- ✅ Removed 5 duplicate files from apex/governance/
- ✅ Created 72-hour deprecation shims
- ✅ Migration guide (MIGRATION_GUIDE_v47.1.md)
- ✅ Rollback procedure (ROLLBACK_PROCEDURE_v47.1.md)

---

## Remaining Work ⏳

### Critical: Move 5 - Test Suite Stabilization (ΔS -1.6)

**Blocker:** v46 schema validation too strict, preventing all imports

**Issue:** 
- Schema expects: `_status`, `arifos_version`, `spec_type`, `description`, `source`, `floors` (lowercase), `floor_categories`, `precedence_order`, `verdicts`, `vitality`, `meta`
- Actual spec has: `version`, `authority`, `locked`, `constitutional_floors` (different key!), `implementation`, `canonical_reference`

**Solutions:**

#### Option A: Update Spec to Match Schema (Recommended)
Update `L2_PROTOCOLS/v46/constitutional_floors.json` to match schema requirements:
- Rename `constitutional_floors` → `floors`
- Add missing fields: `_status`, `arifos_version`, `spec_type`, etc.
- Restructure floor definitions to match schema expectations

#### Option B: Relax Schema Validation
Modify `L2_PROTOCOLS/v46/schema/constitutional_floors.schema.json` to accept current format:
- Make extra fields optional
- Allow `constitutional_floors` as alias for `floors`
- Add backward compatibility mode

#### Option C: Fix Spec Loader
Modify `arifos_core/spec/schema_validator.py` or `arifos_core/enforcement/metrics.py`:
- Add compatibility layer to transform old format to new
- Map `constitutional_floors` → `floors`
- Inject missing required fields with defaults

**Recommended:** Option A (most constitutional - fix spec to match schema)

---

### Move 2: Hypervisor Elevation (ΔS -0.8)

**Files to Convert to Shims:**
```
arifos_core/guards/injection_guard.py
arifos_core/guards/nonce_manager.py
arifos_core/guards/ontology_guard.py
arifos_core/guards/session_dependency.py
```

**Shim Template:**
```python
"""
DEPRECATED: This module has moved to arifos_core.hypervisor.guards.[module]

Guards belong in the hypervisor layer (F10-F12 enforcement).
This shim will be removed in v47.2 (72 hours).

Update your imports:
  OLD: from arifos_core.guards.[module] import Class
  NEW: from arifos_core.hypervisor.guards.[module] import Class
"""
import warnings
warnings.warn(..., DeprecationWarning, stacklevel=2)
from arifos_core.hypervisor.guards.[module] import *
```

**Imports to Update:**
- `arifos_core/system/hypervisor.py`
- `arifos_core/integration/guards/`
- `arifos_core/mcp/*.py`
- Tests in `tests/test_hypervisor*.py`, `tests/test_f1[012]*.py`

**Test Command:**
```bash
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/test_hypervisor_integration.py tests/test_f10_*.py tests/test_f11_*.py tests/test_f12_*.py -v
```

---

### Move 3: Enforcement Consolidation (ΔS -2.1)

**Phase 1: Create Consolidated Modules**

#### Create `enforcement/validators.py`
Merge:
- `floor_detectors/amanah_risk_detectors.py` → Section "Amanah Risk Detection"
- `floor_detectors/search_governance.py` → Section "Search Governance"
- `validators/spec_checker.py` → Section "Spec Validation"
- `verification/distributed.py` → Section "Distributed Verification"

#### Create `enforcement/floor_checks.py`
Merge:
- `eval/agi.py` → Section "AGI Layer Evaluation"
- `eval/asi.py` → Section "ASI Layer Evaluation"
- `judiciary/semantic_firewall.py` → Section "Semantic Firewall"
- `judiciary/witness_council.py` → Section "Witness Council"
- `attestation/manifest.py` → Section "Manifest Attestation"

**Phase 2: Create Deprecation Shims**

Subdirectories to convert:
- `attestation/` → shim to `floor_checks`
- `eval/` → shim to `floor_checks`
- `floor_detectors/` → shim to `validators`
- `judiciary/` → shim to `floor_checks`
- `validators/` → shim to `validators`
- `verification/` → shim to `validators`

**Keep Unchanged:**
- `trinity/` (complex logic, keep separate)
- `routing/` (distinct concern)
- `stages/` (stage-specific overrides)
- `audit/` (eye adapter specific)
- `evidence/` (routing logic)

**Test Command:**
```bash
ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/enforcement/ -v
```

---

### Move 4: Governance Crystallization (ΔS -1.2)

**Already Complete!** The `apex/governance/__init__.py` already has:
- Imports from `arifos_core.state`
- `__getattr__` deprecation handler
- Proper exports

**Just Verify:**
```bash
ARIFOS_ALLOW_LEGACY_SPEC=1 python3 -c "from arifos_core.apex.governance import fag; print('✅ Governance imports work')"
```

---

## Phase 555-777: EMPATHIZE & FORGE

### Add Constitutional Docstrings

Example for moved files:
```python
"""
[Module Name] - [Purpose]

Constitutional Mapping:
- Pipeline Stage: [111-999 range]
- Floors Enforced: F[X], F[Y]
- Thermodynamic Role: [Cooling/Heating/Neutral]
- Layer: [AGI/ASI/APEX/Enforcement]

Related Theory: See L1_THEORY/canon/[XXX]_[name]/

History:
- v47.1: Moved from [old location] to [new location]
  Reason: [entropy reduction / layer alignment / etc]
"""
```

### Create Migration Tests

Create `tests/test_migration_v47_1.py`:
```python
import warnings

def test_state_shims_emit_warnings():
    """Verify apex.governance shims emit deprecation warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from arifos_core.apex.governance import ledger
        assert len(w) == 1
        assert "deprecated" in str(w[0].message).lower()

def test_state_new_imports_silent():
    """Verify state.* imports work silently."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from arifos_core.state import ledger
        assert len(w) == 0

def test_guards_shims_emit_warnings():
    """Verify guards shims emit deprecation warnings."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from arifos_core.guards.injection_guard import InjectionGuard
        assert len(w) == 1

def test_guards_new_imports_silent():
    """Verify hypervisor.guards imports work silently."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from arifos_core.hypervisor.guards.injection_guard import InjectionGuard
        assert len(w) == 0
```

---

## Phase 888: TEST

### Test Strategy

1. **Fix Spec Validation First** (Move 5)
   ```bash
   pytest tests/ --collect-only -q
   # Should show 0 errors
   ```

2. **Test Shims Work**
   ```bash
   ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/test_migration_v47_1.py -v
   ```

3. **Test Targeted Modules**
   ```bash
   ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/test_ledger*.py -v
   ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/test_hypervisor*.py -v
   ARIFOS_ALLOW_LEGACY_SPEC=1 pytest tests/enforcement/ -v
   ```

4. **Full Test Suite**
   ```bash
   # After Move 5 fixes spec validation:
   pytest tests/ -v --tb=short
   ```

5. **Verify Entropy Reduction**
   ```bash
   # Calculate final ΔS (should be ≤ 3.2)
   python scripts/calculate_entropy.py  # If exists
   # Or manually verify directory structure matches PROPOSED_STRUCTURE_v47.1.md
   ```

---

## Phase 999: SEAL

### Documentation Updates

#### 1. CHANGELOG.md
Add section:
```markdown
## [47.1.0] - 2026-01-14

### Changed - Constitutional Cleanup (ΔS 11.7 → 1.8)

**State Management:**
- MOVED: Ledger/merkle files from `apex/governance/` to `state/`
- DEPRECATED: `arifos_core.apex.governance.ledger*` (72h shim)
- USE: `arifos_core.state.ledger*`

**Guards:**
- MOVED: Guards from `guards/` to `hypervisor/guards/`
- DEPRECATED: `arifos_core.guards.*` (72h shim)
- USE: `arifos_core.hypervisor.guards.*`

**Enforcement:**
- CONSOLIDATED: 12 subdirs → 2 modules (validators.py, floor_checks.py)
- DEPRECATED: `enforcement.eval.*`, `enforcement.judiciary.*`, etc. (72h shims)
- USE: `enforcement.validators`, `enforcement.floor_checks`

**Governance:**
- CRYSTALLIZED: `apex/governance/` now pure governance (no state)

**Tests:**
- FIXED: v45→v46 spec validation (131 → 0 collection errors)

See MIGRATION_GUIDE_v47.1.md for complete migration instructions.
```

#### 2. README.md
Update import examples:
```python
# v47.1+ (New)
from arifos_core.state.ledger import AuditLedger
from arifos_core.hypervisor.guards.injection_guard import InjectionGuard
from arifos_core.enforcement.floor_checks import evaluate_agi_layer
```

#### 3. pyproject.toml
Update version and description:
```toml
[project]
name = "arifos-core"
version = "47.1.0"
description = "arifOS Constitutional AI Kernel - v47.1 Equilibrium Architecture (ΔS optimized)"
```

#### 4. AGENTS.md
Update any references to old import paths in agent examples.

#### 5. MCP Documentation
Update `arifos_mcp/README.md` and related docs with new import paths.

---

## Estimated Time Remaining

- Move 5 (Spec fix): 30-60 minutes
- Move 2 (Guards): 20 minutes
- Move 3 (Enforcement): 60-90 minutes (complex merge)
- Move 4 (Governance): 5 minutes (verify only)
- Phase 555-777 (Docstrings): 30 minutes
- Phase 888 (Testing): 30 minutes
- Phase 999 (Documentation): 30 minutes

**Total: ~4-5 hours**

---

## Priority Order

1. **HIGH**: Move 5 (Spec fix) - Unblocks all testing
2. **HIGH**: Move 2 (Guards) - Quick win, reduces entropy
3. **MEDIUM**: Move 3 (Enforcement) - Largest entropy reduction but complex
4. **LOW**: Move 4 (Governance) - Already done, just verify
5. **FINAL**: Phases 555-999 (Polish & Document)

---

## Success Criteria

- [ ] All 1305+ tests passing (zero regressions)
- [ ] ΔS ≤ 3.2 (target: 1.8)
- [ ] Zero ModuleNotFoundError
- [ ] All deprecation warnings documented
- [ ] Migration guide complete
- [ ] Rollback procedure tested
- [ ] CI pipeline green

---

**Status:** Phase 444.1 complete, awaiting Move 5 (spec fix) to unblock testing

**DITEMPA BUKAN DIBERI** — Systematic execution with safety first.
