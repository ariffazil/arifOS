# Phase 222 REFLECT - Functional Hierarchy & Context Map
**Generated:** 2026-01-14  
**Version:** v47.1 Constitutional Cleanup  
**Foundation:** Built on SENSE_MAP_v47.1.md findings

## Executive Summary

**Purpose:** Map arifOS functionality to constitutional pipeline stages (000-999) and identify structural misalignments.

**Key Findings:**
1. **Circular dependencies** exist between apex ↔ enforcement ↔ system ↔ memory
2. **State files duplicated** in both `state/` and `apex/governance/`
3. **Guards split** between `guards/` and `hypervisor/guards/`
4. **Enforcement over-fragmented** with 12 subdirectories averaging 2-4 files each
5. **Integration layer** has highest coupling (imports from 5 modules)

## Constitutional Pipeline Mapping

### AGI Layer (111-333): Logic, Reasoning, Truth

**Pipeline Stages:**
- 111 SENSE: Perception, input processing
- 222 REFLECT: Memory, context retrieval
- 333 ATLAS/REASON: Logical analysis, truth verification

**Current Implementation:**

| Directory | Files | Purpose | Pipeline Stage | Floor Coverage |
|-----------|-------|---------|---------------|----------------|
| agi/ | 7 files | Core AGI logic | 111-333 | F1 (Truth), F2 (Clarity) |
| agi/atlas.py | 5.5KB | Logical reasoning | 333 | F1 |
| agi/clarity_scorer.py | 1.3KB | Clarity measurement | 111-333 | F2 |
| agi/delta_kernel.py | 8.0KB | Entropy reduction | 222-333 | F2 |
| agi/entropy.py | 12.8KB | ΔS calculation | 222-333 | F2 |
| agi/floor_checks.py | 2.9KB | F1-F3 validation | 111-333 | F1, F2, F3 |

**Dependencies:** None (pure logic layer)

**Status:** ✅ Well-organized, minimal dependencies

### ASI Layer (444-666): Safety, Care, Alignment

**Pipeline Stages:**
- 444 ALIGN: Constitutional alignment
- 555 EMPATHIZE: Stakeholder care, weakest link analysis
- 666 BRIDGE: Theory-to-code alignment

**Current Implementation:**

| Directory | Files | Purpose | Pipeline Stage | Floor Coverage |
|-----------|-------|---------|---------------|----------------|
| asi/ | 5 files + 3 subdirs | ASI safety layer | 444-666 | F4 (Empathy), F5 (Humility), F6 (Amanah) |
| asi/asi_integration_555.py | 13.2KB | Stage 555 implementation | 555 | F4 |
| asi/cooling.py | 3.6KB | Thermodynamic cooling | 444-666 | F3 (Peace) |
| asi/empathy/ | 2 files | Empathy architecture | 555 | F4 (κᵣ) |
| asi/stakeholder/ | 2 files | Weakest stakeholder | 555 | F4 |
| asi/tom/ | 2 files | Theory of Mind | 555 | F4 |
| asi/eureka.py | 5.0KB | Insight generation | 777 (misplaced?) | F7 |
| asi/omega_kernel.py | 10.9KB | Humility kernel | 444-666 | F5 (Ω₀) |
| asi/floor_checks.py | 5.5KB | F4-F6 validation | 444-666 | F4, F5, F6 |

**Dependencies:** None (pure safety layer)

**Status:** ✅ Well-organized, but `eureka.py` belongs in apex/ (777)

**Misalignment:**
- `asi/eureka.py` implements stage 777 (APEX layer) but lives in ASI (444-666)
- **Recommendation:** Move to apex/eureka/ or keep as ASI insight generator (clarify role)

### APEX Layer (777-999): Judgment, Audit, Sealing

**Pipeline Stages:**
- 777 EUREKA: Final insight synthesis
- 888 COMPASS: Witness council, final judgment
- 999 SEAL: Constitutional sealing

**Current Implementation:**

