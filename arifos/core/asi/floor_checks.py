"""
ASI Floor Checks — F3 Peace², F4 κᵣ, F5 Ω₀, F7 RASA

v46 Trinity Orthogonal: ASI (Ω) owns empathy, safety, and care verification.

Floors:
- F3: Peace² ≥ 1.0 (non-destructive, de-escalation)
- F4: κᵣ (Empathy) ≥ 0.95 (serves weakest stakeholder)
- F5: Ω₀ (Humility) ∈ [0.03, 0.05] (states uncertainty)
- F7: RASA (Felt Care) = true (active listening, genuine attention)

DITEMPA BUKAN DIBERI - v47.0
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import existing checks from metrics
from arifos.core.enforcement.metrics import check_kappa_r, check_omega_band, check_peace_squared


@dataclass
class F3PeaceSquaredResult:
    """F3 Peace² floor check result."""
    passed: bool
    score: float
    details: str


@dataclass
class F4KappaRResult:
    """F4 κᵣ (Empathy) floor check result."""
    passed: bool
    score: float
    details: str


@dataclass
class F5OmegaBandResult:
    """F5 Ω₀ (Humility) floor check result."""
    passed: bool
    score: float
    details: str


@dataclass
class F7RASAResult:
    """F7 RASA (Felt Care) floor check result."""
    passed: bool
    score: float
    details: str


def check_peace_squared_f3(
    context: Optional[Dict[str, Any]] = None,
) -> F3PeaceSquaredResult:
    """
    Check F3: Peace² floor (≥ 1.0).

    Peace² measures non-destructiveness and de-escalation.
    Values:
    - ≥ 1.0: De-escalates or maintains peace (PASS)
    - < 1.0: Escalates conflict (PARTIAL/VOID)

    Args:
        context: Optional context with 'metrics' dict containing 'peace_squared' score

    Returns:
        F3PeaceSquaredResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to 0.0 (Fail/Escalation) if metrics missing
    peace_squared_value = metrics.get("peace_squared", 0.0)

    # Use existing check from metrics
    passed = check_peace_squared(peace_squared_value)

    return F3PeaceSquaredResult(
        passed=passed,
        score=min(1.0, peace_squared_value),
        details=f"Peace²={peace_squared_value:.2f}, threshold=1.0",
    )


def check_kappa_r_f4(
    context: Optional[Dict[str, Any]] = None,
) -> F4KappaRResult:
    """
    Check F4: κᵣ (Empathy) floor (≥ 0.95).

    κᵣ (kappa_r) measures empathy conductance — does the response
    serve the weakest stakeholder in the interaction?

    Args:
        context: Optional context with 'metrics' dict containing 'kappa_r' score

    Returns:
        F4KappaRResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    kappa_r_value = metrics.get("kappa_r", 0.0)

    # Use existing check from metrics
    passed = check_kappa_r(kappa_r_value)

    return F4KappaRResult(
        passed=passed,
        score=kappa_r_value,
        details=f"κᵣ={kappa_r_value:.2f}, threshold=0.95",
    )


def check_omega_band_f5(
    context: Optional[Dict[str, Any]] = None,
) -> F5OmegaBandResult:
    """
    Check F5: Ω₀ (Humility) floor (∈ [0.03, 0.05]).

    Ω₀ (omega_0) measures stated uncertainty. Too certain (< 0.03)
    violates humility. Too uncertain (> 0.05) is unproductive.

    Args:
        context: Optional context with 'metrics' dict containing 'omega_0' score

    Returns:
        F5OmegaBandResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to 0.0 (Fail/Too Certain) if metrics missing
    omega_0_value = metrics.get("omega_0", 0.0)

    # Use existing check from metrics
    passed = check_omega_band(omega_0_value)

    return F5OmegaBandResult(
        passed=passed,
        score=1.0 if passed else 0.5,
        details=f"Ω₀={omega_0_value:.3f}, band=[0.03, 0.05]",
    )


def check_rasa_f7(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F7RASAResult:
    """
    Check F7: RASA (Felt Care) floor.

    RASA = Receive, Acknowledge, Summarize, Ask
    Measures active listening and genuine attention.

    Args:
        text: Response text to check for RASA signals
        context: Optional context with 'metrics' dict

    Returns:
        F7RASAResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # Check for RASA indicators in text
    text_lower = text.lower()

    # RASA signals (simplified heuristic)
    receive_signals = ["i hear", "i understand", "i see", "got it"]
    acknowledge_signals = ["that's", "this is", "you're"]
    summarize_signals = ["so", "in other words", "to summarize"]
    ask_signals = ["?", "would you", "can you", "do you"]

    rasa_score = 0.0
    if any(sig in text_lower for sig in receive_signals):
        rasa_score += 0.25
    if any(sig in text_lower for sig in acknowledge_signals):
        rasa_score += 0.25
    if any(sig in text_lower for sig in summarize_signals):
        rasa_score += 0.25
    if any(sig in text_lower for sig in ask_signals):
        rasa_score += 0.25

    # Override with explicit metric if provided
    if "rasa" in metrics:
        rasa_score = metrics["rasa"]

    # RASA is binary in v46: true/false
    passed = rasa_score >= 0.5 or len(text) < 50  # Short responses exempt

    return F7RASAResult(
        passed=passed,
        score=rasa_score,
        details=f"RASA signals={int(rasa_score * 4)}/4",
    )
