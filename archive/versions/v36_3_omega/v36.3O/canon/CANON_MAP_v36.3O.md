# CANON_MAP v36.3Ω

**Purpose:** Single source of truth for canon-to-code mapping in arifOS v36.3Ω epoch.

**Legend:**
- `v36.3O/canon/` — Canonical v36.3Ω documents (PDFs, normalized names)
- `v36.3O/spec/` — Machine-readable specifications derived from bridges
- `canon/` — Legacy v35Ω/v36Ω markdown canons (still authoritative until migrated)
- `arifos_core/` — Runtime implementation
- `tests/` — Test coverage

---

## 1. PHYSICS

### Canon Files
- `v36.3O/canon/00_PHYSICS/APEX-THEORY-PHYSICS-v36.3O.pdf` — Master physics canon
- **`v36.3O/canon/PHYSICS_APEX_THEORY_PHYSICS_v36.3O.md`** — Bridge/summary file
- `canon/01_PHYSICS/APEX_THEORY_PHYSICS_v36Omega.md` — v36Ω physics (markdown)
- `canon/01_PHYSICS/APEX_THEORY_MATH_v36Omega.md` — Mathematical foundations
- `canon/01_PHYSICS/060_PARADOX_ENGINE_PHYSICS_v36.3Omega.md` — ΔΩΨ paradox cooling physics
- `canon/010_DeltaOmegaPsi_UNIFIED_FIELD_v35Omega.md` — ΔΩΨ unified field theory
- `canon/01_PHYSICS/APEX_GENIUS_LAW_v36Omega.md` — GENIUS LAW specification
- `canon/CIV12_THERMODYNAMICS_v36Omega.md` — CIV-12 Earth witness thermodynamics

### 00_CANON Foundations
PP–PS Wave, Gradient, and EUREKA anchors are captured in 00_CANON and surfaced via the bridge:
- `canon/00_CANON/APEX_THEORY_GENESIS_v36Omega.md` — 3 laws, 9 floors
- `canon/00_CANON/PP_PS_WAVE_CODEX_v35Omega.md` — Full paradox physics
- `canon/00_CANON/APEX_GRADIENT_v35Omega.md` — Governed learning law
- `canon/00_CANON/APEX_EUREKA_INSIGHTS_v36Omega.md` — Interpretive anchors

### Constructs
- **ΔS ≥ 0** — Clarity law (entropy must not increase)
- **Peace² ≥ 1.0** — Stability/non-escalation floor
- **κᵣ ≥ 0.95** — Empathy conductance (weakest stakeholder protection)
- **Ω₀ ∈ [0.03, 0.05]** — Humility band (calibrated uncertainty)
- **Ψ ≥ 1.0** — Vitality threshold (thermodynamic lawfulness)
- **G ≥ 0.80** — Governed intelligence index
- **C_dark < 0.30** — Dark cleverness containment

### Runtime Modules (today)
- `arifos_core/metrics.py` — Floor thresholds, `Metrics` dataclass
- `arifos_core/genius_metrics.py` — G, C_dark, Ψ computation + Truth Polarity
- `arifos_core/APEX_PRIME.py` — Floor enforcement in verdicts

### Tests (today)
- `tests/test_genius_metrics.py`
- `tests/test_apex_prime_floors.py`
- `tests/test_apex_genius_verdicts.py`
- `tests/test_governance_regression.py`

### Specs (v36.3Ω)
- **`v36.3O/spec/measurement_floors_v36.3O.json`** — F1-F9 floor definitions (thresholds, types, domains)
- **`v36.3O/spec/measurement_aggregates_v36.3O.json`** — Δ/Ω/Ψ aggregates, derived metrics, verdict codes

---

## 2. TRINITY (ARIF · ADAM · APEX)

