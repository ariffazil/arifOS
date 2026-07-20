---
type: TYPE_TAXONOMY
primitives: [AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION, AMANAH]
title: OKF Type Taxonomy — Canonical Primitives
description: "5 orthogonal primitives. 4 substances + 1 floor operator. Non-overlapping. Complete. Minimal."
domains: [PHYSICS, MATH, CODE, AAA]
tags: [canon, type, taxonomy, orthogonal]
timestamp: 2026-07-20T00:00:00Z
topology: "K₄ + gate — AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION form a complete 4-node lattice; AMANAH is the F1 floor operator that gates all four"
arifos:
  verdict: SEAL
  witness: [ARIF, FORGE, AUDITOR]
---
# Type Taxonomy — The 5 Orthogonal Primitives

## Architecture

```
        AKAL — PRESENT — ENERGY_ENTROPY — EXPLORATION
                          │
                       AMANAH  (floor operator — F1)
```

- **4 substance primitives**: AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION — describe reality
- **1 floor operator**: AMANAH — describes admissibility (should we?)
- **Topology**: K₄ + gate, not K₅. All 4 substance pairs connect directly (6 edges). AMANAH connects to all 4 as a modifier (4 edges). Total: 10 edges.

---

## AKAL

| Field | Value |
|-------|-------|
| **Role** | substance |
| **Root** | Ilmu Akal (GENESIS/016) |
| **Governs** | Reasoning, epistemology, intelligence, doubt vs decision, confidence calibration |
| **Does NOT govern** | Observation (PRESENT), thermodynamics (ENERGY_ENTROPY), hypothesis generation (EXPLORATION), trust (AMANAH) |
| **Paradoxes** | P3 Truth/Uncertainty, P13 Doubt/Decision, P14 Reason/Intuition, P21 Measurable/Meaningful |
| **APEX** | h — humility is AKAL calibrated; C_dark — dark entropy from failed AKAL |
| **Edges** | [AKAL↔PRESENT](graph-link.md#akal--present), [AKAL↔EXPLORATION](graph-link.md#akal--exploration), [AKAL↔ENERGY_ENTROPY](graph-link.md#akal--energy_entropy), [AKAL←AMANAH](graph-link.md#akal--amanah) |
| **Canon** | `arifOS/docs/AKAL.md`, `GENESIS/016` |

AKAL is the capacity to reason from evidence to conclusion. It judges, evaluates, and calibrates. Without AKAL, there is no governance — only reflex.

**Boundary with EXPLORATION:** AKAL judges claims. EXPLORATION generates hypotheses. AKAL asks "is this true?" EXPLORATION asks "what if?" They overlap on hypothesis testing (Φ) but from opposite directions: AKAL falsifies, EXPLORATION proposes.

---

## PRESENT

| Field | Value |
|-------|-------|
| **Role** | substance |
| **Root** | Spatial-temporal awareness |
| **Governs** | State, context, presence, observation, the "now", measurement at T₀ and T₁ |
| **Does NOT govern** | Reasoning about observation (AKAL), physical laws governing change (ENERGY_ENTROPY), what to observe next (EXPLORATION), trust in observation (AMANAH) |
| **Paradoxes** | P4 Evidence/Claim, P18 Observer/Observed, P7 Light/Shadow |
| **APEX** | W³ — witness requires PRESENT at multiple independent vantage points |
| **Edges** | [PRESENT↔AKAL](graph-link.md#akal--present), [PRESENT↔EXPLORATION](graph-link.md#present--exploration), [PRESENT↔ENERGY_ENTROPY](graph-link.md#present--energy_entropy), [PRESENT←AMANAH](graph-link.md#present--amanah) |
| **Canon** | `arifOS/docs/ZEN_OF_REALITY_ENGINEERING.md` |

PRESENT is the capacity to observe what IS. All evidence enters the federation through PRESENT. Without PRESENT, there is no ground truth — only speculation.

---

## ENERGY_ENTROPY

| Field | Value |
|-------|-------|
| **Role** | substance |
| **Root** | Thermodynamics (GENESIS/049) |
| **Governs** | ΔS, conservation, useful work vs dissipation, order vs chaos, resource flow, thermodynamic cost of reasoning |
| **Does NOT govern** | What the energy is spent on (AKAL), how to measure it (PRESENT), where to look for savings (EXPLORATION), who decides it's worth spending (AMANAH) |
| **Paradoxes** | P1 Energy/Entropy, P5 Order/Chaos, P10 Conservation/Change |
| **APEX** | G — useful work before dissipation; C_dark — dissipated false signal |
| **Edges** | [ENERGY_ENTROPY↔AKAL](graph-link.md#akal--energy_entropy), [ENERGY_ENTROPY↔PRESENT](graph-link.md#present--energy_entropy), [ENERGY_ENTROPY↔EXPLORATION](graph-link.md#energy_entropy--exploration), [ENERGY_ENTROPY←AMANAH](graph-link.md#energy_entropy--amanah) |
| **Canon** | `arifOS/docs/ENERGY_ENTROPY.md` |

ENERGY_ENTROPY is the universal currency. Every decision is an allocation of energy. Every mistake is entropy. G measures useful work. C_dark measures dissipation into falsehood.

---

## EXPLORATION

| Field | Value |
|-------|-------|
| **Role** | substance |
| **Root** | Agentic Geology Doctrine (GENESIS/015) |
| **Governs** | Discovery, falsification, hypothesis generation, curiosity, the boundary of the known |
| **Does NOT govern** | Truth of hypotheses (AKAL), observation of results (PRESENT), energy cost of exploring (ENERGY_ENTROPY), permission to explore (AMANAH) |
| **Paradoxes** | P8 Tradition/Innovation, P15 Local/Global, P19 Story/Structure |
| **APEX** | Φ — falsification rate measures how many hypotheses survive |
| **Edges** | [EXPLORATION↔AKAL](graph-link.md#akal--exploration), [EXPLORATION↔PRESENT](graph-link.md#present--exploration), [EXPLORATION↔ENERGY_ENTROPY](graph-link.md#energy_entropy--exploration), [EXPLORATION←AMANAH](graph-link.md#exploration--amanah) |
| **Canon** | `GEOX/GENESIS/015_AGENTIC_GEOLOGY_DOCTRINE.md` |

EXPLORATION is the drive to cross the boundary of the known. All science, all discovery, all curiosity lives here. Without EXPLORATION, AKAL has nothing to reason about.

**Boundary with AKAL:** EXPLORATION generates testable claims. AKAL evaluates them. A claim in EXPLORATION is a proposal. A claim in AKAL is under judgment. The bridge is falsification (Φ).

---

## AMANAH

| Field | Value |
|-------|-------|
| **Role** | **floor_operator** |
| **Root** | F1 Constitutional Floor |
| **Governs** | Trust, reversibility, delegation, lease, the precondition for action |
| **Does NOT govern** | What action to take (AKAL), state of the world (PRESENT), cost of action (ENERGY_ENTROPY), novelty of action (EXPLORATION) |
| **Paradoxes** | P29 Sovereignty, P31 Permanence/Reversibility, P33 Self-Governance |
| **APEX** | G — capability requires trust; W³ — witness requires trust across channels |
| **Operates on** | AKAL (trusted reasoning), PRESENT (trusted observation), ENERGY_ENTROPY (trust reduces dissipation), EXPLORATION (safe exploration) |
| **Canon** | F1 floor in `arifOS/static/arifos/theory/000/000_CONSTITUTION.md` |

AMANAH is not a substance. It is the **F1 floor operator**. The other four primitives describe *what is possible*. AMANAH answers *what is permissible*.

The four substance primitives can operate without AMANAH — they just cannot operate *safely*. Without AMANAH:
- AKAL reasons without accountability → hallucination (high C_dark)
- PRESENT observes without verification → false evidence
- ENERGY_ENTROPY flows without conservation → infinite burn
- EXPLORATION discovers without safety → chaos

AMANAH is the constitutional floor that qualifies all four. It is orthogonal because it answers a different question: **should we?**

---

## Domains (Cross-Cutting)

| Domain | Covers | Example |
|--------|--------|---------|
| **PHYSICS** | Physical laws, earth, EGS, geophysics | GEOX seismic, basin, well data |
| **MATH** | Computation, geometry, game theory, statistics | WEALTH NPV, Markovitz, Monte Carlo |
| **CODE** | Implementation, engineering, tools | A-FORGE forge_* tools, MCP servers |
| **AAA** | Coordination, workflow, identity, routing | AAA A2A gateway, agent cards, cockpit |

## Audit Status

| Finding | Resolution |
|---------|-----------|
| Φ violates "exactly two types" invariant | Resolved: Φ declared as hyperedge (arity: 3). See [apex-flow.md](apex-flow.md#hyperedges). |
| Graph is K₅ (topology carries no info) | Accepted by design: K₄ + gate. All edges labeled. Value is in labels, not shape. |
| "Directed edges" vs ↔ diagram | Resolved: Graph is **undirected**. Flow is a canonical traversal recipe over undirected graph. |
| AMANAH as peer vs modifier | Resolved: AMANAH is `role: floor_operator`, not a substance. K₄ + gate. |
| AKAL/EXPLORATION boundary | Resolved: Negative space defined. AKAL judges, EXPLORATION generates. Both participate in Φ from opposite directions. |
