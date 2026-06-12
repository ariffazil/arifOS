"""Lease Engine — issue, check, expire, 888_HOLD.

Every MCP tool call must pass through a lease decision that knows:
  actor, tool, blast radius, reversibility, max invocations, TTL.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LeaseRecord:
    lease_id: str
    subject: str
    tool: str
    roles: list[str] = field(default_factory=list)
    risk_class: str = "LOW"
    reversibility: str = "FULL"
    max_invocations: int = 100
    invocations_used: int = 0
    ttl_seconds: int = 3600
    issued_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    require_888_hold: bool = False
    granted_by: str = "policy"
    audit_chain: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.expires_at == 0.0:
            self.expires_at = self.issued_at + self.ttl_seconds

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def exhausted(self) -> bool:
        return self.invocations_used >= self.max_invocations

    @property
    def valid(self) -> bool:
        return not self.expired and not self.exhausted

    def consume(self) -> bool:
        if not self.valid:
            return False
        self.invocations_used += 1
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "subject": self.subject,
            "tool": self.tool,
            "risk_class": self.risk_class,
            "reversibility": self.reversibility,
            "invocations_used": self.invocations_used,
            "max_invocations": self.max_invocations,
            "expires_at": self.expires_at,
            "expired": self.expired,
            "valid": self.valid,
            "require_888_hold": self.require_888_hold,
        }


@dataclass
class LeaseDecision:
    lease_id: str
    allowed: bool
    held: bool
    reason: str = ""
    risk_class: str = "LOW"
    reversibility: str = "FULL"


class LeaseEngine:
    """In-memory lease registry with TTL, invocation caps, and 888_HOLD gating.

    v0.1: in-memory only. v0.2+: Postgres-backed for persistence.
    """

    def __init__(self) -> None:
        self._leases: dict[str, LeaseRecord] = {}
        self._pending_approvals: dict[str, LeaseRecord] = {}

    def issue(
        self,
        subject: str,
        tool: str,
        roles: list[str] | None = None,
        risk_class: str = "LOW",
        reversibility: str = "FULL",
        max_invocations: int = 100,
        ttl_seconds: int = 3600,
        require_888_hold: bool = False,
        granted_by: str = "policy",
    ) -> LeaseRecord:
        """Issue a new lease for subject+tool."""
        lease = LeaseRecord(
            lease_id=f"LEASE-{uuid.uuid4().hex[:12].upper()}",
            subject=subject,
            tool=tool,
            roles=roles or [],
            risk_class=risk_class,
            reversibility=reversibility,
            max_invocations=max_invocations,
            ttl_seconds=ttl_seconds,
            require_888_hold=require_888_hold,
            granted_by=granted_by,
        )
        self._leases[lease.lease_id] = lease
        return lease

    def lookup(self, subject: str, tool: str) -> LeaseRecord | None:
        """Find an existing valid lease for subject+tool."""
        now = time.time()
        for lease in self._leases.values():
            if lease.subject == subject and lease.tool == tool:
                if lease.valid:
                    return lease
                # Expired or exhausted — clean up
                if lease.expired or lease.exhausted:
                    continue
        return None

    def check(
        self,
        subject: str,
        tool: str,
        roles: list[str] | None = None,
        policy: dict[str, Any] | None = None,
    ) -> LeaseDecision:
        """Check lease status. Issue if needed. Return decision."""
        roles = roles or []
        policy = policy or {}

        # Try existing lease
        existing = self.lookup(subject, tool)
        if existing is not None:
            # Still valid
            risk = existing.risk_class
            held = existing.require_888_hold or risk in ("HIGH", "CRITICAL")
            return LeaseDecision(
                lease_id=existing.lease_id,
                allowed=not held,
                held=held,
                reason="Existing lease valid" if not held else "HIGH_IRREVERSIBLE — requires 888_HOLD",
                risk_class=risk,
                reversibility=existing.reversibility,
            )

        # Issue new lease from policy
        risk_class = policy.get("risk_class", "LOW")
        reversibility = policy.get("reversibility", "FULL")
        require_888 = policy.get("require_888_hold", risk_class in ("HIGH", "CRITICAL"))
        max_inv = policy.get("max_invocations", 100)
        ttl = policy.get("ttl_seconds", 3600)

        lease = self.issue(
            subject=subject,
            tool=tool,
            roles=roles,
            risk_class=risk_class,
            reversibility=reversibility,
            max_invocations=max_inv,
            ttl_seconds=ttl,
            require_888_hold=require_888,
        )

        if require_888 or risk_class in ("HIGH", "CRITICAL"):
            self._pending_approvals[lease.lease_id] = lease
            return LeaseDecision(
                lease_id=lease.lease_id,
                allowed=False,
                held=True,
                reason="HIGH_IRREVERSIBLE — issued but requires 888_HOLD approval",
                risk_class=risk_class,
                reversibility=reversibility,
            )

        return LeaseDecision(
            lease_id=lease.lease_id,
            allowed=True,
            held=False,
            reason="Lease issued from policy",
            risk_class=risk_class,
            reversibility=reversibility,
        )

    def approve(self, lease_id: str) -> bool:
        """Human approves a pending 888_HOLD lease for single execution."""
        lease = self._leases.get(lease_id)
        if lease is None:
            return False
        lease.require_888_hold = False
        self._pending_approvals.pop(lease_id, None)
        lease.granted_by = "human:approved"
        return True

    def revoke(self, lease_id: str) -> bool:
        """Revoke a lease immediately."""
        if lease_id in self._leases:
            del self._leases[lease_id]
            self._pending_approvals.pop(lease_id, None)
            return True
        return False

    def list_all(self) -> list[LeaseRecord]:
        """List all leases (active + expired)."""
        return list(self._leases.values())

    def cleanup(self) -> int:
        """Remove expired and exhausted leases. Returns count removed."""
        before = len(self._leases)
        self._leases = {
            k: v for k, v in self._leases.items()
            if v.valid and v.lease_id not in self._pending_approvals
        }
        return before - len(self._leases)
