# Test Suite Unification Plan - arifOS v47.0.0

**Date:** 2026-01-16
**Authority:** Constitutional Kernel Architecture Alignment
**Status:** 🔴 CRITICAL - 51% of tests use legacy import paths

---

## Executive Summary

The arifOS test suite contains **210+ test files with 2000+ test cases** providing comprehensive coverage of the constitutional system. However, the test architecture predates the **kernel unification** completed in v47.0.0, resulting in:

- **51% of tests (108 files)** import from legacy paths
- **19% of tests (40 files)** are duplicates
- **10+ FAG tests** are completely broken (import non-existent paths)
- **0 tests** cover the new unified kernel (`arifos_core.kernel.*`)

**Goal:** Align all tests with the new kernel architecture while maintaining 100% constitutional coverage.

---

## Critical Issues Summary

### 🔴 **SEVERITY: CRITICAL** (Blocks kernel adoption)

| Issue | Affected Files | Impact |
|-------|---------------|--------|
| FAG tests import from non-existent `arifos_core.apex.governance.fag` | 10+ files | All FAG tests fail |
| No tests for new kernel (`arifos_core.kernel.constitutional`) | 0 files | Zero kernel coverage |
| Dual pipeline architecture (old + new) | 8 files | Import fragmentation |
| APEX Prime fragmentation | 12 files | Verdict path confusion |

### 🟡 **SEVERITY: HIGH** (Technical debt)

| Issue | Affected Files | Impact |
|-------|---------------|--------|
| Duplicate tests (root + subdirectory) | 40 files | Maintenance overhead |
| Legacy version tests (v37, v39) | 6 files | Outdated patterns |
| Governance tests use legacy paths | 6 files | Import misalignment |
| Enforcement tests scattered | 15 files | No consolidation |

### 🟢 **SEVERITY: MEDIUM** (Cleanup)

| Issue | Affected Files | Impact |
|-------|---------------|--------|
| Hardcoded paths in tests | 12 files | Brittle tests |
| Missing mocks for external services | 8 files | Flaky tests |
| Conditional imports (try/except) | 5 files | Fragile logic |

---

## Test Architecture Alignment

### **Current State** (Pre-Unification)

```
tests/
├── test_*.py (110+ files)  ← SCATTERED, mixed patterns
├── core/                    ← Constitutional floors
├── mcp/                     ← Pipeline stages (good organization)
├── trinity/                 ← Trinity governance (duplicates)
├── memory/                  ← Memory system (good organization)
├── enforcement/             ← Floor enforcement (scattered)
├── governance/              ← Governance (legacy imports)
└── integration/             ← Cross-component (mixed imports)
```

**Import Pattern:**
```python
# Legacy (pre-kernel)
from arifos_core.system.apex_prime import apex_review
from arifos_core.apex.governance.fag import FAG  # BROKEN
from arifos_core.system.pipeline import Pipeline  # DEPRECATED

# New (kernel)
from arifos_core.agi.delta_kernel import DeltaKernel  # ✅
from arifos_core.asi.omega_kernel import OmegaKernel  # ✅
from arifos_core.apex.psi_kernel import PsiKernel    # ✅
from arifos_core.kernel.constitutional import ConstitutionalKernel  # MISSING TESTS
```

### **Target State** (Post-Unification)