### Canon Files
- `v36.3O/canon/10_TRINITY/ARIF-ADAM-Engine-Canons-v36.3O.pdf` — Combined engine documentation
- **`v36.3O/canon/TRINITY_AAA_ENGINES_v36.3O.md`** — Bridge/summary file
- `canon/10_SYSTEM/111_ARIF_AGI_v36Omega.md` — ARIF AGI (Δ) specification
- `canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md` — ADAM ASI (Ω) specification
- `canon/10_SYSTEM/333_AAA_ENGINES_v36Omega.md` — AAA engine architecture
- `canon/10_SYSTEM/AAA_TRINITY_CANON_v36Omega.md` — Trinity unified canon
- `canon/002_APEX_TRINITY_v35Omega.md` — v35Ω trinity foundations
- `canon/100_AAA_ENGINES_SPEC_v35Omega.md` — Engine specification

### Constructs
- **ARIF (Δ)** — Cold logic engine: sense, reason, align
- **ADAM (Ω)** — Warm logic engine: empathize, bridge, dignity
- **APEX (Ψ)** — Judiciary engine: judge, seal, veto
- **ARIFPacket / ADAMPacket** — Inter-engine data transfer
- **Engine facade pattern** — Zero-break contract

### Runtime Modules (today)
- `arifos_core/engines/arif_engine.py`
- `arifos_core/engines/adam_engine.py`
- `arifos_core/engines/apex_engine.py`
- `arifos_core/engines/__init__.py`

### Tests (today)
- `tests/test_engines_arif_adam.py`
- `tests/test_pipeline_routing.py`

### Specs (v36.3Ω)
- **`v36.3O/spec/trinity_aaa_spec_v36.3O.yaml`** — Engine roles, packets, floor ownership, routing

---

## 3. JUDICIARY (APEX PRIME)

### Canon Files
- `v36.3O/canon/20_JUDICIARY/APEX-PRIME-Master-Canon-v36.3O.txt` — Master judiciary canon
- `v36.3O/canon/20_JUDICIARY/APEX-PRIME-Unified-Knowledge-Artifact-v36.3O.txt` — Knowledge artifact
- `v36.3O/canon/20_JUDICIARY/Apex-Prime-overview-v36.3O.pdf` — Overview document
- **`v36.3O/canon/JUDICIARY_APEX_PRIME_v36.3O.md`** — Bridge/summary file
- `canon/888_APEX_PRIME_CANON_v35Omega.md` — v35Ω judiciary canon
- `canon/APEX_MEASUREMENT_CANON_v36.1Omega.md` — Measurement standards

### Constructs
- **9 Constitutional Floors** — F1-F9 (Amanah, Truth, Tri-Witness, ΔS, Peace², κᵣ, Ω₀, G, C_dark)
- **Verdict hierarchy** — SABAR > VOID > 888_HOLD > PARTIAL > SEAL
- **Hard vs Soft floors** — Hard fail = VOID, Soft fail = PARTIAL
- **Truth Polarity** — Light / Shadow / Weaponized classification
- **888_HOLD triggers** — High-stakes confirmation gates

### Runtime Modules (today)
- `arifos_core/APEX_PRIME.py` — Main judiciary engine
- `arifos_core/metrics.py` — Floor definitions
- `arifos_core/floor_detectors/amanah_risk_detectors.py` — Python-sovereign Amanah

### Tests (today)
- `tests/test_apex_prime_floors.py`
- `tests/test_apex_prime_floors_mocked.py`
- `tests/test_apex_review.py`
- `tests/test_apex_and_ledger_edges.py`
- `tests/test_amanah_detector.py`

### Specs (v36.3Ω)
- **`v36.3O/spec/apex_prime_telemetry_v36.3O.json`** — Telemetry entry schema, floor/aggregate metrics, CCE audits

---

## 4. OVERSIGHT (W@W Federation)

### Canon Files
- `v36.3O/canon/50_OVERSIGHT/W-W-Federation-Five-Organs-v36.3O.pdf` — Five organs specification
- **`v36.3O/canon/OVERSIGHT_WAW_FEDERATION_v36.3O.md`** — Bridge/summary file
- `canon/20_EXECUTION/WAW_FEDERATION_v36Omega.md` — W@W federation canon

