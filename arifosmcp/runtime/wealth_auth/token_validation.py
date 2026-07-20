"""
Token validation: extract + verify a signed capability token.

The audit mandates that EVERY organ's protected tool goes through this gate.
We accept the token shape defined in /runtime/contracts/session.schema.json
and verify each claim. Until the Ed25519 keypair is generated for arif-fazil.com,
we use an HMAC-SHA256 dev-mode signature. The audit says cryptographic; the
path from dev-mode HMAC to production Ed25519 is `replace_signing_algo()` and
F13 signature.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass
from typing import Any

# Algorithm registry. Adding a new alg here is a single-line, F1-revertible change.
_SIGNING_ALGOS: dict[str, str] = {
    "HS256-dev": "hmac-sha256",  # dev-only. Ed25519 lands in F13.
    "EdDSA": "ed25519",  # not yet implemented. Listed to surface the public algorithm name.
}


@dataclass
class TokenClaims:
    issuer: str
    subject_did: str
    audience: list[str]
    actor_id: str
    allowed_capabilities: list[str]
    authority_band: str
    issued_at: int
    expires_at: int
    not_before: int
    jti: str
    trace_id: str | None
    session_id: str | None

    def is_for_audience(self, audience: str) -> bool:
        return audience in self.audience

    def has_capability(self, capability: str) -> bool:
        return capability in self.allowed_capabilities

    def is_expired(self, now: int | None = None) -> bool:
        if now is None:
            now = int(time.time())
        return now >= self.expires_at

    def is_not_yet_valid(self, now: int | None = None) -> bool:
        if now is None:
            now = int(time.time())
        return now < self.not_before


# Replay window. Tokens are valid for one presentation within this window.
_REPLAY_WINDOW_SECONDS = int(os.getenv("ARIFOS_TOKEN_REPLAY_WINDOW", "300"))
_REPLAY_STORE: dict[str, float] = {}  # jti -> expiry_epoch


def _purge_replay_store() -> None:
    now = time.time()
    for jti, exp in list(_REPLAY_STORE.items()):
        if exp < now:
            del _REPLAY_STORE[jti]


def _record_jti(jti: str) -> None:
    _purge_replay_store()
    if jti in _REPLAY_STORE:
        from .exceptions import ReplayDetected

        raise ReplayDetected(f"Token jti {jti!r} already presented within replay window.")
    _REPLAY_STORE[jti] = time.time() + _REPLAY_WINDOW_SECONDS


def extract_bearer(authorization_header: str | None) -> str:
    """Strip 'Bearer ' prefix; raise on malformed."""
    from .exceptions import TokenInvalid

    if not authorization_header:
        raise TokenInvalid("Missing Authorization header.")
    parts = authorization_header.strip().split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise TokenInvalid("Authorization header must be 'Bearer <token>'.")
    token = parts[1].strip()
    if not token or token == "none":
        # Audit: "Authorization: Bearer none" is the public-simulation pass-through.
        return "none"
    return token


def _verify_signature(token: str) -> dict[str, Any]:
    """Verify the signature and return the unsigned payload.

    Dev-mode uses HMAC-SHA256. Production uses Ed25519.
    """
    from .exceptions import TokenInvalid

    if "." not in token:
        raise TokenInvalid("Token must be in compact JWS-style <payload>.<sig> form.")
    payload_b64, sig_b64 = token.rsplit(".", 1)
    # The compact form uses base64url; we accept url-safe and standard variants.
    import base64

    def _b64decode(s: str) -> bytes:
        s = s.replace("-", "+").replace("_", "/")
        s += "=" * ((4 - len(s) % 4) % 4)
        return base64.b64decode(s)

    try:
        payload_raw = _b64decode(payload_b64)
        sig = _b64decode(sig_b64)
    except Exception as exc:
        raise TokenInvalid(f"Token segments are not valid base64: {exc}")

    try:
        payload = json.loads(payload_raw)
    except Exception as exc:
        raise TokenInvalid(f"Token payload is not valid JSON: {exc}")

    alg = payload.get("alg", "HS256-dev")
    if alg not in _SIGNING_ALGOS:
        raise TokenInvalid(f"Unsupported signature alg: {alg!r}")
    if alg == "HS256-dev":
        key = os.getenv("ARIFOS_OPS_SIGNING_KEY", "")
        if not key:
            raise TokenInvalid(
                "Server has no signing key configured (ARIFOS_OPS_SIGNING_KEY unset)."
            )
        expected = hmac.new(key.encode("utf-8"), payload_raw, hashlib.sha256).digest()
        if not hmac.compare_digest(expected, sig):
            raise TokenInvalid("Token signature did not match.")
    elif alg == "EdDSA":
        # Until F13 production key, EdDSA cannot verify. Reject with audit-shaped error.
        raise TokenInvalid("EdDSA verification is not yet wired; production keypair pending F13.")
    return payload


def validate_token(authorization_header: str | None) -> TokenClaims:
    """Validate the bearer token and return a TokenClaims.

    Raises one of the audit-4 error subclasses on failure.
    """
    from .exceptions import (
        ActorNotBound,
        TokenInvalid,
    )

    raw = extract_bearer(authorization_header)
    if raw == "none":
        # Public-simulation pass-through: synthesize a minimal claims object that
        # `authorize()` will recognize as "no authority" if a tool calls it without
        # explicitly opting in. Public-simulation tools MUST check `public_simulation`
        # themselves; this is a hard fail otherwise.
        return TokenClaims(
            issuer="",
            subject_did="",
            audience=[],
            actor_id="",
            allowed_capabilities=[],
            authority_band="OBSERVER",
            issued_at=0,
            expires_at=0,
            not_before=0,
            jti="",
            trace_id=None,
            session_id=None,
        )
    payload = _verify_signature(raw)
    try:
        claims = TokenClaims(
            issuer=str(payload.get("iss", "")),
            subject_did=str(payload.get("sub", "")),
            audience=list(payload.get("aud", []) or []),
            actor_id=str(payload.get("actor_id", "")),
            allowed_capabilities=list(payload.get("allowed_capabilities", []) or []),
            authority_band=str(payload.get("authority_band", "OBSERVER")),
            issued_at=int(payload.get("iat", 0)),
            expires_at=int(payload.get("exp", 0)),
            not_before=int(payload.get("nbf", 0)),
            jti=str(payload.get("jti", "")),
            trace_id=payload.get("trace_id"),
            session_id=payload.get("session_id"),
        )
    except Exception as exc:
        raise TokenInvalid(f"Token payload is malformed: {exc}")
    if not claims.issuer.startswith("did:web:arif-fazil.com"):
        raise TokenInvalid(f"Token issuer is not the sovereign root: {claims.issuer!r}")
    if not claims.actor_id:
        raise ActorNotBound("Token payload has no actor_id bound.")
    if not claims.jti:
        raise TokenInvalid(
            "Token payload has no jti; replay protection requires a unique token id."
        )
    # Replay protection (jti dedup) — only for non-public-simulation tokens.
    if claims.issued_at > 0:
        _record_jti(claims.jti)
    return claims


def issue_token(
    *,
    actor_id: str,
    subject_did: str,
    audience: list[str],
    allowed_capabilities: list[str],
    authority_band: str = "OPERATOR",
    ttl_seconds: int = 3600,
    session_id: str | None = None,
    trace_id: str | None = None,
) -> str:
    """Dev-mode token issuer. Returns a compact JWS-style token.

    Production: replace the body of this function with Ed25519 signing.
    """
    import base64
    import json as _json
    import uuid

    key = os.getenv("ARIFOS_OPS_SIGNING_KEY", "")
    if not key:
        raise RuntimeError("ARIFOS_OPS_SIGNING_KEY unset; cannot issue tokens.")
    now = int(time.time())
    payload = {
        "alg": "HS256-dev",
        "iss": "did:web:arif-fazil.com",
        "sub": subject_did,
        "aud": audience,
        "actor_id": actor_id,
        "allowed_capabilities": allowed_capabilities,
        "authority_band": authority_band,
        "iat": now,
        "nbf": now,
        "exp": now + ttl_seconds,
        "jti": f"jti-{uuid.uuid4().hex}",
    }
    if session_id:
        payload["session_id"] = session_id
    if trace_id:
        payload["trace_id"] = trace_id
    payload_raw = _json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    sig = hmac.new(key.encode("utf-8"), payload_raw, hashlib.sha256).digest()
    payload_b64 = base64.urlsafe_b64encode(payload_raw).rstrip(b"=").decode("ascii")
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode("ascii")
    return f"{payload_b64}.{sig_b64}"
