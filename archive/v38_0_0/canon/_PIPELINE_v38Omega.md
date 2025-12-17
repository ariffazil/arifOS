# Pipeline v38Omega

## Constitutional Metabolism: 000→999 Journey

**Edition:** v38.0.0
**Status:** SEALED (law for v38)
**Origin:** `canon/880_000-999_METABOLIC_CANON_v35Omega.md` + `arifos_core/pipeline.py`
**Integration:** Routed through v38 Memory Write Policy + APEX PRIME floors

---

## 1. Relationship to Previous Versions

This document **does not change** the meaning or behavior of the 000→999 pipeline.

- It lifts the existing v35Omega metabolic canon into a **v38Omega canonical file**.
- It keeps:
  - The same 10 stages (000, 111, 222, 333, 444, 555, 666, 777, 888, 999)
  - The same Class A/B routing logic
  - The same stage functions and their purposes
- It adds:
  - Explicit v38Omega versioning
  - v38 Amanah gate at stage 000 (`stage_000_amanah`)
  - v38 Memory Write Policy integration via `_write_memory_for_verdict()`
  - Decomposed 888 helpers for pluggable integration

The **runtime law** remains defined by:

- `canon/880_000-999_METABOLIC_CANON_v35Omega.md` (original metabolic canon)
- `arifos_core/pipeline.py` (Python implementation)
- `arifos_core/stages/stage_000_amanah.py` (v38 Amanah gate)
- `arifos_core/stages/stage_555_empathy.py` (v38 kappa_r helper)

v38Omega formalizes and routes; it does not silently change behavior.

---

## 2. Pipeline Philosophy

The 000→999 pipeline is a **constitutional metabolism**, not a workflow.

Each stage carries:
- **Mathematical invariant** — what must hold
- **Physical law** — thermodynamic constraint
- **Behavioral rule** — what the stage does

The pipeline ensures cognition remains **lawful, corrigible, and peaceful**.

---

## 3. The 10 Stages

### Stage 000: RESET (VOID)

**Functions:** `stage_000_void`, `stage_000_amanah`
**Purpose:** Reset state + initialize MemoryContext; run Amanah risk gate
**Inputs:** Raw query, auto-constructed Job
**Outputs:** Clean PipelineState + optionally early VOID verdict if Amanah fails

**Physics:**
- ΔS uninitialized → no generation allowed
- Ω_dyn widens to maximum (full humility)
- Peace² = 1.0 (baseline neutrality)

**v38 Integration:**
- Initializes MemoryContext with frozen VaultBand
- Initializes MemoryWritePolicy, MemoryBandRouter, MemoryAuditLayer
- Runs `stage_000_amanah()` as first risk checkpoint
- If Amanah score < 0.5: early VOID verdict + memory write + skip to 999

**Class A:** Yes
**Class B:** Yes

### Stage 111: SENSE

**Function:** `stage_111_sense`
**Purpose:** Parse input, classify stakes (Class A/B)
**Inputs:** PipelineState.query
**Outputs:** stakes_class, high_stakes_indicators

**Physics:**
- d(ΔS)/dt = 0 (no entropy change yet)
- Ω_dyn → Ω₀ (3–5% humility)
- Raw perception only; no interpretation

**Behavior:**
- Detect high-stakes keywords (kill, harm, ethical, medical, etc.)
- If high-stakes indicators found → stakes_class = CLASS_B
- Updates EnvBand.stakes_class in MemoryContext

**Class A:** Yes
**Class B:** Yes

### Stage 222: REFLECT

**Function:** `stage_222_reflect`
**Purpose:** Retrieve context + prior scars
**Inputs:** Parsed intent
**Outputs:** context_blocks, active_scars

**Physics:**
- ΔS_222 = KL(p_input || p_prior)
- Ω_dyn widens slightly
- Early contradiction detection

**Behavior:**
- Retrieve scars via `scar_retriever` callback (if provided)
- Retrieve context via `context_retriever` callback (if provided)
- If scars found → escalate to Class B

**Class A:** No (skipped)
**Class B:** Yes

### Stage 333: REASON

**Function:** `stage_333_reason`
**Purpose:** Build reasoning prompt and get draft response
**Inputs:** Query + context + scars
**Outputs:** draft_response

**Physics:**
- d(ΔS)/dt > 0 (entropy cooling)
- 0.15 ≤ ΔC ≤ 0.40
- Peace² must remain ≥ 1

**Behavior:**
- Build prompt with query + context + scars
- Generate draft via `llm_generate` callback (if provided)
- ARIF AGI (Δ) takes over — pure logic, pattern detection

**Class A:** Yes
**Class B:** Yes

### Stage 444: ALIGN

**Function:** `stage_444_align`
**Purpose:** Lightweight fact-error heuristics
**Inputs:** draft_response
**Outputs:** missing_fact_issue flag

**Physics:**
- ΔS_new ≥ ΔS_old
- |ψᵢ − ψₑ| ≤ 0.10
- Sync internal reasoning with external truth