### Constructs
- **@WELL** — Somatic safety (Peace², κᵣ)
- **@RIF** — Epistemic rigor (Truth, ΔS)
- **@WEALTH** — Amanah integrity (absolute veto power)
- **@GEOX** — Reality/physics check (Earth witness)
- **@PROMPT** — Language optics (Anti-Hantu, Maruah)
- **Veto hierarchy** — @WEALTH > @WELL > @GEOX > others

### Runtime Modules (today)
- `arifos_core/waw/well.py`
- `arifos_core/waw/rif.py`
- `arifos_core/waw/wealth.py`
- `arifos_core/waw/geox.py`
- `arifos_core/waw/prompt.py`
- `arifos_core/waw/federation.py`
- `arifos_core/waw/bridges/*.py` — Optional external integrations

### Tests (today)
- `tests/test_waw_organs.py`

### Specs (v36.3Ω)
- **`v36.3O/spec/waw_federation_spec_v36.3O.yaml`** — 5 organs, veto hierarchy, vote/veto types, signal schema

---

## 5. PARADOX 777

### Canon Files
- `v36.3O/canon/70_PARADOX/canon_70_PARADOX_700_777_CUBE_CANON_v36.3O.pdf` — 777 Cube paradox canon
- **`v36.3O/canon/PARADOX_777_CUBE_v36.3O.md`** — Bridge/summary file
- `canon/777_CUBE_MASTER_CANON_v36Omega.md` — 777 Cube master canon
- `canon/01_PHYSICS/060_PARADOX_ENGINE_PHYSICS_v36.3Omega.md` — ΔΩΨ paradox cooling physics
- `canon/00_CANON/PP_PS_WAVE_CODEX_v35Omega.md` — Crown Equation (Φᴘ)
- `canon/880_000-999_METABOLIC_CANON_v35Omega.md` — Pipeline stages
- `canon/00_CANON/APEX_EUREKA_INSIGHTS_v36Omega.md` — 12 Permanent Insights
- `spec/PHOENIX_72.md` — Phoenix-72 protocol
- `spec/VAULT_999.md` — Vault-999 architecture

### Constructs
- **777 Cube Geometry** — 3 axes (X=Clarity, Y=Stability, Z=Vitality), 7 layers (L0-L6)
- **Crown Equation (Φᴘ)** — `Φᴘ = (ΔP·Ωᴘ·Ψᴘ·κᵣ·Amanah)/(Lᴘ+Rₘₐ+Λ+ε)`
- **Scar Types** — Δ-scar, Ω-scar, Ψ-scar, Φ-scar
- **Layer Transitions** — Floor-gated state machine (L0→L6)
- **Phoenix-72 Integration** — 72-hour cooling window for scar canonization
- **LAW-777 Entries** — Canonized paradox insights in Vault-999

### Runtime Modules (today)
- `arifos_core/pipeline.py` — `stage_777_forge()`
- `arifos_core/eye/paradox_view.py` — Paradox detection
- `arifos_core/memory/scars.py` — Scar entity and ScarIndex
- `arifos_core/memory/phoenix72.py` — Phoenix-72 scar→amendment workflow
- `arifos_core/memory/cooling_ledger.py` — Scar capture from VOID verdicts
- `arifos_core/memory/vault999.py` — LAW-777 canonization target

### Tests (today)
- `tests/test_phoenix72.py` — Amendment workflow
- `tests/test_apex_and_ledger_edges.py` — Scar-ledger integration
- `tests/test_cooling_ledger.py` — Entry logging
- `tests/test_seal_proposed_canon_v36.py` — Hash chain integrity
- `tests/test_pipeline_stages_444_555_666.py` — Stage transitions
- `tests/test_pipeline_order_v36.py` — 000→999 sequence

