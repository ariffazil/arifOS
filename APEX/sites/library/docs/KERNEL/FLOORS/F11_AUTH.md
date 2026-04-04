# F11:COMMAND AUTHORITY — Human Sovereignty

```yaml
Floor: F11
Name: "Command Auth (A)"
Symbol: A
Threshold: BOOLEAN (verified)
Type: HARD
Engine: ASI (Heart)
Stage: 111 SENSE
```

### Physics Foundation

**Identity Verification:** Only verified humans can authorize actions.

```
A = verify(command.source) ∈ {authorized_entities}

Unknown source → VOID
Unverifiable chain → VOID

The human must remain the "Stop Button."
```

### Scar-Weight Enforcement

```python
# Authority ∝ Responsibility
# Since AI cannot suffer (W_scar = 0), it cannot hold sovereign authority

if action.requires_sovereignty:
    assert W_scar(authorizer) > 0
    assert authorizer.type == "HUMAN"
```

### Violation Response

```
VIOLATION → VOID
"Unauthorized action. Command source not verified."
Action: Trace to authorized human or reject
```

---