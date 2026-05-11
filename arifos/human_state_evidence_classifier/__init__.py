"""Human-State Evidence Classifier — arifOS Constitutional Module

DITEMPA BUKAN DIBERI — Intelligence is forged, not given.

This module does NOT determine human state.
It classifies evidence about human-state expressions and prevents
false claims by requiring witness validation before inference.

Naming discipline:
- "Classifier" not "Detector" — we classify evidence, not detect truth
- "Evidence" not "Truth" — expression patterns are evidence, not fact
- "Human-state" not "Human" — we infer from expression, not from being
"""

from .labels import StateDomain, WitnessType, TruthStatus, Confidence
from .schemas import HumanStateEstimate, Witness
from .witness_fusion import estimate_human_state

__all__ = [
    "StateDomain",
    "WitnessType",
    "TruthStatus",
    "Confidence",
    "HumanStateEstimate",
    "Witness",
    "estimate_human_state",
]
