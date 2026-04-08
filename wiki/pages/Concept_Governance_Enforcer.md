---
type: Concept
tags: [architecture, governance, enforcer, compliance, floors, query-class]
sources: [governance_enforcer.py, AGENTS.md, K000_LAW.md]
last_sync: 2026-04-08
confidence: 1.0
---

# Concept: Governance Enforcer

The **Governance Enforcer** (`governance_enforcer.py`) is the structural "Hard Stop" mechanism of arifOS. It ensures that constitutional principles are not just theoretical goals, but enforced runtime constraints.

## Query Classification (The A/B/C Model)

Before a tool is invoked, the Enforcer classifies the user's intent to determine the required level of metabolic scrutiny.

| Class | Name | Complexity | Enforcement Level |
| :--- | :--- | :--- | :--- |
| **Class A** | INFORMATIONAL | Analytical / explanatory | Direct model response allowed. |
| **Class B** | GOVERNED | State mutation / memory write | Full Floor check (F1-F13). |
| **Class C**| CRITICAL | Irreversible / sovereign | Requires F11 verified identity + SEAL verdict. |

---

## Structural Enforcement (Hard vs. Soft)

The Enforcer differentiates between **Structural Floors** (hard-coded logic) and **Heuristic Floors** (model-derived estimations).

### 1. Structural Logic (Hard Stops)

- **F1 (Amanah)**: Verified by the `irreversibility` flag in the tool envelope. If a tool reports an irreversible action without an explicit acknowledgement, the Enforcer issues a **BLOCKED_F1** verdict.
- **F12 (Injection Guard)**: Verified via automated scanning of `intent`. If a prompt injection pattern is detected, the Enforcer issues a **BLOCKED_VOID** verdict before the model is ever called.
- **F13 (Sovereign Gate)**: Any kernel failure or unhandled exception triggers the **GlobalPanicMiddleware**, emitting a system-wide VOID as a fail-safe.

## Pipeline Operational Modes

The pipeline is not strictly linear; it adapts based on the complexity of the request (see [[Concept_Governance_Enforcer]] for classification).

### 1. Manual / Sequence Mode

Tools are called independently. The user (or an agent) orchestrates the sequence (e.g., `init` → `sense` → `route`). This provides maximum transparency and granularity.

### 2. Auto-AGI Mode (The "Typed" Pipeline)

Used by `arifos_mind`. This mode executes an internal, governed chain of logic within a single tool call:

1.  **Sense Stage**: Reality grounding.
2.  **Mind Stage**: Cognitive hypothesis generation.
3.  **Heart Stage**: Safety and risk evaluation.
4.  **Judge Stage**: Internal verdict generation before returning to the user.

---

## Resilience & Fail-safes

The pipeline is wrapped in the **GlobalPanicMiddleware**. If any kernel exception occurs during metabolism, the system triggers a **"Constitutional VOID."** This ensures that a system error never results in an un-audited or un-governed output.

### 2. Heuristic Logic (Engine Softness)

- **F7 (Humility)**: While the constitution defines complex mathematical formulas ($\Omega < 0.03$), the practical implementation often uses simplified heuristics like `estimate_omega_zero_heuristic` for real-time responsiveness.
- **OmegaZero ($\Omega_0$)**: Used to evaluate candidate actions. If the heuristic score indicates high uncertainty/hallucination, the result is downgraded to **SABAR** (Hold) or **VOID**.

---

## The Verdict Cascade

The Enforcer operates as a non-bypassable guard. If a tool returns any verdict other than `SEAL` or `PARTIAL` (with pass flags), the model output is **BLOCKED**.

> [!IMPORTANT]
> **No Bypass Rule**: The Governance Enforcer is the only entity authorized to "open the gate" for model propagation. This prevents common failure modes where an LLM disregards a tool's safety warnings.

---

## Related
- [[Concept_Floors]]
- [[Concept_Metabolic_Pipeline]]
- [[What-is-arifOS]]
