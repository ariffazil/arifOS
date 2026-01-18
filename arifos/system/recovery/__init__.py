"""
arifos_core.recovery — Floor-Specific Recovery System.

Gap 5 Fix: Structured fallback logic for floor failures.
Graceful degradation > brittle failure.

Version: v45.0.4
"""

from .matrix import (
                     FLOOR_ALIASES,
                     FLOOR_RECOVERY_MATRIX,
                     RecoveryAction,
                     RecoveryAttempt,
                     RecoveryMatrix,
)

__all__ = [
    "RecoveryAction",
    "RecoveryAttempt",
    "RecoveryMatrix",
    "FLOOR_RECOVERY_MATRIX",
    "FLOOR_ALIASES",
]
