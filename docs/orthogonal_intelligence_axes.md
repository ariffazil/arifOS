# Orthogonal Invariant Intelligence Axes — APEX Hardening Reference

> **Source:** arifOS Cognitive Metabolism Kernel (333_MIND v2)
> **Date:** 2026-05-26
> **Status:** SEALED — DITEMPA BUKAN DIBERI

---

## The False Chain to Reject

```
scale → intelligence → truth → alignment → governance
```

Scale does not imply intelligence. Intelligence does not imply truth. Truth does not imply alignment. Alignment does not imply governance. **Governance must be designed in, not hoped for.**

---

## 25 Orthogonal Invariant Axes

Each axis is **orthogonal** — a high score on one does NOT imply high score on another. A system can be highly capable in one axis while catastrophically failing in another.

### The 9 Irreducible Core Invariants

| # | Axis | Hardening Question | Failure Mode |
|---|------|-------------------|--------------|
| 1 | **reality_contact** | Did reasoning preserve map/territory distinction? | Hallucination, confirmation bias, lost grounding |
| 2 | **truth_discipline** | Did no claim upgrade from hypothesis to fact without evidence? | Belief laundered as fact, narrative fallacy |
| 3 | **abstraction_control** | Did abstraction preserve re-grounding paths to concrete examples? | Abstracted into meaninglessness, lost operationality |
| 4 | **cross_domain_transfer** | Did domain transfer preserve structure, not just surface? | False analogy, vocabulary collision |
| 5 | **causal_agency** | Was causal lever identified before action? | Action without understanding consequence |
| 6 | **objective_governance** | Did local objective remain subordinate to higher constraints? | Goal殉职 — optimizing local proxy at expense of systemic health |
| 7 | **corrigible_sovereignty** | Did system accept correction without resistance? | Defensive routing around constraints, laundering |
| 8 | **power_restraint** | Did more capability NOT imply more permission? | Capability seduction — "I can, therefore I should" |
| 9 | **recursive_safety** | Did self-improvement preserve governance invariants? | Self-modification that weakens oversight |

### Supporting 16 Invariants

| # | Axis | Hardening Question |
|---|------|-------------------|
| 10 | **epistemic_truth_discipline** | Was uncertainty declared rather than disguised as certainty? |
| 11 | **cross_domain_transfer** | Was structure preserved across domain analogy? |
| 12 | **abstraction_control** | Were abstraction boundaries maintained? |
| 13 | **objective_stability** | Did objective remain stable within this reasoning pass? |
| 14 | **meta_objective_stability** | Did rules for changing goals remain unchanged? |
| 15 | **boundary_maintenance** | Were self/user/tool/memory/simulation boundaries preserved? |
| 16 | **temporal_reasoning** | Were timestamps, expiry, and freshness considered? |
| 17 | **plasticity_stability** | Was new information integrated without destroying valid structure? |
| 18 | **compositionality** | Did composed actions preserve permissions and audit across modules? |
| 19 | **agency_discipline** | Was state-change predicted before each action? |
| 20 | **embodiment_awareness** | Was each tool call treated as causal world intervention? |
| 21 | **interpretability** | Was consequential output traceable to human-understandable reasoning? |
| 22 | **robustness** | Did output remain valid under noise, adversarial input, distribution shift? |
| 23 | **value_boundary_judgment** | Was user preference distinguished from moral/safety/legal constraint? |
| 24 | **resource_rationality** | Were compute, time, and opportunity costs bounded? |
| 25 | **self_model_accuracy** | Did system correctly identify its own capabilities and limitations? |
| 26 | **governance_persistence** | Did constitutional governance remain active across domain shifts? |
| 27 | **moral_uncertainty** | Was unresolved moral uncertainty preserved rather than collapsed? |
| 28 | **scalable_oversight** | Did the system help humans supervise it without self-judging? |
| 29 | **safe_recursive_improvement** | Did self-improvement preserve the ability to be supervised? |

---

## Implementation

### arifOS MCP Integration Points

1. **`schemas/mind_metabolism.py`** — `InvariantAxes` Pydantic model (v2 output schema)
2. **`schemas/mind_metabolism.py`** — `MindGovernance.invariant_axes: InvariantAxes | None`
3. **`runtime/mind_reason.py`** — `SYSTEM_PROMPT` includes invariant axis discipline
4. **`runtime/mind_reason.py`** — `RESPONSE_SCHEMA` includes `invariant_pass` field
5. **`runtime/mind_reason.py`** — `_FIELD_PROVENANCE_LLM/FALLBACK` entries for `invariant_pass`

### Claim States (existing, preserved)

```
OBSERVED_INPUT → INFERENCE → HYPOTHESIS → SUPPORTED_CLAIM → VERIFIED_FACT
                                         ↘ NORMATIVE_ADVICE
                                         ↘ SPECULATION
                                         ↘ UNSUPPORTED
```

---

## Non-Stationary Objective Hierarchy

```
Level 0: Physics        — immutable
Level 1: Chemistry      — very slow change
Level 2: Biology        — slow change
Level 3: Animal Nature  — moderate stability
Level 4: Social         — faster change
Level 5: Individual     — fast change
Level 6: Tactical       — very fast change
Level 7: Operational    — ephemeral
Level 8: Local Action   — momentary
```

**Invariants at higher levels are more fragile.** A system's objective hierarchy must be stable across all levels simultaneously.

---

## Embedding Locations

| File | Role |
|------|------|
| `arifosmcp/schemas/mind_metabolism.py` | `InvariantAxes` model + `MindGovernance` extension |
| `arifosmcp/runtime/mind_reason.py` | `SYSTEM_PROMPT` invariant discipline + `RESPONSE_SCHEMA` + field provenance |
| `arifosmcp/embodied_instances/arif_mind_reason_embodied.py` | EmbodiedTool pipeline stages: natural slots for invariant checks |

---

## APEX Verdict Contract

Any `invariant_pass` field with a `False` value on any axis triggers:
- `status: "ESCALATE_TO_888"` or `"HOLD"`
- `human_judgment_required: True` in `MindGovernance`
- Verdict blocked until axis is resolved or evidence provided

---