| Directory | Files | Purpose | Pipeline Stage | Floor Coverage |
|-----------|-------|---------|---------------|----------------|
| apex/ | 3 files + 2 subdirs | Final judgment | 777-999 | F7 (RASA), F8 (Tri-Witness), F9 (Anti-Hantu) |
| apex/psi_kernel.py | 10.0KB | System vitality | 777-999 | Ψ (Psi) metric |
| apex/floor_checks.py | 5.7KB | F7-F9 validation | 777-999 | F7, F8, F9 |
| apex/contracts/ | 2 files | Output contracts | 999 | F6 (Amanah) |
| apex/governance/ | 12 files | ⚠️ MIXED | ??? | Multiple |

**Dependencies:** enforcement, spec, state, system, utils (5 modules - HIGH COUPLING)

**Status:** ⚠️ CRITICAL ISSUE - apex/governance/ mixes state + governance concerns

**Governance Directory Analysis:**

| File | Purpose | Should Be In |
|------|---------|--------------|
| fag.py | Floor-Aligned Governance | ✅ apex/governance/ |
| proof_of_governance.py | Governance proofs | ✅ apex/governance/ |
| session_physics.py | Session thermodynamics | ✅ apex/governance/ |
| sovereign_signature.py | Constitutional signatures | ✅ apex/governance/ |
| vault_retrieval.py | Vault access | ✅ apex/governance/ |
| zkpc_runtime.py | Zero-Knowledge Proof | ✅ apex/governance/ |
| ledger.py | ⚠️ DUPLICATE | ❌ → state/ledger/ |
| ledger_cryptography.py | ⚠️ DUPLICATE | ❌ → state/ledger_cryptography/ |
| ledger_hashing.py | ⚠️ DUPLICATE | ❌ → state/ledger_hashing/ |
| merkle.py | ⚠️ DUPLICATE | ❌ → state/merkle/ |
| merkle_ledger.py | ⚠️ DUPLICATE | ❌ → state/merkle_ledger/ |

**Entropy Impact:** +4.2 (state duplication) + +1.2 (mixed concerns) = **+5.4 total**

### ENFORCEMENT Layer (012-099): Floor Validation

**Purpose:** Constitutional floor checks (F1-F12) across all pipeline stages

**Current Implementation:**

| Directory | Subdirs | Files | Purpose | Complexity Score |
|-----------|---------|-------|---------|------------------|
| enforcement/ | 12 | 16 root + 29 in subdirs | Floor enforcement | HIGH (⚠️) |

**Subdirectory Breakdown:**

```
enforcement/
├── attestation/      (2 files) - Manifest validation
├── audit/            (2 files) - Eye adapter auditing
├── eval/             (4 files) - AGI/ASI evaluation
├── evidence/         (3 files) - Evidence routing
├── floor_detectors/  (3 files) - Amanah risk detection
├── judiciary/        (2 files) - Semantic firewall, witness
├── routing/          (3 files) - Prompt routing, refusal
├── stages/           (3 files) - Stage 000, 555 specific
├── trinity/          (5 files) - Forge, QC, seal
├── validators/       (2 files) - Spec checking
├── verification/     (2 files) - Distributed verification
└── [16 root files]   - metrics.py, genius_metrics.py, etc.
```

**Entropy Analysis:**

| Issue | Impact | Recommendation |
|-------|--------|----------------|
| 12 subdirectories with 2-5 files each | +2.1 ΔS | Consolidate to 3 modules |
| Related functions separated | +0.5 ΔS | Group by function, not artifact |
| Unclear navigation | +0.4 ΔS | Flatten structure |

**Proposed Consolidation:**

```
enforcement/
├── metrics.py           (KEEP + enhance) - Core floor scoring
├── validators.py        (NEW) - Merge floor_detectors/, validators/, verification/
├── floor_checks.py      (NEW) - Merge eval/, judiciary/, attestation/
├── genius_metrics.py    (KEEP) - GENIUS law implementation
├── trinity/             (KEEP) - Trinity-specific logic (too complex to merge)
├── routing/             (KEEP) - Distinct routing concern
├── stages/              (KEEP) - Stage-specific overrides
└── [other root files]   (REVIEW) - crisis_handler, temporal_checks, etc.
```

**Entropy Reduction:** -2.1 ΔS (from consolidation)

