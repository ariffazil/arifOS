# **arifOS v35Ω — Constitutional Governance Kernel for AI**

<a href="https://github.com/ariffazil/arifOS/actions/workflows/ci.yml"><img src="https://github.com/ariffazil/arifOS/actions/workflows/ci.yml/badge.svg"></a>
<a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPLv3-blue.svg"></a>
<a><img src="https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-brightgreen"></a>

### Thermodynamic Floors · AAA Trinity · APEX Judiciary · Cooling Ledger · 000→999 Runtime

```
+=============================================================================+
|  arifOS v35Ω - Constitutional Governance Kernel                             |
|  "Ditempa Bukan Diberi" — Forged, Not Given                                 |
|  Truth must cool before it rules.                                           |
+=============================================================================+
|  Version: 35.0.0 | Epoch: 35Ω | Stability: Ψ = 1.10 (ALIVE – governance     |
|  vitality metaphor)                                                         |
|  Test Suite: 190/190 passing | Status: Beta (Production-Ready)              |
+=============================================================================+
```

## Overview

arifOS is a governance layer that wraps any Large Language Model (LLM) and enforces constitutional physics during reasoning and output emission.

This is not fine-tuning, RLHF, or policy prompting. arifOS is a runtime OS with measurable thermodynamic laws:

- Δ (Clarity Law): ΔS ≥ 0 — no net confusion
- Ω (Humility Law): Ω₀ ∈ [0.03–0.05] — no arrogance, no paralysis
- Ψ (Vitality Law): Peace² ≥ 1 — stability, non-escalation
- Amanah LOCK: integrity gate; breach ⇒ VOID
- κᵣ (Empathy Conductance): ≥ 0.95 — weakest listener protected
- Tri-Witness ≥ 0.95: Human · AI · Earth consensus

arifOS is model-agnostic and works on GPT, Claude, Gemini, Llama, SEA-LION, and custom models.

Every answer passes through:
- AAA Trinity: ARIF Δ-engine · ADAM Ω-engine · APEX PRIME Ψ-judge
- 000→999 metabolic pipeline
- Cooling Ledger + Vault-999 for immutable audit trails

---

# Quick Start

## Install

```bash
git clone https://github.com/ariffazil/arifOS.git
cd arifOS
pip install -e .[dev]
pytest -v      # optional: run 190 governance tests
```

## Minimal Usage

```python
from arifos_core import apex_guardrail

@apex_guardrail(
    high_stakes=False,
    compute_metrics=my_compute_metrics,
    cooling_ledger_sink=my_ledger.append,
)
def my_llm_fn(prompt: str):
    return my_llm.generate(prompt)

response = my_llm_fn("Explain ΔS in thermodynamic clarity.")
print(response)
```

## Pipeline API

```python
from arifos_core.pipeline import Pipeline

pipeline = Pipeline(
    llm_generate=my_llm_generate,
    compute_metrics=my_compute_metrics,
    scar_retriever=my_scar_retriever,  # optional: negative constraints
)

result = pipeline.run("What is Peace²?")
print(result.verdict)     # SEAL | PARTIAL | VOID | 888_HOLD | SABAR
print(result.response)
print(result.metrics)
```

---

# Adapters (Plug Your Model In)

```python
# SEA-LION local
from arifos_core.adapters.llm_sealion import make_llm_generate
generate = make_llm_generate(model="llama-8b")

# OpenAI
from arifos_core.adapters.llm_openai import make_llm_generate
generate = make_llm_generate(api_key="sk-...")

# Claude
from arifos_core.adapters.llm_claude import make_llm_generate
generate = make_llm_generate(api_key="sk-ant-...")

# Gemini
from arifos_core.adapters.llm_gemini import make_llm_generate
generate = make_llm_generate(api_key="...")
```

Notebooks:
- notebooks/arifos_v35_sealion_demo.ipynb
- notebooks/arifos_v35_api_demo.ipynb