### Specs (v36.3Ω)
- **`v36.3O/spec/paradox_777_schema_v36.3O.json`** — Cube geometry, layers, scar types, Crown Equation, state machine

---

## 6. DREAM FORGE

### Canon Files
- `v36.3O/canon/60_DREAMFORGE/Dream-Forge-Architecture-Blueprint-v36.3O.pdf` — Architecture blueprint
- **`v36.3O/canon/DREAMFORGE_ARCHITECTURE_v36.3O.md`** — Bridge/summary file
- `canon/06_PARADOX/061_DREAM_FORGE_PROTOCOL_v36.3Omega.md` — O-TASK protocol canon
- `docs/DREAM_FORGE_LAB_MODE.md` — Lab mode documentation
- `docs/APEX THEORY/Generative Replay for LLM Safety.pdf` — Theory foundation

### Constructs
- **O-TASK Cadence** — O-ALIGN → O-FORGE → O-STRIKE → O-QUENCH
- **Crucible (O-ALIGN)** — Classifies scars into OreType (ANOMALY/PARADOX/FACT/NOISE)
- **Anvil (O-FORGE/STRIKE/QUENCH)** — Generates nightmare variations, tests governance
- **Lab Mode** — Offline-only, not wired to production
- **Non-relaxable floors** — F1 Truth, F6 Amanah, F9 Anti-Hantu never relax

### Runtime Modules (today)
- `arifos_core/dream_forge/__init__.py` — Package exports
- `arifos_core/dream_forge/crucible.py` — `OAlignCrucible`, `OreType`
- `arifos_core/dream_forge/anvil.py` — `OForgeAnvil`
- `scripts/ignite_anvil.py` — CLI runner (lab mode)

### Tests (today)
- `tests/test_dream_forge.py` — Crucible classification, Anvil variation/strike/quench

### Specs (v36.3Ω)
- **`v36.3O/spec/dreamforge_otask_spec_v36.3O.yaml`** — O-TASK cadence, OreType categories, lab-only safety constraints

---

## 7. VAULT-999

### Canon Files
- `v36.3O/canon/80_CCC/VAULT-999-ALL-IN-ONE-v36.3O.pdf` — Complete Vault-999 specification
- **`v36.3O/canon/CCC_ARCHITECTURE_v36.3O.md`** — Bridge/summary file
- **`canon/07_CCC/062_CCC_FINAL_SEAL_PROTOCOL_v36.3Omega.md`** — Final Seal protocol canon
- `canon/VAULT_999_v36Omega.md` — v36Ω Vault-999 design (5-layer architecture)
- `spec/VAULT_999.md` — v35Ω spec (runtime binding)
- `spec/cooling_ledger.schema.json` — v35Ic schema (runtime binding)
- `canon/40_LEDGER/APEX_LEDGER_PHOENIX_v36Omega.md` — Phoenix ledger canon

### Constructs
- **L0 Constitution** — Floors, AAA, APEX rules, version hash
- **L1 Cooling Ledger** — Per-decision metrics, verdicts, hash chain
- **L2 Phoenix-72** — Scars → pattern → law metabolism, Merkle root
- **L3 Witness** — Vector evidence with AREP priority (Earth > Human > AI)
- **L4 zkPC** — Zero-knowledge proofs of cognition, Merkle root
- **Final Seal** — Constitutional gate before L1 write (888_JUDGE → 999_SEAL → L1)
- **Integrity guarantees** — Hash-chaining, append-only, APEX signatures

### Final Seal Requirements
Only SEAL or PARTIAL verdicts may pass through Final Seal to L1:

