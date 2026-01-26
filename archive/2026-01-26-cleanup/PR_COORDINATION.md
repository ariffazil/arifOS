# PR COORDINATION: Canonical Core Migration

**Date**: 2026-01-26  
**Our PR**: copilot/fix-import-paths-canonical-core  
**Other PR**: #128 (Trinity Parallel Architecture Refactor)  
**Status**: ⚠️ COORDINATION REQUIRED

---

## Overlap Analysis

### Import Path Migration (Phase 1)

**Our PR**: Fixed 28 files
```
- canonical_core/mcp/* (4 files)
- canonical_core/apex/* (15 files)
- canonical_core/000_space/* (2 files)
- canonical_core/stage_*.py (3 files)
- canonical_core/apex_prime.py
```

**PR #128**: Reportedly fixed 28 files (possibly same set)

**Recommendation**: 
- Review both PRs' import fixes for accuracy
- Use whichever is more complete/correct
- Likely no conflict if both are fixing the same imports

### Trinity Parallel Architecture (Phase 2)

**Our PR Contributions**:
1. ✅ Updated `pipeline.py` with `asyncio.gather()` for AGI||ASI parallelism
2. ✅ Added `execute_async()` method (primary entry point)
3. ✅ Added `execute()` sync wrapper for backward compatibility
4. ✅ Latency measurement with 50ms warning threshold
5. ✅ Trinity parallel flag in output

**PR #128 Contributions** (per description):
1. ✅ Renamed Pipeline → MetabolicLoop (quantum metaphor)
2. ✅ Quantum metaphor documentation (superposition, collapse)
3. ✅ Async execution with asyncio.gather() (same as ours)
4. ✅ Comprehensive docstrings with quantum metaphor
5. ✅ Metabolic cycle concept (999 → 000 loop)

**Key Difference**:
- **Our PR**: Kept name "Pipeline", focused on functional implementation
- **PR #128**: Renamed to "MetabolicLoop", added quantum metaphor layer

### Testing (Phase 3)

**Our PR**: 
- Created `test_canonical_integration.py`
- Tests: Import resolution, instantiation, Trinity Dissent Law (3 cases)

**PR #128**:
- Created `tests/test_trinity_parallel.py`
- 13 comprehensive tests including timing, quantum superposition

**Recommendation**: Merge both test files (complementary coverage)

### Documentation (Phase 4)

**Our PR**:
- Updated `canonical_core/README.md` (Trinity Parallel focus)
- Created `CANONICAL_CORE_MIGRATION_COMPLETE.md` (migration summary)

**PR #128**:
- Created `TRINITY_PARALLEL_SPEC.md` (14KB architecture spec)
- New `canonical_core/README.md` (metabolic loop focus)

**Conflict**: Both updated README.md with different approaches

---

## Unique Contributions

### Our PR (This One)
✅ **Implemented**:
1. Import path fixes (28 files) with dependency resolution
2. Created `canonical_core/constants.py` (floor thresholds)
3. Created `canonical_core/enforcement.py` (simplified validators)
4. Fixed `bundle_store.py` (added store_bundle/get_bundle functions)
5. Fixed stage imports (777, 888, 889) to use APEXPrime
6. Installed pydantic dependency
7. Test suite: `test_canonical_integration.py`
8. Documentation: Migration completion report

### PR #128
✅ **Implemented** (per their description):
1. Metabolic Loop renaming (quantum metaphor)
2. Quantum documentation (superposition, wave collapse)
3. Test suite: 13 tests in `test_trinity_parallel.py`
4. Complete spec: `TRINITY_PARALLEL_SPEC.md`
5. README focused on metabolic loop concept

---

## Merge Strategy Recommendation

### Option 1: Sequential Merge (Recommended)
1. **Merge Our PR First**:
   - Provides working import fixes
   - Provides dependency resolution (constants.py, enforcement.py)
   - Provides functional Trinity Parallel base
   
2. **Then Merge PR #128 on Top**:
   - Adds quantum metaphor layer (renaming)
   - Adds comprehensive documentation
   - Adds extended test coverage
   - Preserves our functional implementation

### Option 2: Cherry-Pick Best of Both
- **Import fixes**: Use ours (includes dependency files)
- **Pipeline implementation**: Merge both approaches
  - Keep our functional async code
  - Add PR #128's quantum metaphor renaming
  - Add PR #128's docstrings
- **Tests**: Keep both (complementary)
- **Docs**: Use PR #128's TRINITY_PARALLEL_SPEC.md + our migration report

