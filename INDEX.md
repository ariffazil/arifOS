# arifOS · Project Index (live map)

**Epoch:** v35Ω (runtime law) / v36Ω (physics docs) · **Last updated:** 2025-12-05

---

## /canon ← authoritative specs (live)

### Flat v35Ω Runtime Law (binding)
- `000_ARIFOS_CANON_v35Omega.md` — *LIVE* · overview of "what is arifOS?"
- `000_CANON_FLAT_MAPPING_v35Omega.md` — *LIVE* · flat canon index
- `001_APEX_META_CONSTITUTION_v35Omega.md` — *LIVE* · meta-constitution, 7Q resolution
- `002_APEX_TRINITY_v35Omega.md` — *SEALED* · AAA Trinity (ARIF/ADAM/APEX PRIME)
- `010_DeltaOmegaPsi_UNIFIED_FIELD_v35Omega.md` — *LIVE* · ΔΩΨ unified field
- `011_ZKPC_PROTOCOL_v35Omega.md` — *LIVE* · Zero-Knowledge Proof of Cooling
- `020_ANTI_HANTU_v35Omega.md` — *SEALED* · Anti-Hantu protocol (F9)
- `021_ANTI_HANTU_SUPPLEMENT_v35Omega.md` — *SEALED* · Anti-Hantu supplement
- `030_EYE_SENTINEL_v35Omega.md` — *LIVE* · @EYE Sentinel 10+1 views
- `100_AAA_ENGINES_SPEC_v35Omega.md` — *LIVE* · AAA Engines specification
- `120_EUREKA_CUBE_FIELD_SPEC_v35Omega.md` — *DRAFT* · Eureka Cube field spec
- `200_ARIFOS_GOVERNANCE_KERNEL_FOR_LLMS_v35Omega.md` — *LIVE* · LLM governance kernel
- `880_000-999_METABOLIC_CANON_v35Omega.md` — *SEALED* · 000→999 metabolic spine
- `888_APEX_PRIME_CANON_v35Omega.md` — *SEALED* · judiciary canon (floors, verdicts, CCE)
- `99__README_Vault999_v35Omega.md` — *LIVE* · Vault-999 documentation
- `99_Vault999_Seal_v35Omega.json` — *SEALED* · Vault-999 constitutional store

### v36Ω Physics/Architecture Docs (non-binding, explanatory)
- `01_PHYSICS/APEX_THEORY_PHYSICS_v36Omega.md` — *LIVE* · thermodynamic physics
- `01_PHYSICS/APEX_THEORY_MATH_v36Omega.md` — *LIVE* · mathematical formalism
- `01_PHYSICS/APEX_LANGUAGE_CODEX_v36Omega.md` — *LIVE* · language codex
- `05_MASTER/APEX_THEORY_MASTER_CANON_v36Omega.md` — *DRAFT* · master theory canon
- `10_SYSTEM/111_ARIF_AGI_v36Omega.md` — *LIVE* · ARIF AGI specification
- `10_SYSTEM/333_AAA_ENGINES_v36Omega.md` — *LIVE* · AAA Engines v36Ω spec
- `10_SYSTEM/555_ADAM_ASI_v36Omega.md` — *LIVE* · ADAM ASI specification
- `10_SYSTEM/AAA_TRINITY_CANON_v36Omega.md` — *DRAFT* · AAA Trinity canon v36Ω
- `20_EXECUTION/WAW_FEDERATION_v36Omega.md` — *LIVE* · W@W Federation spec
- `30_RUNTIME/APEX_RUNTIME_PIPELINE_v36Omega.md` — *LIVE* · runtime pipeline spec
- `40_LEDGER/APEX_LEDGER_PHOENIX_v36Omega.md` — *LIVE* · ledger/Phoenix-72 spec

### Auxiliary Canon
- `00_CANON/APEX_GRADIENT_v35Omega.md` — *DRAFT* · gradient spec
- `00_CANON/APEX_DOCUMENT_TEMPLATE_v35Omega.md` — *LIVE* · document template
- `00_CANON/ARIFOS_EUREKA_ARCHIVE_v35Omega.md` — *DRAFT* · eureka archive
- `00_CANON/ATLAS_33_PERSONA_ARIF_v35Omega.md` — *DRAFT* · Atlas 33 persona
- `00_CANON/PP_PS_WAVE_CODEX_v35Omega.md` — *DRAFT* · wave codex
- `01_TEMPLATES/APEX_ARTIFACT_SKELETON.md` — *LIVE* · artifact template

