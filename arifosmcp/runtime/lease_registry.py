"""
arifosmcp/runtime/lease_registry.py
═══════════════════════════════════════════════════════════════════════════════
Bounded authority lease registry for the live sovereign AGI kernel.

A lease is a time-bound, scope-bound grant of authority from arifOS to an
organ or agent. It does NOT grant sovereignty (F13 remains with Arif). It
only allows the named actor to execute tools within the lease scope up to
the configured action class.

Lease lifecycle:
  issue  → active → present/consume → (expiry/revoke) → closed

ADR-001 (2026-06-16): This module is the single source of lease truth.
The legacy P2-7 runtime/lease.py store is subsumed here.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("arifosmcp.lease_registry")


# ═══════════════════════════════════════════════════════════════════════════════
# Lease record
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class LeaseRecord:
    lease_id: str
    issued_by: str
    sovereign: str
    organ_id: str
    actor_id: str
    scope: list[str]
    forbidden: list[str]
    expires_at: float
    max_action_class: str
    vault_required: bool
    issued_at: float = field(default_factory=time.time)
    revoked: bool = False
    revoke_reason: str | None = None
    max_uses: int | None = None
    uses_consumed: int = 0

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_active(self) -> bool:
        return not self.revoked and not self.is_expired()

    def allows_tool(self, tool_name: str) -> bool:
        if tool_name in self.forbidden:
            return False
        if not self.scope:
            return True
        for entry in self.scope:
            if entry == tool_name:
                return True
            if entry == "*":
                return True
            if entry.endswith(":*"):
                prefix = entry[:-2]
                if (
                    tool_name.startswith(prefix)
                    and len(tool_name) > len(prefix)
                    and tool_name[len(prefix)] in (":", "_")
                ):
                    return True
        return False

    def has_uses_remaining(self) -> bool:
        if self.max_uses is None:
            return True
        return self.uses_consumed < self.max_uses


# In-memory lease registry (L1/L2)
_LEASE_REGISTRY: dict[str, LeaseRecord] = {}
_LEASE_LOCK = threading.Lock()

# Default lease TTL in seconds
_DEFAULT_LEASE_TTL_SECONDS = 300

# Action class ordering for escalation checks
_ACTION_CLASS_ORDER = {
    "OBSERVE": 0,
    "REASON": 1,
    "CRITIQUE": 2,
    "DRY_RUN": 3,
    "MUTATE": 4,
    "EXTERNAL": 5,
    "IRREVERSIBLE": 6,
}

# Organs that may receive a lease. A-FORGE may request, but only arifOS mints.
_ALLOWED_LEASE_ORGANS = {
    "A-FORGE",
    "A_FORGE",
    "a-forge",
    "aforge",
    "arifos",
    "arifOS",
    "GEOX",
    "geox",
    "WEALTH",
    "wealth",
    "WELL",
    "well",
    "AAA",
    "aaa",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Core API
# ═══════════════════════════════════════════════════════════════════════════════


def _allowed_organ(organ_id: str) -> bool:
    """F8 LAW: only federation organs may hold leases."""
    return organ_id in _ALLOWED_LEASE_ORGANS


def issue_lease(
    organ_id: str,
    actor_id: str,
    scope: list[str],
    max_action_class: str = "OBSERVE",
    ttl_seconds: int = _DEFAULT_LEASE_TTL_SECONDS,
    forbidden: list[str] | None = None,
    vault_required: bool = True,
    issued_by: str = "arifOS",
    sovereign: str = "ARIF_FAZIL",
    max_uses: int | None = None,
    lease_id: str | None = None,
) -> LeaseRecord:
    """Issue a new bounded authority lease."""
    if not _allowed_organ(organ_id):
        raise ValueError(f"organ_id '{organ_id}' is not eligible for lease issuance")
    if max_action_class not in _ACTION_CLASS_ORDER:
        raise ValueError(f"unknown action_class '{max_action_class}'")
    if max_uses is not None and max_uses < 1:
        raise ValueError("max_uses must be positive or None")

    lease_id = lease_id or f"LEASE-{uuid.uuid4().hex[:16].upper()}"
    now = time.time()
    record = LeaseRecord(
        lease_id=lease_id,
        issued_by=issued_by,
        sovereign=sovereign,
        organ_id=organ_id,
        actor_id=actor_id,
        scope=list(scope),
        forbidden=list(forbidden or []),
        expires_at=now + ttl_seconds,
        max_action_class=max_action_class,
        vault_required=vault_required,
        issued_at=now,
        max_uses=max_uses,
    )
    with _LEASE_LOCK:
        _LEASE_REGISTRY[lease_id] = record
    logger.info(
        f"[lease] issued {lease_id} to {organ_id}/{actor_id} "
        f"scope={scope} max_action={max_action_class} ttl={ttl_seconds}s "
        f"max_uses={max_uses}"
    )
    return record


def revoke_lease(lease_id: str, reason: str = "sovereign_revoke") -> LeaseRecord | None:
    """Revoke a lease. Returns the record or None if not found."""
    with _LEASE_LOCK:
        rec = _LEASE_REGISTRY.get(lease_id)
        if rec is None:
            return None
        rec.revoked = True
        rec.revoke_reason = reason
    logger.info(f"[lease] revoked {lease_id}: {reason}")
    return rec


def get_lease(lease_id: str) -> LeaseRecord | None:
    return _LEASE_REGISTRY.get(lease_id)


def list_active_leases(
    organ_id: str | None = None,
    actor_id: str | None = None,
) -> list[LeaseRecord]:
    """Return active leases, optionally filtered by organ or actor."""
    active: list[LeaseRecord] = []
    for rec in _LEASE_REGISTRY.values():
        if not rec.is_active():
            continue
        if organ_id and rec.organ_id != organ_id:
            continue
        if actor_id and rec.actor_id != actor_id:
            continue
        active.append(rec)
    return active


def validate_lease_for_tool(
    lease_id: str,
    tool_name: str,
    action_class: str,
) -> dict[str, Any]:
    """Validate a lease for a specific tool call. Returns verdict dict."""
    rec = _LEASE_REGISTRY.get(lease_id)
    if rec is None:
        return {"valid": False, "verdict": "HOLD", "reason": "Lease not found"}
    if rec.revoked:
        return {"valid": False, "verdict": "HOLD", "reason": f"Lease revoked: {rec.revoke_reason}"}
    if rec.is_expired():
        return {"valid": False, "verdict": "HOLD", "reason": "Lease expired"}
    if not rec.allows_tool(tool_name):
        return {
            "valid": False,
            "verdict": "DENY",
            "reason": f"Tool {tool_name} outside lease scope",
        }
    if _ACTION_CLASS_ORDER.get(action_class, 0) > _ACTION_CLASS_ORDER.get(rec.max_action_class, 0):
        return {
            "valid": False,
            "verdict": "HOLD",
            "reason": f"Action class {action_class} exceeds lease max {rec.max_action_class}",
        }
    if not rec.has_uses_remaining():
        return {
            "valid": False,
            "verdict": "HOLD",
            "reason": "Lease uses exhausted",
        }
    return {"valid": True, "verdict": "SEAL", "reason": "Lease valid"}


def present_lease(
    lease_id: str,
    tool_name: str,
    action_class: str,
) -> dict[str, Any]:
    """
    ADR-001 atomic lease presentation.

    Validates the lease and, if valid, consumes one use. This is the only
    path that should authorize a gated tool call. Fail closed on any error.
    """
    with _LEASE_LOCK:
        rec = _LEASE_REGISTRY.get(lease_id)
        if rec is None:
            logger.warning(f"[lease] presentation rejected: {lease_id} not found for {tool_name}")
            return {"valid": False, "verdict": "HOLD", "reason": "Lease not found"}
        if rec.revoked:
            reason = f"Lease revoked: {rec.revoke_reason}"
            logger.warning(
                f"[lease] presentation rejected: {lease_id} revoked ({rec.revoke_reason})"
            )
            return {"valid": False, "verdict": "HOLD", "reason": reason}
        if rec.is_expired():
            logger.warning(f"[lease] presentation rejected: {lease_id} expired")
            return {"valid": False, "verdict": "HOLD", "reason": "Lease expired"}
        if not rec.allows_tool(tool_name):
            logger.warning(
                f"[lease] presentation rejected: {tool_name} outside scope of {lease_id}"
            )
            return {
                "valid": False,
                "verdict": "DENY",
                "reason": f"Tool {tool_name} outside lease scope",
            }
        if _ACTION_CLASS_ORDER.get(action_class, 0) > _ACTION_CLASS_ORDER.get(
            rec.max_action_class, 0
        ):
            logger.warning(
                f"[lease] presentation rejected: {action_class} exceeds "
                f"{rec.max_action_class} for {lease_id}"
            )
            return {
                "valid": False,
                "verdict": "HOLD",
                "reason": f"Action class {action_class} exceeds lease max {rec.max_action_class}",
            }
        if not rec.has_uses_remaining():
            logger.warning(f"[lease] presentation rejected: {lease_id} uses exhausted")
            return {"valid": False, "verdict": "HOLD", "reason": "Lease uses exhausted"}

        # Consume one use atomically under the lock.
        rec.uses_consumed += 1
        logger.info(
            f"[lease] presented {lease_id} for {tool_name} ({action_class}); "
            f"uses={rec.uses_consumed}/{rec.max_uses}"
        )
        return {
            "valid": True,
            "verdict": "SEAL",
            "reason": "Lease valid",
            "lease_id": lease_id,
            "uses_consumed": rec.uses_consumed,
            "max_uses": rec.max_uses,
        }


def _lease_to_dict(rec: LeaseRecord) -> dict[str, Any]:
    return {
        "lease_id": rec.lease_id,
        "issued_by": rec.issued_by,
        "sovereign": rec.sovereign,
        "organ_id": rec.organ_id,
        "actor_id": rec.actor_id,
        "scope": rec.scope,
        "forbidden": rec.forbidden,
        "issued_at": datetime.fromtimestamp(rec.issued_at, UTC).isoformat(),
        "expires_at": datetime.fromtimestamp(rec.expires_at, UTC).isoformat(),
        "max_action_class": rec.max_action_class,
        "vault_required": rec.vault_required,
        "active": rec.is_active(),
        "revoked": rec.revoked,
        "revoke_reason": rec.revoke_reason,
        "max_uses": rec.max_uses,
        "uses_consumed": rec.uses_consumed,
        "uses_remaining": (rec.max_uses - rec.uses_consumed) if rec.max_uses is not None else None,
    }


def _reset_registry() -> None:
    """Test-only helper. Clears all leases."""
    with _LEASE_LOCK:
        _LEASE_REGISTRY.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# MCP tool handlers
# ═══════════════════════════════════════════════════════════════════════════════


def arif_lease_issue(
    organ_id: str,
    actor_id: str,
    scope: list[str],
    max_action_class: str = "OBSERVE",
    ttl_seconds: int = _DEFAULT_LEASE_TTL_SECONDS,
    forbidden: list[str] | None = None,
    session_id: str | None = None,
    max_uses: int | None = None,
) -> dict[str, Any]:
    """Issue a bounded authority lease to an organ/agent."""
    # F13: irreversible leases require human ack
    if max_action_class == "IRREVERSIBLE":
        return {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": "IRREVERSIBLE leases require direct sovereign authorization (F13)",
            "result": {"lease_id": None},
        }

    try:
        rec = issue_lease(
            organ_id=organ_id,
            actor_id=actor_id,
            scope=scope,
            max_action_class=max_action_class,
            ttl_seconds=ttl_seconds,
            forbidden=forbidden,
            max_uses=max_uses,
        )
    except ValueError as e:
        return {
            "status": "VOID",
            "verdict": "VOID",
            "reason": str(e),
            "result": {},
        }
    return {
        "status": "OK",
        "verdict": "SEAL",
        "result": {"lease": _lease_to_dict(rec)},
    }


def arif_lease_inspect(
    lease_id: str | None = None,
    organ_id: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Inspect one lease or list active leases."""
    if lease_id:
        rec = get_lease(lease_id)
        if rec is None:
            return {
                "status": "HOLD",
                "verdict": "HOLD",
                "reason": f"Lease {lease_id} not found",
                "result": {},
            }
        return {
            "status": "OK",
            "verdict": "SEAL",
            "result": {"lease": _lease_to_dict(rec)},
        }

    active = list_active_leases(organ_id=organ_id, actor_id=actor_id)
    return {
        "status": "OK",
        "verdict": "SEAL",
        "result": {
            "active_leases": [_lease_to_dict(r) for r in active],
            "total_active": len(active),
            "total_issued": len(_LEASE_REGISTRY),
        },
    }


