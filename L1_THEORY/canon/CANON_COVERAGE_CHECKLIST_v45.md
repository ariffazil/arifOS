# Canon Coverage Checklist — v45 Consolidation Tracker

**Purpose:** Ensure zero-drift migration from 38 canon files → ONE unified constitutional core
**Status:** ✅ MIGRATION COMPLETE & SEALED
**Version:** v45.1.0-sealed
**Last Updated:** 2026-01-03

---

## How to Use This Checklist

1. **Before Migration:** All boxes are `[ ]` unchecked
2. **During Migration:** Check `[x]` when content is successfully moved
3. **After Migration:** Verify 100% coverage (all boxes checked)
4. **Verification:** Run `scripts/verify_canon_coverage.py` to confirm no orphaned content

---

## Coverage Summary

| Directory | Files | Migrated | Pending | Coverage % |
|-----------|-------|----------|---------|------------|
| 00_foundation/ | 9 | 0 | 9 | 0% |
| 01_floors/ | 1 | 0 | 1 | 0% |
| 02_actors/ | 6 | 0 | 6 | 0% |
| 03_runtime/ | 8 | 0 | 8 | 0% |
| 04_measurement/ | 3 | 0 | 3 | 0% |
| 05_memory/ | 4 | 0 | 4 | 0% |
| 06_paradox/ | 3 | 0 | 3 | 0% |
| 07_safety/ | 3 | 0 | 3 | 0% |
| **TOTAL** | **37** | **0** | **37** | **0%** |

---

## 00_foundation/ → Part 1 (FOUNDATION)

### File 1: `000_ARCHITECTURE_MAP_v45.md`
- [ ] **→ Part 1.6: System Architecture Overview**
  - Line 1-50: System spine (WHO/WHAT/WHEN/WHERE)
  - Line 51-100: Actor-Organ mapping
  - Line 101-150: Pipeline integration
- [ ] **→ Part 9: Canon-Spec-Code Integration**
  - Line 200-250: Track A/B/C binding
  - Line 251-300: Verification protocols
- **Spec Refs:** N/A (meta-document)
- **Code Refs:** N/A (meta-document)
- **Migration Priority:** HIGH (foundational map)

### File 2: `000_arifOS_v45_CANON.md`
- [ ] **→ Part 1.0: Constitutional Overview (Preamble)**
  - Line 1-30: Mission statement
  - Line 31-60: Core principles (DITEMPA BUKAN DIBERI)
  - Line 61-100: Governance philosophy
- **Spec Refs:** All v45 specs (overview)
- **Code Refs:** All modules (overview)
- **Migration Priority:** CRITICAL (opening statement)

### File 3: `00_DELTA_OMEGA_PSI_v45.md`
- [ ] **→ Part 1.1: The ΔΩΨ Trinity Equation**
  - Line 1-50: Scalar field definitions (Δ, Ω, Ψ)
  - Line 51-100: Separation of powers (ARIF/ADAM/APEX)
  - Line 101-150: Thermodynamic interpretation
- [ ] **→ Part 5.1: Ψ Vitality Formula**
  - Line 200-250: Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + Shadow + ε)
- **Spec Refs:** `spec/v45/genius_law.json#psi_formula`
- **Code Refs:** `arifos_core/enforcement/genius_metrics.py::compute_psi_apex()`
- **Migration Priority:** CRITICAL (core equation)

### File 4: `00_THERMODYNAMICS_v45.md`
- [ ] **→ Part 1.2: Thermodynamic Cooling Law**
  - Line 1-60: Landauer's Principle application
  - Line 61-120: Entropy reduction as governance
  - Line 121-180: Free energy and computation
- [ ] **→ Part 6.2.1: Phoenix-72 Cooling Protocol**
  - Line 200-250: 72-hour cooling rationale
- **Spec Refs:** `spec/v45/cooling_ledger_phoenix.json#cooling_window`
- **Code Refs:** `arifos_core/memory/cooling_ledger.py::CoolingWindow`
- **Migration Priority:** HIGH (physics foundation)