```
tests/
├── kernel/                  ← NEW - Unified kernel tests
│   ├── test_constitutional_kernel.py
│   ├── test_trinity_kernel.py
│   ├── test_metrics_kernel.py
│   ├── test_apex_kernel.py
│   ├── test_memory_kernel.py
│   ├── test_search_kernel.py
│   ├── test_fag_kernel.py
│   ├── test_executor_kernel.py
│   ├── test_hypervisor_kernel.py
│   ├── test_integration_kernel.py
│   ├── test_config_kernel.py
│   └── test_utils_kernel.py
│
├── trinity/                 ← Trinity tests (AGI/ASI/APEX)
│   ├── test_delta_kernel.py        ✅ EXISTS
│   ├── test_omega_kernel.py        ✅ EXISTS
│   ├── test_psi_kernel.py          ✅ EXISTS
│   ├── test_trinity_orchestration.py
│   └── test_trinity_isolation.py
│
├── floors/                  ← Constitutional floors (F1-F12)
│   ├── test_f1_amanah.py
│   ├── test_f2_truth.py
│   ├── test_f3_triwitness_peace.py
│   ├── test_f4_clarity_empathy.py
│   ├── test_f5_humility.py
│   ├── test_f6_amanah_integrity.py
│   ├── test_f7_rasa.py
│   ├── test_f8_triwitness.py
│   ├── test_f9_antihantu.py
│   ├── test_f10_ontology.py
│   ├── test_f11_commandauth.py
│   └── test_f12_injection.py
│
├── pipeline/                ← Pipeline stages (000-999)
│   ├── test_000_void.py
│   ├── test_111_sense.py
│   ├── test_222_reflect.py
│   ├── test_333_atlas.py
│   ├── test_444_align.py
│   ├── test_555_empathize.py
│   ├── test_666_bridge.py
│   ├── test_777_eureka.py
│   ├── test_888_judge.py
│   └── test_999_seal.py
│
├── mcp/                     ← MCP integration
│   ├── test_unified_server.py
│   ├── test_mcp_tools.py
│   └── test_mcp_kernel_bridge.py
│
├── memory/                  ← Memory system (6-band)
│   ├── test_cooling_ledger.py
│   ├── test_vault999.py
│   ├── test_phoenix72.py
│   ├── test_memory_bands.py
│   └── test_memory_routing.py
│
├── fag/                     ← Full Autonomy Governance
│   ├── test_fag_core.py
│   ├── test_fag_safety.py
│   ├── test_fag_statistics.py
│   └── test_fag_mcp_integration.py
│
├── integration/             ← Cross-component integration
│   ├── test_kernel_mcp_integration.py
│   ├── test_trinity_memory_integration.py
│   ├── test_pipeline_floor_integration.py
│   └── test_end_to_end.py
│
└── _archive/                ← Archived legacy tests
    ├── v37/
    ├── v39/
    └── pre_kernel_unification/
```

**Import Pattern:**
```python
# Primary: Unified Kernel
from arifos_core.kernel.constitutional import ConstitutionalKernel, ConstitutionalVerdict
from arifos_core.kernel.mcp_server import UnifiedMCPServer

# Secondary: Trinity Kernels
from arifos_core.agi.delta_kernel import DeltaKernel
from arifos_core.asi.omega_kernel import OmegaKernel
from arifos_core.apex.psi_kernel import PsiKernel

# Tertiary: Specialized Modules
from arifos_core.memory.ledger.cooling_ledger import CoolingLedger
from arifos_core.enforcement.metrics import Metrics
from arifos_core.mcp.unified_server import UnifiedServer
```

---

## Migration Strategy

### **Phase 1: Critical Path (Week 1)** 🔴

**Goal:** Establish kernel test coverage and fix broken tests

#### 1.1 Create Kernel Test Suite
- [ ] `tests/kernel/test_constitutional_kernel.py` - Core pipeline execution
- [ ] `tests/kernel/test_trinity_kernel.py` - AGI·ASI·APEX coordination
- [ ] `tests/kernel/test_apex_kernel.py` - APEX Prime integration
- [ ] `tests/kernel/test_memory_kernel.py` - Memory band routing
- [ ] `tests/kernel/test_fag_kernel.py` - FAG kernel integration

**Priority:** CRITICAL - Zero kernel coverage currently

#### 1.2 Fix Broken FAG Tests
- [ ] Update imports from `arifos_core.apex.governance.fag` to `arifos_core.kernel.fag`
- [ ] Verify FAG kernel exists in new architecture
- [ ] Update 10+ FAG test files

**Files:**
- `test_fag.py`
- `test_fag_hardening.py`
- `test_fag_statistics_audit.py`
- `test_fag_v4503_hardening.py`
- `test_fag_write.py`
- `trinity/test_fag*.py` (5 files)

#### 1.3 Fix APEX Prime Fragmentation
- [ ] Consolidate tests to use `arifos_core.apex.psi_kernel.PsiKernel`
- [ ] OR confirm `arifos_core.system.apex_prime` is canonical path
- [ ] Update 12+ APEX test files

