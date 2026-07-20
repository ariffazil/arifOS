---
type: ENERGY_ENTROPY
primitives: [AKAL, AMANAH, ENERGY_ENTROPY]
symbol: G
title: Capability Score
formula: G = A · P · E · X · Φ
description: Nash bargaining product of capability. G measures useful work before entropy. AKAL (reasoning) × AMANAH (trust) × ENERGY_ENTROPY (thermodynamic cost).
domains: [MATH, CODE, AAA]
threshold: "≥ 0.80"
tags: [apex, capability, governance, work]
timestamp: 2026-07-20T00:00:00Z
arifos:
  claim_class: SPECIFICATION
  verdict: SEAL
  witness: [ARIF, FORGE, APEX]
links:
  graph: ../graph-link.md#akal--amanah
  taxonomy: ../type-taxonomy.md#energy_entropy
  paradox: ../atlas333/paradox/P12-capability-authority.md
---
# G — Capability

**Type bridge:** AKAL × AMANAH × ENERGY_ENTROPY

G is not a score. It is a thermodynamic measurement: how much useful work can this system do before C_dark dissipates it?

- AKAL reasons about the action
- AMANAH trusts the actor
- ENERGY_ENTROPY accounts for the cost

Without any one leg, G collapses to zero.
