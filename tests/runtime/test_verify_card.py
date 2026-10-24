"""Phase 1 — verify_card() tests (2026-10-24 · kimi-code/FI-008).

Contract under test (sovereign_verify.verify_card):
  1. valid signature passes
  2. body modified after signing fails
  3. corrupt kid (verificationMethod) fails
  4. empty public key fails closed
Plus: missing key file and absent signatures fail closed (never raise).
"""

from __future__ import annotations

import base64
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from arifosmcp.runtime.sovereign_verify import verify_card


def _canonical(card: dict) -> bytes:
    return json.dumps(card, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _make_signed_card(tmp_path):
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    der = pub.public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )
    fp = __import__("hashlib").sha256(der).hexdigest()
    pub_pem = pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    card = {
        "id": "test-card",
        "warga_binding": {"lane": "333-AGI", "authority_level": "observer"},
        "signatures": [],
    }
    canonical = _canonical(card)  # signer canonicalises BEFORE appending
    sig = priv.sign(canonical)
    card["signatures"].append(
        {
            "type": "Ed25519Signature2020",
            "proofValue": base64.b64encode(sig).decode(),
            "verificationMethod": f"ed25519:sha256:{fp}",
            "created": "2026-10-24T00:00:00Z",
        }
    )
    path = tmp_path / "agent-card.json"
    path.write_text(json.dumps(card))
    return str(path), pub_pem, card


def test_valid_signature_passes(tmp_path):
    path, pub_pem, _ = _make_signed_card(tmp_path)
    result = verify_card(path, public_key_pem=pub_pem)
    assert result["valid"] is True
    assert result["status"] == "VERIFIED"
    assert result["verified"] == 1


def test_body_modified_after_signing_fails(tmp_path):
    path, pub_pem, card = _make_signed_card(tmp_path)
    card["warga_binding"]["authority_level"] = "sovereign-delegate"  # tamper
    with open(path, "w") as f:
        json.dump(card, f)
    result = verify_card(path, public_key_pem=pub_pem)
    assert result["valid"] is False
    assert result["verified"] == 0
    assert "signature_invalid" in (result["results"][0]["reason"] or "")


def test_corrupt_kid_fails(tmp_path):
    path, pub_pem, card = _make_signed_card(tmp_path)
    card["signatures"][0]["verificationMethod"] = "ed25519:sha256:" + "0" * 64
    with open(path, "w") as f:
        json.dump(card, f)
    result = verify_card(path, public_key_pem=pub_pem)
    assert result["valid"] is False
    assert "kid_mismatch" in (result["results"][0]["reason"] or "")


def test_empty_pubkey_fails_closed(tmp_path):
    path, _, _ = _make_signed_card(tmp_path)
    result = verify_card(path, public_key_pem="")
    assert result["valid"] is False
    assert result["status"] == "FAILED"
    assert "empty_public_key" in result["reason"]


def test_missing_key_file_fails_closed(tmp_path):
    path, _, _ = _make_signed_card(tmp_path)
    result = verify_card(path, key_pem_path=str(tmp_path / "nope.pem"))
    assert result["valid"] is False
    assert "pubkey_unreadable" in result["reason"]


def test_no_signatures_fails_closed(tmp_path):
    priv = Ed25519PrivateKey.generate()
    pub_pem = priv.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    card = {"id": "unsigned", "signature_legacy": [{"header": {"kid": "arifos-a2a-card-2026-%q"}}]}
    path = tmp_path / "unsigned.json"
    path.write_text(json.dumps(card))
    result = verify_card(str(path), public_key_pem=pub_pem)
    assert result["valid"] is False
    assert "no_verifiable_signature" in result["reason"]


def test_unreadable_card_fails_closed(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{not json")
    result = verify_card(str(path), public_key_pem="not-empty")
    assert result["valid"] is False
    assert "card_unreadable" in result["reason"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