**Files:**
- `core/test_apex_prime_floors.py`
- `core/test_apex_prime_floors_mocked.py`
- `core/test_apex_genius_verdicts.py`
- `test_apex_measurements_eval.py`
- `test_apex_and_ledger_edges.py`

### **Phase 2: Pipeline Alignment (Week 2)** 🟡

**Goal:** Consolidate pipeline tests to use unified kernel

#### 2.1 Update Pipeline Tests
- [ ] Migrate from `arifos_core.system.pipeline` to `arifos_core.kernel.constitutional`
- [ ] Consolidate dual architecture tests
- [ ] Update 8+ pipeline test files

**Files:**
- `test_pipeline.py`
- `test_pipeline_stages_444_555_666.py`
- `test_pipeline_routing.py`
- `test_pipeline_waw_integration.py`

#### 2.2 Update Stage Tests
- [ ] Verify all stage tests import from `arifos_core.mcp.tools.mcp_NNN_*`
- [ ] Add missing stages (333 ATLAS if missing)
- [ ] Ensure stage tests cover kernel integration

**Files:**
- `mcp/test_mcp_000_reset.py` through `mcp/test_mcp_999_seal.py`

### **Phase 3: Floor Consolidation (Week 2-3)** 🟡

**Goal:** Organize floor tests by floor number, not scattered

#### 3.1 Reorganize Floor Tests
- [ ] Move all floor tests to `tests/floors/`
- [ ] One file per floor: `test_f1_amanah.py` through `test_f12_injection.py`
- [ ] Consolidate duplicate floor tests

**Files:**
- F1-F2: `test_delta_kernel.py`, `test_law_truth_threshold_enforcement.py`, `test_amanah_detector.py`
- F3-F7: `test_omega_kernel.py`, `test_law_f3_f6_threshold_enforcement.py`, `test_anti_hantu_f9.py`
- F9: `test_antihantu_unit.py`, `enforcement/test_f9_negation_aware_v1.py`
- F10-F12: `test_f10_ontology.py`, `test_f11_nonce_auth.py`, `test_f12_injection.py`

#### 3.2 Update Floor Import Paths
- [ ] AGI floors use `arifos_core.agi.floor_checks`
- [ ] ASI floors use `arifos_core.asi.floor_checks`
- [ ] APEX floors use `arifos_core.apex.floor_checks`
- [ ] Hypervisor floors use `arifos_core.hypervisor.*`

### **Phase 4: Cleanup & Archive (Week 3)** 🟢

**Goal:** Remove duplicates and archive legacy tests

#### 4.1 Remove Duplicates
- [ ] Identify 40+ duplicate test files (root + subdirectory)
- [ ] Keep subdirectory version, delete root version
- [ ] Update CI/CD to use subdirectory tests only

**Pattern:**
```
KEEP:   tests/trinity/test_trinity.py
DELETE: tests/test_trinity.py
```

#### 4.2 Archive Legacy Tests
- [ ] Move v37 tests to `tests/_archive/v37/`
- [ ] Move v39 tests to `tests/_archive/v39/`
- [ ] Move pre-kernel tests to `tests/_archive/pre_kernel_unification/`
- [ ] Add README.md to archive explaining historical context

**Files:**
- `test_memory_enforcement_v37.py`
- `test_memory_stack_v37.py`
- `test_spec_v44_*.py` (if v44 is archived)

### **Phase 5: Integration & Validation (Week 4)** 🟢

**Goal:** Full kernel integration testing and CI validation

#### 5.1 Create Integration Tests
- [ ] `tests/integration/test_kernel_mcp_integration.py`
- [ ] `tests/integration/test_trinity_memory_integration.py`
- [ ] `tests/integration/test_pipeline_floor_integration.py`
- [ ] `tests/integration/test_end_to_end_kernel.py`

#### 5.2 Update CI/CD
- [ ] Update pytest configuration to use new test structure
- [ ] Add kernel test coverage requirements (minimum 80%)
- [ ] Add import linting to prevent legacy path usage
- [ ] Add test organization validation

