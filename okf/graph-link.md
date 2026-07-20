---
type: GRAPH_LINK
primitives: [AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION, AMANAH]
title: Type Graph — Edge Definitions
description: "Topology: K₄ + gate. Undirected graph. 10 labeled edges. Value is in labels, not shape."
domains: [PHYSICS, MATH, CODE, AAA]
tags: [canon, graph, link, flow]
topology: "undirected"  # Not directed. The Flow is a traversal recipe over an undirected graph.
timestamp: 2026-07-20T00:00:00Z
arifos:
  verdict: SEAL
  witness: [ARIF, FORGE, AUDITOR]
---
# Type Graph — 10 Undirected Edges

## Topology

This is an **undirected** graph. All edges are traversable in either direction.
The canonical traversal recipe (Flow) is defined in [apex-flow.md](apex-flow.md#the-complete-apex-cycle).

The graph is K₄ + gate — not K₅:

```
        AKAL — PRESENT — ENERGY_ENTROPY — EXPLORATION
                          │
                       AMANAH  (floor operator qualifying all 4)
```

- 4 substance nodes form a complete subgraph (K₄): 6 edges
- AMANAH connects to all 4 as floor operator: 4 edges
- Total: 10 edges

This is K₄ + gate by design: **all pairs are meaningful**. The value is not in topological distance (which is always 1) but in the **edge label** — what kind of interaction exists between the two primitives.

---

## Edge Definitions

### AKAL ↔ EXPLORATION

**Label:** Hypothesis-driven reasoning  
**Directionality:** Undirected (AKAL judges claims, EXPLORATION generates them)  
**Paradox:** P3 Truth/Uncertainty, P19 Story/Structure  
**APEX:** Φ — both primitives participate from opposite directions  
**Canon:** `GENESIS/016` (ILMU_AKAL), `GENESIS/015` (AGENTIC GEOLOGY)  
**Gap:** No A-FORGE doc on this edge

AKAL reasons about truth. EXPLORATION generates what might be true. The boundary is hypothesis — AKAL demands evidence, EXPLORATION supplies candidates.

### AKAL ↔ PRESENT

**Label:** Aware reasoning  
**Directionality:** Undirected (AKAL interprets what PRESENT observes, PRESENT grounds what AKAL reasons about)  
**Paradox:** P18 Observer/Observed  
**APEX:** W³ — tri-witness requires present observers whose reports AKAL evaluates  
**Canon:** `docs/ZEN_OF_REALITY_ENGINEERING.md`  
**Gap:** No AAA doc on observer effect

Observation without reasoning is blind. Reasoning without observation is empty.

### AKAL ↔ ENERGY_ENTROPY

**Label:** Intelligence as entropy reduction  
**Directionality:** Undirected (AKAL reasons at thermodynamic cost, ENERGY_ENTROPY constrains what AKAL can afford to reason about)  
**Paradox:** P1 Energy/Entropy, P5 Order/Chaos  
**APEX:** C_dark — hallucination is reasoning that generates entropy instead of reducing it  
**Canon:** `docs/ENERGY_ENTROPY.md`  
**Gap:** WEALTH should own information value economics on this edge

Reasoning is not free. Every inference has a thermodynamic cost. This edge accounts for it.

### AKAL ← AMANAH

**Label:** Trusted reasoning  
**Directionality:** AMANAH → AKAL (floor operator qualifies reasoning) — AKAL does not reciprocate  
**Paradox:** P12 Capability/Authority, P29 Sovereignty  
**APEX:** G — capability = AKAL operating within AMANAH's trust boundary  
**Canon:** F1 floor, `GENESIS/001` (MUHAMMAD_MODE)  
**Gap:** No doc on AMANAH as precondition for AKAL

AKAL can reason without AMANAH. But without AMANAH, AKAL's output cannot be trusted enough to act on. This is the single most important edge in the graph.

### PRESENT ↔ ENERGY_ENTROPY

**Label:** State change measurement  
**Directionality:** Undirected (PRESENT measures at T₀/T₁, ENERGY_ENTROPY computes ΔS)  
**Paradox:** P5 Order/Chaos  
**APEX:** All dials depend on present measurement  
**Canon:** `docs/ZEN_OF_REALITY_ENGINEERING.md`  
**Gap:** No dedicated measurement cycle doc

You cannot measure ΔS without PRESENT at two points in time. This edge is the measurement primitive.

### PRESENT ↔ EXPLORATION

**Label:** Observation-driven discovery  
**Directionality:** Undirected (PRESENT notices anomaly, EXPLORATION generates hypothesis, PRESENT tests)  
**Paradox:** P4 Evidence/Claim  
**APEX:** Φ — falsification requires present observation of test results  
**Canon:** `GEOX/GENESIS/015`  
**Gap:** Thin in A-FORGE

Curiosity begins with PRESENT noticing something that doesn't fit.

### PRESENT ← AMANAH

**Label:** Trusted observation  
**Directionality:** AMANAH → PRESENT (floor operator qualifies observation)  
**Paradox:** P33 Self-Governance  
**APEX:** W³ — witness channels must be trusted  
**Canon:** F3 WITNESS floor  
**Gap:** Need explicit F3 witness doc

Observation without trust produces unreliable evidence. AMANAH creates the safety for honest reporting.

### ENERGY_ENTROPY ↔ EXPLORATION

**Label:** Falsification as energy dissipation  
**Directionality:** Undirected (EXPLORATION generates hypotheses, ENERGY_ENTROPY measures cost of false ones)  
**Paradox:** P35 Positive/Closed  
**APEX:** Φ — falsification dissipates false models  
**Canon:** `GEOX/docs/PHYSICS9_EARTH_WITNESS.md`  
**Gap:** This is the thinnest edge — poorly documented everywhere

A false hypothesis consumes energy (time, compute, drilling budget). ENERGY_ENTROPY measures the dissipation. EXPLORATION learns from it.

### ENERGY_ENTROPY ← AMANAH

**Label:** Trust as entropy reduction  
**Directionality:** AMANAH → ENERGY_ENTROPY (floor operator qualifies energy allocation)  
**Paradox:** P31 Permanence/Reversibility  
**APEX:** G — trust reduces friction, frictionless systems conserve energy  
**Canon:** F1 floor  
**Gap:** No thermodynamic model of trust

AMANAH reduces the friction of coordination. Less friction = less entropy = more useful work. This is G's thermodynamic basis.

### EXPLORATION ← AMANAH

**Label:** Safe exploration  
**Directionality:** AMANAH → EXPLORATION (floor operator qualifies discovery)  
**Paradox:** P31 Permanence/Reversibility  
**APEX:** h — humility enables exploration by acknowledging the unknown  
**Canon:** F1 reversibility guarantee  
**Gap:** No AAA doc

AMANAH guarantees reversibility. EXPLORATION can only take risks if it knows the floor will hold. Without AMANAH, exploration is reckless.

---

## Audit: All Findings Addressed

| Finding | Status |
|---------|--------|
| Φ violates invariant | Referred to [apex-flow.md](apex-flow.md) hyperedge handling |
| K₅ carries no topological info | Accepted — K₄ + gate by design. Value in edge labels. |
| "Directed" vs ↔ | Resolved — declared **undirected**. Canonical Flow is traversal recipe. |
| AMANAH as peer vs modifier | Resolved — AMANAH is `role: floor_operator`. All 4 AMANAH edges are directional (AMANAH→substance). |
| AKAL/EXPLORATION boundary | Resolved — negative space in [type-taxonomy.md](type-taxonomy.md). AKAL judges, EXPLORATION generates. |
