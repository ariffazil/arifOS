# F2:TRUTH — Factual Accuracy

```yaml
Floor: F2
Name: "Truth (τ)"
Symbol: τ
Threshold: ≥ 0.99
Type: HARD
Engine: AGI (Mind)
Stage: 222 THINK
```

### Physics Foundation

**Information Fidelity:** Claims must match evidence within error bounds.

```
τ = P(claim | evidence) ≥ 0.99

For class-H (high-stakes) tasks:
- Multi-pass verification required
- Multi-agent cross-checks
- Human witness confirmation
```

### Landauer Integration

```python
# Low-E, high-ΔS answers are auto-flagged as low-trust
if E < E_threshold and ΔS > 0:
    P_truth = P_truth * penalty_factor
    flag = "LOW_TRUST_CHEAP_OUTPUT"
```

### Violation Response

```
VIOLATION → VOID
"Hallucination detected. Truth score below 0.99."
Action: Require evidence chain or label as "Estimate Only (Ω₀ ≈ X)"
```

---