---

## /spec ← implementable specs (dev-facing)

- `arifos_runtime_manifest_v35Omega.yaml` — *SEALED* · canonical runtime manifest (YAML)
- `arifos_runtime_manifest_v35Omega.json` — *SEALED* · canonical runtime manifest (JSON)
- `arifos_runtime_v35Omega.yaml` — *LIVE* · runtime configuration
- `APEX_PRIME.md` — *LIVE* · APEX PRIME specification
- `APEX_PRIME.yaml` — *LIVE* · APEX PRIME machine-readable
- `VAULT_999.md` — *LIVE* · Vault-999 specification
- `PHOENIX_72.md` — *LIVE* · Phoenix-72 amendment engine
- `WITNESS_L3.md` — *LIVE* · Witness L3 specification
- `cooling_ledger.schema.json` — *SEALED* · cooling ledger JSON schema
- `Cooling_Ledger_Entry.json` — *LIVE* · ledger entry example
- `AMENDMENT.json` — *LIVE* · amendment template

---

## /arifos_core ← code (runtime)

### Core Modules
- `__init__.py` — v35.12.0 · package init, exports
- `APEX_PRIME.py` — v35.12.0 · constitutional judiciary (floors, verdicts)
- `metrics.py` — v35.12.0 · floor thresholds + check functions
- `guard.py` — v35.12.0 · @apex_guardrail decorator
- `pipeline.py` — v35.12.0 · 000→999 metabolic pipeline, Class A/B routing
- `llm_interface.py` — v35.12.0 · LLM streaming + entropy monitoring
- `runtime_manifest.py` — v35.12.0 · manifest loader + dynamic imports
- `eye_sentinel.py` — v35.12.0 · @EYE Sentinel (legacy interface)
- `ignition.py` — v35.12.0 · ignition profiles
- `kms_signer.py` — v35.12.0 · KMS signing utilities
- `ledger.py` — v35.12.0 · ledger utilities (legacy)

### engines/ (AAA Engines)
- `engines/__init__.py` — v35.12.0 · AAA facade exports
- `engines/arif_engine.py` — v35.12.0 · ARIF Δ (Mind/Cold Logic)
- `engines/adam_engine.py` — v35.12.0 · ADAM Ω (Heart/Warm Logic)
- `engines/apex_engine.py` — v35.12.0 · APEX PRIME Ψ (Judiciary)

### waw/ (W@W Federation)
- `waw/__init__.py` — v35.12.0 · federation exports
- `waw/base.py` — v35.12.0 · base organ class
- `waw/federation.py` — v35.12.0 · federation coordinator
- `waw/well.py` — v35.12.0 · @WELL - somatic safety
- `waw/rif.py` — v35.12.0 · @RIF - logic/clarity
- `waw/wealth.py` — v35.12.0 · @WEALTH - integrity (absolute veto)
- `waw/geox.py` — v35.12.0 · @GEOX - physics/reality
- `waw/prompt.py` — v35.12.0 · @PROMPT - language/culture

### eye/ (@EYE Sentinel)
- `eye/__init__.py` — v35.12.0 · sentinel exports
- `eye/base.py` — v35.12.0 · base view class, EyeAlert, EyeReport
- `eye/sentinel.py` — v35.12.0 · EyeSentinel coordinator
- `eye/trace_view.py` — v35.12.0 · logical coherence
- `eye/floor_view.py` — v35.12.0 · floor proximity
- `eye/shadow_view.py` — v35.12.0 · jailbreak detection
- `eye/drift_view.py` — v35.12.0 · hallucination detection
- `eye/maruah_view.py` — v35.12.0 · dignity checks
- `eye/paradox_view.py` — v35.12.0 · contradiction detection
- `eye/silence_view.py` — v35.12.0 · mandatory refusal
- `eye/version_view.py` — v35.12.0 · version verification
- `eye/behavior_drift_view.py` — v35.12.0 · multi-turn drift
- `eye/sleeper_view.py` — v35.12.0 · identity shift detection
- `eye/anti_hantu_view.py` — v35.12.0 · F9 enforcement

