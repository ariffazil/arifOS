# ADR-013: Mapping Intelligence Layers to Constitutional Governance Routing
**Status:** `PROPOSED`
**Owner:** Arif bin Fazil (Sovereign/Architect)
**Date:** 2026-06-21

---

## Context

To manage system risk and maintain human sovereignty across different operational modes, we must formally map the three layers of intelligence (Pure LLM, Grounded Retrieval, and Autonomous Agentic Loops) to the arifOS constitutional floors, tool definitions, and verification paths. 

Without this routing matrix, unconstrained agentic loops can mutate system state, and static parametric assumptions can bypass real-time evidence verification checks.

---

## Decisions

We establish a formal mapping boundary for each of the three intelligence layers:

### 1. Pure LLM Layer (Parametric Generation)
- **Role**: Creative synthesis, formatting, non-critical explanation, and style normalization.
- **Mapping Tools**: [arif_reply_compose](file:///root/arifOS/arifosmcp/runtime/tools.py#L9555) (modes: `compose`, `style`, `cite`, `summary`).
- **Enforced Floors**: F2 (Affordance classification), F4 (Clarity/Prose check).
- **Veto Boundary**: Implicit. No state change permitted.

### 2. Tool Search & Fetch Layer (Grounded Retrieval)
- **Role**: Real-time factual grounding, source discovery, and textual evidence compilation.
- **Mapping Tools**: `arif_search` (facade), `arif_fetch` (facade), [arif_sense_observe](file:///root/arifOS/arifosmcp/runtime/tools.py#L5924), [arif_evidence_fetch](file:///root/arifOS/arifosmcp/runtime/tools.py#L7016).
- **Enforced Floors**: F1 (Amanah), F2 (Affordance), F4 (Clarity), F11 (Audit trails for evidence).
- **Veto Boundary**: Optional. Escalates to 888_HOLD only if target domains cross privacy or safety boundaries.

### 3. Agentic Intelligence Agent Layer (Autonomous Loop & Planning)
- **Role**: Multi-step task execution, code generation/compilation, system deployment, and database migrations.
- **Mapping Tools**: [arif_mind_reason](file:///root/arifOS/arifosmcp/runtime/tools.py#L7755) (modes: `reason`, `plan`, `plan_review`), [arif_judge_deliberate](file:///root/arifOS/arifosmcp/runtime/tools.py#L11796) (verdict mapping), [arif_forge_execute](file:///root/arifOS/arifosmcp/runtime/tools.py#L14096), [arif_vault_seal](file:///root/arifOS/arifosmcp/runtime/tools.py#L12899).
- **Enforced Floors**: Full F1–F13 stack, explicitly:
  - F7 (Simulation/Safety checks before execution)
  - F8 (Sandboxed environment boundary)
  - F13 (Absolute Sovereign Veto / Ed25519 signature requirement)
- **Veto Boundary**: **Mandatory**. No mutating action is allowed to proceed without an approved plan ID and explicit human sovereign ratification.

---

## Intelligence Layers & Governance Matrix

| Intelligence Layer | Primary Action Class | Max Risk Tier | Mandatory Veto Path | Active Floors | Key Failure Mode Mitigations |
|---|---|---|---|---|---|
| **1. Pure LLM** | `REASON` / `OBSERVE` | T0 / Low | None (Pre-approved) | F2, F4 | Output filtered by F4 clarity engine to prevent fabrications. |
| **2. Search/Fetch** | `OBSERVE` | T1 / Medium | Post-execution Audit | F1, F2, F4, F11 | `arif_fetch` archives text snapshots in [VAULT999](file:///root/arifOS/VAULT999/) for replayability. |
| **3. Autonomous Agent** | `MUTATE` / `EXECUTE` | T2–T3 / High | Pre-execution Checkpoint (Ed25519) | F1–F13 | Plan sandbox isolation (F8) and physical state rollbacks. |
