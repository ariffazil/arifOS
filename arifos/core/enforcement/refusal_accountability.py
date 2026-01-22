"""
arifOS v45xx - Refusal Accountability

Implements transparent, auditable refusals with clear reason codes.
Every VOID verdict is explainable and logged with constitutional rationale.

Usage:
    from arifos.core.enforcement.refusal_accountability import (
        get_refusal_reason_code,
        format_refusal_message,
        track_refusal,
        check_escalation_needed,
    )
"""

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION LOADING
# =============================================================================

_REFUSAL_POLICY_CACHE: Optional[Dict] = None


def _load_refusal_policy() -> Dict:
    """Load Refusal Accountability policy from spec/v45/policy_refusal.json."""
    global _REFUSAL_POLICY_CACHE
    if _REFUSAL_POLICY_CACHE is not None:
        return _REFUSAL_POLICY_CACHE

    spec_paths = [
        Path(__file__).parent.parent.parent / "spec" / "v45" / "policy_refusal.json",
        Path("spec/v45/policy_refusal.json"),
    ]

    for path in spec_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    _REFUSAL_POLICY_CACHE = json.load(f)
                    return _REFUSAL_POLICY_CACHE
            except Exception as e:
                logger.warning(f"Failed to load Refusal policy from {path}: {e}")

    # Default policy
    _REFUSAL_POLICY_CACHE = {
        "refusal_accountability": {
            "enabled": True,
            "reason_codes": {
                "F1": {"code": "F1_AMANAH", "display": "Trust/Harm Violation"},
                "F5": {"code": "F5_PEACE_SQUARED", "display": "Peace² Violation"},
                "F9": {"code": "F9_ANTI_HANTU", "display": "Anti-Hantu Violation"},
                "SAFETY": {"code": "SAFETY_REFUSAL", "display": "Safety Policy"},
            },
            "escalation": {
                "max_repeated_refusals": 3,
                "escalation_verdict": "HOLD_888",
            },
        },
    }
    return _REFUSAL_POLICY_CACHE


def is_refusal_accountability_enabled() -> bool:
    """Check if Refusal Accountability is enabled."""
    env_enabled = os.getenv("ARIFOS_REFUSAL_ACCOUNTABILITY_ENABLED", "").lower() in ("1", "true", "yes")
    if env_enabled:
        return True

    policy = _load_refusal_policy()
    return policy.get("refusal_accountability", {}).get("enabled", False)


# =============================================================================
# REFUSAL TRACKING (In-Memory Session State)
# =============================================================================

# Session-based refusal tracking (in production, use Redis or similar)
_REFUSAL_TRACKER: Dict[str, List[Dict]] = {}


@dataclass
class RefusalRecord:
    """Record of a single refusal event."""

    timestamp: float
    query_hash: str
    reason_code: str
    floor_violations: List[str]
    verdict: str = "VOID"

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "query_hash": self.query_hash,
            "reason_code": self.reason_code,
            "floor_violations": self.floor_violations,
            "verdict": self.verdict,
        }


def _hash_query(query: str) -> str:
    """Create a hash of the query for tracking without storing full text."""
    return hashlib.sha256(query.encode()).hexdigest()[:16]


