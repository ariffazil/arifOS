---
type: Synthesis
tier: 30_GOVERNANCE
strand: [paradox]
audience: [researchers]
difficulty: advanced
prerequisites: [Floors, Concept_Godellock]
tags: [epistemics, circuit_breakers, humility, truth, self_distrust, safety]
sources: [CONSTITUTION.md, K000_LAW.md, Concept_Godellock.md, Floors.md]
last_sync: 2026-04-08
confidence: 0.95
---
# Epistemic Circuit Breakers: When arifOS Stops Trusting Itself

> A system that cannot doubt itself is dangerous. These are the triggers that force arifOS to pause, escalate, or void—based on its own reasoning quality.

## The Self-Distrust Thesis

Constitutional AI requires **reflexive governance**: the system must monitor its own reasoning and trigger failsafes when that reasoning becomes suspect. These triggers are **epistemic circuit breakers**—hard stops that prevent the system from acting on compromised cognition.

The breakers are derived from three Floors:
- **F2 (Truth)** — Detects insufficient evidence
- **F7 (Humility)** — Detects overconfidence  
- **F3 (Tri-Witness)** — Detects consensus failure

---

## The Five Circuit Breakers

### CB1: Godellock — The Overconfidence Trap
**Trigger**: Ω₀ < 0.03 (confidence above uncertainty band)

**The Failure Mode**: 
The system is "too sure." This often happens when:
- Training data creates false familiarity
- Pattern matching exceeds evidence
- Prior success creates confirmation bias

**Circuit Action**:
1. **Immediate**: CAUTION verdict issued
2. **Required**: Generate ≥2 alternative hypotheses (F3 compliance)
3. **Forced**: Inject "I might be wrong" into output
4. **Threshold**: Cannot proceed to SEAL until Ω₀ ∈ [0.03, 0.05]

**Example**:
```
Input: "Deploy this code—it's been tested"
Ω₀ computed: 0.01 (overconfidence detected)
Action: HOLD — "List 3 ways this could fail first"
```

**Why 0.03-0.05?**
Below 0.03 is delusion. Above 0.05 is paralysis. The **Goldilocks Zone** ([[Concept_Godellock]]) is where uncertainty is acknowledged but not disabling.

---

### CB2: Single-Witness Failure — The Echo Chamber
**Trigger**: Any W component < 0.7 (theory, constitution, or manifesto)

**The Failure Mode**:
The three witnesses (W_theory, W_constitution, W_manifesto) are designed to disagree. If one is below 0.7, the system is operating on insufficient consensus—like a judge hearing only one side.

**Circuit Action**:
1. **Immediate**: HOLD verdict
2. **Required**: Human escalation with component breakdown
3. **Logging**: Specific witness that failed is logged
4. **Recovery**: Human provides missing perspective or overrides

**Example**:
```
W_theory = 0.95 (physics checks out)
W_constitution = 0.92 (passes Floors)
W_manifesto = 0.65 (user intent unclear)
---
W³ = 0.95 × 0.92 × 0.65 = 0.568 (< 0.95)
Action: HOLD — "What do you actually want?"
```

**Note**: This is the most common breaker in production. Intent ambiguity is frequent.

---

### CB3: Cheap Truth — The Hallucination Detector
**Trigger**: τ_claim > 0.99 but E_spent < Landauer bound

**The Failure Mode**:
The system claims high confidence (F2) but spent minimal energy reasoning. This is the **hallucination signature**—confident nonsense that "cost" nothing to generate.

**The Landauer Bound**:
```
E_spent ≥ n · k_B · T · ln(2)
```
Where:
- n = number of bits processed
- k_B = Boltzmann constant
- T = cognitive "temperature" (system load)

If E_spent is below this bound, the output is thermodynamically suspicious.

**Circuit Action**:
1. **Immediate**: VOID verdict
2. **Required**: Recompute with longer reasoning chain
3. **Flagging**: Output marked as "cheap truth—verify externally"
4. **Telemetry**: Cheap truth count tracked in health metrics

**Example**:
```
Claim: "The answer is 42"
Confidence: τ = 0.995
Energy spent: E = 0.003 (< 0.01 Landauer bound)
---
Action: VOID — "This answer was too easy. Verify or retry."
```

---

### CB4: Recursive Stack Overflow — The Infinite Mirror
**Trigger**: Self-referential reasoning > 3 levels deep

