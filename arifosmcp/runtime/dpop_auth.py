"""
DPoP verification for bearer-bound HTTP ingress.

Implements the minimum RFC 9449 proof-of-possession checks needed to stop
replayable bearer tokens from becoming execution authority:
- signed DPoP proof with public JWK in header
- htm / htu binding to the concrete request
- ath binding to the presented bearer token
- optional cnf.jkt binding for JWT access tokens
- in-memory jti replay cache
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any

import jwt as pyjwt
from jwt.algorithms import ECAlgorithm, OKPAlgorithm, RSAAlgorithm

ALLOWED_ALGORITHMS = {"RS256", "ES256", "EdDSA"}
DPoP_CLOCK_SKEW_MAX = int(os.getenv("ARIFOS_DPOP_CLOCK_SKEW_MAX", "300"))
DPoP_REPLAY_TTL_SECONDS = int(os.getenv("ARIFOS_DPOP_REPLAY_TTL_SECONDS", "300"))


def _b64url_sha256(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return pyjwt.utils.base64url_encode(digest).decode("ascii")


def _json_dumps_canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _jwk_thumbprint(jwk: dict[str, Any]) -> str:
    kty = str(jwk.get("kty") or "")
    if kty == "RSA":
        payload = {"e": jwk["e"], "kty": "RSA", "n": jwk["n"]}
    elif kty == "EC":
        payload = {"crv": jwk["crv"], "kty": "EC", "x": jwk["x"], "y": jwk["y"]}
    elif kty == "OKP":
        payload = {"crv": jwk["crv"], "kty": "OKP", "x": jwk["x"]}
    else:
        raise ValueError(f"unsupported_jwk_kty: {kty}")
    return _b64url_sha256(_json_dumps_canonical(payload))


def extract_cnf_jkt(access_token: str) -> str | None:
    """Read cnf.jkt from a JWT access token without verifying signature."""
    try:
        claims = pyjwt.decode(access_token, options={"verify_signature": False})
    except pyjwt.PyJWTError:
        return None
    cnf = claims.get("cnf")
    if isinstance(cnf, dict):
        jkt = cnf.get("jkt")
        return str(jkt) if jkt else None
    return None


def _public_key_from_jwk(jwk: dict[str, Any], alg: str) -> Any:
    jwk_text = json.dumps(jwk)
    if alg == "RS256":
        return RSAAlgorithm.from_jwk(jwk_text)
    if alg == "ES256":
        return ECAlgorithm.from_jwk(jwk_text)
    if alg == "EdDSA":
        return OKPAlgorithm.from_jwk(jwk_text)
    raise ValueError(f"unsupported_algorithm: {alg}")


@dataclass
class DPoPReplayCache:
    ttl_seconds: int = DPoP_REPLAY_TTL_SECONDS
    _entries: dict[str, float] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def consume(self, jti: str, now: float | None = None) -> bool:
        current = float(now if now is not None else time.time())
        with self._lock:
            expired = [key for key, expiry in self._entries.items() if expiry <= current]
            for key in expired:
                self._entries.pop(key, None)
            expiry = self._entries.get(jti)
            if expiry and expiry > current:
                return False
            self._entries[jti] = current + self.ttl_seconds
            return True


@dataclass
class DPoPVerificationResult:
    valid: bool
    error: str = ""
    claims: dict[str, Any] = field(default_factory=dict)
    jwk_thumbprint: str | None = None


_replay_cache = DPoPReplayCache()


def verify_dpop_proof(
    proof_jwt: str,
    *,
    method: str,
    url: str,
    access_token: str,
    access_token_cnf_jkt: str | None = None,
) -> DPoPVerificationResult:
    if not proof_jwt.strip():
        return DPoPVerificationResult(valid=False, error="missing_dpop_proof")
    if not access_token.strip():
        return DPoPVerificationResult(valid=False, error="missing_bearer_token")

    try:
        header = pyjwt.get_unverified_header(proof_jwt)
    except pyjwt.PyJWTError as exc:
        return DPoPVerificationResult(valid=False, error=f"malformed_dpop_header: {exc}")

    typ = str(header.get("typ") or "").lower()
    if typ != "dpop+jwt":
        return DPoPVerificationResult(valid=False, error="invalid_dpop_typ")

    alg = str(header.get("alg") or "")
    if alg not in ALLOWED_ALGORITHMS:
        return DPoPVerificationResult(valid=False, error=f"unsupported_dpop_alg: {alg or 'missing'}")

    jwk = header.get("jwk")
    if not isinstance(jwk, dict):
        return DPoPVerificationResult(valid=False, error="missing_dpop_jwk")

    try:
        public_key = _public_key_from_jwk(jwk, alg)
        thumbprint = _jwk_thumbprint(jwk)
    except Exception as exc:
        return DPoPVerificationResult(valid=False, error=f"invalid_dpop_jwk: {exc}")

    try:
        claims = pyjwt.decode(
            proof_jwt,
            key=public_key,
            algorithms=[alg],
            options={"require": ["htu", "htm", "iat", "jti"]},
            leeway=DPoP_CLOCK_SKEW_MAX,
        )
    except pyjwt.PyJWTError as exc:
        return DPoPVerificationResult(valid=False, error=f"dpop_signature_verification_failed: {exc}")

    htm = str(claims.get("htm") or "").upper()
    if htm != method.upper():
        return DPoPVerificationResult(valid=False, error="dpop_htm_mismatch")

    htu = str(claims.get("htu") or "")
    if htu != url:
        return DPoPVerificationResult(valid=False, error="dpop_htu_mismatch")

    iat = claims.get("iat")
    if not isinstance(iat, int):
        return DPoPVerificationResult(valid=False, error="invalid_dpop_iat")
    if abs(int(time.time()) - iat) > DPoP_CLOCK_SKEW_MAX:
        return DPoPVerificationResult(valid=False, error="dpop_iat_out_of_window")

    jti = str(claims.get("jti") or "")
    if not jti:
        return DPoPVerificationResult(valid=False, error="missing_dpop_jti")
    if not _replay_cache.consume(jti):
        return DPoPVerificationResult(valid=False, error="dpop_replay_detected")

    ath = str(claims.get("ath") or "")
    if not ath:
        return DPoPVerificationResult(valid=False, error="missing_dpop_ath")
    if ath != _b64url_sha256(access_token):
        return DPoPVerificationResult(valid=False, error="dpop_ath_mismatch")

    if access_token_cnf_jkt and thumbprint != access_token_cnf_jkt:
        return DPoPVerificationResult(valid=False, error="dpop_cnf_jkt_mismatch")

    return DPoPVerificationResult(
        valid=True,
        claims=claims,
        jwk_thumbprint=thumbprint,
    )
