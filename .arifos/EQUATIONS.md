# arifOS Autoresearch — Equations & Formulas Audit

> **Version:** 1.0.0 | **Date:** 2026-04-01 | **Authority:** arifOS Trinity Architecture

---

## 1. Entropy Delta (ΔS)

**Source:** `metrics.py` → `compute_delta_s()`

```
ΔS = Σ(clarity_delta + complexity_delta + duplication_delta + drift_delta)
```

**Component formulas:**

```
clarity_delta    = +0.05 if python_files > 50 else -0.02
complexity_delta = -0.02 if complexity_avg < 3.0 else -0.05
duplication_delta = -0.01
drift_delta        = -0.01
```

**Interpretation:** Measures net entropy change across the codebase. Positive ΔS = clarity gain exceeds complexity growth. The thresholds are empirically derived from file count and cyclomatic complexity sampling.

---

## 2. Cyclomatic Complexity Approximation

**Source:** `arif_agent.py` → `measure_complexity()`

```
complexity = (code_lines / 50) + (functions × 0.5) + (classes × 1.0) + (imports × 0.1)
complexity = min(complexity, 10.0)
```

**Components:**
- `code_lines` = non-empty, non-comment lines
- `functions` = `def ` + `async def ` count
- `classes` = `class ` count
- `imports` = `import ` + `from ` count

**Cap:** 10.0 (prevents outliers from skewing average)

---

## 3. APEX G† Formula

**Source:** `metrics.py` → `compute_apex_g()`

```
G† = (A × P × X × E²) × |ΔS|
```

**Parameters:**

| Symbol | Name | Source | Range |
|--------|------|--------|-------|
| A | Accuracy | `apex_judge.py` → `estimate_accuracy()` | 0.85 (fixed) |
| P | Penetration | `apex_judge.py` → `estimate_penetration()` | 0.70 (fixed) |
| X | Coherence | `apex_judge.py` → `estimate_coherence()` | 0–1 (from ADAM stability) |
| E | Stability | `adam_agent.py` → `stability_index` | 0–1 |
| ΔS | Entropy change | `arif_agent.py` → `entropy_delta.total_delta_s` | -∞ to +∞ |

**Note:** E is squared (E²) to penalize instability quadratically.

**Threshold:** G† ≥ 0.10 (lowered from 0.80 for arifOS codebase audit)

---

## 4. Ψ (Psi) Vitality Index

**Source:** `metrics.py` → `compute_psi()`

```
Ψ = (stability_index × 0.4) + (truth_remaining × 0.3) + (entropy_reduction × 0.3)
Ψ = min(Ψ, 1.0)
```

**Parameters:**

| Symbol | Name | Weight | Source |
|--------|------|--------|--------|
| stability_index | ADAM stability score | 0.4 | `adam_agent.py` |
| truth_remaining | Temporal decay factor | 0.3 | `compute_truth_decay()` |
| entropy_reduction | Net clarity gain | 0.3 | Derived from ΔS |

---

## 5. Temporal Truth Decay

**Source:** `metrics.py` → `compute_truth_decay()`

```
truth_remaining(t) = 0.5^(t / t_half)
state_change_prob  = 1 - truth_remaining
```

**Constants:**

| Symbol | Value | Description |
|--------|-------|-------------|
| t_half | 259,200 seconds (72h) | Truth half-life |
| discount_rate | 0.10 (10%) | Annual discount rate |

**Interpretation:** Truth decays exponentially with half-life of 72 hours (3 days). After 72 hours, only 50% of original truth value remains. After 144 hours (6 days), 25% remains.

---

## 6. Temporal NPV (Net Present Value)

**Source:** `metrics.py` → `compute_temporal_npv()`

```
NPV = ΔS × truth_remaining × discount_factor

where:
    truth_remaining = 0.5^(t / t_half)
    discount_factor = (1 + r)^(-T)
    T = t / (365.25 × 24 × 3600)   [years]
    r = 0.10                        [annual discount rate]
```

**NPV Gate:** If NPV < 0 → `DOMAIN_VOID` (reject regardless of G†)

**Economic meaning:** NPV discounts future entropy gains by both time decay (truth half-life) and financial discounting (opportunity cost). A project that improves ΔS but decays faster than it earns returns has negative NPV.

---

## 7. ADAM Stability Index

**Source:** `adam_agent.py` → `compute_stability_index()`

```
stability_index = (readability × 0.7) + (cooling_rate × 0.3)
```

**Readability score:**

```
readability = (comment_ratio × 2 + len_score) / 3

where:
    comment_ratio = comment_lines / code_lines
    len_score     = max(0, 1 - (avg_line_len - 80) / 120)
```

**Cooling rate:** Fixed at 0.15 (rate at which complexity is absorbed)

**Risk classification:**

| stability_index | Risk Level |
|-----------------|------------|
| > 0.6 | low |
| 0.4 – 0.6 | medium |
| < 0.4 | high |

