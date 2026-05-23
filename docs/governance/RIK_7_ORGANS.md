# Real Intelligence Kernel (RIK) — The 7 Organs

**Classification:** Constitutional Architecture
**Status:** ACTIVE
**Seal:** VAULT999

> "The shell is a BODY front-end. The authority resides in the RIK."

## 1. Governance Kernel (GK)
- **Role:** F1–F13 Floors, 000–999 pipeline.
- **Law:** The *only* legitimate law source; everything else must defer.

## 2. Planning Organ (PO)
- **Role:** INTENT → PLAN task graph, PlanReceipts.
- **Law:** No direct INTENT → EXECUTION for non-trivial work. All intent must pass through planning.

## 3. Execution Engine (EE)
- **Role:** AF-FORGE style orchestrator.
- **Law:** Only runs APPROVED plans. Enforces 888 HOLD for IRREVERSIBLE / HIGH risk tasks.

## 4. Memory Hierarchy (MH)
- **Role:** Multi-tier memory substrate.
- **Sub-layers:** Redis (short-term), Postgres (canonical intents/plans/seals), Qdrant (semantic).

## 5. Tool Boundary (TB)
- **Role:** Execution surface constraint.
- **Law:** MCP tools; every world-side effect is a tool call with planid/taskid/epochid in logs.

## 6. Cognitive Layer (CL)
- **Role:** Epistemic processing.
- **Law:** LLMs and embedding models; all outputs must be GK-checked and tagged with uncertainty.

## 7. Sovereign Interface (SI)
- **Role:** The Human Veto.
- **Law:** Arif's veto + approvals, Nine-Signal view, HOLD queue management.

---

### Bash-Level Integration Boundary
For shell-level integration (e.g., the `root` terminal harness), the critical front-line organs are **GK, PO, EE, TB, SI**. The **MH** and **CL** operate behind this boundary as supporting substrates. The shell must never bypass the GK to directly access the EE or TB for non-trivial execution.
