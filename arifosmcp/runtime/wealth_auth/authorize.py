"""
authorize() — the single gate every protected tool must call.

Audit-4 PR2: ONE function, no tool implements its own auth logic. The
gate validates:

  - signature
  - issuer (must be the sovereign root)
  - audience (must contain the calling organ)
  - expiry and not-before
  - per-jti replay protection
  - required capability is granted in the token
  - minimum authority_band is met
  - actor_id is bound (no caller-supplied actor — see audit note)
  - per-tool public_simulation opt-in for "Authorization: Bearer none"

Errors are returned via the audit-4 structured envelope (errors.schema.json).
"""

from __future__ import annotations

from typing import Any, Iterable

from .exceptions import (
    AuthError,
    CapabilityNotGranted,
    SessionRequired,
    WrongAudience,
)
from .token_validation import TokenClaims, validate_token

AUTHORITY_BANDS = ("OBSERVER", "OPERATOR", "SOVEREIGN")
_BAND_ORDER = {b: i for i, b in enumerate(AUTHORITY_BANDS)}


def _band_sufficient(token_band: str, required_band: str) -> bool:
    a = _BAND_ORDER.get(token_band, -1)
    b = _BAND_ORDER.get(required_band, 99)
    return a >= b


def authorize(
    *,
    authorization_header: str | None,
    audience: str,
    required_capability: str,
    minimum_authority: str = "OPERATOR",
    public_simulation: bool = False,
    actor_override: dict[str, Any] | None = None,
) -> TokenClaims:
    """Validate the bearer token. Returns TokenClaims on success. Raises AuthError on failure.

    `actor_override` is FORBIDDEN in normal flows — actor MUST come from the signed
    token. It is allowed only by the kernel's own bootstrap path and is
    flagged when used.
    """
    if not authorization_header:
        raise SessionRequired(
            "A governed session is required for this capability.",
            required_action="INITIALIZE_SESSION_AT_AAA_OR_MCP_GATEWAY",
            requested_capability=required_capability,
        )
    if actor_override is not None:
        # The audit says: "Do not trust caller-supplied actor_id when supplied only
        # by the caller." We honor that — the override is logged and ignored.
        # Only the signed token's actor counts.
        import logging

        logging.getLogger(__name__).warning(
            "authorize: actor_override was supplied but is being ignored; "
            "actor comes from the signed token."
        )
    claims = validate_token(authorization_header)
    if claims.actor_id == "" and claims.issuer == "":
        # Public-simulation path. We accept only if the tool opted in.
        if not public_simulation:
            raise SessionRequired(
                f"Public-simulation mode is not allowed for capability {required_capability!r}.",
                required_action="INITIALIZE_SESSION_AT_AAA_OR_MCP_GATEWAY",
                requested_capability=required_capability,
            )
        # Public simulation: actor is anonymous, no authority.
        return claims
    if not claims.is_for_audience(audience):
        raise WrongAudience(
            f"Token audience {claims.audience!r} does not contain calling organ {audience!r}.",
            requested_capability=required_capability,
            actor_id=claims.actor_id,
            session_id=claims.session_id,
        )
    if claims.is_expired():
        from .exceptions import TokenExpired

        raise TokenExpired(
            f"Token expired at epoch {claims.expires_at}.",
            requested_capability=required_capability,
            actor_id=claims.actor_id,
            session_id=claims.session_id,
        )
    if claims.is_not_yet_valid():
        from .exceptions import TokenInvalid

        raise TokenInvalid(
            f"Token not yet valid (nbf epoch {claims.not_before}).",
            requested_capability=required_capability,
            actor_id=claims.actor_id,
            session_id=claims.session_id,
        )
    if not claims.has_capability(required_capability):
        raise CapabilityNotGranted(
            f"Token does not grant capability {required_capability!r}.",
            required_action="REQUEST_NEW_TOKEN_WITH_REQUIRED_CAPABILITY",
            requested_capability=required_capability,
            actor_id=claims.actor_id,
            session_id=claims.session_id,
        )
    if not _band_sufficient(claims.authority_band, minimum_authority):
        raise CapabilityNotGranted(
            f"Token authority band {claims.authority_band!r} is below required {minimum_authority!r}.",
            required_action="REQUEST_NEW_TOKEN_WITH_HIGHER_AUTHORITY",
            requested_capability=required_capability,
            actor_id=claims.actor_id,
            session_id=claims.session_id,
        )
    return claims


def error_to_envelope(exc: Exception) -> dict[str, Any]:
    """Convert any AuthError to the audit-shaped error envelope.

    Tool code calls `try: ... except AuthError as e: return JSONResponse(error_to_envelope(e))`.
    """
    if isinstance(exc, AuthError):
        return exc.to_envelope()
    return {
        "status": "ERROR",
        "error_code": "INTERNAL_ERROR",
        "message": f"{type(exc).__name__}: {exc}",
        "retryable": False,
        "mutation_occurred": False,
    }
