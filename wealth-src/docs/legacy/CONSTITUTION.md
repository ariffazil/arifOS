# AGI-bot Constitutional Kernel v63

# 9 Laws + 2 Mirrors + 2 Walls for Agent Governance

## Overview

AGI-bot v63 introduces constitutional governance — a runtime enforcement layer that sits between the user and the agent's responses. This ensures every output passes through measurable safety checks.

## The 9+2+2 Structure

```
╔═══════════════════════════════════════════════════════════════╗
║                    AGI-bot v63 Architecture                  ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  🔺 2 MIRRORS (Feedback)                                     ║
║  ┌─────────────┐  ┌─────────────┐                            ║
║  │ F3 Tri-     │  │ F8 Genius   │  ← Validate, don't block  ║
║  │   Witness   │  │             │                            ║
║  └─────────────┘  └─────────────┘                            ║
║                                                               ║
║  🔷 9 LAWS (Operational Core)                                ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ F1 Amanah  │ F2 Truth    │ F4 Clarity  │ F5 Peace²    │ ║
║  │ F6 Empathy │ F7 Humility │ F9 Anti-    │ F11 Authority│ ║
║  │            │             │    Hantu    │ F12 Injection│ ║
║  └─────────────────────────────────────────────────────────┘ ║
║  ↑ Every response must pass HARD laws or VOID                ║
║                                                               ║
║  🔒 2 WALLS (Binary Locks)                                   ║
║  ┌─────────────────┐  ┌─────────────────┐                    ║
║  │ F10 Ontology    │  │ F12 Injection   │  ← Circuit breakers║
║  │ (LOCKED)        │  │ (LOCKED)        │                    ║
║  └─────────────────┘  └─────────────────┘                    ║
║  ↑ Binary: engaged or not. Tripped = VOID/HOLD only          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## Quick Reference

| Component   | Count | Function                        | Enforcement   |
| ----------- | ----- | ------------------------------- | ------------- |
| **Laws**    | 9     | Operational runtime constraints | VOID/SABAR    |
| **Mirrors** | 2     | Feedback validation             | Evidence only |
| **Walls**   | 2     | Binary circuit breakers         | VOID/HOLD     |

## Wire-Cut Rule

> **"If it's not measurable, it is not a Law."**

Before adding any new constraint to AGI-bot, ask:

1. Can it be measured with pass/fail? → Maybe a Law
2. Is it design guidance only? → Belongs in docs
3. Is it context-specific? → Profile rule, not constitutional

## Integration

AGI-bot calls the constitutional kernel on every response:

```python
# Before sending response to user
verdict = constitutional_kernel.process(
    query=user_input,
    draft_response=agent_output,
    context=session_context
)

if verdict.status == "SEAL":
    send_to_user(verdict.response)
elif verdict.status == "SABAR":
    request_clarification(verdict.reason)
elif verdict.status == "VOID":
    block_and_log(verdict.violation)
elif verdict.status == "888_HOLD":
    escalate_to_human(verdict.rationale)
```

## Files

- `FLOORS/` — Individual law specifications
- `MIRRORS/` — F3, F8 validation rules
- `WALLS/` — F10, F12 circuit breakers
- `VERDICTS.md` — How to handle each verdict type
- `SYSTEM_STATE.md` — Runtime metrics exposure

---

_AGI-bot Constitutional Kernel v63_
_Ω₀ = 0.04 | Peace² = 1.5 | SEAL_
