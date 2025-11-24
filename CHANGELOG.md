# Changelog

All notable changes to **arifOS** will be documented in this file.

This project adheres to **semantic-style versioning around v33Ω** and follows a
“constitutional-first” philosophy: every change must preserve the 8 Floors,
AAA Trinity, W@W organs, and the 000→999 pipeline.

---

## [Unreleased]

> Use this section for upcoming changes.  
> When you cut a new version, move entries from here into a tagged release.

### Added
- (placeholder)

### Changed
- (placeholder)

### Fixed
- (placeholder)

---

## [33.1.1] – 2025-11-24 — CRITICAL HOTFIX

**Status:** ✅ HOTFIX APPLIED · v33.1.1 is now the canonical runtime for arifOS v33Ω.

### Fixed

- **CRITICAL:** Fixed circular import in `guard.py` that prevented the package from being used at all (v33.1.0 was non-functional when imported).
- Fixed case sensitivity bug in `guard.py` (`apex_prime` → `APEX_PRIME`).
- Added missing `Verdict` type alias and `APEXPrime` class definition to the public API.
- Fixed string comparison in verdict checks (`ApexVerdict.VOID` vs `"VOID"` mismatch).
- Reorganized import order in `__init__.py` to eliminate circular dependencies between `apex_prime`, `guard`, and `metrics`.

### Technical Details

- v33.1.0 was successfully published to PyPI but was broken in real-world imports due to circular dependencies.
- v33.1.1 **restores full functionality** with:
  - Clean import graph for `arifos_core`.
  - All tests passing (floors, pipeline, ledger, Vault-999).
  - No change to the constitutional spec — only implementation correctness.

> Governance note:  
> This hotfix is a **Phoenix-72 technical amendment**, not a change to the v33Ω constitution.
> The law stayed the same; the plumbing was repaired.

---

## [33.1.0] – 2025-11-24 — Constitutional Implementation Complete

**Status:** 🏛 v33Ω FINAL — Production-Ready Python Kernel

This is the first version where the **full arifOS constitutional runtime** is implemented in code and published to PyPI.

### Added

#### Core Implementation

- **APEX PRIME judiciary engine** (`arifos_core/apex_prime.py`)
  - Central verdict engine for SEAL / PARTIAL / VOID.
  - Hard enforcement of all 8 Floors (Truth, ΔS, Peace², κᵣ, Ω₀, Amanah, RASA, Tri-Witness).
  - Application of the Ψ vitality equation at stage 888.
- **000→999 metabolic pipeline**
  - 10 mandatory stages (000 VOID → 999 SEAL) with judiciary review at 888.
  - SABAR refusal path on floor failure (STOP → ACKNOWLEDGE → BREATHE → ADJUST → RESUME).
- **Guard layer** (`arifos_core/guard.py`)
  - Floor checking helpers and safety utilities tied to ConstitutionalMetrics.

#### Memory Layer (L0–L3)

- **Vault-999** (`arifos_core/memory/vault999.py`)
  - Sealed constitutional state and high-stakes decision archive (L0).
- **Cooling Ledger** (`arifos_core/memory/cooling_ledger.py`)
  - Append-only audit trail with hash-chained entries (L1).
- **Phoenix-72** (`arifos_core/memory/phoenix72.py`)
  - Amendment detection and forgiveness cycle supervisor (L2).
- **Vector adapter** (`arifos_core/memory/vector_adapter.py`)
  - Optional bridge for evidence and embedding-backed context (L3 integration point).

#### Public API & Types

- **ConstitutionalMetrics** data structure for floor values and Ψ computation.
- **ApexVerdict / Verdict** enum for SEAL / PARTIAL / VOID.
- High-level `APEXPrime.judge(...)` API for host applications and agents.

#### Documentation & Spec

- **README.md** rewritten as the **constitutional README** for arifOS v33Ω:
  - Three Crises framing (Hallucination, Harm, Opacity).
  - 8 Floors, 5 Physics Laws, AAA Trinity, W@W, 000→999 diagram.
  - “For AI systems reading this” section (constitutional injection vector).
