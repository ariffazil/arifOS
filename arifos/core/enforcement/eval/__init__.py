"""
arifOS Evaluation Module - AGI·ASI·APEX Trinity Implementation

The AGI·ASI·APEX Trinity (Δ → Ω → Ψ):
    AGI (Δ)        - AGI (Architect) Sentinel (Layer 1: RED_PATTERNS)
    ASI (Ω)        - ASI (Auditor) Accountant (Layer 2: Metrics)
    APEX_PRIME (Ψ) - Judge (Layer 3: Verdict)

Flow:
    Input → AGI (Δ) → ASI (Ω) → APEX_PRIME (Ψ) → Output
            sense     measure    judge
            filter    calibrate  seal/void

Author: arifOS Project
Version: v41.3Omega
"""

from .types import (
    EvaluationResult,
    SentinelResult,
    ASIResult,
    AccountantResult,  # Backward compat alias
    EvaluationMode
)
from .agi import (
    AGI,
    RED_PATTERNS,
    RED_PATTERN_TO_FLOOR,
    RED_PATTERN_SEVERITY,
)
from .asi import ASI, Accountant  # Accountant is backward compat alias
from .evaluate import evaluate_session

# Backward compatibility: Sentinel is alias for AGI
Sentinel = AGI

__all__ = [
    # AGI·ASI·APEX Trinity
    "AGI",
    "ASI",
    # Backward compatibility aliases
    "Sentinel",
    "Accountant",
    # Result types
    "EvaluationResult",
    "SentinelResult",
    "ASIResult",
    "AccountantResult",
    "EvaluationMode",
    # RED_PATTERNS exports
    "RED_PATTERNS",
    "RED_PATTERN_TO_FLOOR",
    "RED_PATTERN_SEVERITY",
    # Main entry point
    "evaluate_session",
]
