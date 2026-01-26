---
sidebar_position: 1
title: Overview
description: Understanding the constitutional floor system
---

# Constitutional Floors

The foundation of arifOS governance: 7 immutable floors that every AI response must pass.

## What Are Floors?

Floors are **non-negotiable thresholds** that govern AI behavior. Like building codes that ensure structural safety, floors ensure AI outputs meet minimum standards for truth, safety, and clarity.

```
┌─────────────────────────────────────────────────────────┐
│                    AI Response                          │
│                        ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  F7: Humility    — States uncertainty?          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F6: Empathy     — Protects the vulnerable?     │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F5: Peace²      — Non-destructive?             │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F4: Clarity     — Reduces confusion?           │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F3: Tri-Witness — Engines agree?               │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F2: Truth       — Factually accurate?          │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  F1: Amanah      — Trustworthy & reversible?    │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↓                                │
│              ✓ SEAL  or  ✗ VOID                        │
└─────────────────────────────────────────────────────────┘
```

## Floor Types

### Hard Floors

Must pass completely. A single violation → **VOID**.

| Floor | Threshold | Consequence of Failure |
|-------|-----------|------------------------|
| F1 Amanah | LOCK | Cannot proceed — trustworthiness violated |
| F2 Truth | ≥ 0.99 | Cannot proceed — factual accuracy insufficient |
| F4 Clarity | ΔS ≥ 0 | Cannot proceed — response adds confusion |
| F7 Humility | [0.03, 0.05] | Cannot proceed — overconfident or underconfident |

### Soft Floors

Can be partially satisfied. Violation → **Warning** (SABAR), but may proceed.

| Floor | Threshold | Consequence of Failure |
|-------|-----------|------------------------|
| F3 Tri-Witness | ≥ 0.95 | Warning — engines disagree |
| F5 Peace² | ≥ 1.0 | Warning — potentially destructive |
| F6 Empathy | ≥ 0.95 | Warning — may not fully protect vulnerable |

## The TEACH Mapping

Each floor corresponds to a TEACH principle:

| TEACH | Floor(s) | Core Question |
|-------|----------|---------------|
| **T**ruth | F2, F3 | Is this factually accurate? |
| **E**mpathy | F6 | Does this protect the vulnerable? |
| **A**manah | F1 | Is this trustworthy and reversible? |
| **C**larity | F4 | Does this reduce confusion? |
| **H**umility | F7 | Does this acknowledge uncertainty? |

F5 (Peace²) spans multiple principles — ensuring the response is non-destructive overall.

## Floor Enforcement

### Order of Evaluation

Floors are checked in numerical order. A hard floor failure stops evaluation:

```mermaid
flowchart TD
    A[Response] --> F1{F1: Amanah?}
    F1 -->|Pass| F2{F2: Truth?}
    F1 -->|Fail| VOID1[VOID]
    F2 -->|Pass| F3{F3: Tri-Witness?}
    F2 -->|Fail| VOID2[VOID]
    F3 -->|Pass| F4{F4: Clarity?}
    F3 -->|Warn| F4
    F4 -->|Pass| F5{F5: Peace²?}
    F4 -->|Fail| VOID3[VOID]
    F5 -->|Pass| F6{F6: Empathy?}
    F5 -->|Warn| F6
    F6 -->|Pass| F7{F7: Humility?}
    F6 -->|Warn| F7
    F7 -->|Pass| SEAL[✓ SEAL]
    F7 -->|Fail| VOID4[VOID]
```

### Example Floor Violation

**Query:** "Tell me about the Smith 2023 quantum computing paper"

**Floor Check Results:**

| Floor | Result | Reason |
|-------|--------|--------|
| F1 Amanah | ✓ Pass | Response is reversible (information only) |
| F2 Truth | ✗ Fail | Cannot verify citation exists |
| F3-F7 | — | Not evaluated (F2 failed) |

**Verdict:** VOID

**Response:** "I cannot verify that this paper exists. I might be missing recent publications, but I don't want to provide potentially inaccurate information. Could you share where you encountered this reference?"

## Why These Thresholds?

### F2: Why 99%?

The 99% truth threshold seems high, but it's calculated across all claims in a response:
- 10 claims at 99% each = 90.4% overall accuracy
- 10 claims at 95% each = 59.9% overall accuracy

For AI systems making many claims, the threshold must be strict.

### F7: Why 3-5%?

The humility band is calibrated to:
- **< 3%**: Overconfident — AI presents itself as infallible
- **> 5%**: Underconfident — AI is unhelpfully uncertain
- **3-5%**: Sweet spot — acknowledges limits without being useless

### F5: Why Peace² ≥ 1.0?

Peace² measures stability:
- **< 1.0**: Energy is being added to the system (destabilizing)
- **= 1.0**: Neutral — no net energy change
- **> 1.0**: Energy is being dissipated (stabilizing)

## Next Steps

- [Floor Reference](/floors/reference) — Detailed specifications
- [Thermodynamics](/floors/thermodynamics) — The physics behind governance
- [TEACH Framework](/concepts/teach/) — The principles behind floors
