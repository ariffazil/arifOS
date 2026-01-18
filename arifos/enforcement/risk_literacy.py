"""
arifOS v45xx - Risk-Literacy Output Mode

Implements explicit uncertainty disclosure and risk communication.
Extends F7 (Humility) to require transparent confidence levels.

Usage:
    from arifos.enforcement.risk_literacy import (
        calculate_risk_score,
        get_risk_level,
        format_risk_disclosure,
        RiskLiteracyResult,
    )
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

_RISK_LITERACY_POLICY_CACHE: Optional[Dict] = None


def _load_risk_literacy_policy() -> Dict:
    """Load Risk-Literacy policy from spec/v45/policy_risk_literacy.json with caching."""
    global _RISK_LITERACY_POLICY_CACHE
    if _RISK_LITERACY_POLICY_CACHE is not None:
        return _RISK_LITERACY_POLICY_CACHE

    # Try to load from spec
    spec_paths = [
        Path(__file__).parent.parent.parent / "spec" / "v45" / "policy_risk_literacy.json",
        Path("spec/v45/policy_risk_literacy.json"),
    ]

    for path in spec_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _RISK_LITERACY_POLICY_CACHE = json.load(f)
                    return _RISK_LITERACY_POLICY_CACHE
            except Exception as e:
                logger.warning(f"Failed to load Risk-Literacy policy from {path}: {e}")

    # Default policy if file not found
    _RISK_LITERACY_POLICY_CACHE = {
        "risk_literacy": {
            "enabled": True,
            "thresholds": {
                "min_confidence_for_full_release": 0.95,
                "min_confidence_for_partial_release": 0.80,
                "high_risk_score_threshold": 0.70,
            },
            "templates": {
                "uncertainty_note": "(Note: Confidence {confidence:.0%} – This response may require verification.)",
                "low_confidence_note": "(Caution: Low confidence ({confidence:.0%}). Please verify critical details independently.)",
            },
        },
    }
    return _RISK_LITERACY_POLICY_CACHE


def is_risk_literacy_enabled() -> bool:
    """Check if Risk-Literacy is enabled via environment variable or policy."""
    env_enabled = os.getenv("ARIFOS_RISK_LITERACY_ENABLED", "").lower() in ("1", "true", "yes")
    if env_enabled:
        return True

    policy = _load_risk_literacy_policy()
    return policy.get("risk_literacy", {}).get("enabled", False)


# =============================================================================
# RISK LITERACY RESULT DATACLASS
# =============================================================================


@dataclass
class RiskLiteracyResult:
    """Result of risk analysis for output formatting."""

    # Core metrics
    confidence: float = 1.0  # 0.0-1.0, derived from floor metrics
    risk_score: float = 0.0  # 0.0-1.0, composite risk from floor failures

    # Derived classifications
    risk_level: str = "LOW"  # LOW, MODERATE, HIGH, CRITICAL
    uncertainty_flag: bool = False  # True if confidence < threshold

    # Output formatting
    should_append_disclaimer: bool = False
    disclaimer_text: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for telemetry/API output."""
        return {
            "confidence": round(self.confidence, 4),
            "risk_score": round(self.risk_score, 4),
            "risk_level": self.risk_level,
            "uncertainty_flag": self.uncertainty_flag,
            "should_append_disclaimer": self.should_append_disclaimer,
            "disclaimer_text": self.disclaimer_text,
        }


# =============================================================================
# RISK CALCULATION FUNCTIONS
# =============================================================================


def calculate_confidence_from_metrics(metrics: Any) -> float:
    """
    Calculate overall confidence score from floor metrics.

    Confidence is derived from:
    - F2 Truth score (primary)
    - F7 Omega0 (humility/uncertainty)
    - Ψ (Psi) life force

    Args:
        metrics: Metrics object from enforcement.metrics

    Returns:
        Confidence score 0.0-1.0
    """
    if metrics is None:
        return 0.5  # Default uncertainty

    # Primary: Truth score
    truth = getattr(metrics, "truth", 0.99)

    # Secondary: Inverse of Omega0 (higher Omega0 = more uncertainty = lower confidence)
    omega0 = getattr(metrics, "omega_0", 0.04)
    omega_factor = 1.0 - (omega0 * 10)  # Scale omega to 0-0.5 impact
    omega_factor = max(0.5, min(1.0, omega_factor))

    # Tertiary: Psi life force
    psi = getattr(metrics, "psi", 1.0)
    if psi is None:
        psi = 1.0
    psi_factor = min(1.0, psi)  # Cap at 1.0

    # Weighted combination
    confidence = (truth * 0.6) + (omega_factor * 0.2) + (psi_factor * 0.2)

    return max(0.0, min(1.0, confidence))


def calculate_risk_score(metrics: Any = None, floor_failures: List[str] = None) -> float:
    """
    Calculate composite risk score from floor metrics and failures.

    Risk increases with:
    - Low truth scores
    - Floor failures
    - High Omega0 (uncertainty)
    - Low Psi (vitality)

    Args:
        metrics: Metrics object
        floor_failures: List of failed floor names

    Returns:
        Risk score 0.0-1.0 (higher = more risk)
    """
    risk = 0.0

    if metrics is not None:
        # Truth inversely correlates with risk
        truth = getattr(metrics, "truth", 0.99)
        risk += (1.0 - truth) * 0.4

        # High Omega0 = more uncertainty = more risk
        omega0 = getattr(metrics, "omega_0", 0.04)
        if omega0 > 0.05:  # Above humility band
            risk += 0.15

        # Low Psi = low vitality = more risk
        psi = getattr(metrics, "psi", 1.0) or 1.0
        if psi < 1.0:
            risk += (1.0 - psi) * 0.2

    # Floor failures increase risk
    if floor_failures:
        failure_risk = min(0.3, len(floor_failures) * 0.1)
        risk += failure_risk

    return max(0.0, min(1.0, risk))