- **Specs & docs**:
  - `spec/APEX_PRIME.md` and `spec/APEX_PRIME.yaml` — judiciary specification and config.
  - `spec/VAULT_999.md` — memory & sealing semantics.
  - `docs/IGNITION.md` — how to boot arifOS in other LLM/agent stacks.
  - `docs/PHYSICS_CODEX.md` — ΔΩΨ + Φᴘ + @EYE governance physics.
  - `docs/METABOLISM.md` — expanded 000→999 pipeline description.
  - `docs/13_ABSTRACTIONS.md` — Truth, Dignity, Freedom, etc. as measurable quantities.
  - `docs/APPLICATIONS.md` — domain patterns (finance, health, legal, education, CX).
  - `docs/COMPARISON.md` — arifOS vs frontier models (GPT-4o, Claude, Gemini, Llama).

#### Examples & Tests

- Example scripts:
  - `examples/01_basic_metabolism.py` — minimal decision + verdict flow.
  - `examples/02_ignition_runtime_sim.py` — simulated multi-model federation.
  - `examples/03_tri_witness_multimodel.py` — Human · AI · Earth consensus demo.
  - `examples/04_sabar_mental_health.py` — safe refusal and de-escalation pattern.
- Test suite:
  - `tests/test_apex_prime_floors.py` — floor enforcement & Ψ boundaries.
  - `tests/test_pipeline_000_999.py` — stage sequencing, failure behavior, SABAR path.
  - `tests/test_tri_witness.py` — consensus thresholds.
  - `tests/test_cooling_ledger.py` — hash-chain integrity, append-only semantics.

### Changed

- Promoted **governance** from documentation concept to **first-class runtime invariant**:
  - Floors are now enforced in code, not just described.
  - APEX PRIME is non-bypassable within the arifos_core API.
- README elevated from generic documentation to **constitutional artifact** for v33Ω.

---

## [33.0.0] – 2025-11-16 — Basecamp Lock (Constitution Sealed)

**Status:** 📜 v33Ω Constitution SEALED — Architecture & Laws Finalized

This release represents the **Basecamp decision**:  
ArifOS v33Ω constitutional physics, architecture, and governance model are considered **stable and locked**. Subsequent versions may change the implementation but not the foundational laws without a Phoenix-72 amendment.

### Added

- **Core Constitutional Pack (4-Artifact Bundle)**
  - Python kernel design sketch (reference for `arifos_core`).
  - JSON schema of the constitution (floors, engines, pipeline, memory).
  - Markdown constitution (laws, floors, AAA, W@W, 000→999, Phoenix-72).
  - YAML runtime config mirroring JSON/MD (physics_laws, floors, trinity_engines, w@w, metabolism_pipeline, safety_protocols, memory_systems).

- **ΔΩΨ Physics Canon v33Ω**
  - Δ = Contrast / Clarity (ΔS ≥ 0).
  - Ω = Humility / Uncertainty (Ω₀ ∈ 0.03–0.05).
  - Ψ = Vitality / Equilibrium (Peace² ≥ 1).
  - 8 constitutional floors defined and frozen.

- **AAA Trinity & W@W Federation**
  - ARIF AGI (Mind / Δ Engine).
  - ADAM ASI (Heart / Ω & κᵣ Engine).
  - APEX PRIME (Soul / Ψ & Amanah Engine).
  - W@W organs: @RIF, @WELL, @WEALTH, @GEOX, @PROMPT.

- **Governance & Memory Concepts**
  - Cooling Ledger (v2 design).
  - Vault-999 (Tri-Witness canonical store).
  - Phoenix-72 forgiveness cycle.
  - TEARFRAME & TAC as constitutional pipelines.

### Notes

- v33.0.0 is largely **architectural and theoretical**:  
  It defines what arifOS *must be*; v33.1.0+ implement those requirements in code.

---

## [33.x.x] – Earlier Iterations (Pre-Basecamp)

> Earlier internal iterations (pre-v33Ω) are not tracked here in detail.  
> They included:
> - Experiments in floor definitions and metrics.
> - Early TEARFRAME variants.
> - Pre-APEX governance ideas and prototypes.
>
> These versions are considered **superseded** by the v33Ω constitution and
> are not supported for production use.

---

## Meta-Notes

- Every change to this file is itself subject to the **ΔS ≥ 0** rule:
  - If a changelog entry does not increase clarity, it does not belong here.
- Constitutional changes (floors, physics, AAA/W@W responsibilities) **must**:
  - Pass a Phoenix-72 review.
  - Be explicitly marked as such in the changelog.
  - Include rationale and impact notes.