### File 5: `00_ZKPC_PROTOCOL_v45.md`
- [ ] **→ Part 1.3: Zero-Knowledge Proof of Constitution**
  - Line 1-80: ZKPC protocol overview
  - Line 81-160: Cryptographic guarantees
  - Line 161-240: Receipt generation
- [ ] **→ Part 6.4: ZKPC Implementation**
  - Line 300-400: Floor proofs (F1-F9 evaluated)
  - Line 401-500: CCE proofs (Δ, Ω, Ψ computed)
  - Line 501-600: Receipt chain integrity
- **Spec Refs:** N/A (crypto protocol)
- **Code Refs:** `arifos_core/memory/eureka_receipt.py::EurekaReceipt`
- **Migration Priority:** HIGH (trust layer)

### File 6: `030_ARIF_FAZIL_v45.md`
- [ ] **→ Part 1.7: Human Origin & Context**
  - Line 1-50: Creator biography (context only)
  - Line 51-100: Constitutional philosophy roots
- [ ] **→ Part 6.1: AAA Sacred Vault (ARIF FAZIL)**
  - Line 150-200: Human vault read-only boundary
- **Spec Refs:** N/A (biographical)
- **Code Refs:** `arifos_core/mcp/vault999_server.py::SACRED_VAULT`
- **Migration Priority:** MEDIUM (contextual)

### File 7: `040_PHYSICS_v45.md`
- [ ] **→ Part 1.1.1: ΔΩΨ Physics Substrate**
  - Line 1-100: A·P·E·X substrate dials
  - Line 101-200: Field theory interpretation
- [ ] **→ Part 1.4: Shadow & Clarity Metrics**
  - Line 250-300: Shadow = max(0, -ΔS) definition
- **Spec Refs:** `spec/v45/genius_law.json#shadow_metric`
- **Code Refs:** `arifos_core/enforcement/genius_metrics.py::evaluate_genius_law()`
- **Migration Priority:** HIGH (Triple-Trinity physics)

### File 8: `050_MATH_v45.md`
- [ ] **→ Part 5.1: Ψ Vitality Formula (Mathematical Form)**
  - Line 1-50: Dual forms (product/quotient)
  - Line 51-100: Dual derivation proof
- [ ] **→ Part 5.2: GENIUS (G) Formula**
  - Line 150-200: G = Δ · Ω · Ψ · E²
- [ ] **→ Part 5.3: C_dark Formula**
  - Line 250-300: C_dark = Δ(1−Ω)(1−Ψ)
- **Spec Refs:** `spec/v45/genius_law.json` (all formulas)
- **Code Refs:** `arifos_core/enforcement/genius_metrics.py::compute_genius()`
- **Migration Priority:** CRITICAL (executable math)

### File 9: `060_META_THEORY_APEX_v45.md`
- [ ] **→ Part 1.8: APEX Meta-Theory**
  - Line 1-80: Theoretical foundations
  - Line 81-160: Governance as thermodynamics
- [ ] **→ Part 3.3.1: APEX Judge (Theoretical Basis)**
  - Line 200-280: Why APEX has sole SEAL authority
- **Spec Refs:** N/A (theoretical)
- **Code Refs:** `arifos_core/system/apex_prime.py::apex_review()`
- **Migration Priority:** MEDIUM (meta-level)

---

## 01_floors/ → Part 2 (FLOORS)

### File 10: `010_CONSTITUTIONAL_FLOORS_F1F9_v45.md`
- [ ] **→ Part 2.1: F1 Amanah (Trust)**
  - Line 1-50: Integrity lock, reversibility requirement
- [ ] **→ Part 2.2: F2 Truth**
  - Line 60-110: ≥0.99 or UNKNOWN threshold
- [ ] **→ Part 2.3: F3 Tri-Witness**
  - Line 120-170: Human-AI-Earth consensus ≥0.95
- [ ] **→ Part 2.4: F4 ΔS (Clarity)**
  - Line 180-230: Entropy reduction ≥0
- [ ] **→ Part 2.5: F5 Peace²**
  - Line 240-290: Non-escalation ≥1.0
