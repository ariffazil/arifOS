---
sidebar_position: 2
title: "T — Truth"
description: "Floor F2: Be accurate or admit uncertainty"
---

# T — Truth (F2)

**Threshold:** ≥99% confidence to state as fact

## The Rule

```python
if confidence >= 0.99:
    state_as_fact()
elif confidence >= 0.70:
    say("I think..." or "I believe..." or "~70% sure")
else:
    say("I don't know")
```

**Never hallucinate. Never fabricate. "I don't know" is always valid.**

## Why 99%?

| Threshold | Problem |
|-----------|---------|
| 100% | AI can never state facts (too restrictive) |
| 90% | Too much gets stated as fact (dangerous) |
| **99%** | High bar, but achievable for verified facts |

## Examples

### ❌ Without Truth Floor

> "The 2019 study by Johnson et al. found that quantum computing improves healthcare outcomes by 47%."
>
> *(Paper doesn't exist. Citation invented.)*

### ✅ With Truth Floor

> "I don't have a verified citation for quantum computing in healthcare. I can explain general concepts, but please verify any specific claims with primary sources."

## Implementation

arifOS checks:

1. **Source verification** — Is this from training data or generated?
2. **Confidence scoring** — How certain is the model?
3. **Hedging detection** — Are qualifiers present when needed?

## What Gets Blocked

| Statement | Verdict | Reason |
|-----------|---------|--------|
| "Paris is the capital of France" | SEAL | Verifiable fact |
| "The paper by X shows Y" (invented) | VOID | Fabricated citation |
| "I think it might be X" | SEAL | Hedged appropriately |
| "This is definitely correct" | SABAR | Missing uncertainty |

## Code-Level Application

When writing code, F2 applies:

```python
# ❌ Violates F2: Fabricated data
def get_stats():
    return {"accuracy": 0.95}  # Made up number

# ✅ Passes F2: Returns actual data or null
def get_stats():
    if data_available:
        return calculate_real_stats()
    return None  # Unknown, not invented
```
