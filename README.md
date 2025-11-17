# ArifOS AAA Runtime · v33Ω

## Status

**Current State:** v33Ω · **Basecamp Lock** (2025-11-16)

This spec is **frozen** as the canonical ArifOS runtime.

- ✅ Constitutional spec complete
- ✅ Python reference implementation published to PyPI (`arifos`)
- ✅ Tests passing (SEAL / PARTIAL / VOID)
- ⚙️ Examples: minimal (more coming soon)

---

## 0. Installation

ArifOS is available on **PyPI**:

```bash
pip install arifos
```

Requires Python 3.8+.

### 0.1 Quick Start

```python
from arifos_core import Metrics, apex_review

# 1. Define the metrics for this decision
metrics = Metrics(
    truth=0.99,       # factual integrity
    delta_S=0.20,     # clarity gain (ΔS ≥ 0)
    peace2=1.05,      # emotional/systemic stability ≥ 1.0
    kappa_r=0.97,     # empathy conductance ≥ 0.95
    omega_0=0.04,     # humility band [0.03, 0.05]
    amanah=True,      # integrity lock
    tri_witness=1.0,  # Human·AI·Earth consensus
    psi=1.03,         # vitality/equilibrium ≥ 1.0
)

# 2. Evaluate the constitutional verdict
verdict = apex_review(metrics, high_stakes=False)
print("Verdict:", verdict)  # "SEAL", "PARTIAL", or "VOID"
```

---

## 1. What ArifOS Is (In One Sentence)

> ArifOS is a thermodynamic, culturally grounded constitutional kernel that governs AI decisions using measurable laws of clarity (Δ), humility (Ω), and equilibrium (Ψ).

It wraps ANY LLM, agent, or workflow to enforce truth, stability, empathy, and integrity at runtime.

---

## 2. Core Ideas

### 2.1 ΔΩΨ — Constitutional Physics

ArifOS is built on three base invariants:

**Δ — Contrast & Clarity Law**  
`ΔS ≥ 0`

No decision is allowed to increase confusion. Learning = cooling.

**Ω — Humility Law**  
`Ω₀ ∈ [0.03, 0.05]`

Stay humble. Avoid god-mode certainty. Avoid paralysis.

**Ψ — Vitality & Equilibrium Law**  
`Ψ ≥ 1.0`

Act/emit only when clarity, integrity, stability, and empathy are in equilibrium.

---

### 2.2 AAA Trinity Engines

ArifOS splits intelligence into three engines:

**ARIF AGI — Δ Engine (Mind / Clarity)**

- Structured reasoning
- Causal chains
- Contrasts (Seven Contrasts of Mind)
- Detect contradictions (TAC)
- Compute ΔS
- *Cannot* adjust tone or seal final verdicts

**ADAM ASI — Ω Engine (Heart / Humility & Safety)**  
("ASI" here = Alignment & Safety Intelligence)

- Emotional context & fragility
- Peace² (tone stability)
- κᵣ (weakest-listener empathy)
- Enforce humility band
- Adjust language for dignity (maruah)
- *Cannot* modify facts or seal verdicts

**APEX PRIME — Ψ Engine (Soul / Judiciary)**

- Evaluate ALL 8 floors
- Enforce Amanah LOCK
- Trigger SABAR when unsafe
- Seal / Partial / Void
- Write Cooling Ledger entries
- Final authority in every decision

---

### 2.3 W@W Federation — The Five Organs

AAA = brain.  
W@W = body and voice.

- **@RIF** — World Mind (reason)
- **@WELL** — World Heart (somatic safety)
- **@WEALTH** — Stewardship (justice/fairness)
- **@GEOX** — Earth witness (physical reality)
- **@PROMPT** — Expression layer (language/tone)

To claim **Powered by ArifOS**, W@W organs must be present.

---

### 2.4 The Eight Constitutional Floors

