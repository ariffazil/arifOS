"""
arifOS Gateway Lease State Machine v0.1
═════════════════════════════════════════

9 canonical states per sprint spec:

  REQUESTED → ACTIVE → EXECUTING → EXHAUSTED
                  ↓          ↓
               EXPIRED    PENDING_888
                  ↓          ↓
               REVOKED   APPROVED_888 → EXECUTING
                           ↓
                        DENIED_888 → REVOKED

Every transition emits a receipt and checks invariants.
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any

log = logging.getLogger("arifos-gateway.lease_sm")


# ── States ───────────────────────────────────────────────────────────────────

class LeaseState(Enum):
    REQUESTED = auto()
    ACTIVE = auto()
    EXECUTING = auto()
    EXHAUSTED = auto()
    EXPIRED = auto()
    REVOKED = auto()
    PENDING_888 = auto()
    APPROVED_888 = auto()
    DENIED_888 = auto()


# Valid transitions
TRANSITIONS: dict[LeaseState, set[LeaseState]] = {
    LeaseState.REQUESTED: {LeaseState.ACTIVE, LeaseState.DENIED_888},
    LeaseState.ACTIVE: {LeaseState.EXECUTING, LeaseState.EXPIRED, LeaseState.REVOKED},
    LeaseState.EXECUTING: {LeaseState.ACTIVE, LeaseState.EXHAUSTED, LeaseState.PENDING_888},
    LeaseState.EXHAUSTED: set(),  # terminal
    LeaseState.EXPIRED: {LeaseState.REVOKED},  # can be explicitly revoked
    LeaseState.REVOKED: set(),  # terminal
    LeaseState.PENDING_888: {LeaseState.APPROVED_888, LeaseState.DENIED_888, LeaseState.EXPIRED},
    LeaseState.APPROVED_888: {LeaseState.EXECUTING, LeaseState.EXPIRED, LeaseState.REVOKED},
    LeaseState.DENIED_888: {LeaseState.REVOKED},
}

TERMINAL_STATES = {LeaseState.EXHAUSTED, LeaseState.REVOKED}
ACTIVE_STATES = {LeaseState.ACTIVE, LeaseState.EXECUTING, LeaseState.PENDING_888, LeaseState.APPROVED_888}


# ── Risk classes ─────────────────────────────────────────────────────────────

class RiskClass(Enum):
    LOW = "LOW"
    MEDIUM_MUTATION = "MEDIUM_MUTATION"
    HIGH_IRREVERSIBLE = "HIGH_IRREVERSIBLE"
    HIGH_EXTERNAL = "HIGH_EXTERNAL"
    HIGH_SECRET = "HIGH_SECRET"
    HIGH_CAPITAL = "HIGH_CAPITAL"
    HIGH_PRODUCTION_MUTATION = "HIGH_PRODUCTION_MUTATION"
    SOVEREIGN = "SOVEREIGN"


REQUIRES_888: set[RiskClass] = {
    RiskClass.HIGH_IRREVERSIBLE,
    RiskClass.HIGH_EXTERNAL,
    RiskClass.HIGH_SECRET,
    RiskClass.HIGH_CAPITAL,
    RiskClass.HIGH_PRODUCTION_MUTATION,
    RiskClass.SOVEREIGN,
}


# ── Lease object (spec §3) ───────────────────────────────────────────────────

@dataclass
class LeaseScope:
    resources: list[str] = field(default_factory=list)
    allowed_args: dict[str, Any] = field(default_factory=dict)
    max_depth_m: int | None = None


@dataclass
class LeaseRisk:
    risk_class: RiskClass = RiskClass.LOW
    reversibility: str = "FULL"  # FULL | PARTIAL | NONE
    blast_radius: str = "LOW"    # LOW | MEDIUM | HIGH | SOVEREIGN
    require_888_hold: bool = False


@dataclass
class LeaseLimits:
    max_invocations: int = 1
    remaining_invocations: int = 1
    ttl_seconds: int = 3600
    expires_at: str = ""


@dataclass
class LeaseAuthority:
    issued_by: str = "arifOS-constitution-v1"
    granted_by: str = "policy:auto"
    mutation_allowed: bool = False
    external_side_effect_allowed: bool = False
    irreversible_allowed: bool = False


@dataclass
class LeaseTool:
    upstream_id: str = ""
    name: str = ""


@dataclass
class LeaseRecord:
    """Canonical v0.1 lease object matching sprint spec §3."""
    lease_id: str = ""
    state: LeaseState = LeaseState.REQUESTED
    state_history: list[dict] = field(default_factory=list)
    subject: dict[str, Any] = field(default_factory=dict)
    tool: LeaseTool = field(default_factory=LeaseTool)
    scope: LeaseScope = field(default_factory=LeaseScope)
    risk: LeaseRisk = field(default_factory=LeaseRisk)
    limits: LeaseLimits = field(default_factory=LeaseLimits)
    authority: LeaseAuthority = field(default_factory=LeaseAuthority)
    audit_chain: list[str] = field(default_factory=list)
    last_receipt_id: str | None = None
    policy_id: str = ""
    schema_hash: str = ""

    def to_canonical(self) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "status": self.state.name,
            "state": self.state.name,
            "state_history": self.state_history,
            "subject": self.subject,
            "tool": {
                "upstream_id": self.tool.upstream_id,
                "name": self.tool.name,
            },
            "scope": {
                "resources": self.scope.resources,
                "max_depth_m": self.scope.max_depth_m,
                "allowed_args": self.scope.allowed_args,
            },
            "risk": {
                "risk_class": self.risk.risk_class.value,
                "reversibility": self.risk.reversibility,
                "blast_radius": self.risk.blast_radius,
                "require_888_hold": self.risk.require_888_hold,
            },
            "limits": {
                "max_invocations": self.limits.max_invocations,
                "remaining_invocations": self.limits.remaining_invocations,
                "ttl_seconds": self.limits.ttl_seconds,
                "expires_at": self.limits.expires_at,
            },
            "authority": {
                "issued_by": self.authority.issued_by,
                "granted_by": self.authority.granted_by,
                "mutation_allowed": self.authority.mutation_allowed,
                "external_side_effect_allowed": self.authority.external_side_effect_allowed,
                "irreversible_allowed": self.authority.irreversible_allowed,
            },
            "audit": {
                "audit_chain": self.audit_chain,
                "last_receipt_id": self.last_receipt_id,
            },
            "policy_id": self.policy_id,
            "schema_hash": self.schema_hash,
        }

    def is_active(self) -> bool:
        return self.state in ACTIVE_STATES

    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    def requires_888(self) -> bool:
        return self.risk.require_888_hold

    def is_expired(self) -> bool:
        if not self.limits.expires_at:
            return False
        try:
            expiry = datetime.fromisoformat(self.limits.expires_at.replace("Z", "+00:00"))
            return datetime.now(UTC) > expiry
        except (ValueError, TypeError):
            return False

    def has_invocations(self) -> bool:
        return self.limits.remaining_invocations > 0


# ── State machine engine ─────────────────────────────────────────────────────

class LeaseStateMachine:
    """Governed lease state machine with invariant checks."""

    @staticmethod
    def transition(lease: LeaseRecord, to_state: LeaseState, reason: str = "") -> str | None:
        """Attempt a state transition. Returns None on success, error string on failure."""
        if to_state not in TRANSITIONS.get(lease.state, set()):
            return f"INVALID_TRANSITION: {lease.state.name} → {to_state.name}"

        # Invariant: ACTIVE requires remaining_invocations > 0
        if to_state == LeaseState.ACTIVE and lease.limits.remaining_invocations <= 0:
            return "INVARIANT_VIOLATION: ACTIVE requires remaining_invocations > 0"

        # Invariant: EXECUTING requires ACTIVE or APPROVED_888
        if to_state == LeaseState.EXECUTING and lease.state not in {LeaseState.ACTIVE, LeaseState.APPROVED_888}:
            return f"INVARIANT_VIOLATION: EXECUTING requires ACTIVE or APPROVED_888 (was {lease.state.name})"

        # Invariant: PENDING_888 requires require_888_hold == True
        if to_state == LeaseState.PENDING_888 and not lease.risk.require_888_hold:
            return "INVARIANT_VIOLATION: PENDING_888 requires require_888_hold == True"

        # Invariant: APPROVED_888 must come from PENDING_888
        if to_state == LeaseState.APPROVED_888 and lease.state != LeaseState.PENDING_888:
            return f"INVARIANT_VIOLATION: APPROVED_888 requires PENDING_888 (was {lease.state.name})"

        # Record transition
        old_state = lease.state
        lease.state = to_state
        entry = {
            "from": old_state.name,
            "to": to_state.name,
            "timestamp": datetime.now(UTC).isoformat(),
            "reason": reason,
        }
        lease.state_history.append(entry)

        log.info("LEASE_SM | %s: %s → %s | %s", lease.lease_id, old_state.name, to_state.name, reason)
        return None

    @staticmethod
    def activate(lease: LeaseRecord) -> str | None:
        """REQUESTED → ACTIVE"""
        return LeaseStateMachine.transition(lease, LeaseState.ACTIVE, "policy_match")

    @staticmethod
    def start_execution(lease: LeaseRecord) -> str | None:
        """ACTIVE → EXECUTING, with decrement"""
        err = LeaseStateMachine.transition(lease, LeaseState.EXECUTING, "tool_call_start")
        if err:
            return err
        lease.limits.remaining_invocations -= 1
        return None

    @staticmethod
    def complete_execution(lease: LeaseRecord) -> str | None:
        """EXECUTING → ACTIVE (if invocations remain) or EXHAUSTED"""
        if lease.limits.remaining_invocations <= 0:
            return LeaseStateMachine.transition(lease, LeaseState.EXHAUSTED, "invocations_exhausted")
        return LeaseStateMachine.transition(lease, LeaseState.ACTIVE, "tool_call_complete")

    @staticmethod
    def hold_888(lease: LeaseRecord) -> str | None:
        """EXECUTING → PENDING_888 (for high-risk tools)"""
        return LeaseStateMachine.transition(lease, LeaseState.PENDING_888, "888_hold_required")

    @staticmethod
    def approve_888(lease: LeaseRecord, approver: str) -> str | None:
        """PENDING_888 → APPROVED_888"""
        return LeaseStateMachine.transition(lease, LeaseState.APPROVED_888, f"approved_by:{approver}")

    @staticmethod
    def deny_888(lease: LeaseRecord, denier: str) -> str | None:
        """PENDING_888 → DENIED_888"""
        return LeaseStateMachine.transition(lease, LeaseState.DENIED_888, f"denied_by:{denier}")

    @staticmethod
    def expire(lease: LeaseRecord) -> str | None:
        """ACTIVE → EXPIRED (time-based)"""
        return LeaseStateMachine.transition(lease, LeaseState.EXPIRED, "ttl_expired")

    @staticmethod
    def revoke(lease: LeaseRecord, reason: str = "") -> str | None:
        """Any active → REVOKED"""
        if lease.state in TERMINAL_STATES:
            return f"INVARIANT_VIOLATION: {lease.state.name} is terminal, cannot revoke"
        return LeaseStateMachine.transition(lease, LeaseState.REVOKED, f"revoked:{reason}")


# ── Factory ──────────────────────────────────────────────────────────────────

def create_lease(
    subject: dict[str, Any],
    tool_name: str,
    upstream_id: str,
    policy_id: str,
    risk_class: RiskClass = RiskClass.LOW,
    reversibility: str = "FULL",
    blast_radius: str = "LOW",
    max_invocations: int = 1,
    ttl_seconds: int = 3600,
    mutation_allowed: bool = False,
    external_side_effect_allowed: bool = False,
    irreversible_allowed: bool = False,
    scope_resources: list[str] | None = None,
    schema_hash: str = "",
) -> LeaseRecord:
    """Create a new lease in REQUESTED state."""
    lease_id = f"lease_{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)
    expires_at = datetime.fromtimestamp(now.timestamp() + ttl_seconds, tz=UTC)

    risk = LeaseRisk(
        risk_class=risk_class,
        reversibility=reversibility,
        blast_radius=blast_radius,
        require_888_hold=risk_class in REQUIRES_888,
    )

    limits = LeaseLimits(
        max_invocations=max_invocations,
        remaining_invocations=max_invocations,
        ttl_seconds=ttl_seconds,
        expires_at=expires_at.isoformat(),
    )

    authority = LeaseAuthority(
        mutation_allowed=mutation_allowed,
        external_side_effect_allowed=external_side_effect_allowed,
        irreversible_allowed=irreversible_allowed,
    )

    lease = LeaseRecord(
        lease_id=lease_id,
        state=LeaseState.REQUESTED,
        state_history=[{
            "from": "NONE",
            "to": "REQUESTED",
            "timestamp": now.isoformat(),
            "reason": "lease_created",
        }],
        subject=subject,
        tool=LeaseTool(upstream_id=upstream_id, name=tool_name),
        scope=LeaseScope(resources=scope_resources or []),
        risk=risk,
        limits=limits,
        authority=authority,
        policy_id=policy_id,
        schema_hash=schema_hash,
    )

    # Auto-activate for non-sovereign leases
    if risk_class not in REQUIRES_888:
        err = LeaseStateMachine.activate(lease)
        if err:
            log.warning("Lease %s auto-activation failed: %s", lease_id, err)

    log.info("LEASE CREATED | %s | tool=%s risk=%s 888=%s",
             lease_id, tool_name, risk_class.value, lease.requires_888())
    return lease
