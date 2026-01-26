---
name: Thermodynamic Planning
description: |
  Plan design with entropy accounting. Every plan must minimize total disorder (Entropy)
  and specify the cost of reversibility (time, compute, data risk).
  Ensures that systems cool down (become more ordered) rather than heat up (become chaotic).
triggers:
  - "create a plan"
  - "thermal plan"
  - "entropy audit"
  - "what is the undo cost?"
---

## Planning Ritual

### Phase 1: Entropy Audit
Before defining steps, calculate:
*   **Initial State (S₀)**: Current level of disorder, ambiguity, or risk.
*   **Target State (S_f)**: Desired level of order, clarity, and safety.
*   **Delta S (ΔS)**: S_f - S₀. (Must be negative, indicating a reduction in entropy/chaos).

### Phase 2: Reversibility Cost Matrix
For each proposed step, estimate the **Cost to Undo**:

| Action Type | Reversibility | Cost (Hours/Res) | Risk |
| :--- | :--- | :--- | :--- |
| **Local Config** | Full | Low | None |
| **Code Change** | Full (Git Revert) | Low | Low |
| **Infrastructure** | Partial | High | Medium |
| **Data Deletion** | None | Infinite | Critical |

**Rule**: If Reversibility Cost is High, a Human Checkpoint is **REQUIRED**.

### Phase 3: Cooling Sequence
Order steps to minimize "Peak Entropy" (maximum disorder during the process).
*   **Bad**: Create chaos first, fix later.
*   **Good**: Stabilize first, build incrementally.

### Phase 4: Undo Protocol
Define the exact sequence to revert changes if the plan fails.

```json
{
  "undo_protocol": [
    "git reset --hard <pre_plan_commit>",
    "restore database from snapshot <id>",
    "remove created artifacts"
  ]
}
```

## Tools
*   `scripts/thermodynamic_planner.py`: Calculates entropy and cost.
*   `scripts/cooling_sequence.py`: Optimizes step order.
