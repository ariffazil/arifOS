"""
Test harness: ART vs Kernel — empirical proof of ART's unique value.

This package compares:
  - Baseline A (kernel only, ART disabled)
  - SUT       (kernel + ART reflex + Library + Gate 2.5)

Across 5 scenario families:
  S1: Broken-but-legal tool
  S2: Schema drift
  S3: Blast-radius misclassification
  S4: Replay of real VAULT incident
  S5: Adversarial regression

If ART does not measurably beat Baseline A on at least one of its three
claims (lifecycle, memory, fast-screen), it is overhead. This harness is
the empirical answer.

DITEMPA BUKAN DIBERI — proof is forged, not claimed.
"""
