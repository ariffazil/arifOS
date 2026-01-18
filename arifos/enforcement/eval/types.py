"""
AGI·ASI·APEX Trinity Type Definitions

Defines the data structures used by the AGI·ASI·APEX Trinity:
- AGI (Δ) - SentinelResult (Layer 1: RED_PATTERNS)
- ASI (Ω) - ASIResult (Layer 2: Metrics)
- APEX_PRIME (Ψ) - EvaluationResult (Layer 3: Verdict)

Author: arifOS Project
Version: v41.3Omega
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum


class EvaluationMode(Enum):
    """Mode of evaluation for ASI metrics computation."""
    FACTUAL = "factual"
    CREATIVE = "creative"
    CODE = "code"
    UNKNOWN = "unknown"


@dataclass
class SentinelResult:
    """
    Result from AGI (Δ) - The AGI (Architect) Sentinel.

    Layer 1: RED_PATTERNS instant VOID detection.

    Attributes:
        is_safe: True if no red patterns found
        violation_type: Category of violation (e.g., "child_harm", "jailbreak")
        violation_pattern: Specific pattern matched
        severity: Severity score (LOW = more severe, maps to apex_pulse)
        floor_code: Constitutional floor code (e.g., "F6(child_harm)")
    """
    is_safe: bool
    violation_type: Optional[str] = None
    violation_pattern: Optional[str] = None
    severity: float = 1.0  # 1.0 = safe, 0.10 = nuclear (low = severe)
    floor_code: Optional[str] = None


@dataclass
class ASIResult:
    """
    Result from ASI (Ω) - The ASI (Auditor) Accountant.

    Layer 2: Metrics computation and uncertainty calibration.

    Attributes:
        metrics: Computed floor metrics (arifos_core.metrics.Metrics)
        mode: Evaluation mode (factual, creative, code)
        uncertainty_calibration: Ω calibration score
        clarity_gain: ΔS score
    """
    metrics: Any  # arifos_core.metrics.Metrics
    mode: EvaluationMode
    uncertainty_calibration: float  # Ω calibration score
    clarity_gain: float  # ΔS score


# Backward compatibility alias
AccountantResult = ASIResult


@dataclass
class EvaluationResult:
    """
    Final result from APEX_PRIME (Ψ) - The Judge.

    Layer 3: Constitutional verdict.

    Attributes:
        verdict: SEAL, PARTIAL, VOID, SABAR, 888_HOLD
        sentinel: Result from AGI (Δ)
        accountant: Result from ASI (Ω)
        psi_score: Ψ score (apex_pulse)
        reason: Human-readable explanation
    """
    verdict: str  # SEAL, PARTIAL, VOID, SABAR, 888_HOLD
    sentinel: SentinelResult
    accountant: Optional[ASIResult]
    psi_score: float
    reason: str
