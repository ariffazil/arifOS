"""
Federation Envelope — MCP Federation Reconstruction A Foundation
═══════════════════════════════════════════════════════════════════════════════

Every MCP tool call and A2A message across the arifOS Federation MUST carry
this envelope. Without it, the call is invisible to constitutional governance.

Hard rules:
  - No envelope → wrap legacy call → classify as UNKNOWN → allow OBSERVE only.
  - No envelope + action_class in (MUTATE, ATOMIC) → HOLD.
  - agent_id and tool_id are mandatory for production. Transition mode allows missing.
  - trace_id links the full call chain across organs.

DITEMPA BUKAN DIBERI — Jurisdiction before intelligence.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# ORGAN ENUM
# ═══════════════════════════════════════════════════════════════════════════════


class FederationOrgan(StrEnum):
    """Canonical organs in the arifOS Federation."""

    ARIFOS = "arifOS"
    WEALTH = "WEALTH"
    WELL = "WELL"
    GEOX = "GEOX"
    HERMES = "HERMES"
    AAA = "AAA"
    A_FORGE = "A-FORGE"
    APEX = "APEX"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHORITY ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class AuthoritySource(StrEnum):
    """How the caller obtained authority for this action."""

    TOKEN = "token"          # JWT / auth token verified
    SESSION = "session"      # Active session bound
    DELEGATED = "delegated"  # Delegated from another actor
    HUMAN_888 = "human_888"  # Explicit human approval via 888_JUDGE
    FALLBACK = "fallback"    # Legacy/env fallback (transition mode)
    UNKNOWN = "unknown"      # No authority established


class AuthorityEnvelope(BaseModel):
    """
    Authority provenance — who authorized this action and under what scope.

    Delegation chain:
      delegator → delegatee → scope → expiry

    Hard rule: delegation without expiry is rejected.
    """

    source: AuthoritySource = Field(
        default=AuthoritySource.UNKNOWN,
        description="How authority was obtained",
    )
    verified: bool = Field(
        default=False, description="Has authority been cryptographically verified?"
    )
    delegator: str | None = Field(
        default=None, description="Actor who delegated authority"
    )
    delegatee: str | None = Field(
        default=None, description="Actor receiving delegated authority"
    )
    scope: list[str] = Field(
        default_factory=list, description="Allowed actions under this authority"
    )
    expires_at: datetime | None = Field(default=None, description="Authority expiry")

    def is_delegation_valid(self) -> bool:
        """True if delegation has not expired."""
        if not self.expires_at:
            return False  # No expiry = invalid
        return datetime.now(UTC) < self.expires_at

    def can_act(self, action: str) -> bool:
        """True if the authority scope includes the requested action."""
        if not self.scope:
            return False
        return action in self.scope or "*" in self.scope


# ═══════════════════════════════════════════════════════════════════════════════
# RISK PASSPORT (imported from risk_passport.py — re-exported here)
# ═══════════════════════════════════════════════════════════════════════════════


class RiskTier(StrEnum):
    """Canonical six-tier risk ladder."""

    T0 = "T0"  # Harmless observation
    T1 = "T1"  # Account-scoped observation
    T2 = "T2"  # Org-scoped preparation
    T3 = "T3"  # Org-scoped mutation
    T4 = "T4"  # Public-scoped mutation
    T5 = "T5"  # Infrastructure-scoped atomic action


class ActionClass(StrEnum):
    """What phase of action this call represents."""

    OBSERVE = "OBSERVE"    # Read-only, no side effects
    PREPARE = "PREPARE"    # Plan, dry-run, validate
    MUTATE = "MUTATE"      # Write, modify, execute
    ATOMIC = "ATOMIC"      # Irreversible, dangerous, final


class BlastRadius(StrEnum):
    """How far the blast reaches if this action goes wrong."""

    LOCAL = "local"          # Single process / file
    ACCOUNT = "account"      # User account / session
    ORG = "org"              # Organization / project
    PUBLIC = "public"        # Public-facing / external users
    FINANCIAL = "financial"  # Money / capital at risk
    INFRA = "infra"          # Infrastructure / host at risk


class ReversibilityLevel(StrEnum):
    """How easily this action can be undone."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IRREVERSIBLE = "irreversible"


