"""
arifOS Memory Envelope Schemas — 555_MEMORY v2
═══════════════════════════════════════════════════════════════════════════════

The constitutional envelope for every memory event in the federation.
Every store, recall, quarantine, seal, or forget carries this provenance.

Hard law:
  - can_authorize_action defaults to FALSE.
  - Memory can guide. Memory can remind. Memory must not silently authorize.
  - L3 can suggest. L4 can prove occurrence. L6 can anchor authority.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# MEMORY RISK TIERS (M0–M4)
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryRiskTier(StrEnum):
    """Five-tier memory risk classification."""

    M0 = "M0"  # Ephemeral scratch — dies after session
    M1 = "M1"  # User preference — persistent but editable, no action authority
    M2 = "M2"  # Operational project memory — needs provenance, can guide routing
    M3 = "M3"  # Identity / authority memory — requires explicit confirmation + expiry
    M4 = "M4"  # Sealed constitutional memory — requires VAULT999 seal + human authority


class MemoryIntent(StrEnum):
    """Why this memory exists — typed so recall knows what it is retrieving."""

    PREFERENCE = "preference"
    FACT = "fact"
    VERDICT = "verdict"
    CASE_LAW = "case_law"
    IDENTITY = "identity"
    AUTHORITY = "authority"
    OPERATIONAL = "operational"
    EMOTIONAL = "emotional"
    PROJECT = "project"


class SourceType(StrEnum):
    """Provenance type — who asserted this memory into existence."""

    USER_DIRECT = "user_direct"
    TOOL_OBSERVED = "tool_observed"
    FILE_EVIDENCE = "file_evidence"
    WEB_EVIDENCE = "web_evidence"
    INFERENCE = "inference"
    AGENT_GENERATED = "agent_generated"


class Durability(StrEnum):
    """How long this memory should live."""

    EPHEMERAL = "ephemeral"
    SESSION = "session"
    PERSISTENT = "persistent"
    SEALED = "sealed"


class AuthorityEffect(StrEnum):
    """What effect this memory may have on downstream decisions."""

    NONE = "none"
    ADVISORY = "advisory"
    OPERATIONAL = "operational"
    SOVEREIGN = "sovereign"


class PrivacyLevel(StrEnum):
    """Visibility boundary for this memory."""

    PUBLIC = "public"
    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    SECRET = "secret"


class Reversibility(StrEnum):
    """How easily this memory can be undone."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MemoryStatus(StrEnum):
    """Lifecycle state of a memory record."""

    ACTIVE = "active"
    QUARANTINED = "quarantined"
    SEALED = "sealed"
    TOMBSTONED = "tombstoned"
    REVOKED = "revoked"


class VirtueVerdict(StrEnum):
    """Result of a single virtue gate."""

    PASS = "PASS"
    FAIL = "FAIL"
    DEFER = "DEFER"


class MemoryStoreStatus(StrEnum):
    """Final disposition after virtue gates."""

    STORED_ADVISORY = "stored_advisory"
    STORED_AUTHORITY = "stored_authority"
    QUARANTINED = "quarantined"
    SEALED = "sealed"
    REJECTED = "rejected"


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


class MemorySource(BaseModel):
    """Provenance metadata — every memory must declare where it came from."""

    type: SourceType = Field(description="Who or what asserted this memory")
    uri: str | None = Field(default=None, description="Canonical source URI or reference")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC), description="When the source event occurred")
    confidence: float = Field(ge=0.0, le=1.0, default=0.8, description="Confidence in the source (0.0–1.0)")


class MemoryRisk(BaseModel):
    """Risk passport for a memory event — blast radius of remembering this."""

    durability: Durability = Field(default=Durability.SESSION, description="Memory lifetime")
    authority_effect: AuthorityEffect = Field(default=AuthorityEffect.NONE, description="Decision influence level")
    privacy: PrivacyLevel = Field(default=PrivacyLevel.INTERNAL, description="Visibility boundary")
    reversibility: Reversibility = Field(default=Reversibility.HIGH, description="How easily this can be undone")


