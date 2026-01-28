# arifOS Test Archive

**Archived:** 2026-01-29  
**Reason:** Test suite cleanup - moved outdated/deprecated tests

---

## Directory Structure

```
tests/archive/
├── README.md                      # This file
├── TEST_AUDIT_2026-01-29.md       # Full audit report
├── ARCHIVE_OLD_FILE               # Original archive file (pre-cleanup)
├── v46_tests/                     # v45-v46 version tests
├── v52_tests/                     # v52 version tests
└── deprecated_features/           # Deprecated feature tests
```

---

## Contents

### v46_tests/ (2 files)
Tests for v45-v46 features that are now obsolete:
- `test_v46_enhancements.py` - v46.1 hardening enhancements
- `test_aaa_mcp_gaps.py` - v45.0.4 gap fixes (Gap 4, 5, 6)

### v52_tests/ (10 files)
Tests for v52 architecture that's been superseded by v53:
- `test_agi_imports_fixed.py` - v52.6.0 import fixes
- `test_agi_imports_summary.md` - Import fix documentation
- `test_agi_metrics.py` - Thermodynamic dashboard tests
- `test_agi_upgrades_complete.py` - AGI upgrade tests
- `test_architectures.py` - Legacy vs new architecture comparison
- `test_architectures_fixed.py` - Architecture comparison (fixed)
- `test_native_v53.py` - Native v53 tests (old implementation)
- `test_parallel_hypothesis.py` - Parallel hypothesis matrix
- `test_trinity_hat.py` - Trinity HAT loop tests
- `test_trinity_parallel.py` - Trinity parallel tests

### deprecated_features/ (31 files)
Tests for features that no longer exist:

**Old Kernel Tests:**
- `test_delta_kernel.py` - Old AGI delta kernel
- `test_omega_kernel.py` - Old ASI omega kernel
- `test_psi_kernel.py` - Old APEX psi kernel
- `test_asi_engine.py` - Old ASI engine

**Old Guard Tests:**
- `test_f10_ontology.py` - Old ontology guard
- `test_f11_nonce_auth.py` - Old nonce manager
- `test_f12_injection.py` - Old injection guard
- `test_amanah_detector.py` - Old amanah detection
- `test_antihantu_unit.py` - Old anti-hantu view
- `test_session_dependency_guard.py` - Old session guard

**Old Memory/Ledger Tests:**
- `test_cooling_ledger.py` - Old cooling ledger
- `test_cooling_ledger_integrity.py` - Old ledger integrity
- `test_cooling_ledger_kms_integration.py` - Old KMS integration
- `test_memory_phase1_invariants.py` - Old memory phase 1
- `test_memory_phase1_routing.py` - Old memory routing
- `test_ledger_cryptography.py` - Old ledger crypto
- `test_kms_signer.py` - Old KMS signer
- `test_time_immutability.py` - Old time policy
- `test_sabar_partial_separation.py` - Old memory bands

**Old System Tests:**
- `test_dream_forge.py` - Old Dream Forge system
- `test_entropy.py` - Old entropy implementation
- `test_atlas_lanes.py` - Old ATLAS lanes
- `test_budi_quick.py` - Old BUDI metrics
- `test_ignition_profiles.py` - Old ignition system
- `test_vector_adapter.py` - Old L7 vector adapter
- `stress_tearframe_physics.py` - Old pipeline stress test
- `test_mcp_utils.py` - Old MCP utils server

**Old FAG Tests (File Access Guard):**
- `test_fag.py`
- `test_fag_hardening.py`
- `test_fag_statistics_audit.py`
- `test_fag_v4503_hardening.py`

**Other:**
- `test_apex_and_ledger_edges.py` - All tests commented out
- `test_grey_zone.py` - Old grey zone detection
- `test_refusal_accountability.py` - Old refusal system

---

## Active Tests (Remaining in tests/)

These tests are still current and use the `codebase` architecture:

```
tests/
├── conftest.py                    # pytest fixtures
├── utils.py                       # Test utilities
├── safe_chatbot_demo.py           # Demo script
├── constitutional/                # Constitutional compliance tests
├── core/                          # Core engine tests
├── enforcement/                   # Floor enforcement tests
├── evidence/                      # Evidence system tests
├── governance/                    # Governance tests
├── integration/                   # Integration tests
├── k6/                            # Load tests
├── logs/                          # Test logs
├── mcp/                           # MCP server tests
├── memory/                        # Memory system tests
├── runtime/                       # Runtime tests
└── test_integration/              # More integration tests
```

---

## Recovery

To restore an archived test:

```bash
mv tests/archive/v52_tests/test_architectures.py tests/
```

**Note:** Most archived tests use legacy `arifos` imports that will need to be updated to `codebase` imports to work with the current architecture.

---

## Migration Guide

If you need to update an archived test to work with v53:

### Import Path Changes

```python
# OLD (v52 and earlier)
from arifos.core.guards.injection_guard import InjectionGuard
from arifos.core.agi.delta_kernel import DeltaKernel
from arifos.mcp.bridge import bridge_agi_action_router

# NEW (v53)
from codebase.guards.injection_guard import InjectionGuard
from codebase.engines.agi.kernel import AGINeuralCore
from codebase.mcp.bridge import bridge_agi_router
```

### Key Architecture Changes

| Old (v52) | New (v53) |
|-----------|-----------|
| `arifos.core.agi.delta_kernel` | `codebase.engines.agi.kernel` |
| `arifos.core.asi.omega_kernel` | `codebase.engines.asi.kernel` |
| `arifos.core.apex.psi_kernel` | `codebase.engines.apex.kernel` |
| `arifos.core.guards.*` | `codebase.guards.*` |
| `arifos.mcp.bridge` | `codebase.mcp.bridge` |
| `arifos.core.memory.ledger` | `codebase.vault.*` |

---

*DITEMPA BUKAN DIBERI*
