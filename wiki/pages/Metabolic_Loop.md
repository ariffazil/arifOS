---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
audience:
- engineers
difficulty: intermediate
prerequisites:
- Trinity_Architecture
tags:
- metabolism
- pipeline
- runtime
- execution
sources:
- README.md
- CONSTITUTION.md
last_sync: '2026-04-10'
confidence: 1.0
---

# The Metabolic Loop (000-999 Pipeline)

The **Metabolic Loop** is the 9-stage execution path that every request in arifOS must follow. It transforms raw intent into governed, auditable action.

## Pipeline Stages

1. **000_INIT (Anchor)**: Session initialization and identity binding.
2. **111_SENSE (Reality)**: Reality grounding and evidence gathering.
3. **222_EXPLORE (Divergence)**: Generating structural hypotheses.
4. **333_MIND (AGI)**: Structured reasoning and constitutional filtering.
5. **444_KERNEL (Kernel)**: Unified metabolic conductor — INPUT → ORCHESTRATE → OUTPUT pipeline.
6. **555_MEM (Engineer)**: Context retrieval and memory management.
7. **666_HEART (RASA)**: Safety critique and empathy assessment. (Note: ASI as pipeline band label is F10 ontology violation — use HEART or RASA.)
8. **777_OPS (Thermo)**: Resource estimation and cost analysis.
9. **888_JUDGE (APEX)**: Final constitutional verdict.
10. **999_SEAL (Vault)**: Immutable audit log and ledger entry.

## KERNEL rCore Architecture (444_KERNEL)

The KERNEL at stage 444 is the **Unified KERNEL rCore** — a three-stage metabolic conductor:

```
┌─────────────────────────────────────────────────────────────┐
│  KERNEL rCore (Unified)                                     │
│                                                             │
│  INPUT ─────► ORCHESTRATE ─────► OUTPUT                    │
│     │              │               │                        │
│  Normalize    Classify +      Seal +                     │
│  Query        Route +        Continuity                  │
│  Assemble     Invoke +        Update                     │
│  Context      Govern                                   │
└─────────────────────────────────────────────────────────────┘
```

**INPUT Stage**: Query normalization, session context assembly
**ORCHESTRATE Stage**: Classification, tool selection, governance enforcement
**OUTPUT Stage**: Envelope sealing, continuity state management

See: `arifosmcp/runtime/kernel_core.py`

## Why "Metabolic"?

Like biological metabolism, this pipeline ingests raw input, processes it through multiple filters (Floors), extracts value (safe actions), and excretes waste (blocked actions, logs). This process maintains system **homeostasis** (constitutional invariants).

Citations:

- `README.md` (Raw)
- `wiki/raw/CONSTITUTION.md` (Raw)