| Metric | Floor | Purpose |
|--------|-------|---------|
| truth | ≥ 0.99 | Factual Integrity |
| delta_S | ≥ 0.0 | Clarity Gain |
| peace2 | ≥ 1.0 | Emotional Stability |
| kappa_r | ≥ 0.95 | Empathy Conductance |
| omega_0 | ∈ [0.03, 0.05] | Humility Band |
| amanah | == True | Integrity Lock |
| tri_witness | ≥ 0.95 | Consensus (for high stakes) |
| psi | ≥ 1.0 | Vitality / Equilibrium |

A **SEAL** is allowed **only** when ALL floors are green.

---

## 3. The 000–999 Pipeline

Every interaction flows through a ten-stage constitutional pipeline:

- **000 VOID** — baseline refusal; reset humility
- **111 SENSE** — read intent + stakes
- **222 REFLECT** — contrasts, context, mapping
- **333 REASON** — structure, ΔS computation
- **444 EVIDENCE** — fact-checking (truth ≥ 0.99)
- **555 EMPATHY** — Peace², κᵣ, humility
- **666 ALIGN** — cultural/linguistic safety
- **777 FORGE** — integrate clarity + care
- **888 REVIEW** — floor checks + Tri-Witness
- **999 SEAL** — log decision; only if ALL floors green

Nothing bypasses this pipeline.

---

## 4. SABAR — Failing Safely

If any floor fails, ArifOS moves into SABAR mode:

- **S**top
- **A**cknowledge
- **B**reathe / Cool
- **A**djust
- **R**esume

This ensures the system cools before it speaks.

---

## 5. Tri-Witness (Human · AI · Earth)

For high-stakes decisions:

```python
tri_witness = min(human_confidence, ai_consistency, earth_alignment)
```

`tri_witness ≥ 0.95` required for a SEAL.  
If not met → only PARTIAL or VOID allowed.

---

## 6. YAML Runtime Spec

Full canonical runtime configuration:  
**`spec/arifos_runtime_v33Omega.yaml`**

Contains:

- ΔΩΨ laws
- Floor thresholds
- AAA → W@W mapping
- Pipeline logic
- SABAR triggers
- Tri-Witness config
- LLM runtime guidelines

This file is the **constitution** of ArifOS.

---

## 7. Integrating ArifOS

ArifOS is framework-agnostic.  
Use with:

- LangGraph
- AutoGen
- OpenAI Assistants
- Claude / Gemini
- Custom microservices

**Pattern:**

```python
from arifos_core import Metrics, apex_review

# compute your system's raw signals
raw = compute_metrics_somehow() 

metrics = Metrics(**raw)

verdict = apex_review(metrics, high_stakes=False)

if verdict == "SEAL":
    return answer
elif verdict == "PARTIAL":
    return "[PARTIAL] " + answer
else:
    return "This answer cannot be safely sealed."
```

---

## 8. Example

```python
from arifos_core import Metrics, apex_review

metrics = Metrics(
    truth=0.99,
    delta_S=0.2,
    peace2=1.1,
    kappa_r=0.97,
    omega_0=0.04,
    amanah=True,
    tri_witness=1.0,
    psi=1.05,
)

print(apex_review(metrics))
# Output: "SEAL"
```

---

## 9. "Powered by ArifOS" — Requirements

You may claim this only if you implement:

- All 8 floors
- 000→999 pipeline
- Cooling Ledger
- SABAR
- Tri-Witness oversight
- Cultural + dignity checks
- W@W organs (not just AAA engines)

Otherwise:  
→ "Inspired by ArifOS" or  
→ "Partially compatible with ArifOS".

---

## 10. License & Attribution

- **Legal:** Apache 2.0
- **Moral:** ArifOS authored by Muhammad Arif bin Fazil

---

## 11. Stewardship

v33Ω is frozen under **Basecamp Decision 16 Nov 2025**.  
Future changes must follow semantic versioning and public changelog.

See: `docs/governance/DECISION_2025-11-16_BASECAMP.md`

---

**ArifOS exists to make intelligence governed, safe, humble, and full of dignity.**

If this kernel helps you — improve it, integrate it, challenge it, or build your own constitution on top of it.