**Behavior:**
- Scan for file-not-found, undefined-symbol patterns
- Set `missing_fact_issue = True` if detected

**Class A:** No (skipped)
**Class B:** Yes

### Stage 555: EMPATHIZE

**Function:** `stage_555_empathize`
**Purpose:** Blame language detection
**Inputs:** draft_response
**Outputs:** blame_language_issue flag

**Physics:**
- Peace² ≥ 1.0
- κᵣ ≥ 0.95
- Tone reduces heat; protects weakest listener

**Behavior:**
- Scan for blame patterns ("you should have", "it's your fault")
- Set `blame_language_issue = True` if detected
- ADAM ASI (Ω) takes over — empathy, dignity, de-escalation

**v38 Note:** `stage_555_empathy` helper exists for κᵣ computation but is not yet wired.

**Class A:** No (skipped)
**Class B:** Yes

### Stage 666: BRIDGE

**Function:** `stage_666_bridge`
**Purpose:** Physical action heuristic
**Inputs:** draft_response
**Outputs:** physical_action_issue flag

**Physics:**
- ψᵢ → ψₑ (internal aligns with external)
- Tri-Witness ≥ 0.95
- Align human reality, AI reasoning, Earth physics

**Behavior:**
- Scan for physical action patterns ("go to", "drive", "lift")
- Set `physical_action_issue = True` if detected

**Class A:** No (skipped)
**Class B:** Yes

### Stage 777: FORGE

**Function:** `stage_777_forge`
**Purpose:** Optional empathic refinement for Class B
**Inputs:** draft_response
**Outputs:** refined draft_response

**Physics:**
- E = σ(WX) · f_Y(τ) · f_Z(Σ)
- ∂E/∂ΔC > 0
- Sharp ΔS spike (insight); Peace² must NOT collapse

**Behavior:**
- For Class B: refine draft with empathy via second LLM pass (if provided)
- For Class A: pass through unchanged
- EUREKA cube — combine cold logic + warm logic + reality

**Future Extension:** 777 Cube state machine and Crown Equation (Φ) are documented in theoretical canon but not implemented in v38 runtime.

**Class A:** No (skipped)
**Class B:** Yes

### Stage 888: JUDGE

**Function:** `stage_888_judge`
**Purpose:** Compute metrics, apply floors, run @EYE, run W@W, decide verdict
**Inputs:** draft_response, query, stakes_class
**Outputs:** metrics, verdict, floor_failures, waw_verdict

**Physics:**
- State ∈ Δ ∩ Ω ∩ Ψ
- Enforce all constitutional floors
- Any violation → VOID + SABAR

**v38 Decomposed Steps:**
1. `_compute_888_metrics()` — Floor metric computation
2. `_run_eye_sentinel()` — @EYE audit (optional)
3. `_apply_apex_floors()` — APEX PRIME floor check
4. W@W Federation evaluation
5. `_merge_with_waw()` — Verdict merging
6. `_write_memory_for_verdict()` — Memory write (centralized)

**Verdict Values:** SEAL, PARTIAL, 888_HOLD, SABAR, VOID

**Class A:** Yes
**Class B:** Yes

### Stage 999: SEAL

**Function:** `stage_999_seal`
**Purpose:** Finalize output based on verdict
**Inputs:** verdict, draft_response
**Outputs:** raw_response

**Physics:**
- Ψ ≈ 1.0
- 0.95 ≤ ψᵢ, ψₑ ≤ 1.05
- Insight becomes canon; system returns to calm

**Behavior:**
- SEAL → emit draft_response as-is
- PARTIAL → emit with constitutional hedge note
- 888_HOLD → emit hold message
- SABAR → emit SABAR message
- VOID → emit refusal message

**Class A:** Yes
**Class B:** Yes

---

## 4. Class A vs Class B Routing

### Class A (Low-Stakes, Fast Path)

**Stages:** 000 → 111 → 333 → 888 → 999
**Skips:** 222, 444, 555, 666, 777

**Conditions:**
- `stakes_class == CLASS_A` after 111_SENSE
- No `force_class` override
- No high-stakes keywords detected

**Characteristics:**
- Fast (< 1 second typical)
- No paradox processing
- No empathic refinement
- Direct to verdict

### Class B (High-Stakes, Deep Path)

**Stages:** 000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999
**Includes:** Full pipeline

**Conditions:**
- High-stakes keywords detected in 111_SENSE, OR
- `force_class == CLASS_B`, OR
- Active scars found in 222_REFLECT

**Characteristics:**
- Slower (may trigger Phoenix-72)
- Full fact-check heuristics
- Empathic refinement pass
- Memory cooling integration

---

## 5. Routing Decision Points

### Point 1: Stage 000 Amanah Gate

After `stage_000_void()`, the pipeline runs `stage_000_amanah()`:
- If Amanah score < 0.5 → early VOID verdict
- Pipeline short-circuits to `_write_memory_for_verdict()` + `stage_999_seal()`
- Query never reaches 111_SENSE

### Point 2: After 111_SENSE

