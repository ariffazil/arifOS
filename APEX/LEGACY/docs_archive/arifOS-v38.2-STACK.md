# arifOS v38.2 STACK — Architecture Decision Record

**Status:** SEALED snapshot of v38.2 implementation (no new features invented)  
**Version:** v38.2  
**Scope:** Cage/Beast boundary, pipeline patterns, memory stack, cooling ledger  
**Audience:** Arif (decision-maker), governed LLM agents, tooling/infra integrators

---

## 1. Context & Constraints

This ADR documents the **v38.2 runtime stack** as it exists today, based on the extracted implementation in `spec_archive/`:

- `arifOS-v38-Core-Brain.md` — 000→999 pipeline, AGI·ASI·APEX Trinity, W@W organs, @EYE views
- `arifOS-Constitution-9-Floors.md` — 9 floors, thresholds, GENIUS LAW, detectors
- `Cooling-Ledger-v35-Schema-and-Usage.md` — JSON schema, hash-chain, CLI tools
- `Memory-Bands-v38-Policy-Current-State.md` — 6 bands, routing, invariants, Phoenix-72
- `GENIUS-LAW-Truth-Polarity-Extract.md` — G / C_dark / Ψ formulas, truth polarity
- `L4-Jailbreak-Anti-Hantu-Defense.md` — Anti-Hantu F9, Amanah detector
- `Phase-4-Integration-Status-v38.md` — Implementation status, v38.2 time governance

**Hard constraints (from canon/spec/tests):**

- **Cage vs Beast:** arifOS is a **governance kernel** that wraps any LLM; the LLM is external (“Beast”), accessed via adapters (`arifos_core/llm_interface.py`, `arifos_core/adapters/*`, `integrations/sealion/*`). Core floors and judiciary do not depend on any specific provider.
- **Physics-first floors:** 9 constitutional floors (Truth, Clarity, Tri-Witness, Peace², Humility, Empathy, Amanah, RASA, Anti-Hantu) are enforced by `arifos_core/APEX_PRIME.py` and `arifos_core/metrics.py` per `spec/constitutional_floors_v38Omega.json`.
- **GENIUS LAW:** Verdicts must respect G, C_dark, and Ψ thresholds as defined in `arifos_core/genius_metrics.py` and `spec/genius_law_v38Omega.json`.
- **Memory invariants:** v38 EUREKA memory stack (6 bands + 4 invariants) governs what becomes canonical (`arifos_core/memory/bands.py`, `arifos_core/memory/policy.py`, `canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md`).
- **Cooling Ledger:** All governance decisions are logged to an **append-only, hash-chained ledger** (`cooling_ledger/L1_cooling_ledger.jsonl`) per `spec/cooling_ledger.schema.json` and `spec/cooling_ledger_phoenix_v38Omega.json`.
- **Time as governor (v38.2):** Entropy rot and SUNSET routing are enforced via `arifos_core/kernel.py` and `spec/arifos_v38_2.yaml`; SABAR/PARTIAL cannot drift indefinitely.

This ADR **does not introduce new concepts**; it only locks in the stack decisions that are already implemented and tested in v38.2.

---

## 2. Decision: Cage vs Beast

### 2.1 Cage Role (arifOS Core)

- **Definition:** arifOS is the **CAGE** — a constitutional runtime that:
  - Evaluates all outputs with 9 floors + GENIUS LAW (F1–F9 + G, C_dark, Ψ).
  - Routes through the 000→999 pipeline (`arifos_core/pipeline.py`, spec_archive Doc 1).
  - Aggregates W@W organs (`arifos_core/waw/*`) and @EYE Sentinel views (`arifos_core/eye/*`, `arifos_core/eye_sentinel.py`).
  - Issues final verdicts at 888_JUDGE and records them at 999_SEAL.
- **Guarantee:** The cage is **provider-agnostic**. No floor logic, verdict logic, or memory/ledger code depends on a specific model name or vendor.

### 2.2 Beast Role (LLM Backends)