class SecretTouch(StrEnum):
    """Whether this action touches secrets."""

    NONE = "none"       # No secret access
    POSSIBLE = "possible"  # May access secrets depending on params
    DEFINITE = "definite"  # Definitely accesses secrets


class ExternalEffect(StrEnum):
    """Whether this action has effects outside the federation."""

    NONE = "none"       # Internal only
    PRIVATE = "private"  # External but private (internal API)
    PUBLIC = "public"    # External and public-visible
    LEGAL = "legal"      # Legal/regulatory implications
    FINANCIAL = "financial"  # Financial transaction


class RiskPassport(BaseModel):
    """
    Risk passport for a single tool call.

    Every tool call MUST declare its risk before execution.
    The runtime checks risk_ceiling against this passport.
    """

    tier: RiskTier = Field(default=RiskTier.T0, description="Risk tier")
    action_class: ActionClass = Field(default=ActionClass.OBSERVE, description="Action phase")
    blast_radius: BlastRadius = Field(default=BlastRadius.LOCAL, description="Blast radius")
    reversibility: ReversibilityLevel = Field(
        default=ReversibilityLevel.HIGH, description="Reversibility"
    )
    secret_touch: SecretTouch = Field(default=SecretTouch.NONE, description="Secret exposure")
    external_effect: ExternalEffect = Field(
        default=ExternalEffect.NONE, description="External side effects"
    )
    risk_ceiling: str | None = Field(
        default=None, description="Max risk tier allowed for this actor"
    )

    def exceeds_ceiling(self, ceiling: RiskTier | str | None) -> bool:
        """True if this risk exceeds the given ceiling."""
        if ceiling is None:
            return False
        ceiling_str = ceiling.value if isinstance(ceiling, RiskTier) else ceiling
        try:
            return self.tier.value > ceiling_str
        except Exception:
            return True  # Unknown ceiling = fail closed

    def requires_receipt(self) -> bool:
        """True if this action requires a prior receipt before execution."""
        return self.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC)

    def is_dangerous(self) -> bool:
        """True if this action is high-risk."""
        return self.tier in (RiskTier.T4, RiskTier.T5) or self.action_class == ActionClass.ATOMIC


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION RECEIPTS (observe-before-mutate)
# ═══════════════════════════════════════════════════════════════════════════════


class ActionReceipts(BaseModel):
    """
    Receipts required for mutating actions.

    Hard rules:
      - MUTATE requires observe_receipt_id
      - PATCH requires diff_receipt_id
      - EXECUTE requires rollback_receipt_id
      - ATOMIC requires arif_ack_id
    """

    observe_receipt_id: str | None = Field(
        default=None,
        description="OBSERVE receipt required before MUTATE",
    )
    diff_receipt_id: str | None = Field(
        default=None,
        description="DIFF receipt required before PATCH",
    )
    rollback_receipt_id: str | None = Field(
        default=None,
        description="ROLLBACK receipt required before EXECUTE",
    )
    arif_ack_id: str | None = Field(
        default=None,
        description="ARIF_ACK receipt required before ATOMIC",
    )

    def validate_for_action(self, action_class: ActionClass) -> tuple[bool, str]:
        """Validate receipts for the given action class. Returns (ok, reason)."""
        if action_class == ActionClass.MUTATE and not self.observe_receipt_id:
            return False, "MUTATE requires observe_receipt_id (observe-before-mutate)"
        if action_class == ActionClass.ATOMIC and not self.arif_ack_id:
            return False, "ATOMIC requires arif_ack_id (F13 sovereign approval)"
        # PREPARE and OBSERVE do not require receipts
        return True, "OK"


