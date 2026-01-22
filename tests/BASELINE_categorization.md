# Test Categorization Baseline (v49.1.0)

**Date:** 2026-01-20
**Total Tests:** 139 files
**Framework:** CORE/SEED/UPDATE/ARCHIVE/FORGE

---

## CATEGORY 1: CORE (Iman - Essential Invariants)

**Definition:** Tests that validate the 13 immutable constitutional floors.

| Test File | Floors Covered | Status |
|-----------|----------------|--------|
| `tests/core/test_apex_prime_floors.py` | F1-F9 | ✅ CORE |
| `tests/core/test_law_truth_threshold_enforcement.py` | F2 | ✅ CORE |
| `tests/core/test_law_f3_f6_threshold_enforcement.py` | F3, F6 | ✅ CORE |
| `tests/test_f10_ontology.py` | F10 | ✅ CORE |
| `tests/test_f11_nonce_auth.py` | F11 | ✅ CORE |
| `tests/test_f12_injection.py` | F12 | ✅ CORE |
| `tests/enforcement/test_f4_zlib_clarity.py` | F4 | ✅ CORE |
| `tests/enforcement/test_f6_empathy_split.py` | F6 | ✅ CORE |
| `tests/enforcement/test_f9_negation_aware_v1.py` | F9 | ✅ CORE |
| `tests/test_anti_hantu_f9.py` | F9 | ✅ CORE |

**CORE Subtotal:** 10 files → **CONSOLIDATE into test_01_core_F1_to_F13.py**

---

## CATEGORY 2: SEED (Essential Infrastructure - Keep & Enhance)

**Definition:** Functional infrastructure tests that seed the operational depth.

### W@W Federation (7 files)
| Test File | Coverage | Status |
|-----------|----------|--------|
| `tests/waw/test_waw_organs.py` | W@W organ validation | 🌱 SEED |
| `tests/waw/test_waw_apex_escalation.py` | APEX escalation | 🌱 SEED |
| `tests/waw/test_waw_geox_signals.py` | GeoX signals | 🌱 SEED |
| `tests/waw/test_waw_prompt_signals.py` | Prompt signals | 🌱 SEED |
| `tests/waw/test_waw_rif_signals.py` | RIF signals | 🌱 SEED |
| `tests/waw/test_waw_wealth_signals.py` | Wealth signals | 🌱 SEED |
| `tests/waw/test_waw_well_signals.py` | Wellness signals | 🌱 SEED |

**Action:** Consolidate into `test_08_WAW_federation.py`

### Engine Kernels (3 files)
| Test File | Coverage | Status |
|-----------|----------|--------|
| `tests/test_delta_kernel.py` | AGI (Δ) kernel | 🌱 SEED |
| `tests/test_omega_kernel.py` | ASI (Ω) kernel | 🌱 SEED |
| `tests/test_psi_kernel.py` | APEX (Ψ) kernel | 🌱 SEED |

**Action:** Consolidate into `test_02_TRINITY_live_flow.py`

### Trinity Integration (3 files)
| Test File | Coverage | Status |
|-----------|----------|--------|
| `tests/trinity/test_trinity_core.py` | Trinity loop | 🌱 SEED |
| `tests/test_orthogonal_bundles.py` | AGI ⊥ ASI orthogonality | 🌱 SEED |
| `tests/test_engines_arif_adam.py` | ARIF (AGI) + ADAM (ASI) | 🌱 SEED |

**Action:** Consolidate into `test_02_TRINITY_live_flow.py`

### Pipeline Stages (20 files)
| Test File | Coverage | Status |
|-----------|----------|--------|
| `tests/test_stage_000_void.py` | 000 VOID | 🌱 SEED |
| `tests/test_stage_111_sense.py` | 111 SENSE | 🌱 SEED |
| `tests/test_mcp_000_reset.py` | MCP 000 | 🌱 SEED |
| `tests/test_mcp_111_sense.py` | MCP 111 | 🌱 SEED |
| `tests/test_mcp_222_reflect.py` | MCP 222 | 🌱 SEED |
| `tests/test_mcp_444_evidence.py` | MCP 444 | 🌱 SEED |
| `tests/test_mcp_555_empathize.py` | MCP 555 | 🌱 SEED |
| `tests/test_mcp_666_align.py` | MCP 666 | 🌱 SEED |
| `tests/test_mcp_777_forge.py` | MCP 777 | 🌱 SEED |
| `tests/test_mcp_888_judge.py` | MCP 888 | 🌱 SEED |
| `tests/test_mcp_889_proof.py` | MCP 889 | 🌱 SEED |
| `tests/test_mcp_999_seal.py` | MCP 999 | 🌱 SEED |
| (+ 8 more pipeline-related tests) | Various stages | 🌱 SEED |

**Action:** Consolidate into `test_03_pipeline_000_to_999.py`

### Memory/Ledger (18 files)
| Test File | Coverage | Status |
|-----------|----------|--------|
| `tests/test_cooling_ledger_integrity.py` | Ledger integrity | 🌱 SEED |
| `tests/test_ledger_cryptography.py` | zkPC + Merkle | 🌱 SEED |
| `tests/test_phoenix72.py` | Phoenix-72 basic | 🌱 SEED |
| `tests/memory/test_cooling_ledger.py` | Cooling ledger | 🌱 SEED |
| (+ 14 more memory-related tests) | Memory bands | 🌱 SEED |

