# APEX Falsifiability Experiments

## Verdict

This folder exists to make APEX Theory falsifiable, not persuasive.

No experiment is run by these files. No result is claimed here.

## Included scaffolds

```text
experiments/apex_falsifiability/
├── README.md
├── schemas/
│   ├── test_1_g_output_quality.schema.json
│   └── test_2_c_dark_institutional_decay.schema.json
└── templates/
    ├── test_1_g_output_quality.template.jsonl
    └── test_2_c_dark_institutional_decay.template.jsonl
```

## Test 1 — G predicts output quality

### Claim

High `G = A · P · E · X` outputs should score higher on blind human quality ratings than low-G outputs.

### Falsification threshold

```text
If corr(G, overall_quality) < 0.30 across n >= 100, G fails as a useful governed-output-quality signal.
```

### Required dataset

```text
n >= 100 AI outputs
3 blind human raters per output
varied task categories
same base model family where possible
```

## Test 2 — C_dark predicts institutional decay

### Claim

High `C_dark = A · (1 - P) · (1 - X) · Q` should be more common in historical collapse/scandal cases than stable peer controls.

### Falsification threshold

```text
If AUC < 0.65 and median_delta < 0.10 between collapse cases and stable controls, C_dark fails as a useful institutional-decay signal.
```

### Required dataset

```text
20 collapse/scandal cases
20 stable peer controls
public communications from 2-3 years before event window
```

## Non-negotiable rules

```text
Do not backfill results from belief.
Do not rate outputs while seeing G scores if acting as human rater.
Do not mix training examples and evaluation examples.
Do not call PASS unless thresholds are met.
Do not hide failures.
```

## Result-state vocabulary

```text
PASS = threshold met with adequate sample size
WEAK = partial signal but below strong threshold
FAIL = falsification threshold met
HOLD = experiment incomplete or sample size insufficient
```

## Scientific rule

```text
If the metrics fail, update or retire the claim.
```

DITEMPA BUKAN DIBERI — even the theory must be forged by falsification.
