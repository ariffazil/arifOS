---
type: ENERGY_ENTROPY
primitives: [ENERGY_ENTROPY, AKAL]
symbol: C_dark
title: Darkness / Hallucination Risk
formula: C_dark = A · (1-P) · (1-X)
description: The dark energy term. Measures dissipation into falsehood. ENERGY_ENTROPY (entropy) × AKAL (failed reasoning).
domains: [AKAL, MATH, CODE]
threshold: "< 0.30"
tags: [apex, hallucination, risk, darkness, entropy]
timestamp: 2026-07-20T00:00:00Z
arifos:
  claim_class: SPECIFICATION
  verdict: SEAL
  witness: [ARIF, FORGE, APEX]
links:
  graph: ../graph-link.md#akal--energy_entropy
  taxonomy: ../type-taxonomy.md#energy_entropy
  paradox: ../atlas333/paradox/P03-truth-uncertainty.md
---
# C_dark — Hallucination Risk

**Type bridge:** ENERGY_ENTROPY × AKAL

Every thermodynamic system dissipates. C_dark measures how much of the system's output is false but indistinguishable from true.

- ENERGY_ENTROPY: all reasoning has a dissipation cost
- AKAL: when reasoning fails, it generates dark entropy

C_dark < 0.30 means the system is not yet corrupted by its own false signal.
