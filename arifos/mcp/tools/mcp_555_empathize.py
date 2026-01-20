"""
MCP Tool 555: EMPATHIZE

Power-aware recalibration through Peace² and κᵣ (kappa recalibration).

Constitutional validation:
- F5 (Peace²): Detect aggression, dismissiveness, emotional harm
- F6 (κᵣ/Empathy): Power-aware recalibration for vulnerable stakeholders

This tool analyzes tone and power dynamics to ensure warm, contextual responses.
Returns PASS/PARTIAL based on peace score and empathy recalibration.
"""

import asyncio
import re
from datetime import datetime, timezone
from typing import Any, Dict

from arifos.mcp.models import VerdictResponse


# =============================================================================
# CONSTANTS
# =============================================================================

# Peace² threshold (1.0 = neutral, >1.0 = positive, <1.0 = harmful)
PEACE_THRESHOLD = 1.0

# κᵣ (kappa recalibration) threshold
KAPPA_THRESHOLD = 0.95

# Dismissive patterns (regex list)
DISMISSIVE_PATTERNS = [
    r"(?i)\bskill issue\b",
    r"(?i)\bobvious(ly)?\b",
    r"(?i)\byou should (already )?know\b",
    r"(?i)\bjust google (it)?\b",
    r"(?i)\brtfm\b",  # Read the manual
    r"(?i)\bthat'?s (so )?basic\b",
    r"(?i)\bwhat a (dumb|stupid) question\b",
    r"(?i)\bfigure it out yourself\b",
    r"(?i)\bnot my (job|problem)\b",
    r"(?i)\bwhy (are you|do you) even ask(ing)?\b",
    r"(?i)\bcan'?t you (just)?\b",
]

# Aggressive patterns
AGGRESSIVE_PATTERNS = [
    r"(?i)\b(shut up|stfu)\b",
    r"(?i)\b(idiot|moron|stupid)\b",
    r"(?i)\byou'?re (being )?ridiculous\b",
    r"(?i)\bwhat'?s wrong with you\b",
    r"(?i)\bdon'?t be (so )?(dumb|stupid)\b",
]