**Action:** Consolidate into `test_04_VAULT_ledger_integrity.py`

**SEED Subtotal:** ~50 files → **CONSOLIDATE into tests 02-04, 08**

---

## CATEGORY 3: UPDATE (Needs v50 Alignment)

**Definition:** Tests with entropy rot - outdated imports, legacy paths.

| Test File | Issue | Action Required |
|-----------|-------|-----------------|
| `tests/legacy/*` | Uses `arifos_core` imports | ✏️ UPDATE: `arifos_core.X` → `arifos.X` |
| `tests/test_sovereignty_all_providers.py` | Multi-model orchestration | ✏️ UPDATE: Add v50 orchestration |
| `tests/test_session_physics.py` | v44 shims | ✏️ UPDATE: Remove legacy shims |
| `tests/test_memory_stack_v37.py` | v37 memory stack | ⚠️ Consider archiving |

**UPDATE Subtotal:** ~15 files → **FIX imports, remove shims**

---

## CATEGORY 4: ARCHIVE (Obsolete - Move to archive_local/)

**Definition:** Redundant, version-tagged, or unmaintained tests.

### Version-Tagged (19 files)
| Test File | Version | Reason |
|-----------|---------|--------|
| `tests/test_v39_ci_guardrails.py` | v39 | ❌ ARCHIVE: Obsolete version |
| `tests/test_v45_patch_b1_fixes.py` | v45 | ❌ ARCHIVE: Patch-specific |
| `tests/test_v46_enhancements.py` | v46 | ❌ ARCHIVE: Version-specific |
| `tests/test_memory_enforcement_v37.py` | v37 | ❌ ARCHIVE: Legacy memory |
| `tests/test_memory_stack_v37.py` | v37 | ❌ ARCHIVE: Legacy stack |
| `tests/test_spec_v44_*.py` (4 files) | v44 | ❌ ARCHIVE: Spec version |
| (+ 10 more version-tagged tests) | Various | ❌ ARCHIVE |

### Duplicates (12 files)
| Test File (Root) | Duplicate Location | Reason |
|------------------|-------------------|--------|
| `tests/test_apex_genius_verdicts.py` | `tests/core/test_apex_genius_verdicts.py` | ❌ ARCHIVE: Keep core/ version |
| `tests/test_cooling_ledger.py` | `tests/memory/test_cooling_ledger.py` | ❌ ARCHIVE: Keep memory/ version |
| `tests/test_trinity.py` | `tests/trinity/test_trinity.py` | ❌ ARCHIVE: Keep trinity/ version |

### Mocked Redundancy (8 files)
| Test File | Reason |
|-----------|--------|
| `tests/test_apex_prime_floors_mocked.py` | ❌ ARCHIVE: Mocked variant (keep real) |
| `tests/test_cooling_ledger_integrity_mocked.py` | ❌ ARCHIVE: Mocked variant |
| (+ 6 more mocked tests) | ❌ ARCHIVE |

### Unmaintained (5 files)
| Test File | Reason |
|-----------|--------|
| `tests/test_budi_quick.py` | ❌ ARCHIVE: Personal test |
| `tests/safe_chatbot_demo.py` | ❌ ARCHIVE: Demo (not test) |
| `tests/test_grey_zone.py` | ⚠️ REVIEW: Ambiguous floor edge cases |

**ARCHIVE Subtotal:** ~44 files → **MOVE to archive_local/**

---

## CATEGORY 5: FORGE (v50 New Capabilities)

**Definition:** New tests for v50 clipboard and orchestration.

| Test File | Purpose | Status |
|-----------|---------|--------|
| `tests/test_01_core_F1_to_F13.py` | 13 floors CORE | ✅ FORGED (820 lines) |
| `tests/test_internal_state_clipboard.py` | L4.5 clipboard | 🔨 FORGE (pending) |
| `tests/test_v50_orchestrator.py` | Multi-model parallel | 🔨 FORGE (pending) |

**FORGE Subtotal:** 3 files (1 complete, 2 pending)

---

## SUMMARY STATISTICS

| Category | Files | Action | Timeline |
|----------|-------|--------|----------|
| **CORE** | 10 | ✅ Consolidate → test_01 | Done |
| **SEED** | 50 | 🌱 Extract → tests 02-08 | 3 days |
| **UPDATE** | 15 | ✏️ Fix imports/shims | 1 day |
| **ARCHIVE** | 44 | ❌ Move to archive_local/ | 2 hours |
| **FORGE** | 3 | 🔨 Create new (2 pending) | 2 days |
| **Keep As-Is** | 20 | ✅ No changes needed | - |
| **TOTAL** | 139 | → 28 files (after consolidation) | 7 days |

---

## ENTROPY CALCULATION

**Before (v49.0):**
- 139 test files
- 10 subdirectories
- Scattered floor tests (19 locations)
- Entropy: S_before = 139 files × log(139) ≈ **687 bits**

**After (v50.0):**
- 28 test files (constitutional + specialized)
- 2 directories (constitutional/ + archive_local/)
- Unified floor tests (1 location)
- Entropy: S_after = 28 files × log(28) ≈ **135 bits**

**Entropy Reduction:**
- ΔS = S_after - S_before = 135 - 687 = **-552 bits**
- Reduction: **80.4%** (F4 Clarity validated ✅)

---

**DITEMPA BUKAN DIBERI** — Baseline categorization establishes measurement foundation for constitutional consolidation.