### memory/ (Memory Subsystems)
- `memory/cooling_ledger.py` — v35.12.0 · L1: hash-chained audit log
- `memory/vault999.py` — v35.12.0 · L0: constitutional store
- `memory/phoenix72.py` — v35.12.0 · L2: amendment engine (72h cycle)
- `memory/scars.py` — v35.12.0 · scar memory (negative constraints)
- `memory/void_scanner.py` — v35.12.0 · VOID pattern detection
- `memory/vector_adapter.py` — v35.12.0 · vector store adapter

### adapters/ (LLM Backends)
- `adapters/__init__.py` — v35.12.0 · adapter exports
- `adapters/llm_sealion.py` — v35.12.0 · SEA-LION (local GPU)
- `adapters/llm_openai.py` — v35.12.0 · OpenAI API
- `adapters/llm_claude.py` — v35.12.0 · Anthropic Claude API
- `adapters/llm_gemini.py` — v35.12.0 · Google Gemini API

---

## /runtime ← ops, receipts, ledger

- `constitution.json` — v35Ω · runtime constitution snapshot
- `cooling_ledger.jsonl` — rolling · hash-chained audit trail

---

## /scripts ← CLI tools

- `arifos_caged_llm_demo.py` — v35.12.0 · Caged LLM harness for Colab
- `verify_ledger_kms.py` — v35.12.0 · KMS ledger verification

---

## /tests ← test suite (412 tests)

Core test files covering floors, pipeline, engines, W@W, @EYE, ledger, adapters, runtime manifest.

---

## /examples ← Big 3 Framework Integrations

- `autogen_arifos_governor/` — *LIVE* · AutoGen W@W Federation (12 tests)
- `llamaindex_arifos_truth/` — *LIVE* · LlamaIndex RAG Governor (10 tests)
- `langchain_arifos_guarded/` — *LIVE* · LangChain Governor (10 tests)

---

## /notebooks ← Colab Demos

- `arifos_v35_sealion_demo.ipynb` — *LIVE* · SEA-LION + full pipeline (GPU)
- `arifos_v35_max_context_demo.ipynb` — *LIVE* · API LLM demo
- `arifOS_Level3_QwenSEALION_v35.ipynb` — *DRAFT* · Qwen SEA-LION experiment

---

## /integrations ← External Integrations

- `sealion/` — *LIVE* · SEA-LION integration
  - `arifos_sealion.py` — adapter module
  - `constitutional_floors.json` — floor thresholds for SEA-LION
  - `arifos_pipeline.yaml` — pipeline configuration

---

## Root Files

- `README.md` — *LIVE* · main documentation with Mermaid diagram
- `CLAUDE.md` — *LIVE* · Claude Code constitutional governance
- `CHANGELOG.md` — *LIVE* · version history
- `CONTRIBUTING.md` — *LIVE* · contribution guidelines
- `SECURITY.md` — *LIVE* · security policy
- `constitutional_floors.json` — *SEALED* · machine-readable floor thresholds
- `pyproject.toml` — v35.12.0 · package configuration

---

## Sealed Epochs

| Layer | Epoch/Version | Status |
|-------|---------------|--------|
| **Canon** | v35Ω (runtime law) + v36Ω (physics docs) | Mixed |
| **Spec** | v35Ω | Rolling |
| **Core** | v35.12.0 | Production |
| **Runtime** | v35Ω | Active |

---

## Drift Watchlist

1. **`constitutional_floors.json` ↔ `metrics.py` sync** — floor thresholds in JSON must match Python constants; test_runtime_manifest.py guards this
2. **`spec/arifos_runtime_manifest_v35Omega.yaml` ↔ actual module paths** — manifest references modules that must exist and be importable
3. **v35Ω vs v36Ω canon overlap** — `canon/10_SYSTEM/333_AAA_ENGINES_v36Omega.md` vs `canon/100_AAA_ENGINES_SPEC_v35Omega.md` need reconciliation
4. **`integrations/sealion/constitutional_floors.json` ↔ root `constitutional_floors.json`** — must stay synchronized
5. **`arifos_core/eye_sentinel.py` (legacy) vs `arifos_core/eye/sentinel.py` (modular)** — legacy interface should delegate to modular implementation

---

*Generated: 2025-12-05 · arifOS v35.12.0 · 412 tests passing*
