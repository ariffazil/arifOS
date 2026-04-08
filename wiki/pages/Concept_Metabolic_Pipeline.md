---
type: Concept
tags: [architecture, runtime, governance, pipeline, stages, tools]
sources: [constitutional_map.py, server.py, tools.py, arifosmcp-metabolic-pipeline-audit-2026-04-08.md]
last_sync: 2026-04-08
confidence: 1.0
---

# Concept: Metabolic Pipeline

## Definition
The **Metabolic Pipeline** is the 11-stage thermodynamic execution path discovered in the `arifosmcp` kernel. It transforms raw, high-entropy user intent into "cooled," audited, and sealed intelligence. 

Unlike traditional "linear" mechanical processing, the arifOS pipeline supports both **Atomic Tool Invocations** and **Integrated AGI Workflows**.

---

## 🏛️ The 9+1+1 Canonical Surface

To resolve naming drift, arifOS maintains a clear distinction between the **numbered stage** (Math/CCC Layer) and the **functional alias** (App/AAA Layer).

| Stage | Math/CCC Name | App/AAA Alias | Legacy Alias (Horizon) |
| :--- | :--- | :--- | :--- |
| **000** | `void_000` | `arifos_init` | `init_anchor` |
| **111** | `anchor_111` | `arifos_sense` | `physics_reality` |
| **222** | `explore_222` | `arifos_mind` (partial) | `agi_mind` |
| **333** | `agi_333` | `arifos_mind` (full) | `agi_mind` |
| **444** | `kernel_444` | `arifos_route` | `arifOS_kernel` |
| **555** | `forge_555` | `arifos_memory` | `engineering_memory` |
| **666** | `rasa_666` | `arifos_heart` | `asi_heart` |
| **777** | `math_777` | `arifos_ops` | `math_estimator` |
| **888** | `apex_888` | `arifos_judge` | `apex_soul` |
| **999** | `seal_999` | `arifos_vault` | `vault_ledger` |
| **+1** | `forge_bridge`| `arifos_forge` | `code_engine` |
| **EXT** | `vps_audit` | `arifos_vps_monitor`| `vps_monitor` |

---

## Pipeline Operational Modes

The pipeline is not strictly linear; it adapts based on the complexity of the request (see [[Concept_Governance_Enforcer]] for classification).

### 1. Manual / Sequence Mode
Tools are called independently. The user (or an agent) orchestrates the sequence (e.g., `init` → `sense` → `route`). This provides maximum transparency and granularity.

### 2. Auto-AGI Mode (The "Typed" Pipeline)
Used by `arifos_mind`. This mode executes an internal, governed chain of logic within a single tool call:
1. **Sense Stage**: Reality grounding.
2. **Mind Stage**: Cognitive hypothesis generation.
3. **Heart Stage**: Safety and risk evaluation.
4. **Judge Stage**: Internal verdict generation before returning to the user.

---

## Resilience & Fail-safes
The pipeline is wrapped in the **GlobalPanicMiddleware**. If any kernel exception occurs during metabolism, the system triggers a **"Constitutional VOID."** This ensures that a system error never results in an un-audited or un-governed output.

---

## Related
- [[What-is-arifOS]]
- [[Concept_Architecture]]
- [[Concept_Deployment_Architecture]]
- [[Concept_Governance_Enforcer]]
