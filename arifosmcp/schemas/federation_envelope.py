"""
Federation Envelope — MCP Federation Reconstruction A Foundation (v2)
═══════════════════════════════════════════════════════════════════════════════

Every MCP tool call and A2A message across the arifOS Federation MUST carry
this envelope. Without it, the call is invisible to constitutional governance.

v2 Hard rules (Chapter 6 Upgrade — Human Wakefulness Federation):
  - No envelope → wrap legacy call → allow OBSERVE only.
  - LEGACY_WRAP + any action beyond OBSERVE → HOLD.
  - claim_state is mandatory for consequential actions (PREPARE, MUTATE, ATOMIC).
  - Tool calls touching dignity, memory, mutation, vault, identity, or external
    effects REQUIRE a SovereigntyCheckpoint before execution.
  - host_attestation identifies the calling runtime for semi-trusted host defense.
  - agent_id and tool_id are mandatory for production. Transition mode allows missing.
  - trace_id links the full call chain across organs.

DITEMPA BUKAN DIBERI — Jurisdiction before intelligence.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.schemas.embodied_tool import ClaimState
from arifosmcp.schemas.sovereignty_checkpoint import SovereigntyCheckpoint

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

    TOKEN = "token"  # JWT / auth token verified
    SESSION = "session"  # Active session bound
    DELEGATED = "delegated"  # Delegated from another actor
    HUMAN_888 = "human_888"  # Explicit human approval via 888_JUDGE
    FALLBACK = "fallback"  # Legacy/env fallback (transition mode)
    UNKNOWN = "unknown"  # No authority established


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
    delegator: str | None = Field(default=None, description="Actor who delegated authority")
    delegatee: str | None = Field(default=None, description="Actor receiving delegated authority")
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
    """What phase of action this call represents.

    Canonical seven-class ladder. Higher = more dangerous.
    Import from kernel_envelope as the single source of truth.

    OBSERVE: Read-only. No external side effects.
    ANALYZE: Reason over existing data. No mutation.
    DRAFT: Create proposed content, plan, patch. No external side effects.
    SIMULATE: Run reversible sandbox execution only.
    MUTATE: Change local state, files, memory, database, configuration.
    EXTERNAL_SIDE_EFFECT: Send email, call external API, post, publish.
    IRREVERSIBLE: Delete, rotate keys, deploy production, vault seal.
    """

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    DRAFT = "DRAFT"
    SIMULATE = "SIMULATE"
    MUTATE = "MUTATE"
    EXTERNAL_SIDE_EFFECT = "EXTERNAL_SIDE_EFFECT"
    IRREVERSIBLE = "IRREVERSIBLE"
    UNKNOWN = "UNKNOWN"


class ToolClass(StrEnum):
    """Policy/approval risk class for the tool.

    Distinct from ActionClass: ToolClass governs approval posture,
    ActionClass governs execution phase. Both coexist on RiskPassport.

    observe   → read-only, no approval
    retrieve  → fetch from external source, attestation only
    decide    → judgment/routing/evaluation, floor check + receipt
    mutate    → write/modify/execute/deploy, 888_JUDGE or L13
    """

    OBSERVE = "observe"
    RETRIEVE = "retrieve"
    DECIDE = "decide"
    MUTATE = "mutate"


class BlastRadius(StrEnum):
    """Canonical 8-class blast radius (Hermes ASI standard).

    Import from kernel_envelope as the single source of truth.
    Kept here for import convenience in federation-facing code.

    NONE, LOCAL, ACCOUNT, ORG, PUBLIC, MARKET, INFRASTRUCTURE, CIVILIZATIONAL.
    """

    NONE = "NONE"
    LOCAL = "LOCAL"
    ACCOUNT = "ACCOUNT"
    ORG = "ORG"
    PUBLIC = "PUBLIC"
    MARKET = "MARKET"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CIVILIZATIONAL = "CIVILIZATIONAL"
    UNKNOWN = "UNKNOWN"


class ReversibilityLevel(StrEnum):
    """How easily this action can be undone."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    IRREVERSIBLE = "irreversible"


class SecretTouch(StrEnum):
    """Whether this action touches secrets."""

    NONE = "none"  # No secret access
    POSSIBLE = "possible"  # May access secrets depending on params
    DEFINITE = "definite"  # Definitely accesses secrets


class ExternalEffect(StrEnum):
    """Whether this action has effects outside the federation."""

    NONE = "none"  # Internal only
    PRIVATE = "private"  # External but private (internal API)
    PUBLIC = "public"  # External and public-visible
    LEGAL = "legal"  # Legal/regulatory implications
    FINANCIAL = "financial"  # Financial transaction