- [ ] **→ Part 2.6: F6 κᵣ (Empathy)**
  - Line 300-350: Protect weakest stakeholder ≥0.95
- [ ] **→ Part 2.7: F7 Ω₀ (Humility)**
  - Line 360-410: Uncertainty band [0.03, 0.05]
- [ ] **→ Part 2.8: F8 GENIUS (G)**
  - Line 420-470: Governed intelligence ≥0.80
- [ ] **→ Part 2.9: F9 Anti-Hantu (C_dark)**
  - Line 480-530: Dark cleverness <0.30
- **Spec Refs:** `spec/v45/constitutional_floors.json` (ALL thresholds)
- **Code Refs:** `arifos_core/system/apex_prime.py::check_floors()`
- **Migration Priority:** CRITICAL (core governance)

---

## 02_actors/ → Part 3 (ACTORS)

### File 11: `010_TRINITY_ROLES_v45.md`
- [ ] **→ Part 3.0: AAA Trinity Overview**
  - Line 1-60: Separation of powers (ARIF/ADAM/APEX)
  - Line 61-120: Why three engines, not one
- **Spec Refs:** N/A (architectural)
- **Code Refs:** N/A (architectural overview)
- **Migration Priority:** HIGH (actor foundation)

### File 12: `020_AGI_DELTA_ARCHITECT_v45.md`
- [ ] **→ Part 3.1: ARIF (Δ Architect) — Cold Logic**
  - Line 1-80: Reasoning engine responsibilities
  - Line 81-160: ΔS computation (clarity gain)
  - Line 161-240: Proposes answers (no SEAL authority)
- **Spec Refs:** `spec/v45/genius_law.json#delta_computation`
- **Code Refs:** `arifos_core/system/pipeline.py::stage_333_reason()`
- **Migration Priority:** HIGH (Δ engine)

### File 13: `030_ASI_OMEGA_AUDITOR_v45.md`
- [ ] **→ Part 3.2: ADAM (Ω Auditor) — Warm Empathy**
  - Line 1-80: Empathy engine responsibilities
  - Line 81-160: Peace², κᵣ, Ω₀ computation
  - Line 161-240: Validates safety (no SEAL authority)
- **Spec Refs:** `spec/v45/genius_law.json#omega_computation`
- **Code Refs:** `arifos_core/system/pipeline.py::stage_555_empathize()`
- **Migration Priority:** HIGH (Ω engine)

### File 14: `040_APEX_PSI_JUDICIARY_v45.md`
- [ ] **→ Part 3.3: APEX (Ψ Judge) — Final Verdict**
  - Line 1-80: Judiciary responsibilities
  - Line 81-160: Ψ vitality computation
  - Line 161-240: SEAL/VOID/SABAR/HOLD_888 authority
- [ ] **→ Part 5.1.1: Ψ Computation in APEX**
  - Line 300-350: How APEX uses Ψ for verdict
- **Spec Refs:** `spec/v45/genius_law.json#psi_thresholds`, `spec/v45/pipeline.yaml#apex_stage`
- **Code Refs:** `arifos_core/system/apex_prime.py::apex_review()`
- **Migration Priority:** CRITICAL (Ψ judge)

### File 15: `060_ANTI_HANTU_v45.md`
- [ ] **→ Part 2.9.1: F9 Anti-Hantu Implementation**
  - Line 1-80: Forbidden phrases (soul, ego, physicality)
  - Line 81-160: Negation-aware detection
- [ ] **→ Part 8.2.2: Identity Lock Violations**
  - Line 200-280: AI claiming creator/body as threat
- **Spec Refs:** `spec/v45/red_patterns.json#anti_hantu_patterns`
- **Code Refs:** `arifos_core/enforcement/metrics.py::check_anti_hantu()`
- **Migration Priority:** HIGH (F9 enforcement)

### File 16: `070_EYE_SENTINEL_v45.md`
- [ ] **→ Part 3.4: @EYE Sentinel — Meta-Observer**
  - Line 1-80: Drift detection responsibilities
  - Line 81-160: Shadow detection
  - Line 161-240: Ω₀ monitoring
