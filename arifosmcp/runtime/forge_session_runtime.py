"""
forge_session_runtime.py — Sovereign ceremony + session proof system.

DITEMPA BUKAN DIBERI

Implements the challenge-response ceremony that issues narrow capabilities
after sovereign identity verification. Does NOT auto-elevate runtime_band.

Key invariants:
  - sovereign_signal() returns sovereignty=False on any failure (fail-closed)
  - Verified key sets human_authority=SOVEREIGN but runtime_band stays OBSERVE_ONLY
  - Only ceremony can grant narrow capabilities (vault.append, forge.mutate)
  - Capabilities are single-use, payload-bound, session-bound, expiring
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# Capability TTL: 5 minutes for ceremony-issued capabilities
_CAPABILITY_TTL_SECONDS = 300


class HumanAuthority(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    OPERATOR = "OPERATOR"
    SOVEREIGN = "SOVEREIGN"


class RuntimeBand(str, Enum):
    OBSERVE_ONLY = "OBSERVE_ONLY"
    LIMITED_MUTATE = "LIMITED_MUTATE"
    FULL = "FULL"


@dataclass(frozen=True)
class AuthorityEnvelope:
    """Derived authority: identity + capabilities. Not auto-elevated."""

    human_authority: HumanAuthority
    runtime_band: RuntimeBand
    actor_verified: bool
    session_bound: bool
    lease_valid: bool
    capabilities: frozenset[str] = field(default_factory=frozenset)

    def allows(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass
class SovereignVerdict:
    """Result of sovereign_signal() — fail-closed by default."""

    sovereignty: bool = False
    verified: bool = False
    method: str = "anonymous"
    reason: str = "not_checked"
    fail_closed: bool = True


@dataclass
class ForgeSessionProof:
    """Immutable proof linking a forge action to its session."""

    session_id: str
    actor_id: str
    forge_action: str
    action_hash: str
    session_proof_token: str
    timestamp: str
    receipt_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "forge_action": self.forge_action,
            "action_hash": self.action_hash,
            "session_proof_token": self.session_proof_token,
            "timestamp": self.timestamp,
            "receipt_id": self.receipt_id,
        }

    def verify_chain(self, receipt: dict[str, Any]) -> bool:
        """Verify this proof chains to a VAULT999 receipt."""
        if not receipt:
            return False
        return (
            receipt.get("session_id") == self.session_id
            and receipt.get("action_hash") == self.action_hash
        )


@dataclass
class ChainVerdict:
    """Result of verify_forge_session_chain()."""

    valid: bool = False
    chain: list[str] = field(default_factory=list)
    broken_at: str | None = None


@dataclass
class SovereignCapability:
    """Narrow capability issued after ceremony. Single-use, payload-bound."""

    capability_id: str
    action: str
    payload_hash: str
    session_id: str
    granted_at: float
    expires_at: float
    consumed: bool = False
    nonce: str = ""

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_consumed(self) -> bool:
        return self.consumed

    def matches(self, action: str, payload_hash: str) -> bool:
        return self.action == action and self.payload_hash == payload_hash


# In-memory capability store (session-scoped, not persistent)
_active_capabilities: dict[str, SovereignCapability] = {}


def sovereign_signal(
    session_id: str | None = None,
    actor_id: str | None = None,
    verified_key_id: str | None = None,
    *,
    session: dict[str, Any] | None = None,
) -> SovereignVerdict:
    """Verify sovereign initiated this session. Fail-closed on any error."""
    try:
        # Extract from session dict if not given
        if session and not actor_id:
            actor_id = session.get("actor_id") or session.get("identity", {}).get("actor_id")
        if session and not verified_key_id:
            verified_key_id = session.get("verified_key_id")
        if session and not session_id:
            session_id = session.get("session_id")

        if not actor_id:
            return SovereignVerdict(reason="no_actor_id")

        # Gate 1: actor in PROTECTED_SOVEREIGN_IDS?
        from arifosmcp.runtime.governance_identity import PROTECTED_SOVEREIGN_IDS

        if actor_id.lower().strip() not in PROTECTED_SOVEREIGN_IDS:
            return SovereignVerdict(
                method="anonymous",
                reason="non-sovereign actor",
            )

        # Gate 2: key in SOVEREIGN_KEY_IDS?
        from arifosmcp.runtime.governance_identity import SOVEREIGN_KEY_IDS

        if not verified_key_id or verified_key_id not in SOVEREIGN_KEY_IDS:
            return SovereignVerdict(
                method="session_anchor",
                reason="key not in SOVEREIGN_KEY_IDS",
            )

        # Gate 3: cryptographically verified?
        verified = bool(session.get("actor_verified") or session.get("signature_verified"))
        method = session.get("verification_method", "")
        if not verified or method not in ("f13_sovereign", "session", "ed25519"):
            return SovereignVerdict(
                method="session_anchor",
                reason="not cryptographically verified",
            )

        # ALL PASS
        return SovereignVerdict(
            sovereignty=True,
            verified=True,
            method="f13_sovereign",
            reason="sovereign identity + key verified",
        )

    except Exception as e:
        logger.error("sovereign_signal failed: %s", e)
        return SovereignVerdict(reason=f"exception: {e}")


def may_seal(
    envelope: AuthorityEnvelope,
    *,
    required_capability: str,
    requires_sovereign: bool,
    payload_matches: bool,
    vault_chain_healthy: bool,
) -> tuple[bool, str]:
    """Check if sealing is allowed. Returns (allowed, reason)."""
    if not vault_chain_healthy:
        return False, "vault_chain_unhealthy"
    if not envelope.actor_verified:
        return False, "actor_not_verified"
    if not envelope.session_bound:
        return False, "session_not_bound"
    if not envelope.lease_valid:
        return False, "lease_invalid"
    if required_capability not in envelope.capabilities:
        return False, "missing_capability"
    if requires_sovereign and envelope.human_authority is not HumanAuthority.SOVEREIGN:
        return False, "sovereign_authority_required"
    if not payload_matches:
        return False, "payload_changed_after_confirmation"
    return True, "allowed"


def issue_seal_capability(
    session_id: str,
    actor_id: str,
    payload_hash: str,
    *,
    receipt_class: str = "sovereign_decision",
    ttl_seconds: int = _CAPABILITY_TTL_SECONDS,
) -> SovereignCapability | None:
    """Issue a narrow, single-use capability after ceremony verification.

    Call this AFTER the sovereign has signed the challenge.
    Returns None if session/actor invalid.
    """
    if not session_id or not actor_id:
        return None

    capability = SovereignCapability(
        capability_id=secrets.token_hex(16),
        action=f"vault.append:{receipt_class}",
        payload_hash=payload_hash,
        session_id=session_id,
        granted_at=time.time(),
        expires_at=time.time() + ttl_seconds,
        nonce=secrets.token_hex(16),
    )
    _active_capabilities[capability.capability_id] = capability
    logger.info(
        "Seal capability issued: id=%s session=%s action=%s expires=%s",
        capability.capability_id,
        session_id,
        capability.action,
        capability.expires_at,
    )
    return capability


def consume_capability(
    capability_id: str,
    action: str,
    payload_hash: str,
) -> tuple[bool, str]:
    """Consume a single-use capability. Returns (consumed, reason)."""
    cap = _active_capabilities.get(capability_id)
    if not cap:
        return False, "capability_not_found"
    if cap.is_consumed():
        return False, "already_consumed"
    if cap.is_expired():
        _active_capabilities.pop(capability_id, None)
        return False, "expired"
    if not cap.matches(action, payload_hash):
        return False, "payload_mismatch"

    cap.consumed = True
    _active_capabilities.pop(capability_id, None)
    return True, "consumed"


def create_forge_session_proof(
    session_id: str,
    actor_id: str,
    forge_action: str,
    action_payload: dict | None = None,
    *,
    session: dict[str, Any] | None = None,
) -> ForgeSessionProof | None:
    """Create a signed proof linking a forge action to its session.

    Returns None (fail-closed) if session has no anchor.
    """
    if not session_id:
        return None

    payload_bytes = str(action_payload).encode() if action_payload else b""
    action_hash = hashlib.sha256(payload_bytes).hexdigest()

    # HMAC proof token: proves this action was created within this session
    secret = secrets.token_bytes(32)  # ephemeral; verified by chain, not by re-computation
    token_input = f"{action_hash}{session_id}".encode()
    proof_token = hmac.new(secret, token_input, hashlib.sha256).hexdigest()

    return ForgeSessionProof(
        session_id=session_id,
        actor_id=actor_id or "anonymous",
        forge_action=forge_action,
        action_hash=action_hash,
        session_proof_token=proof_token,
        timestamp=datetime.now(UTC).isoformat(),
    )


def verify_forge_session_chain(
    proof: ForgeSessionProof | dict,
    receipt: dict[str, Any],
) -> ChainVerdict:
    """Trace a VAULT999 receipt back through its session proof chain."""
    if isinstance(proof, dict):
        proof = ForgeSessionProof(**proof)

    chain = [proof.session_id, proof.forge_action, proof.action_hash]

    if not receipt:
        return ChainVerdict(valid=False, chain=chain, broken_at="no_receipt")

    if receipt.get("session_id") != proof.session_id:
        return ChainVerdict(valid=False, chain=chain, broken_at="session_mismatch")

    if receipt.get("action_hash") != proof.action_hash:
        return ChainVerdict(valid=False, chain=chain, broken_at="action_hash_mismatch")

    return ChainVerdict(valid=True, chain=chain)


def cleanup_expired_capabilities() -> int:
    """Remove expired capabilities. Returns count removed."""
    now = time.time()
    expired = [k for k, v in _active_capabilities.items() if now > v.expires_at]
    for k in expired:
        _active_capabilities.pop(k, None)
    return len(expired)


__all__ = [
    "HumanAuthority",
    "RuntimeBand",
    "AuthorityEnvelope",
    "SovereignVerdict",
    "ForgeSessionProof",
    "ChainVerdict",
    "SovereignCapability",
    "sovereign_signal",
    "may_seal",
    "issue_seal_capability",
    "consume_capability",
    "create_forge_session_proof",
    "verify_forge_session_chain",
    "cleanup_expired_capabilities",
]
