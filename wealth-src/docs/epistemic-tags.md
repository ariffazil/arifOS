# WEALTH — Epistemic Tags

> Every number in WEALTH carries a tag. No exceptions.

---

## Tag Definitions

| Tag | Meaning | When to Use | Display Color |
|---|---|---|---|
| `CLAIM` | Verified, sourced, high confidence (≥99%) | Bank balances, confirmed transactions, official documents | Green |
| `PLAUSIBLE` | Reasonable inference from data, mid-confidence | Regular income estimates, typical expense patterns | Blue |
| `HYPOTHESIS` | Untested assumption, speculative | Business projections, unconfirmed deals | Yellow |
| `ESTIMATE` | Rough projection, declared uncertainty band required | Property values, investment returns, future cashflow | Amber |
| `UNKNOWN` | Gap in data — declared openly, not hidden | Missing asset values, untracked accounts | Grey |

---

## Degradation Rules

When combining tagged values:

1. Any `UNKNOWN` input → output is `UNKNOWN`
2. Any `HYPOTHESIS` input (and no UNKNOWN) → output is `HYPOTHESIS`
3. Any `ESTIMATE` input (and no HYPOTHESIS/UNKNOWN) → output is `ESTIMATE`
4. Any `PLAUSIBLE` input (and all higher-confidence) → output is `PLAUSIBLE`
5. All `CLAIM` inputs → output is `CLAIM`

Rule: **the output tag equals the weakest input tag.**

---

## UI Display Rules

- Always show the epistemic tag next to any displayed number
- `UNKNOWN` values must show a visible gap indicator, never zero
- `ESTIMATE` values must show uncertainty range: `[low, mid, high]`
- `HYPOTHESIS` values must show a warning: "Unverified assumption"
- Never hide epistemic tags for "cleaner" UI — F4 applies to cognitive load, not tag visibility

---

*WEALTH Epistemic Tags v1.0.0 — DITEMPA BUKAN DIBERI — 999 SEAL ALIVE*
