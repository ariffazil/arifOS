---
type: APEX_FLOW
primitives: [AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION, AMANAH]
title: APEX Flow — Dials as Type Bridges
description: "5 dials. 4 bridges (arity 2) + 1 hyperedge (arity 3). Every dial measures the tension at a type boundary."
domains: [PHYSICS, MATH, CODE, AAA]
tags: [apex, dials, flow, governance]
hyperedge_rule: "Hyperedges (arity ≥ 3) are legal. Bridge edges for traversal are extracted as pairwise projections. See Φ."
timestamp: 2026-07-20T00:00:00Z
arifos:
  verdict: SEAL
  witness: [ARIF, FORGE, APEX, AUDITOR]
---
# APEX Flow

## Design Rule

- 4 dials bridge **exactly 2 types** (arity 2)
- 1 dial (Φ) bridges **3 types** (hyperedge, arity 3)
- Hyperedges are legal. For traversal purposes, project the hyperedge into pairwise sub-edges.

## G — Capability (arity 2)

| Field | Value |
|-------|-------|
| **type** | ENERGY_ENTROPY |
| **bridges** | AKAL × AMANAH |
| **arity** | 2 |
| **formula** | G = A · P · E · X · Φ |
| **threshold** | ≥ 0.80 |
| **Meaning** | Useful work before entropy. AKAL (reasoning to act) operating within AMANAH (trust boundary), measured in ENERGY_ENTROPY (thermodynamic cost). |
| **Paradoxes** | P12 Capability/Authority, P31 Permanence/Reversibility |
| **Canon** | [type-taxonomy → ENERGY_ENTROPY](../type-taxonomy.md#energy_entropy) |

```
AKAL ──────╮
           ╬──→ G = useful work before dissipation
AMANAH ────┘
    ↕
ENERGY_ENTROPY (residency — measurement domain)
```

## C_dark — Hallucination Risk (arity 2)

| Field | Value |
|-------|-------|
| **type** | ENERGY_ENTROPY |
| **bridges** | AKAL × ENERGY_ENTROPY |
| **arity** | 2 |
| **formula** | C_dark = A · (1-P) · (1-X) |
| **threshold** | < 0.30 |
| **Meaning** | Dark entropy. When AKAL fails to reason correctly, the output is not zero — it is false signal that dissipates into the system. |
| **Paradoxes** | P3 Truth/Uncertainty, P32 Certainty/Uncertainty |
| **Canon** | [graph-link → AKAL↔ENERGY_ENTROPY](../graph-link.md#akal--energy_entropy) |

```
AKAL ──────────╮
               ╬──→ C_dark = false signal in the reasoning channel
ENERGY_ENTROPY ─┘
```

## W³ — Tri-Witness (arity 2)

| Field | Value |
|-------|-------|
| **type** | AMANAH |
| **bridges** | PRESENT × AMANAH |
| **arity** | 2 |
| **formula** | W³ = ∛(Human × AI × External) |
| **threshold** | All channels > 0; ≥ 0.70 for SEAL |
| **Meaning** | Consensus across independent observers. PRESENT provides the vantage points. AMANAH provides the trust that each channel reports honestly. |
| **Paradoxes** | P18 Observer/Observed, P33 Self-Governance |
| **Canon** | [graph-link → PRESENT↔AMANAH](../graph-link.md#present--amanah) |

```
PRESENT (Human) ──╮
PRESENT (AI) ─────╬──→ W³ = consensus
PRESENT (Earth) ──┘
     ↕
AMANAH (trust across channels)
```

## h — Humility Calibration (arity 2)

| Field | Value |
|-------|-------|
| **type** | AKAL |
| **bridges** | AKAL × EXPLORATION |
| **arity** | 2 |
| **formula** | h = 1 - \|confidence_claimed - confidence_actual\| |
| **threshold** | ≥ 0.85; confidence capped at 0.90 (F7) |
| **Meaning** | Epistemic calibration. AKAL knows what it knows. EXPLORATION knows what it doesn't know. h measures the gap. |
| **Paradoxes** | P7 Light/Shadow, P14 Reason/Intuition, P21 Measurable/Meaningful |
| **Canon** | [graph-link → AKAL↔EXPLORATION](../graph-link.md#akal--exploration) |

```
AKAL ─────────╮
              ╬──→ h = knowing what you know + what you don't
EXPLORATION ──┘
```

## Φ — Falsification Rate (arity 3 — hyperedge)

| Field | Value |
|-------|-------|
| **type** | EXPLORATION |
| **bridges** | EXPLORATION × AKAL × ENERGY_ENTROPY |
| **arity** | **3** (hyperedge) |
| **formula** | Φ = falsified_claims / total_testable_claims |
| **threshold** | Tracked; feeds into G computation |
| **Meaning** | Φ measures all three primitives simultaneously |
| **Paradoxes** | P4 Evidence/Claim, P35 Positive/Closed |
| **Canon** | [graph-link → EXPLORATION↔AKAL](../graph-link.md#akal--exploration), [graph-link → ENERGY_ENTROPY↔EXPLORATION](../graph-link.md#energy_entropy--exploration) |

### Why Φ is a hyperedge

Φ inherently involves three primitives:

```
EXPLORATION — generates hypotheses (testable claims)
AKAL — reasons about what would falsify them (falsification logic)
ENERGY_ENTROPY — measures the cost of false models (dissipated energy)
```

You cannot decompose Φ into pairwise edges without losing meaning. The falsification rate is:
- meaningless without **hypotheses to test** (EXPLORATION)
- unmeasurable without **reasoning about what constitutes falsification** (AKAL)
- uninformative without **the cost of being wrong** (ENERGY_ENTROPY)

### Hyperedges: Traversal Rule

For traversal agents, project the hyperedge into pairwise sub-edges:

| Pairwise Projection | Label |
|--------------------|-------|
| EXPLORATION ↔ AKAL | Hypothesis judgment |
| EXPLORATION ↔ ENERGY_ENTROPY | Cost of false models |
| AKAL ↔ ENERGY_ENTROPY | Reasoning has thermodynamic cost |

The hyperedge is the *union* of these three pairs. An agent traversing any of the three pairs encounters Φ.

## Dials Summary

| Dial | type: | Bridges | Arity |
|------|-------|---------|-------|
| G | ENERGY_ENTROPY | AKAL × AMANAH | 2 |
| C_dark | ENERGY_ENTROPY | AKAL × ENERGY_ENTROPY | 2 |
| W³ | AMANAH | PRESENT × AMANAH | 2 |
| h | AKAL | AKAL × EXPLORATION | 2 |
| Φ | EXPLORATION | EXPLORATION × AKAL × ENERGY_ENTROPY | **3** |

## The Complete APEX Cycle — Undirected Graph, Directed Traversal

```
                    Φ
            EXPLORATION
           ↗           ↘
    AKAL ←────────────→ PRESENT
    ↕  ↓                    ↕  ↑
    h  G                  W³  G
    ↑  ↕                    ↓  ↕
    ENERGY_ENTROPY ←──────→ AMANAH
           ↖           ↗
              C_dark
```

**Traversal recipe (the Flow):**

```
AKAL reasons → PRESENT observes → EXPLORATION hypothesizes → Φ measures
                                                                    ↕
                                                            ENERGY_ENTROPY accounts
                                                                    ↕
                                                            AMANAH gates all
```

This is one valid traversal of an undirected graph. The same graph supports other traversals for different cognitive modes:
- **Crisis mode:** AMANAH → AKAL → ENERGY_ENTROPY → PRESENT → EXPLORATION
- **Discovery mode:** EXPLORATION → PRESENT → AKAL → ENERGY_ENTROPY → AMANAH
- **Audit mode:** PRESENT → ENERGY_ENTROPY → AKAL → AMANAH → EXPLORATION
