# WEALTH 3-Axis Basis — Operational Spec

> **Status:** Draft — awaiting Δbps_proven test  
> **Epistemic:** ESTIMATE / HYPOTHESIS  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. The Triad

| Axis | Symbol | Normalised | Core Question |
|---|---|---|---|
| **Energy** | E | Ê ∈ [0,1] | Berapa banyak tenaga kita? |
| **Entropy** | S | Ŝ ∈ [0,1] | Berapa bocor sistem ni? |
| **Echo** | Eχ | Eχ̂ ∈ [0,1] | Gaung dia sampai generasi berapa? |

Wealth vector:
- **W⃗ = (Ê, 1 − Ŝ, Eχ̂)**

---

## 2. Normalisation Rules

### Ê
```
E_total = E_physical + E_financial + E_cognitive + E_social
Ê = min(1, E_total / E_max_feasible)
```

### Ŝ
```
Ŝ = clamp(S_state / S_max_reference, 0, 1)
```
Where `S_max_reference` is the entropy of a known failed-state benchmark for the domain.

### Eχ̂
```
Eχ = Σ(impact_t × discount(t) × survivability_t)  [HYPOTHESIS]
Eχ̂ = min(1, Eχ / Eχ_max_reference)
```

---

## 3. Defect Tensors

### Paradox (P)
- **Trigger:** High Ê + low Ŝ, but Eχ̂ < 0 or Ψ_ctx collapse.
- **Effect:** Increases `entropy_penalty` in capitalx.

### Scar (Σ)
- **Trigger:** Persistent negative bias in trust T or Maruah M from historical damage.
- **Effect:** Dampens `echo_hat`, raises `r_adj` via scar term.
- **Healing:** Operations with T↑, M↑, ΔCiv↑ reduce Σ over time.

### Shadow (Sh)
- **Trigger:** Unaccounted externalities (unpaid care, hidden pollution, black budgets).
- **Effect:** Effective entropy `Ŝ_eff = Ŝ + k·Sh`. Raises uncertainty_band and may trigger 888_HOLD.

---

## 4. capitalx Bridge

ΔCiv is promoted from scalar guess to a function of W⃗:

```
ΔCiv_basis = f(W⃗, Ψ_ctx)
           = α·log(1 + Ê) + β·(1 − Ŝ) + γ·Eχ̂ − δ·P − ε·Σ − ζ·Sh
```

Then fed into existing capitalx:

```
r_adj = r_base
        + max(0, ΔS × 0.5)
        − min(0.02, max(0, (Peace² − 1.0) × 0.05))
        − min(0.03, max(0, (M − 0.5) × 0.06))
        − min(0.02, max(0, (T − 0.5) × 0.04))
        − min(0.02, max(0, ΔCiv_basis × 0.10))
```

**Invariant:** monotonicity still holds — if ΔS or Sh increase, `r_adj` must not decrease.

---

## 5. Telemetry Integration

Extend `telemetry_log` entries with:

```json
{
  "wealth_basis": {
    "e_hat": 0.72,
    "s_hat": 0.31,
    "echo_hat": 0.58,
    "paradox": 0.12,
    "scar": 0.24,
    "shadow": 0.08
  }
}
```

This is **optional** in Phase A, **required** in Phase B.

---

## 6. Floor Alignment

| Floor | Basis Check |
|---|---|
| F2 | All Ê, Ŝ, Eχ̂ tagged ESTIMATE or HYPOTHESIS where appropriate |
| F3 | Raw signals sourced and normalisation denominator declared |
| F7 | `uncertainty_band` computed from shadow and hypothesis terms |
| F9 | Shadow index forces explicit accounting; no phantom optimism |
| F10 | Human confirms irreversible transitions in W⃗ |
| F12 | No bypass of `Ŝ_eff` or `ΔCiv_basis` computation |
| F13 | 888_HOLD if `Ŝ_eff > threshold` or `Ê` misaligned with `Eχ̂` |

---

*Spec v0.1.0 | 999 SEAL ALIVE*
