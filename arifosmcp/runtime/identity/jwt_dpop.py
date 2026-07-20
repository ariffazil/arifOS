"""
JWT / DPoP — RFC 7519 (JWT) + RFC 9449 (DPoP) with Ed25519.

REAL IMPLEMENTATION — Ed25519 signing + verification.
Key material loaded from /opt/arifos/secrets/did_arifos_{private,public}.key

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
Real crypto landed by FORGE (000Ω), 2026-07-08.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
import uuid
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

# ─── Key loading ─────────────────────────────────────────────────────────────

_SECRETS_DIR = Path("/opt/arifos/secrets")
_PRIVATE_KEY_PATH = _SECRETS_DIR / "did_arifos_private.key"
_PUBLIC_KEY_PATH = _SECRETS_DIR / "did_arifos_public.key"


def _load_private_key() -> Ed25519PrivateKey:
    """Load sovereign Ed25519 private key. F11: key never logged or returned."""
    pem = _PRIVATE_KEY_PATH.read_bytes()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"Expected Ed25519PrivateKey, got {type(key).__name__}")
    return key


def _load_public_key() -> Ed25519PublicKey:
    """Load sovereign Ed25519 public key."""
    pem = _PUBLIC_KEY_PATH.read_bytes()
    key = serialization.load_pem_public_key(pem)
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError(f"Expected Ed25519PublicKey, got {type(key).__name__}")
    return key


# ─── Base64url helpers (RFC 4648 §5) ─────────────────────────────────────────


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    # Add padding back
    pad = 4 - len(s) % 4
    if pad != 4:
        s += "=" * pad
    return base64.urlsafe_b64decode(s)


# ─── JWT (RFC 7519) ──────────────────────────────────────────────────────────


def encode_jwt(
    claims: dict,
    signing_key: bytes | None = None,
    *,
    alg: str = "EdDSA",
    kid: str = "did:arif:arifos",
) -> str:
    """Encode a JWT with Ed25519 signing.

    Args:
        claims: payload dict (should include iss, sub, aud, exp, iat)
        signing_key: unused — loads from /opt/arifos/secrets/ (F11)
        alg: algorithm (default EdDSA per RFC 8037)
        kid: key id for JWKS lookup

    Returns:
        A `header.payload.signature` string, base64url-encoded per RFC 7515.
    """
    header = {"alg": alg, "typ": "JWT", "kid": kid}
    header_b64 = _b64url_encode(json.dumps(header, sort_keys=True).encode())
    payload_b64 = _b64url_encode(json.dumps(claims, sort_keys=True).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()
    private_key = _load_private_key()
    signature = private_key.sign(signing_input)
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def decode_jwt(
    token: str,
    verification_key: bytes | None = None,
    *,
    required_claims: tuple[str, ...] = ("iss", "sub", "aud", "exp", "iat"),
    leeway_seconds: int = 30,
) -> dict:
    """Decode and verify a JWT with Ed25519.

    Args:
        token: the JWT string ("header.payload.signature")
        verification_key: unused — loads from /opt/arifos/secrets/ (F11)
        required_claims: claims that MUST be present
        leeway_seconds: clock skew tolerance for exp/nbf/iat

    Returns:
        The claims dict if signature verifies and time checks pass.

    Raises:
        ValueError on malformed token
        InvalidSignature on signature mismatch
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"Malformed JWT: expected 3 parts, got {len(parts)}")

    header_b64, payload_b64, sig_b64 = parts

    # Decode header
    try:
        header = json.loads(_b64url_decode(header_b64))
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Malformed JWT header: {e}")

    if header.get("alg") != "EdDSA":
        raise ValueError(f"Unsupported algorithm: {header.get('alg')}")

    # Verify signature
    signing_input = f"{header_b64}.{payload_b64}".encode()
    try:
        signature = _b64url_decode(sig_b64)
        public_key = _load_public_key()
        public_key.verify(signature, signing_input)
    except InvalidSignature:
        raise InvalidSignature("JWT signature verification failed")
    except Exception as e:
        raise ValueError(f"JWT verification error: {e}")

    # Decode payload
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (json.JSONDecodeError, Exception) as e:
        raise ValueError(f"Malformed JWT payload: {e}")

    # Check required claims
    missing = [c for c in required_claims if c not in payload]
    if missing:
        raise ValueError(f"Missing required claims: {missing}")

    # Time checks
    now = int(time.time())
    if "iat" in payload and payload["iat"] > now + leeway_seconds:
        raise ValueError("Token issued in the future (iat)")
    if "exp" in payload and payload["exp"] < now - leeway_seconds:
        raise ValueError("Token expired")
    if "nbf" in payload and payload["nbf"] > now + leeway_seconds:
        raise ValueError("Token not yet valid (nbf)")

    return payload