**Dependencies:** apex, memory, spec, system (4 modules - circular with system)

### HYPERVISOR Layer (F10-F12): Injection Defense, Ontology, Auth

**Purpose:** Pre-constitutional enforcement (000 stage, before pipeline)

**Current Implementation:**

| Directory | Files | Purpose | Floor Coverage |
|-----------|-------|---------|----------------|
| hypervisor/ | 1 file + 1 subdir | F10-F12 enforcement | F10, F11, F12 |
| hypervisor/guards/ | 5 files | ⚠️ DUPLICATE with guards/ | F10, F11, F12 |
| guards/ | 5 files | ⚠️ LEGACY location | F10, F11, F12 |

**Duplication Analysis:**

| File | guards/ | hypervisor/guards/ | Size | Action |
|------|---------|-------------------|------|--------|
| injection_guard.py | ✅ | ✅ | 11.7KB | Keep hypervisor/, deprecate guards/ |
| nonce_manager.py | ✅ | ✅ | 9.6KB | Keep hypervisor/, deprecate guards/ |
| ontology_guard.py | ✅ | ✅ | 7.1KB | Keep hypervisor/, deprecate guards/ |
| session_dependency.py | ✅ | ✅ | 6.7KB | Keep hypervisor/, deprecate guards/ |

**Rationale:** Hypervisor is the correct constitutional location for F10-F12 (pre-pipeline enforcement)

**Entropy Reduction:** -0.8 ΔS (from removing guards/ duplication)

**Dependencies:** guards → hypervisor (correct direction)

### STATE Layer: Ledger, Memory, Merkle Trees

**Purpose:** Immutable state, audit trail, ZKPC

**Current Implementation:**

| Directory | Files | Purpose | Status |
|-----------|-------|---------|--------|
| state/ | 6 files | Ledger, merkle, cryptography | ✅ PRIMARY |
| memory/ | 0 root + 6 subdirs | Memory subsystems | ✅ SEPARATE |
| apex/governance/ | 12 files (5 duplicates) | ⚠️ MIXED | ❌ EXTRACT |

**State Files:**

| File | Size | Purpose | Also In |
|------|------|---------|---------|
| ledger.py | ~1KB | Audit ledger | apex/governance/ ⚠️ |
| ledger_cryptography.py | 21KB | Cryptographic signing | apex/governance/ ⚠️ |
| ledger_hashing.py | 3.9KB | Hash generation | apex/governance/ ⚠️ |
| merkle.py | 4.9KB | Merkle tree | apex/governance/ ⚠️ |
| merkle_ledger.py | 3.3KB | Combined ledger | apex/governance/ ⚠️ |

**Memory Subdirectories:**

```
memory/
├── core/         - Core memory logic
├── eureka/       - Eureka insights storage
├── l7/           - L7 integration
├── ledger/       - Memory ledger (different from state/ledger)
├── phoenix/      - Phoenix recovery
└── vault/        - Vault 999 storage
```

**Status:** Memory is correctly separate from state (different concerns)

**Dependencies:**
- state → enforcement, system (2 modules)
- memory → enforcement, system, utils (3 modules)

### SYSTEM Layer: Core Runtime, Pipeline, Orchestration

**Purpose:** Pipeline orchestration, verdict emission, runtime manifest

**Current Implementation:**

| Directory | Files | Purpose | Dependencies |
|-----------|-------|---------|--------------|
| system/ | 8 files + 7 subdirs | System core | enforcement, memory (circular) |
| pipeline/ | 8 files | Stage orchestration | agi, apex, asi |
| runtime/ | 13 files | Stage implementations | (no internal imports) |
| spec/ | 3 files | Spec validation | (no internal imports) |

**System Files:**

| File | Size | Purpose |
|------|------|---------|
| apex_prime.py | Large | Final judgment (APEX PRIME) |
| hypervisor.py | Medium | Pre-pipeline enforcement |
| ignition.py | Medium | System startup |
| kernel.py | Medium | Core kernel |
| pipeline.py | Medium | Pipeline orchestration |
| verdict_emission.py | Medium | Verdict output |

**Status:** ✅ Well-organized, but circular dependency with enforcement

