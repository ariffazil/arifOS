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
    def from_string(cls, s: str) -> AuthorityTier:
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


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL IDENTITY NORMALIZATION (P0 — AGENTIC CLOSURE)
# ═══════════════════════════════════════════════════════════════════════════════

# Known canonical actor identities. All ingress identity strings must resolve
# to one of these. Case-insensitive matching with alias resolution.
# "arif", "Arif", " ARIF " -> "ARIF" with sovereign authority.
CANONICAL_ACTORS: dict[str, dict[str, str | list[str]]] = {
    "ARIF": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "SOVEREIGN",
        "aliases": ["arif", "Arif", "arif-fazil", "ariffazil"],
    },
    "FORGE": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["forge", "a-forge", "000", "000Ω"],
    },
    "AUDITOR": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["auditor", "a-audit", "ψ"],
    },
    "OPS": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "OPERATOR",
        "aliases": ["ops", "🌐"],
    },
    "PLAN": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["plan", "planner", "Ω"],
    },
    "AAAGW": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "OPERATOR",
        "aliases": ["aaa", "aaa-gateway", "cockpit"],
    },
    "HERMES": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["hermes", "hermes-asi"],
    },
    "OPENCODE": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["opencode", "OpenCode", "opencode-333", "333-agi", "333"],
    },
    "codex": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["codex", "codex-cli", "FI-005", "FI-005-codex-cli"],
    },
    # F1 AMANAH · Tier-A identity registration (calibration session 2026-08-01).
    # Fingerprint a1d4971c986c1642 · Ed25519 public key at
    # /root/AAA/IDENTITY/keys/FI-008_public.pem.
    # Reversible: delete this block + restore the .bak file.
    "FI-008": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["FI-008", "fi-008", "kimi-code-fi008", "kimi-code"],
    },
    # T3 grant 2026-08-07 by 888 SOVEREIGN: register SOTCRON as Tier-A identity.
    # Federation SOT/Drift cron — continuous World Model vault bridge.
    # Ed25519 public key fingerprint matches did:arif:sot-cron in
    # /opt/arifos/secrets/did-registry.json. DPoP+registry promotion channel
    # gates actual seal authority — this entry only grants identity normalization.
    "SOTCRON": {
        "sovereign_id": "ARIF_FAZIL",
        "default_tier": "AGENT",
        "aliases": ["SOTCRON", "sot-cron", "sotcron"],
    },
}


_NORMALIZATION_CACHE: dict[str, str | None] = {}
_MAX_CACHE_SIZE = 256


def normalize_actor_identity(
    raw_actor_id: str | None,
) -> dict[str, object]:
    """Normalize a raw actor identity string to canonical form.

    Normalization does NOT imply verification. This function only maps
    case variants and known aliases to the canonical identifier.
    Cryptographic verification is a separate step.

    Returns:
        CanonicalIdentity with fields:
          raw:             Original input string (or None)
          normalized:      Canonical actor ID (or None if unrecognised)
          sovereign_id:    Sovereign that governs this actor
          verification_state: 'UNVERIFIED' | 'VERIFIED' | 'REJECTED'
          normalization_version: Schema version
    """
    if not raw_actor_id or not isinstance(raw_actor_id, str):
        return {
            "raw": raw_actor_id,
            "normalized": None,
            "sovereign_id": None,
            "verification_state": "REJECTED",
            "normalization_version": "1",
        }

    stripped = raw_actor_id.strip()

    # Check cache first
    cache_key = stripped.lower()
    if cache_key in _NORMALIZATION_CACHE:
        normalized = _NORMALIZATION_CACHE[cache_key]
        if normalized is None:
            return {
                "raw": raw_actor_id,
                "normalized": None,
                "sovereign_id": None,
                "verification_state": "REJECTED",
                "normalization_version": "1",
            }
        canon = CANONICAL_ACTORS[normalized]
        return {
            "raw": raw_actor_id,
            "normalized": normalized,
            "sovereign_id": canon.get("sovereign_id"),
            "verification_state": "UNVERIFIED",
            "normalization_version": "1",
        }

    # Linear scan through canonical actors
    for canonical_id, info in CANONICAL_ACTORS.items():
        # Exact match (case-insensitive)
        if stripped.lower() == canonical_id.lower():
            _set_cache(cache_key, canonical_id)
            return {
                "raw": raw_actor_id,
                "normalized": canonical_id,
                "sovereign_id": info.get("sovereign_id"),
                "verification_state": "UNVERIFIED",
                "normalization_version": "1",
            }
        # Alias match
        for alias in info.get("aliases", []):
            if isinstance(alias, str) and stripped.lower() == alias.lower():
                _set_cache(cache_key, canonical_id)
                return {
                    "raw": raw_actor_id,
                    "normalized": canonical_id,
                    "sovereign_id": info.get("sovereign_id"),
                    "verification_state": "UNVERIFIED",
                    "normalization_version": "1",
                }

    # No match found — reject
    _set_cache(cache_key, None)
    return {
        "raw": raw_actor_id,
        "normalized": None,
        "sovereign_id": None,
        "verification_state": "REJECTED",
        "normalization_version": "1",
    }


def _set_cache(key: str, value: str | None) -> None:
    """Cache with LRU-like eviction (simple size cap)."""
    if len(_NORMALIZATION_CACHE) >= _MAX_CACHE_SIZE:
        # Evict oldest entry
        _NORMALIZATION_CACHE.pop(next(iter(_NORMALIZATION_CACHE)))
    _NORMALIZATION_CACHE[key] = value


def normalize_session_actor(
    raw_actor_id: str | None,
    session_token: str | None = None,
) -> dict[str, object]:
    """Full session identity resolution: normalization + optional token hint.

    Returns the same shape as normalize_actor_identity but allows
    session-level identity inference from token context.
    """
    result = normalize_actor_identity(raw_actor_id)

    # If normalization rejected and a session token exists,
    # attempt token-based identity inference
    if result["normalized"] is None and session_token:
        # Token prefix-based canonical mapping
        token_prefixes: dict[str, str] = {
            "arif_": "ARIF",
            "forge_": "FORGE",
            "audit_": "AUDITOR",
            "ops_": "OPS",
            "plan_": "PLAN",
            "aaa_": "AAAGW",
            "hermes_": "HERMES",
        }
        for prefix, canonical_id in token_prefixes.items():
            if session_token.lower().startswith(prefix):
                return {
                    "raw": raw_actor_id,
                    "normalized": canonical_id,
                    "sovereign_id": CANONICAL_ACTORS[canonical_id].get("sovereign_id"),
                    "verification_state": "UNVERIFIED",
                    "normalization_version": "1",
                }

    return result
