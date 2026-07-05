"""
JWT / DPoP STUBS — RFC 7519 (JWT) + RFC 9449 (DPoP) interfaces only.

ALGORITHM PLACEHOLDER: ALG_PLACEHOLDER_ED25519_REPLACE_BEFORE_PROD

When real crypto lands:

  1. import cryptography.hazmat.primitives.asymmetric.ed25519
  2. Replace _STUB_ALG with `EdDSA`
  3. Wire encode_jwt to: header.alg=EdDSA, signing with Ed25519 private
  4. Wire decode_jwt to: verify with Ed25519 public, check exp/iss/aud/nbf
  5. Wire make_dpop_proof: include htm/htu/iat/nonce, sign with Ed25519
  6. Wire verify_dpop_proof: same checks as JWT + nonce cache for replay defense

INTERFACE SIGNATURES are real RFC-compliant shapes (header.payload.signature,
base64url). Bodies raise NotImplementedError.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
"""

from __future__ import annotations


# Hardcoded placeholder constant — DO NOT use in production.
# Every signature that requires _STUB_ALG should be replaced when real crypto lands.
_STUB_ALG: str = "ALG_PLACEHOLDER_ED25519_REPLACE_BEFORE_PROD"


# ─── JWT stubs (RFC 7519) ────────────────────────────────────────────────────


def encode_jwt(
    claims: dict,
    signing_key: bytes,
    *,
    alg: str | None = None,
    kid: str | None = None,
) -> str:
    """Encode a JWT. STUB — raises NotImplementedError.

    Args:
        claims: payload dict (must include iss, sub, aud, exp, iat at minimum)
        signing_key: raw private key bytes for signing
        alg: override `_STUB_ALG` (use only for tests)
        kid: key id for JWKS lookup at verification time

    Returns:
        A `header.payload.signature` string, base64url-encoded per RFC 7515.

    Implementation:
        Header: {"alg": alg or _STUB_ALG, "typ": "JWT", "kid": kid}
        Payload: claims dict (json.dumps sort_keys)
        Signature: ed25519_sign(header_b64 + "." + payload_b64, signing_key)
    """
    raise NotImplementedError(
        "JWT encode stub — replace with Ed25519 sign. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


def decode_jwt(
    token: str,
    verification_key: bytes,
    *,
    required_claims: tuple[str, ...] = ("iss", "sub", "aud", "exp", "iat"),
    leeway_seconds: int = 30,
) -> dict:
    """Decode and verify a JWT. STUB — raises NotImplementedError.

    Args:
        token: the JWT string ("header.payload.signature")
        verification_key: raw public key bytes
        required_claims: claims that MUST be present
        leeway_seconds: clock skew tolerance for exp/nbf/iat

    Returns:
        The claims dict if signature verifies and time checks pass.

    Raises:
        jwt.InvalidTokenError on malformed token
        jwt.ExpiredSignatureError on exp violation
        jwt.InvalidSignatureError on signature mismatch

    Implementation:
        1. Split token on "."; verify 3 parts
        2. base64url-decode header and payload
        3. Verify header.alg == alg or _STUB_ALG (if mismatch, fail)
        4. Verify ed25519_verify(signature, header_b64+"."+payload_b64, verification_key)
        5. Verify all required_claims present
        6. Verify iat <= now+leeway AND exp >= now-leeway (or check nbf)
    """
    raise NotImplementedError(
        "JWT decode stub — replace with Ed25519 verify + time checks. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


# ─── DPoP stubs (RFC 9449) ───────────────────────────────────────────────────


def make_dpop_proof(
    http_method: str,
    http_url: str,
    access_token: str,
    signing_key: bytes,
    *,
    htu: str | None = None,
    nonce: str | None = None,
) -> str:
    """Mint a DPoP proof JWT. STUB — raises NotImplementedError.

    Args:
        http_method: GET/POST/etc (used as `htm` claim)
        http_url: target URL (used as `htu` claim — exact match)
        access_token: the access_token being bound; included as `ath` (hash)
        signing_key: ephemeral Ed25519 key per session
        htu: override http_url extraction (e.g. when behind proxy)
        nonce: server-provided nonce from DPoP-Nonce header

    Returns:
        A JWT string ready to be sent as `DPoP` header.

    Implementation:
        Claims: {"htm": http_method, "htu": htu or http_url, "iat": now,
                 "jti": uuid4(), "ath": sha256(access_token)[:32]}
        Sign with ed25519 over the JWT
        Return header.payload.signature
    """
    raise NotImplementedError(
        "DPoP mint stub — replace with Ed25519 sign over DPoP claims. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


def verify_dpop_proof(
    dpop_jwt: str,
    expected_method: str,
    expected_url: str,
    verification_key: bytes,
    *,
    expected_ath: str | None = None,
    nonce_cache: set[str] | None = None,
    leeway_seconds: int = 30,
) -> dict:
    """Verify a DPoP proof. STUB — raises NotImplementedError.

    Args:
        dpop_jwt: the JWT string from DPoP header
        expected_method: must equal claim `htm`
        expected_url: must equal claim `htu`
        verification_key: public key
        expected_ath: must equal claim `ath` (if provided)
        nonce_cache: jti values already seen in this window (replay defense)
        leeway_seconds: clock skew tolerance for `iat`

    Returns:
        Decoded claims dict.

    Raises:
        Various DPoPError subclasses per RFC 9449 §5.

    Implementation:
        1. Parse JWT (uses decode_jwt)
        2. Verify htm == expected_method
        3. Verify htu == expected_url
        4. Verify iat in window [now-leeway, now+leeway]
        5. Verify ath == expected_ath (if provided)
        6. If jti in nonce_cache, raise replay error; else add
        7. Return claims
    """
    raise NotImplementedError(
        "DPoP verify stub — replace with decode_jwt + DPoP-specific checks. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


# ─── Constants (real; exported) ──────────────────────────────────────────────


def stub_algorithm() -> str:
    """Return the current stub algorithm marker. Replace before production.

    Sentinel value to grep for when implementing real crypto:
        rg "_STUB_ALG" or grep "_STUB_ALG" --include='*.py'
    """
    return _STUB_ALG
