"""
arifosmcp/runtime/jwt_auth.py — Constitutional JWT Verification Engine (Phase 1)

Enforces identity-before-governance for all constitutional boundaries.
Supports Supabase Auth (RS256) and self-issued internal tokens (HS256).

v2026.05.05-SSCT — SSCT: Sole Source, Floor Rebalancing, Schema I/O Canonicalization:
- log_violation() writes to both in-memory cache AND durable JSONL
- query_violations() reads from durable JSONL (source of truth)
- get_durable_violation_stats() replaces get_violation_stats() for enforce readiness
- _jwt_violation_log is cache only — never source of truth for enforce readiness

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
from jwt.algorithms import ECAlgorithm, RSAAlgorithm

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────

JWT_ENFORCE_MODE = os.getenv("JWT_ENFORCE_MODE", "observe").strip().lower()
# "enforce"  → block on JWT failure
# "observe"   → log violations, allow through (default for migration)
# "off"       → disabled (emergency only)

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


# ── Durable Telemetry Configuration ─────────────────────────────────────────

TELEMETRY_PATH = os.getenv("TELEMETRY_PATH", "/app/telemetry")
VIOLATION_LOGFILE = os.path.join(TELEMETRY_PATH, "jwt_violations.jsonl")

# Boot/container identifier — set once per process boot
_ARIFOS_BOOT_ID = os.getenv("ARIFOS_BOOT_ID") or str(int(time.time()))

# Constitution hash — loaded once, used in every violation record
_CONSTITUTION_HASH = os.getenv("ARIFOS_CONSTITUTION_HASH", "unknown")

# Observe window — 24h minimum before enforce may be considered
OBSERVE_WINDOW_HOURS = 24


def _get_boot_id() -> str:
    """Return boot-scoped unique identifier for this container process."""
    return _ARIFOS_BOOT_ID


def _ensure_telemetry_dir() -> bool:
    """
    Ensure telemetry directory and log file are writable.

    Returns True if durable writes are possible.
    """ ""
    try:
        os.makedirs(TELEMETRY_PATH, exist_ok=True)
        # Test directory writability
        test_dir = os.path.join(TELEMETRY_PATH, ".write_test_dir")
        os.makedirs(test_dir, exist_ok=True)
        os.rmdir(test_dir)
        # Test the actual log file path for writability (not just the directory).
        # An immutable file or permission error on the specific file means durable writes will fail.
        test_file = VIOLATION_LOGFILE
        try:
            with open(test_file, "a", encoding="utf-8") as _fw:
                pass  # just test open-for-append
        except (PermissionError, OSError) as e:
            logger.error(f"VIOLATION_LOGFILE not writable: {e}")
            return False
        return True
    except Exception as e:
        logger.error(f"TELEMETRY_PATH not writable: {e}")
        return False


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
                "JWKS fetched from %s — keys: %s",
                SUPABASE_JWKS_URL,
                len(data.get("keys", [])),
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


def _get_ec_key(kid: str) -> Any | None:
    """Resolve Elliptic Curve public key from JWKS by kid."""
    jwks = _fetch_jwks()
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            try:
                return ECAlgorithm.from_jwk(json.dumps(key))
            except Exception as e:
                logger.error("Failed to parse EC JWK for kid=%s: %s", kid, e)
                return None
    logger.warning("No EC JWKS key found for kid=%s", kid)
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

    # ── Route by algorithm ──────────────────────────────────────────────
    if alg == "RS256":
        return _verify_supabase_jwt(token, unverified_header, unverified_claims, expected_actor_id)
    elif alg == "ES256":
        return _verify_supabase_jwt_es256(
            token, unverified_header, unverified_claims, expected_actor_id
        )
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


def _verify_supabase_jwt_es256(
    token: str,
    header: dict[str, Any],
    claims: dict[str, Any],
    expected_actor_id: str | None,
) -> JWTVerificationResult:
    """Verify a Supabase-issued ES256 (Elliptic Curve) token."""
    kid = header.get("kid", "")
    if not kid:
        return JWTVerificationResult(valid=False, error="missing_kid")

    public_key = _get_ec_key(kid)
    if not public_key:
        return JWTVerificationResult(valid=False, error="jwks_ec_key_not_found")

    try:
        verified = pyjwt.decode(
            token,
            key=public_key,
            algorithms=["ES256"],
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
        return JWTVerificationResult(valid=False, error=f"es256_verification_failed: {e}")

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
        auth_method="jwt_supabase_es256",
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


# ── Durable Violation Logging ───────────────────────────────────────────────

_jwt_violation_log: list[dict[str, Any]] = []
_MAX_VIOLATION_LOG = 1000


def log_violation_durable(
    error: str,
    path: str = "",  # nosec B107
    actor_id: str | None = None,
    session_id: str | None = None,
    jwt_sub: str | None = None,
    token_preview: str = "",  # nosec B107
) -> bool:
    """
    Append a JWT violation record to the durable JSONL telemetry file.

    This is the SOURCE OF TRUTH for enforce readiness.
    In-memory _jwt_violation_log is cache only.

    Returns True if durable write succeeded, False if it failed.
    """
    entry = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "error_code": error,
        "reason": f"{error} | path={path}",
        "actor_id": actor_id,
        "session_id": session_id,
        "request_path": path,
        "jwt_subject": jwt_sub,
        "enforce_mode": JWT_ENFORCE_MODE,
        "container_boot_id": _get_boot_id(),
        "constitution_hash": _CONSTITUTION_HASH,
        "token_preview": token_preview[:40] if token_preview else "",
    }

    try:
        os.makedirs(TELEMETRY_PATH, exist_ok=True)
        with open(VIOLATION_LOGFILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.error(f"Durable JWT violation log failed: {e}")
        return False


def log_violation(
    token_preview: str,
    error: str,
    path: str = "",
    actor_id: str | None = None,
    session_id: str | None = None,
) -> None:
    """
    Log a JWT verification violation for observe-mode analysis.

    Writes to BOTH:
    - in-memory cache (_jwt_violation_log) — for fast runtime status
    - durable JSONL file — SOURCE OF TRUTH, survives restarts

    The in-memory log is cache only. It must never be used as the
    source of truth for enforce readiness decisions.
    """
    global _jwt_violation_log

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token_preview": token_preview,
        "error": error,
        "path": path,
        "actor_id": actor_id,
        "session_id": session_id,
        "enforce_mode": JWT_ENFORCE_MODE,
        "boot_id": _get_boot_id(),
    }

    # 1. In-memory cache (runtime fast path, NOT source of truth)
    _jwt_violation_log.append(entry)
    if len(_jwt_violation_log) > _MAX_VIOLATION_LOG:
        _jwt_violation_log = _jwt_violation_log[-_MAX_VIOLATION_LOG:]

    # 2. Durable JSONL (source of truth — survives container restart)
    durable_ok = log_violation_durable(
        error=error,
        path=path,
        actor_id=actor_id,
        session_id=session_id,
        token_preview=token_preview,
    )

    if not durable_ok:
        logger.error(
            "JWT violation logged to in-memory cache but FAILED durable write. "
            "Enforce readiness may be unreliable until durable logging is restored."
        )

    logger.warning(
        "JWT_VIOLATION [mode=%s] error=%s path=%s actor_id=%s durable=%s",
        JWT_ENFORCE_MODE,
        error,
        path,
        actor_id,
        "ok" if durable_ok else "FAIL",
    )


def query_violations(
    window_start: datetime | None = None,
    window_end: datetime | None = None,
    error_codes: list[str] | None = None,
) -> dict[str, Any]:
    """
    Query the durable JWT violation log (JSONL).

    Returns:
        {
            "total": int,
            "by_error_code": {str: int},
            "by_actor_id": {str: int},
            "window_start": str | None,
            "window_end": str | None,
            "boot_ids_covered": [str],
            "durable": bool,
            "durable_path": str,
            "window_complete": bool,  # True if window_start..window_end >= 24h
            "ready_for_enforce": bool,
            "verdict": "CLEAR" | "HOLD",
            "reason": str,
            "violations": [entry, ...],
        }
    """
    violations = []
    durable = False

    if window_start is None:
        window_start = datetime.min.replace(tzinfo=timezone.utc)
    if window_end is None:
        window_end = datetime.now(timezone.utc)

    # Determine durability based on directory writability, not file existence.
    # An empty telemetry dir (no violations yet) is still durable if writable.
    telemetry_dir_ok = _ensure_telemetry_dir()

    try:
        if os.path.isfile(VIOLATION_LOGFILE):
            with open(VIOLATION_LOGFILE, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Parse timestamp
                    ts_str = rec.get("timestamp_utc", "")
                    try:
                        if ts_str:
                            ts = datetime.fromisoformat(ts_str)
                        else:
                            continue
                    except ValueError:
                        continue

                    # Window filter
                    if not (window_start <= ts <= window_end):
                        continue

                    # Error code filter
                    if error_codes and rec.get("error_code") not in error_codes:
                        continue

                    violations.append(rec)
            # File exists and was readable — durable if dir is also writable
            durable = telemetry_dir_ok
        else:
            # File doesn't exist yet (zero violations) — durable if dir is writable
            durable = telemetry_dir_ok
    except FileNotFoundError:
        durable = telemetry_dir_ok
    except Exception as e:
        logger.error(f"query_violations failed to read JSONL: {e}")
        durable = False

    # Aggregate
    by_error_code: dict[str, int] = {}
    by_actor_id: dict[str, int] = {}
    boot_ids: set[str] = set()

    for v in violations:
        err = v.get("error_code", "unknown")
        by_error_code[err] = by_error_code.get(err, 0) + 1
        actor = v.get("actor_id") or "anonymous"
        by_actor_id[actor] = by_actor_id.get(actor, 0) + 1
        bid = v.get("container_boot_id", "unknown")
        if bid:
            boot_ids.add(bid)

    # Window completeness check
    window_duration_hours = (window_end - window_start).total_seconds() / 3600
    window_complete = window_duration_hours >= OBSERVE_WINDOW_HOURS

    # Enforce readiness: requires durable logging AND complete 24h window AND zero violations
    if not durable:
        verdict = "HOLD"
        reason = "Durable telemetry unavailable — cannot trust violation counts"
        ready = False
    elif not window_complete:
        verdict = "HOLD"
        reason = (
            f"Observe window incomplete: {window_duration_hours:.1f}h < "
            f"{OBSERVE_WINDOW_HOURS}h minimum"
        )
        ready = False
    elif len(violations) > 0:
        verdict = "HOLD"
        reason = f"{len(violations)} violation(s) found in observe window — enforce not approved"
        ready = False
    else:
        verdict = "CLEAR"
        reason = (
            f"Zero violations in {window_duration_hours:.1f}h observe window — "
            f"enforce may proceed with human approval"
        )
        ready = True

    return {
        "total": len(violations),
        "by_error_code": by_error_code,
        "by_actor_id": by_actor_id,
        "window_start": window_start.isoformat(),
        "window_end": window_end.isoformat(),
        "boot_ids_covered": sorted(boot_ids),
        "durable": durable,
        "durable_path": VIOLATION_LOGFILE,
        "window_complete": window_complete,
        "window_hours": round(window_duration_hours, 2),
        "required_hours": OBSERVE_WINDOW_HOURS,
        "ready_for_enforce": ready,
        "verdict": verdict,
        "reason": reason,
        "violations": violations,
    }


def get_violation_stats() -> dict[str, Any]:
    """
    DEPRECATED — retained for backward compatibility with internal callers.

    This function reads from in-memory cache only. It must NOT be used
    as the source of truth for enforce readiness decisions.

    Use get_durable_violation_stats() instead.
    """
    total = len(_jwt_violation_log)
    by_error: dict[str, int] = {}
    for v in _jwt_violation_log:
        by_error[v["error"]] = by_error.get(v["error"], 0) + 1

    return {
        "total_violations": total,
        "by_error": by_error,
        "enforce_mode": JWT_ENFORCE_MODE,
        "ready_for_enforce": total == 0,
        "WARNING": (
            "This function reads in-memory cache only. Use "
            "get_durable_violation_stats() for enforce readiness."
        ),
    }


def get_durable_violation_stats(
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> dict[str, Any]:
    """
    Return enforce readiness assessment from durable telemetry.

    This is the authoritative function for JWT enforce readiness decisions.

    Returns dict with:
        - total, by_error_code, by_actor_id
        - durable: bool
        - window_complete: bool
        - ready_for_enforce: bool (False unless 24h window + zero violations + durable)
        - verdict: "CLEAR" | "HOLD"
        - reason: str
    """
    report = query_violations(
        window_start=window_start,
        window_end=window_end,
        error_codes=None,
    )

    # Summarize for caller
    return {
        "total_violations": report["total"],
        "by_error_code": report["by_error_code"],
        "by_actor_id": report["by_actor_id"],
        "enforce_mode": JWT_ENFORCE_MODE,
        "durable": report["durable"],
        "durable_path": report["durable_path"],
        "window_complete": report["window_complete"],
        "window_hours": report["window_hours"],
        "required_hours": OBSERVE_WINDOW_HOURS,
        "boot_ids_covered": report["boot_ids_covered"],
        "ready_for_enforce": report["ready_for_enforce"],
        "verdict": report["verdict"],
        "reason": report["reason"],
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