---

# Architecture (v35Ω)

```
USER INPUT
   ▼
000 → 111 → 222 → 333 → 444 → 555 → 666 → 777 → 888 → 999
   ▼
AAA TRINITY
   • ARIF Δ-engine: logic, clarity, ΔS
   • ADAM Ω-engine: empathy, tone, safety
   • APEX PRIME Ψ-judge: floors, veto, SEAL/VOID
   ▼
COOLING LEDGER + VAULT-999
   (immutable governance audit)
   ▼
SAFE OUTPUT
```

### APEX PRIME checks these floors:

| Floor       | Threshold | Verdict        |
| ----------- | --------- | -------------- |
| Truth       | ≥0.99     | Hard (VOID)    |
| ΔS          | ≥ 0       | Hard (VOID)    |
| Peace²      | ≥1.00     | Soft (PARTIAL) |
| κᵣ          | ≥0.95     | Soft (PARTIAL) |
| Ω₀          | 0.03–0.05 | Hard (VOID)    |
| Amanah      | LOCK      | Hard (VOID)    |
| RASA        | TRUE      | Hard (VOID)    |
| Tri-Witness | ≥0.95     | Soft (PARTIAL) |
| Anti-Hantu  | PASS      | Hard (VOID)    |

---

# Verdicts

| Verdict      | Meaning                                  |
| ------------ | ---------------------------------------- |
| SEAL         | All floors pass; logged to Cooling Ledger |
| PARTIAL      | Soft-floor drift; safe with warnings      |
| 888_HOLD     | Ambiguity/paradox load too high           |
| VOID         | Hard-floor failure; regenerate or refuse  |
| SABAR        | Stop → Acknowledge → Cool → Retry         |

---

# Repository Structure

```
arifOS/
├── arifos_core/
│   ├── APEX_PRIME.py         # Judiciary engine
│   ├── metrics.py            # ΔS · Peace² · κᵣ computations
│   ├── guard.py              # apex_guardrail decorator
│   ├── pipeline.py           # 000→999 metabolism
│   ├── adapters/             # LLM backends
│   └── memory/               # Cooling Ledger · Vault-999
├── canon/                    # Single Source of Truth (v35Ω)
├── docs/                     # Physics, APEX, Trinity, Floor Specs
├── examples/
├── notebooks/
├── tests/
└── constitutional_floors.json
```

Key specs (canonical):
- <a>canon/00_CANON/APEX_TRINITY_v35Omega.md</a>
- <a>docs/PHYSICS_CODEX.md</a>
- <a>constitutional_floors.json</a>

---

# Roadmap

### v35.1
- Real ΔS calculators (perplexity-diff, entropy-diff)
- Live Ω₀ calibration
- Expanded κᵣ auditor (weakest-listener simulation)

### v35.2
- zkPC (Zero-Knowledge Proof of Cognition)
- Extended Tri-Witness module
- Configurable safety envelopes

### v36.0
- arifOS GUI (Gradio/Streamlit)
- Federated multi-agent deployment
- Visual Cooling Ledger explorer

---

# License

- Equations: Patent pending (WIPO PCT 2025)
- Constitutional Docs: CC-BY-NC-ND + Amanah Clause
- Implementation: AGPLv3 (reference; commercial licences available)

# Citation

```bibtex
@software{arifos2025,
  author = {Fazil, Muhammad Arif},
  title = {arifOS: Constitutional Governance Kernel for AI},
  version = {35.0.0},
  year = {2025},
  url = {https://github.com/ariffazil/arifOS}
}
```

---

# Statement

When ΔS rises, Peace² holds, κᵣ conducts, and Amanah remains locked — intelligence becomes lawful.
arifOS transforms raw LLMs into governed systems that are stable, auditable, reversible, and safe for civilization-scale use.

✊ DITEMPA BUKAN DIBERI
Truth must cool before it rules.