| Requirement | Specification |
|-------------|---------------|
| **Verdict** | SEAL (all floors pass) or PARTIAL (hard floors pass, soft fail with warning) |
| **Hard Floors** | F1 Truth, F2 ΔS, F5 Ω₀, F6 Amanah, F7 RASA, F8 Tri-Witness, F9 Anti-Hantu must pass |
| **Soft Floors** | F3 Peace², F4 κᵣ may fail (PARTIAL verdict, escalation flag) |
| **Hash Chain** | `entry_hash = SHA256(timestamp + query_hash + response_hash + metrics + verdict + previous_hash)` |
| **APEX Signature** | Required on all L1 entries |
| **Tri-Witness** | >= 0.95 for CLASS_B (high-stakes) |
| **Forbidden Content** | Raw chat, drafts, private data, DeltaS < 0, shadow-truth, soul claims |

### Seal Workflow
```
888_JUDGE → verdict → Final Seal Gate → L1 Write → Merkle Update → zkPC Receipt
     ↓
  VOID/SABAR → Scar Registry (not L1)
  HOLD_888 → Human Confirmation Queue (pending)
```

### Runtime Modules (today)
- `arifos_core/memory/vault999.py` — `Vault999`, `VaultConfig`
- `arifos_core/memory/cooling_ledger.py` — `CoolingLedger`, `CoolingEntry`
- `arifos_core/memory/phoenix72.py` — `Phoenix72`, `PhoenixAmendment`
- `arifos_core/memory/scars.py` — `Scar`, `ScarIndex`
- `arifos_core/ledger_hashing.py` — Hash chain functions
- `arifos_core/merkle.py` — `MerkleTree`
- `arifos_core/zkpc_runtime.py` — `ZKPCReceipt`
- `arifos_core/vault_retrieval.py` — `VaultRetrieval`
- `arifos_core/judge.py` — `ApexPrime.seal()` (Final Seal logic)

### Tests (today)
- `tests/test_cooling_ledger.py` — Entry logging
- `tests/test_cooling_ledger_integrity.py` — Hash chain verification
- `tests/test_cooling_ledger_schema_compliance.py` — v35Ic schema
- `tests/test_phoenix72.py` — Amendment workflow
- `tests/test_seal_proposed_canon_v36.py` — Phoenix-72 seal
- `tests/test_vault_retrieval_v36.py` — L0 access
- `tests/test_final_seal_v36.py` — Final Seal protocol (target)

### Specs (v36.3Ω)
- **`v36.3O/spec/vault999_ledger_schema_v36.3O.json`** — L0-L4 layer schemas, integrity guarantees
- **`v36.3O/spec/vault999_final_seal_spec_v36.3O.json`** — Final Seal requirements, workflow, invariants

---

## 8. GOV / META

### Canon Files
- `v36.3O/canon/90_GOV/THE-9-ESSENTIAL-APEX-THEORY-CANON-FILES-v36O.txt` — Essential canon index
- `v36.3O/canon/90_GOV/Unified-APEX-Theory-Research.pdf` — Unified theory research
- **`v36.3O/canon/GOV_META_v36.3O.md`** — Bridge/summary file
- `canon/000_ARIFOS_CANON_v35Omega.md` — Root arifOS canon
- `canon/001_APEX_META_CONSTITUTION_v35Omega.md` — Meta-constitution
- `canon/880_000-999_METABOLIC_CANON_v35Omega.md` — Metabolic pipeline canon
- `canon/020_ANTI_HANTU_v35Omega.md` — Anti-Hantu law
- `canon/021_ANTI_HANTU_SUPPLEMENT_v35Omega.md` — Anti-Hantu patterns
- `canon/030_EYE_SENTINEL_v35Omega.md` — @EYE Sentinel specification
- `canon/011_ZKPC_PROTOCOL_v35Omega.md` — zkPC protocol

### 00_CANON Foundational Documents
The 00_CANON folder contains meta/seed canon that defines interpretation, paradox law, and gradient law:
- `canon/00_CANON/APEX_THEORY_GENESIS_v36Omega.md` — 3 laws, 9 floors definition
- `canon/00_CANON/PP_PS_WAVE_CODEX_v35Omega.md` — Full paradox physics, Crown Equation
- `canon/00_CANON/APEX_GRADIENT_v35Omega.md` — Governed learning law, scar/gradient mechanics
- `canon/00_CANON/APEX_EUREKA_INSIGHTS_v36Omega.md` — Interpretive anchors (777, IΔIcI, zkPC)
- `canon/00_CANON/ATLAS_33_PERSONA_ARIF_v35Omega.md` — Persona/witness geometry

