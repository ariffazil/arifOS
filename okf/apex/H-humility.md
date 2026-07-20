---
type: AKAL
primitives: [AKAL, EXPLORATION]
symbol: h
title: Humility Calibration
formula: h = 1 - |confidence_claimed - confidence_actual|
description: Epistemic calibration score. AKAL (reasoning about what you know) × EXPLORATION (knowing what you don't know).
domains: [MATH, AAA]
threshold: "≥ 0.85; confidence capped at 0.90"
tags: [apex, humility, calibration, epistemology]
timestamp: 2026-07-20T00:00:00Z
arifos:
  claim_class: SPECIFICATION
  verdict: SEAL
  witness: [ARIF, FORGE, APEX]
links:
  graph: ../graph-link.md#akal--exploration
  taxonomy: ../type-taxonomy.md#akal
  paradox: ../atlas333/paradox/P14-reason-intuition.md
---
# h — Humility

**Type bridge:** AKAL × EXPLORATION

Humility is not a virtue. It is a calibration metric. h measures the gap between claimed confidence and actual accuracy.

- AKAL: reasoning about what you know
- EXPLORATION: knowing what you don't know — the unknown unknown

Confidence capped at 0.90 (F7). The remaining 0.10 is the irreducible unknown that EXPLORATION covers.
