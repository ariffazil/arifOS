from __future__ import annotations

import base64
import hashlib
import json

from arifosmcp.runtime import observatory_signing


def test_sign_snapshot_payload_is_verifiable(monkeypatch, tmp_path):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    private = Ed25519PrivateKey.generate()
    private_path = tmp_path / "key.pem"
    public_path = tmp_path / "key.pub.pem"
    private_path.write_bytes(
        private.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    monkeypatch.setattr(observatory_signing, "PRIVATE_KEY_PATH", private_path)
    monkeypatch.setattr(observatory_signing, "PUBLIC_KEY_PATH", public_path)

    payload = {"snapshot_id": "obs_test", "observed_at": "2026-07-17T00:00:00Z"}
    result = observatory_signing.sign_snapshot_payload(payload)
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode()
    private.public_key().verify(base64.b64decode(result["value"]), canonical)

    assert result["state"] == "signed"
    assert result["algorithm"] == "ed25519"
    assert result["signed_at"] == payload["observed_at"]
    assert result["payload_hash"] == hashlib.sha256(canonical).hexdigest()


def test_missing_key_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(observatory_signing, "PRIVATE_KEY_PATH", tmp_path / "missing.pem")
    monkeypatch.setattr(observatory_signing, "PUBLIC_KEY_PATH", tmp_path / "missing.pub.pem")

    try:
        observatory_signing.sign_snapshot_payload({"snapshot_id": "obs_test"})
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing signing identity must fail closed")
