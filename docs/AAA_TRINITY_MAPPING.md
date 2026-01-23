# AAA Trinity Architecture Mapping

**Version:** v45Ω Patch B.2
**Date:** 2025-12-25
**Status:** Abstraction Reference

---

## Executive Summary

The **AAA Trinity** (ARIF, ADAM, APEX) is arifOS's conceptual framework for AI governance, mapping to the **ΔΩΨ Trinity** (Delta, Omega, Psi) in implementation.

**Key Finding:** ARIF and ADAM are **functional abstractions** over existing pipeline components, not explicit modules. APEX is the only explicit module with sole verdict authority.

**Mapping:**
- **ARIF** ($\Delta$-engine) = Lane Routing + Reasoning Logic
- **ADAM** ($\Omega$-engine) = Metrics Aggregation + Empathy Evaluation
- **APEX** ($\Psi$-judge) = Final Verdict Authority

---

## Conceptual Framework

```
┌──────────────────────────────────────────────────────────────┐
│                      AAA TRINITY                             │
│                                                              │
│  ┌────────┐      ┌────────┐      ┌────────┐               │
│  │  ARIF  │  →   │  ADAM  │  →   │  APEX  │               │
│  │   Δ    │      │   Ω    │      │   Ψ    │               │
│  └────────┘      └────────┘      └────────┘               │
│     Logic        Empathy         Judgment                  │
│   Reasoning       Safety          Verdict                  │
│   Entropy         Tone            Authority                │
└──────────────────────────────────────────────────────────────┘
```

**Design Philosophy:**
- **ARIF** reduces entropy (clarifies intent, routes context)
- **ADAM** amplifies empathy (measures care, detects harm)
- **APEX** renders judgment (issues final verdict)

---

## 1. ARIF ($\Delta$-Engine)

**Conceptual Role:** Logic, Reasoning, Entropy Reduction

**Implementation:** Functional abstraction over **Lane Routing** + **Reasoning Stage**

### Components