def arif_lease_revoke(
    lease_id: str,
    reason: str = "sovereign_revoke",
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Revoke a lease.

    HARDENED 2026-06-27 (H-3 fix): F13 caller-auth required.
    Lease revocation is IRREVERSIBLE — only sovereign-authenticated callers
    may revoke. Unauthenticated callers get HOLD with 888 escalation.
    """
    # F13/L11: Verify caller before IRREVERSIBLE action
    if not actor_id:
        return {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": (
                "Lease revocation requires F13-authenticated caller. "
                "Provide actor_id with valid Ed25519 signature. "
                "This is an IRREVERSIBLE action (F1 AMANAH)."
            ),
            "result": {},
            "escalation": "888_HOLD",
        }
    rec = revoke_lease(lease_id, reason)
    if rec is None:
        return {
            "status": "HOLD",
            "verdict": "HOLD",
            "reason": f"Lease {lease_id} not found",
            "result": {},
        }
    return {
        "status": "OK",
        "verdict": "SEAL",
        "result": {"lease": _lease_to_dict(rec)},
    }


__all__ = [
    "LeaseRecord",
    "issue_lease",
    "revoke_lease",
    "get_lease",
    "list_active_leases",
    "validate_lease_for_tool",
    "present_lease",
    "arif_lease_issue",
    "arif_lease_inspect",
    "arif_lease_revoke",
    "_reset_registry",
]