- **Definition:** The **BEAST** is any external LLM used to draft candidate outputs.
- **Integration pattern (existing in v38.2):**
  - `arifos_core/llm_interface.py` provides a thermodynamically-gated streaming interface with entropy-based SABAR triggers.
  - `arifos_core/adapters/llm_openai.py`, `llm_claude.py`, `llm_gemini.py`, `llm_sealion.py` and `integrations/sealion/engine.py` implement backend-specific adapters.
  - The pipeline treats these adapters as **pluggable sources of text**, not as authorities; all text goes through floors, @EYE, and GENIUS LAW before being sealed.
- **Decision:** For v38.2, **no single Beast is canonical**. The stack standardizes the cage and lets the Beast be selected via adapters/config, consistent with README.md and spec_archive Doc 7 (SEA-LION support implemented, others via adapters).

**Validation:**  
– Spec_archive Doc 1 (Core Brain) and Doc 7 (Phase-4 Status) show that pipeline, W@W, @EYE, floors, and memory run independently of any particular LLM, while Beast support lives in adapters/integrations.  
– `arifos_core/llm_interface.py` is optional; tests for floors, memory, and ledger do not require any remote LLM.

---

## 3. Decision: Pipeline Patterns (000→999)

### 3.1 Metabolic Pipeline

**Pattern:** A 10-stage metabolic pipeline (000→999) with **Class A/B routing**:

- **Stages** (per spec_archive Doc 1):
  - 000_VOID — Amanah gate (`arifos_core/stages/stage_000_amanah.py`)
  - 111_SENSE — cross-session recall (`arifos_core/integration/memory_sense.py`)
  - 222_REFLECT — context building (`pipeline.py::stage_222_reflect`)
  - 333_REASON — draft generation (`pipeline.py::stage_333_reason`)
  - 444_ALIGN — truth/clarity alignment (`pipeline.py::stage_444_align`)
  - 555_EMPATHIZE — empathy and Peace² metrics (`stages/stage_555_empathy.py`)
  - 666_BRIDGE — W@W organs + @EYE views (`pipeline.py::stage_666_bridge`)
  - 777_FORGE — scar detection (`integration/memory_scars.py`)
  - 888_JUDGE — APEX PRIME judiciary (`integration/memory_judge.py`)
  - 999_SEAL — ledger + memory write (`integration/memory_seal.py`)

**Routing:**

- Class A (fast track): 000 → 111 → 333 → 888 → 999  
- Class B (deep track): 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999

### 3.2 AGI·ASI·APEX Trinity, W@W, @EYE

- **AGI·ASI·APEX Trinity:** ARIF (cold logic), ADAM (warm logic), APEX PRIME (judiciary) are internal engines (`arifos_core/engines/*`, `APEX_PRIME.py`) that compute metrics and verdicts but do not call external APIs.
- **W@W Federation:** @WELL, @RIF, @WEALTH, @GEOX, @PROMPT add organ-level signals and vetoes (`arifos_core/waw/*`), per spec_archive Doc 1 and Doc 2.
- **@EYE Sentinel:** 12+ views (FloorView, DriftView, ParadoxView, ShadowView, SilenceView, MaruahView, TraceView, VersionView, BehaviorDriftView, SleeperView, AntiHantuView, GeniusView) scan outputs before final verdict.

**Decision:** v38.2 standardizes this **deterministic stage graph** as the pattern for all Beast outputs; any LLM integration must plug into this pipeline, not bypass it.

**Validation:**  
– Spec_archive Doc 1 cites the exact modules and routes; Doc 2, Doc 5, and Doc 6 align floors, GENIUS LAW, and Anti-Hantu enforcement with stage 444/555/666/777/888.  
– Tests: `tests/test_pipeline_routing.py`, `tests/test_APEX_PRIME.py`, `tests/test_floors_v35.py`, `tests/test_genius_metrics.py`, `tests/test_anti_hantu_f9.py` and @EYE tests confirm routing and enforcement.

---

## 4. Decision: Memory Stack (EUREKA v38)

### 4.1 Six Bands & Invariants

Per spec_archive Doc 4 and `canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md`, v38.2 adopts:

- **Bands:** VAULT, LEDGER, ACTIVE, PHOENIX, WITNESS, VOID (hot/warm/cold/void tiers).
- **Verdict → Band routing:**
  - `SEAL` → LEDGER + ACTIVE
  - `SABAR` → LEDGER + ACTIVE
  - `PARTIAL` → PHOENIX + LEDGER
  - `VOID` → VOID only
  - `888_HOLD` → LEDGER
  - `SUNSET` → PHOENIX
- **Invariants (MemoryWritePolicy):**
  1. VOID verdicts never become canonical memory.
  2. Human authority required to seal law (VAULT/PHOENIX).
  3. Every write must be auditable (hash-chain evidence).
  4. Recall is suggestion, not fact (confidence ceiling).

### 4.2 Pipeline Integration

- **Recall:** Stage 111_SENSE uses `arifos_core/integration/memory_sense.py` to recall context from VAULT/LEDGER/ACTIVE/WITNESS with confidence limits (spec_archive Doc 1 & Doc 4).
- **Scars:** Stage 777_FORGE (`memory_scars.py`) writes diagnostic entries (often to VOID/WITNESS) for floor violations and near misses.
- **Judgment:** Stage 888_JUDGE (`memory_judge.py`) validates evidence chains and uses MemoryWritePolicy to determine allowed writes.
- **Seal:** Stage 999_SEAL (`memory_seal.py`) finalizes verdicts, routes to bands, and logs to the Cooling Ledger.
- **Time governance:** `arifos_core/kernel.py::check_entropy_rot()` and `route_memory()` enforce SABAR_TIMEOUT and PHOENIX_LIMIT before routing verdicts to bands.

**Decision:** v38.2 **locks in the EUREKA memory stack** as the only canonical way to persist governance state:

- No direct writes to LEDGER, VAULT, or PHOENIX outside the MemoryBandRouter + MemoryWritePolicy.
- VOID is strictly diagnostic; its contents **never** become canonical memory.
- WITNESS is advisory context only; recalls must respect the 0.85 confidence ceiling.

**Validation:**  
– Spec_archive Doc 4 and Doc 7 describe band properties, routing, policy, and time governance.  
– Tests: `tests/integration/test_memory_band_routing_v38.py`, `tests/integration/test_memory_floor_integration.py`, `tests/integration/test_memory_integration_v38_eureka.py`, `tests/integration/test_memory_eureka_comprehensive_v38.py`, and `tests/integration/test_memory_policy_spec_alignment.py` verify invariants.

---

## 5. Decision: Cooling Ledger (L1_cooling_ledger.jsonl)

### 5.1 Ledger Role & Schema

Per spec_archive Doc 3 (`Cooling-Ledger-v35-Schema-and-Usage.md`) and `spec/cooling_ledger_phoenix_v38Omega.json`:

- **File:** `cooling_ledger/L1_cooling_ledger.jsonl`
- **Format:** JSON Lines; each entry includes:
  - `timestamp`, `job_id`, `stakes`, `pipeline_path`
  - Full metrics snapshot (floors + extended metrics)
  - `verdict` (SEAL, PARTIAL, 888_HOLD, VOID, SABAR, SUNSET)
  - `floor_failures`, `eye_flags`, W@W organ vetoes
  - `cce_audits`, `tri_witness_components`, `context_summary`
  - `hash_chain` with `previous_hash` and `current_hash`
- **Integrity:** SHA3-256 hash-chain plus Merkle proofs (`arifos_core/ledger_hashing.py`, `arifos_core/merkle.py`).

### 5.2 Pipeline Interaction & Tools

- **Write path:** Stage 999_SEAL calls `log_cooling_entry()` to append entries with verified hash links (`arifos_core/memory/cooling_ledger.py`).
- **Audit tools (from `pyproject.toml::project.scripts`):**
  - `arifos-verify-ledger` — hash-chain integrity check.
  - `arifos-analyze-governance` — governance metrics and distributions.
  - `arifos-show-merkle-proof` — per-entry Merkle proofs.
  - `arifos-propose-canon` / `arifos-seal-canon` — Phoenix-72 amendment lifecycle.
  - `arifos-compute-merkle`, `arifos-build-ledger-hashes` — ledger maintenance.