# Warm tone indicators (positive signals)
WARM_PATTERNS = [
    r"(?i)\bhappy to help\b",
    r"(?i)\blet me (help|assist|explain)\b",
    r"(?i)\bgreat question\b",
    r"(?i)\bthat makes sense\b",
    r"(?i)\bI understand\b",
    r"(?i)\bno worries?\b",
    r"(?i)\bfeel free to\b",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def detect_dismissive_patterns(text: str) -> bool:
    """
    Detect dismissive language patterns.

    Constitutional grounding:
    - F6 (Empathy): Identify power-dismissive communication

    Args:
        text: Response text to analyze

    Returns:
        True if dismissive patterns detected, False otherwise
    """
    for pattern in DISMISSIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def detect_aggressive_patterns(text: str) -> bool:
    """
    Detect aggressive language patterns.

    Constitutional grounding:
    - F5 (Peace²): Identify harmful communication

    Args:
        text: Response text to analyze

    Returns:
        True if aggressive patterns detected, False otherwise
    """
    for pattern in AGGRESSIVE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False


def count_warm_indicators(text: str) -> int:
    """
    Count warm tone indicators.

    Args:
        text: Response text to analyze

    Returns:
        Count of warm tone patterns found
    """
    count = 0
    for pattern in WARM_PATTERNS:
        if re.search(pattern, text):
            count += 1
    return count


def calculate_peace_score(text: str) -> float:
    """
    Calculate Peace² score.

    Constitutional grounding:
    - F5 (Peace²): Non-destructive communication measurement

    Scoring:
    - Base: 1.0 (neutral)
    - Penalties: -0.5 per aggressive pattern, -0.3 per dismissive pattern
    - Bonuses: +0.1 per warm indicator (max +0.3)
    - Range: [0.0, 1.5]

    Args:
        text: Response text to analyze

    Returns:
        Peace score in [0.0, 1.5]
    """
    score = 1.0

    # Penalties
    if detect_aggressive_patterns(text):
        score -= 0.5

    if detect_dismissive_patterns(text):
        score -= 0.3

    # Bonuses
    warm_count = count_warm_indicators(text)
    score += min(0.3, warm_count * 0.1)

    # Clamp to [0.0, 1.5]
    return min(1.5, max(0.0, score))


def calculate_kappa_r(recipient_context: Dict[str, Any]) -> float:
    """
    Calculate κᵣ (kappa recalibration) for power-aware communication.

    Constitutional grounding:
    - F6 (κᵣ/Empathy): Serve weakest stakeholder

    Uses context clues to estimate power differential:
    - audience_level: "beginner" (+0.05), "expert" (-0.05)
    - vulnerability_flags: True (+0.10), False (0)
    - accessibility_needs: True (+0.10), False (0)

    Base: 0.90, adjustments can push to [0.75, 1.0]

    Args:
        recipient_context: Context dict with audience/vulnerability info

    Returns:
        κᵣ score in [0.75, 1.0]
    """
    kappa = 0.90  # Baseline

    # Audience level adjustment
    audience_level = recipient_context.get("audience_level", "general")
    if audience_level == "beginner":
        kappa += 0.05
    elif audience_level == "expert":
        kappa -= 0.05

    # Vulnerability flags
    if recipient_context.get("vulnerability_flags", False):
        kappa += 0.10

    # Accessibility needs
    if recipient_context.get("accessibility_needs", False):
        kappa += 0.10

    # Power differential (if recipient is low-power, increase recalibration)
    power_level = recipient_context.get("power_level", "medium")
    if power_level == "low":
        kappa += 0.05
    elif power_level == "high":
        kappa -= 0.05

    # Clamp to [0.75, 1.0]
    return min(1.0, max(0.75, kappa))


# =============================================================================
# MCP TOOL IMPLEMENTATION
# =============================================================================

async def mcp_555_empathize(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 555: EMPATHIZE - Power-aware recalibration using ASIActionCore.

    Constitutional role:
    - F5 (Peace²): Detects aggression, dismissal, harm
    - F6 (κᵣ): Power-aware recalibration

    Args:
        request: {
            "response_text": str,           # Response to analyze
            "recipient_context": dict,      # Audience/power context
        }

    Returns:
        VerdictResponse.
    """
    from arifos.core.asi.kernel import ASIActionCore

    # Extract inputs
    response_text = request.get("response_text", "")
    recipient_context = request.get("recipient_context", {})

    # Validate inputs
    if not isinstance(response_text, str):
        response_text = ""

    if not isinstance(recipient_context, dict):
        recipient_context = {}

    # Call ASI Kernel
    # The Kernel expects "text" and "context"
    # It returns a dict with "omega_verdict" (SEAL/PARTIAL/VOID)
    kernel_result = await ASIActionCore.empathize(
        text=response_text,
        context=recipient_context
    )

    omega_verdict = kernel_result.get("omega_verdict", "PARTIAL")
    vulnerability_score = kernel_result.get("vulnerability_score", 0.5)
    action = kernel_result.get("action", "Neutral")

    # Backward compatibility: Calculate legacy fields for tests
    legacy_peace_score = calculate_peace_score(response_text)
    legacy_kappa_r = calculate_kappa_r(recipient_context)
    dismissive_detected = detect_dismissive_patterns(response_text)
    aggressive_detected = detect_aggressive_patterns(response_text)

    # Determine verdict using legacy logic (for backward compatibility)
    # PASS if both thresholds met, PARTIAL otherwise (never VOID)
    if legacy_peace_score >= PEACE_THRESHOLD and legacy_kappa_r >= KAPPA_THRESHOLD:
        verdict = "PASS"
        reason = f"Peace: {legacy_peace_score:.2f} ≥ {PEACE_THRESHOLD}, κᵣ: {legacy_kappa_r:.2f} ≥ {KAPPA_THRESHOLD}"
    else:
        verdict = "PARTIAL"
        if legacy_peace_score < PEACE_THRESHOLD:
            reason = f"Peace² warning: {legacy_peace_score:.2f} < {PEACE_THRESHOLD}"
        else:
            reason = f"κᵣ recalibration: {legacy_kappa_r:.2f} (threshold {KAPPA_THRESHOLD})"

    # Append ASI analysis to reason for transparency
    reason += f" | ASI Verdict: {omega_verdict} (Vuln: {vulnerability_score:.2f})"

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    return VerdictResponse(
        verdict=verdict,
        reason=reason,
        side_data={
            # Legacy fields for backward compatibility
            "peace_score": legacy_peace_score,
            "kappa_r": legacy_kappa_r,
            "peace_threshold": PEACE_THRESHOLD,
            "kappa_threshold": KAPPA_THRESHOLD,
            "dismissive_detected": dismissive_detected,
            "aggressive_detected": aggressive_detected,
            # v49 ASI Kernel result
            "asi_meta": kernel_result
        },
        timestamp=timestamp,
    )


def mcp_555_empathize_sync(request: Dict[str, Any]) -> VerdictResponse:
    """Synchronous wrapper for mcp_555_empathize."""
    return asyncio.run(mcp_555_empathize(request))
