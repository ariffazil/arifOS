# GENESIS/045 — The Three-Layer Separation Doctrine

> **Canonical correction: ART, ACT, and Kernel — with AAA as visibility, not governance.**
> **Authority:** F13 SOVEREIGN (Muhammad Arif bin Fazil, 888)
> **Status:** CANON · Forged 2026-06-21 · Sealed to VAULT999
> **SoT:** `ariffazil/arifOS/GENESIS/045_THREE_LAYER_SEPARATION.md`
> **Correction of:** GENESIS/040 (which miscounted Gate as a layer)

---

## 0. What This Document Is

**GENESIS/040 called Gate a "fourth layer." That was wrong.**

This document is the canonical correction. Gate is not a layer. Gate is the
constitutional eval hook that ART invokes to check Kernel floors (F1–F13)
before allowing a tool call. The real stack has **three physics layers**
(ART, ACT, Kernel) and **one visibility layer** (AAA).

**The four layers collapse to three:**

| False Layer | Actual Identity |
|-------------|-----------------|
| Gate (Ω) | Constitutional eval **function** inside ART, backed by Kernel's floors |

This restores orthogonality. There are now exactly **three physics layers**
(Ψ, Δ, Φ) and **one visibility layer** (👁).

---

## 1. The Corrected Layer Model

```
                  ┌──────────────────────────────────────────────┐
                  │           KERNEL (Φ — Law)                   │
                  │  "What is allowed?"                          │
                  │  Invariants · F1–F13 · Permissible state     │
                  │  Persistent — loaded once, never moves       │
                  └─────────────────────┬────────────────────────┘
                                        │ supplies floor definitions to
                                        │
              ┌─────────────────────────┼───────────────────────────┐
              │                         │                           │
              ▼                         ▼                           ▼
   ┌───────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
   │  ART (Ψ — Reflex) │    │  ACT (Δ — Ceremony) │    │  AAA (👁 — Visib.)  │
   │                   │    │                     │    │                     │
   │ "Is THIS call     │    │ "How to sequence    │    │ "Who sees what?"    │
   │  safe?"           │    │  ALL calls?"        │    │                     │
   │                   │    │                     │    │ Cockpit · A2A       │
   │ Tool metadata     │    │ Program graph       │    │ Agent registry      │
   │ Blast radius      │    │ Dependency order    │    │ 888_HOLD display    │
   │ Trust lifecycle   │    │ Staging + rollback  │    │ Human interface     │
   │ Reversibility     │    │ Multi-call          │    │                     │
   │                   │    │                     │    │                     │
   │ ┌─────────────┐   │    │                     │    │                     │
   │ │ Gate (eval) │───┤    │                     │    │                     │
   │ │ (calls      │   │    │                     │    │                     │
   │ │  Kernel     │   │    │                     │    │                     │
   │ │  floors)    │   │    │                     │    │                     │
   │ └─────────────┘   │    │                     │    │                     │
   └─────────┬─────────┘    └──────────┬──────────┘    └──────────┬──────────┘
             │                        │                          │
             └────────────────────────┼──────────────────────────┘
                                      │ all converge on
                                      ▼
                           ┌──────────────────────┐
                           │   A-FORGE (Hands)    │
                           │   "Execute this"     │
                           │   7071/7072          │
                           │   Tool call surface  │
                           └──────────┬───────────┘
                                      │
                                      ▼
                           ┌──────────────────────┐
                           │   WORLD + VAULT999   │
                           │   State mutation +   │
                           │   Sealed memory      │
                           └──────────────────────┘
```

---

## 2. What Each Layer Actually Is

### ART (Ψ) — Reflex. Single-call wisdom.

| Attribute | Value |
|-----------|-------|
| Timescale | Microsecond |
| Substrate | Tool metadata + risk heuristics |
| Question | "Is THIS single call safe?" |
| Output | PROCEED / HOLD / BLOCK / DEFAULT_OBSERVE |
| Ownership | `runtime/art/` — ≤500 lines, ceiling enforced |

ART is the **AKAL layer** — the reflexive judgment before any tool is touched.
It is not a planner, not a sequencer, not a kernel.

**Gate is inside ART.** Gate is a function call, not a layer. When ART needs
constitutional floor verification on a call, it invokes Gate, which calls
Kernel's floor definitions and returns PASS/HOLD/FAIL. ART decides what to
do with that verdict.

ART's internal flow:
```
incoming call → classify blast radius
             → check trust lifecycle (UNTRUSTED→OBSERVED→TRUSTED→FALLBACK)
             → Gate.eval(call)  ← calls Kernel floors
             → return PROCEED/HOLD/BLOCK
```

### ACT (Δ) — Ceremony. Multi-call orchestration.

| Attribute | Value |
|-----------|-------|
| Timescale | Millisecond–second |
| Substrate | Program graph + dependency ordering |
| Question | "How do we sequence ALL calls safely?" |
| Output | Execution plan + staging + rollback strategy |
| Ownership | `runtime/act/` — ≤300 lines, ceiling enforced |

ACT is the **ritual layer** — it ensures the agent does not behave like a
chaotic LLM loop. It stages, sequences, and compensates across N calls.

