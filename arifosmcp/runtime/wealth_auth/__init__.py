"""
Federation Authorization Middleware (audit-4 PR2).

Honors the audit's verdict:
  - WEALTH (and every other organ) must NEVER create a session.
  - AAA / MCP creates the governed session.
  - arifOS issues the signed capability token.
  - Each organ's protected tool calls `authorize(...)` here.
  - This module verifies token + audience + capability + expiry + replay
    and rejects with the audit's structured error contract.

Single source of truth: every protected tool goes through `authorize(...)`.
No tool implements its own auth logic. Verified by `tests/runtime/test_no_inline_auth.py`.

F1 AMANAH: additive module. The legacy WEALTH MCP endpoints still work
unchanged; new tools adopt the middleware at their own pace.
"""

from .authorize import authorize, error_to_envelope
from .exceptions import (
    ActorNotBound,
    AuthError,
    CapabilityNotGranted,
    EvidenceInsufficient,
    HumanRatificationRequired,
    ReplayDetected,
    Revoked,
    SessionRequired,
    TokenExpired,
    TokenInvalid,
    WrongAudience,
)
from .stateful_middleware import bound_call, extract_envelope
from .token_validation import TokenClaims, extract_bearer, issue_token, validate_token

__all__ = [
    "AuthError",
    "SessionRequired",
    "TokenInvalid",
    "TokenExpired",
    "WrongAudience",
    "CapabilityNotGranted",
    "ActorNotBound",
    "ReplayDetected",
    "Revoked",
    "EvidenceInsufficient",
    "HumanRatificationRequired",
    "validate_token",
    "extract_bearer",
    "TokenClaims",
    "issue_token",
    "authorize",
    "error_to_envelope",
    "bound_call",
    "extract_envelope",
]