def get_risk_level(risk_score: float) -> str:
    """
    Classify risk score into risk level.

    Args:
        risk_score: Risk score 0.0-1.0

    Returns:
        Risk level: LOW, MODERATE, HIGH, or CRITICAL
    """
    policy = _load_risk_literacy_policy()
    risk_levels = policy.get("risk_literacy", {}).get("risk_levels", {})

    for level, config in risk_levels.items():
        if isinstance(config, dict):
            range_vals = config.get("range", [0, 1])
            if len(range_vals) == 2:
                if range_vals[0] <= risk_score < range_vals[1]:
                    return level

    # Default classification if policy not loaded
    if risk_score < 0.30:
        return "LOW"
    elif risk_score < 0.70:
        return "MODERATE"
    elif risk_score < 0.85:
        return "HIGH"
    else:
        return "CRITICAL"


# =============================================================================
# DISCLOSURE FORMATTING
# =============================================================================


def format_risk_disclosure(
    confidence: float,
    risk_score: float,
    risk_level: str,
) -> str:
    """
    Format the risk disclosure text based on confidence and risk.

    Args:
        confidence: Confidence score 0.0-1.0
        risk_score: Risk score 0.0-1.0
        risk_level: Risk level string

    Returns:
        Formatted disclosure text
    """
    policy = _load_risk_literacy_policy()
    templates = policy.get("risk_literacy", {}).get("templates", {})
    thresholds = policy.get("risk_literacy", {}).get("thresholds", {})

    min_confidence_full = thresholds.get("min_confidence_for_full_release", 0.95)
    min_confidence_partial = thresholds.get("min_confidence_for_partial_release", 0.80)

    if confidence >= min_confidence_full:
        # High confidence - no disclosure needed
        return ""
    elif confidence >= min_confidence_partial:
        # Medium confidence - standard uncertainty note
        template = templates.get(
            "uncertainty_note",
            "(Note: Confidence {confidence:.0%} – This response may require verification.)"
        )
    else:
        # Low confidence - stronger warning
        template = templates.get(
            "low_confidence_note",
            "(Caution: Low confidence ({confidence:.0%}). Please verify critical details independently.)"
        )

    # Add high risk note if applicable
    if risk_level in ("HIGH", "CRITICAL"):
        high_risk_template = templates.get(
            "high_risk_note",
            "⚠️ HIGH RISK: This response involves uncertainty. Please proceed with caution."
        )
        template = high_risk_template + "\n" + template

    return template.format(confidence=confidence, risk_score=risk_score, risk_level=risk_level)


def analyze_for_risk_literacy(
    metrics: Any = None,
    floor_failures: List[str] = None,
) -> RiskLiteracyResult:
    """
    Full risk literacy analysis.

    Args:
        metrics: Metrics object from enforcement
        floor_failures: List of failed floor names

    Returns:
        RiskLiteracyResult with all computed values
    """
    result = RiskLiteracyResult()

    # Calculate metrics
    result.confidence = calculate_confidence_from_metrics(metrics)
    result.risk_score = calculate_risk_score(metrics, floor_failures)
    result.risk_level = get_risk_level(result.risk_score)

    # Determine if uncertainty flag should be set
    policy = _load_risk_literacy_policy()
    thresholds = policy.get("risk_literacy", {}).get("thresholds", {})
    min_confidence_full = thresholds.get("min_confidence_for_full_release", 0.95)

    result.uncertainty_flag = result.confidence < min_confidence_full
    result.should_append_disclaimer = result.uncertainty_flag or result.risk_level in ("HIGH", "CRITICAL")

    if result.should_append_disclaimer:
        result.disclaimer_text = format_risk_disclosure(
            result.confidence,
            result.risk_score,
            result.risk_level,
        )

    return result


# =============================================================================
# VERDICT ENHANCEMENT
# =============================================================================


def enhance_verdict_with_risk_literacy(
    verdict: Any,
    metrics: Any = None,
    floor_failures: List[str] = None,
) -> Tuple[Any, RiskLiteracyResult]:
    """
    Enhance a verdict object with risk literacy data.

    Args:
        verdict: ApexVerdict object
        metrics: Metrics object
        floor_failures: List of failed floors

    Returns:
        Tuple of (enhanced verdict, RiskLiteracyResult)
    """
    risk_result = analyze_for_risk_literacy(metrics, floor_failures)

    # Add risk literacy fields to verdict if possible
    if hasattr(verdict, "__dict__"):
        verdict.confidence = risk_result.confidence
        verdict.risk_score = risk_result.risk_score
        verdict.risk_level = risk_result.risk_level
        verdict.uncertainty_flag = risk_result.uncertainty_flag

    return verdict, risk_result


def format_output_with_risk_literacy(
    response_text: str,
    risk_result: RiskLiteracyResult,
) -> str:
    """
    Append risk literacy disclosure to response text if needed.

    Args:
        response_text: Original response text
        risk_result: RiskLiteracyResult from analysis

    Returns:
        Response with disclaimer appended if applicable
    """
    if not is_risk_literacy_enabled():
        return response_text

    if not risk_result.should_append_disclaimer:
        return response_text

    if not risk_result.disclaimer_text:
        return response_text

    # Append disclaimer
    return f"{response_text}\n\n{risk_result.disclaimer_text}"
