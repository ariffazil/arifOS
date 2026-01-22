# arifos_core Architecture Proposal (v46.1)

**Date:** 2026-01-12
**Authority:** Based on v46 spec, AGENTS.md, and Trinity Orthogonal principles
**Current State:** 16 directories, ~36,842 lines, mixed organization
**Goal:** Clear orthogonal architecture aligned with constitutional principles

---

## Executive Summary

**Problem:** `arifos_core` has grown organically with:
- Mixed responsibilities in `enforcement/` (9 subdirectories)
- Duplication across kernel directories
- Unclear separation between kernels, governance, and integration
- ~36,842 lines spread across 16 top-level directories

**Solution:** Reorganize into **8 Orthogonal Zones** matching v46.1 architecture:

```
arifos_core/
├── agi/          # AGI Kernel (Δ-Mind) - Logic & Reasoning [F1, F2, F5, F10]
├── asi/          # ASI Kernel (Ω-Heart) - Safety & Care [F3, F4, F6, F7, F9, F11-F12]
├── apex/         # APEX Kernel (Ψ-Soul) - Final Judgment [F8, verdict authority]
├── enforcement/  # Trinity Orchestration & Floor Enforcement [metrics, orchestrator]
├── integration/  # External LLM/API/MCP Adapters [litellm, openai, anthropic]
├── memory/       # Ledger, Cooling, EUREKA, Phoenix-72 [state persistence]
├── guards/       # F10-F12 Hypervisor Guards [ontology, nonce, injection]
├── system/       # Pipeline, APEX PRIME, Runtime Lifecycle [orchestration]
└── mcp/          # Model Context Protocol Server [tools, resources]
```

---

## Current State Analysis

### Current Directory Structure (16 directories)

| Directory | Files | Purpose | Issues |
|-----------|-------|---------|--------|
| `enforcement/` | 47 | Mixed: attestation, audit, eval, evidence, floor_detectors, judiciary, routing, stages, trinity, validators, verification | **TOO LARGE** - 9 subdirs with mixed concerns |
| `integration/` | 38 | External adapters (LLM, API, connectors, waw) | Has internal guards (should move to `guards/`) |
| `system/` | 22 | Pipeline, engines, eye, recovery, research, runtime, temporal | Mixed runtime + research artifacts |
| `mcp/` | 18 | MCP server, tools, certs | Good separation |
| `apex/` | 16 | APEX kernel, contracts, governance | Governance overlap with enforcement |
| `memory/` | 8 | Ledger, cooling, EUREKA | Good separation |
| `agi/` | 4 | AGI kernel, floor checks | Minimal, needs expansion |
| `asi/` | 4 | ASI kernel, floor checks | Minimal, needs expansion |
| `guards/` | 5 | F10-F12 Hypervisor guards | Good separation (v46.0 new) |
| `utils/` | 6 | General utilities | Utility dumping ground |
| `foundation/` | 3 | Foundation utilities | Overlap with utils |
| `organs/` | 2 | W@W organs | Should integrate with kernels |
| `spec/` | 2 | Spec loading | Good separation |
| `floors/` | 1 | Floor definitions | **DUPLICATE** - floor checks in kernels |
| `adapters/` | 1 | Legacy adapters | Overlap with integration |

**Total:** ~170 Python files, 36,842 lines

---

## Proposed Architecture (v46.1 Orthogonal Zones)

### Design Principles

1. **Trinity Orthogonal**: AGI (Δ) → ASI (Ω) → APEX (Ψ) separation
2. **Single Responsibility**: Each zone has ONE clear purpose
3. **Floor Ownership**: Floors live in the kernel that enforces them
4. **No Duplication**: One canonical location per concept
5. **Dependency Direction**: Enforcement → Kernels → System (uni-directional)

---

### Zone 1: AGI Kernel (Δ-Mind) - Logic & Reasoning

**Purpose:** Truth, clarity, logic, symbolic reasoning
**Floors Owned:** F1 (Truth), F2 (ΔS/Clarity), F5 (Ω₀/Humility), F10 (Ontology)

