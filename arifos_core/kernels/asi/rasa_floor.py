"""
F7 RASA Floor — Active Listening & Felt Care Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/777_eureka/760_RASA_F7_v46.md
Stage: 777_eureka (ASI Omega Engine)

RASA Floor Requirements:
  • RASA = true (Receive, Acknowledge, Summarize, Ask)
  • Active listening and genuine attention
  • Responsiveness to stakeholder needs
  • FAIL-CLOSED: missing signals → FAIL

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class F7RASAResult:
    """F7 RASA (Felt Care) floor check result."""
    passed: bool
    score: float
    details: str


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
