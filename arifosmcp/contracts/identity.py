"""
arifosmcp/contracts/identity.py — Canonical Identity Continuity (Audit Fix 1)

Rule 3: One source of truth per concern. 
Identity must be normalized once and propagated immutably.
"""

from enum import Enum
from pydantic import BaseModel, Field

class IdentityStatus(str, Enum):
    """Canonical identity states."""
    ANONYMOUS = "anonymous"
    DECLARED = "declared"  # Has declared_name but unverified
    VERIFIED = "verified"  # Cryptographically verified
    DEGRADED = "degraded"  # Was higher, now reduced (CRITICAL: explicit)
    REVOKED = "revoked"    # Explicitly invalidated

class DegradationReason(str, Enum):
    """Explicit reasons for identity degradation."""
    VERIFICATION_NOT_PROVIDED = "verification_not_provided"
    VERIFICATION_FAILED = "verification_failed"
    TOKEN_EXPIRED = "token_expired"
    SESSION_INVALID = "session_invalid"
    SCOPE_MISMATCH = "scope_mismatch"
    CONSTITUTIONAL_VOID = "constitutional_void"
    EXPLICIT_DOWNGRADE = "explicit_downgrade"

class IdentityContext(BaseModel):
    """
    Audit Fix 1: Immutable Identity Context.
    Ensures 'arif' remains 'arif' across the trinity.
    """
    declared_actor_id: str = "anonymous"
    verified_actor_id: str | None = None
    effective_actor_id: str = "anonymous"
    
    status: IdentityStatus = IdentityStatus.ANONYMOUS
    degradation_reason: DegradationReason | None = None
    
    # Audit trail fields (F11)
    session_id: str
    iat: int | None = None
    exp: int | None = None
    approval_scope: list[str] = Field(default_factory=list)
