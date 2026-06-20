"""
arifos/contracts/identity.py — Canonical Identity + Authority Proof
═══════════════════════════════════════════════════════════════════

P0.6 from the 2026-06-09 readiness audit:
"claimed_id is not enough. Need signed actor identity, session nonce,
authority tier, replay protection."

v2 (2026-06-09): Added nonce, signature, authority_tier, pubkey_ref,
and replay protection. Identity without proof is just a claim.

DITEMPA BUKAN DIBERI — Authority must be proved, not declared.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY STATUS
# ═══════════════════════════════════════════════════════════════════════════════


class IdentityStatus(StrEnum):
    """Canonical identity states."""

    ANONYMOUS = "anonymous"  # No identity claimed
    DECLARED = "declared"  # Identity claimed but unverified
    CHALLENGED = "challenged"  # Verification in progress (nonce sent)
    VERIFIED = "verified"  # Cryptographically verified (signature checks out)
    DEGRADED = "degraded"  # Was verified, now reduced
    REVOKED = "revoked"  # Explicitly invalidated


class DegradationReason(StrEnum):
    """Explicit reasons for identity degradation."""

    VERIFICATION_NOT_PROVIDED = "verification_not_provided"
    VERIFICATION_FAILED = "verification_failed"
    SIGNATURE_INVALID = "signature_invalid"
    NONCE_REPLAYED = "nonce_replayed"
    NONCE_EXPIRED = "nonce_expired"
    TOKEN_EXPIRED = "token_expired"
    SESSION_INVALID = "session_invalid"
    SCOPE_MISMATCH = "scope_mismatch"
    CONSTITUTIONAL_VOID = "constitutional_void"
    EXPLICIT_DOWNGRADE = "explicit_downgrade"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHORITY TIER
# ═══════════════════════════════════════════════════════════════════════════════


class AuthorityTier(IntEnum):
    """What level of authority the actor holds.

    Higher tiers include all lower tier capabilities.
    Tier 0 = read-only observer. Tier 4 = sovereign (Arif only).
    """

    OBSERVER = 0  # Read-only: observe, search, fetch
    OPERATOR = 1  # Read + plan: reason, route, recall
    AGENT = 2  # Read + plan + execute: critique, compose, measure
    JUDGE = 3  # Read + plan + execute + judge: deliberate, seal
    SOVEREIGN = 4  # Full authority: forge, deploy, vault write (ARIF ONLY)

    @classmethod
    def from_string(cls, s: str) -> "AuthorityTier":
        mapping = {
            "observer": cls.OBSERVER,
            "operator": cls.OPERATOR,
            "agent": cls.AGENT,
            "judge": cls.JUDGE,
            "sovereign": cls.SOVEREIGN,
        }
        return mapping.get(s.lower(), cls.OBSERVER)

    @property
    def label(self) -> str:
        return self.name.lower()

    @property
    def may_seal(self) -> bool:
        return self >= AuthorityTier.JUDGE

    @property
    def may_forge(self) -> bool:
        return self >= AuthorityTier.SOVEREIGN

    @property
    def may_judge(self) -> bool:
        return self >= AuthorityTier.JUDGE

    @property
    def may_execute(self) -> bool:
        return self >= AuthorityTier.AGENT


# ═══════════════════════════════════════════════════════════════════════════════
# NONCE — Replay Protection
# ═══════════════════════════════════════════════════════════════════════════════


class Nonce(BaseModel):
    """A cryptographic nonce for replay protection.

    Every session gets a unique nonce. Every signed action binds to this nonce.
    Once used (or expired), the nonce is invalid for further actions.
    """

    value: str = Field(default_factory=lambda: uuid4().hex)
    issued_at: float = Field(default_factory=lambda: __import__("time").time())
    expires_at: float | None = Field(default=None)
    used: bool = Field(default=False)

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        import time

        return time.time() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.used and not self.is_expired

    def consume(self) -> None:
        """Mark this nonce as used (one-time)."""
        self.used = True


# ═══════════════════════════════════════════════════════════════════════════════
# SIGNED IDENTITY — The Full Proof
# ═══════════════════════════════════════════════════════════════════════════════


class SignedIdentity(BaseModel):
    """A complete, verifiable identity proof.

    This is what replaces bare `actor_id="arif-fazil"` with something
    that can be cryptographically verified.

    Fields:
        actor_id: Who this identity claims to be
        authority_tier: What level of authority they hold
        pubkey_ref: Reference to the public key for signature verification
        nonce: Unique nonce bound to this identity assertion
        signature: Ed25519 signature over (actor_id + nonce + timestamp)
        signed_at: When the signature was created
        verified_by: Who verified this identity (kernel, judge, etc.)
    """

    actor_id: str = Field(description="Claimed actor identity")
    authority_tier: AuthorityTier = Field(
        default=AuthorityTier.OBSERVER,
        description="Granted authority level",
    )
    pubkey_ref: str = Field(
        default="",
        description="Reference to the Ed25519 public key (file path or key ID)",
    )
    nonce: Nonce = Field(
        default_factory=Nonce,
        description="Cryptographic nonce for replay protection",
    )
    signature: str = Field(
        default="",
        description="Ed25519 signature over (actor_id + nonce.value + signed_at.isoformat())",
    )
    signed_at: float = Field(
        default_factory=lambda: __import__("time").time(),
        description="Unix timestamp when the signature was created",
    )
    verified_by: str = Field(
        default="",
        description="Entity that verified this identity (arifOS kernel, 888 JUDGE, etc.)",
    )
    verification_method: str = Field(
        default="none",
        description="How verification was performed: none | ed25519 | jwt | oauth",
    )

    @property
    def is_verified(self) -> bool:
        """Has this identity been cryptographically verified?"""
        return bool(self.signature and self.verified_by)

    @property
    def is_sovereign(self) -> bool:
        """Is this the sovereign (Arif)?"""
        return self.authority_tier >= AuthorityTier.SOVEREIGN

    @property
    def signing_payload(self) -> str:
        """The exact string that was (or should be) signed."""
        return f"{self.actor_id}:{self.nonce.value}:{self.signed_at}"

    @field_validator("authority_tier", mode="before")
    @classmethod
    def _coerce_tier(cls, v: object) -> AuthorityTier:
        if isinstance(v, AuthorityTier):
            return v
        if isinstance(v, str):
            return AuthorityTier.from_string(v)
        if isinstance(v, int):
            return AuthorityTier(v)
        return AuthorityTier.OBSERVER


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY CONTEXT — Propagated through the session
# ═══════════════════════════════════════════════════════════════════════════════


class IdentityContext(BaseModel):
    """Immutable identity context propagated through the session.

    This is the single source of truth for who is acting and with what authority.
    Every tool call inherits this context from the session.
    """

    declared_actor_id: str = "anonymous"
    verified_actor_id: str | None = None
    effective_actor_id: str = "anonymous"

    status: IdentityStatus = IdentityStatus.ANONYMOUS
    degradation_reason: DegradationReason | None = None

    authority_tier: AuthorityTier = AuthorityTier.OBSERVER

    # Cryptographic proof (filled after verification)
    signed_identity: SignedIdentity | None = None

    # Session binding
    session_id: str = ""
    iat: int | None = None  # Issued at
    exp: int | None = None  # Expires at

    # Capability grants
    approval_scope: list[str] = Field(default_factory=list)

    @property
    def may_seal(self) -> bool:
        if self.signed_identity is None:
            return False
        return self.signed_identity.authority_tier.may_seal

    @property
    def may_forge(self) -> bool:
        if self.signed_identity is None:
            return False
        return self.signed_identity.authority_tier.may_forge

    @property
    def is_verified(self) -> bool:
        return self.status == IdentityStatus.VERIFIED and self.signed_identity is not None