class ToolScope(StrEnum):
    """What domains the tool touches — for semi-trusted host defense."""

    READ = "read"  # Read-only tool surface
    WRITE = "write"  # Mutation of state
    EXTERNAL = "external"  # External API / side effect
    SECRET = "secret"  # Touches secrets / credentials
    MEMORY = "memory"  # Reads or writes memory
    DIGNITY = "dignity"  # Touches human dignity / identity
    VAULT = "vault"  # Touches VAULT999


class HostAttestation(StrEnum):
    """Level of trust for the calling host runtime."""

    TRUSTED = "trusted"  # Locally verified host
    SEMI_TRUSTED = "semi_trusted"  # Known host, not fully verified
    UNTRUSTED = "untrusted"  # Unknown or public host
    UNKNOWN = "unknown"  # No attestation available


class RiskPassport(BaseModel):
    """
    Risk passport for a single tool call.

    Every tool call MUST declare its risk before execution.
    The runtime checks risk_ceiling against this passport.
    """

    tier: RiskTier = Field(default=RiskTier.T0, description="Risk tier")
    action_class: ActionClass = Field(default=ActionClass.OBSERVE, description="Action phase")
    tool_class: ToolClass = Field(
        default=ToolClass.OBSERVE,
        description="Policy/approval risk class: observe | retrieve | decide | mutate",
    )
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
            return False, "ATOMIC requires arif_ack_id (L13 sovereign approval)"
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

    v2 (Chapter 6 Upgrade — Human Wakefulness Federation):
      - claim_state: epistemic tag on the call itself (OBSERVED/DERIVED/...)
      - tool_scope: what domains this tool touches (read/write/external/secret/memory/dignity/vault)
      - host_attestation: trust level of the calling runtime
      - expires_at: envelope expiry for short-lived authority
      - actor_verification: claimed | verified | delegated
      - sovereignty_checkpoint: required for dignity/memory/mutation/vault/identity tools
    """

    envelope_version: str = Field(default="2.0", description="Envelope spec version — Chapter 6 Upgrade")
    trace_id: str = Field(description="Unique trace ID for this call chain")
    parent_trace_id: str | None = Field(default=None, description="Parent trace for nested calls")

    # Identity
    actor_id: str = Field(description="Who triggered this call (the human sovereign, after delegation chain)")
    actor_verification: str = Field(
        default="claimed",
        description="claimed | verified | delegated — how the actor was verified",
    )
    session_id: str = Field(description="Governing session")
    agent_id: str | None = Field(default=None, description="Which agent is acting")
    tool_id: str | None = Field(default=None, description="Which tool is being invoked")
    organ: FederationOrgan = Field(description="Which organ this call targets")

    # ── v3: Delegation Chain (preserved across A2A bridges) ──────────
    # The original human caller, preserved through relay hops so
    # downstream tools see the sovereign, not the relay.
    caller_actor: str | None = Field(
        default=None,
        description="Original human caller — preserved through A2A relay (e.g. arifbfazil)",
    )
    executor_actor: str | None = Field(
        default=None,
        description="Agent/relay executing this call on behalf of caller (e.g. Hermes@af-forge)",
    )
    sovereign: str | None = Field(
        default=None,
        description="Human sovereign — always the human, never the relay. Used for F13 floor.",
    )

    # Niat / Matlamat separation
    niat: str | None = Field(default=None, description="Moral intent: why this action exists")
    matlamat: str | None = Field(
        default=None, description="Concrete goal: what outcome is requested"
    )

    # Authority and Risk
    authority: AuthorityEnvelope = Field(default_factory=AuthorityEnvelope)
    risk: RiskPassport = Field(default_factory=RiskPassport)
    receipts: ActionReceipts = Field(default_factory=ActionReceipts)

    # ── v2: Chapter 6 Upgrade Fields ──────────────────────────────────────
    # Epistemic tag on the call itself — separates certainty from capability
    claim_state: ClaimState = Field(
        default=ClaimState.UNKNOWN,
        description="Epistemic tag on this call: VERIFIED | INTERPRETED | HYPOTHESIS | UNKNOWN",
    )
    # What domains this tool touches — for semi-trusted host defense
    tool_scope: list[ToolScope] = Field(
        default_factory=list,
        description="Domains this tool touches: read | write | external | secret | memory | dignity | vault",
    )
    # Trust level of the calling host runtime
    host_attestation: HostAttestation = Field(
        default=HostAttestation.UNKNOWN,
        description="Trust level of the calling host runtime",
    )
    # Envelope expiry for short-lived authority
    expires_at: datetime | None = Field(
        default=None,
        description="When this envelope expires (default: 5 min from creation)",
    )
    # Sovereignty checkpoint for high-impact actions
    sovereignty_checkpoint: SovereigntyCheckpoint | None = Field(
        default=None,
        description="Completed wakefulness checkpoint for dignity/memory/vault/identity actions",
    )
    # ───────────────────────────────────────────────────────────────────────

    # ── v2: Lineage propagation ───────────────────────────────────────────
    # Links this envelope to the constitutional chain for audit and appeal
    judge_state_hash: str | None = Field(
        default=None,
        description="Hash of the judge deliberation state that authorized this call",
    )
    vault_entry_id: str | None = Field(
        default=None,
        description="VAULT999 entry ID that sealed the prior decision in this chain",
    )
    constitutional_chain_id: str | None = Field(
        default=None,
        description="Canonical constitutional chain ID for lineage tracking",
    )
    # ───────────────────────────────────────────────────────────────────────

    # Transition mode flag
    legacy_wrap: bool = Field(
        default=False,
        description="True if this envelope was auto-generated for a legacy call",
    )

    def requires_sovereignty_checkpoint(self) -> bool:
        """
        True if this call touches domains that require the human to stay awake.

        Triggers for: dignity, memory mutation, vault writes, identity operations,
        external effects at scale, or secret access.
        """
        checkpoint_scopes = {
            ToolScope.DIGNITY,
            ToolScope.VAULT,
            ToolScope.MEMORY,
            ToolScope.SECRET,
        }
        touched = set(self.tool_scope) & checkpoint_scopes
        if touched:
            return True
        # Also trigger for ATOMIC actions regardless of scope
        if self.risk.action_class == ActionClass.ATOMIC:
            return True
        # External effects at PUBLIC/FINANCIAL/LEGAL level
        if self.risk.external_effect in (
            ExternalEffect.PUBLIC,
            ExternalEffect.FINANCIAL,
            ExternalEffect.LEGAL,
        ):
            return True
        return False

    def validate_for_execution(self) -> tuple[bool, str]:
        """
        Validate this envelope before tool execution.

        Returns (ok, reason).

        v2: tightened legacy_wrap — anything beyond OBSERVE with legacy_wrap = HOLD.
        """
        # Identity check
        if not self.actor_id:
            return False, "actor_id is mandatory"
        if self.actor_id == "anonymous" and self.risk.action_class in (
            ActionClass.MUTATE,
            ActionClass.ATOMIC,
        ):
            return False, f"{self.risk.action_class.value} requires non-anonymous actor_id"
        if not self.session_id:
            return False, "session_id is mandatory"

        # ── v2: Tightened legacy_wrap — OBSERVE + PREPARE allowed ─────────
        # PREPARE (reasoning, planning, recall) does not mutate state;
        # legacy clients should be able to call mind_reason, memory_recall,
        # evidence_fetch without a full FederationEnvelope.
        if self.legacy_wrap and self.risk.action_class not in (
            ActionClass.OBSERVE,
            ActionClass.PREPARE,
        ):
            return False, (
                f"LEGACY_WRAP cannot execute {self.risk.action_class.value}. "
                "Upgrade client to send FederationEnvelope with verified authority, "
                "claim_state, tool_scope, and host_attestation."
            )

        # Authority check
        if self.authority.source == AuthoritySource.UNKNOWN:
            if self.risk.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC):
                return False, f"UNKNOWN authority cannot execute {self.risk.action_class.value}"

        # v2: actor_verification check for mutating actions
        if self.risk.action_class in (ActionClass.MUTATE, ActionClass.ATOMIC):
            if self.actor_verification == "claimed" and self.authority.source not in (
                AuthoritySource.TOKEN,
                AuthoritySource.HUMAN_888,
            ):
                return False, (
                    f"{self.risk.action_class.value} requires verified actor, not claimed. "
                    "Use actor_verification='verified' or authority source TOKEN/HUMAN_888."
                )

        # Delegation expiry check
        if self.authority.delegator and not self.authority.is_delegation_valid():
            return False, "Delegation expired or missing expiry"

        # Envelope expiry check (v2)
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False, "Envelope expired — reissue with fresh authority"

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
            "actor_verification": self.actor_verification,
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
            "claim_state": self.claim_state.value,
            "tool_scope": [s.value for s in self.tool_scope],
            "host_attestation": self.host_attestation.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
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
    v2: only OBSERVE is allowed with legacy_wrap. PREPARE/MUTATE/ATOMIC
    will be rejected by validate_for_execution().
    """
    return FederationEnvelope(
        trace_id=f"legacy-{datetime.now(UTC).isoformat()}",
        actor_id=actor_id or "anonymous",
        actor_verification="claimed",
        session_id=session_id or "unknown",
        tool_id=tool_name,
        organ=organ,
        authority=AuthorityEnvelope(source=AuthoritySource.FALLBACK),
        risk=RiskPassport(
            tier=RiskTier.T2 if action_class == ActionClass.MUTATE else RiskTier.T0,
            action_class=action_class,
        ),
        claim_state=ClaimState.UNKNOWN,
        tool_scope=[ToolScope.READ] if action_class == ActionClass.OBSERVE else [],
        host_attestation=HostAttestation.UNKNOWN,
        legacy_wrap=True,
    )