ACT does NOT evaluate constitutional floors. That is ART's job (via Gate).
ACT does NOT define what is lawful. That is Kernel's job.

ACT's internal flow:
```
incoming program → select pattern (SINGLE_SHOT / DANGEROUS_MIGRATION / HUMAN_IN_LOOP)
                 → stage N calls in dependency order
                 → for each stage: verify → advance → verify
                 → on failure: compensate (rollback partial/full)
```

### Gate (—) — Constitutional eval function (belongs inside ART)

| Attribute | Value |
|-----------|-------|
| Timescale | Sub-millisecond (same as ART) |
| Substrate | Constitutional floors (F1–F13) |
| Question | "Does this action violate law?" |
| Output | PASS / HOLD / FAIL |
| Ownership | `runtime/art/gate.py` (proposed) or folded into ART |

Gate is **not a layer.** It is a function that ART calls. Gate has:
- No independent lifecycle (same lifecycle as ART)
- No independent authority (borrows from Kernel)
- No independent timescale (same as ART)
- No independent scope (same call as ART)

Gate = `kernel.evaluate_floors(call_context)`
ART = `reflex(call) → gate(call) → reflex_decision`

### Kernel (Φ) — Law engine. The constitution.

| Attribute | Value |
|-----------|-------|
| Timescale | Persistent |
| Substrate | Constitutional physics (F1–F13, Δ, Ω, Ψ) |
| Question | "What is allowed in this universe?" |
| Output | Invariants + allowed transitions + forbidden states |
| Ownership | `runtime/kernel/`, `core/enforcement/`, `constitutional_map.py` |

Kernel defines the physics of the agentic universe:
- F1–F13 floor definitions and thresholds
- Permissible state transitions
- 000→999 metabolic pipeline
- Vault seal semantics
- Witness requirements

Kernel does NOT execute. Kernel does NOT stage. Kernel does NOT reflect on
individual tool calls. Kernel defines what IS.

### AAA (👁) — Visibility. Rendered state to human.

| Attribute | Value |
|-----------|-------|
| Timescale | Human-paced (seconds–minutes) |
| Substrate | React 19 dashboard + A2A gateway |
| Question | "Who sees what?" |
| Output | Rendered state + agent registry + HOLD queue |
| Ownership | AAA repo, port 3001 |

