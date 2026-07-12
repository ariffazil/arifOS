# APEX Claim-Class Calibration Programme

**Status:** ACTIVE research programme (not complete science)  
**Date:** 2026-07-12  
**Rule:** No single global confidence number. Calibrate **per claim class**.

---

## Confidence object (required)

```json
{
  "value": 0.0-1.0,
  "kind": "bayesian_posterior|frequentist_rate|model_output|expert_judgment|calibration_score|heuristic|unknown",
  "target": "string — what the number is about",
  "method": "string",
  "calibration_model": "id|null",
  "validation_window": "string|null",
  "sample_size": "int|null",
  "expires_at": "RFC3339|null"
}
```

Validator: `contracts/confidence_validator.py`

---

## Calibration families

| Claim class | Target of calibration | Method (when data exists) | Owner |
|-------------|----------------------|---------------------------|--------|
| Binary physical | P(Y=1 \| p̂) ≈ p̂ | Brier, reliability curve | GEOX |
| Continuous estimate | Interval coverage | Prediction-interval hit rate | GEOX/WEALTH |
| Geological scenario | Posterior predictive | Hold-out wells / plays | GEOX |
| Financial forecast | Error + tails | Residual dist, VaR backtest | WEALTH |
| Human readiness | Outcome link (ethical limits) | Strict: only consented ops outcomes | WELL |
| Agent execution success | Task success frequency | Lease-scoped empirical rate | A-FORGE |
| Constitutional judgment | Policy agreement | Expert/F13 review set | arifOS |
| Catastrophic risk | Conservative upper bound | Stress tests, not mean | MULTI |

**Illegal:** pooling LLM `model_output` with GEOX `bayesian_posterior` in one reliability curve.

---

## Minimum viable calibration (MVP this phase)

1. **Schema gate:** reject bare float confidence in new envelopes (`confidence_validator`).  
2. **Label inventory:** log `kind` counts per organ (start zero → grow).  
3. **Execution class only:** A-FORGE / recovery_v1 success rate under allowlist (empirical).  
4. **Hold for domain curves:** GEOX/WEALTH need labeled outcome sets (not inventable).

---

## Execution-class seed metric (live)

From WELL `loop/receipts/recovery_*.json`:

- success = `final_verdict == SEAL` and verify success  
- failure = HOLD after mutate attempt or verify fail  
- VOID unauth does **not** count as failure of authorised path  

Updated by: `contracts/run_calibration_inventory.py`

---

## Exit criteria for “calibrated enough” (narrow)

| Class | Ready when |
|-------|------------|
| Agent execution (allowlisted recovery) | ≥20 trials, success rate reported with CI |
| Constitutional block | Adversarial suite blocks unauth 100% on public MCP |
| Domain posteriors | Separate GEOX validation set exists (future) |

Until exit: mark confidence `kind=heuristic|unknown` honestly.
