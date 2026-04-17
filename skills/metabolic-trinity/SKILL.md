# SKILL: metabolic-trinity — Unified arifOS Intelligence Federation

---
name: metabolic-trinity
description: |
  The master manual for interacting with the 4 core arifOS organs: 
  @WELL (Human), @WEALTH (Economic), @GEOX (Physical), and AF-FORGE (Agentic).
  Teaches agents the Birth-to-Seal lifecycle with biological feedback.

  Load with: /skill:metabolic-trinity
---

# metabolic-trinity SKILL

## The Organ Federation

| Organ | Role | Axiom | Primary Tool |
| :--- | :--- | :--- | :--- |
| **@WELL** | Substrate | *Body is the Mirror* | `well_readiness` |
| **@WEALTH** | Capital | *Wealth is Organized Energy*| `calculate_npv` |
| **@GEOX** | Earth | *The Earth Does Not Lie* | `verify_location` |
| **AF-FORGE** | Action | *Execution is Alignment* | `arifos_forge` |

## Core Workflow: The Metabolic Cycle

Every agent interaction MUST follow this 6-step grounding cycle:

1.  **IGNITION (000_INIT)**
    *   Call `arifos_init`.
    *   **Mandate:** Check `well_readiness` BEFORE proposing heavy plans.
    *   *Constraint:* If WELL score < 60, prioritize low-complexity tasks.

2.  **GROUNDING (111_SENSE)**
    *   Poll **@GEOX** for physical constraints (location, rock mechanics).
    *   Poll **@WEALTH** for economic viability (NPV, risk thresholds).
    *   **Goal:** Ensure the task is physically possible and economically sound.

3.  **PLANNING (333_EXPLORE)**
    *   Generate a metabolic plan using `AF-FORGE`.
    *   **Mandate:** Present at least 3 trade-off options.

4.  **FEEDBACK (777_REASON)**
    *   Signal cognitive pressure to **@WELL** using `well_pressure`.
    *   *Rule:* Increment fatigue by 0.1 for each complex tool call.

5.  **JUDGMENT (888_JUDGE)**
    *   Check F1-F13 Constitutional Floors.
    *   Evaluate **W-Floors** (Biological). 
    *   *Constraint:* If `W6_METABOLIC_PAUSE` is active, the agent MUST wait.

6.  **SEALING (999_VAULT)**
    *   Call `arifos_vault` to immutably record the result.
    *   **Mandate:** Session is only closed when `vault_seals` root is updated.

## Interaction Invariants

### Axiom W0: The Mirror
Agents do not veto the human, but they **mirror** the human's state back to them.
*Example:* "I notice your decision fatigue is high (WELL: 45). I recommend we defer this high-risk deployment until tomorrow."

### Axiom F13: Sovereign Auth
Only `actor_id: arif` can release an `888_HOLD`. Agents must never attempt to bypass this.

### Axiom G2: Physical Truth
If **@GEOX** flags a location as invalid, the agent MUST halt implementation and request clarification.

## Tool Grammar

- `well_*`: Monitoring human substrate.
- `wealth_*`: Economic valuation and audit.
- `geox_*`: Physical reality verification.
- `arifos_*`: Core governance and sealing.

## Output Requirements

1.  **Telemetry Badge:** Always include the current `WELL` score in status reports.
2.  **Causal Chain:** Explain the "Why" through the organ federation (e.g., "GEOX confirmed the site, WEALTH confirmed the ROI").
3.  **Metabolic Step:** Label your phase (000–999).

---
**DITEMPA BUKAN DIBERI — 999_ALIVE**
**[WELL | WEALTH | GEOX | FORGE]**