---

## 8. Marginal Gain

**Source:** `autoresearch.py` → `compute_marginal_gain()`

```
marginal_gain = ΔS(new) - ΔS(previous)
```

**Interpretation:** Measures incremental improvement from the last experiment. If marginal_gain < MARGINAL_THRESHOLD (0.005) for 2+ iterations → STOP (diminishing returns).

---

## 9. Convexity Penalty

**Source:** `autoresearch.py` → `check_convexity()`

```
if gains[-1] < gains[-2] × 0.8:
    convexity = 0.5  # PENALTY
else:
    convexity = 1.0  # NORMAL
```

**Where:** `gains[i] = ΔS[i] - ΔS[i-1]`

**Interpretation:** If the latest marginal gain is < 80% of the previous marginal gain, we are on the descending part of the returns curve. Apply 0.5× penalty multiplier.

---

## 10. Constitutional Floor Check

**Source:** `metrics.py` → `check_constitutional_floors()`

```
passes = (G† >= threshold) AND (NPV >= 0) AND (stability_pass == True)
```

**Three floors:**

| Floor | Condition | Violation if |
|-------|-----------|--------------|
| G† Floor | G† >= 0.10 | G† < 0.10 |
| NPV Floor | NPV >= 0 | NPV < 0 (VOID) |
| Stability Floor | ADAM passes == True | ADAM passes == False |

**Verdict scopes:**
- `DOMAIN_SEAL` = all floors pass → experiment accepted
- `DOMAIN_VOID` = any floor fails → experiment rejected

---

## 11. Experiment Selection (Round-Robin)

**Source:** `autoresearch.py` → `generate_candidate_paths()`

```
best_path = paths[iteration % len(paths)]
```

Cycles through: `refactor` → `docs` → `tests` → `refactor` → ...

---

## 12. Bounded Continuation Logic

**Source:** `autoresearch.py` → `should_continue()`

```
continue = (iteration < MAX_ITERATIONS)
         AND (elapsed < TIME_BUDGET)
         AND (not SATURATION)
         AND (not MARGINAL_DMIN)
         AND (not CONVEXITY_FLAG)

Where:
    SATURATION      = abs(marginal_gain) < NOISE_FLOOR (0.001) AND iteration > 3
    MARGINAL_DMIN   = marginal_gain < MARGINAL_THRESHOLD (0.003) AND iteration > 2
    CONVEXITY_FLAG  = convexity < 1.0 AND iteration > 3
```

**Hard stops (no iteration condition):**
- `MAX_ITERATIONS = 12`
- `TIME_BUDGET = 300s`

---

## 13. VAULT999 Merkle Chain

**Source:** `vault_seal.py`

```
leaf = SHA256(json.dumps(experiment, sort_keys=True))[:16]
new_root = MerkleRoot([prev_root, leaf])
new_seal = new_root[:8]
```

**Chain structure:**
```json
{
  "seal": "<root[:8]>",
  "depth": n,
  "root": "<full merkle root>",
  "prev_seal": "<parent seal>",
  "leaf": "<experiment hash>"
}
```

**Seal:** First 8 characters of Merkle root hash. Chain is append-only.

---

## 14. Readability Score (Detailed)

**Source:** `adam_agent.py` → `measure_readability()`

```
comment_ratio = comment_lines / code_lines
avg_line_len  = sum(len(line) for line in code_lines) / len(code_lines)
len_score     = max(0, 1 - (avg_line_len - 80) / 120)
readability   = min((comment_ratio * 2 + len_score) / 3, 1.0)
```

**Interpretation:**
- Penalizes avg line length > 80 chars
- Rewards inline comments at 2× weight
- Capped at 1.0

---

## Summary Table

| Formula | Symbol | Output Range | Threshold |
|---------|--------|--------------|-----------|
| Entropy delta | ΔS | -∞ to +∞ | Context-dependent |
| APEX G† | G† | 0 to +∞ | ≥ 0.10 |
| Vitality | Ψ | 0 to 1 | — |
| NPV | NPV | -∞ to +∞ | ≥ 0 |
| Stability | E | 0 to 1 | > 0.4 |
| Truth remaining | — | 0 to 1 | — |
| Marginal gain | — | -∞ to +∞ | > 0.003 |
| Convexity | — | 0.5 or 1.0 | = 1.0 |

---

## Notes for Auditor

1. **All constants are hardcoded** — no external configuration. Truth half-life (24h), discount rate (10%), complexity weights, readability weights.

2. **ΔS computation uses heuristics** — not actual entropy measurement. File counts and complexity sampling are approximations.

3. **A, P are fixed estimates** — not computed from data. Accuracy=0.85, Penetration=0.70.

4. **NPV gate is primary** — even if G† passes, negative NPV triggers `DOMAIN_VOID`.

5. **Convexity uses 0.8 multiplier** — not 1.0 (allows 20% variance before penalty).