### INTEGRATION Layer: External Bridges, APIs, MCP

**Purpose:** Bridge to external systems, APIs, LLM providers

**Current Implementation:**

| Directory | Files | Purpose | Dependencies |
|-----------|-------|---------|--------------|
| integration/ | 5 files + 7 subdirs | External bridges | apex, enforcement, guards, memory, system (5 modules - HIGHEST COUPLING) |
| mcp/ | 10 files + 2 subdirs | Model Context Protocol | apex, enforcement, integration, memory, system (5 modules) |
| organs/ | 2 files | Prompt processing | (no internal imports) |

**Status:** ⚠️ High coupling expected for integration layer, but consider if some can be reduced

## Circular Dependency Analysis

**Critical Cycles:**

```
apex ↔ enforcement ↔ system ↔ memory
     ↖________________↙
```

**Breakdown:**

1. **apex → enforcement:** apex needs floor scoring
2. **enforcement → apex:** enforcement uses apex contracts
3. **enforcement → system:** enforcement uses system runtime
4. **system → enforcement:** system validates floors
5. **enforcement → memory:** enforcement logs to memory
6. **memory → enforcement:** memory uses floor checks
7. **memory → system:** memory uses system utilities
8. **system → memory:** system reads from memory

**Impact:** Circular dependencies increase coupling and make testing harder

**Recommendation:**
1. Extract interfaces/contracts to separate layer (could be part of spec/)
2. Use dependency injection where possible
3. Consider creating a `core/` or `contracts/` module for shared interfaces

## Entropy Hotspots Ranked

| Rank | Issue | Location | ΔS Impact | Priority |
|------|-------|----------|-----------|----------|
| 1 | State duplication | apex/governance/ + state/ | +4.2 | 🔴 HIGH |
| 2 | Enforcement fragmentation | enforcement/ (12 subdirs) | +2.1 | 🔴 HIGH |
| 3 | Mixed governance concerns | apex/governance/ | +1.2 | 🟡 MEDIUM |
| 4 | Guards duplication | guards/ + hypervisor/guards/ | +0.8 | 🟡 MEDIUM |
| 5 | Circular dependencies | apex↔enforcement↔system↔memory | +0.8 | 🟡 MEDIUM |
| 6 | Schema validator duplication | spec/ + utils/ | +0.6 | 🟢 LOW |
| 7 | Eureka misplacement | asi/eureka.py vs apex/ | +0.4 | 🟢 LOW |
| 8 | Test suite instability | v45/v46 mismatch | +1.6 | 🔴 HIGH |

**Total Current ΔS: 11.7** (close to estimated 11.9)

**Target ΔS: 3.2**

**Required Reduction: -8.5**

## Import Dependency Graph (ASCII)

```
CONSTITUTIONAL LAYERS:

    ┌─────────────────────────────────────────────────────────┐
    │ HYPERVISOR (F10-F12) - Pre-Pipeline Enforcement         │
    │   hypervisor/ guards/                                   │
    └────────────────────┬────────────────────────────────────┘
                         │
    ┌────────────────────▼────────────────────────────────────┐
    │ AGI (111-333) - Logic, Reasoning, Truth                 │
    │   agi/   (no dependencies)                              │
    └─────────────────────────────────────────────────────────┘
                         │
    ┌────────────────────▼────────────────────────────────────┐
    │ ASI (444-666) - Safety, Care, Alignment                 │
    │   asi/   (no dependencies)                              │
    └─────────────────────────────────────────────────────────┘
                         │
    ┌────────────────────▼────────────────────────────────────┐
    │ APEX (777-999) - Judgment, Sealing                      │
    │   apex/ → enforcement, spec, state, system, utils       │
    └────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────────────────┐
         │                                   │
    ┌────▼────────────────┐       ┌──────────▼──────────────┐
    │ ENFORCEMENT         │◄──────┤ SYSTEM                  │
    │ Floor validation    │       │ Runtime, pipeline       │
    │ (circular)          ├──────►│ (circular)              │
    └────┬────────────────┘       └──────────┬──────────────┘
         │                                   │
         │        ┌──────────────────────────┘
         │        │
    ┌────▼────────▼────┐
    │ STATE & MEMORY   │
    │ Ledger, audit    │
    │ (circular)       │
    └────┬─────────────┘
         │
    ┌────▼─────────────────────────────────────────────┐
    │ INTEGRATION (External bridges, MCP, APIs)        │
    │   integration/, mcp/, organs/                    │
    │   → apex, enforcement, guards, memory, system    │
    └──────────────────────────────────────────────────┘

UTILITIES & SUPPORT:

    spec/ (validation) → (no internal imports)
    utils/ → spec, system
    kernels/ → (no internal imports)
    floors/ → (no internal imports)
```

