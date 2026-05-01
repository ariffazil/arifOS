# Constitutional Quotes — Ingestion Guide

**Version:** 1.0.0  
**Total Quotes:** 102 human calibration anchors  
**Tools Covered:** 10 arifOS organs

---

## Design Philosophy

> **Quotes are nudges, not dogma.**  
> **Human witness signals, not constitutional replacement.**

Each quote:
- Maps to a reasoning function (not decoration)
- Maps to a tool output field
- Is real, attributable, human
- Is short enough to survive embedding/retrieval/prompt compression
- Triggers based on runtime conditions

---

## Quote Inventory by Tool

| Tool | Stage | Trinity | Quotes | Core Function |
|------|-------|---------|--------|---------------|
| `arifos.init` | 000_INIT | Δ | 10 | Anchor identity, establish sovereignty |
| `arifos.sense` | 111_SENSE | Δ | 11 | Ground reality, classify truth |
| `arifos.mind` | 333_MIND | Δ | 11 | Synthesize, reason, structure |
| `arifos.heart` | 666_HEART | Ω | 10 | Safety critique, dignity guard |
| `arifos.judge` | 888_JUDGE | Ψ | 10 | Final decision, verdict, authority |
| `arifos.vault` | 999_VAULT | Ψ | 10 | Seal, record, canonical archive |
| `arifos.memory` | 555_MEMORY | Ω | 10 | Store, retrieve, learn, adapt |
| `arifos.route` | 444_ROUTER | Δ | 10 | Route, orchestrate, dispatch |
| `arifos.ops` | 777_OPS | Ψ | 10 | Execute, implement, operate |
| `arifos.forge` | 888_FORGE | Δ | 10 | Create, build, design, synthesize |

**Total: 102 human calibration anchors**

---

## Category Mapping

### 8 Categories → Tool Output Fields

| Category | Disciplines | Output Mapping |
|----------|-------------|----------------|
| `reality_perception` | What is seen vs what is true | grounding, observation_notes, frame_check |
| `logic_truth` | Coherence, contradiction, validity | reasoning_chain, consistency_check, truth_assessment |
| `uncertainty_humility` | Limits of knowledge, confidence bounds | uncertainty, confidence, omega0_cap |
| `knowledge_selfknowledge` | Knowns, unknowns, assumptions | knowns, unknowns, assumptions |
| `ethics_dignity` | Harm bounds, respect, means vs ends | ethical_flags, human_impact, dignity_check |
| `action_judgment` | Decision under constraint | options, tradeoffs, recommended_next_step |
| `time_change` | Impermanence, drift, adaptation | temporal_context, change_risk, stability_check |
| `order_complexity_limits` | Entropy, systems, scale, fragility | system_map, failure_modes, complexity_note |

---

## Attribution Hygiene

| Status | Meaning | Example |
|--------|---------|---------|
| `exact` | Verifiable wording | Feynman, Newton, Clifford |
| `traditional_attribution` | Common form, ancient sources | Socrates, Heraclitus |
| `paraphrase` | Spirit preserved, wording modern | "The only constant in life is change" |
| `attributed` | Widely cited, exact source debated | Einstein simplicity quote |
| `summary_attribution` | Summary of larger work | Will Durant on Aristotle |
| `common` | Folk wisdom, no single author | "First things first" |

**Critical:** Do not treat all quotes as equally authoritative. Mark epistemic status clearly.

---

## Trigger Conditions

Quotes activate based on runtime signals:

```json
{
  "trigger_when": [
    "overconfidence",
    "weak_evidence", 
    "high_conflict",
    "ethical_decision",
    "time_pressure",
    "uncertainty_high"
  ]
}
```

**Not decoration. Conditional calibration.**

---

## Core 8 Seed Quotes (Default Set)

If loading only the strongest anchors:

| # | Quote | Author | Tool | Function |
|---|-------|--------|------|----------|
| 1 | "The first principle is that you must not fool yourself" | Feynman | mind | Self-deception guard |
| 2 | "It is wrong... to believe anything upon insufficient evidence" | Clifford | mind | Evidence threshold |
| 3 | "To know what you know and what you do not know" | Confucius | mind | Known/unknown partition |
| 4 | "The unexamined life is not worth living" | Socrates | mind | Reflective depth |
| 5 | "Primum non nocere" | Hippocrates | heart | Harm prevention |
| 6 | "Act only according to that maxim..." | Kant | heart | Universalizability |
| 7 | "We are more often frightened than hurt" | Seneca | sense | Reality/perception gap |
| 8 | "No man ever steps in the same river twice" | Heraclitus | sense | Change awareness |

---

## Usage Modes

| Mode | When Used |
|------|-----------|
| `reason` | Active analysis, chain-of-thought |
| `reflect` | Introspection, assumption interrogation |
| `forge` | Creation, design, synthesis |
| `judge` | Decision, verdict, final call |
| `sense` | Grounding, observation, evidence |

---

## JSON Schema

```json
{
  "quote_id": "TOOL_Q_###",
  "category": "category_name",
  "author": "Full Name",
  "quote": "The human wisdom text",
  "attribution_status": "exact|traditional_attribution|paraphrase|attributed|summary_attribution|common",
  "function": ["reasoning_function_1", "reasoning_function_2"],
  "trigger_when": ["condition_1", "condition_2"],
  "use_mode": ["reason", "reflect", "forge"]
}
```

---

## Ingestion Example

```python
import json

# Load quotes
with open('constitutional_quotes.json') as f:
    corpus = json.load(f)

# Get mind quotes
mind_quotes = corpus['arifos.mind']['quotes']

# Filter by trigger
relevant = [q for q in mind_quotes 
            if 'overconfidence' in q['trigger_when']]

# Use in prompt
for q in relevant:
    print(f"[{q['author']}] {q['quote']}")
```

---

## Warning: Anti-Patterns

❌ **Do NOT:**
- Use quotes as deterministic rules
- Treat all quotes as equally authoritative
- Let quotes override evidence and logic
- Use quotes as "decorative prompt perfume"
- Quote without attribution status

✅ **DO:**
- Use quotes as human witness signals
- Let evidence, logic, and constraints outrank quotes
- Mark attribution status honestly
- Trigger conditionally based on runtime state
- Keep quotes short for compression survival

---

## Files

| File | Purpose |
|------|---------|
| `constitutional_quotes.json` | Master corpus (102 quotes) |
| `QUOTES_INGESTION_GUIDE.md` | This guide |

---

## Constitutional Reminder

> **Quotes may nudge, but evidence, logic, and constraints still outrank them.**

Human wisdom is calibration, not constitution. 🔐

---

*DITEMPA BUKAN DIBERI — Forged, Not Given*