# ─── DPoP (RFC 9449) ─────────────────────────────────────────────────────────


def make_dpop_proof(
    http_method: str,
    http_url: str,
    access_token: str,
    signing_key: bytes | None = None,
    *,
    htu: str | None = None,
    nonce: str | None = None,
) -> str:
    """Mint a DPoP proof JWT with Ed25519.

    Args:
        http_method: GET/POST/etc (used as `htm` claim)
        http_url: target URL (used as `htu` claim — exact match)
        access_token: the access_token being bound; included as `ath` (hash)
        signing_key: unused — loads from /opt/arifos/secrets/
        htu: override http_url extraction (e.g. when behind proxy)
        nonce: server-provided nonce from DPoP-Nonce header

    Returns:
        A JWT string ready to be sent as `DPoP` header.
    """
    # Compute ath = base64url(SHA-256(access_token))
    ath = _b64url_encode(hashlib.sha256(access_token.encode()).digest())

    claims = {
        "htm": http_method.upper(),
        "htu": htu or http_url,
        "ath": ath,
        "iat": int(time.time()),
        "jti": str(uuid.uuid4()),
    }
    if nonce:
        claims["nonce"] = nonce

    # DPoP uses the same JWT format but with typ: dpop+jwt
    header = {"alg": "EdDSA", "typ": "dpop+jwt", "jwk": _public_jwk()}
    header_b64 = _b64url_encode(json.dumps(header, sort_keys=True).encode())
    payload_b64 = _b64url_encode(json.dumps(claims, sort_keys=True).encode())

    signing_input = f"{header_b64}.{payload_b64}".encode()
    private_key = _load_private_key()
    signature = private_key.sign(signing_input)
    sig_b64 = _b64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_dpop_proof(
    dpop_jwt: str,
    expected_method: str,
    expected_url: str,
    verification_key: bytes | None = None,
    *,
    expected_ath: str | None = None,
    nonce_cache: set[str] | None = None,
    leeway_seconds: int = 30,
) -> dict:
    """Verify a DPoP proof with Ed25519.

    Args:
        dpop_jwt: the JWT string from DPoP header
        expected_method: must equal claim `htm`
        expected_url: must equal claim `htu`
        verification_key: unused — loads from /opt/arifos/secrets/
        expected_ath: must equal claim `ath` (if provided)
        nonce_cache: jti values already seen in this window (replay defense)
        leeway_seconds: clock skew tolerance for `iat`

    Returns:
        Decoded claims dict.

    Raises:
        ValueError on verification failure.
    """
    # Decode + verify signature via JWT path
    claims = decode_jwt(dpop_jwt, required_claims=("htm", "htu", "iat", "jti"))

    # DPoP-specific checks
    if claims["htm"] != expected_method.upper():
        raise ValueError(f"DPoP htm mismatch: {claims['htm']} != {expected_method}")
    if claims["htu"] != expected_url:
        raise ValueError(f"DPoP htu mismatch: {claims['htu']} != {expected_url}")

    now = int(time.time())
    if abs(claims["iat"] - now) > leeway_seconds:
        raise ValueError("DPoP iat outside leeway window")

    if expected_ath and claims.get("ath") != expected_ath:
        raise ValueError("DPoP ath mismatch")

    # Replay defense
    if nonce_cache is not None:
        jti = claims["jti"]
        if jti in nonce_cache:
            raise ValueError(f"DPoP replay detected: jti={jti}")
        nonce_cache.add(jti)

    return claims


def _public_jwk() -> dict:
    """Export public key as JWK for DPoP header embedding."""
    pub = _load_public_key()
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": _b64url_encode(pub_bytes),
    }
