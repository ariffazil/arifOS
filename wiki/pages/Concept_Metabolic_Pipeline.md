---
type: Concept
tags: [architecture, runtime, governance, pipeline, stages, tools]
sources: [tool_specs.py, tools.py, capability_map.py, Audit_MCP_Tools_vs_Wiki.md]
last_sync: 2026-04-08
confidence: 1.0
---

# Concept: Metabolic Pipeline

## Definition
The **Metabolic Pipeline** is the 11-stage thermodynamic execution path of arifOS. It transforms raw, high-entropy user intent into "cooled," audited, and sealed intelligence. 

The pipeline supports two primary execution modes: **Sequence Mode** (Manual) and **Integrative Mode** (Auto-AGI).

---

## 🏛️ The 11 Canonical Tools

To resolve naming drift, arifOS standardizes on **Underscore Aliases** mapping to **Numbered Stages**.

| Stage | Canonical Alias | Trinity | Layer | Legacy Source |
| :--- | :--- | :--- | :--- | :--- |
| **000** | `arifos_init` | Ψ | GOV | `init_anchor` |
| **111** | `arifos_sense` | Δ | MAC | `physics_reality` |
| **333** | `arifos_mind` | Δ | INT | `agi_mind` |
| **444** | `arifos_route` | Δ/Ψ | GOV | `arifOS_kernel` |
| **555** | `arifos_memory` | Ω | INT | `engineering_memory` |
| **666** | `arifos_heart` | Ω | INT | `asi_heart` |
| **777** | `arifos_ops` | Δ | MAC | `math_estimator` |
| **888** | `arifos_judge` | Ψ | GOV | `apex_soul` |
| **999** | `arifos_vault` | Ψ | GOV | `vault_ledger` |
| **010** | `arifos_forge` | Δ | EXE | *(New: AF-FORGE Bridge)* |
| **EXT** | `arifos_vps_monitor` | Δ | MAC | *(New: Telemetry)* |

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