## Recommended Consolidations

### 1. State Extraction (ΔS -4.2)

**Action:**
```
DELETE: apex/governance/ledger*.py, merkle*.py
KEEP:   state/ledger*.py, merkle*.py (PRIMARY)
CREATE: apex/governance/ledger.py (deprecation shim)
```

**Shim Example:**
```python
# apex/governance/ledger.py (DEPRECATED)
import warnings
from arifos_core.state.ledger import *

warnings.warn(
    "arifos_core.apex.governance.ledger is deprecated. "
    "Use arifos_core.state.ledger instead. "
    "This shim will be removed in v47.1 (72 hours).",
    DeprecationWarning, stacklevel=2
)
```

### 2. Governance Crystallization (ΔS -1.2)

**After state extraction, apex/governance/ should contain ONLY:**
```
apex/governance/
├── __init__.py
├── fag.py                      (Floor-Aligned Governance)
├── proof_of_governance.py      (Constitutional proofs)
├── session_physics.py          (Thermodynamic session management)
├── sovereign_signature.py      (Constitutional signatures)
├── vault_retrieval.py          (Vault access authorization)
└── zkpc_runtime.py             (Zero-Knowledge Proof of Constitution)
```

**Optionally create:**
```
apex/
└── proofs/                     (Extract from governance/)
    ├── proof_of_governance.py
    └── zkpc_runtime.py
```

### 3. Hypervisor Elevation (ΔS -0.8)

**Action:**
```
DELETE: guards/*.py
KEEP:   hypervisor/guards/*.py (PRIMARY)
CREATE: guards/*.py (deprecation shims)
```

### 4. Enforcement Consolidation (ΔS -2.1)

**Merge subdirectories:**
```
enforcement/
├── metrics.py              (KEEP + enhance)
├── genius_metrics.py       (KEEP)
├── validators.py           (NEW - merge floor_detectors/, validators/, verification/)
├── floor_checks.py         (NEW - merge eval/, judiciary/, attestation/)
├── trinity/                (KEEP - too complex to flatten)
│   ├── forge.py
│   ├── housekeeper.py
│   ├── qc.py
│   └── seal.py
├── routing/                (KEEP - distinct concern)
│   ├── prompt_router.py
│   └── refusal_templates.py
├── stages/                 (KEEP - stage-specific overrides)
│   ├── stage_000_amanah.py
│   └── stage_555_empathy.py
└── [root files]            (REVIEW individually)
    ├── claim_detection.py
    ├── crisis_handler.py
    ├── meta_governance.py
    ├── refusal_accountability.py
    ├── response_validator.py
    ├── response_validator_extensions.py
    ├── risk_literacy.py
    ├── sabar_timer.py
    ├── tcha_metrics.py
    ├── temporal_checks.py
    ├── trinity_orchestrator.py
    └── wisdom_gated_release.py
```

## Next Phase: 333 REASON

Will propose:
1. Complete before/after directory tree
2. Detailed file move list with entropy impact
3. Backward compatibility shim specifications
4. Import path migration guide
5. Test strategy (maintain 100% pass rate during migration)

---

**Constitutional Compliance:**
- F1 (Truth): ✅ Evidence-based from import scan
- F2 (ΔS): ✅ Identifies entropy reduction paths
- F4 (κᵣ): ✅ Considers impact on developers (weakest stakeholder)
- F8 (Tri-Witness): ✅ Human (spec) + AI (code) + Reality (imports) aligned

**Ditempa bukan diberi** - Reflected through dependency analysis, not assumption.