#### 5.3 Documentation
- [ ] Create `tests/README.md` with new organization
- [ ] Update `CONTRIBUTING.md` with test writing guidelines
- [ ] Create test migration guide for contributors
- [ ] Document kernel test patterns

---

## Import Path Migration Matrix

### **FAG (Full Autonomy Governance)**

| Old (Broken) | New (Kernel) | Status |
|--------------|--------------|--------|
| `arifos_core.apex.governance.fag` | `arifos_core.kernel.fag` OR `arifos_core.mcp.tools.fag_*` | 🔴 VERIFY PATH |

### **APEX Prime (Verdict Authority)**

| Old | New | Status |
|-----|-----|--------|
| `arifos_core.system.apex_prime` | `arifos_core.apex.psi_kernel` | 🟡 CONFIRM CANONICAL |

### **Pipeline Execution**

| Old | New | Status |
|-----|-----|--------|
| `arifos_core.system.pipeline` | `arifos_core.kernel.constitutional` | ✅ MIGRATE |

### **Trinity Kernels**

| Old | New | Status |
|-----|-----|--------|
| N/A (new in v47) | `arifos_core.agi.delta_kernel` | ✅ CORRECT |
| N/A (new in v47) | `arifos_core.asi.omega_kernel` | ✅ CORRECT |
| N/A (new in v47) | `arifos_core.apex.psi_kernel` | ✅ CORRECT |

### **Governance & Cryptography**

| Old | New | Status |
|-----|-----|--------|
| `arifos_core.apex.governance.merkle_ledger` | `arifos_core.memory.ledger.merkle_ledger` OR keep as-is | 🟡 VERIFY |
| `arifos_core.apex.governance.proof_of_governance` | `arifos_core.apex.governance.proof_of_governance` | ✅ KEEP |
| `arifos_core.apex.governance.ledger_cryptography` | `arifos_core.memory.ledger.cryptography` | 🟡 VERIFY |

### **Memory System**

| Old | New | Status |
|-----|-----|--------|
| `arifos_core.memory.*` | `arifos_core.memory.*` (no change) | ✅ CORRECT |
| `arifos_core.memory.ledger.cooling_ledger` | `arifos_core.memory.ledger.cooling_ledger` | ✅ CORRECT |

### **Enforcement**

| Old | New | Status |
|-----|-----|--------|
| `arifos_core.enforcement.metrics` | `arifos_core.enforcement.metrics` | ✅ CORRECT |
| `arifos_core.enforcement.genius_metrics` | `arifos_core.enforcement.genius_metrics` | ✅ CORRECT |

---

## Test Coverage Requirements

### **Kernel Coverage (NEW)**

- [ ] **Constitutional Kernel** - 90% line coverage
  - Pipeline execution (000→999)
  - Context propagation between stages
  - Early termination on hard failures
  - Verdict rendering
  - Ledger integration

- [ ] **Trinity Kernel** - 85% line coverage
  - AGI·ASI·APEX coordination
  - Orthogonal execution
  - Cross-kernel data flow
  - Isolation enforcement

- [ ] **APEX Kernel** - 95% line coverage (CRITICAL)
  - Verdict rendering (SEAL/VOID/PARTIAL/888_HOLD/SABAR)
  - Floor aggregation
  - GENIUS metrics
  - Verdict hierarchy enforcement

- [ ] **Memory Kernel** - 85% line coverage
  - 6-band routing (VAULT/LEDGER/ACTIVE/PHOENIX/WITNESS/VOID)
  - Verdict-based band selection
  - Cryptographic sealing
  - Merkle proof generation

- [ ] **FAG Kernel** - 80% line coverage
  - Autonomous governance
  - Budget tracking
  - Safety constraints
  - Human-in-the-loop triggers

### **Floor Coverage (EXISTING - MAINTAIN)**

- [ ] **F1-F12 Floors** - 95% coverage for each floor
  - Threshold validation
  - Edge cases (boundary conditions)
  - Failure modes
  - Integration with APEX verdict

### **Pipeline Coverage (EXISTING - MIGRATE)**

- [ ] **Stages 000-999** - 90% coverage for each stage
  - Stage execution logic
  - Context updates
  - Metric generation
  - Error handling

### **Integration Coverage (NEW)**

