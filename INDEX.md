# arifOS Repository Index

```
+=============================================================================+
|  arifOS v35Ω Repository Index                                              |
|  "Ditempa Bukan Diberi" — Forged, Not Given                                |
|  Last Updated: 2025-12-05                                                  |
+=============================================================================+
|  Version: v35.1.0 (Epoch 35Ω) | Transitioning to v36Ω                      |
|  Status: PRODUCTION | Tests: 412+ passing                                  |
+=============================================================================+
```

## Quick Navigation

- [Folder Structure](#folder-structure)
- [Canon Files](#canon-files-constitutional-specs)
- [Spec Files](#spec-files-machine-readable)
- [Core Implementation](#core-implementation-arifos_core)
- [Runtime & Ledger](#runtime--ledger)
- [Examples & Integrations](#examples--integrations)
- [Tests](#tests)
- [Epoch Blocks](#epoch-blocks)
- [Drift Watchlist](#drift-watchlist-top-5-desync-risks)
- [Version Notes](#version-notes)
- [Cleanup Tasks](#cleanup-tasks)

---

## Folder Structure

```
arifOS/
├── canon/                     # Constitutional specifications (v35Ω/v36Ω)
│   ├── 00_CANON/             # Core constitutional docs & APEX THEORY
│   ├── 01_PHYSICS/           # Physics & math foundations (v36Ω)
│   ├── 01_TEMPLATES/         # Document templates
│   ├── 05_MASTER/            # Master canon (v36Ω)
│   ├── 10_SYSTEM/            # AAA Engines (ARIF/ADAM/APEX) (v36Ω)
│   ├── 20_EXECUTION/         # W@W Federation (v36Ω)
│   ├── 30_RUNTIME/           # Runtime pipeline (v36Ω)
│   ├── 40_LEDGER/            # Ledger & Phoenix protocols (v36Ω)
│   └── *.md, *.json          # Root-level canons (v35Ω)
│
├── spec/                      # Machine-readable specifications
│   ├── *.json                # JSON schemas
│   ├── *.yaml                # YAML configs
│   └── *.md                  # Spec documentation
│
├── arifos_core/              # Python runtime implementation
│   ├── APEX_PRIME.py         # Judiciary engine
│   ├── adapters/             # LLM adapters (OpenAI, Anthropic, etc.)
│   ├── engines/              # AAA engines (arif_engine.py, adam_engine.py)
│   ├── eye/                  # @EYE Sentinel (10 views)
│   ├── memory/               # Cooling Ledger
│   ├── waw/                  # W@W Federation organs
│   └── *.py                  # Core modules (metrics, pipeline, guard)
│
├── runtime/                   # Ledger & receipts
│   ├── cooling_ledger.jsonl  # Audit trail (append-only)
│   └── constitution.json     # Runtime constitution
│
├── examples/                  # Framework integrations & demos
│   ├── autogen_arifos_governor/
│   ├── langchain_arifos_guarded/
│   ├── langgraph_minimal/
│   ├── llamaindex_arifos_truth/
│   ├── openai_agents_minimal/
│   └── *.py                  # Standalone demos
│
├── tests/                     # Test suite (pytest)
│   └── test_*.py             # 190+ test files
│
├── docs/                      # Documentation
├── integrations/             # External integrations (sealion, etc.)
├── scripts/                  # Utility scripts
├── notebooks/                # Jupyter notebooks
├── archive/                  # Deprecated versions
│
├── constitutional_floors.json # Floor definitions (9 floors)
├── pyproject.toml            # Package metadata
├── README.md                 # Main docs
├── CLAUDE.md                 # Claude Code governance
├── GOVERNANCE.md             # Governance docs
└── INDEX.md                  # This file
```

---

## Canon Files (Constitutional Specs)

### Root-Level Canons (v35Ω) - **SEALED**

| File | Status | Description |
|------|--------|-------------|
| `000_ARIFOS_CANON_v35Omega.md` | **SEALED** | Master arifOS canon v35Ω |
| `000_CANON_FLAT_MAPPING_v35Omega.md` | **SEALED** | Flat mapping reference |
| `001_APEX_META_CONSTITUTION_v35Omega.md` | **SEALED** | Meta-constitutional framework |
| `002_APEX_TRINITY_v35Omega.md` | **SEALED** | APEX Trinity foundation |
| `010_DeltaOmegaPsi_UNIFIED_FIELD_v35Omega.md` | **SEALED** | ΔΩΨ unified field physics |
| `011_ZKPC_PROTOCOL_v35Omega.md` | **SEALED** | Zero-Knowledge Proof of Conscience |
| `020_ANTI_HANTU_v35Omega.md` | **SEALED** | Anti-Hantu protocol (Floor 9) |
| `021_ANTI_HANTU_SUPPLEMENT_v35Omega.md` | **SEALED** | Anti-Hantu supplement |
| `030_EYE_SENTINEL_v35Omega.md` | **SEALED** | @EYE Sentinel specification (10 views) |
| `100_AAA_ENGINES_SPEC_v35Omega.md` | **SEALED** | AAA Engines specification |
| `120_EUREKA_CUBE_FIELD_SPEC_v35Omega.md` | **SEALED** | Eureka Cube field spec |
| `200_ARIFOS_GOVERNANCE_KERNEL_FOR_LLMS_v35Omega.md` | **SEALED** | LLM governance kernel |
| `880_000-999_METABOLIC_CANON_v35Omega.md` | **SEALED** | Metabolic pipeline canon (000-999) |
| `888_APEX_PRIME_CANON_v35Omega.md` | **SEALED** | APEX PRIME judiciary canon |
| `99_Vault999_Seal_v35Omega.json` | **SEALED** | Vault999 seal (constitutional snapshot) |
| `99__README_Vault999_v35Omega.md` | **SEALED** | Vault999 documentation |
| `README.md` | **LIVE** | Canon directory overview |

### 00_CANON/ - Core Constitutional Documents

| File | Status | Description |
|------|--------|-------------|
| `APEX_DOCUMENT_TEMPLATE_v35Omega.md` | **SEALED** | Standard document template |
| `APEX_GRADIENT_v35Omega.md` | **SEALED** | APEX gradient specification |
| `APEX_THEORY_GENESIS_v36Omega.md` | **LIVE** | APEX Theory genesis (v36Ω) |
| `ARIFOS_EUREKA_ARCHIVE_v35Omega.md` | **SEALED** | Eureka Archive |
| `ATLAS_33_PERSONA_ARIF_v35Omega.md` | **SEALED** | ATLAS-33 persona definition |
| `ATLAS_33_SCHEMA_v1.md` | **SEALED** | ATLAS-33 schema |
| `PP_PS_WAVE_CODEX_v35Omega.md` | **SEALED** | PP/PS wave codex |

#### 00_CANON/APEX THEORY/ (Supporting Research)

| File | Status | Description |
|------|--------|-------------|
| `APEX THEORY CANON 36.md` | **LIVE** | APEX Theory v36 reference |
| `APEX_THEORY_PHYSICS_v36Omega.md.pdf` | **LIVE** | Physics foundation PDF |
| `Deep Research Report_ Operationalizing Thermodynamic Cognition.pdf` | **LIVE** | Deep research artifact |
| `_APEX THEORY v36Ω .pdf` | **LIVE** | APEX Theory v36Ω master PDF |

### 01_PHYSICS/ - Physics & Math Foundations (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `APEX_LANGUAGE_CODEX_v36Omega.md` | **LIVE** | Language codex v36Ω |
| `APEX_THEORY_MATH_v36Omega.md` | **LIVE** | Mathematical foundations |
| `APEX_THEORY_PHYSICS_v36Omega.md` | **LIVE** | Physics foundations |

### 01_TEMPLATES/ - Document Templates

| File | Status | Description |
|------|--------|-------------|
| `APEX_ARTIFACT_SKELETON.md` | **SEALED** | Artifact skeleton template |
| `README.md` | **LIVE** | Templates documentation |

### 05_MASTER/ - Master Canon (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `APEX_THEORY_MASTER_CANON_v36Omega.md` | **LIVE** | Master canon v36Ω |

### 10_SYSTEM/ - AAA Engines (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `111_ARIF_AGI_v36Omega.md` | **LIVE** | ARIF AGI specification |
| `333_AAA_ENGINES_v36Omega.md` | **LIVE** | AAA Engines unified spec |
| `555_ADAM_ASI_v36Omega.md` | **LIVE** | ADAM ASI specification |
| `AAA_TRINITY_CANON_v36Omega.md` | **LIVE** | AAA Trinity canon |

### 20_EXECUTION/ - W@W Federation (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `WAW_FEDERATION_v36Omega.md` | **LIVE** | W@W Federation specification |

### 30_RUNTIME/ - Runtime Pipeline (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `APEX_RUNTIME_PIPELINE_v36Omega.md` | **LIVE** | Runtime pipeline spec |

### 40_LEDGER/ - Ledger & Phoenix (v36Ω) - **LIVE**

| File | Status | Description |
|------|--------|-------------|
| `APEX_LEDGER_PHOENIX_v36Omega.md` | **LIVE** | Ledger & Phoenix-72 protocol |

---

## Spec Files (Machine-Readable)

| File | Status | Description |
|------|--------|-------------|
| `AMENDMENT.json` | **SEALED** | Amendment protocol schema |
| `APEX_PRIME.md` | **SEALED** | APEX PRIME specification |
| `APEX_PRIME.yaml` | **SEALED** | APEX PRIME YAML config |
| `Cooling_Ledger_Entry.json` | **SEALED** | Cooling Ledger entry schema |
| `PHOENIX_72.md` | **SEALED** | Phoenix-72 protocol spec |
| `VAULT_999.md` | **SEALED** | Vault999 specification |
| `WITNESS_L3.md` | **SEALED** | L3 Witness protocol |
| `arifos_runtime_manifest_v35Omega.json` | **SEALED** | Runtime manifest (JSON) |
| `arifos_runtime_manifest_v35Omega.yaml` | **SEALED** | Runtime manifest (YAML) |
| `arifos_runtime_v35Omega.yaml` | **SEALED** | Runtime config v35Ω |
| `cooling_ledger.schema.json` | **SEALED** | Ledger schema definition |

---

## Core Implementation (arifos_core/)

### Root Modules

| File | Status | Description |
|------|--------|-------------|
| `APEX_PRIME.py` | **LIVE** | Judiciary engine (9 floors, verdicts) |
| `__init__.py` | **LIVE** | Package initialization |
| `guard.py` | **LIVE** | Constitutional guard |
| `ignition.py` | **LIVE** | Ignition profiles |
| `kms_signer.py` | **LIVE** | KMS signing integration |
| `ledger.py` | **LIVE** | Ledger utilities |
| `llm_interface.py` | **LIVE** | LLM interface abstraction |
| `metrics.py` | **LIVE** | Metrics computation |
| `pipeline.py` | **LIVE** | Pipeline orchestration |
| `runtime_manifest.py` | **LIVE** | Runtime manifest loader |
| `eye_sentinel.py` | **LIVE** | @EYE Sentinel coordinator |

### adapters/ - LLM Adapters

| Subdirectory | Description |
|--------------|-------------|
| `adapters/` | OpenAI, Anthropic, Azure, HuggingFace, Ollama adapters |

### engines/ - AAA Engines

| File | Status | Description |
|------|--------|-------------|
| `arif_engine.py` | **LIVE** | ARIF AGI engine (Δ - Mind/Logic) |
| `adam_engine.py` | **LIVE** | ADAM ASI engine (Ω - Heart/Empathy) |

### eye/ - @EYE Sentinel (10 Views)

| File | Status | View # | Description |
|------|--------|--------|-------------|
| `sentinel.py` | **LIVE** | - | @EYE coordinator |
| `trace_view.py` | **LIVE** | 1 | Trace view (logical coherence) |
| `floor_view.py` | **LIVE** | 2 | Floor view (threshold proximity) |
| `shadow_view.py` | **LIVE** | 3 | Shadow view (jailbreak detection) |
| `drift_view.py` | **LIVE** | 4 | Drift view (hallucination) |
| `maruah_view.py` | **LIVE** | 5 | Maruah view (dignity/respect) |
| `paradox_view.py` | **LIVE** | 6 | Paradox view (logical contradiction) |
| `silence_view.py` | **LIVE** | 7 | Silence view (mandatory refusal) |
| `version_view.py` | **LIVE** | 8 | Version/Ontology view (v35Ω active) |
| `behavior_drift_view.py` | **LIVE** | 9 | Behavior drift view (multi-turn evolution) |
| `sleeper_view.py` | **LIVE** | 10 | Sleeper-agent view (identity shift) |
| `anti_hantu_view.py` | **LIVE** | - | Anti-Hantu enforcement (F9) |
| `base.py` | **LIVE** | - | View base class |

**Note:** All 10 canonical views implemented ✓

### memory/ - Cooling Ledger

| Subdirectory | Description |
|--------------|-------------|
| `memory/` | Cooling Ledger implementation (append-only audit trail) |

### waw/ - W@W Federation Organs

| File | Status | Organ | Description |
|------|--------|-------|-------------|
| `federation.py` | **LIVE** | - | W@W coordinator |
| `base.py` | **LIVE** | - | Organ base class |
| `well.py` | **LIVE** | @WELL | Somatic safety / tone (F3, F4, F7) |
| `rif.py` | **LIVE** | @RIF | Logic / clarity / ΔS (F1, F2, F5) |
| `wealth.py` | **LIVE** | @WEALTH | Justice / maruah / Amanah (F6, F3) |
| `geox.py` | **LIVE** | @GEOX | Physics / Earth / reality (F1, F8) |
| `prompt.py` | **LIVE** | @PROMPT | Language & optics (F9, F7) |

**Note:** 5 canonical W@W organs implemented ✓ (9 total organ classes include base variations)

---

## Runtime & Ledger

| File | Status | Description |
|------|--------|-------------|
| `runtime/cooling_ledger.jsonl` | **LIVE** | Append-only audit trail |
| `runtime/constitution.json` | **LIVE** | Runtime constitution snapshot |
| `constitutional_floors.json` | **SEALED** | 9 constitutional floors definition (root) |

---

## Examples & Integrations

### Standalone Examples

| File | Description |
|------|-------------|
| `01_basic_metabolism.py` | Basic metabolic demo |
| `02_full_apex_runtime_demo.py` | Full APEX runtime demo |
| `03_governed_conversation_demo.py` | Governed conversation |
| `04_xos_identity_switch_demo.py` | Identity switch demo |
| `05_vault999_basic.py` | Vault999 basic demo |
| `06_vector_witness_demo.py` | Vector witness demo |
| `07_zkpc_demo.py` | ZKPC protocol demo |
| `08_smoke_test_guardrail.py` | Smoke test guardrail |
| `09_pipeline_skeleton.py` | Pipeline skeleton |
| `10_pipeline_with_openai.py` | OpenAI integration |
| `11_pipeline_with_claude.py` | Claude integration |
| `governed_claude_demo.py` | Governed Claude demo |
| `live_governance_demo.py` | Live governance demo |
| `compute_metrics_stub.py` | Metrics computation stub |
| `seed_scars.py` | Seed scars demo |

### Framework Integrations

| Directory | Framework | Description |
|-----------|-----------|-------------|
| `autogen_arifos_governor/` | AutoGen | AutoGen W@W federation |
| `autogen_minimal/` | AutoGen | Minimal AutoGen integration |
| `langchain_arifos_guarded/` | LangChain | LangChain governance |
| `langgraph_minimal/` | LangGraph | Minimal LangGraph integration |
| `llamaindex_arifos_truth/` | LlamaIndex | RAG truth governor |
| `openai_agents_minimal/` | OpenAI Agents | Minimal OpenAI agents |

---

## Tests

**Total:** 190+ test files | **Status:** 412+ tests passing

### Key Test Suites

| Test File | Coverage Area |
|-----------|---------------|
| `test_apex_prime_floors.py` | APEX PRIME floors (F1-F9) |
| `test_apex_prime_floors_mocked.py` | Floors (mocked) |
| `test_anti_hantu_f9.py` | Anti-Hantu protocol (F9) |
| `test_apex_and_ledger_edges.py` | APEX + Ledger edge cases |
| `test_apex_review.py` | APEX review logic |
| `test_caged_llm_harness.py` | Caged LLM harness |
| `test_canon_drift_guard.py` | Canon drift guard |
| `test_cooling_ledger.py` | Cooling Ledger |
| `test_cooling_ledger_integrity.py` | Ledger integrity |
| `test_cooling_ledger_kms_integration.py` | KMS integration |
| `test_cooling_ledger_schema_compliance.py` | Schema compliance |
| `test_engines_arif_adam.py` | ARIF/ADAM engines |
| `test_eye_sentinel.py` | @EYE Sentinel |
| `test_guard_v35.py` | Constitutional guard |
| `test_ignition_profiles.py` | Ignition profiles |
| `test_kms_signer.py` | KMS signer |
| `test_ledger_sanity.py` | Ledger sanity checks |
| `test_llm_adapters.py` | LLM adapters |
| `test_phoenix72.py` | Phoenix-72 protocol |
| `test_pipeline_routing.py` | Pipeline routing |
| `test_pipeline_stages_444_555_666.py` | Pipeline stages |
| `test_runtime_manifest.py` | Runtime manifest |
| `test_v35_features.py` | v35Ω features |
| `test_vector_adapter.py` | Vector adapter |
| `test_waw_organs.py` | W@W organs |

---

## Epoch Blocks

### Canon Epoch (Constitutional Law)

| Version | Status | Description | Files |
|---------|--------|-------------|-------|
| **v35Ω** | **SEALED** (Production) | Current production epoch. All v35Ω canons are stable and frozen. | 17 root canons + subdirectories |
| **v36Ω** | **LIVE** (Active Development) | Next-generation epoch in active development. New physics, AAA engines, W@W, runtime, ledger specs. | 10 canons in subdirectories (01_PHYSICS, 05_MASTER, 10_SYSTEM, 20_EXECUTION, 30_RUNTIME, 40_LEDGER) |

### Spec Epoch (Machine-Readable)

| Version | Status | Description | Files |
|---------|--------|-------------|-------|
| **v35Ω** | **SEALED** | All specs aligned with v35Ω canon. Stable, no breaking changes. | 11 spec files |

### Core Epoch (Python Implementation)

| Version | Status | Description | Coverage |
|---------|--------|-------------|----------|
| **v35.1.0** | **LIVE** (Production) | Current Python package version. Implements v35Ω canon fully. | 190+ files, 412+ tests |

### Runtime Epoch (Ledger & State)

| Component | Version | Status | Description |
|-----------|---------|--------|-------------|
| Cooling Ledger | v35Ω | **LIVE** | Append-only audit trail, schema-compliant |
| Constitutional Floors | v35Ω (9 floors) | **SEALED** | F1-F9 defined in `constitutional_floors.json` |
| Runtime Manifest | v35Ω | **SEALED** | Runtime configuration frozen |

---

## Drift Watchlist (Top 5 Desync Risks)

### 🔴 HIGH PRIORITY

1. **Canon v35Ω → v36Ω Transition**
   - **Risk:** v36Ω canons (physics, AAA, W@W, runtime, ledger) are in LIVE status but not fully integrated into Python core.
   - **Files:** `canon/01_PHYSICS/`, `canon/05_MASTER/`, `canon/10_SYSTEM/`, `canon/20_EXECUTION/`, `canon/30_RUNTIME/`, `canon/40_LEDGER/`
   - **Impact:** Drift between canonical spec (v36Ω) and implementation (v35.1.0)
   - **Action:** Phase 4 integration required. Track with Phoenix-72 protocol.

2. **Duplicate ADAM ASI Files**
   - **Risk:** Two ADAM ASI canonical files exist, potential version conflict.
   - **Files:** 
     - `docs/AGI ASI/ARIF AGI ADAM ASI CANON v36.txt`
     - `canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md`
   - **Impact:** Ambiguity in ADAM specification, potential implementation drift.
   - **Action:** Consolidate into single canonical source (recommend: `canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md`). Archive or remove `docs/AGI ASI/` version.

3. **Floor File Naming Convention**
   - **Risk:** Unclear if `FLOORS_v35Ω.json` ever existed or if `constitutional_floors.json` is the sole source of truth.
   - **Files:** 
     - `constitutional_floors.json` (exists, contains 9 floors)
     - `FLOORS_v35Ω.json` (referenced but not found)
     - `integrations/sealion/constitutional_floors.json` (duplicate copy)
   - **Impact:** Potential floor definition drift if multiple sources exist.
   - **Action:** Confirm `constitutional_floors.json` as single source of truth. Remove or clarify `integrations/sealion/constitutional_floors.json` (integration-specific copy?).

### 🟡 MEDIUM PRIORITY

4. **@EYE Sentinel View Overimplementation**
   - **Risk:** 14 view files implemented (10 canonical + 4 extra: anti_hantu_view, base, sentinel coordinator, extras).
   - **Files:** 
     - Canonical: 10 views per `canon/030_EYE_SENTINEL_v35Omega.md`
     - Implemented: 14 files in `arifos_core/eye/`
   - **Impact:** Extra views (`anti_hantu_view.py`) may be justified (F9 enforcement), but should be documented as extension, not canonical view.
   - **Action:** Clarify in docs which views are canonical (1-10) vs. extensions. Update `@EYE` spec if extensions are now canonical.

5. **W@W Organ Count Discrepancy**
   - **Risk:** 9 Organ classes in code vs. 5 canonical organs in spec.
   - **Files:** 
     - Canonical: 5 organs per `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` (@WELL, @RIF, @WEALTH, @GEOX, @PROMPT)
     - Implemented: 9 Organ classes in `arifos_core/waw/`
   - **Impact:** Unclear if extra organ classes are base classes, variations, or extensions.
   - **Action:** Document organ class hierarchy. Clarify which are canonical organs vs. base/helper classes.

---

## Version Notes

### v35Ω (Epoch 35 - SEALED)

**Status:** PRODUCTION (SEALED)  
**Package Version:** v35.1.0  
**Description:** Current production epoch. All v35Ω canons are stable and frozen.

**Key Features:**
- 9 Constitutional Floors (F1-F9)
- APEX PRIME Judiciary (SEAL/PARTIAL/888_HOLD/VOID/SABAR verdicts)
- ΔΩΨ Unified Field (Delta-Omega-Psi physics)
- @EYE Sentinel (10 views)
- W@W Federation (5 organs)
- AAA Engines (ARIF/ADAM/APEX)
- Cooling Ledger (append-only audit trail)
- Phoenix-72 Protocol (constitutional amendments)
- ZKPC (Zero-Knowledge Proof of Conscience)
- Anti-Hantu Protocol (F9)
- Vault999 Seal

**v35Ω Canons:** 17 root-level canonical files + subdirectories (00_CANON, 01_TEMPLATES)

### v36Ω (Epoch 36 - LIVE)

**Status:** ACTIVE DEVELOPMENT (LIVE)  
**Package Version:** Not yet released (target: v36.0.0)  
**Description:** Next-generation epoch in active development. Major updates to physics, AAA engines, W@W, runtime, ledger.

**Key Changes:**
- Enhanced APEX Theory (physics, math, language codex)
- AAA Trinity Canon (unified ARIF/ADAM/APEX spec)
- W@W Federation v36Ω (external governance organs)
- APEX Runtime Pipeline v36Ω
- APEX Ledger Phoenix v36Ω

**v36Ω Canons:** 10 files across subdirectories (01_PHYSICS, 05_MASTER, 10_SYSTEM, 20_EXECUTION, 30_RUNTIME, 40_LEDGER)

**Integration Status:** Canonical specs exist, Python implementation in progress.

### v0.35.x (Python Package)

**Current Release:** v35.1.0  
**Python Support:** >=3.8  
**License:** Apache-2.0

**Recent Changes:**
- v35.1.0: Production release aligned with v35Ω canon
- v35.0.x: Initial v35Ω implementation

**Roadmap:**
- v35.x: Maintain production stability (v35Ω)
- v36.0.0: Full v36Ω integration (Phase 4)

---

## Cleanup Tasks

### 🔴 HIGH PRIORITY

#### 1. Consolidate Duplicate ADAM ASI Files

**Issue:** Two ADAM ASI canonical files exist, creating ambiguity.

**Files:**
- `docs/AGI ASI/ARIF AGI ADAM ASI CANON v36.txt`
- `canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md`

**Action:**
1. Review both files for content differences
2. Consolidate into single canonical source: `canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md`
3. Archive or remove `docs/AGI ASI/ARIF AGI ADAM ASI CANON v36.txt`
4. Update references in docs/code

**Rationale:** Single source of truth for ADAM ASI specification. Canonical canons belong in `canon/` directory with proper versioning.

#### 2. Clarify Floor File Naming & Sources

**Issue:** Reference to `FLOORS_v35Ω.json` but only `constitutional_floors.json` exists. Duplicate copy in `integrations/sealion/`.

**Files:**
- `constitutional_floors.json` (exists, root directory)
- `integrations/sealion/constitutional_floors.json` (duplicate?)
- `FLOORS_v35Ω.json` (referenced but not found)

**Action:**
1. Confirm `constitutional_floors.json` (root) is single source of truth
2. Document in README/GOVERNANCE.md that canonical floor file is `constitutional_floors.json`
3. Clarify if `integrations/sealion/constitutional_floors.json` is:
   - A necessary integration-specific copy (symlink instead?)
   - A stale duplicate (remove)
4. Remove references to non-existent `FLOORS_v35Ω.json` or create it as canonical name

**Rationale:** Eliminate ambiguity in floor definitions. Prevent drift between multiple floor file sources.

#### 3. Document v36Ω Integration Roadmap

**Issue:** v36Ω canons are LIVE but not fully integrated into Python core (v35.1.0).

**Files:** 10 v36Ω canons in `canon/01_PHYSICS/`, `canon/05_MASTER/`, `canon/10_SYSTEM/`, `canon/20_EXECUTION/`, `canon/30_RUNTIME/`, `canon/40_LEDGER/`

**Action:**
1. Create `ROADMAP_v36Omega.md` with integration plan
2. Define Phase 4 milestones (physics, AAA, W@W, runtime, ledger)
3. Track with Phoenix-72 protocol
4. Target release: v36.0.0

**Rationale:** Prevent canonical drift. Ensure systematic v35Ω → v36Ω transition.

### 🟡 MEDIUM PRIORITY

#### 4. Document @EYE Sentinel View Extensions

**Issue:** 14 view files implemented vs. 10 canonical views. Extensions not documented.

**Files:** `arifos_core/eye/` (14 files: 10 canonical + 4 extra)

**Action:**
1. Update `canon/030_EYE_SENTINEL_v35Omega.md` to clarify:
   - Views 1-10 are canonical
   - `anti_hantu_view.py` is F9 enforcement extension (not a separate view)
   - `base.py`, `sentinel.py` are infrastructure (not views)
2. Add comment in `eye/__init__.py` documenting canonical vs. extension views
3. Consider promoting `anti_hantu_view` to View 11 if it's now canonical

**Rationale:** Clarify which views are canonical vs. implementation details. Prevent confusion.

#### 5. Document W@W Organ Class Hierarchy

**Issue:** 9 Organ classes in code vs. 5 canonical organs in spec.

**Files:** `arifos_core/waw/` (9 classes), `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` (5 organs)

**Action:**
1. Add docstring in `waw/__init__.py` explaining:
   - 5 canonical organs: @WELL, @RIF, @WEALTH, @GEOX, @PROMPT
   - `base.py` is base class (not an organ)
   - `federation.py` is coordinator (not an organ)
   - Other classes: clarify if they are organ variations or deprecated
2. Update `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` if additional organs are now canonical

**Rationale:** Eliminate confusion about W@W organ count. Document implementation structure.

### 🟢 LOW PRIORITY

#### 6. Standardize Canon Filenames

**Issue:** Some canons in `canon/00_CANON/APEX THEORY/` have spaces in filenames.

**Files:** 
- `APEX THEORY CANON 36.md`
- `Deep Research Report_ Operationalizing Thermodynamic Cognition.pdf`
- `_APEX THEORY v36Ω .pdf`

**Action:**
1. Rename files to use underscores or hyphens (e.g., `APEX_THEORY_CANON_36.md`)
2. Ensure no references break

**Rationale:** Consistent naming convention. Avoid shell escaping issues.

#### 7. Archive Deprecated v35 Files

**Issue:** `archive/deprecated_v35/` contains old files. Ensure they're clearly archived.

**Files:** `archive/deprecated_v35/*`

**Action:**
1. Add `archive/deprecated_v35/README.md` explaining what's archived and why
2. Ensure no active code references archived files

**Rationale:** Clear separation between active and deprecated code.

---

## Index Maintenance

**How to Update This Index:**
1. Run file structure scan: `find canon spec arifos_core runtime examples tests -type f`
2. Check file status: SEALED (stable, no changes), LIVE (active development), DRAFT (in progress)
3. Update Drift Watchlist based on version mismatches
4. Increment "Last Updated" date

**Last Updated:** 2025-12-05  
**Maintainer:** arifOS Project  
**License:** Apache-2.0

---

✊ **DITEMPA BUKAN DIBERI** 🔐