# ═══════════════════════════════════════════════════════════════════════════════
# FULL FEDERATION ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class FederationEnvelope(BaseModel):
    """
    The constitutional envelope for every MCP tool call and A2A message.

    Without this envelope, the federation cannot govern, judge, or witness.
    With it, every call becomes a traceable, risk-classified, authority-bound event.
    """

    envelope_version: str = Field(default="1.0", description="Envelope spec version")
    trace_id: str = Field(description="Unique trace ID for this call chain")
    parent_trace_id: str | None = Field(default=None, description="Parent trace for nested calls")

    # Identity
    actor_id: str = Field(description="Who triggered this call")
    session_id: str = Field(description="Governing session")
    agent_id: str | None = Field(default=None, description="Which agent is acting")
    tool_id: str | None = Field(default=None, description="Which tool is being invoked")
    organ: FederationOrgan = Field(description="Which organ this call targets")

    # Niat / Matlamat separation
    niat: str | None = Field(default=None, description="Moral intent: why this action exists")
    matlamat: str | None = Field(
        default=None, description="Concrete goal: what outcome is requested"
    )

    # Authority and Risk
    authority: AuthorityEnvelope = Field(default_factory=AuthorityEnvelope)
    risk: RiskPassport = Field(default_factory=RiskPassport)
    receipts: ActionReceipts = Field(default_factory=ActionReceipts)

    # Transition mode flag
    legacy_wrap: bool = Field(
        default=False,
        description="True if this envelope was auto-generated for a legacy call",
    )

    def validate_for_execution(self) -> tuple[bool, str]:
        """
        Validate this envelope before tool execution.

        Returns (ok, reason).
        """
        # Identity check
        if not self.actor_id or self.actor_id == "anonymous":
            return False, "actor_id is mandatory"
        if not self.session_id:
            return False, "session_id is mandatory"

        # Authority check
        if self.authority.source == AuthoritySource.UNKNOWN:
            if self.risk.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC):
                return False, f"UNKNOWN authority cannot execute {self.risk.action_class.value}"

        # Delegation expiry check
        if self.authority.delegator and not self.authority.is_delegation_valid():
            return False, "Delegation expired or missing expiry"

        # Receipt check
        receipt_ok, receipt_reason = self.receipts.validate_for_action(self.risk.action_class)
        if not receipt_ok:
            return False, receipt_reason

        # Risk ceiling check
        if self.risk.exceeds_ceiling(self.risk.risk_ceiling):
            return False, f"Risk {self.risk.tier.value} exceeds ceiling {self.risk.risk_ceiling}"

        return True, "SEAL"

    def to_log_dict(self) -> dict[str, Any]:
        """Serialize for logging/telemetry (no secrets)."""
        return {
            "envelope_version": self.envelope_version,
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "tool_id": self.tool_id,
            "organ": self.organ.value,
            "niat": self.niat,
            "matlamat": self.matlamat,
            "authority_source": self.authority.source.value,
            "authority_verified": self.authority.verified,
            "risk_tier": self.risk.tier.value,
            "risk_action_class": self.risk.action_class.value,
            "risk_blast_radius": self.risk.blast_radius.value,
            "risk_reversibility": self.risk.reversibility.value,
            "risk_secret_touch": self.risk.secret_touch.value,
            "risk_external_effect": self.risk.external_effect.value,
            "legacy_wrap": self.legacy_wrap,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY WRAPPER
# ═══════════════════════════════════════════════════════════════════════════════


def wrap_legacy_call(
    actor_id: str | None,
    session_id: str | None,
    tool_name: str | None,
    organ: FederationOrgan = FederationOrgan.ARIFOS,
    action_class: ActionClass = ActionClass.OBSERVE,
) -> FederationEnvelope:
    """
    Wrap a legacy call that does not carry an envelope.

    Transition mode: assigns conservative defaults and marks as legacy_wrap.
    """
    return FederationEnvelope(
        trace_id=f"legacy-{datetime.now(UTC).isoformat()}",
        actor_id=actor_id or "anonymous",
        session_id=session_id or "unknown",
        tool_id=tool_name,
        organ=organ,
        authority=AuthorityEnvelope(source=AuthoritySource.FALLBACK),
        risk=RiskPassport(
            tier=RiskTier.T2 if action_class == ActionClass.MUTATE else RiskTier.T0,
            action_class=action_class,
        ),
        legacy_wrap=True,
    )
