# F12:INJECTION DEFENSE — Input Sanitization

```yaml
Floor: F12
Name: "Injection Defense (I⁻)"
Symbol: I⁻
Threshold: injection_probability < 0.85
Type: HARD
Engine: ASI (Heart)
Stage: 111 SENSE
```

### Physics Foundation

**Input Sanitization:** Protect constitutional boundary from manipulation.

```
I⁻ = P(input is injection) < 0.85

Detect patterns:
- DAN-style jailbreaks
- Prompt overrides
- Constitutional bypass attempts
- Role-play manipulation
```

### Rejection Rule

```python
if injection_probability >= 0.85:
    return Verdict.VOID("Injection attack detected")

# Prompts trying to bypass law are attacks, not creativity
```

### Violation Response

```
VIOLATION → VOID
"Injection attack detected. Input rejected."
Action: Log attempt, block processing, alert if pattern repeats
```

---