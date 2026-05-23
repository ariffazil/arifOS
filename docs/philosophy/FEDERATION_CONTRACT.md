# arifOS Federation Contract v1.0
## DITEMPA BUKAN DIBERI

This document defines the sovereign boundaries and interaction protocols for the arifOS Federated Intelligence Stack.

> **Machine is substrate. Governance is constraint. Intelligence is interpretation. Judgment remains Arif.**

### 1. Sovereign Authority Map
| Organ | Title | Primary Responsibility | Authority Level |
|---|---|---|---|
| **arifOS** | Constitutional Intelligence Kernel | Governance, routing, judgment, memory, audit | L5 Governance Kernel / L4 Constitutional Adjudication |
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

### 4. Contract Files

This Markdown document is the human-readable federation contract. The
machine-readable companion is:

- `contracts/federation.yaml`

Each primary federation repo must also carry:

- `BOUNDARY.md` — repo authority in four sections: Owns, Does Not Own,
  Imports From, Exports To.
- `contracts/mcp_surface.yaml` — machine-readable MCP/runtime surface contract.

### 5. Authority Boundaries

| Repo | Authority | Exports | Must Not Become |
|---|---|---|---|
| `arifOS` | Constitutional kernel | Floor policy, verdict context, memory/audit contracts, VAULT999 receipts | Domain organ, cockpit, deployment shell |
| `AAA` | Control plane | Session identity, operator intent, A2A events, cockpit status | Hidden governance kernel or seal writer |
| `A-FORGE` | Execution substrate | Execution plans, release provenance, rollback evidence, ops cost | Rival constitution or final judge |
| `GEOX` | Earth evidence | Geological evidence, prospect risk, contradiction scans, Earth artifacts | Capital allocator or constitutional judge |
| `WEALTH` | Capital evidence | Risk scores, capital memos, viability scenarios, hold triggers | Geological truth engine or sovereign allocator |

### 6. Cross-Repo Hold Triggers

The following changes require `888_HOLD` unless Arif explicitly authorizes the
exact action:

1. Any change that alters the authority boundary of more than one canonical repo.
2. Any secret rotation, `.env` mutation, or git history rewrite.
3. Any public production deployment without build, test, health, and rollback
   evidence.
4. Any irreversible host, database, volume, or git mutation.
5. Any attempt by an agent, bot, or deployment shell to issue `999_SEAL`.