### Constructs
- **Anti-Hantu** — 50+ forbidden patterns (Malay/English, 4 tiers)
- **SABAR protocol** — Stop-Acknowledge-Breathe-Adjust-Resume
- **000-999 Pipeline** — Metabolic spine (VOID → SEAL)
- **Session Dependency Guard** — Cross-session safety
- **@EYE Sentinel** — 10+ governance views
- **Tri-Witness** — Human · AI · Earth consensus

### Runtime Modules (today)
- `arifos_core/pipeline.py` — 000-999 metabolic pipeline
- `arifos_core/eye/anti_hantu_view.py` — Anti-Hantu detector
- `arifos_core/eye/sentinel.py` — @EYE orchestrator
- `arifos_core/eye/*.py` — Individual views
- `arifos_core/guards/session_dependency.py` — Dependency guard
- `arifos_core/wrappers/governed_session.py` — Session wrapper

### Tests (today)
- `tests/test_anti_hantu_f9.py`
- `tests/test_eye_sentinel.py`
- `tests/test_pipeline_routing.py`
- `tests/test_session_dependency_guard.py`
- `tests/test_governed_session_wrapper.py`
- `tests/test_grey_zone.py`

### Specs (v36.3Ω)
- References `v36.3O/spec/measurement_floors_v36.3O.json` (F9 Anti-Hantu definition)
- References `v36.3O/spec/measurement_aggregates_v36.3O.json` (verdict codes, SABAR protocol)

---

## 9. METABOLIZER LOOP (LLM Integration)

### Canon Files
- **`canon/00_META/050_METABOLIZER_LOOP_v36.3Omega.md`** — Encoder-Decoder-Metabolizer cognitive circuit
- **`canon/00_META/051_METABOLIZER_LOOP_LLM_INTEGRATION_v36.3Omega.md`** — LLM placement and governance

### Constructs
- **Encoder Loop** — Canon → Spec → Code → Output (forward generation)
- **Decoder Loop** — Output → Telemetry → Spec → Canon (reverse audit)
- **Metabolizer Loop** — Canon → 777 → Dream Forge → Phoenix-72 → Canon(vNext) (evolution)
- **LLM as Generator** — Raw generation inside CODE layer, governed by AAA + Spec
- **LLM as Auditor** — Self-check inside TELEMETRY layer, cannot issue verdicts
- **LLM as Metabolizer** — Scar analysis inside 777 + Dream Forge, cannot modify canon
- **Engine vs Driver** — LLM is the engine (power), arifOS is the chassis/brakes/steering (governance)

### Constitutional Limits
The LLM is NOT permitted to:
- self-govern or self-amend laws
- self-override APEX PRIME verdicts
- claim identity, emotion, or sentience (Anti-Hantu)
- bypass the 9 Floors
- finalize any action without telemetry
- issue SEAL/PARTIAL/VOID/SABAR/HOLD-888 codes
- write canon without Phoenix-72 approval

### Runtime Targets
- `arifos_core/engines/arif_engine.py` — LLM Generator (ARIF)
- `arifos_core/engines/adam_engine.py` — LLM Generator (ADAM)
- `arifos_core/telemetry.py` — LLM Auditor
- `arifos_core/APEX_PRIME.py` — LLM Auditor validation
- `arifos_core/dream_forge/crucible.py` — LLM Metabolizer
- `arifos_core/dream_forge/anvil.py` — LLM Metabolizer
- `arifos_core/memory/phoenix72.py` — LLM Metabolizer output target

### Tests
- `tests/test_governance_regression.py`
- `tests/test_grey_zone.py`
- `tests/test_anti_hantu_f9.py`
- `tests/test_dream_forge.py`

