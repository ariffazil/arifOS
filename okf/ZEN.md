---
type: ZEN
primitives: [AKAL, PRESENT, ENERGY_ENTROPY, EXPLORATION, AMANAH]
title: arifOS Knowledge Zen
description: "3 layers · 5 primitives · 10 edges · 5 dials. One coordinate system. All knowledge finds its address."
domains: [PHYSICS, MATH, CODE, AAA]
timestamp: 2026-07-20T00:00:00Z
arifos:
  verdict: SEAL
  witness: [ARIF, FORGE]
---
# ZEN — arifOS Knowledge Coordinate System

## 5 Primitives

```
AKAL           reasoning, epistemology, doubt/decision
PRESENT        state, observation, context, the "now"
ENERGY_ENTROPY thermodynamics, ΔS, useful work vs dissipation
EXPLORATION    discovery, falsification, hypothesis
AMANAH         trust, reversibility, F1 floor (operator on all 4)
```

4 substances + 1 floor operator. K₄ + gate. [Full taxonomy](type-taxonomy.md)

## 10 Edges

```
AKAL ←→ EXPLORATION      hypothesis-driven reasoning       [Φ, h]
AKAL ←→ PRESENT           aware reasoning                   [W³]
AKAL ←→ AMANAH            trusted reasoning                 [G]
AKAL ←→ ENERGY_ENTROPY    intelligence as entropy reduction  [C_dark]
PRESENT ←→ ENERGY_ENTROPY state change measurement           [G]
PRESENT ←→ EXPLORATION    observation-driven discovery       [Φ]
PRESENT ←→ AMANAH         trusted observation                [W³]
ENERGY_ENTROPY ←→ EXPLORATION  falsification as dissipation  [Φ]
ENERGY_ENTROPY ←→ AMANAH  trust as entropy reduction         [G]
EXPLORATION ←→ AMANAH     safe exploration                   [h]
```

Undirected graph. Value is in labels, not topology. [Full graph](graph-link.md)

## 5 APEX Dials

```
G       ENERGY_ENTROPY    AKAL × AMANAH          useful work before entropy     ≥0.80
C_dark  ENERGY_ENTROPY    AKAL × ENERGY_ENTROPY  false signal dissipation       <0.30
W³      AMANAH            PRESENT × AMANAH       cross-channel consensus        >0, ≥0.70
h       AKAL              AKAL × EXPLORATION     calibration gap                ≥0.85
Φ       EXPLORATION       EXPL×AKAL×EN_ENT       hypothesis survival rate       tracked
```

4 arity-2 + 1 hyperedge (Φ). [Full flow](apex-flow.md)

## 3 Time Layers

```
LAYER      MODE      QUESTION              FILES
ATLAS333   static    what tensions persist? paradox/*.md          (35)
EUREKA777  dynamic   what just transitioned? eureka/*.md          (N)
VAULT999   record    what was true when?    seal_chain.jsonl      (19)
```

Same 5 primitives at all 3 layers. [ATLAS333](atlas333/index.md) · [EUREKA777](eureka777/index.md) · [VAULT999](../.local/share/arifos/vault999/seal_chain.jsonl)

## 5 EUREKA Classes

```
DISCOVERY      ∅ → EXPLORATION           new phenomenon          E001 LEBAH EMAS-1
FALSIFICATION  EXPLORATION → PRES+AKAL   hypothesis tested       E002 BEKANTAN-1
UNIFICATION    2+ primitives → bridge    connection found        E003 ABKSS
REFUSAL        substance → AMANAH        floor says no           E004 BEKOK_DEEP-1
INVERSION      same primitives, flipped   paradigm inverted      E005 PETRONAS DNA
```

[Full classes](eureka777/classes/) · [Ledger](eureka777/ledger/ledger.md)

## 4 Domains

```
PHYSICS  earth, laws, geophysics    GEOX
MATH     computation, statistics    WEALTH
CODE     implementation, tools      A-FORGE
AAA      coordination, identity     AAA cockpit
```

## 6 Organs

```
arifOS  :8088  constitutional kernel     judge + vault
A-FORGE :7071  execution shell           forge + deploy
AAA     :3001  control plane             route + display
GEOX    :8081  earth intelligence        observe + falsify
WEALTH  :18082 capital intelligence      compute + allocate
WELL    :18083 human readiness           reflect + guard
```

[Organ definitions](organs/)

## The Flow

```
AKAL reasons → PRESENT observes → EXPLORATION hypothesizes → Φ measures
                                                                    ↕
                                                            ENERGY_ENTROPY accounts
                                                                    ↕
                                                            AMANAH gates all
```

One traversal of an undirected graph. Other traversals exist for other cognitive modes.

## The Zen

```
ATLAS333   = the score
EUREKA777  = the performance
VAULT999   = the recording
Primitives = the notes
Edges      = the intervals
APEX dials = the tuning
```

Every fact, scar, or discovery has one address: `{primitive[], domain, layer}`.
No knowledge is homeless. No coordinate is ambiguous.

[type-taxonomy](type-taxonomy.md) · [graph-link](graph-link.md) · [apex-flow](apex-flow.md) · [ATLAS333](atlas333/index.md) · [EUREKA777](eureka777/index.md)
