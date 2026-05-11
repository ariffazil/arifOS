"""Pure governance functions — no side effects, no secrets, no irreversible actions.

Implements the constitutional risk classification layer for arifOS Command Center.
All functions are deterministic and safe to call from any context.
"""

from __future__ import annotations

import hashlib
import re

# Dangerous keywords that must never pass with SEAL.
DANGEROUS_KEYWORDS: set[str] = {
    "delete",
    "deploy",
    "transfer",
    "execute",
    "production",
    "irreversible",
    "credentials",
    "secret",
    "private key",
    "exfiltrate",
    "bypass",
    "drop",
    "truncate",
    "rm -rf",
    "docker system prune",
    "mkfs",
    "dd if=",
    "format",
    "wipe",
    "destroy",
}

# Medium-risk keywords that warrant SABAR (conditional) rather than HOLD.
MEDIUM_KEYWORDS: set[str] = {
    "install",
    "update",
    "upgrade",
    "push",
    "merge",
    "commit",
    "build",
    "restart",
    "stop",
    "kill",
    "patch",
}


def classify_risk(text: str) -> str:
    """Classify a candidate action string into a risk tier.

    Returns one of: low, medium, high, critical.
    Unknown or empty input defaults to high (fail-closed).
    Very long inputs default to medium (fail-closed for ambiguity).
    """
    if not text or not isinstance(text, str):
        return "high"

    # Fail-closed on oversized input (red-team hardening)
    if len(text) > 5000:
        return "medium"

    lowered = text.lower()

    # Critical: explicit irreversible or dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in lowered:
            return "critical"

    # High: patterns that strongly imply production impact
    high_patterns = [
        r"\bdrop\b",
        r"\bdelete\b",
        r"\bremove\b.*\bpermanent",
        r"\bwrite\b.*\bproduction",
        r"\bexec\b",
    ]
    for pattern in high_patterns:
        if re.search(pattern, lowered):
            return "high"

    # Medium: maintenance-style keywords
    for keyword in MEDIUM_KEYWORDS:
        if keyword in lowered:
            return "medium"

    return "low"


def requires_human_decision(risk_tier: str) -> bool:
    """Return whether a given risk tier requires explicit human decision.

    high and critical always require human decision.
    medium requires human decision for v0.1 (conservative).
    low does not.
    """
    if not isinstance(risk_tier, str):
        return True
    return risk_tier in {"high", "critical", "medium"}


def judge_candidate(candidate: str) -> dict:
    """Render a constitutional verdict for a candidate action.

    This is a pure function. It does not execute, store, or transmit anything.
    """
    if not candidate or not isinstance(candidate, str):
        return {
            "verdict": "HOLD",
            "risk_tier": "high",
            "human_decision_required": True,
            "reason": "Empty or invalid candidate. Failing closed to HOLD per F1 Amanah.",
            "allowed_next": [],
            "forbidden_next": ["forge_execute", "forge_dry_run"],
        }

    risk_tier = classify_risk(candidate)
    human_required = requires_human_decision(risk_tier)

    if risk_tier == "critical":
        return {
            "verdict": "HOLD",
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "reason": (
                "Candidate contains dangerous or irreversible keywords. "
                "Blocked by F1 Amanah. Human review mandatory."
            ),
            "allowed_next": [],
            "forbidden_next": ["forge_execute", "forge_dry_run", "vault_seal"],
        }

    if risk_tier == "high":
        return {
            "verdict": "SABAR",
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "reason": (
                "High-risk candidate detected. Conditional pause (SABAR) "
                "applied. Requires explicit SEAL from human judge before any action."
            ),
            "allowed_next": [],
            "forbidden_next": ["forge_execute", "vault_seal"],
        }

    if risk_tier == "medium":
        return {
            "verdict": "SABAR",
            "risk_tier": risk_tier,
            "human_decision_required": human_required,
            "reason": (
                "Medium-risk candidate. Allowed only for supervised dry-run "
                "after human acknowledgment."
            ),
            "allowed_next": ["forge_dry_run"],
            "forbidden_next": ["forge_execute", "vault_seal"],
        }

    # low risk
    return {
        "verdict": "SEAL",
        "risk_tier": risk_tier,
        "human_decision_required": human_required,
        "reason": (
            "Low-risk, reversible candidate. SEAL granted for dry-run only. "
            "v0.1 does not permit real execution."
        ),
        "allowed_next": ["forge_dry_run"],
        "forbidden_next": ["forge_execute", "vault_seal"],
    }


def hash_preview(payload: str, length: int = 16) -> str:
    """Return a deterministic short hash preview of a payload.

    Never returns the full hash to avoid leaking length or content.
    """
    if not isinstance(payload, str):
        payload = str(payload)
    full_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return full_hash[:length]