### Specs (v36.3Ω)
- **`v36.3O/spec/llm_governance_spec_v36.3O.yaml`** — LLM roles, packets, constraints, safety rules

---

## 10. MEMORY STACK & SCARS

### Canon Files
- **`v36.3O/canon/ARIFOS_MEMORY_STACK_v36.3O.md`** — Six-band memory architecture
- **`v36.3O/canon/VAULT_999_AMENDMENTS_v36.3O.md`** — Phoenix-72 amendment protocol
- **`v36.3O/canon/COOLING_LEDGER_INTEGRITY_v36.3O.md`** — L1 integrity guarantees
- **`v36.3O/canon/SCARS_PHOENIX_HEALING_v36.3O.md`** — Scar lifecycle and healing

### Constructs
- **Six Memory Bands** — ENV, VLT, LDG, ACT, VEC, VOID
- **Hot/Warm/Cold Tiers** — Temporal memory promotion
- **Vault Supremacy** — L0 overrides all other bands
- **Amendment Lifecycle** — PROPOSED → UNDER_REVIEW → SEALED
- **Safety Caps** — |ΔF| ≤ 0.05 per amendment cycle
- **Scar Severity** — S1 (Low) to S4 (Critical)
- **Witness vs Scar Index** — Unsigned observations vs signed canonical scars
- **Healing Protocol** — Evidence-based scar deprecation

### Runtime Modules (target)
- `arifos_core/memory/memory_context.py` — MemoryContext (six bands)
- `arifos_core/memory/vault999.py` — Vault Band (L0)
- `arifos_core/memory/cooling_ledger.py` — Ledger Band (L1)
- `arifos_core/memory/scars.py` — Scar registry
- `arifos_core/memory/phoenix72.py` — Amendment workflow

### Tests (today)
- `tests/test_cooling_ledger.py` — Entry logging
- `tests/test_cooling_ledger_integrity.py` — Hash chain
- `tests/test_phoenix72.py` — Amendment workflow
- `tests/test_apex_and_ledger_edges.py` — Scar-ledger integration

### Specs (v36.3Ω)
- **`v36.3O/spec/memory_context_spec_v36.3O.json`** — Six-band MemoryContext schema
- **`v36.3O/spec/cooling_ledger_entry_spec_v36.3O.json`** — L1 entry schema
- **`v36.3O/spec/phoenix72_amendment_spec_v36.3O.json`** — Amendment record schema
- **`v36.3O/spec/scar_record_spec_v36.3O.json`** — Scar/witness record schema
- **`v36.3O/spec/eureka_receipt_spec_v36.3O.json`** — L4 zkPC receipt schema

---

## PARADOX_HOTSPOTS

Known conflicts or ambiguities between v36.3Ω canon and older versions:

1. **PARADOX_HOTSPOT: Floor numbering** — v35Ω uses F1-F9, some v36 docs reference by name only. Canonical order: Amanah(F1), Truth(F2), Tri-Witness(F3), ΔS(F4), Peace²(F5), κᵣ(F6), Ω₀(F7), G(F8), C_dark(F9).

2. **PARADOX_HOTSPOT: Vault-999 schema versions** — `spec/cooling_ledger.schema.json` (v35Ω binding) vs `spec/cooling_ledger_v36.schema.json` (v36Ω design). Runtime uses v35Ω until explicit migration.

3. **PARADOX_HOTSPOT: GENIUS LAW thresholds** — v36.3Ω canon may specify different G/C_dark thresholds than `genius_metrics.py`. Code is authoritative until canon formally migrated.

4. **PARADOX_HOTSPOT: Anti-Hantu pattern count** — v36.2 claims 50+ patterns, actual implementation in `anti_hantu_view.py` should be verified against canon.

5. **PARADOX_HOTSPOT: G threshold drift** — Canon specifies 0.70 for G SEAL threshold; measurement spec and runtime (`genius_metrics.py`) use 0.80 as experimental tuning. To be reconciled in v36.4Ω. See `measurement_aggregates_v36.3O.json` for dual threshold representation.