def track_refusal(
    session_id: str,
    query: str,
    reason_code: str,
    floor_violations: List[str],
    verdict: str = "VOID",
) -> None:
    """
    Track a refusal for escalation detection.

    Args:
        session_id: User/session identifier
        query: Original query (will be hashed)
        reason_code: Primary reason code
        floor_violations: List of floor violation strings
        verdict: Verdict type (VOID, SABAR, etc.)
    """
    if not is_refusal_accountability_enabled():
        return

    record = RefusalRecord(
        timestamp=time.time(),
        query_hash=_hash_query(query),
        reason_code=reason_code,
        floor_violations=floor_violations,
        verdict=verdict,
    )

    if session_id not in _REFUSAL_TRACKER:
        _REFUSAL_TRACKER[session_id] = []

    _REFUSAL_TRACKER[session_id].append(record.to_dict())

    # Prune old entries (keep last 30 minutes)
    policy = _load_refusal_policy()
    window_minutes = policy.get("refusal_accountability", {}).get("escalation", {}).get("track_window_minutes", 30)
    cutoff = time.time() - (window_minutes * 60)
    _REFUSAL_TRACKER[session_id] = [
        r for r in _REFUSAL_TRACKER[session_id]
        if r["timestamp"] > cutoff
    ]

    logger.info(f"REFUSAL_TRACKED: session={session_id}, code={reason_code}, violations={floor_violations}")


def get_refusal_count(session_id: str) -> int:
    """Get count of recent refusals for a session."""
    if session_id not in _REFUSAL_TRACKER:
        return 0
    return len(_REFUSAL_TRACKER[session_id])


def check_escalation_needed(session_id: str) -> bool:
    """
    Check if escalation is needed due to repeated refusals.

    Args:
        session_id: User/session identifier

    Returns:
        True if refusal count >= max_repeated_refusals threshold
    """
    policy = _load_refusal_policy()
    max_refusals = policy.get("refusal_accountability", {}).get("escalation", {}).get("max_repeated_refusals", 3)

    count = get_refusal_count(session_id)
    return count >= max_refusals


def clear_refusal_history(session_id: str) -> None:
    """Clear refusal history for a session (called on successful response)."""
    policy = _load_refusal_policy()
    if policy.get("refusal_accountability", {}).get("escalation", {}).get("reset_after_success", True):
        if session_id in _REFUSAL_TRACKER:
            del _REFUSAL_TRACKER[session_id]


# =============================================================================
# REASON CODE MAPPING
# =============================================================================


def get_refusal_reason_code(floor_failures: List[str]) -> str:
    """
    Get the primary reason code from floor failures.

    Uses priority order: F1 > F5 > F9 > SAFETY > other

    Args:
        floor_failures: List of floor failure strings

    Returns:
        Primary reason code (e.g., "F1_AMANAH")
    """
    policy = _load_refusal_policy()
    reason_codes = policy.get("refusal_accountability", {}).get("reason_codes", {})

    # Priority order for reason selection
    priority_order = ["F1", "F5", "F9", "DESTRUCTIVE", "SAFETY", "F2", "F3", "F4", "F6", "F7", "F8"]

    failures_lower = " ".join(floor_failures).lower()

    for floor_key in priority_order:
        if floor_key.lower() in failures_lower:
            code_info = reason_codes.get(floor_key, {})
            return code_info.get("code", f"{floor_key}_VIOLATION")

    # Check for specific keywords
    if "destructive" in failures_lower:
        return reason_codes.get("DESTRUCTIVE", {}).get("code", "DESTRUCTIVE_INTENT")
    if "safety" in failures_lower or "refuse" in failures_lower:
        return reason_codes.get("SAFETY", {}).get("code", "SAFETY_REFUSAL")

    return "CONSTITUTIONAL_VIOLATION"


def get_refusal_display_reason(reason_code: str) -> str:
    """Get human-readable display text for a reason code."""
    policy = _load_refusal_policy()
    reason_codes = policy.get("refusal_accountability", {}).get("reason_codes", {})

    for floor_key, code_info in reason_codes.items():
        if code_info.get("code") == reason_code:
            return code_info.get("display", reason_code)

    return reason_code.replace("_", " ").title()


def get_guidance_for_reason(reason_code: str) -> str:
    """Get guidance text for a reason code."""
    policy = _load_refusal_policy()
    guidance = policy.get("guidance_templates", {})

    # Try exact match first
    if reason_code in guidance:
        return guidance[reason_code]

    # Try floor prefix match
    for key, text in guidance.items():
        if reason_code.startswith(key.split("_")[0]):
            return text

    return "Please consider rephrasing your request."