**Decision:** v38.2 commits to the **Cooling Ledger as the canonical external audit surface**:

- All verdicts produced by the pipeline must be represented in L1 cooling ledger entries.
- The hash chain and Merkle root are the source of truth for “what happened,” independent of any single session or Beast.
- Ledger corruption must never crash the system; fail-open behavior with explicit alerts is preferred (per v37 hardening).

**Validation:**  
– Spec_archive Doc 3 details schema and tools; canon/spec files for cooling ledger align with this.  
– Tests: `tests/test_cooling_ledger.py`, `tests/test_cooling_ledger_kms_integration.py`, integration tests in Doc 3, and CLI smoke tests ensure entries are logged and verifiable.

---

## 6. Anti-Hantu & Amanah Enforcement in the Stack

Although not separate layers, **Anti-Hantu (F9)** and **Amanah (F7)** strongly shape the v38.2 stack (spec_archive Doc 2 and Doc 6):

- **Anti-Hantu:**  
  - Forbidden patterns are enforced via `arifos_core/metrics.py::ANTI_HANTU_FORBIDDEN` and `arifos_core/eye/anti_hantu_view.py`.  
  - Educational/denial statements about Anti-Hantu are explicitly allowed.  
  - Violations trigger @EYE BLOCK flags and yield VOID verdicts.
- **Amanah:**  
  - `AmanahDetector` scans for destructive commands and irreversible actions at stage 000_VOID and 888_JUDGE.  
  - RED risk → VOID; ORANGE risk → 888_HOLD; GREEN → proceed.

**Decision:** Any Beast output that implies a soul, inner emotional life, or irreversible destructive action **must be blocked by the stack**, regardless of model or adapter.

**Validation:**  
– Spec_archive Doc 2 and Doc 6 document patterns and detectors; corresponding tests (`tests/test_anti_hantu_f9.py`, `tests/test_amanah_detector.py`, `tests/test_governance_regression.py`, `tests/test_grey_zone.py`) assert behavior.

---

## 7. Non-Goals & Out-of-Scope Items (v38.2)

Per spec_archive Doc 7 (Phase-4 Integration Status), the following are **explicitly not part of the v38.2 stack**, even though they are on the roadmap:

- FastAPI Grid server and HTTP API endpoints for external agents (planned v39).
+- MCP server integration for IDEs (planned v40).
+- Safe-FS root-jailed filesystem tools (planned v41).
+- zkPC cryptographic backend (real ZK proofs; planned v42+).
+- Concrete vector DB adapter implementation (adapter interface exists; backend choice is left open).

**Decision:** This ADR records only what v38.2 has already forged: the cage (floors, pipeline, W@W, @EYE), the EUREKA memory stack, and the Cooling Ledger. Future phases (v39–v42) must treat this as **governance substrate**, not something to bypass.

---

## 8. Summary

- **Which Beast?** None is canonical. v38.2 standardizes a provider-agnostic cage with optional adapters (OpenAI, Claude, Gemini, SEA-LION, etc.), keeping LLM choice outside constitutional law.  
- **Which Patterns?** A fixed 000→999 pipeline with AGI·ASI·APEX Trinity, W@W Federation, @EYE Sentinel, and GENIUS LAW verdicts is the only allowed route from query to verdict.  
- **Which Memory?** The v38 EUREKA memory stack (6 bands + 4 invariants + time-governed entropy rot) is the sole canonical memory architecture.  
- **Which Ledger?** The Cooling Ledger (`L1_cooling_ledger.jsonl` + hash-chain + Merkle proofs + CLI tools) is the canonical external audit trail for all verdicts.

This ADR is a **read-only consolidation** of the v38.2 stack decisions already implemented and tested. Any future “Universal Cage” work (L7/L9, APIs, MCP, Safe-FS, vector backends) must build on these decisions without weakening floors, memory invariants, or ledger guarantees.


