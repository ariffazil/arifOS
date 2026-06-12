"""
arifosmcp/runtime/lease_registry.py
═══════════════════════════════════════════════════════════════════════════════
Bounded authority lease registry for the live sovereign AGI kernel.

A lease is a time-bound, scope-bound grant of authority from arifOS to an
organ or agent. It does NOT grant sovereignty (F13 remains with Arif). It
only allows the named actor to execute tools within the lease scope up to
the configured action class.

Lease lifecycle:
  issue  → active → (expiry/revoke) → closed

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import logging
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

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_active(self) -> bool:
        return not self.revoked and not self.is_expired()

    def allows_tool(self, tool_name: str) -> bool:
        if tool_name in self.forbidden:
            return False
        if not self.scope:
            return True
        # Scope entries can be exact tool names or prefixes like "GEOX:*"
        for entry in self.scope:
            if entry == tool_name:
                return True
            if entry.endswith(":*") and tool_name.startswith(entry[:-1]):
                return True
        return False


# In-memory lease registry (L1/L2)
_LEASE_REGISTRY: dict[str, LeaseRecord] = {}

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


# ═══════════════════════════════════════════════════════════════════════════════
# Core API
# ═══════════════════════════════════════════════════════════════════════════════


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
) -> LeaseRecord:
    """Issue a new bounded authority lease."""
    lease_id = f"LEASE-{uuid.uuid4().hex[:16].upper()}"
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
    )
    _LEASE_REGISTRY[lease_id] = record
    logger.info(
        f"[lease] issued {lease_id} to {organ_id}/{actor_id} "
        f"scope={scope} max_action={max_action_class} ttl={ttl_seconds}s"
    )
    return record


def revoke_lease(lease_id: str, reason: str = "sovereign_revoke") -> LeaseRecord | None:
    """Revoke a lease. Returns the record or None if not found."""
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
    return {"valid": True, "verdict": "SEAL", "reason": "Lease valid"}


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
    }


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

    rec = issue_lease(
        organ_id=organ_id,
        actor_id=actor_id,
        scope=scope,
        max_action_class=max_action_class,
        ttl_seconds=ttl_seconds,
        forbidden=forbidden,
    )
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
    """Revoke a lease."""
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
    "arif_lease_issue",
    "arif_lease_inspect",
    "arif_lease_revoke",
]
