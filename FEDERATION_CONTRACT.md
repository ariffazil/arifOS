# arifOS Federation Contract v1.0
## DITEMPA BUKAN DIBERI

This document defines the sovereign boundaries and interaction protocols for the arifOS Federated Intelligence Stack.

> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**

### 1. Sovereign Authority Map
| Organ | Title | Primary Responsibility | Authority Level |
|---|---|---|---|
| **arifOS** | Constitutional Intelligence Kernel | Governance, routing, judgment, memory, audit | L5 APEX / L4 ASI |
| **AAA** | Control Plane Agent Gateway | Identity broker, OAuth, agent registry, session anchoring | L3 Control Plane |
| **A-FORGE** | Execution Intelligence / Forge Engine | Build, deploy, artifact execution under governance | L3 Execution |
| **GEOX** | Earth Intelligence / Governed World Model | Physical Earth, geoscience, subsurface, evidence preparation | L2 Evidence Organ |
| **WEALTH** | Resource Intelligence / Capital Thermodynamics | Capital, flow, risk, allocation, stewardship | L2 Evidence Organ |
| **WELL** | Vitality Intelligence | Human readiness, machine substrate, coupled state, governance coherence | L2 Organ |
| **VAULT999** | Immutable Provenance Ledger | Audit, sealed lineage, append-only memory | L1 Persistence |
| **ARIF/F13** | Human Sovereign | Final veto, constitutional witness | L6 Sovereign |

### 2. Interaction Rules
1. **One Repo, One Authority:** No organ shall implement logic belonging to another (e.g., A-FORGE does not judge).
2. **Evidence Before Verdict:** No SEAL verdict shall be issued without a valid evidence object from a domain organ.
3. **Formal Over Heuristic:** Transition all heuristic LLM checks (F1-F13) to deterministic formal verification (Z3/SMT).
4. **Immutable Trace:** Every tool execution must produce a VAULT999 receipt with a valid `trace_id`.

### 3. Canonical Schemas
All communication between organs must adhere to the standard JSON schemas defined in `arifos/schemas/`.
