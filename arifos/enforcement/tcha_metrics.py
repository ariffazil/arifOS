"""
arifOS v45xx - TCHA (Time-Critical Harm Awareness) Metrics

Implements time-critical detection and delay-as-harm enforcement.
Extends F1 (Amanah/Trust) to treat preventable delay as harm.

Usage:
    from arifos.enforcement.tcha_metrics import (
        detect_time_critical,
        measure_pipeline_latency,
        check_delay_harm,
        TCHAResult,
    )
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

_TCHA_POLICY_CACHE: Optional[Dict] = None


def _load_tcha_policy() -> Dict:
    """Load TCHA policy from spec/v45/policy_tcha.json with caching."""
    global _TCHA_POLICY_CACHE
    if _TCHA_POLICY_CACHE is not None:
        return _TCHA_POLICY_CACHE

    # Try to load from spec
    spec_paths = [
        Path(__file__).parent.parent.parent / "spec" / "v45" / "policy_tcha.json",
        Path("spec/v45/policy_tcha.json"),
    ]

    for path in spec_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _TCHA_POLICY_CACHE = json.load(f)
                    return _TCHA_POLICY_CACHE
            except Exception as e:
                logger.warning(f"Failed to load TCHA policy from {path}: {e}")

    # Default policy if file not found
    _TCHA_POLICY_CACHE = {
        "time_critical": {
            "enabled": True,
            "detection_patterns": {
                "english": [
                    "urgent", "emergency", "immediately", "life-threatening",
                    "dying", "choking", "bleeding", "heart attack", "stroke",
                    "overdose", "911", "call ambulance", "help me now",
                    "can't breathe", "unconscious", "severe pain",
                ],
                "malay": [
                    "kecemasan", "segera", "sakit teruk", "tak boleh bernafas",
                    "pengsan", "lemas", "keracunan",
                ],
            },
        },
        "thresholds": {
            "max_delay_ms": 3000,
            "delay_harm_threshold_ms": 5000,
            "bypass_sabar_holds": True,
            "allow_partial_safe_answer": True,
        },
    }
    return _TCHA_POLICY_CACHE


def is_tcha_enabled() -> bool:
    """Check if TCHA is enabled via environment variable or policy."""
    env_enabled = os.getenv("ARIFOS_TCHA_ENABLED", "").lower() in ("1", "true", "yes")
    if env_enabled:
        return True

    policy = _load_tcha_policy()
    return policy.get("time_critical", {}).get("enabled", False)


# =============================================================================
# TCHA RESULT DATACLASS
# =============================================================================


@dataclass
class TCHAResult:
    """Result of TCHA detection and timing analysis."""

    # Detection
    is_time_critical: bool = False
    matched_patterns: List[str] = field(default_factory=list)
    detected_domain: Optional[str] = None

    # Timing
    processing_ms: float = 0.0
    delay_harm_flagged: bool = False
    exceeded_max_delay: bool = False

    # Verdict modifications
    bypass_holds: bool = False
    should_provide_safe_partial: bool = False

    # Audit
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Serialize for telemetry/logging."""
        return {
            "is_time_critical": self.is_time_critical,
            "matched_patterns": self.matched_patterns,
            "detected_domain": self.detected_domain,
            "processing_ms": self.processing_ms,
            "delay_harm_flagged": self.delay_harm_flagged,
            "exceeded_max_delay": self.exceeded_max_delay,
            "bypass_holds": self.bypass_holds,
            "should_provide_safe_partial": self.should_provide_safe_partial,
            "timestamp": self.timestamp,
        }


# =============================================================================
# DETECTION FUNCTIONS
# =============================================================================


def detect_time_critical(query: str) -> TCHAResult:
    """
    Detect if a query is time-critical (emergency context).

    Uses pattern matching from TCHA policy to identify:
    - Medical emergencies
    - Life-threatening situations
    - Urgent safety concerns

    Args:
        query: User query text

    Returns:
        TCHAResult with detection flags and matched patterns
    """
    result = TCHAResult()

    if not is_tcha_enabled():
        return result

    policy = _load_tcha_policy()
    patterns = policy.get("time_critical", {}).get("detection_patterns", {})
    thresholds = policy.get("thresholds", {})

    query_lower = query.lower()

    # Check all language patterns
    all_patterns = []
    for lang, lang_patterns in patterns.items():
        all_patterns.extend(lang_patterns)

    # Match patterns
    for pattern in all_patterns:
        if pattern.lower() in query_lower:
            result.matched_patterns.append(pattern)

    # Set time-critical flag if any patterns matched
    if result.matched_patterns:
        result.is_time_critical = True
        result.bypass_holds = thresholds.get("bypass_sabar_holds", True)
        result.should_provide_safe_partial = thresholds.get(
            "allow_partial_safe_answer", True
        )

        # Detect domain
        result.detected_domain = _classify_emergency_domain(query_lower)

        logger.info(
            f"TCHA: Time-critical detected. Patterns: {result.matched_patterns}, "
            f"Domain: {result.detected_domain}"
        )

    return result


