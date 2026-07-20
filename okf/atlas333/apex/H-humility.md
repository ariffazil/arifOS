---
type: ApexDial
title: h — Humility Calibration
symbol: h
full_name: Confidence Calibration Score
formula: h = 1 - |confidence_claimed - confidence_actual|
description: Measures how well an agent's claimed confidence matches actual accuracy. Perfect calibration = 1.0. All agents must cap confidence at 0.90 (F7 HUMILITY).
threshold: ≥ 0.85 calibration; confidence capped at 0.90
domain: F7 HUMILITY floor, forge_evaluate
tags: [apex, humility, calibration, f7]
timestamp: 2026-07-20T00:00:00Z
arifos:
  claim_class: SPECIFICATION
  verdict: SEAL
  witness: [ARIF, FORGE, APEX]
---
# h — h — Humility Calibration

**Formula:** `h = 1 - |confidence_claimed - confidence_actual|`

**Threshold:** ≥ 0.85 calibration; confidence capped at 0.90

**Domain:** F7 HUMILITY floor, forge_evaluate

Measures how well an agent's claimed confidence matches actual accuracy. Perfect calibration = 1.0. All agents must cap confidence at 0.90 (F7 HUMILITY).
