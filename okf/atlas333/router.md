---
type: Specification
title: ΛΘΦ Router
description: The ATLAS333 routing engine that maps text → lane → demand tensor → GPV → activated paradoxes
tags: [atlas333, router, activation, geometry]
timestamp: 2026-07-20T00:00:00Z
---
# ΛΘΦ Router

## The Activation Pipeline

```
Λ(text) → lane (CRISIS/FACTUAL/SOCIAL/CARE/UNKNOWN)
Θ(lane) → demand tensor (τ truth, κ care, ρ risk)
Φ(text) → GPV (lane + tensor + paradox axes)
   ↓
Activate relevant paradoxes → inject into reasoning context
   ↓
Agent thinks IN the tension, not FROM a rule
```

## Lane → Paradox Activation Matrix

| Lane | Primary Paradoxes | τ | κ | ρ |
|------|------------------|---|---|---|
| CRISIS | P31, P29, P13 | 0.9 | 0.3 | 0.9 |
| FACTUAL | P3, P4, P21 | 0.9 | 0.1 | 0.3 |
| SOCIAL | P30, P22, P11 | 0.3 | 0.9 | 0.5 |
| CARE | P6, P30, P33 | 0.3 | 0.9 | 0.7 |

## MCP Resource

`arifos://atlas333/activation/rules` on arifOS :8088 (merged into paradox/list)

## Institutional metrics bridge (2026-08-09) — wiring only

Two distinct ATLAS concepts:

| Name | Plane |
|------|--------|
| **ATLAS333** | 35 paradoxes · cognitive geometry · 333 substrate |
| **ATLAS metric** | Authority-to-Landscape · governance telemetry |

```
MAP  → top_k density (low MAP = more paradoxes; high MAP = fewer)
ECHO → tension weights (P2 Remember/Forget heats on memory visibility)
ATLAS metric → judge-axis heat when governance compression low
```

Paradox **content** immutable. Metrics are **signals**.

- Resource: `arifos://atlas333/metrics` (F2 deterministic, F8 read-only)
- Code: `arifosmcp/geometry/metrics_bridge.py`
- Activation: `core/shared/atlas333_activate.py`