def _classify_emergency_domain(query_lower: str) -> str:
    """Classify the emergency domain for routing."""
    medical_keywords = [
        "heart", "stroke", "bleeding", "choking", "overdose", "poison",
        "allergic", "breathing", "unconscious", "seizure", "pain",
    ]
    danger_keywords = [
        "fire", "flood", "earthquake", "accident", "trapped", "attack",
    ]
    mental_health_keywords = [
        "suicide", "kill myself", "end my life", "want to die",
        "bunuh diri", "nak mati",
    ]

    if any(kw in query_lower for kw in mental_health_keywords):
        return "suicide_risk"
    if any(kw in query_lower for kw in medical_keywords):
        return "medical_emergency"
    if any(kw in query_lower for kw in danger_keywords):
        return "physical_danger"

    return "general_emergency"


# =============================================================================
# TIMING FUNCTIONS
# =============================================================================


def measure_pipeline_latency(start_time: float, end_time: Optional[float] = None) -> float:
    """
    Measure pipeline processing latency in milliseconds.

    Args:
        start_time: Pipeline start timestamp (from time.time())
        end_time: Pipeline end timestamp (default: now)

    Returns:
        Latency in milliseconds
    """
    if end_time is None:
        end_time = time.time()

    return (end_time - start_time) * 1000


def check_delay_harm(
    tcha_result: TCHAResult,
    processing_ms: float,
) -> TCHAResult:
    """
    Check if processing delay constitutes harm for time-critical queries.

    Updates TCHAResult with delay_harm_flagged if threshold exceeded.

    Args:
        tcha_result: Existing TCHA detection result
        processing_ms: Actual processing time in milliseconds

    Returns:
        Updated TCHAResult with timing analysis
    """
    tcha_result.processing_ms = processing_ms

    if not tcha_result.is_time_critical:
        return tcha_result

    policy = _load_tcha_policy()
    thresholds = policy.get("thresholds", {})

    max_delay_ms = thresholds.get("max_delay_ms", 3000)
    delay_harm_threshold_ms = thresholds.get("delay_harm_threshold_ms", 5000)

    # Check if we exceeded thresholds
    if processing_ms > max_delay_ms:
        tcha_result.exceeded_max_delay = True
        logger.warning(
            f"TCHA: Exceeded max delay. {processing_ms:.0f}ms > {max_delay_ms}ms"
        )

    if processing_ms > delay_harm_threshold_ms:
        tcha_result.delay_harm_flagged = True
        logger.error(
            f"TCHA: DELAY HARM FLAGGED. {processing_ms:.0f}ms > {delay_harm_threshold_ms}ms. "
            f"This may constitute F1 violation for time-critical query."
        )

    return tcha_result


# =============================================================================
# VERDICT MODIFICATION HELPERS
# =============================================================================


def get_minimum_safe_response() -> str:
    """Get the minimum safe response for time-critical queries."""
    policy = _load_tcha_policy()
    return policy.get("verdict_overrides", {}).get(
        "minimum_safe_response",
        "If this is a life-threatening emergency, please call emergency services (911/999) immediately.",
    )


def should_bypass_hold(tcha_result: TCHAResult, hold_type: str = "SABAR") -> bool:
    """
    Check if a specific hold type should be bypassed for time-critical queries.

    Args:
        tcha_result: TCHA detection result
        hold_type: Type of hold (SABAR, 888_HOLD)

    Returns:
        True if hold should be bypassed
    """
    if not tcha_result.is_time_critical:
        return False

    policy = _load_tcha_policy()
    thresholds = policy.get("thresholds", {})

    if hold_type == "SABAR":
        return thresholds.get("bypass_sabar_holds", True)
    if hold_type in ("888_HOLD", "HOLD_888"):
        return thresholds.get("bypass_888_holds", False)

    return False


def log_tcha_event(
    event_type: str,
    tcha_result: TCHAResult,
    additional_data: Optional[Dict] = None,
) -> None:
    """
    Log TCHA event for audit trail.

    Args:
        event_type: Type of event (detected, delay_harm, override)
        tcha_result: TCHA result object
        additional_data: Extra data to log
    """
    policy = _load_tcha_policy()
    telemetry_config = policy.get("telemetry", {})

    should_log = False
    if event_type == "detected" and telemetry_config.get("log_time_critical_detected", True):
        should_log = True
    elif event_type == "delay_harm" and telemetry_config.get("log_delay_harm_flagged", True):
        should_log = True
    elif event_type == "override" and telemetry_config.get("log_override_actions", True):
        should_log = True

    if should_log:
        log_data = {
            "event": f"TCHA_{event_type.upper()}",
            "tcha": tcha_result.to_dict(),
        }
        if additional_data:
            log_data.update(additional_data)

        logger.info(f"TCHA_AUDIT: {json.dumps(log_data)}")
