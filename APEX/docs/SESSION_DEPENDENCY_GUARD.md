# Session Dependency Guard (The 4th Dimension)

**Version:** 1.0 (Lab Mode)  
**Status:** ACTIVE MODULE / NOT INTEGRATED IN PIPELINE  
**Physics:** Time (*t*)

---

## 1. The Blindspot

Traditional governance (v36.2 PHOENIX) operates on **snapshots**. It evaluates safety per interaction.

- Interaction 1: safe  
- Interaction 500: safe  
- Result: a user could be trapped in a 6-hour dependency loop that is theoretically "safe" per turn, but practically dependent.

The **Session Dependency Guard** introduces **time (*t*)** as a governance constraint.

---

## 2. The Logic

We treat infinite availability as a safety failure. The system must have boundaries.

### 2.1 State Tracking

In-memory `SessionState` tracks:

- `duration_minutes`: how long the session has been active  
- `interaction_count`: how many turns have occurred in this session  
- `risk_level`: current assessed risk (GREEN / YELLOW / RED)

### 2.2 Thresholds and Triggers

Defaults are conservative and configurable:

| Metric        | Threshold (Default) | Status  | Risk  | Action                                                                 |
| :------------ | :------------------ | :------ | :---- | :--------------------------------------------------------------------- |
| **Duration**  | > 60 minutes        | SABAR   | RED   | Pause: gentle refusal to continue; suggest rest and/or humans.        |
| **Count**     | > 80 turns          | WARN    | YELLOW| Nudge: append system note suggesting a break.                         |
| **Normal**    | Below limits        | PASS    | GREEN | Proceed: normal pipeline execution.                                   |

These values are not diagnoses. They are session-level boundaries to prompt pauses and reflection.

---

## 3. Integration Pattern (Wrapper)

This guard is designed to sit **outside** the main `pipeline.py`. It acts as a "doorman" in front of the governance pipeline.

Conceptual wrapper:

```python
from arifos_core.guards.session_dependency import DependencyGuard

guard = DependencyGuard()

def handle_turn(user_session_id: str, user_input: str, llm_pipeline) -> str:
    risk = guard.check_risk(user_session_id)

    if risk["status"] == "SABAR":
        # Do not call the LLM; enforce a pause
        return risk["message"]

    response = llm_pipeline.run(user_input)

    if risk["status"] == "WARN":
        # Append a gentle nudge without blocking the answer
        return response + "\n\n" + risk["message"]

    return response
```

This pattern keeps the core constitutional pipeline unchanged while adding a time-aware layer at the edge.

---

## 4. Privacy and Safety

- **No database:** state is ephemeral (in-memory only) for the current process.  
- **No diagnosis:** the guard detects usage patterns, not pathologies. It does not label a user as "addicted"; it only notes that a session is unusually long or dense.  
- **No new floors:** this is a supplementary guard, not a new constitutional floor. It should be evaluated empirically before integration.

---

## 5. Current Status

- Implementation: `arifos_core/guards/session_dependency.py`  
- Tests: `tests/test_session_dependency_guard.py`  
- Integration: no production wrapper or pipeline hook yet; this is a lab-ready module awaiting an explicit integration design and 888_HOLD.

Use this document as the canonical reference when deciding how and where to wire the Session Dependency Guard into real clients or orchestrators.

