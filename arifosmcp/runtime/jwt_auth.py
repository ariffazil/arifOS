"""
arifosmcp/runtime/jwt_auth.py — Constitutional JWT Verification Engine (Phase 1)

Enforces identity-before-governance for all constitutional boundaries.
Supports Supabase Auth (RS256) and self-issued internal tokens (HS256).

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import contextvars
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any

import jwt as pyjwt
from jwt.algorithms import RSAAlgorithm

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────

JWT_ENFORCE_MODE = os.getenv("JWT_ENFORCE_MODE", "observe").strip().lower()
# "enforce"  → block on JWT failure
# "observe"  → log violations, allow through (default for migration)
# "off"      → disabled (emergency only)

TRUSTED_ISSUERS = [
    iss.strip()
    for iss in os.getenv("JWT_TRUSTED_ISSUERS", "https://arifos.supabase.co,arifos-internal").split(
        ","
    )
    if iss.strip()
]

SUPABASE_JWKS_URL = os.getenv("SUPABASE_JWKS_URL", "").strip()
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "arifOS")
CLOCK_SKEW_MAX = int(os.getenv("JWT_CLOCK_SKEW_MAX", "60"))

# Internal service secrets — per-service compartmentalization
# Env pattern: ARIFOS_INTERNAL_SECRET_<UPPERCASE_SERVICE_NAME>
# e.g. ARIFOS_INTERNAL_SECRET_SENTINELWATCH, ARIFOS_INTERNAL_SECRET_WELL


def _get_internal_secret(service_name: str) -> str | None:
    """Retrieve per-service internal secret. Returns None if not configured."""
    env_name = f"ARIFOS_INTERNAL_SECRET_{service_name.upper().replace('-', '_')}"
    secret = os.getenv(env_name, "").strip()
    if secret:
        return secret
    # Fallback: try legacy global secret (deprecated, warn)
    legacy = os.getenv("ARIFOS_INTERNAL_SECRET", "").strip()
    if legacy:
        logger.warning(
            "Using legacy ARIFOS_INTERNAL_SECRET for %s — migrate to per-service secret %s",
            service_name,
            env_name,
        )
        return legacy
    return None


# ── JWKS Cache ─────────────────────────────────────────────────────────────

_jwks_cache: dict[str, Any] = {}
_jwks_fetched_at: float = 0.0
_JWKS_TTL_SECONDS = 300


def _fetch_jwks() -> dict[str, Any]:
    """Fetch JWKS from Supabase. Cached with TTL."""
    global _jwks_cache, _jwks_fetched_at

    now = time.monotonic()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_TTL_SECONDS:
        return _jwks_cache

    if not SUPABASE_JWKS_URL:
        logger.warning("SUPABASE_JWKS_URL not set — cannot fetch JWKS")
        return {}

    try:
        import urllib.request

        req = urllib.request.Request(
            SUPABASE_JWKS_URL,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # nosec B310
            data = json.loads(resp.read().decode("utf-8"))
            _jwks_cache = data
            _jwks_fetched_at = now
            logger.info(
                "JWKS fetched from %s — keys: %s", SUPABASE_JWKS_URL, len(data.get("keys", []))
            )
            return data  # type: ignore[no-any-return]
    except Exception as e:
        logger.warning("JWKS fetch failed: %s — using cached/stale keys", e)
        return _jwks_cache


def _get_rsa_key(kid: str) -> Any | None:
    """Resolve RSA public key from JWKS by kid."""
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            try:
                return RSAAlgorithm.from_jwk(json.dumps(key))
            except Exception as e:
                logger.error("Failed to parse JWK for kid=%s: %s", kid, e)
                return None
    logger.warning("No JWKS key found for kid=%s", kid)
    return None


# ── Token Verification ─────────────────────────────────────────────────────


class JWTVerificationResult:
    """Structured result from JWT verification."""

    def __init__(
        self,
        valid: bool,
        claims: dict[str, Any] | None = None,
        error: str = "",
        auth_method: str = "",
    ):
        self.valid = valid
        self.claims = claims or {}
        self.error = error
        self.auth_method = auth_method

    def to_auth_lineage(self) -> dict[str, Any] | None:
        """Produce auth_lineage snapshot for VAULT seals."""
        if not self.valid:
            return None
        return {
            "sub": self.claims.get("sub"),
            "iss": self.claims.get("iss"),
            "kid": self.claims.get("kid"),
            "auth_method": self.auth_method,
        }


def verify_jwt(token: str, expected_actor_id: str | None = None) -> JWTVerificationResult:
    """
    Verify a JWT token against constitutional invariants.

    Supports:
    - Supabase Auth tokens (RS256, verified via JWKS)
    - Self-issued internal tokens (HS256, verified via per-service secret)

    Returns JWTVerificationResult with claims or error description.
    """
    if JWT_ENFORCE_MODE == "off":
        return JWTVerificationResult(valid=True, claims={}, auth_method="disabled")

    if not token or not token.strip():
        return JWTVerificationResult(valid=False, error="missing_token")

    # ── Parse unverified header to determine issuer/key type ──────────────
    try:
        unverified_header = pyjwt.get_unverified_header(token)
        unverified_claims = pyjwt.decode(token, options={"verify_signature": False})
    except pyjwt.PyJWTError as e:
        return JWTVerificationResult(valid=False, error=f"malformed_token: {e}")

    alg = unverified_header.get("alg", "")

    # ── Route by algorithm ────────────────────────────────────────────────
    if alg == "RS256":
        return _verify_supabase_jwt(token, unverified_header, unverified_claims, expected_actor_id)
    elif alg == "HS256":
        return _verify_internal_jwt(token, unverified_header, unverified_claims, expected_actor_id)
    else:
        return JWTVerificationResult(valid=False, error=f"unsupported_algorithm: {alg}")


def _verify_supabase_jwt(
    token: str,
    header: dict[str, Any],
    claims: dict[str, Any],
    expected_actor_id: str | None,
) -> JWTVerificationResult:
    """Verify a Supabase-issued RS256 token."""
    kid = header.get("kid", "")
    if not kid:
        return JWTVerificationResult(valid=False, error="missing_kid")

    public_key = _get_rsa_key(kid)
    if not public_key:
        return JWTVerificationResult(valid=False, error="jwks_key_not_found")

    try:
        verified = pyjwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=JWT_AUDIENCE,
            issuer=(
                "https://arifos.supabase.co" if "arifos.supabase.co" in TRUSTED_ISSUERS else None
            ),
            options={"require": ["exp", "iat", "sub", "iss"]},
            leeway=CLOCK_SKEW_MAX,
        )
    except pyjwt.ExpiredSignatureError:
        return JWTVerificationResult(valid=False, error="expired")
    except pyjwt.InvalidAudienceError:
        return JWTVerificationResult(valid=False, error="invalid_audience")
    except pyjwt.InvalidIssuerError:
        return JWTVerificationResult(valid=False, error="invalid_issuer")
    except pyjwt.PyJWTError as e:
        return JWTVerificationResult(valid=False, error=f"signature_verification_failed: {e}")

    # ── Invariant checks ──────────────────────────────────────────────────
    iss = verified.get("iss", "")
    if iss not in TRUSTED_ISSUERS:
        return JWTVerificationResult(valid=False, error="untrusted_issuer")

    sub = verified.get("sub", "")
    if expected_actor_id is not None and sub != expected_actor_id:
        return JWTVerificationResult(
            valid=False,
            error=f"actor_id_mismatch: expected={expected_actor_id}, jwt.sub={sub}",
        )

    return JWTVerificationResult(
        valid=True,
        claims=verified,
        auth_method="jwt_supabase",
    )


def _verify_internal_jwt(
    token: str,
    header: dict[str, Any],
    claims: dict[str, Any],
    expected_actor_id: str | None,
) -> JWTVerificationResult:
    """Verify a self-issued HS256 internal token."""
    sub = claims.get("sub", "")
    if not sub.startswith("system:"):
        return JWTVerificationResult(valid=False, error="internal_token_missing_system_prefix")

    service_name = sub.split(":", 1)[1]
    secret = _get_internal_secret(service_name)
    if not secret:
        return JWTVerificationResult(
            valid=False, error=f"internal_secret_not_configured: {service_name}"
        )

    try:
        verified = pyjwt.decode(
            token,
            key=secret,
            algorithms=["HS256"],
            audience=JWT_AUDIENCE,
            issuer="arifos-internal",
            options={"require": ["exp", "iat", "sub", "iss"]},
            leeway=CLOCK_SKEW_MAX,
        )
    except pyjwt.ExpiredSignatureError:
        return JWTVerificationResult(valid=False, error="expired")
    except pyjwt.PyJWTError as e:
        return JWTVerificationResult(valid=False, error=f"signature_verification_failed: {e}")

    # ── Invariant checks ──────────────────────────────────────────────────
    iss = verified.get("iss", "")
    if iss != "arifos-internal":
        return JWTVerificationResult(valid=False, error="untrusted_internal_issuer")

    if expected_actor_id is not None and verified.get("sub") != expected_actor_id:
        return JWTVerificationResult(
            valid=False,
            error=f"actor_id_mismatch: expected={expected_actor_id}, jwt.sub={verified.get('sub')}",
        )

    return JWTVerificationResult(
        valid=True,
        claims=verified,
        auth_method="jwt_internal",
    )


# ── Observe Mode Logging ───────────────────────────────────────────────────


_jwt_violation_log: list[dict[str, Any]] = []
_MAX_VIOLATION_LOG = 1000


def log_violation(
    token_preview: str,
    error: str,
    path: str = "",
    actor_id: str | None = None,
) -> None:
    """Log a JWT verification violation for observe-mode analysis."""
    global _jwt_violation_log

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token_preview": token_preview,
        "error": error,
        "path": path,
        "actor_id": actor_id,
        "enforce_mode": JWT_ENFORCE_MODE,
    }
    _jwt_violation_log.append(entry)
    if len(_jwt_violation_log) > _MAX_VIOLATION_LOG:
        _jwt_violation_log = _jwt_violation_log[-_MAX_VIOLATION_LOG:]

    logger.warning(
        "JWT_VIOLATION [mode=%s] error=%s path=%s actor_id=%s token_preview=%s",
        JWT_ENFORCE_MODE,
        error,
        path,
        actor_id,
        token_preview,
    )


def get_violation_stats() -> dict[str, Any]:
    """Return violation statistics for observe-mode readiness check."""
    total = len(_jwt_violation_log)
    by_error: dict[str, int] = {}
    for v in _jwt_violation_log:
        by_error[v["error"]] = by_error.get(v["error"], 0) + 1

    return {
        "total_violations": total,
        "by_error": by_error,
        "enforce_mode": JWT_ENFORCE_MODE,
        "ready_for_enforce": total == 0,
    }


# ── Convenience: Check if in enforce mode ──────────────────────────────────


def is_enforce_mode() -> bool:
    return JWT_ENFORCE_MODE == "enforce"


def is_observe_mode() -> bool:
    return JWT_ENFORCE_MODE == "observe"


# ── Request-scoped auth lineage (async-safe via contextvars) ───────────────

_current_auth_lineage: contextvars.ContextVar[dict[str, Any] | None] = contextvars.ContextVar(
    "arifos_auth_lineage", default=None
)


def set_request_auth_lineage(lineage: dict[str, Any] | None) -> None:
    """Set auth lineage for the current request context."""
    _current_auth_lineage.set(lineage)


def get_request_auth_lineage() -> dict[str, Any] | None:
    """Get auth lineage for the current request context."""
    return _current_auth_lineage.get(None)
