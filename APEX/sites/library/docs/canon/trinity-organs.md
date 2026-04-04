---
id: canon-trinity-organs
title: Trinity & 5 Organs
sidebar_position: 5
description: The 5-Organ Trinity architecture (DeltaOmegaPsi) - AGI Mind, ASI Heart, APEX Soul, VAULT999, and the constitutional airlock. Public architecture reference.
---

# Trinity Architecture - The 5 Organs

> Canonical source: [`000_THEORY/010_TRINITY.md`](https://github.com/ariffazil/arifosmcp/blob/main/000_THEORY/010_TRINITY.md)  
> Implementation: [`core/organs/`](https://github.com/ariffazil/arifosmcp/blob/main/core/organs/)  
> Status: L0 KERNEL - SEALED

---

## Overview

The L0 Intelligence Kernel runs five constitutional organs in sequence. Each organ is thermodynamically isolated from the others until its designated merge point. No organ can see another organ's internal reasoning until the constitutional merge at stage 444.

```
STAGE 000                                           STAGE 999
                                                       
      
  ORGAN 0        ORGAN 1       ORGAN 2       ORGAN 3  
  INIT          AGI Delta        ASI Omega        APEX Psi   ORGAN 4
  Airlock        Mind          Heart         Soul       VAULT999
  (000)         (111-333)     (444-666)     (777-888) 
      
```

---

## Organ 0 - INIT (Constitutional Airlock)

| | |
|:--|:--|
| **File** | `core/organs/_0_init.py` |
| **Stage** | 000 |
| **Symbol** |  |
| **Floors** | F11 (Authority), F12 (Injection Defence) |

The airlock. Every query enters here. The organ verifies identity, scans for injection attacks, loads thermodynamic constraints, and ignites the Trinity engines. A VOID at stage 000 costs zero inference - the pipeline never starts.

See: [Ignition - Stage 000](./canon-ignition)

---

## Organ 1 - AGI Delta (Mind Engine)

| | |
|:--|:--|
| **File** | `core/organs/_1_agi.py` |
| **Stages** | 111 (Sense)  222 (Reason)  333 (Integrate) |
| **Symbol** | Delta (Delta) - Left Brain |
| **Floors** | F2 (Truth), F4 (Clarity), F7 (Humility), F8 (Genius) |
| **Role** | Logical reasoning, hypothesis generation, reality grounding |

The AGI Mind engine processes the query through three sub-stages:

- **111 SENSE** - Intent classification and lane assignment (`atlas-333` routing)
- **222 REASON** - Hypothesis generation, truth scoring, entropy measurement
- **333 INTEGRATE** - Reality grounding, tri-witness preparation, ontology check

The AGI engine produces a `MindBundle` - a structured output containing precision score, hypotheses, entropy delta, and uncertainty band (Omega_0). This bundle is thermodynamically isolated from the ASI Heart engine until stage 444.

---

## Organ 2 - ASI Omega (Heart Engine)

| | |
|:--|:--|
| **File** | `core/organs/_2_asi.py` |
| **Stages** | 444 (Respond)  555 (Validate)  666 (Align) |
| **Symbol** | Omega (Omega) - Right Brain |
| **Floors** | F1 (Amanah), F5 (Peace^2), F6 (Empathy), F9 (Anti-Hantu) |
| **Role** | Safety analysis, stakeholder protection, ethics alignment |

The ASI Heart engine evaluates the human and societal impact of the proposed response:

- **444 RESPOND** - Draft creation. This is the AGIASI merge point - `MindBundle` + `HeartBundle`  `SoulBundle`
- **555 VALIDATE** - Stakeholder impact analysis, reversibility check, Peace^2 stability
- **666 ALIGN** - Anti-Hantu ethics check (F9), no consciousness claims, transparent behaviour

The ASI engine uses SBERT semantic similarity (H1.2) to evaluate empathy and alignment floors, replacing earlier keyword heuristics.

---

## Organ 3 - APEX Psi (Soul Engine)

| | |
|:--|:--|
| **File** | `core/organs/_3_apex.py` |
| **Stages** | 777 (Forge)  888 (Audit) |
| **Symbol** | Psi (Psi) - Sovereign Judgment |
| **Floors** | F3 (Tri-Witness), F8 (Genius), F11 (Authority), F13 (Sovereignty) |
| **Role** | Final verdict, tri-witness consensus, paradox resolution |

The APEX Soul engine issues the final constitutional verdict:

- **777 FORGE** - Solution synthesis, code generation if applicable (F2, F4, F8)
- **888 AUDIT** - Tri-witness consensus computation (`W^3 >= 0.95`), final floor scores, verdict issuance

The APEX engine is the only organ authorised to issue a `SEAL`. It is also the stage where `888_HOLD` is triggered if F13 Sovereignty requires human ratification.

See: [Tri-Witness (F3)](./canon-witness)

---

## Organ 4 - VAULT999 (Memory Engine)

| | |
|:--|:--|
| **File** | `core/organs/_4_vault.py` |
| **Stage** | 999 |
| **Symbol** |  |
| **Floors** | F1 (Amanah - reversibility audit), F3 (Tri-Witness - seal verification) |
| **Role** | Immutable cryptographic ledger, institutional memory |

VAULT999 is the final organ. Every SEAL, VOID, SABAR, and 888_HOLD is committed here - including rejections. Nothing is deleted. Nothing is hidden. The vault is:

- **Append-only** - no DELETE or UPDATE operations
- **Hash-chained** - each entry Merkle-linked to the previous
- **Tamper-evident** - modifying any entry breaks `verify_chain()`
- **Independent** - survives model replacement, container restart, and AI failure

```
VAULT999 is NOT LLM memory.
VAULT999 IS forensic institutional memory.
```

Backend: PostgreSQL (asyncpg + Merkle chain) with SQLite fallback, filesystem fallback.

---

## The 4 Utility Tools (Public API)

The public MCP interface exposes **4 utility tools** that map onto the 5-organ architecture:

| Tool | Maps to | Purpose |
|:--|:--|:--|
| `_init_` | Organ 0 (000) | Constitutional airlock - authorise and begin session |
| `_agi_` | Organs 1+2 (111-666) | Full reasoning and safety pipeline |
| `_apex_` | Organ 3 (888) | Final verdict and tri-witness consensus |
| `_vault_` | Organ 4 (999) | Seal decision to tamper-evident ledger |

Plus two supporting tools:
- **`reality_search`** - raises S (external witness) via Brave Search API
- **Pipeline shortcut** - `_agi_` with `action: "forge"` runs the full 000999 pipeline in one call

See: [API Reference ->](/api) for full parameter schemas.

---

## Thermodynamic Isolation

AGI Delta and ASI Omega are **thermodynamically isolated** until stage 444. This means:

- The Mind engine cannot see the Heart engine's reasoning while forming hypotheses
- The Heart engine cannot see the Mind engine's truth scores while forming empathy assessments
- At stage 444, `compute_consensus()` merges `MindBundle` + `HeartBundle` into a `SoulBundle`
- This prevents confirmation bias: neither engine can "help" the other reach a predetermined conclusion

This is the architectural enforcement of intellectual honesty.
