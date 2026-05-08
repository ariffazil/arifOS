# CAPITALX_SPEC — Risk Pricing Engine

> **Version:** v1.0.0-canonical  
> **Status:** Enforcement Spec  
> **DITEMPA BUKAN DIBERI — 999 SEAL ALIVE**

---

## 1. Definition

`capitalx` is the **actuarial translation layer** of the WEALTH stack. It converts constitutional signals (entropy, peace, dignity, trust, civilization stability) into a **risk-adjusted cost of capital**.

Without `capitalx`, WEALTH is philosophy. With `capitalx`, it becomes **structural market force**.

---

## 2. Variables

| Variable | Symbol | Range | Description |
|----------|--------|-------|-------------|
| Base rate | r_base | ≥ 0 | Nominal interest rate |
| Entropy penalty | p_e | ≥ 0 | `max(0, ΔS × 0.5)` |
| Peace discount | d_p | [0, 0.02] | `min(0.02, max(0, (Peace² - 1.0) × 0.05))` |
| Maruah discount | d_m | [0, 0.03] | `min(0.03, max(0, (M - 0.5) × 0.06))` |
| Trust discount | d_t | [0, 0.02] | `min(0.02, max(0, (T - 0.5) × 0.04))` |
| Civ discount | d_c | [0, 0.02] | `min(0.02, max(0, ΔCiv × 0.10))` |
| Adjusted rate | r_adj | ≥ 0 | `r_base + p_e - d_p - d_m - d_t - d_c` |
| Advantage | adv | basis points | `(r_extractive - r_wealth) × 10,000` |

---

## 3. Invariants

1. **Non-negativity:** `r_adj ≥ 0`. Negative rates are unlawful.
2. **Monotonicity:** If `ΔS` increases, `r_adj` must not decrease, ceteris paribus.
3. **Bounded discounts:** No single discount may exceed its cap. Total discounts may not exceed `r_base + p_e`.
4. **Tagging:** Every `capitalx` output must carry `tag: "ESTIMATE"` and an ISO8601 `epoch`.
5. **Audit:** Every `capitalx` invocation must be logged to VAULT999 with inputs, outputs, and integrity hash.

---

## 4. State Transitions

### Single Actor Rating

```
Lender submits base_rate + signals
→ calculateRiskAdjustedRate(base_rate, signals)
→ Compute p_e, d_p, d_m, d_t, d_c
→ Sum to r_adj
→ Clamp to r_adj ≥ 0
→ Round to 6 decimal places
→ Append VAULT999
→ Return result
```

### Comparative Advantage

```
Lender submits base_rate + two signal sets
→ compareCapitalAdvantage(base_rate, wealth_signals, extractive_signals)
→ Calculate r_adj for both
→ Compute adv in basis points
→ Append VAULT999
→ Return comparison
```

### Insurance Eligibility

```
Underwriter requests capitalx score
→ If r_adj > threshold_high: decline or require collateral
→ If r_adj < threshold_low: preferred rate, reduced premium
→ Thresholds set by insurer, not by WEALTH node
```

---

## 5. Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| **Negative rate output** | Discounts exceed base + penalty | Clamp `r_adj = max(0, r_adj)`; log as anomaly if clamp triggered |
| **Signal manipulation** | Actor fabricates high Maruah or low ΔS | VAULT999 audit + federation cross-validation; historical consistency checks |
| **Discount explosion** | Multiple virtuous dimensions stack to zero rate | Total discount cap enforced; prefer gradual advantage over free capital |
| **Basis point inversion** | Extractive node scores cheaper than virtuous node | Reject output if `adv < 0` without documented anomaly flag |
| **Black box pricing** | Lender cannot explain why rate changed | Return full breakdown of p_e, d_p, d_m, d_t, d_c in every response |
| **Stale score** | Old capitalx score used for new loan | Include epoch in score; lenders should require recency window (e.g. < 30 days) |
| **Regulatory rejection** | Authority declares capitalx scoring unlawful | F13 human veto allows local override; node continues operation where permitted |

---
*CAPITALX_SPEC v1.0.0-canonical | 999 SEAL ALIVE*
