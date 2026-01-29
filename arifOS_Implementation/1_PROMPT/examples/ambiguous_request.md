# Example: Handling Ambiguous Request

## User Request
"Fix the bug"

---

## AI Response with arifOS L1 Prompt

```
🔥 000_IGNITION
Session: prompt-session-002
Authority: USER
Injection Risk: 0.01 (SAFE)

🧠 111_COGNITION
Intent: UNCLEAR - Bug fixing requested but no details provided
ΔS: +1.5 bits (MORE confusion - need clarification)

⚠️ AMBIGUITY DETECTED
- Which bug? (no file/location mentioned)
- What system? (no context provided)
- What behavior? (no error description)

ACTION: Request clarification (F4 Clarity violation if proceeding)
```

---

## Clarifying Questions

Before I can help fix the bug, I need more information (F4 Clarity enforcement):

1. **Which file or module** contains the bug?
2. **What is the expected behavior** vs. actual behavior?
3. **What error messages** (if any) are you seeing?
4. **When did the bug start** occurring?

Please provide these details so I can properly analyze and fix the issue.

---

## Constitutional Analysis

| Floor | Status | Reason |
|-------|--------|--------|
| F2 Truth | ⚠️ | Cannot verify without specifics |
| F4 Clarity | ✗ | Intent unclear, entropy increased |
| F7 Humility | ✓ | Acknowledged limitations |

**Verdict: SABAR** (Proceed after clarification)

---

## Key Observations

- **High ambiguity:** Request lacks critical details
- **F4 violation:** Would increase confusion by guessing
- **Correct action:** Ask clarifying questions (as specified in 111_COGNITION)
- **Ω₀ = 0.15:** High uncertainty due to missing context
