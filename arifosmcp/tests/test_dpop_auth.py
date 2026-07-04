from __future__ import annotations

import time
import uuid
import sys
from pathlib import Path

import jwt as pyjwt
from cryptography.hazmat.primitives.asymmetric import ec
from jwt.algorithms import ECAlgorithm

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.dpop_auth import (
    DPoPReplayCache,
    extract_cnf_jkt,
    verify_dpop_proof,
)


def _make_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_jwk = ECAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    return private_key, public_jwk


def _make_access_token(jkt: str) -> str:
    now = int(time.time())
    return pyjwt.encode(
        {
            "sub": "arif",
            "iss": "arifos-internal",
            "aud": "arifOS",
            "iat": now,
            "exp": now + 300,
            "cnf": {"jkt": jkt},
        },
        "internal-secret-for-tests",
        algorithm="HS256",
    )


def _make_proof(private_key, public_jwk: dict[str, str], url: str, token: str, *, jti: str | None = None) -> str:
    now = int(time.time())
    claims = {
        "htu": url,
        "htm": "POST",
        "iat": now,
        "jti": jti or str(uuid.uuid4()),
        "ath": pyjwt.utils.base64url_encode(__import__("hashlib").sha256(token.encode("utf-8")).digest()).decode("ascii"),
    }
    return pyjwt.encode(
        claims,
        private_key,
        algorithm="ES256",
        headers={"typ": "dpop+jwt", "jwk": public_jwk},
    )


def test_verify_dpop_proof_happy_path():
    private_key, public_jwk = _make_keypair()
    access_token = _make_access_token("placeholder")
    proof = _make_proof(private_key, public_jwk, "https://mcp.arif-fazil.com/mcp", access_token)

    jkt = verify_dpop_proof(
        proof,
        method="POST",
        url="https://mcp.arif-fazil.com/mcp",
        access_token=access_token,
    ).jwk_thumbprint
    access_token = _make_access_token(jkt or "")
    proof = _make_proof(private_key, public_jwk, "https://mcp.arif-fazil.com/mcp", access_token)

    result = verify_dpop_proof(
        proof,
        method="POST",
        url="https://mcp.arif-fazil.com/mcp",
        access_token=access_token,
        access_token_cnf_jkt=extract_cnf_jkt(access_token),
    )

    assert result.valid is True
    assert result.jwk_thumbprint == extract_cnf_jkt(access_token)


def test_verify_dpop_proof_replay_rejected():
    cache = DPoPReplayCache(ttl_seconds=300)
    assert cache.consume("same-jti") is True
    assert cache.consume("same-jti") is False


def test_verify_dpop_proof_ath_mismatch():
    private_key, public_jwk = _make_keypair()
    access_token = _make_access_token("placeholder")
    proof = _make_proof(private_key, public_jwk, "https://mcp.arif-fazil.com/mcp", access_token)

    result = verify_dpop_proof(
        proof,
        method="POST",
        url="https://mcp.arif-fazil.com/mcp",
        access_token="wrong-token",
    )

    assert result.valid is False
    assert result.error == "dpop_ath_mismatch"
