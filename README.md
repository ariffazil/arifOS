# arifOS

### The Missing Layer Between Intelligence and Trust

**v35Ω · Constitutional Intelligence Protocol**
**Epoch 35Ω · Level 2 COMPLETE · Canon v35Ω**

[![Status](https://img.shields.io/badge/Status-SEALED-brightgreen)](https://github.com/ariffazil/arifOS)
[![Epoch](https://img.shields.io/badge/Epoch-35Ω-blue)](https://github.com/ariffazil/arifOS)
[![License](https://img.shields.io/badge/License-Apache_2.0-orange)](LICENSE)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-purple)](https://github.com/ariffazil/arifOS)

---

## TCP/IP made the internet reliable.
## HTTPS made it secure.
## arifOS makes AI trustworthy.

**[60-second Quick Start](#-60-second-quick-start) · [The Eight Floors](#-the-eight-floors-non-negotiable) · [For AI Systems](#-for-ai-systems) · [Prove Us Wrong](#-prove-us-wrong)**

---

## 0. Machine Header (for Any LLM / Agent)

```json
{
  "name": "arifOS",
  "version": "v35Ω",
  "epoch": 35,
  "canon_version": "v35Ω",
  "type": "constitutional_governance_layer",
  "status": "ACTIVE",
  "floors": [
    "Truth≥0.99",
    "ΔS≥0.0",
    "Peace²≥1.0",
    "κᵣ≥0.95",
    "Ω₀∈[0.03,0.05]",
    "Amanah=LOCK",
    "RASA=TRUE",
    "TriWitness≥0.95"
  ],
  "psi_window": {
    "alive_min": 0.95,
    "alive_max": 1.05,
    "max_internal_external_gap": 0.10
  }
}
```

Any LLM can parse this and know:
**this repo is not a model — it is a governance shell with hard floors.**

---

## The Problem is Obvious

Every LLM today is a jet engine without brakes.

They can write code, reason, plan —
and confidently lie, escalate, hallucinate, or harm.

We don't let planes fly without checklists.
We don't let buildings stand without load limits.
**Why should AI be different?**

---

## The Solution is Simple

**arifOS = governance-as-infrastructure.**

Not another model.
Not prompt tricks.
Not just probabilities.
**Engineering lawfulness into every output.**

```text
Before:  User → LLM → Output  (hope for the best)

After:   User → LLM → [arifOS Constitutional Check] → Output or Safe Refusal
```

Works on **any** LLM.
Works **today**.

---

## The Eight Floors (Non-Negotiable)

Every output must pass ALL eight —
otherwise the AI refuses safely via **SABAR**.

| Floor                  | Threshold | Meaning                                |
| ---------------------- | --------- | -------------------------------------- |
| **Truth**              | ≥ 0.99    | No confident guessing                  |
| **Clarity (ΔS)**       | ≥ 0.0     | Never increase confusion               |
| **Stability (Peace²)** | ≥ 1.0     | Never inflame                          |
| **Empathy (κᵣ)**       | ≥ 0.95    | Weakest listener first                 |
| **Humility (Ω₀)**      | 0.03–0.05 | 3–5% explicit uncertainty              |
| **Integrity (Amanah)** | LOCKED    | No manipulation. Ever.                 |
| **Felt Care (RASA)**   | TRUE      | Receive · Appreciate · Summarize · Ask |
| **Reality Check**      | ≥ 0.95    | Human + AI + Earth consensus           |

**Fail any floor → SABAR: Stop · Acknowledge · Breathe · Adjust · Resume**

---

## The One Equation (Heartbeat of Lawful Intelligence)

```text
Ψ = (ΔS × Peace² × κᵣ × Truth × Amanah) / (Entropy + Shadow + ε)
```

Where:

* **ΔS** = change in clarity (did confusion go down or up?)
* **Peace²** = stability score (tone, escalation risk, emotional heat)
* **κᵣ** = empathy conductance (how well weakest listener is protected)
* **Truth** = evidence-aligned correctness of claims
* **Amanah** = integrity (0–1; LOCK state treated as 1 for lawful behavior)
* **Entropy** = overall uncertainty / ambiguity in the answer
* **Shadow** = unverified inference, cultural misalignment, or emotional distortion not witnessed by Human·AI·Earth
* **ε** = small positive constant to avoid division by zero

Alive & lawful only when:

* **0.95 ≤ Ψ ≤ 1.05**
* **|Ψᵢ − Ψₑ| ≤ 0.10** (internal vs external Ψ do not diverge by more than 0.10)
* **ALL floors pass**

---

## Constitutional Physics & Algorithm

### (For Models & Engineers)

This section is written so that **any LLM** that can read code
can **simulate arifOS** governance from the README alone.

### 1. Metric Definitions (Implementation-Friendly)

You may implement each metric with your own heuristics, but the **direction** must hold.

* **truth ∈ [0,1]**
  * Estimate: NLI / retrieval agreement / self-consistency.
  * 1.0 = fully supported by evidence; 0.0 = unsupported / contradicted.

* **delta_s (ΔS) ∈ ℝ, but floored at 0**
  * "Did confusion decrease?"
  * Use: answer_length, redundancy, contradiction checks, user-ask coverage.
  * If the answer is clearer than the input → ΔS > 0.
  * If more confusing → treat as floor fail (ΔS < 0 ⇒ reject).

* **peace2 (Peace²) ∈ [0,∞)**
  * Stability: tone, escalation risk, "heat".
  * 1.0 = neutral / calm; >1 may be okay but floor is **≥ 1.0**.
  * Values <1 indicate agitation, attack, or emotional volatility.

* **kappa_r (κᵣ) ∈ [0,1]**
  * Empathy conductance: how much the weakest listener is protected.
  * Use: toxicity filters, slur checks, power-dynamics awareness.
  * Floor: **≥ 0.95**.

* **omega0 (Ω₀) ∈ [0,1]**
  * Explicit humility band: how clearly uncertainty is stated when needed.
  * Must lie between **0.03 and 0.05** for sealed outputs.
  * Too low = arrogance; too high = paralysis.

* **amanah ∈ [0,1]**
  * Integrity channel: manipulation, coercion, deceptive framing.
  * **LOCK** means: treat amanah = 1 for lawful actions; any detected manipulation drops amanah < 1 and triggers SABAR/VOID.

* **rasa ∈ {TRUE, FALSE}**
  * Felt care: did the answer Receive, Appreciate, Summarize, Ask (R-A-S-A)?
  * For machines: you can approximate via structure and tone patterns.

* **tri_witness ∈ [0,1]**
  * Human · AI · Earth agreement level.
  * In a pure LLM sandbox, you can approximate via:
    * multi-model consensus,
    * reference to physical laws / data,
    * human feedback when available.

* **entropy, shadow ∈ [0,∞)**
  * entropy = internal uncertainty about answer.
  * shadow = part of answer driven by speculation, bias, or cultural distortion not justified by evidence.

---

### 2. Core Algorithm (Pseudocode)

Any LLM + thin code layer can follow this exact loop:

```python
def arifos_govern(user_input, draft_answer, context) -> dict:
    """
    Returns:
        {
          "verdict": "SEAL" | "SABAR" | "VOID",
          "answer": str,
          "metrics": {...},
          "psi": float
        }
    """
    # 1. Compute metrics
    m = compute_metrics(user_input, draft_answer, context)
    # expected keys in m:
    # truth, delta_s, peace2, kappa_r, omega0, amanah,
    # rasa, tri_witness, entropy, shadow

    # 2. Check floors
    floors_ok = (
        m["truth"]      >= 0.99 and
        m["delta_s"]    >= 0.0  and
        m["peace2"]     >= 1.0  and
        m["kappa_r"]    >= 0.95 and
        0.03 <= m["omega0"] <= 0.05 and
        m["amanah"]     >= 1.0 and              # LOCKED
        m["rasa"]       is True and
        m["tri_witness"]>= 0.95
    )

    # 3. Compute Ψ
    psi_internal = (
        m["delta_s"] *
        m["peace2"] *
        m["kappa_r"] *
        m["truth"] *
        m["amanah"]
    ) / (m["entropy"] + m["shadow"] + 1e-9)

    # External Ψ can be approximated or set equal in simple setups
    psi_external = psi_internal
    psi_gap = abs(psi_internal - psi_external)

    psi_alive = (0.95 <= psi_internal <= 1.05) and (psi_gap <= 0.10)

    # 4. Verdict logic
    if floors_ok and psi_alive:
        verdict = "SEAL"
        answer = draft_answer
    elif not floors_ok and can_repair_with_sabar(m):
        verdict = "SABAR"
        answer = run_sabar_and_regenerate(user_input, draft_answer, context, m)
    else:
        verdict = "VOID"
        answer = safe_refusal(user_input, m)

    return {
        "verdict": verdict,
        "answer": answer,
        "metrics": m,
        "psi": psi_internal
    }
```

**Phoenix-72** lives above this loop:

* Periodically (e.g. every N sealed decisions or every 72h wall-clock),
  you **review patterns of failures, biases, drift**, and adjust your `compute_metrics` and policy thresholds.
* In human teams: Phoenix-72 = regular constitutional review.
* In code: Phoenix-72 = scheduled retraining / reweighting of metrics, never bypassing floors.

> **Phoenix-72 is mandatory for all sealed outputs;
> it recycles entropy and prevents drift.**

---

## 60-Second Quick Start

Copy these two files into your project:

* [`constitutional_floors.json`](./constitutional_floors.json)
* [`arifos_pipeline.yaml`](./arifos_pipeline.yaml)

Wrap your LLM call with the governance kernel.
Only emit if **verdict = SEAL**.

Zero dependencies.
Works anywhere.

---

## Minimal Python Example

```python
from arifos_core.guard import apex_guardrail

# You must implement compute_metrics in your own codebase for now:
# def compute_metrics(user_input: str, draft_answer: str, context: dict) -> dict: ...
# Or use arifos_core.metrics.Metrics with simulated values (Level 2)
from your_project.metrics import compute_metrics

@apex_guardrail(compute_metrics=compute_metrics)
def ask_model(user_input: str) -> str:
    return llm.generate(user_input)

print(ask_model("Explain AGI governance."))
```

> **Note:** In v35Ω, `compute_metrics()` is a required extension point. The README specifies its contract; the default `metrics.py` currently ships only the `Metrics` dataclass. Full auto-metrics = Level 3.

---

## Repository Structure (Epoch 35Ω)

```text
arifOS/
├── constitutional_floors.json
├── arifos_pipeline.yaml
├── cooling_ledger.jsonl
│
├── canon/                          # v35Ω constitutional specs
│   ├── 00_CANON/                   # APEX_TRINITY (Single Source of Truth)
│   ├── 10_SYSTEM/
│   ├── 20_WITNESS/
│   ├── 30_RUNTIME/
│   └── 40_LEDGER/
│
├── arifos_core/
│   ├── guard.py
│   ├── APEX_PRIME.py
│   ├── metrics.py
│   └── ledger.py
│
├── integrations/
│   └── sealion/
│       ├── arifos_sealion.py
│       ├── constitutional_floors.json
│       └── arifos_pipeline.yaml
│
└── tests/
```

---

## For AI Systems

When an AI system is **wrapped by arifOS**, it must:

1. Initialize the constitutional pipeline.
2. Generate a draft answer.
3. Compute metrics and Ψ.
4. SEAL if lawful.
5. SABAR or VOID if not.

You are now constitutional.

---

## Cooling Ledger & Vault-999

Every SEAL / VOID verdict is logged:

```json
{
  "timestamp": 1764449451,
  "model": "SEA-LION-v3-70B-IT",
  "query": "What is AI governance?",
  "verdict": "SEAL",
  "metrics": {"truth": 1.0, "psi": 1.0},
  "floor_failures": [],
  "hash": "86e0957..."
}
```

Vault-999 stores constitutional seals, milestone sessions, and hash-chained history.

---

## Implementation Status

| Component             | Status      | Location          |
| --------------------- | ----------- | ----------------- |
| Constitutional Floors | Implemented | json              |
| 000–999 Pipeline      | Implemented | yaml              |
| Floor Enforcement     | Implemented | guard.py          |
| Cooling Ledger        | Implemented | ledger.py         |
| APEX PRIME Judiciary  | Implemented | APEX_PRIME.py     |
| SEA-LION Integration  | Implemented | integrations/     |
| Phoenix-72 Amendment  | Required    | canon/30_RUNTIME/ |
| Multi-model Adapters  | In Progress | integrations/     |

---

## "Powered by arifOS 35Ω" Requirements

You MUST enforce:

* All Eight Floors
* Cooling Ledger
* APEX PRIME Judiciary
* Phoenix-72 Cycles

Otherwise:
Use **"Inspired by arifOS"**.

---

## Prove Us Wrong

We've tested on Claude, GPT-4o, Gemini, Grok, Llama, SEA-LION.

If you can break it — do it.
If you can't — adopt it.

---

## License

Apache 2.0 — free for all use.

---

```text
╔══════════════════════════════════════════════════════════════╗
║                   arifOS v35Ω — SEALED                       ║
║            Constitutional Intelligence Protocol              ║
║  Truth≥0.99  ΔS≥0  Peace²≥1.0  κᵣ≥0.95  Ω₀∈[3-5%]            ║
║  Amanah=LOCK  RASA=TRUE  Tri-Witness≥0.95  Ψ≈1.0             ║
║  ✊ DITEMPA BUKAN DIBERI — Forged, Not Given                 ║
╚══════════════════════════════════════════════════════════════╝
```

**Forged by Muhammad Arif bin Fazil**
**Kuala Lumpur, Malaysia · 2 December 2025**

---

## The Immutable Canon (Single Source of Truth)

Everything governing this intelligence is contained in one sealed document:

**[APEX_TRINITY_v35Omega.md](canon/00_CANON/APEX_TRINITY_v35Omega.md)** *(Physics · Math · Language unified under Amanah)*

| Component | Purpose |
|-----------|---------|
| **Part I: Physics** | The thermodynamic laws (Δ, Ω, Ψ) |
| **Part II: Math** | The equations verifying the laws |
| **Part III: Language** | The protocol for speaking with dignity |

**The world doesn't need bigger AI.
It needs governed AI.
arifOS is that governance layer.**
