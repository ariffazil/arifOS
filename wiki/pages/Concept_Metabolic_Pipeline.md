---
type: Concept
tier: 20_RUNTIME
strand:
- architecture
audience:
- engineers
difficulty: advanced
prerequisites:
- Metabolic_Loop
tags:
- architecture
- runtime
- governance
- pipeline
- stages
- tools
sources:
- tool_specs.py
- tools.py
- capability_map.py
- Audit_MCP_Tools_vs_Wiki.md
last_sync: '2026-04-10'
confidence: 1.0
---

# Concept: Metabolic Pipeline

## Definition

The **Metabolic Pipeline** is the 9-stage thermodynamic execution path of arifOS (8 active processing stages + vault seal). It transforms raw, high-entropy user intent into "cooled," audited, and sealed intelligence. 

The pipeline supports two primary execution modes: **Sequence Mode** (Manual) and **Integrative Mode** (Auto-AGI).

---

## 🏛️ The 12 Canonical Tools

arifOS standardizes on **Underscore Aliases** mapping to **Numbered Stages**. The registry contains 12 tools (including `arifos_kernel` as the canonical 444 stage, with `arifos_route` as a transitional alias).

| Stage | Canonical Alias | Trinity | Layer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **000** | `arifos_init` | Ψ | GOV | Session anchoring |
| **111** | `arifos_sense` | Δ | MAC | Reality grounding |
| **111** | `arifos_vps_monitor` | Δ | MAC | VPS telemetry (separate tool) |
| **333** | `arifos_mind` | Δ | INT | Structured reasoning |
| **444** | `arifos_kernel` | Δ/Ψ | GOV | Primary metabolic conductor *(canonical)* |
| **444** | `arifos_route` | Δ/Ψ | GOV | Alias for `arifos_kernel` *(transitional)* |
| **555** | `arifos_memory` | Ω | INT | Vector memory recall |
| **666** | `arifos_heart` | Ω | INT | Safety & empathy critique |
| **777** | `arifos_ops` | Δ | MAC | Thermodynamic estimation |
| **888** | `arifos_judge` | Ψ | GOV | Final constitutional verdict |
| **999** | `arifos_vault` | Ψ | GOV | Immutable audit ledger |
| **010** | `arifos_forge` | Δ | EXE | AF-FORGE execution bridge |

---

## Pipeline Execution Modes

### 1. Manual Sequence Mode

Tools are called independently. This provides maximum transparency for auditors.

- Example: `init` → `sense` → `judge` → `vault`.

### 2. Auto-AGI Mode (The "Typed" Pipeline)

The `arifos_mind` tool can execute an internal, governed chain of reasoning within a single call. This "Typed" pipeline handles the transition between Sensing, Thinking, and Red-Teaming (Heart) before returning a synthesized result.

---

## Fail-safes & Hard-Stops

- **GlobalPanicMiddleware**: Intercepts kernel panics and emits a **Constitutional VOID**.
- **GovernanceEnforcer**: Performs pre-tool classification (Class A/B/C) and structural enforcement of Floors F1, F12, and F13.

---

## Related

- [[Concept_Architecture]]
- [[Concept_Governance_Enforcer]]
- [[Concept_Floors]]
- [[Audit_MCP_Tools_vs_Wiki]]