class MemoryGovernance(BaseModel):
    """Constitutional governance bindings for a memory event."""

    requires_888: bool = Field(default=False, description="Does this require 888_JUDGE approval?")
    floors: list[str] = Field(default_factory=list, description="Constitutional floors activated")
    expiry: datetime | None = Field(default=None, description="When this memory expires")
    can_authorize_action: bool = Field(
        default=False,
        description="HARD DEFAULT: FALSE. Memory may not authorize action.",
    )

    @field_validator("can_authorize_action", mode="before")
    @classmethod
    def _force_default_false(cls, v: Any) -> bool:
        """F13-enforced: memory can never self-authorize at storage time."""
        if v is True:
            # Log the violation but force false — authority is granted at recall time by judge
            return False
        return False


class MemoryVirtueReceipt(BaseModel):
    """Receipt from the four virtue gates — every memory write gets one."""

    amanah: VirtueVerdict = Field(default=VirtueVerdict.DEFER, description="Trustworthiness gate")
    beradab: VirtueVerdict = Field(default=VirtueVerdict.DEFER, description="Proper conduct gate")
    berhikmah: VirtueVerdict = Field(default=VirtueVerdict.DEFER, description="Wisdom gate")
    berakal: VirtueVerdict = Field(default=VirtueVerdict.DEFER, description="Reason gate")
    memory_status: MemoryStoreStatus = Field(
        default=MemoryStoreStatus.STORED_ADVISORY,
        description="Final disposition",
    )
    reasons: list[str] = Field(default_factory=list, description="Why each gate passed/failed/deferred")

    def all_pass(self) -> bool:
        """True only if all four virtues pass."""
        return all(
            v == VirtueVerdict.PASS
            for v in (self.amanah, self.beradab, self.berhikmah, self.berakal)
        )

    def any_fail(self) -> bool:
        """True if any virtue failed."""
        return any(
            v == VirtueVerdict.FAIL
            for v in (self.amanah, self.beradab, self.berhikmah, self.berakal)
        )


# ═══════════════════════════════════════════════════════════════════════════════
# FULL MEMORY ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryEventEnvelope(BaseModel):
    """
    The constitutional envelope for every memory event.

    This is the nervous system of the federation — without this envelope,
    memory becomes chaos. With it, memory becomes governed evidence.
    """

    actor_id: str = Field(description="Who triggered this memory event")
    session_id: str = Field(description="Governing session for audit chain")
    memory_intent: MemoryIntent = Field(description="Why this memory exists")
    niat: str | None = Field(default=None, description="Moral intent behind this memory")
    content: str = Field(description="The memory content itself")
    source: MemorySource = Field(description="Where this memory came from")
    risk: MemoryRisk = Field(default_factory=MemoryRisk, description="Risk passport")
    governance: MemoryGovernance = Field(default_factory=MemoryGovernance, description="Constitutional bindings")
    tags: list[str] = Field(default_factory=list, description="Cross-organ search tags")

    # Virtue receipt is computed at storage time, not provided by caller
    virtue_receipt: MemoryVirtueReceipt | None = Field(
        default=None,
        description="Computed by the memory gate — not set by caller",
    )

    # Internal routing
    m_tier: MemoryRiskTier = Field(default=MemoryRiskTier.M1, description="Computed M-tier")
    memory_status: MemoryStatus = Field(default=MemoryStatus.ACTIVE, description="Lifecycle state")
    supersedes_id: str | None = Field(default=None, description="Previous version for update chaining")

    # Capability abstraction (never store raw secrets)
    capability_ref: dict[str, Any] | None = Field(
        default=None,
        description="Capability reference — agent_visible_secret must be false",
    )

    @field_validator("capability_ref")
    @classmethod
    def _no_visible_secrets(cls, v: dict[str, Any] | None) -> dict[str, Any] | None:
        """RULE 7: No raw API key enters any memory layer."""
        if v is None:
            return None
        if v.get("agent_visible_secret") is True:
            raise ValueError("RULE 7 VIOLATION: agent_visible_secret cannot be true in memory")
        return v

    @field_validator("content")
    @classmethod
    def _no_raw_secrets_in_content(cls, v: str) -> str:
        """RULE 6 + 7: Scan content for secret patterns and reject."""
        import re

        secret_patterns = [
            r"sk-[a-zA-Z0-9]{20,}",  # OpenAI-style API keys
            r"ghp_[a-zA-Z0-9]{36}",  # GitHub personal access tokens
            r"AKIA[0-9A-Z]{16}",  # AWS access key ID
            r"[A-Za-z0-9/+=]{40}",  # Generic base64-like secrets (heuristic)
        ]
        for pattern in secret_patterns:
            if re.search(pattern, v):
                raise ValueError(
                    f"RULE 7 VIOLATION: content contains possible secret pattern "
                    f"matching {pattern}. Store capabilities, not secrets."
                )
        return v