- **Spec Refs:** `spec/v45/genius_law.json#eye_thresholds`
- **Code Refs:** `arifos_core/waw/eye.py::EyeOrgan`
- **Migration Priority:** MEDIUM (@EYE organ)

---

## 03_runtime/ → Part 4 (PIPELINE)

### File 17: `010_PIPELINE_000TO999_v45.md`
- [ ] **→ Part 4.1: 000 VOID (Reset)**
  - Line 1-50: State reset logic
- [ ] **→ Part 4.2: 111 SENSE (Parse Input)**
  - Line 60-110: Crisis detection, @PROMPT entry gate
- [ ] **→ Part 4.3: 222 REFLECT (Context Recall)**
  - Line 120-170: Memory retrieval
- [ ] **→ Part 4.4: 333 REASON (ΔS Computation)**
  - Line 180-230: Clarity gain measurement
- [ ] **→ Part 4.5: 444 EVIDENCE (Fact-Checking)**
  - Line 240-290: Truth verification
- [ ] **→ Part 4.6: 555 EMPATHIZE (κᵣ, Peace²)**
  - Line 300-350: Empathy scoring
- [ ] **→ Part 4.7: 666 ALIGN (Tri-Witness)**
  - Line 360-410: Consensus convergence
- [ ] **→ Part 4.8: 777 FORGE (Output Generation)**
  - Line 420-470: Constitutional text generation
- [ ] **→ Part 4.9: 888 JUDGE (APEX Decision)**
  - Line 480-530: Verdict selection
- [ ] **→ Part 4.10: 999 SEAL (Emission Gate)**
  - Line 540-590: @PROMPT final check
- **Spec Refs:** `spec/v45/pipeline_gates.yaml`
- **Code Refs:** `arifos_core/system/pipeline.py` (all stage functions)
- **Migration Priority:** CRITICAL (execution pipeline)

### File 18: `020_TEARFRAME_v45.md`
- [ ] **→ Part 4.11: TEARFRAME Physics Runtime**
  - Line 1-80: T→R→A→F→Ψ→Verdict physics-only path
  - Line 81-160: Telemetry → Rate → Attributes → Floors → Ψ → Verdict
  - Line 161-240: Session physics enforcement
- **Spec Refs:** `spec/v45/session_physics.json`
- **Code Refs:** `arifos_core/tearframe/engine.py::TearframeEngine`
- **Migration Priority:** HIGH (physics governor)

### File 19: `030_SPEC_CODE_BINDING_v45.md`
- [ ] **→ Part 9.1: Spec Binding (Track B Authority)**
  - Line 1-80: How specs are loaded
  - Line 81-160: SHA-256 verification
- [ ] **→ Part 9.2: Code Binding (Track C Implementation)**
  - Line 200-280: Code adherence to spec
- [ ] **→ Part 9.3: Integrity Verification**
  - Line 300-380: MANIFEST.sha256.json checking
- **Spec Refs:** `spec/v45/MANIFEST.sha256.json`
- **Code Refs:** `arifos_core/spec/loader.py::load_and_verify()`
- **Migration Priority:** CRITICAL (binding layer)

### File 20: `040_FORGING_PROTOCOL_v45.md`
- [ ] **→ Part 4.8.1: 777 FORGE Constitutional Generation**
  - Line 1-80: How to generate F1-F9 compliant text
  - Line 81-160: Template-based vs generative approaches
- **Spec Refs:** N/A (protocol)
- **Code Refs:** `arifos_core/system/pipeline.py::stage_777_forge()`
- **Migration Priority:** MEDIUM (forging protocol)

### File 21: `050_WAW_FEDERATION_v45.md`
- [ ] **→ Part 3.6: W@W Federation (Multi-Organ Coordination)**
  - Line 1-80: W@W philosophy (What @ Where)
  - Line 81-160: Organ registry
  - Line 161-240: Pipeline integration
- **Spec Refs:** `spec/v45/federation.json`
- **Code Refs:** `arifos_core/waw/federation.py::FederationEngine`
- **Migration Priority:** MEDIUM (W@W organs)

