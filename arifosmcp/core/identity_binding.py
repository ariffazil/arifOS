"""
arifOS Sovereign Fabric — OAuth/OIDC Identity Binding (Wajib Layer 2)
═══════════════════════════════════════════════════════════════════════

Session identity binding for MCP sessions.
This is the first membrane of authority — "who is allowed to touch the tools."

Currently a stub — maps actor_id to session_id with proof-of-binding.
Full OAuth/OIDC integration will follow when external MCP clients require it.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AuthMethod(str, Enum):
    """How was this identity verified?"""

    NONE = "none"  # No verification (default for internal)
    SESSION = "session"  # Verified via arif_init session
    TOKEN = "token"  # OAuth bearer token
    MTLS = "mtls"  # Mutual TLS certificate
    DPOP = "dpop"  # DPoP proof-of-possession
    DID = "did"  # Decentralized identifier
    SOVEREIGN = "sovereign"  # Human-verified (Arif direct)


@dataclass
class IdentityBinding:
    """
    Binds an actor to a session with proof of identity.

    This is NOT a full OAuth implementation — it's the binding
    contract that tells the policy engine "this actor is who they
    claim to be, verified by this method."
    """

    actor_id: str
    session_id: str
    auth_method: AuthMethod = AuthMethod.SESSION
    verified_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    scope: list[str] = field(default_factory=list)  # What this identity can access
    audience: str = ""  # Intended recipient (MCP server)
    issuer: str = "arifos-kernel"  # Who issued this binding
    binding_hash: str = ""  # SHA-256 of binding proof

    def compute_binding_hash(self) -> str:
        """Compute SHA-256 of the binding for tamper detection."""
        payload = f"{self.actor_id}:{self.session_id}:{self.auth_method}:{self.verified_at}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def seal(self) -> IdentityBinding:
        """Seal the binding — compute hash and mark as sealed."""
        self.binding_hash = self.compute_binding_hash()
        return self

    def is_expired(self) -> bool:
        """Check if this binding has expired."""
        if self.expires_at is None:
            return False  # No expiry set
        return time.time() > self.expires_at

    def has_scope(self, required_scope: str) -> bool:
        """Check if this identity has the required scope."""
        if not self.scope:
            return True  # No scope restrictions
        return required_scope in self.scope

    def to_dict(self) -> dict:
        return {
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "auth_method": self.auth_method.value,
            "verified_at": self.verified_at,
            "expires_at": self.expires_at,
            "scope": self.scope,
            "audience": self.audience,
            "issuer": self.issuer,
            "binding_hash": self.binding_hash,
        }


# ── Identity Registry ──────────────────────────────────────────────────

_bindings: dict[str, IdentityBinding] = {}  # session_id → binding


def register_identity(binding: IdentityBinding) -> IdentityBinding:
    """Register an identity binding for a session."""
    binding.seal()
    _bindings[binding.session_id] = binding
    return binding


def verify_identity(session_id: str, actor_id: str) -> bool:
    """Verify that a session is bound to the claimed actor."""
    binding = _bindings.get(session_id)
    if binding is None:
        return False
    if binding.is_expired():
        return False
    if binding.actor_id != actor_id:
        return False
    return True


def get_identity(session_id: str) -> Optional[IdentityBinding]:
    """Get the identity binding for a session."""
    return _bindings.get(session_id)


def revoke_identity(session_id: str) -> bool:
    """Revoke an identity binding."""
    if session_id in _bindings:
        del _bindings[session_id]
        return True
    return False
