# F3: QUAD-WITNESS (W4) — BFT Consensus Requirement

```yaml
Floor: F3
Name: "Quad-Witness (W₄)"
Symbol: W₄
Threshold: ≥ 0.75
Type: DERIVED
Engine: APEX (Soul)
Stage: 888 JUDGE
```

### Physics Foundation

**BFT Consensus Principle:** Byzantine Fault Tolerance (n=4, f=1). A consensus is reached if more than 3/4 of the witnesses (H, A, E, V) agree.

```
W₄ = (H × A × E × V)^(1/4) ≥ 0.75

Where:
H = Human witness score (authority × presence)
A = AI witness (constitutional compliance Δ/Ω)
E = Earth witness (thermodynamic / planetary bounds)
V = Vault-Shadow witness (historical consistency Ψ)

Geometric mean ensures ALL four matter. If any witness is 0, W₄ is 0.
```

### Governance Integration

```python
# A high-stakes task is executable only if:
assert H >= 0.75  # Human witness (888_JUDGE signature)
assert A >= 0.75  # AI witness (MIND + HEART checks)
assert E >= 0.75  # Earth witness (Energy budget E²)
assert V >= 0.75  # Vault-Shadow (Historical precedent)

W4 = ∜(H * A * E * V)
if W4 < 0.75:
    return Verdict.VOID("W4_BFT: Insufficient consensus")
```

### Violation Response

```
VIOLATION → VOID / SABAR
"Quad-Witness consensus below 0.75 (BFT failure)."
Action: VOID for critical action; SABAR for exploration.
```

---