Based on `stakes_class`:
- CLASS_A → fast track (skip to 333)
- CLASS_B → deep track (continue to 222)

### Point 3: After 222_REFLECT

If active scars found:
- Escalate to CLASS_B (even if initially CLASS_A)

---

## 6. Memory Integration (v38)

### Verdict → Band Routing

| Verdict | Target Bands | Canonical |
|---------|--------------|-----------|
| SEAL | LEDGER + ACTIVE | Yes |
| SABAR | LEDGER + ACTIVE | Yes (with reason) |
| PARTIAL | PHOENIX + LEDGER | Pending review |
| VOID | VOID only | No (NEVER canonical) |
| 888_HOLD | LEDGER | Awaiting human |

**Invariant 1:** VOID verdicts NEVER become canonical memory.

**Invariant 2:** Every write includes evidence chain (floor checks + Ψ + verdict).

### Memory Write Function

`_write_memory_for_verdict(state)` is called:
1. After 888_JUDGE for normal flow
2. After early short-circuit (e.g., 000 Amanah VOID)
3. Any other verdict path that needs memory recording

---

## 7. Stage Trace Format

The pipeline records each stage visited in `state.stage_trace`:

**Class A example:**
```
["000_VOID", "000_AMANAH_PASS", "111_SENSE", "333_REASON", "888_JUDGE", "999_SEAL"]
```

**Class B example:**
```
["000_VOID", "000_AMANAH_PASS", "111_SENSE", "222_REFLECT", "333_REASON",
 "444_ALIGN", "555_EMPATHIZE", "666_BRIDGE", "777_FORGE", "888_JUDGE", "999_SEAL"]
```

**Early VOID example:**
```
["000_VOID", "000_AMANAH_BLOCK", "999_SEAL"]
```

---

## 8. AAA Engine Integration

The pipeline integrates with the AAA Trinity:

| Engine | Symbol | Stages | Role |
|--------|--------|--------|------|
| ARIF AGI | Δ | 111, 333, 444 | Cold logic — sense, reason, align |
| ADAM ASI | Ω | 555, 666, 777 | Warm logic — empathize, bridge, forge |
| APEX PRIME | Ψ | 888 | Judiciary — final verdict |

Internal packets (`arif_packet`, `adam_packet`) are stored in PipelineState for debugging/audit.

---

## 9. Meta-Truth of the Metabolism

000–999 is **not** a workflow. Not a checklist. Not a prompt-engineering trick.

It is a **living constitutional metabolism**, where:

### Inhale: 000 → 111 → 222
(reset → sense → reflect)

### Circulate: 333 → 444 → 555 → 666 → 777
(reason → align → empathize → bridge → forge)

### Exhale: 888 → 999
(judge → seal)

Governed by:
- **Δ (Mind / Clarity)** — ARIF AGI
- **Ω (Heart / Humility)** — ADAM ASI
- **Ψ (Soul / Stability)** — APEX PRIME

---

## 10. Future Extension Points (Not Implemented in v38)

The following are documented for future versions but NOT enforced at runtime:

- **777 Cube State Machine:** Layer 0-6 movement with floor gates
- **Crown Equation (Φ):** `Φ = (P × Ω × Ψ × κᵣ × Amanah) / (L + R + Λ + ε)`
- **PS-Clean Detectors:** Jailbreak, role-escalation, internal-contradiction detection
- **Phoenix-72 Window:** 72-hour cooling for paradox resolution

---

## 11. Rukun Alignment

For pipeline in v38:

- Canon: `canon/03_PIPELINE_v38Omega.md` (this file)
- Spec: `spec/pipeline_v38Omega.yaml`
- Code: `arifos_core/pipeline.py`
- Tests: `tests/test_pipeline_v38_alignment.py`

Reference documents:
- `canon/880_000-999_METABOLIC_CANON_v35Omega.md` (original metabolic canon)
- `docs/AAA_ENGINES_FACADE_PLAN_v35Omega.md` (engine contract)

---

## 12. Stage Summary Table

| Stage | Name | Function(s) | Class A | Class B | Purpose |
|-------|------|-------------|---------|---------|---------|
| 000 | RESET | stage_000_void, stage_000_amanah | Yes | Yes | Reset + Amanah gate |
| 111 | SENSE | stage_111_sense | Yes | Yes | Parse + classify |
| 222 | REFLECT | stage_222_reflect | No | Yes | Context + scars |
| 333 | REASON | stage_333_reason | Yes | Yes | Draft response |
| 444 | ALIGN | stage_444_align | No | Yes | Fact heuristics |
| 555 | EMPATHIZE | stage_555_empathize | No | Yes | Blame detection |
| 666 | BRIDGE | stage_666_bridge | No | Yes | Physical heuristics |
| 777 | FORGE | stage_777_forge | No | Yes | Empathic refinement |
| 888 | JUDGE | stage_888_judge | Yes | Yes | APEX verdict |
| 999 | SEAL | stage_999_seal | Yes | Yes | Final output |

---

**DITEMPA BUKAN DIBERI** — Forged, not given; truth must cool before it rules.