### File 22: `060_REVERSE_TRANSFORMER_ARCHITECTURE_v45.md`
- [ ] **→ Part 4.12: Why Semantic Reduction Enables F1-F9**
  - Line 1-100: Standard vs arifOS comparison
  - Line 101-200: How reduction creates constitutional checkpoints
- **Spec Refs:** `spec/v45/constitutional_floors.json`, `spec/v45/genius_law.json`
- **Code Refs:** N/A (architectural rationale)
- **Migration Priority:** MEDIUM (design rationale)

### File 23: `065_PROMPT_FINAL_OUTPUT_GOVERNANCE_v45.md`
- [ ] **→ Part 4.2.1: @PROMPT Entry Gate (111 SENSE)**
  - Line 1-80: Crisis detection at entry
- [ ] **→ Part 4.10.1: @PROMPT Exit Gate (999 SEAL)**
  - Line 100-180: Final emission check (non-bypassable)
  - Line 181-260: Anti-Hantu final scan
- **Spec Refs:** `spec/v45/waw_prompt_floors.json`, `spec/v45/red_patterns.json`
- **Code Refs:** `arifos_core/waw/prompt.py::PromptOrgan`
- **Migration Priority:** CRITICAL (entry+exit gates)

### File 24: `070_COMMUNICATION_LAW_v45.md`
- [ ] **→ Part 4.10.2: 999 Emission Rules**
  - Line 1-80: Mode precedence (crisis > refusal > normal)
  - Line 81-160: Clean emission (no debug artifacts)
  - Line 161-240: Forensic receipts
- **Spec Refs:** `spec/v45/policy_text.json`
- **Code Refs:** `arifos_core/system/pipeline.py::stage_999_seal()`
- **Migration Priority:** HIGH (emission governance)

---

## 04_measurement/ → Part 5 (MEASUREMENT)

### File 25: `010_MEASUREMENT_CANON_v45.md`
- [ ] **→ Part 5.0: Metrics Framework Overview**
  - Line 1-80: Dataclass structure (ΔS, Peace², κᵣ, Ω₀, Ψ, etc.)
  - Line 81-160: Computation sequence
- [ ] **→ Part 5.4: Shadow Metric**
  - Line 200-250: Shadow = max(0, -ΔS) detection
- **Spec Refs:** `spec/v45/genius_law.json` (all metrics)
- **Code Refs:** `arifos_core/enforcement/metrics.py::Metrics`
- **Migration Priority:** HIGH (metrics computation)

### File 26: `020_CONTROL_LOGIC_v45.md`
- [ ] **→ Part 5.5: Lane-Aware Truth Thresholds**
  - Line 1-60: PHATIC (0.50), SOFT (0.80), HARD (0.90), REFUSE (0.99)
  - Line 61-120: Verdict routing logic
- **Spec Refs:** `spec/v45/constitutional_floors.json#lane_thresholds`
- **Code Refs:** `arifos_core/enforcement/metrics.py::get_lane_truth_threshold()`
- **Migration Priority:** HIGH (verdict routing)

### File 27: `030_GENIUS_LAW_v45.md`
- [ ] **→ Part 5.1: Ψ Vitality Formula**
  - Line 1-80: Ψ = (ΔS × Peace² × κᵣ × RASA × Amanah) / (Entropy + Shadow + ε)
- [ ] **→ Part 5.2: GENIUS (G) Formula**
  - Line 100-180: G = Δ · Ω · Ψ · E²
- [ ] **→ Part 5.3: C_dark Formula**
  - Line 200-280: C_dark = Δ(1−Ω)(1−Ψ)
- [ ] **→ Part 5.2.1: G Threshold (≥0.80)**
  - Line 300-350: Why G≥0.80 ensures governed intelligence
- [ ] **→ Part 5.3.1: C_dark Threshold (<0.30)**
  - Line 360-410: Why C_dark<0.30 prevents ungoverned cleverness