- [ ] **Kernel ↔ MCP** - 80% coverage
- [ ] **Kernel ↔ Memory** - 85% coverage
- [ ] **Kernel ↔ Trinity** - 85% coverage
- [ ] **End-to-End** - 75% coverage (full pipeline flows)

---

## Validation Checklist

### **Before Migration**
- [ ] Backup current test suite
- [ ] Document all test failures (baseline)
- [ ] Create test migration branch
- [ ] Set up test coverage tracking

### **During Migration**
- [ ] Run tests after each phase completion
- [ ] Track coverage delta (before/after)
- [ ] Document breaking changes
- [ ] Update fixtures and conftest.py as needed

### **After Migration**
- [ ] Achieve minimum 85% kernel coverage
- [ ] Zero broken imports
- [ ] All duplicate tests removed
- [ ] Legacy tests archived with documentation
- [ ] CI/CD passing with new structure
- [ ] Test README.md complete
- [ ] Migration guide published

---

## Risk Mitigation

### **Risk 1: Breaking Existing Tests**
- **Mitigation**: Create migration branch, run tests in parallel with legacy
- **Rollback**: Keep legacy tests in `_archive/` for reference

### **Risk 2: Import Path Uncertainty**
- **Mitigation**: Verify kernel paths exist before updating tests
- **Validation**: Create import validation script

### **Risk 3: Coverage Regression**
- **Mitigation**: Track coverage delta per phase
- **Requirement**: No phase completes with <80% coverage

### **Risk 4: FAG Path Confusion**
- **Mitigation**: Investigate `arifos_core.apex.governance.fag` vs `arifos_core.kernel.fag`
- **Decision Point**: Confirm canonical FAG location BEFORE Phase 1.2

---

## Success Metrics

### **Quantitative**
- [ ] **0 broken imports** (currently ~108 files)
- [ ] **0 duplicate tests** (currently ~40 files)
- [ ] **≥85% kernel coverage** (currently 0%)
- [ ] **≥95% APEX coverage** (CRITICAL)
- [ ] **≤5% test suite runtime increase**

### **Qualitative**
- [ ] Clean test organization (subdirectories by component)
- [ ] Consistent import patterns (kernel-first)
- [ ] Comprehensive documentation (README, migration guide)
- [ ] CI/CD stability (zero flaky tests)
- [ ] Contributor confidence (clear test writing guidelines)

---

## Timeline

| Phase | Duration | Dependencies | Milestone |
|-------|----------|--------------|-----------|
| **Phase 1: Critical Path** | Week 1 (Jan 16-22) | Kernel paths verified | Kernel tests exist, FAG tests fixed |
| **Phase 2: Pipeline Alignment** | Week 2 (Jan 23-29) | Phase 1 complete | Pipeline uses kernel imports |
| **Phase 3: Floor Consolidation** | Week 2-3 (Jan 23-Feb 5) | Phase 1 complete | Floor tests organized |
| **Phase 4: Cleanup & Archive** | Week 3 (Jan 30-Feb 5) | Phase 2-3 complete | Duplicates removed, legacy archived |
| **Phase 5: Integration & Validation** | Week 4 (Feb 6-12) | Phase 1-4 complete | CI passing, docs complete |

**Total Duration:** 4 weeks (Jan 16 - Feb 12, 2026)

---

## Next Actions (Immediate)

### **Today (Jan 16, 2026):**
1. ✅ Complete test inventory analysis
2. ⏭️ Verify kernel import paths exist
3. ⏭️ Create `tests/kernel/` directory
4. ⏭️ Write `test_constitutional_kernel.py` (first kernel test)
5. ⏭️ Fix first FAG test as proof-of-concept

### **This Week:**
- Complete Phase 1.1 (kernel test suite)
- Complete Phase 1.2 (FAG test fixes)
- Begin Phase 1.3 (APEX Prime consolidation)

---

**DITEMPA BUKAN DIBERI** - Tests will be forged to match the unified kernel architecture, not left scattered across legacy paths.

**Version:** v47.0.0 Test Unification Plan
**Status:** 🔴 CRITICAL PRIORITY
**Last Updated:** 2026-01-16