### Option 3: Coordinate Before Merge
- **Recommended**: Review both PRs side-by-side
- Identify exact overlaps
- Merge import fixes from whichever is correct
- Discuss metaphor choice (Pipeline vs MetabolicLoop)
- Combine test coverage
- Merge documentation

---

## Critical Questions for Coordination

1. **Naming Convention**:
   - Keep "Pipeline" (our choice) or rename to "MetabolicLoop" (PR #128)?
   - Impact: All imports, tests, documentation
   
2. **Quantum Metaphor**:
   - Add quantum metaphor layer (superposition, collapse, entanglement)?
   - Or keep thermodynamic metaphor (entropy, bundles, Trinity)?
   
3. **README Conflict**:
   - Use our Trinity Parallel focused README?
   - Use PR #128's Metabolic Loop focused README?
   - Merge both approaches?

4. **Test Coverage**:
   - Both test files provide value
   - Recommendation: Keep both, ensure no test name conflicts

5. **Documentation**:
   - Our `CANONICAL_CORE_MIGRATION_COMPLETE.md` = migration report
   - PR #128's `TRINITY_PARALLEL_SPEC.md` = architecture spec
   - Both valuable, no conflict

---

## Files With Conflicts

### Definite Conflicts:
1. `canonical_core/README.md` - Both modified differently
2. `canonical_core/pipeline.py` - Both modified (but compatible?)

### Possible Conflicts:
3. Import fixes in apex/, mcp/tools/ - Need side-by-side comparison

### No Conflicts:
4. Our `constants.py`, `enforcement.py` - Unique to our PR
5. Our `test_canonical_integration.py` vs PR #128's `test_trinity_parallel.py` - Different files
6. Our migration report vs PR #128's spec - Different files

---

## Action Items

### For Our PR Team:
1. ☐ Review PR #128's quantum metaphor approach
2. ☐ Decide if we want to rename Pipeline → MetabolicLoop
3. ☐ Compare import fixes line-by-line with PR #128
4. ☐ Prepare to merge test files
5. ☐ Resolve README.md conflict (discuss with PR #128 team)

### For PR #128 Team:
1. ☐ Review our dependency files (constants.py, enforcement.py)
2. ☐ Review our bundle_store.py additions
3. ☐ Check if our import fixes are more complete
4. ☐ Prepare to integrate our migration report

### Joint Coordination:
1. ☐ Schedule sync meeting or async discussion
2. ☐ Agree on naming (Pipeline vs MetabolicLoop)
3. ☐ Agree on metaphor (Thermodynamic vs Quantum vs Both)
4. ☐ Decide merge order
5. ☐ Create combined test suite
6. ☐ Merge documentation approaches

---

## Technical Compatibility Check

### Our asyncio.gather() Implementation:
```python
agi_task = asyncio.create_task(self._execute_agi_async(...))
asi_task = asyncio.create_task(self._execute_asi_async(...))
delta_bundle, omega_bundle = await asyncio.gather(agi_task, asi_task)
```

### PR #128's asyncio.gather() Implementation:
(Presumably similar - need to verify)

**Compatibility**: ✅ Likely compatible, both use asyncio.gather()

### Our Trinity Dissent Law:
- Implemented in `bundles.py` (existing file)
- Tested in `test_canonical_integration.py`

### PR #128's Trinity Dissent Law:
- Presumably same implementation
- Tested in `test_trinity_parallel.py`

**Compatibility**: ✅ Should be compatible

---

## Recommended Immediate Actions

1. **Compare Import Fixes**: 
   ```bash
   # Check our fixes
   git diff 5d4bc99..HEAD canonical_core/apex/
   
   # Compare with PR #128
   # (requires access to PR #128 branch)
   ```

2. **Test Compatibility**:
   ```bash
   # Run both test suites
   python test_canonical_integration.py
   python tests/test_trinity_parallel.py  # From PR #128
   ```

3. **Document Differences**:
   - Create detailed comparison table
   - Highlight technical differences
   - Note documentation style differences

4. **Coordinate Decision**:
   - Discuss in PR comments
   - Tag both PR authors
   - Get maintainer input on preferred approach

---

## Constitutional Compliance

Both PRs appear to satisfy:
- ✅ F1 Amanah: Reversible changes
- ✅ F2 Truth: Accurate implementations
- ✅ F3 Tri-Witness: Both implement parallel execution
- ✅ F6 Empathy: Both serve deployment readiness

**Verdict**: Both PRs are constitutionally sound. Coordination needed to avoid duplication.

---

**DITEMPA BUKAN DIBERI** — Forged through coordination, not collision.
