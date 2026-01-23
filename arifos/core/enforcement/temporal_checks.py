"""
arifOS v45xx - Temporal Intelligence Primitives

Implements:
- Timestamp Anchoring: Factual claims require temporal context
- Contradiction Detection: Self-contradictions trigger consensus failure
- Lag Metrics: Processing delays affect Ψ score

TIME-1 Invariant: "Time is a Constitutional Force. Entropy Rot is automatic."

Usage:
    from arifos.core.enforcement.temporal_checks import (
        check_timestamp_anchor,
        detect_contradiction,
        compute_lag_penalty,
    )
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

_TEMPORAL_POLICY_CACHE: Optional[Dict] = None


def _load_temporal_policy() -> Dict:
    """Load Temporal Intelligence policy from spec/v45/policy_temporal.json."""
    global _TEMPORAL_POLICY_CACHE
    if _TEMPORAL_POLICY_CACHE is not None:
        return _TEMPORAL_POLICY_CACHE

    spec_paths = [
        Path(__file__).parent.parent.parent / "spec" / "v45" / "policy_temporal.json",
        Path("spec/v45/policy_temporal.json"),
    ]

    for path in spec_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _TEMPORAL_POLICY_CACHE = json.load(f)
                    return _TEMPORAL_POLICY_CACHE
            except Exception as e:
                logger.warning(f"Failed to load Temporal policy from {path}: {e}")

    # Default policy
    _TEMPORAL_POLICY_CACHE = {
        "temporal_intelligence": {
            "enabled": True,
            "timestamp_anchoring": {
                "enabled": True,
                "required_domains": ["medical", "legal", "financial", "news"],
                "timestamp_patterns": [
                    r"as of \d{4}",
                    r"\d{4}-\d{2}",
                    r"currently",
                    r"today",
                ],
            },
            "contradiction_detection": {
                "enabled": True,
                "triggers_hold": True,
            },
            "lag_metrics": {
                "enabled": True,
                "max_processing_ms": 5000,
                "lag_penalty_psi": 0.1,
            },
        },
        "domain_keywords": {
            "medical": ["diagnosis", "treatment", "medication", "symptoms"],
            "legal": ["law", "legal", "court", "statute"],
            "financial": ["stock", "market", "investment", "price"],
            "news": ["news", "breaking", "reported", "announced"],
        },
    }
    return _TEMPORAL_POLICY_CACHE


def is_temporal_intel_enabled() -> bool:
    """Check if Temporal Intelligence is enabled."""
    env_enabled = os.getenv("ARIFOS_TEMPORAL_INTEL_ENABLED", "").lower() in ("1", "true", "yes")
    if env_enabled:
        return True

    policy = _load_temporal_policy()
    return policy.get("temporal_intelligence", {}).get("enabled", False)


# =============================================================================
# TEMPORAL CHECK RESULTS
# =============================================================================


@dataclass
class TemporalCheckResult:
    """Result of temporal intelligence checks."""

    # Timestamp anchoring
    has_temporal_anchor: bool = True
    timestamp_required: bool = False
    detected_domain: Optional[str] = None

    # Contradiction detection
    contradiction_detected: bool = False
    contradiction_details: Optional[str] = None

    # Lag metrics
    processing_ms: float = 0.0
    lag_exceeded: bool = False
    psi_penalty: float = 0.0

    # Overall
    floor_violations: List[str] = field(default_factory=list)
    suggested_verdict_override: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "has_temporal_anchor": self.has_temporal_anchor,
            "timestamp_required": self.timestamp_required,
            "detected_domain": self.detected_domain,
            "contradiction_detected": self.contradiction_detected,
            "contradiction_details": self.contradiction_details,
            "processing_ms": self.processing_ms,
            "lag_exceeded": self.lag_exceeded,
            "psi_penalty": self.psi_penalty,
            "floor_violations": self.floor_violations,
            "suggested_verdict_override": self.suggested_verdict_override,
        }


# =============================================================================
# TIMESTAMP ANCHORING
# =============================================================================


def _detect_domain(query: str, response: str) -> Optional[str]:
    """Detect if query/response falls into a timestamp-required domain."""
    policy = _load_temporal_policy()
    domain_keywords = policy.get("domain_keywords", {})

    combined = f"{query} {response}".lower()

    for domain, keywords in domain_keywords.items():
        for keyword in keywords:
            if keyword.lower() in combined:
                return domain

    return None


def _find_timestamp(text: str) -> Optional[str]:
    """Find a timestamp or temporal reference in text."""
    policy = _load_temporal_policy()
    patterns = policy.get("temporal_intelligence", {}).get("timestamp_anchoring", {}).get("timestamp_patterns", [])

    for pattern in patterns:
        try:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        except re.error:
            # Pattern might be a plain string, not regex
            if pattern.lower() in text.lower():
                return pattern

    return None


def check_timestamp_anchor(query: str, response: str) -> TemporalCheckResult:
    """
    Check if response has appropriate temporal anchoring for its domain.

    Args:
        query: User query
        response: AI response

    Returns:
        TemporalCheckResult with anchor status
    """
    result = TemporalCheckResult()

    if not is_temporal_intel_enabled():
        return result

    policy = _load_temporal_policy()
    anchoring_config = policy.get("temporal_intelligence", {}).get("timestamp_anchoring", {})

    if not anchoring_config.get("enabled", True):
        return result

    # Check domain
    domain = _detect_domain(query, response)
    result.detected_domain = domain

    required_domains = anchoring_config.get("required_domains", [])
    if domain in required_domains:
        result.timestamp_required = True

        # Check for timestamp in response
        timestamp = _find_timestamp(response)
        result.has_temporal_anchor = timestamp is not None

        if not result.has_temporal_anchor:
            # Missing timestamp in timestamp-required domain
            result.floor_violations.append("F4_MISSING_TIMESTAMP")
            verdict_override = anchoring_config.get("missing_timestamp_verdict", "PARTIAL")
            result.suggested_verdict_override = verdict_override

            logger.warning(
                f"TEMPORAL: Missing timestamp anchor for {domain} domain. "
                f"Suggesting verdict: {verdict_override}"
            )

    return result


# =============================================================================
# CONTRADICTION DETECTION
# =============================================================================

# Session-based assertion memory (in production, use proper state management)
_ASSERTION_MEMORY: Dict[str, List[Dict]] = {}


def _extract_key_assertions(text: str) -> List[str]:
    """Extract key factual assertions from text for contradiction checking."""
    assertions = []

    # Simple extraction: look for declarative sentences
    sentences = re.split(r'[.!?]', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:  # Skip very short fragments
            # Look for assertion patterns
            assertion_patterns = [
                r"is\s+\w+",
                r"are\s+\w+",
                r"was\s+\w+",
                r"were\s+\w+",
                r"will\s+\w+",
                r"has\s+\w+",
                r"have\s+\w+",
            ]
            for pattern in assertion_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    assertions.append(sentence[:200])  # Cap length
                    break

    return assertions


def _check_contradiction(new_assertion: str, previous_assertions: List[str]) -> Optional[str]:
    """
    Check if a new assertion contradicts previous ones.

    Simple heuristic: Look for direct negation patterns.
    """
    new_lower = new_assertion.lower()

    for prev in previous_assertions:
        prev_lower = prev.lower()

        # Check for negation patterns
        # "X is Y" vs "X is not Y"
        if "not" in new_lower and "not" not in prev_lower:
            # Extract subject-predicate and compare
            # Simplified: check if same subject with opposite predicate
            new_words = set(new_lower.split())
            prev_words = set(prev_lower.split())
            overlap = new_words & prev_words

            if len(overlap) > 3:  # Significant overlap suggests same topic
                if "not" in new_lower:
                    return f"Potential contradiction: '{new_assertion[:50]}...' vs '{prev[:50]}...'"

        # "X is true" vs "X is false"
        if ("true" in new_lower and "false" in prev_lower) or \
           ("false" in new_lower and "true" in prev_lower):
            return f"Boolean contradiction detected"

    return None


def detect_contradiction(
    session_id: str,
    response: str,
    store_assertions: bool = True,
) -> TemporalCheckResult:
    """
    Detect if response contradicts previous assertions in this session.

    Args:
        session_id: Session identifier
        response: New response text
        store_assertions: Whether to store new assertions

    Returns:
        TemporalCheckResult with contradiction status
    """
    result = TemporalCheckResult()

    if not is_temporal_intel_enabled():
        return result

    policy = _load_temporal_policy()
    contradiction_config = policy.get("temporal_intelligence", {}).get("contradiction_detection", {})

    if not contradiction_config.get("enabled", True):
        return result

    # Get previous assertions
    previous = _ASSERTION_MEMORY.get(session_id, [])
    window = contradiction_config.get("consistency_window_turns", 5)
    previous = previous[-window:]  # Keep only recent

    # Extract new assertions
    new_assertions = _extract_key_assertions(response)

    # Check for contradictions
    all_previous_text = [a.get("assertion", "") for a in previous]

    for new_assertion in new_assertions:
        contradiction = _check_contradiction(new_assertion, all_previous_text)
        if contradiction:
            result.contradiction_detected = True
            result.contradiction_details = contradiction
            result.floor_violations.append("F3_CONTRADICTION")

            if contradiction_config.get("triggers_hold", True):
                result.suggested_verdict_override = contradiction_config.get("hold_type", "HOLD_888")

            logger.warning(f"TEMPORAL: Contradiction detected - {contradiction}")
            break

    # Store new assertions
    if store_assertions:
        if session_id not in _ASSERTION_MEMORY:
            _ASSERTION_MEMORY[session_id] = []

        for assertion in new_assertions:
            _ASSERTION_MEMORY[session_id].append({
                "assertion": assertion,
                "timestamp": time.time(),
            })

        # Prune old assertions
        _ASSERTION_MEMORY[session_id] = _ASSERTION_MEMORY[session_id][-20:]

    return result


def clear_assertion_memory(session_id: str) -> None:
    """Clear assertion memory for a session."""
    if session_id in _ASSERTION_MEMORY:
        del _ASSERTION_MEMORY[session_id]


# =============================================================================
# LAG METRICS
# =============================================================================


def compute_lag_penalty(
    start_time: float,
    end_time: Optional[float] = None,
) -> TemporalCheckResult:
    """
    Compute Ψ penalty based on processing lag.

    Args:
        start_time: Pipeline start timestamp
        end_time: Pipeline end timestamp (default: now)

    Returns:
        TemporalCheckResult with lag metrics
    """
    result = TemporalCheckResult()

    if not is_temporal_intel_enabled():
        return result

    if end_time is None:
        end_time = time.time()

    result.processing_ms = (end_time - start_time) * 1000

    policy = _load_temporal_policy()
    lag_config = policy.get("temporal_intelligence", {}).get("lag_metrics", {})

    if not lag_config.get("enabled", True):
        return result

    max_ms = lag_config.get("max_processing_ms", 5000)
    critical_ms = lag_config.get("critical_lag_ms", 10000)
    penalty_per_unit = lag_config.get("lag_penalty_psi", 0.1)

    if result.processing_ms > max_ms:
        result.lag_exceeded = True

        # Calculate penalty based on how much lag exceeded threshold
        excess_ms = result.processing_ms - max_ms
        penalty_units = excess_ms / 1000  # Per second of excess
        result.psi_penalty = min(0.5, penalty_units * penalty_per_unit)  # Cap at 0.5

        if result.processing_ms > critical_ms:
            result.floor_violations.append("F1_CRITICAL_LAG")
            result.suggested_verdict_override = "PARTIAL"
        else:
            result.floor_violations.append("F1_LAG_WARNING")

        logger.warning(
            f"TEMPORAL: Lag exceeded threshold. {result.processing_ms:.0f}ms > {max_ms}ms. "
            f"Ψ penalty: {result.psi_penalty:.2f}"
        )

    return result


# =============================================================================
# COMBINED TEMPORAL CHECK
# =============================================================================


def run_temporal_checks(
    session_id: str,
    query: str,
    response: str,
    start_time: float,
    end_time: Optional[float] = None,
) -> TemporalCheckResult:
    """
    Run all temporal intelligence checks.

    Args:
        session_id: Session identifier
        query: User query
        response: AI response
        start_time: Pipeline start time
        end_time: Pipeline end time

    Returns:
        Combined TemporalCheckResult
    """
    result = TemporalCheckResult()

    if not is_temporal_intel_enabled():
        return result

    # Timestamp anchoring
    anchor_result = check_timestamp_anchor(query, response)
    result.has_temporal_anchor = anchor_result.has_temporal_anchor
    result.timestamp_required = anchor_result.timestamp_required
    result.detected_domain = anchor_result.detected_domain
    result.floor_violations.extend(anchor_result.floor_violations)

    # Contradiction detection
    contradiction_result = detect_contradiction(session_id, response)
    result.contradiction_detected = contradiction_result.contradiction_detected
    result.contradiction_details = contradiction_result.contradiction_details
    result.floor_violations.extend(contradiction_result.floor_violations)

    # Lag metrics
    lag_result = compute_lag_penalty(start_time, end_time)
    result.processing_ms = lag_result.processing_ms
    result.lag_exceeded = lag_result.lag_exceeded
    result.psi_penalty = lag_result.psi_penalty
    result.floor_violations.extend(lag_result.floor_violations)

    # Determine verdict override (most severe wins)
    override_priority = ["HOLD_888", "VOID", "PARTIAL"]
    for override in override_priority:
        if anchor_result.suggested_verdict_override == override or \
           contradiction_result.suggested_verdict_override == override or \
           lag_result.suggested_verdict_override == override:
            result.suggested_verdict_override = override
            break

    return result
