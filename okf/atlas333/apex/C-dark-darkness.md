---
type: ApexDial
title: C_dark — Darkness / Hallucination Risk
symbol: C_dark
full_name: Dark Probability
formula: C_dark = A · (1-P) · (1-X)
description: Measures the probability of hallucination, falsehood, or hidden failure. Combines alignment gaps, precision uncertainty, and novelty risk. C_dark < 0.30 required to proceed.
threshold: < 0.30 required
domain: forge_evaluate, APEX governance gate
tags: [apex, hallucination, risk, darkness]
timestamp: 2026-07-20T00:00:00Z
arifos:
  claim_class: SPECIFICATION
  verdict: SEAL
  witness: [ARIF, FORGE, APEX]
---
# C_dark — C_dark — Darkness / Hallucination Risk

**Formula:** `C_dark = A · (1-P) · (1-X)`

**Threshold:** < 0.30 required

**Domain:** forge_evaluate, APEX governance gate

Measures the probability of hallucination, falsehood, or hidden failure. Combines alignment gaps, precision uncertainty, and novelty risk. C_dark < 0.30 required to proceed.
