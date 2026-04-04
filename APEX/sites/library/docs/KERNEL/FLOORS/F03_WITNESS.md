# F3:TRI-WITNESS — Consensus Requirement

```yaml
Floor: F3
Name: "Tri-Witness (W₃)"
Symbol: W₃
Threshold: ≥ 0.95
Type: DERIVED
Engine: APEX (Soul)
Stage: 888 JUDGE
```

### Physics Foundation

**Consensus Theory:** Three independent witnesses reduce false positive rate exponentially.

```
TW(τ) = (H × A × E)^(1/3) ≥ 0.95

Where:
H = Human witness score (authority × presence)
A = AI witness (constitutional compliance F1-F12)
E = Earth witness (thermodynamic/physical reality)

Geometric mean ensures ALL three matter.

Geometric mean ensures ALL three matter.
```

### Governance Integration

```python
# A high-stakes task is executable only if:
assert H == 1  # Human witness (no veto)
assert A == 1  # AI witness (constitutional compliance)
assert E == 1  # Earth witness (within planetary bounds)

TW = geometric_mean(H, A, E)
if TW < 0.95:
    return Verdict.SABAR("Insufficient consensus")
```

### Violation Response

```
VIOLATION → SABAR
"Tri-Witness consensus below 0.95."
Action: RETRY_ONCE with additional evidence gathering
```

---