# ═══════════════════════════════════════════════════════════════════════════════
# M-TIER MAPPING
# ═══════════════════════════════════════════════════════════════════════════════


M_TIER_CONFIG: dict[MemoryRiskTier, dict[str, Any]] = {
    MemoryRiskTier.M0: {
        "legacy_tier": "ephemeral",
        "ttl_hours": 1,
        "auto_prune": True,
        "requires_888": False,
        "vault_seal": False,
    },
    MemoryRiskTier.M1: {
        "legacy_tier": "canon",
        "ttl_hours": 24 * 90,
        "auto_prune": False,
        "requires_888": False,
        "vault_seal": False,
    },
    MemoryRiskTier.M2: {
        "legacy_tier": "canon",
        "ttl_hours": 24 * 90,
        "auto_prune": False,
        "requires_888": False,
        "vault_seal": False,
    },
    MemoryRiskTier.M3: {
        "legacy_tier": "sacred",
        "ttl_hours": None,
        "auto_prune": False,
        "requires_888": True,
        "vault_seal": False,
    },
    MemoryRiskTier.M4: {
        "legacy_tier": "sacred",
        "ttl_hours": None,
        "auto_prune": False,
        "requires_888": True,
        "vault_seal": True,
    },
}


def compute_m_tier(envelope: MemoryEventEnvelope) -> MemoryRiskTier:
    """
    Compute M-tier from envelope fields.

    M-tier is determined by authority_effect + durability + memory_intent,
    not by caller request. This prevents an agent from claiming M0 for M4 content.
    """
    # M4: sealed constitutional memory
    if envelope.risk.durability == Durability.SEALED:
        return MemoryRiskTier.M4
    if envelope.memory_intent in (MemoryIntent.VERDICT, MemoryIntent.CASE_LAW):
        if envelope.governance.requires_888:
            return MemoryRiskTier.M4

    # M3: identity / authority memory
    if envelope.memory_intent in (MemoryIntent.IDENTITY, MemoryIntent.AUTHORITY):
        if envelope.governance.requires_888 or envelope.risk.authority_effect == AuthorityEffect.OPERATIONAL:
            return MemoryRiskTier.M3

    # M2: operational project memory
    if envelope.memory_intent in (MemoryIntent.OPERATIONAL, MemoryIntent.PROJECT):
        if envelope.risk.authority_effect in (AuthorityEffect.ADVISORY, AuthorityEffect.OPERATIONAL):
            return MemoryRiskTier.M2

    # M1: user preference
    if envelope.memory_intent == MemoryIntent.PREFERENCE:
        return MemoryRiskTier.M1

    # M0: everything else defaults ephemeral
    if envelope.risk.durability == Durability.EPHEMERAL:
        return MemoryRiskTier.M0

    # Default: M1 (safe middle ground)
    return MemoryRiskTier.M1
