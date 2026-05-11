# arifOS Federation Contract v1.0
## DITEMPA BUKAN DIBERI

This document defines the sovereign boundaries and interaction protocols for the arifOS Federated Intelligence Stack.

### 1. Sovereign Authority Map
| Organ | Primary Responsibility | Authority Level |
|---|---|---|
| **arifOS** | Constitutional Kernel, Verdict Engine | L5 APEX / L4 ASI |
| **AAA** | Identity Broker, OAuth, Agent Registry | L3 Control Plane |
| **A-FORGE** | Execution Shell, Sandbox, State Machine | L3 Execution |
| **GEOX** | Earth Intelligence (Seismic, Basin, Physics) | L2 Evidence Organ |
| **WEALTH** | Capital Intelligence (NPV, IRR, Risk) | L2 Evidence Organ |
| **VAULT999** | Immutable Ledger, Audit Trail | L1 Persistence |
| **ARIF/F13** | Final Human Veto | L6 Sovereign |

### 2. Interaction Rules
1. **One Repo, One Authority:** No organ shall implement logic belonging to another (e.g., A-FORGE does not judge).
2. **Evidence Before Verdict:** No SEAL verdict shall be issued without a valid evidence object from a domain organ.
3. **Formal Over Heuristic:** Transition all heuristic LLM checks (F1-F13) to deterministic formal verification (Z3/SMT).
4. **Immutable Trace:** Every tool execution must produce a VAULT999 receipt with a valid `trace_id`.

### 3. Canonical Schemas
All communication between organs must adhere to the standard JSON schemas defined in `arifos/schemas/`.