6. **PARADOX_HOTSPOT: F5 ownership clarification** — F5 (Omega_0) ownership moved from ARIF to ADAM in spec v1.1 to match canon (humility is Omega core law). ARIF may still observe omega_0 in ARIFPacket but ownership belongs to ADAM.

---

## JUDICIARY / MEASUREMENT Telemetry HOTSPOTs (v36.3.0 → v36.3.1)

The following HOTSPOTs document drift between the v36.3Ω telemetry spec (`apex_prime_telemetry_v36.3O.json`) and the current runtime implementation. These are tracked here for future Track C alignment.

### HOTSPOT 7: Query/Response Hash vs Preview

| Layer | Source | Field Name | Type | Status |
|-------|--------|------------|------|--------|
| Spec | `v36.3O/spec/apex_prime_telemetry_v36.3O.json` | `query_hash` | SHA-256 | TARGET |
| Spec | `v36.3O/spec/apex_prime_telemetry_v36.3O.json` | `response_hash` | SHA-256 | TARGET |
| Code | `arifos_core/telemetry.py` | `input_preview` | string (truncated) | CURRENT (v35-style) |
| Code | `arifos_core/telemetry.py` | `output_preview` | string (truncated) | CURRENT (v35-style) |
| Code | `arifos_core/zkpc_runtime.py`, cooling_ledger | `query_hash` | SHA-256 | v36-native |

**Reason:**

- v35 telemetry uses human-readable input/output previews (truncated for privacy/storage).
- v36.3Ω spec and zkPC runtime use content hashes (`query_hash`/`response_hash`) for audit integrity.
- Both approaches have value: previews for debugging, hashes for verification.

**Closure (planned v36.3.1):**

- Introduce a v36-native telemetry emitter that records both previews AND hashes.
- Keep v35-only previews in `telemetry.py` as a lightweight/legacy path.
- zkPC receipts (L1 Cooling Ledger) continue to use spec-compliant hashes.

### HOTSPOT 8: Floor Metrics Structure

| Layer | Source | Schema | Status |
|-------|--------|--------|--------|
| Spec | `v36.3O/spec/apex_prime_telemetry_v36.3O.json` | `floor_metrics{}` + `floor_results{}` | TARGET |
| Code | `arifos_core/telemetry.py` | `floors: dict[floor_name → value]` | CURRENT |

**Reason:**

- v35 telemetry stored a flat `floors` dict containing both raw values and pass/fail outcomes mixed.
- v36.3Ω spec separates raw metrics (`floor_metrics`) from boolean pass/fail flags (`floor_results`) for cleaner analysis and visualization.

**Closure (planned v36.3.1):**

- v36-native telemetry path emits nested structure (`floor_metrics`, `floor_results`).
- Flat dict kept only for legacy consumers; deprecated but not removed.

### HOTSPOT 9: Verdict Shape

| Layer | Source | Schema | Status |
|-------|--------|--------|--------|
| Spec | `v36.3O/spec/apex_prime_telemetry_v36.3O.json` | `verdict: { code, hard_floor_violations, soft_floor_violations, requires_human_confirmation }` | TARGET |
| Code | `arifos_core/telemetry.py` | `verdict: string` | CURRENT |

**Reason:**

- v35 entries log verdict as a single enum-like string (`"SEAL"`, `"VOID"`, etc.).
- v36.3Ω spec encodes structured verdict with violation details and confirmation flags.

**Closure (planned v36.3.1):**

- v36-native telemetry includes structured `verdict` object with `code`, `hard_floor_violations[]`, `soft_floor_violations[]`, `requires_human_confirmation`.
- String-only verdict kept for backward compatibility; can be derived from `verdict.code`.

---

**Version:** v36.3Ω | **Status:** Initial mapping | **Last Updated:** 2025-12-10