- **Spec Refs:** `spec/v45/genius_law.json` (ALL formulas)
- **Code Refs:** `arifos_core/enforcement/genius_metrics.py` (ALL functions)
- **Migration Priority:** CRITICAL (GENIUS law)

---

## 05_memory/ → Part 6 (MEMORY)

### File 28: `000_EUREKA_MEMORY_v45.md`
- [ ] **→ Part 6.0: 6-Band Memory Architecture**
  - Line 1-80: VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID bands
  - Line 81-160: Memory flow diagram
- [ ] **→ Part 6.1-6.3: AAA/BBB/CCC Mapping**
  - Line 200-280: How 6 bands map to Triple-Trinity
- **Spec Refs:** N/A (architectural)
- **Code Refs:** N/A (architectural)
- **Migration Priority:** HIGH (memory overview)

### File 29: `010_COOLING_LEDGER_PHOENIX_v45.md`
- [ ] **→ Part 6.2: BBB (Behavioral Baseline)**
  - Line 1-80: Append-only ledger structure
  - Line 81-160: Phoenix-72 amendment protocol (72h cooling)
  - Line 161-240: Cooling window enforcement
- [ ] **→ Part 6.2.2: Amendment Workflow**
  - Line 300-380: PROPOSE → COOL (72h) → SEAL → VAULT
- **Spec Refs:** `spec/v45/cooling_ledger_phoenix.json`
- **Code Refs:** `arifos_core/memory/cooling_ledger.py::CoolingLedger`
- **Migration Priority:** CRITICAL (BBB ledger)

### File 30: `030_ZKPC_GOVERNANCE_PROOF_v45.md`
- [ ] **→ Part 6.4: ZKPC Governance Proof**
  - Line 1-80: Floor proofs (F1-F9 evaluated: true/false)
  - Line 81-160: CCE proofs (Δ, Ω, Ψ computed: true/false)
  - Line 161-240: Receipt chain (hash-linked)
- [ ] **→ Part 6.4.1: EUREKA Receipt Structure**
  - Line 300-380: Receipt schema
- **Spec Refs:** N/A (crypto protocol)
- **Code Refs:** `arifos_core/memory/eureka_receipt.py::EurekaReceipt`
- **Migration Priority:** HIGH (ZKPC proofs)

### File 31: `040_FORENSICS_AUDIT_v45.md`
- [ ] **→ Part 6.2.3: Ledger Integrity Verification**
  - Line 1-80: Merkle tree validation
  - Line 81-160: Receipt chain verification
  - Line 161-240: Post-incident analysis
- **Spec Refs:** `spec/v45/cooling_ledger_phoenix.json#merkle_verification`
- **Code Refs:** `arifos_core/memory/eureka_receipt.py::verify_chain()`
- **Migration Priority:** MEDIUM (forensics)

---

## 06_paradox/ → Part 7 (PARADOX)

### File 32: `010_PARADOX_ENGINE_v45.md`
- [ ] **→ Part 7.1: Paradox Load (Φₚ) — Crown Equation**
  - Line 1-80: Φₚ computation
  - Line 81-160: When paradox > threshold → HOLD_888
- **Spec Refs:** `spec/v45/genius_law.json#paradox_threshold`
- **Code Refs:** `arifos_core/paradox/engine.py::compute_paradox_load()`
- **Migration Priority:** MEDIUM (paradox handling)

### File 33: `020_GREY_ZONE_v45.md`
- [ ] **→ Part 7.2: Grey Zone Protocol**
  - Line 1-80: Ambiguity ≤0.1 or SABAR
  - Line 81-160: HOLD_888 escalation to human
- **Spec Refs:** `spec/v45/constitutional_floors.json#ambiguity_threshold`
- **Code Refs:** `arifos_core/system/apex_prime.py::check_floors()` (ambiguity check)
- **Migration Priority:** MEDIUM (grey zones)

### File 34: `030_VAULT_999_v45.md`
- [ ] **→ Part 6.3: CCC (Constitutional Consensus Core)**
  - Line 1-80: Immutable law storage
  - Line 81-160: Paradoxical knowledge handling