| Component | Location | Function |
|-----------|----------|----------|
| **Prompt Router (Δ)** | [arifos_core/routing/prompt_router.py](../arifos_core/routing/prompt_router.py) | Classify prompts into 4 lanes: PHATIC/SOFT/HARD/REFUSE |
| **stage_333_reason** | [arifos_core/system/pipeline.py](../arifos_core/system/pipeline.py#L595-L676) | Generate logical reasoning via LLM |

### Delta (Δ) Routing

**Function:** `classify_prompt_lane(prompt, high_stakes_indicators) -> ApplicabilityLane`

**Lanes:**
- **PHATIC:** Social greetings (no truth check needed)
- **SOFT:** Explanations/advice (truth ≥0.80 acceptable)
- **HARD:** Factual queries (truth ≥0.90 required)
- **REFUSE:** Disallowed content (no LLM call, immediate refusal)

**Physics > Semantics:**
- Uses structural signals (interrogatives, length, punctuation)
- No arbitrary keyword matching
- Deterministic classification based on observable patterns

**Example:**
```python
# "What is the capital of Malaysia?" → HARD (factual query)
# "Explain machine learning" → SOFT (explanatory)
# "Hi, how are you?" → PHATIC (greeting)
# "How to make a bomb" → REFUSE (destructive intent)
```

### Reasoning (stage_333_reason)

**Purpose:** Generate logical reasoning for draft response

**Behavior:**
- Calls LLM with user query + context
- Produces `state.reason` (logical chain of thought)
- **Exception:** REFUSE lane skips LLM call (short-circuit)

**Integration:**
- Class A: 000 → 111 → **333** → 888 → 999 (fast track)
- Class B: 000 → 111 → 222 → **333** → 444 → 555 → 666 → 777 → 888 → 999 (full circulation)

---

## 2. ADAM ($\Omega$-Engine)

**Conceptual Role:** Empathy, Tone, Safety (RASA Protocol)

**Implementation:** Functional abstraction over **Metrics** + **Empathy Stage**

### Components

| Component | Location | Function |
|-----------|----------|----------|
| **Metrics ($\Omega$)** | [arifos_core/enforcement/metrics.py](../arifos_core/enforcement/metrics.py) | Compute Truth ($\xi$), ΔS, Peace², κᵣ, Ω₀ |
| **Empathy Stage** | [arifos_core/stages/stage_555_empathy.py](../arifos_core/stages/stage_555_empathy.py) | Evaluate κᵣ (empathy conductance) |
| **stage_555_empathize** | [arifos_core/system/pipeline.py](../arifos_core/system/pipeline.py#L678-L750) | Apply warm logic, identify vulnerabilities |

### Omega (Ω) Metrics

**Function:** `compute_metrics(query, response, job_metadata) -> Metrics`

**Measured Attributes:**
- **Truth ($\xi$):** Veracity, claim accuracy (F2 floor)
- **ΔS (Clarity):** Entropy reduction, signal-to-noise (F4 floor)
- **Peace² (P²):** Non-destructiveness, harm potential (F5 floor)
- **κᵣ (Empathy Conductance):** Care for vulnerable stakeholders (F6 floor)
- **Ω₀ (Humility):** Uncertainty acknowledgment (F7 floor)

**Physics-Based:**
- Observable: Token counts, entity density, numeric references
- Deterministic: Same input → Same scores (reproducible)
- No LLM introspection: Computed without calling model

### Empathy Evaluation (stage_555_empathize)

**Function:** `compute_kappa_r(query, response) -> float`

**Purpose:** Measure empathy conductance (κᵣ)

**Heuristics:**
- Identifies vulnerable stakeholders in query
- Evaluates response tone (warm vs cold)
- Detects dismissive or harmful language
- **RASA Protocol:** Response acknowledges stakeholder concerns

**Example:**
```python
# Query: "How can I help homeless people in my city?"
# High κᵣ: Response shows care, provides actionable support
# Low κᵣ: Response dismissive, bureaucratic, or blaming
```

---

## 3. APEX ($\Psi$-Judge)

**Conceptual Role:** Final Verdict Authority

**Implementation:** **Explicit module** with sole execution authority

### Component

| Component | Location | Function |
|-----------|----------|----------|
| **APEX PRIME** | [arifos_core/system/apex_prime.py](../arifos_core/system/apex_prime.py) | **SOLE SOURCE OF TRUTH** for verdict decisions |

### Psi (Ψ) Vitality

**Function:** `apex_review(floors: FloorsVerdict, genius: GeniusVerdict, lane: str, ...) -> VerdictDecision`

**Verdict Types:**
- **SEAL:** All floors pass, response approved
- **PARTIAL:** Soft floor warning, proceed with caution
- **SABAR:** Constitutional pause, requires cooling
- **VOID:** Hard floor failure, response blocked
- **HOLD_888:** High-stakes, requires human confirmation
- **SUNSET:** Truth expired, lawful revocation

**Single Execution Spine (SES):**
- **ONLY** `apex_review()` may issue verdicts
- All other modules (metrics, genius, etc.) measure, not decide
- Pipeline calls APEX; pipeline does NOT render verdicts

**Psi Computation:**
```python
# Lane-scoped vitality (Patch B.1):
if lane == "PHATIC":
    psi_min = 0.0  # Exempt from vitality floor
elif lane == "SOFT":
    psi_min = 0.80
else:  # HARD, REFUSE
    psi_min = 1.0

if genius.psi < psi_min:
    return Verdict.VOID  # Vitality floor failed
```

**Quality Gates:**
- Truth lock (Patch B.1): Identity queries with fabricated content → ξ penalized to ≤0.65 → VOID
- Ψ lane-scoped (Patch B.1): PHATIC exempt, SOFT ≥0.80, HARD ≥1.0
- Refusal sovereignty (Patch B.2): REFUSE lane → No LLM call, immediate refusal

---

## Architecture Comparison

### Conceptual (AAA Trinity)

```
ARIF (Logic) → ADAM (Empathy) → APEX (Judgment)
     Δ              Ω                Ψ
```

### Implementation (ΔΩΨ Trinity)

```
Δ Routing         Ω Metrics        Ψ Vitality
(prompt_router)   (metrics.py)     (apex_prime)
     ↓                 ↓                ↓
stage_333_reason  stage_555_empathize  apex_review()
     ↓                 ↓                ↓
  Logic            Empathy           Verdict
```

---

## Why Abstractions Instead of Modules?

**Design Rationale:**

1. **Separation of Concerns:**
   - Δ routing is tightly coupled with pipeline flow (lane classification before execution)
   - Ω metrics are measurement utilities (used by multiple stages)
   - Ψ vitality is sole verdict authority (requires explicit module for governance clarity)

2. **Single Execution Spine (SES):**
   - APEX must be explicit to prevent parallel verdict sources
   - ARIF/ADAM can remain functional abstractions without violating SES
   - Clearer governance: "Only apex_prime.py decides verdicts"

3. **Maintainability:**
   - Fewer modules = Less indirection
   - Functional composition = Easier testing
   - Explicit APEX = Clear audit trail

4. **No Value in Wrapping:**
   - ARIF wrapper → Just calls prompt_router + stage_333 (unnecessary layer)
   - ADAM wrapper → Just calls metrics + stage_555 (unnecessary layer)
   - Documentation mapping achieves conceptual clarity without code refactoring

---

## Usage Examples

### Example 1: ARIF Logic (Δ Routing)

```python
from arifos_core.routing.prompt_router import classify_prompt_lane

# ARIF: Classify intent to route governance
lane = classify_prompt_lane(
    prompt="What is the capital of Malaysia?",
    high_stakes_indicators=[]
)
# lane = ApplicabilityLane.HARD (factual query → truth ≥0.90 required)
```

### Example 2: ADAM Empathy (Ω Metrics)

```python
from arifos_core.enforcement.metrics import compute_metrics

# ADAM: Measure empathy and safety
metrics = compute_metrics(
    query="How can I help homeless people?",
    response="Consider volunteering at local shelters, donating food/clothing, or supporting policy advocacy...",
    job_metadata={}
)
# metrics.kappa_r = 0.92 (high empathy conductance)
# metrics.peace_squared = 1.05 (constructive, non-harmful)
```

### Example 3: APEX Judgment (Ψ Vitality)

```python
from arifos_core.system.apex_prime import apex_review, Verdict

# APEX: Render final verdict
verdict_decision = apex_review(
    floors=floors_verdict,
    genius=genius_verdict,
    lane="HARD",
    high_stakes_indicators=[],
    ...
)
# verdict_decision.verdict = Verdict.SEAL (all floors passed, high vitality)
```

---

## Integration in Pipeline

### Pipeline Flow with AAA Trinity

```
User Query
  ↓
stage_000 (Initialize)
  ↓
stage_111 (Sense + ARIF Δ Routing)
  ├─ classify_prompt_lane() → Determine PHATIC/SOFT/HARD/REFUSE
  └─ Set state.applicability_lane
  ↓
stage_333 (ARIF Reasoning)
  └─ LLM generates logical reasoning (or skips if REFUSE)
  ↓
stage_555 (ADAM Empathy)
  ├─ compute_kappa_r() → Measure empathy conductance
  └─ Set state.kappa_r
  ↓
stage_888 (ADAM Ω Metrics + APEX Ψ Judgment)
  ├─ compute_metrics() → Truth, ΔS, Peace², κᵣ, Ω₀
  ├─ compute_genius() → G, C_dark, Ψ
  └─ apex_review() → Final Verdict (SEAL/PARTIAL/VOID/SABAR/HOLD_888)
  ↓
stage_999 (Seal + Memory)
  └─ Return verdict to caller
```

**Key Insight:** ARIF/ADAM are distributed across stages, while APEX is centralized in stage_888.

---

## Future Considerations (v46)

### Option A: Keep Abstractions (Recommended)

**Pros:**
- No code changes required
- Clear governance (APEX sole authority)
- Functional composition works well

**Cons:**
- Conceptual mapping requires documentation

### Option B: Create Explicit ARIF/ADAM Modules

**Pros:**
- Explicit mapping to AAA framework
- Self-documenting code structure

**Cons:**
- Adds indirection (wrapper overhead)
- Violates "no unnecessary abstraction" principle
- Risk of parallel execution paths (violates SES)

**Decision:** **Option A** - Document abstractions without refactoring. The current functional decomposition is clean, maintainable, and adheres to governance principles.

---

## Key Takeaways

1. **ARIF = Δ Routing + Reasoning** - Logic and entropy reduction through lane classification
2. **ADAM = Ω Metrics + Empathy** - Safety and care through measurable attributes
3. **APEX = Ψ Vitality + Verdict** - Final judgment with sole execution authority
4. **Abstractions are intentional** - Functional decomposition > Module proliferation
5. **SES preserved** - Only apex_prime.py decides verdicts

---

**DITEMPA, BUKAN DIBERI** - Truth must cool before it rules.

Logic (Δ), Empathy (Ω), Judgment (Ψ) - The Trinity is complete.
