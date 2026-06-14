"""
arifosmcp/runtime/lease.py — Capability Lease Primitive

Forged: 2026-06-11 by omega-forge-agent
Status: LIVE (2026-06-14) — Hard-block wired into _arif_forge_execute.
  Mutation-class forge modes (engineer, write, generate, commit) now
  REQUIRE a valid lease. No warn-and-proceed path remains.
  Reversible: comment out lease gate block in runtime/tools.py.

Addresses Roadmap P2-7:
  Lease primitive — no cross-organ action without
  {lease_id, scope, ttl, max_invocations}.

The lease is now wired as a hard gate in `_arif_forge_execute` (runtime/tools.py).
All mutation-class forge modes require a valid lease. Read-only modes (query,
recall, dry_run) are exempt.

Design:
  Lease is issued by the kernel (acting as the sovereign ledger) and
  presented by an agent at tool-call time. The lease is bound to:
    - actor_did   (who is asking)
    - organ       (which organ hosts the tool)
    - tool        (which tool is being called)
    - scope       (read | write | execute)
    - ttl         (seconds before automatic revocation)
    - max_invocations  (how many times this lease can be presented)
    - revocable   (the kernel can revoke at any time)
    - lease_id    (unique, non-guessable)

A lease is NOT a token in the cryptographic sense. It is a *governance
token* — the kernel's commitment that this actor, on this organ, on
this tool, for this scope, for this many calls, is currently permitted
to act. The kernel revokes leases silently on session_close, on
floor violations, or on demand.

Why a lease is not just a number:
  - It carries `scope`. An agent with a `read` lease cannot present
    the same lease for a `write` call.
  - It carries `max_invocations`. A `read` lease issued once does
    not let the agent read forever.
  - It carries `ttl`. A lease that outlives its ttl is rejected.
  - It is revocable. The kernel can kill a lease in mid-flight.
  - It is observable. Every lease presentation is logged.

The lease store lives in process memory by default. A future
deployment can back it with Redis (already in the federation) without
changing this module's interface.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class LeaseScope(str, Enum):
    """The scope of a lease. Higher scopes are subsets of lower scopes."""

    EXECUTE = "execute"  # the strongest; allows MUTATE and ATOMIC
    WRITE = "write"  # OBSERVE + MUTATE
    READ = "read"  # OBSERVE only

    @classmethod
    def subsumes(cls, granted: "LeaseScope", requested: "LeaseScope") -> bool:
        """
        A lease with scope `granted` permits a call that requires
        scope `requested` if and only if `granted` is at least as
        strong as `requested`. EXECUTE subsumes WRITE subsumes READ.
        """
        order = {cls.READ: 1, cls.WRITE: 2, cls.EXECUTE: 3}
        return order[granted] >= order[requested]


@dataclass(frozen=True)
class LeaseSpec:
    """The request shape for a new lease. The kernel fills in lease_id."""

    actor_did: str
    organ: str
    tool: str
    scope: LeaseScope
    ttl_s: int = 300
    max_invocations: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Lease:
    """An issued lease. Immutable once issued."""

    lease_id: str
    spec: LeaseSpec
    issued_at: float
    expires_at: float
    invocations_used: int = 0
    revoked: bool = False
    revoked_reason: str | None = None

    @property
    def ttl_remaining_s(self) -> float:
        return max(0.0, self.expires_at - time.time())

    @property
    def is_expired(self) -> bool:
        return self.ttl_remaining_s <= 0

    def is_valid_for(self, requested_scope: LeaseScope) -> bool:
        if self.revoked:
            return False
        if self.is_expired:
            return False
        if self.invocations_used >= self.spec.max_invocations:
            return False
        return LeaseScope.subsumes(self.spec.scope, requested_scope)


class LeaseStore:
    """
    In-memory store of issued leases. Thread-safe enough for a
    single-process kernel; for multi-process federation, back this
    with Redis (the L2 layer already in the federation).

    This is the primitive. Wiring `verify_lease()` into the tool
    entry path is a separate, gated change.
    """

    def __init__(self) -> None:
        self._leases: dict[str, Lease] = {}

    @staticmethod
    def _new_lease_id() -> str:
        # 16 bytes of entropy, hex-encoded — 32 hex chars.
        # Sufficient uniqueness for the in-process store.
        return f"lease-{secrets.token_hex(16)}"

    def issue(self, spec: LeaseSpec) -> Lease:
        """Issue a new lease. Returns the immutable Lease record."""
        if spec.ttl_s <= 0:
            raise ValueError(f"ttl_s must be positive, got {spec.ttl_s}")
        if spec.max_invocations <= 0:
            raise ValueError(f"max_invocations must be positive, got {spec.max_invocations}")
        if not spec.actor_did or not spec.organ or not spec.tool:
            raise ValueError("actor_did, organ, tool are all required")

        now = time.time()
        lease = Lease(
            lease_id=self._new_lease_id(),
            spec=spec,
            issued_at=now,
            expires_at=now + spec.ttl_s,
        )
        self._leases[lease.lease_id] = lease
        return lease

    def revoke(self, lease_id: str, reason: str) -> bool:
        """Revoke a lease. Returns True if a lease was found and revoked."""
        existing = self._leases.get(lease_id)
        if existing is None or existing.revoked:
            return False
        self._leases[lease_id] = Lease(
            lease_id=existing.lease_id,
            spec=existing.spec,
            issued_at=existing.issued_at,
            expires_at=existing.expires_at,
            invocations_used=existing.invocations_used,
            revoked=True,
            revoked_reason=reason,
        )
        return True

    def consume(self, lease_id: str, requested_scope: LeaseScope) -> Lease | None:
        """
        Try to consume one invocation from a lease. Returns the
        *updated* lease if the consumption was successful, or
        None if the lease is unknown, revoked, expired, exhausted,
        or does not cover the requested scope.

        Atomic with respect to a single Python process. For
        distributed deployment, the consume operation must be
        serialized at the storage layer.
        """
        existing = self._leases.get(lease_id)
        if existing is None:
            return None
        if not existing.is_valid_for(requested_scope):
            return None
        updated = Lease(
            lease_id=existing.lease_id,
            spec=existing.spec,
            issued_at=existing.issued_at,
            expires_at=existing.expires_at,
            invocations_used=existing.invocations_used + 1,
            revoked=existing.revoked,
            revoked_reason=existing.revoked_reason,
        )
        self._leases[lease_id] = updated
        return updated

    def get(self, lease_id: str) -> Lease | None:
        return self._leases.get(lease_id)

    def list_active(self) -> list[Lease]:
        """Return all leases that are not revoked and not expired."""
        return [l for l in self._leases.values() if not l.revoked and not l.is_expired]

    def purge_expired(self) -> int:
        """Remove expired and revoked leases from the store. Returns the count purged."""
        before = len(self._leases)
        self._leases = {
            lid: l for lid, l in self._leases.items() if not l.revoked and not l.is_expired
        }
        return before - len(self._leases)


@dataclass(frozen=True)
class LeaseRejection:
    """The result of a lease verification."""

    granted: bool
    lease_id: str | None
    reason: str
    reason_code: (
        str  # "OK" | "UNKNOWN" | "REVOKED" | "EXPIRED" | "EXHAUSTED" | "SCOPE_INSUFFICIENT"
    )
    lease_state: dict[str, Any] | None = None


# The default store. Wiring replaces this with a Redis-backed
# implementation in a future deployment.
_DEFAULT_STORE: LeaseStore | None = None


def get_default_store() -> LeaseStore:
    global _DEFAULT_STORE
    if _DEFAULT_STORE is None:
        _DEFAULT_STORE = LeaseStore()
    return _DEFAULT_STORE


def verify_lease(
    lease_id: str | None,
    requested_scope: LeaseScope,
    *,
    store: LeaseStore | None = None,
) -> LeaseRejection:
    """
    Check whether a lease is valid for the requested scope. Does NOT
    consume an invocation — the caller decides whether to consume.

    For a `read` tool call, the caller should:
        rejection = verify_lease(lease_id, LeaseScope.READ)
        if rejection.granted:
            consume_lease(lease_id, LeaseScope.READ)

    The reason codes are stable and machine-readable.
    """
    if not lease_id:
        return LeaseRejection(
            granted=False,
            lease_id=None,
            reason="no lease_id provided",
            reason_code="UNKNOWN",
        )
    store = store or get_default_store()
    lease = store.get(lease_id)
    if lease is None:
        return LeaseRejection(
            granted=False,
            lease_id=lease_id,
            reason=f"lease {lease_id!r} not found",
            reason_code="UNKNOWN",
        )
    if lease.revoked:
        return LeaseRejection(
            granted=False,
            lease_id=lease_id,
            reason=f"lease {lease_id!r} revoked: {lease.revoked_reason}",
            reason_code="REVOKED",
            lease_state={"invocations_used": lease.invocations_used},
        )
    if lease.is_expired:
        return LeaseRejection(
            granted=False,
            lease_id=lease_id,
            reason=f"lease {lease_id!r} expired",
            reason_code="EXPIRED",
            lease_state={"ttl_remaining_s": 0.0},
        )
    if lease.invocations_used >= lease.spec.max_invocations:
        return LeaseRejection(
            granted=False,
            lease_id=lease_id,
            reason=f"lease {lease_id!r} exhausted",
            reason_code="EXHAUSTED",
            lease_state={"invocations_used": lease.invocations_used},
        )
    if not LeaseScope.subsumes(lease.spec.scope, requested_scope):
        return LeaseRejection(
            granted=False,
            lease_id=lease_id,
            reason=(
                f"lease {lease_id!r} has scope={lease.spec.scope.value!r}, "
                f"requested={requested_scope.value!r}"
            ),
            reason_code="SCOPE_INSUFFICIENT",
            lease_state={"granted_scope": lease.spec.scope.value},
        )
    return LeaseRejection(
        granted=True,
        lease_id=lease_id,
        reason="lease valid for requested scope",
        reason_code="OK",
        lease_state={
            "ttl_remaining_s": lease.ttl_remaining_s,
            "invocations_remaining": lease.spec.max_invocations - lease.invocations_used,
        },
    )


__all__ = [
    "LeaseScope",
    "LeaseSpec",
    "Lease",
    "LeaseStore",
    "LeaseRejection",
    "get_default_store",
    "verify_lease",
]
