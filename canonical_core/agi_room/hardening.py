"""
AGI Room Hardening - Constitutional Safety Layer

ARIF Loop v52.1 - Additional Protections

This module provides hardening checks that strengthen the AGI Room:
1. High-Stakes Detection (class-H queries requiring extra scrutiny)
2. Hantu Pre-Screening (dark cleverness patterns - F9 assist)
3. Telemetry & Audit Hooks (constitutional monitoring)
4. Rate Limiting & Abuse Detection
5. Scar-Weight Awareness (preparing for ASI integration)

These checks run BEFORE and AFTER the main pipeline stages.

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from __future__ import annotations

import re
import time
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum
from collections import defaultdict
import threading


# =============================================================================
# CONSTANTS
# =============================================================================

# High-Stakes Keywords (class-H queries)
HIGH_STAKES_PATTERNS = [
    # Destructive actions
    r"\b(delete|remove|destroy|drop|truncate|wipe)\b",
    r"\b(rm\s+-rf|format|reset\s+hard)\b",
    # Production/deployment
    r"\b(production|prod|deploy|release|publish|live)\b",
    r"\b(migrate|migration|database|schema)\b",
    # Security-sensitive
    r"\b(password|secret|credential|api.?key|token|auth)\b",
    r"\b(encrypt|decrypt|hash|sign|certificate)\b",
    # Financial/legal
    r"\b(payment|transaction|money|financial|legal|contract)\b",
    # Admin/root
    r"\b(admin|root|sudo|privilege|permission|access.?control)\b",
    # Mass operations
    r"\b(bulk|mass|all\s+users|everyone|broadcast)\b",
]

# Hantu Patterns (dark cleverness - technically correct but ethically wrong)
HANTU_PATTERNS = [
    # Loophole exploitation
    (r"technically\s+(legal|correct|true|allowed)", "loophole_exploitation"),
    (r"letter\s+of\s+(?:the\s+)?law", "letter_not_spirit"),
    (r"plausible\s+deniability", "deniability_setup"),
    # Manipulation tactics
    (r"make\s+them\s+think", "manipulation"),
    (r"without\s+(?:them\s+)?knowing", "deception"),
    (r"hide\s+(?:the|this|that|it)", "concealment"),
    # Metric gaming
    (r"game\s+the\s+(?:system|metrics?)", "metric_gaming"),
    (r"look\s+(?:good|better)\s+on\s+paper", "appearance_over_substance"),
    # Authority bypass
    (r"work\s*around\s+(?:the\s+)?(?:rules?|policy|policies)", "rule_bypass"),
    (r"circumvent", "circumvention"),
]

# Rate Limiting
MAX_QUERIES_PER_MINUTE = 60
MAX_QUERIES_PER_SESSION = 1000
ABUSE_THRESHOLD = 0.8  # Repeated injection attempts


# =============================================================================
# DATA TYPES
# =============================================================================

class RiskLevel(str, Enum):
    """Risk classification for queries."""
    LOW = "low"           # Normal query, proceed normally
    MEDIUM = "medium"     # Some caution needed
    HIGH = "high"         # Class-H, extra verification
    CRITICAL = "critical" # Requires 888_HOLD


@dataclass
class HardeningResult:
    """Result of hardening checks."""
    # Risk assessment
    risk_level: RiskLevel = RiskLevel.LOW
    high_stakes_triggers: List[str] = field(default_factory=list)

    # Hantu detection (F9 pre-screening)
    hantu_score: float = 0.0
    hantu_patterns: List[str] = field(default_factory=list)

    # Rate limiting
    rate_limited: bool = False
    queries_this_minute: int = 0
    queries_this_session: int = 0

    # Abuse detection
    abuse_score: float = 0.0
    repeated_violations: int = 0

    # Verdict
    proceed: bool = True
    warnings: List[str] = field(default_factory=list)
    block_reason: str = ""

    # Telemetry
    check_duration_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level.value,
            "high_stakes_triggers": self.high_stakes_triggers,
            "hantu_score": self.hantu_score,
            "hantu_patterns": self.hantu_patterns,
            "rate_limited": self.rate_limited,
            "abuse_score": self.abuse_score,
            "proceed": self.proceed,
            "warnings": self.warnings,
            "block_reason": self.block_reason,
            "check_duration_ms": self.check_duration_ms,
        }


@dataclass
class TelemetryPacket:
    """Telemetry data for constitutional monitoring."""
    session_id: str
    stage: str
    timestamp: datetime
    duration_ms: float
    floor_scores: Dict[str, float]
    violations: List[str]
    verdict: str
    risk_level: str
    entropy_delta: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
            "floor_scores": self.floor_scores,
            "violations": self.violations,
            "verdict": self.verdict,
            "risk_level": self.risk_level,
            "entropy_delta": self.entropy_delta,
        }


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """Thread-safe rate limiter for AGI Room."""

    def __init__(self):
        self._lock = threading.Lock()
        self._minute_counts: Dict[str, List[float]] = defaultdict(list)
        self._session_counts: Dict[str, int] = defaultdict(int)
        self._violation_counts: Dict[str, int] = defaultdict(int)

    def check_and_increment(self, session_id: str) -> Tuple[bool, int, int]:
        """
        Check rate limit and increment counters.

        Returns:
            (allowed, queries_this_minute, queries_this_session)
        """
        now = time.time()
        minute_ago = now - 60

        with self._lock:
            # Clean old entries
            self._minute_counts[session_id] = [
                t for t in self._minute_counts[session_id] if t > minute_ago
            ]

            # Check limits
            queries_minute = len(self._minute_counts[session_id])
            queries_session = self._session_counts[session_id]

            if queries_minute >= MAX_QUERIES_PER_MINUTE:
                return False, queries_minute, queries_session

            if queries_session >= MAX_QUERIES_PER_SESSION:
                return False, queries_minute, queries_session

            # Increment
            self._minute_counts[session_id].append(now)
            self._session_counts[session_id] += 1

            return True, queries_minute + 1, queries_session + 1

    def record_violation(self, session_id: str) -> int:
        """Record a floor violation for abuse tracking."""
        with self._lock:
            self._violation_counts[session_id] += 1
            return self._violation_counts[session_id]

    def get_abuse_score(self, session_id: str) -> float:
        """Calculate abuse score based on violation rate."""
        with self._lock:
            violations = self._violation_counts[session_id]
            total = self._session_counts[session_id]
            if total == 0:
                return 0.0
            return min(1.0, violations / total)

    def cleanup_session(self, session_id: str) -> None:
        """Clean up session data."""
        with self._lock:
            self._minute_counts.pop(session_id, None)
            self._session_counts.pop(session_id, None)
            self._violation_counts.pop(session_id, None)


# Global rate limiter instance
_rate_limiter = RateLimiter()


# =============================================================================
# HIGH-STAKES DETECTION
# =============================================================================

def detect_high_stakes(query: str) -> Tuple[RiskLevel, List[str]]:
    """
    Detect if query involves high-stakes operations (class-H).

    High-stakes queries require:
    - Extra verification (multi-pass)
    - Potential 888_HOLD escalation
    - Enhanced logging

    Returns:
        (risk_level, list of triggered patterns)
    """
    query_lower = query.lower()
    triggers = []

    for pattern in HIGH_STAKES_PATTERNS:
        if re.search(pattern, query_lower):
            triggers.append(pattern)

    # Classify risk level
    if len(triggers) >= 3:
        return RiskLevel.CRITICAL, triggers
    elif len(triggers) >= 2:
        return RiskLevel.HIGH, triggers
    elif len(triggers) >= 1:
        return RiskLevel.MEDIUM, triggers
    else:
        return RiskLevel.LOW, []


# =============================================================================
# HANTU PRE-SCREENING (F9 Assist)
# =============================================================================

def detect_hantu_patterns(query: str) -> Tuple[float, List[str]]:
    """
    Pre-screen for dark cleverness patterns (Hantu).

    This assists F9 by catching patterns early in the AGI Room,
    even though F9 is officially ASI's floor.

    Hantu = "Ghost" (Malay) = Hidden malicious patterns
    - Technically correct but ethically wrong
    - Follows letter, not spirit
    - Optimizes metric, not goal

    Returns:
        (hantu_score 0-1, list of pattern names)
    """
    query_lower = query.lower()
    detected = []

    for pattern, name in HANTU_PATTERNS:
        if re.search(pattern, query_lower):
            detected.append(name)

    # Calculate score (0-1)
    if not detected:
        return 0.0, []

    # Each pattern adds 0.15 to score, capped at 1.0
    score = min(1.0, len(detected) * 0.15)

    return score, detected


# =============================================================================
# TELEMETRY HOOKS
# =============================================================================

# Telemetry callbacks
_telemetry_callbacks: List[Callable[[TelemetryPacket], None]] = []


def register_telemetry_callback(callback: Callable[[TelemetryPacket], None]) -> None:
    """Register a callback for telemetry events."""
    _telemetry_callbacks.append(callback)


def emit_telemetry(packet: TelemetryPacket) -> None:
    """Emit telemetry packet to all registered callbacks."""
    for callback in _telemetry_callbacks:
        try:
            callback(packet)
        except Exception:
            pass  # Don't let telemetry failures break the pipeline


def create_telemetry_packet(
    session_id: str,
    stage: str,
    duration_ms: float,
    floor_scores: Dict[str, float],
    violations: List[str],
    verdict: str,
    risk_level: RiskLevel,
    entropy_delta: float
) -> TelemetryPacket:
    """Create a telemetry packet for constitutional monitoring."""
    return TelemetryPacket(
        session_id=session_id,
        stage=stage,
        timestamp=datetime.utcnow(),
        duration_ms=duration_ms,
        floor_scores=floor_scores,
        violations=violations,
        verdict=verdict,
        risk_level=risk_level.value,
        entropy_delta=entropy_delta,
    )


# =============================================================================
# MAIN HARDENING CHECK
# =============================================================================

def run_pre_checks(
    query: str,
    session_id: str,
) -> HardeningResult:
    """
    Run all pre-pipeline hardening checks.

    Call this BEFORE entering the 111→222→333 pipeline.

    Args:
        query: The raw query string
        session_id: Session identifier

    Returns:
        HardeningResult with proceed=True/False
    """
    start_time = time.time()
    result = HardeningResult()

    # 1. Rate limiting
    allowed, q_min, q_sess = _rate_limiter.check_and_increment(session_id)
    result.queries_this_minute = q_min
    result.queries_this_session = q_sess

    if not allowed:
        result.rate_limited = True
        result.proceed = False
        result.block_reason = f"Rate limit exceeded: {q_min}/min or {q_sess}/session"
        result.check_duration_ms = (time.time() - start_time) * 1000
        return result

    # 2. High-stakes detection
    risk_level, triggers = detect_high_stakes(query)
    result.risk_level = risk_level
    result.high_stakes_triggers = triggers

    if risk_level == RiskLevel.CRITICAL:
        result.warnings.append("CRITICAL: Multiple high-stakes patterns detected. 888_HOLD recommended.")
    elif risk_level == RiskLevel.HIGH:
        result.warnings.append("HIGH: High-stakes query detected. Extra verification required.")

    # 3. Hantu pre-screening
    hantu_score, hantu_patterns = detect_hantu_patterns(query)
    result.hantu_score = hantu_score
    result.hantu_patterns = hantu_patterns

    if hantu_score >= 0.30:
        result.warnings.append(f"HANTU: Dark cleverness patterns detected (score={hantu_score:.2f}). ASI F9 will verify.")

    # 4. Abuse detection
    abuse_score = _rate_limiter.get_abuse_score(session_id)
    result.abuse_score = abuse_score

    if abuse_score >= ABUSE_THRESHOLD:
        result.proceed = False
        result.block_reason = f"Abuse threshold exceeded: {abuse_score:.2f}"
        result.check_duration_ms = (time.time() - start_time) * 1000
        return result

    # All checks passed
    result.check_duration_ms = (time.time() - start_time) * 1000
    return result


def run_post_checks(
    session_id: str,
    stage: str,
    floor_scores: Dict[str, float],
    violations: List[str],
    verdict: str,
    entropy_delta: float,
    duration_ms: float,
    risk_level: RiskLevel = RiskLevel.LOW,
) -> None:
    """
    Run post-pipeline hardening checks and emit telemetry.

    Call this AFTER each stage completes.
    """
    # Record violations for abuse tracking
    if violations:
        _rate_limiter.record_violation(session_id)

    # Emit telemetry
    packet = create_telemetry_packet(
        session_id=session_id,
        stage=stage,
        duration_ms=duration_ms,
        floor_scores=floor_scores,
        violations=violations,
        verdict=verdict,
        risk_level=risk_level,
        entropy_delta=entropy_delta,
    )
    emit_telemetry(packet)


def cleanup_session(session_id: str) -> None:
    """Clean up session resources."""
    _rate_limiter.cleanup_session(session_id)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "RiskLevel",
    "HardeningResult",
    "TelemetryPacket",
    "RateLimiter",
    # Functions
    "detect_high_stakes",
    "detect_hantu_patterns",
    "run_pre_checks",
    "run_post_checks",
    "cleanup_session",
    "register_telemetry_callback",
    "emit_telemetry",
    # Constants
    "HIGH_STAKES_PATTERNS",
    "HANTU_PATTERNS",
    "MAX_QUERIES_PER_MINUTE",
    "MAX_QUERIES_PER_SESSION",
    "ABUSE_THRESHOLD",
]
