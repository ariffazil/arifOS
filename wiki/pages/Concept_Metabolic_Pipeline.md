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
- APEX/ASF1/tool_registry.json
- tool_specs.py
- tools.py
- capability_map.py
- Audit_MCP_Tools_vs_Wiki.md
- wiki/raw/governed_packet_bands_and_godellock_ingest_2026-04-11.md
last_sync: '2026-04-11'
confidence: 0.96
---

# Concept: Metabolic Pipeline

## Definition

The **Metabolic Pipeline** is the 9-stage thermodynamic execution path of arifOS (8 active processing stages + vault seal). It transforms raw, high-entropy user intent into "cooled," audited, and sealed intelligence. 

The pipeline supports two primary execution modes: **Sequence Mode** (Manual) and **Integrative Mode** (Auto-AGI).

---

## 🏛️ Current Public Canon Candidate

The current registry target is a **10-tool public canon**. Transitional names such as `arifos_route`, `arifos_reply`, and `arifos_vps_monitor` still exist in runtime and compatibility layers, so this pipeline page treats them as migration surfaces rather than stable public canon.

| Stage | Canonical Alias | Trinity | Layer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **000** | `arifos_init` | Ψ | GOV | Session anchoring |
| **111** | `arifos_sense` | Δ | MAC | Reality grounding |
| **333** | `arifos_mind` | Δ | INT | Structured reasoning |
| **444** | `arifos_kernel` | Δ/Ψ | GOV | Primary metabolic conductor |
| **555** | `arifos_memory` | Ω | INT | Vector memory recall |
| **666** | `arifos_heart` | Ω | INT | Safety & empathy critique |
| **777** | `arifos_ops` | Δ | MAC | Thermodynamic estimation |
| **888** | `arifos_judge` | Ψ | GOV | Final constitutional verdict |
| **999** | `arifos_vault` | Ψ | GOV | Immutable audit ledger |
| **010** | `arifos_forge` | Δ | EXE | A-FORGE execution bridge |

## Proposed 3x3 + 1 Reading

The cleanest long-term reading of the pipeline is:

| Stage / Lane | Reality | Intelligence | Governance |
|--------------|---------|--------------|------------|
| Ingest | `arifos_init` | `arifos_memory` | `arifos_sense` |
| Deliberate | `arifos_ops` | `arifos_mind` | `arifos_heart` |
| Act | `arifos_forge` | `arifos_kernel` | `arifos_judge` |

Plus one sovereign boundary:

- `arifos_vault`

This remains a **target organizing model**, not yet a claim that runtime/export surfaces are fully clean.

---

## Pipeline Execution Modes

### 1. Manual Sequence Mode

Tools are called independently. This provides maximum transparency for auditors.

- Example: `init` → `sense` → `judge` → `vault`.

### 2. Auto-AGI Mode (The "Typed" Pipeline)

The `arifos_mind` tool can execute an internal, governed chain of reasoning within a single call. This "Typed" pipeline handles the transition between Sensing, Thinking, and Red-Teaming (Heart) before returning a synthesized result.

## Proposed Governed Packet Contract

The newest doctrine proposal describes each MCP call as a **governed packet** carrying:

- identity and budget header
- decision contract
- tripwire thresholds
- payload
- verdict expectations

It also proposes three mandatory output bands for every tool:

1. physics note
2. math metrics
3. linguistic anchor

Special override:

- `arifos_init` and `arifos_vault` always emit `DITEMPA BUKAN DIBERI`

This is documented here as a **proposed output contract**, not as proven runtime behavior.

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
- [[Concept_Godellock]]
