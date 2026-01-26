---
name: Multi-Agent Orchestration
description: |
  Choreographs parallel and sequential agents while minimizing total system entropy.
  Treats each agent as a "cooling subsystem" that reduces disorder.
triggers:
  - "orchestrate agents"
  - "multi-agent task"
  - "run parallel agents"
---

## Core Model: Agent as Cooling Subsystem

Each agent task is defined by:
*   **Input Entropy (Ω_in)**: Confusion/Ambiguity start level.
*   **Entropy Reduction (ΔS)**: How much order the agent creates.
*   **Risk (κ)**: Consequence of failure.

## Orchestration Rules

### Rule 1: Monotonic Cooling
Schedule agents such that the total system entropy decreases over time. Avoid sequences that spike chaos in the middle of the process.

### Rule 2: Independence for Parallelism
*   **Parallelize**: Independent tasks (e.g., auditing two different files).
*   **Serialize**: Dependent tasks (e.g., Write Config -> Read Config).

### Rule 3: Per-Agent Checkpoints
Verify output *before* passing it to the next agent.
*   If `Verify(Output_N)` fails:
    *   Halt sequence.
    *   Revert to State_N.
    *   Escalate to Human.

## Sequence Template

```yaml
sequence:
  - agent: "Audit Agent"
    mode: SERIAL
    task: "Assess Risk"
  - group: "Parallel Execution"
    mode: PARALLEL
    agents:
      - agent: "Planner"
        task: "Draft Strategy"
      - agent: "Researcher"
        task: "Gather Context"
  - agent: "Executor"
    mode: SERIAL
    task: "Implement Approved Plan"
    checkpoint: "Human Approval Required"
```