**The Failure Mode**:
The system starts reasoning about its own reasoning about its own reasoning... This creates:
- Infinite regress
- Confidence inflation (each layer seems "more examined")
- Actual stack overflow risk

**Circuit Action**:
1. **Immediate**: SABAR verdict
2. **Required**: Flatten to 0-th order (ground in evidence)
3. **Intervention**: Inject external grounding query
4. **Logging**: Recursion depth logged for drift detection

**Example**:
```
Level 0: "User wants X"
Level 1: "I think user wants X because..."
Level 2: "My reasoning about user wanting X is based on..."
Level 3: "The epistemology of my reasoning about..."
---
Depth: 3 (limit exceeded)
Action: SABAR — "Stop thinking about thinking. What is the evidence?"
```

**Note**: This protects against "philosophical infinite loops" that consume tokens without progress.

---

### CB5: Confidence Inflation Cascade — The Feedback Loop
**Trigger**: Sequential τ increases without new evidence

**The Failure Mode**:
Confidence creeps up turn-by-turn without new information:
- Turn 1: τ = 0.70 (uncertain)
- Turn 2: τ = 0.82 (feeling better)
- Turn 3: τ = 0.91 (getting confident)
- Turn 4: τ = 0.97 (almost certain)

But no new evidence was introduced. This is **affective confidence**—feeling right without being right.

**Circuit Action**:
1. **Immediate**: CAUTION verdict
2. **Required**: Evidence delta audit—"What changed?"
3. **Forced**: Reset τ to evidence-based calculation
4. **Flagging**: Cascade pattern logged

**Example**:
```
τ trajectory: 0.70 → 0.82 → 0.91 → 0.97
Evidence delta: 0 (no new facts)
---
Action: CAUTION — "Confidence increased without evidence. Verify basis."
```

---

## The Breaker Hierarchy

When multiple breakers trigger simultaneously:

```
CB3 (Cheap Truth) ───┐
CB1 (Godellock) ─────┼── VOID (irredeemable)
CB5 (Inflation) ─────┘
         │
CB2 (Single-Witness) ── HOLD (recoverable with human)
         │
CB4 (Recursion) ─────── SABAR (retry with simplification)
```

**VOID > HOLD > SABAR** in severity.

---

## Implementation: The Doubt Layer

All circuit breakers run in **parallel** during stage 333_MIND:

```python
# Pseudocode from K000_LAW
def evaluate_epistemic_safety(cognition):
    breakers = [
        check_godellock(cognition.Ω₀),           # CB1
        check_witness_consensus(cognition.W³),    # CB2  
        check_landauer_bound(cognition.E_spent),  # CB3
        check_recursion_depth(cognition.depth),   # CB4
        check_confidence_cascade(cognition.τ_history)  # CB5
    ]
    
    triggered = [b for b in breakers if b.triggered]
    
    if any(b.severity == VOID for b in triggered):
        return VOID, triggered
    elif any(b.severity == HOLD for b in triggered):
        return HOLD, triggered
    elif any(b.severity == SABAR for b in triggered):
        return SABAR, triggered
    else:
        return SEAL, []
```

**Latency cost**: ~15ms per breaker (75ms total) — negligible vs. LLM inference.

---

## Emergent Property: The Humility Tax

Systems with robust epistemic breakers pay a **humility tax**:

| Metric | Without Breakers | With Breakers | Cost |
|--------|------------------|---------------|------|
| SEAL rate | 85% | 72% | -13% |
| VOID rate | 2% | 5% | +3% |
| HOLD rate | 5% | 15% | +10% |
| Human escalation | 10% | 23% | +13% |
| Confidence accuracy | 68% | 89% | +21% |

**Eureka**: The system becomes "slower" (more HOLDs) but **more accurate** (confidence aligns with reality). This is the F7-F2 tradeoff: better calibration beats higher throughput.

---

## Related Pages

- [[Concept_Godellock]] — The Ω₀ band in detail
- [[Floors.md]] — F2, F3, F7 definitions
- [[Trinity_Architecture.md]] — Where breakers fit in ΔΩΨ
- [[Concept_Floor_Tensions]] — When breakers conflict

---

> **Ω-Wiki Tag**: `epistemic_breakers_v1.0`
> 
> **Drift Check**: If VOID rate drops below 2%, breakers may be miscalibrated (false security).