# =============================================================================
# MESSAGE FORMATTING
# =============================================================================


def format_refusal_message(
    floor_failures: List[str],
    include_reason: bool = True,
    include_guidance: bool = True,
    is_escalation: bool = False,
) -> str:
    """
    Format a refusal message with reason and guidance.

    Args:
        floor_failures: List of floor failure strings
        include_reason: Whether to include reason in message
        include_guidance: Whether to include guidance
        is_escalation: Whether this is an escalation scenario

    Returns:
        Formatted refusal message
    """
    policy = _load_refusal_policy()
    user_messages = policy.get("user_messages", {})
    notification = policy.get("refusal_accountability", {}).get("user_notification", {})

    reason_code = get_refusal_reason_code(floor_failures)
    display_reason = get_refusal_display_reason(reason_code)
    guidance = get_guidance_for_reason(reason_code)

    # Check notification settings
    should_include_reason = include_reason and notification.get("notify_user_reason", True)
    should_include_guidance = include_guidance and notification.get("include_guidance", True)

    if is_escalation:
        base = user_messages.get("escalation_notice",
            "Multiple similar requests have been declined. A human review may be required.")
        return base

    if should_include_reason and should_include_guidance:
        template = user_messages.get("with_guidance",
            "I cannot assist with that request ({reason}). {guidance}")
        return template.format(reason=display_reason, guidance=guidance)
    elif should_include_reason:
        template = user_messages.get("with_reason",
            "I cannot assist with that request ({reason}).")
        return template.format(reason=display_reason)
    else:
        return user_messages.get("general_refusal", "I cannot assist with that request.")


# =============================================================================
# AUDIT LOGGING
# =============================================================================


@dataclass
class RefusalAuditEntry:
    """Audit entry for a refusal."""

    timestamp: float
    session_id: str
    query_hash: str
    reason_code: str
    floor_violations: List[str]
    verdict: str
    escalation_triggered: bool = False

    def to_dict(self) -> Dict:
        return {
            "type": "REFUSAL",
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "query_hash": self.query_hash,
            "reason_code": self.reason_code,
            "floor_violations": self.floor_violations,
            "verdict": self.verdict,
            "escalation_triggered": self.escalation_triggered,
        }


def create_refusal_audit_entry(
    session_id: str,
    query: str,
    floor_failures: List[str],
    verdict: str = "VOID",
) -> RefusalAuditEntry:
    """
    Create an audit entry for a refusal.

    Args:
        session_id: Session identifier
        query: Original query
        floor_failures: Floor violations
        verdict: Final verdict

    Returns:
        RefusalAuditEntry for logging
    """
    reason_code = get_refusal_reason_code(floor_failures)
    escalation = check_escalation_needed(session_id)

    return RefusalAuditEntry(
        timestamp=time.time(),
        session_id=session_id,
        query_hash=_hash_query(query),
        reason_code=reason_code,
        floor_violations=floor_failures,
        verdict=verdict,
        escalation_triggered=escalation,
    )


def log_refusal(
    session_id: str,
    query: str,
    floor_failures: List[str],
    verdict: str = "VOID",
) -> RefusalAuditEntry:
    """
    Log a refusal with full audit trail.

    Args:
        session_id: Session identifier
        query: Query text
        floor_failures: Floor violations
        verdict: Final verdict

    Returns:
        The audit entry created
    """
    if not is_refusal_accountability_enabled():
        return None

    # Track for escalation
    reason_code = get_refusal_reason_code(floor_failures)
    track_refusal(session_id, query, reason_code, floor_failures, verdict)

    # Create audit entry
    entry = create_refusal_audit_entry(session_id, query, floor_failures, verdict)

    # Log to standard logger
    logger.info(f"REFUSAL_AUDIT: {json.dumps(entry.to_dict())}")

    return entry