AAA has NO authority over:
- PROCEED/HOLD/BLOCK (that's ART)
- Execution order (that's ACT)
- What is lawful (that's Kernel)

AAA only:
- Renders governed state for Arif
- Hosts A2A mesh (agent discovery)
- Holds warga authentication boundary
- Displays 888_HOLD queue

---

## 2B. What the Stack Is NOT

| False Name | Reality | Verdict |
|------------|---------|---------|
| Gate as "4th layer" | Constitutional eval function inside ART | **HARAM** — not a substrate |
| pre_execution_gate as organ | ART library (`art/gate.py`) | **HARAM** — not a layer |
| "4-layer architecture" | 3 physics + 1 visibility | **MAKRUH** — the 4th was never a layer |

---

## 3. Why Gate Cannot Be a Layer

Gate violates all four orthogonality axes if treated as a layer:

| Axis | Gate's Violation |
|------|-----------------|
| **Time** | Gate has no independent timescale — it operates at ART's speed |
| **Authority** | Gate has no sovereign authority — it borrows all authority from Kernel |
| **Uncertainty** | Gate does not resolve entropy — it checks floors, which are static |
| **Scope** | Gate does not own calls — ART owns calls |

A layer must have:
1. Independent timescale (different temporal substrate)
2. Independent authority (owns its decision space)
3. Independent uncertainty resolution (reduces a distinct entropy class)
4. Independent scope boundary (owns a distinct unit of work)

Gate has none of these. It is purely functional, not architectural.

**The fix:** Fold `pre_execution_gate.py` into ART as a module or utility function.
Rename to `runtime/art/gate.py`. Gate is what ART calls, not what ART is.

---

## 4. The Four Orthogonal Axes (Physics-9 Compliant)

### 4.1 Time Axis

| Layer | Timescale | If collapsed → |
|-------|-----------|----------------|
| ART (Ψ) | microseconds | Contaminates Kernel with tool metadata |
| ACT (Δ) | milliseconds–seconds | Kernel becomes deployment strategy |
| Kernel (Φ) | persistent | Loses law purity |
| AAA (👁) | human-paced | Human cannot track machine time |

### 4.2 Authority Axis

| Layer | Authority | If collapsed → |
|-------|-----------|----------------|
| ART (Ψ) | Reflex — tool lifecycle | ACT becomes too fast, loses ceremony |
| ACT (Δ) | Orchestration — execution order | ART becomes too slow, loses reflex |
| Kernel (Φ) | Sovereign — what is lawful | No invariants to enforce |
| AAA (👁) | Visibility — observation only | Sovereignty without sight |

### 4.3 Uncertainty Axis

| Layer | Resolves | If collapsed → |
|-------|----------|----------------|
| ART (Ψ) | Tool-level uncertainty | Blast radius and trust lifecycle lost |
| ACT (Δ) | Program-level uncertainty | Multi-step staging becomes ad-hoc |
| Kernel (Φ) | Universe-level uncertainty | No foundation for floor enforcement |
| AAA (👁) | Human-level uncertainty | Arif cannot see what happened |

### 4.4 Scope Axis

| Layer | Unit | If collapsed → |
|-------|------|----------------|
| ART (Ψ) | 1 call | ACT tries to check each call individually |
| ACT (Δ) | N calls | ART tries to sequence N calls — impossible without program graph |
| Kernel (Φ) | All possible calls | Universe scope is lost |
| AAA (👁) | All rendered state | No single window into federation |

---

## 5. The Corrected Energy Flow

```
LLM proposes
  → ART.reflex(call)           # classify blast, trust, reversibility
      → ART.Gate.eval(call)    # call kernel floors via gate function
      → return PROCEED/HOLD
  → ACT.sequence(program)      # stage N calls in dependency order
  → For each stage:
      → ART.reflex(stage_N)    # re-check wisdom for this specific call
      → ART.Gate.eval(stage_N) # re-check floors for this call
      → A-FORGE.execute(stage_N)
      → ACT.verify(stage_N)    # verify outcome, advance or compensate
  → After all stages:
      → Kernel.log(VAULT999)   # seal the entire program
      → AAA.render(program)    # show Arif what happened
```

**Gate is a function, not a substrate.**

---

## 6. Correction to GENESIS/040

GENESIS/040 §0 "What This Document Is" lists:

```
| Layer | Question | File | Ceiling |
|-------|----------|------|---------|
| ART | Which tool move makes sense pre-call? | runtime/art.py | ≤500 lines |
| pre_execution_gate | Whether the call may proceed | runtime/pre_execution_gate.py | — |
| ACT | How to execute a program of lawful calls | runtime/act.py | ≤300 lines |
| Kernel / Floors / Judge | Whether the action is lawful | F1-F13 · 888 JUDGE | — |
```

**Corrected to:**

```
| Substrate | Question | File | Ceiling | Is A Layer? |
|-----------|----------|------|---------|-------------|
| ART (Ψ) | Which tool move makes sense pre-call? | runtime/art/ | ≤500 lines | ✅ YES — reflex layer |
| Gate (—) | Whether the call may proceed | runtime/art/gate.py | — | ❌ NO — eval function inside ART |
| ACT (Δ) | How to execute a program of lawful calls | runtime/act/ | ≤300 lines | ✅ YES — ceremony layer |
| Kernel (Φ) | Whether the action is lawful | F1-F13 · 888 JUDGE | — | ✅ YES — law layer |
| AAA (👁) | Who sees what? | AAA repo / :3001 | — | ✅ Visibility (non-governance) |
```

GENESIS/040 also states:

> **ART ≠ ACT. ACT ≠ Gate. ACT ≠ Kernel. Kernel ≠ ACT.**

This remains true. The corrected form adds:

> **Gate is not a layer. Gate is a function inside ART that calls Kernel floors.**

---

## 7. The HARAM Table (Corrected)

| Collapse | Result | Verdict |
|----------|--------|---------|
| ART → ACT | ART becomes >500 lines, loses reflex speed; ACT becomes epistemological | **HARAM** |
| ACT → ART | ART tries to sequence N calls — impossible without program graph | **HARAM** |
| ART → Kernel | Kernel gets contaminated with tool metadata, loses universality | **HARAM** |
| Kernel → ART | ART becomes >500 lines, loses reflex purity | **HARAM** |
| ACT → Kernel | Kernel becomes deployment strategy, loses law purity | **HARAM** |
| Kernel → ACT | ACT becomes sovereign, loses fail-open | **HARAM** |
| **Gate → Layer** | **False 4th layer violates orthogonality; Gate has no independent timescale, authority, uncertainty, or scope** | **HARAM** |

---

## 8. The File Restructuring Plan

| Current File | Correct Location | Rationale |
|-------------|-----------------|-----------|
| `runtime/pre_execution_gate.py` | `runtime/art/gate.py` | Gate is an ART library, not a standalone organ |
| `runtime/art.py` | `runtime/art/__init__.py` (stays) | ART ceiling ≤500 lines already enforced |
| `runtime/act.py` | `runtime/act/__init__.py` (stays) | ACT ceiling ≤300 lines already enforced |
| `runtime/act_library.py` | `runtime/act/library.py` (stays) | ACT submodule |

**Gate must never:**
- Import from ACT (ACT sequences; it does not evaluate floors)
- Import from AAA (AAA renders; it does not decide)
- Be imported by Kernel (Kernel defines law; it does not apply it per-call)
- Call itself a "layer" in any documentation

---

## 9. The One-Sentence Summary

> **ART makes the agent safe per-call. ACT makes the agent safe per-program.**
> **Gate is the constitutional eval function inside ART.**
> **Kernel makes the constitution safe from the agent.**
> **AAA makes the federation visible to Arif.**

**DITEMPA BUKAN DIBERI — Three physics layers forged. One visibility layer. Zero fake layers.**
