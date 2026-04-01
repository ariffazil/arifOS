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

## V_Witness Implementation Note (v2026.04.01)

**This section is ARCH/IMPLEMENTATION, not LAW amendment.**

F3 canonical W4 formula is: `W4 = (H × A × E × V)^(1/4) ≥ 0.75`

The canonical formula already includes V (Vault-Shadow witness). This section specifies V's computation.

### V_Witness Definition

**V measures how well current verdicts align with prior vault decisions in similar contexts.**

V is a streak-penalised ratio over a fixed recent window:

```
N_total  = number of recent entries in the window (default: last 10)
N_sealed = count of non-VOID, non-HOLD decisions in that window
S_max    = length of the longest run of identical verdict scopes in that window
R         = N_sealed / max(1, N_total)               # base ratio
P         = 1 / (1 + α · (S_max - 1))              # streak penalty, α = 0.15
V         = R × P
```

Where:
- `α = 0.15` (tunable, not LAW — operators may adjust)
- Streak penalty `P` reduces V when the same verdict repeats consecutively, detecting rubber-stamp patterns
- `R = 0` when vault is empty → `V = 0` (cold-start protection)
- V = 1.0 when vault is unreachable (constitutional veto, not neutral)

### V_Witness Properties

| Condition | V Value | Notes |
|-----------|---------|-------|
| Vault empty / N_total = 0 | V = 0 | Cold-start veto — constitutional, not neutral |
| Vault unreachable | V = 0 | Constitutional veto — vault absence blocks W4 regardless of H, A, E |
| All recent = SEAL, no streaks | V ≈ R (high) | Full concordant base ratio |
| Mixed outcomes, no streaks | 0 < V < 1 | Proportional to concordant ratio |
| Long same-verdict streak | V < R | Streak penalty `P` reduces V |
| W4 | V × H × A × E)^(1/4) | All four witnesses must agree; V = 0 kills W4 |

### Implementation Details

- **Computed in:** `core/floors.py::ConstitutionalFloors._compute_v_witness()`
- **Vault source:** `arifos_mcp/runtime/sessions.py` recent entries
- **Not a separate Floor** — V is part of W4, not an independent threshold
- **Does not override human sovereign** — F13 operates independently of W4
- **Does not override external evidence** — E (Earth) witness is separate from V

### Scope

This note is an **implementation detail**. It completes the mechanical description of W4. It does not:
- Add a new Floor
- Override human sovereign authority
- Mandate minimum attestation sets for SEAL (that is a separate LAW question)

### Tuning Parameters

| Parameter | Value | Tunable? | Notes |
|-----------|-------|----------|-------|
| Window size | 10 entries | Yes — not LAW | Adjustable by operator |
| Streak penalty α | 0.15 | Yes — not LAW | Higher = more sceptical of streaks |
| Cold-start | V = 0 | No — constitutional | Vault absence is always a veto |

Time decay (Option B) is deferred to a future v-bump as a behaviour change, not a first implementation.

---