```
arifos_core/agi/
├── __init__.py
├── atlas.py              # AGI core reasoning (Stage 333)
├── clarity_scorer.py     # ΔS (F2) measurement
├── floor_checks.py       # F1, F2, F5 enforcement
├── truth_detector.py     # F1 Truth verification (NEW - move from enforcement)
├── humility_band.py      # F5 Ω₀ band checking (NEW - move from enforcement)
└── symbolic_mode.py      # F10 Ontology support (NEW - coordinate with guards)
```

**Migrations:**
- ✅ Keep: `atlas.py`, `clarity_scorer.py`, `floor_checks.py`
- ⬆️ Move IN: Truth/humility detectors from `enforcement/floor_detectors/`
- 🔗 Reference: `guards/ontology_guard.py` for F10 (don't duplicate)

---

### Zone 2: ASI Kernel (Ω-Heart) - Safety & Care

**Purpose:** Empathy, stability, care protocols, felt-care
**Floors Owned:** F3 (Peace²), F4 (κᵣ/Empathy), F6 (Amanah), F7 (RASA), F9 (Anti-Hantu), F11-F12 (Command Auth, Injection via guards)

```
arifos_core/asi/
├── __init__.py
├── cooling.py            # Cooling protocol (SABAR)
├── eureka.py             # EUREKA notes & cross-session memory
├── floor_checks.py       # F3, F4, F5, F7 enforcement
├── peace_scorer.py       # F3 Peace² measurement (NEW - move from enforcement)
├── empathy_scorer.py     # F4 κᵣ measurement (NEW - move from enforcement)
├── amanah_detector.py    # F6 Amanah risk detection (NEW - move from enforcement)
├── rasa_detector.py      # F7 RASA signal detection (NEW - move from enforcement)
├── anti_hantu.py         # F9 Anti-Hantu pattern detection (NEW - move from enforcement)
└── crisis_handler.py     # Crisis override logic (MOVE from enforcement)
```

**Migrations:**
- ✅ Keep: `cooling.py`, `eureka.py`, `floor_checks.py`
- ⬆️ Move IN:
  - `enforcement/floor_detectors/amanah_risk_detectors.py` → `amanah_detector.py`
  - `enforcement/crisis_handler.py` → `crisis_handler.py`
  - Peace²/κᵣ/RASA detectors from enforcement
- 🔗 Reference: `guards/nonce_manager.py` (F11), `guards/injection_guard.py` (F12)

---

### Zone 3: APEX Kernel (Ψ-Soul) - Final Judgment

**Purpose:** Constitutional judiciary, verdict authority, tri-witness
**Floors Owned:** F8 (Tri-Witness)
**Authority:** SOLE SOURCE OF TRUTH for verdicts (SES - Single Execution Spine)

```
arifos_core/apex/
├── __init__.py
├── floor_checks.py       # F6, F8, F9 enforcement
├── tri_witness.py        # F8 Tri-Witness consensus (NEW - extract from floor_checks)
├── contracts/
│   ├── __init__.py
│   └── apex_prime_output_v41.py  # Verdict contracts
└── governance/
    ├── __init__.py
    ├── fag.py            # File Access Governance (MOVE to system/)
    ├── ledger*.py        # Ledger modules (MOVE to memory/)
    ├── merkle*.py        # Merkle proofs (MOVE to memory/)
    ├── proof_of_governance.py
    ├── session_physics.py  # Session state (MOVE to system/)
    ├── sovereign_signature.py
    ├── vault_retrieval.py  # Vault access (MOVE to memory/)
    └── zkpc_runtime.py
```

**Migrations:**
- ✅ Keep: `floor_checks.py`, `contracts/`, core governance files
- ⬇️ Move OUT:
  - `governance/fag.py` → `system/fag.py`
  - `governance/ledger*.py` → `memory/ledger.py`
  - `governance/merkle*.py` → `memory/merkle.py`
  - `governance/vault_retrieval.py` → `memory/vault.py`
  - `governance/session_physics.py` → `system/session.py`
- 🎯 Result: APEX focuses on verdict authority, not infrastructure

---

### Zone 4: Enforcement (Trinity Orchestration)

**Purpose:** Coordinate AGI/ASI/APEX kernels, compute metrics, route verdicts
**NOT:** Individual floor detection (that's in kernels)

```
arifos_core/enforcement/
├── __init__.py
├── metrics.py            # Constitutional metrics computation (KEEP)
├── genius_metrics.py     # GENIUS LAW (G, C_dark) (KEEP)
├── trinity_orchestrator.py  # Coordinate AGI→ASI→APEX (KEEP)
├── claim_detection.py    # Claim profiling (KEEP)
├── response_validator.py # Response validation (KEEP)
├── meta_governance.py    # Meta-floor governance (KEEP)
├── risk_literacy.py      # Risk scoring (KEEP)
├── refusal_accountability.py  # Refusal tracking (KEEP)
├── attestation/          # Manifest verification (KEEP)
│   ├── __init__.py
│   └── manifest.py
├── audit/                # @EYE audit adapter (KEEP)
│   ├── __init__.py
│   └── eye_adapter.py
├── evidence/             # Evidence routing (KEEP)
│   ├── __init__.py
│   ├── conflict_routing.py
│   ├── evidence_pack.py
│   └── routing_signal.py
└── eval/                 # Constitutional evaluation (KEEP)
    ├── __init__.py
    ├── agi.py
    ├── asi.py
    ├── evaluate.py
    └── types.py
```

**Migrations:**
- ✅ Keep: Core orchestration (metrics, trinity, claim detection, validation, eval)
- ⬇️ Move OUT (DELETE from enforcement/):
  - `floor_detectors/` → Move to kernels (AGI/ASI)
  - `judiciary/` → Move to APEX or system
  - `routing/` → Merge into evidence/ or system/
  - `stages/` → Move to system/pipeline/
  - `trinity/` → Already have `trinity_orchestrator.py` (consolidate)
  - `validators/` → Already have `response_validator.py` (consolidate)
  - `verification/` → Merge into attestation/ or audit/
  - `emergency_calibration_v45.py` → Move to system/recovery/

**Result:** Enforcement becomes thin orchestration layer, not implementation layer

---

### Zone 5: Integration (External Adapters)

**Purpose:** Connect to external LLMs, APIs, MCP clients
**NOT:** Internal guards (those go in guards/)

```
arifos_core/integration/
├── __init__.py
├── adapters/             # LLM adapters (litellm, openai, anthropic)
│   ├── __init__.py
│   └── ...
├── api/                  # FastAPI server
│   ├── __init__.py
│   ├── main.py
│   └── routes/
├── config/               # Configuration management
├── connectors/           # Database/external connectors
│   ├── __init__.py
│   └── ...
├── plugins/              # Plugin system
├── sealion_suite/        # SEA-LION test harness
├── waw/                  # W@W organ bridges (KEEP - but consider moving organs here)
│   ├── __init__.py
│   ├── bridges/
│   └── ...
└── wrappers/             # LLM wrappers
    ├── __init__.py
    └── ...
```

**Migrations:**
- ✅ Keep: All external adapters
- ⬇️ Move OUT:
  - `integration/guards/` → `guards/` (internal guards don't belong here)
- 🔗 Consider: Merge `organs/` into `integration/waw/organs/` for cohesion

---

### Zone 6: Memory (State Persistence)

**Purpose:** Ledger, cooling, EUREKA, Phoenix-72, vault
**Authority:** ALL state writes go through this zone

```
arifos_core/memory/
├── __init__.py
├── ledger.py             # Cooling ledger (MOVE from apex/governance)
├── ledger_hashing.py     # Hash chains (MOVE from apex/governance)
├── ledger_cryptography.py  # Crypto (MOVE from apex/governance)
├── merkle.py             # Merkle proofs (MOVE from apex/governance)
├── merkle_ledger.py      # Merkle ledger (MOVE from apex/governance)
├── eureka.py             # EUREKA notes (ALREADY HERE, expand)
├── cooling.py            # Cooling protocol (REFERENCE asi/cooling.py)
├── phoenix.py            # Phoenix-72 amendment protocol (NEW)
├── vault.py              # Vault-999 retrieval (MOVE from apex/governance)
├── scar.py               # SCAR lifecycle (NEW - if exists)
└── session_state.py      # Session state persistence (NEW - from system)
```

**Migrations:**
- ✅ Keep: Existing memory files
- ⬆️ Move IN: All ledger/merkle/vault files from `apex/governance/`
- 🎯 Result: Single source of truth for ALL memory operations

---

### Zone 7: Guards (Hypervisor Layer - F10-F12)

**Purpose:** OS-level guards that cannot be bypassed by prompts
**Authority:** v46.0 CIV-12 Hypervisor Layer

```
arifos_core/guards/
├── __init__.py
├── ontology_guard.py     # F10: Literalism detection (KEEP)
├── nonce_manager.py      # F11: Command authentication (KEEP)
├── injection_guard.py    # F12: Injection defense (KEEP)
└── session_dependency.py # Session management (KEEP)
```

**Migrations:**
- ✅ Keep: All existing guards (newly created in v46.0)
- ⬆️ Move IN: `integration/guards/*` if any exist
- 🎯 Result: Clean hypervisor layer

---

### Zone 8: System (Pipeline & Runtime)

**Purpose:** Orchestrate lifecycle (000→999), APEX PRIME, runtime, recovery
**NOT:** Business logic (that's in kernels)

```
arifos_core/system/
├── __init__.py
├── pipeline.py           # Main 000→999 pipeline (KEEP)
├── apex_prime.py         # APEX PRIME judiciary (KEEP)
├── hypervisor.py         # F10-F12 orchestration (KEEP - v46.0 new)
├── verdict_emission.py   # Verdict formatting (KEEP)
├── fag.py                # File Access Governance (MOVE from apex)
├── session.py            # Session physics (MOVE from apex)
├── engines/              # Execution engines (KEEP)
│   ├── __init__.py
│   └── ...
├── eye/                  # @EYE Sentinel (KEEP)
│   ├── __init__.py
│   └── ...
├── recovery/             # Error recovery (KEEP + add emergency_calibration)
│   ├── __init__.py
│   └── ...
├── runtime/              # Runtime state (KEEP)
│   ├── __init__.py
│   └── ...
└── temporal/             # Time governance (KEEP)
    ├── __init__.py
    └── ...
```

**Migrations:**
- ✅ Keep: Core system orchestration
- ⬆️ Move IN:
  - `apex/governance/fag.py` → `system/fag.py`
  - `apex/governance/session_physics.py` → `system/session.py`
  - `enforcement/stages/` → Integrate into `pipeline.py` or create `system/stages/`
  - `enforcement/emergency_calibration_v45.py` → `system/recovery/`
- ⬇️ Move OUT:
  - `system/dream_forge/` → Delete or move to research/
  - `system/research/` → Delete or move to separate research package
- 🎯 Result: Clean runtime orchestration

---

### Zone 9: MCP (Model Context Protocol)

**Purpose:** MCP server, tools, resources
**Authority:** MCP protocol compliance

```
arifos_core/mcp/
├── __init__.py
├── server.py             # MCP server entry point
├── tools/                # MCP tools
│   ├── __init__.py
│   ├── remote/           # Remote tools
│   └── well/             # W@W tools
└── certs/                # SSL certificates
```

**Migrations:**
- ✅ Keep: All MCP infrastructure
- 🎯 Result: Clean MCP layer

---

## Deprecated / Delete

### Remove Entirely

1. **`floors/`** - Floor checks live in kernels, not separate directory
2. **`foundation/`** - Merge into `utils/` or kernels
3. **`adapters/`** - Merge into `integration/adapters/`
4. **`organs/`** - Merge into `integration/waw/organs/`
5. **`system/dream_forge/`** - Research artifact, not production
6. **`system/research/`** - Research artifact, not production

### Consolidate

1. **`enforcement/floor_detectors/`** → Move to AGI/ASI kernels
2. **`enforcement/judiciary/`** → Move to APEX or system
3. **`enforcement/routing/`** → Merge into evidence/ or system
4. **`enforcement/stages/`** → Move to system/pipeline/
5. **`enforcement/trinity/`** → Already have trinity_orchestrator.py
6. **`enforcement/validators/`** → Already have response_validator.py
7. **`enforcement/verification/`** → Merge into attestation/

---

## Migration Strategy (3-Phase Plan)

### Phase 1: Move OUT of enforcement/ (Week 1)

**Goal:** Reduce enforcement/ from 9 subdirs to 4

1. **Move floor detectors to kernels:**
   - `enforcement/floor_detectors/amanah_risk_detectors.py` → `asi/amanah_detector.py`
   - Create `agi/truth_detector.py`, `agi/humility_band.py`
   - Create `asi/peace_scorer.py`, `asi/empathy_scorer.py`, `asi/rasa_detector.py`, `asi/anti_hantu.py`

2. **Move stages to system:**
   - `enforcement/stages/` → `system/stages/` or integrate into `system/pipeline.py`

3. **Consolidate duplicates:**
   - Delete `enforcement/trinity/` (keep `trinity_orchestrator.py`)
   - Merge `enforcement/validators/` into `response_validator.py`
   - Merge `enforcement/verification/` into `attestation/`

4. **Move infrastructure:**
   - `enforcement/emergency_calibration_v45.py` → `system/recovery/`
   - `enforcement/crisis_handler.py` → `asi/crisis_handler.py`

**Result:** enforcement/ has 4 subdirs: attestation/, audit/, evidence/, eval/

---

### Phase 2: Move OUT of apex/governance/ (Week 2)

**Goal:** APEX focuses on verdict authority, not infrastructure

1. **Move ledger to memory:**
   - `apex/governance/ledger.py` → `memory/ledger.py`
   - `apex/governance/ledger_hashing.py` → `memory/ledger_hashing.py`
   - `apex/governance/ledger_cryptography.py` → `memory/ledger_cryptography.py`
   - `apex/governance/merkle.py` → `memory/merkle.py`
   - `apex/governance/merkle_ledger.py` → `memory/merkle_ledger.py`
   - `apex/governance/vault_retrieval.py` → `memory/vault.py`

2. **Move system to system:**
   - `apex/governance/fag.py` → `system/fag.py`
   - `apex/governance/session_physics.py` → `system/session.py`

3. **Keep in apex/governance:**
   - `proof_of_governance.py`
   - `sovereign_signature.py`
   - `zkpc_runtime.py`

**Result:** apex/governance/ has 3 files (governance only, not infrastructure)

---

### Phase 3: Cleanup & Consolidate (Week 3)

**Goal:** Remove deprecated directories, consolidate duplicates

1. **Delete deprecated:**
   - `floors/` (move content to kernels)
   - `foundation/` (merge into utils/)
   - `adapters/` (merge into integration/adapters/)
   - `system/dream_forge/` (delete)
   - `system/research/` (delete)

2. **Consolidate organs:**
   - `organs/` → `integration/waw/organs/`

3. **Move guards:**
   - `integration/guards/*` → `guards/`

4. **Update imports:**
   - Run global find-replace for moved modules
   - Update `__init__.py` files
   - Fix tests

**Result:** 8 clean orthogonal zones

---

## Final Architecture (v46.1)

```
arifos_core/                      (~36,842 lines → organized into 8 zones)
│
├── agi/                          # AGI Kernel (Δ-Mind) [F1, F2, F5, F10]
│   ├── atlas.py
│   ├── clarity_scorer.py
│   ├── floor_checks.py
│   ├── truth_detector.py         # NEW
│   ├── humility_band.py          # NEW
│   └── symbolic_mode.py          # NEW
│
├── asi/                          # ASI Kernel (Ω-Heart) [F3, F4, F6, F7, F9, F11-F12]
│   ├── cooling.py
│   ├── eureka.py
│   ├── floor_checks.py
│   ├── peace_scorer.py           # NEW
│   ├── empathy_scorer.py         # NEW
│   ├── amanah_detector.py        # MOVED from enforcement
│   ├── rasa_detector.py          # NEW
│   ├── anti_hantu.py             # NEW
│   └── crisis_handler.py         # MOVED from enforcement
│
├── apex/                         # APEX Kernel (Ψ-Soul) [F8, Verdict Authority]
│   ├── floor_checks.py
│   ├── tri_witness.py            # NEW
│   ├── contracts/
│   │   └── apex_prime_output_v41.py
│   └── governance/               # Slimmed down (3 files)
│       ├── proof_of_governance.py
│       ├── sovereign_signature.py
│       └── zkpc_runtime.py
│
├── enforcement/                  # Trinity Orchestration (4 subdirs)
│   ├── metrics.py
│   ├── genius_metrics.py
│   ├── trinity_orchestrator.py
│   ├── claim_detection.py
│   ├── response_validator.py
│   ├── meta_governance.py
│   ├── risk_literacy.py
│   ├── refusal_accountability.py
│   ├── attestation/
│   ├── audit/
│   ├── evidence/
│   └── eval/
│
├── integration/                  # External Adapters
│   ├── adapters/
│   ├── api/
│   ├── config/
│   ├── connectors/
│   ├── plugins/
│   ├── sealion_suite/
│   ├── waw/
│   │   ├── bridges/
│   │   └── organs/               # MOVED from organs/
│   └── wrappers/
│
├── memory/                       # State Persistence
│   ├── ledger.py                 # MOVED from apex
│   ├── ledger_hashing.py         # MOVED from apex
│   ├── ledger_cryptography.py    # MOVED from apex
│   ├── merkle.py                 # MOVED from apex
│   ├── merkle_ledger.py          # MOVED from apex
│   ├── eureka.py
│   ├── cooling.py
│   ├── phoenix.py                # NEW
│   ├── vault.py                  # MOVED from apex
│   └── session_state.py          # NEW
│
├── guards/                       # Hypervisor Layer (F10-F12)
│   ├── ontology_guard.py
│   ├── nonce_manager.py
│   ├── injection_guard.py
│   └── session_dependency.py
│
├── system/                       # Pipeline & Runtime
│   ├── pipeline.py
│   ├── apex_prime.py
│   ├── hypervisor.py
│   ├── verdict_emission.py
│   ├── fag.py                    # MOVED from apex
│   ├── session.py                # MOVED from apex
│   ├── engines/
│   ├── eye/
│   ├── recovery/                 # + emergency_calibration
│   ├── runtime/
│   ├── stages/                   # MOVED from enforcement
│   └── temporal/
│
├── mcp/                          # Model Context Protocol
│   ├── server.py
│   ├── tools/
│   │   ├── remote/
│   │   └── well/
│   └── certs/
│
├── spec/                         # Spec Loading (keep)
├── utils/                        # Utilities (keep + foundation)
└── __init__.py
```

**Total:** 8 orthogonal zones (down from 16 mixed directories)

---

## Benefits

### 1. **Clear Ownership**
- Each floor has ONE kernel that enforces it
- F1, F2, F5, F10 → AGI
- F3, F4, F6, F7, F9, F11-F12 → ASI
- F8 → APEX
- Hypervisor coordination → guards/

### 2. **No Duplication**
- `floors/` deleted (floor checks in kernels)
- `floor_detectors/` moved to kernels
- Trinity orchestration consolidated

### 3. **Orthogonal Separation**
- AGI = Logic/Truth
- ASI = Safety/Care
- APEX = Judgment
- Enforcement = Orchestration
- Integration = External
- Memory = State
- Guards = Hypervisor
- System = Runtime

### 4. **Easier Navigation**
- Want truth logic? → `agi/truth_detector.py`
- Want empathy scoring? → `asi/empathy_scorer.py`
- Want ledger? → `memory/ledger.py`
- Want verdict authority? → `apex/floor_checks.py` or `system/apex_prime.py`

### 5. **Testability**
- Each kernel can be tested independently
- Clear boundaries = easier mocking
- Integration tests obvious (test orchestration layer)

---

## Implementation Checklist

### Pre-Migration
- [ ] Create feature branch: `refactor/v46-orthogonal-zones`
- [ ] Freeze new features (refactor only)
- [ ] Run full test suite (baseline)
- [ ] Document current import graph

### Phase 1: Move floor detectors (Week 1)
- [ ] Create new files in AGI/ASI
- [ ] Update imports in enforcement/
- [ ] Run tests after each move
- [ ] Update `__init__.py` exports

### Phase 2: Move apex/governance (Week 2)
- [ ] Move ledger files to memory/
- [ ] Move system files to system/
- [ ] Update imports in apex/
- [ ] Run tests after each move

### Phase 3: Cleanup (Week 3)
- [ ] Delete deprecated directories
- [ ] Consolidate organs → integration/waw/
- [ ] Global import updates
- [ ] Full test suite pass
- [ ] Update documentation

### Post-Migration
- [ ] Run Trinity QC (`python scripts/trinity.py qc`)
- [ ] Update ARCHITECTURE.md
- [ ] Create migration guide for external users
- [ ] Merge to main after human approval

---

## Risk Mitigation

### Risks

1. **Breaking Changes:** External users import from old paths
2. **Test Failures:** Imports break during migration
3. **Scope Creep:** Temptation to refactor logic during moves

### Mitigations

1. **Backward Compatibility (Optional):**
   - Keep `__init__.py` aliases for 1-2 versions
   - Example: `from arifos_core.enforcement.floor_detectors import X` → imports from `arifos_core.asi.X`
   - Deprecation warnings for old paths

2. **Incremental Testing:**
   - Run tests after EACH file move
   - Don't batch moves

3. **File Moves Only:**
   - **Rule:** Move files, don't change logic
   - **Exception:** Only fix imports, nothing else
   - **Discipline:** Refactoring logic comes AFTER reorganization

---

## Success Metrics

- ✅ **Reduced Directories:** 16 → 8 orthogonal zones
- ✅ **Enforcement Subdirs:** 9 → 4 (attestation, audit, evidence, eval)
- ✅ **APEX Governance:** 9 files → 3 files (governance only)
- ✅ **Clear Floor Ownership:** Each floor has ONE canonical implementation
- ✅ **Test Suite:** 100% passing after migration
- ✅ **Documentation:** ARCHITECTURE.md updated with new structure

---

## Constitutional Compliance

### Floors Checked:
- ✅ **F1 (Truth):** Based on PRIMARY source (AGENTS.md v46 architecture)
- ✅ **F2 (ΔS):** Reduces confusion (clear zones vs mixed enforcement/)
- ✅ **F6 (Amanah):** Reversible (file moves via git, can revert)
- ✅ **F7 (RASA):** Listened to user request for organization
- ✅ **F9 (Anti-Hantu):** No consciousness, structural analysis only

### Verdict: SEAL
**Reason:** Architecture proposal aligns with v46 Trinity Orthogonal principles. Clear separation, no duplication, constitutional floor ownership mapped.

---

**DITEMPA BUKAN DIBERI** — Architecture forged from constitutional principles.

**Architect:** Claude Code (Ω - Engineer)
**Authority:** AGENTS.md v46, L2_PROTOCOLS/v46/constitutional_floors.json
**Sealed:** 2026-01-12
