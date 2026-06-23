"""
arifosmcp/schemas/authority_registry.py — Canonical Authority Registry
=======================================================================

Single source of truth for "who can do what" in the arifOS federation.

APEX AUTHORITY dimension: every transition must be signed by the right principal.
This registry defines the mapping from authority source → allowed action classes.

A-FORGE and AAA query this registry. arifOS owns it.

Constitutional binding:
  F11 AUTH      — identity must be verified before sensitive ops
  F13 SOVEREIGN — human veto is absolute; no agent may self-authorize

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AuthorityLevel(str, Enum):
    """Canonical authority levels. Lower = less authority."""

    OBSERVER = "OBSERVER"  # Read-only, no mutations
    OPERATOR_CLAIMED = "OPERATOR_CLAIMED"  # Claimed identity, not verified
    HMAC_VERIFIED = "HMAC_VERIFIED"  # Telegram HMAC verification
    SOVEREIGN = "SOVEREIGN"  # Ed25519 sovereign signature
    SYSTEM = "SYSTEM"  # System/cron/daemon
    JUDGE = "JUDGE"  # 888_JUDGE deliberation
    ORGAN = "ORGAN"  # Federation organ attestation


# Authority level hierarchy (higher index = more authority)
_AUTHORITY_HIERARCHY: list[str] = [
    AuthorityLevel.OBSERVER,
    AuthorityLevel.OPERATOR_CLAIMED,
    AuthorityLevel.HMAC_VERIFIED,
    AuthorityLevel.SYSTEM,
    AuthorityLevel.ORGAN,
    AuthorityLevel.JUDGE,
    AuthorityLevel.SOVEREIGN,
]


class ActionClass(str, Enum):
    """7-tier action taxonomy (from A-FORGE actionClassifier.ts)."""

    OBSERVE = "OBSERVE"
    SUGGEST = "SUGGEST"
    SIMULATE = "SIMULATE"
    DRAFT = "DRAFT"
    QUEUE = "QUEUE"
    EXECUTE_REVERSIBLE = "EXECUTE_REVERSIBLE"
    EXECUTE_HIGH_IMPACT = "EXECUTE_HIGH_IMPACT"
    IRREVERSIBLE = "IRREVERSIBLE"


# What each authority level is allowed to do
_AUTHORITY_PERMISSIONS: dict[str, list[str]] = {
    AuthorityLevel.OBSERVER: [
        ActionClass.OBSERVE,
    ],
    AuthorityLevel.OPERATOR_CLAIMED: [
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
    ],
    AuthorityLevel.HMAC_VERIFIED: [
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
        ActionClass.DRAFT,
        ActionClass.QUEUE,
    ],
    AuthorityLevel.SYSTEM: [
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
        ActionClass.DRAFT,
        ActionClass.QUEUE,
        ActionClass.EXECUTE_REVERSIBLE,
    ],
    AuthorityLevel.ORGAN: [
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
        ActionClass.DRAFT,
        ActionClass.QUEUE,
        ActionClass.EXECUTE_REVERSIBLE,
    ],
    AuthorityLevel.JUDGE: [
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
        ActionClass.DRAFT,
        ActionClass.QUEUE,
        ActionClass.EXECUTE_REVERSIBLE,
        ActionClass.EXECUTE_HIGH_IMPACT,
    ],
    AuthorityLevel.SOVEREIGN: [
        # All actions
        ActionClass.OBSERVE,
        ActionClass.SUGGEST,
        ActionClass.SIMULATE,
        ActionClass.DRAFT,
        ActionClass.QUEUE,
        ActionClass.EXECUTE_REVERSIBLE,
        ActionClass.EXECUTE_HIGH_IMPACT,
        ActionClass.IRREVERSIBLE,
    ],
}


class AuthorityCheckResult(BaseModel):
    """Result of an authority check."""

    allowed: bool = Field(description="Whether the action is permitted")
    authority_level: str = Field(description="The authority level of the caller")
    action_class: str = Field(description="The requested action class")
    reason: str = Field(default="", description="Why the check passed or failed")
    requires_escalation: bool = Field(
        default=False, description="True if this requires 888_HOLD or sovereign approval"
    )


def check_authority(
    authority_level: str,
    action_class: str,
) -> AuthorityCheckResult:
    """
    Check if an authority level is permitted to perform an action class.

    This is the single canonical authority check for the federation.
    A-FORGE and AAA should call this (or query the registry) before execution.

    Args:
        authority_level: The caller's authority level (from session init)
        action_class: The requested action class

    Returns:
        AuthorityCheckResult with allowed=True/False and reason
    """
    # Normalize
    auth = authority_level.strip().upper()
    action = action_class.strip().upper()

    # Unknown authority → deny
    if auth not in [e.value for e in AuthorityLevel]:
        return AuthorityCheckResult(
            allowed=False,
            authority_level=auth,
            action_class=action,
            reason=f"Unknown authority level: {auth}",
            requires_escalation=True,
        )

    # Unknown action class → deny
    if action not in [e.value for e in ActionClass]:
        return AuthorityCheckResult(
            allowed=False,
            authority_level=auth,
            action_class=action,
            reason=f"Unknown action class: {action}",
            requires_escalation=True,
        )

    # Check permission
    allowed_actions = _AUTHORITY_PERMISSIONS.get(auth, [])
    if action in allowed_actions:
        return AuthorityCheckResult(
            allowed=True,
            authority_level=auth,
            action_class=action,
            reason=f"{auth} is permitted to perform {action}",
        )

    # Not permitted — check if escalation would help
    _escalation_map = {
        ActionClass.EXECUTE_HIGH_IMPACT: "Requires JUDGE authority (888 deliberation)",
        ActionClass.IRREVERSIBLE: "Requires SOVEREIGN authority (F13 human approval)",
    }
    escalation_reason = _escalation_map.get(ActionClass(action), f"{auth} cannot perform {action}")

    return AuthorityCheckResult(
        allowed=False,
        authority_level=auth,
        action_class=action,
        reason=escalation_reason,
        requires_escalation=True,
    )


def get_authority_permissions(authority_level: str) -> list[str]:
    """Return the list of allowed action classes for an authority level."""
    return _AUTHORITY_PERMISSIONS.get(authority_level.strip().upper(), [])


def get_authority_hierarchy() -> list[str]:
    """Return the authority hierarchy from lowest to highest."""
    return list(_AUTHORITY_HIERARCHY)