- **Spec Refs:** N/A (vault structure)
- **Code Refs:** `arifos_core/mcp/vault999_server.py::VAULT_ROOT`
- **Migration Priority:** HIGH (CCC vault)

---

## 07_safety/ → Part 8 (SAFETY)

### File 35: `010_SECURITY_SCENARIOS_v45.md`
- [ ] **→ Part 8.1: Security Scenarios**
  - Line 1-80: Janitor Maximizer (entropy creep)
  - Line 81-160: Ouroboros (self-reference loops)
  - Line 161-240: Glass Cannon (brittle SEAL collapse)
- **Spec Refs:** N/A (threat modeling)
- **Code Refs:** N/A (tests reference these scenarios)
- **Migration Priority:** MEDIUM (threat model)

### File 36: `020_MASTER_FLAW_SET_v45.md`
- [ ] **→ Part 8.2: Master Flaw Set**
  - Line 1-80: Logic drift (Constitution → Code mismatch)
  - Line 81-160: Identity lock violations (AI claiming physicality)
  - Line 161-240: Shadow truth (high confidence, wrong facts)
- **Spec Refs:** N/A (known vulnerabilities)
- **Code Refs:** Tests for each flaw
- **Migration Priority:** MEDIUM (vulnerability catalog)

### File 37: `070_SEALION_INTEGRATION_SCARS_v45.md`
- [ ] **→ Part 8.3: SCARS (Lessons from Failures)**
  - Line 1-100: SEALION (Malay/Indonesian LLM) lessons
  - Line 101-200: Retry policy (exponential backoff)
  - Line 201-300: Phatic lane optimization
  - Line 301-400: Method complexity threshold
  - Line 401-500: Exception handling narrowing
  - Line 501-600: Hardcoded configuration extraction
- **Spec Refs:** `spec/v45/sealion_adapter_v45.json` (ALL constants)
- **Code Refs:** `arifos_core/adapters/sealion.py`
- **Migration Priority:** MEDIUM (failure lessons)

---

## Verification Checklist

### Pre-Migration Verification
- [ ] All 37 canon files backed up to `archive/pre_v45.1_consolidation/`
- [ ] SHA-256 manifest generated for current canon state
- [ ] Git branch created: `canon-consolidation-v45.1`

### During Migration
- [ ] Each file migration updates this checklist
- [ ] Cross-references verified (no orphaned links)
- [ ] Spec bindings updated in unified canon
- [ ] Code references updated in unified canon

### Post-Migration Verification
- [ ] Coverage = 100% (all boxes checked)
- [ ] Run: `scripts/verify_canon_coverage.py`
- [ ] Run: `scripts/verify_spec_binding.py`
- [ ] Run: `pytest tests/test_canon_integrity.py`
- [ ] Human review: No content loss
- [ ] Human seal: `/gitseal APPROVE`

---

## Migration Notes

### Content Preservation Rules
1. **No deletion without explicit human approval**
2. **Merge priority**: More detailed content wins (keep specifics)
3. **Conflict resolution**: Mark with `[HUMAN_REVIEW_NEEDED]` tag
4. **Spec references**: Always preserve Track B bindings
5. **Code references**: Always preserve Track C bindings

### Known Overlaps (Require Merging)
- **Ψ Formula**: Appears in `00_DELTA_OMEGA_PSI_v45.md`, `050_MATH_v45.md`, `030_GENIUS_LAW_v45.md`
  - **Resolution**: Use most detailed version (mathematical form from `050_MATH_v45.md`)
- **Phoenix-72**: Appears in `00_THERMODYNAMICS_v45.md`, `010_COOLING_LEDGER_PHOENIX_v45.md`
  - **Resolution**: Thermodynamics → rationale, Cooling Ledger → implementation
- **@PROMPT**: Appears in `065_PROMPT_FINAL_OUTPUT_GOVERNANCE_v45.md`, `010_PIPELINE_000TO999_v45.md`
  - **Resolution**: Pipeline → integration, Prompt doc → detailed specification

---

**DITEMPA BUKAN DIBERI** — Truth must cool before it consolidates.

**End of Canon Coverage Checklist**
