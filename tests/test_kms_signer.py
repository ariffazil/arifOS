import base64
import hashlib
from typing import Any, Dict

import pytest

from arifos_core.utils.kms_signer import KmsSigner, KmsSignerConfig, KmsClientProtocol


class FakeKmsClient(KmsClientProtocol):
    """
    Minimal fake KMS client used for unit tests.

    Behavior:
      - sign(...) returns Signature = sha256(b"FAKE" + Message)
      - verify(...) compares provided signature against expected sha256(b"FAKE" + Message)
    """

    def __init__(self) -> None:
        self.calls: Dict[str, Any] = {}

    def sign(self, **kwargs):
        self.calls["sign"] = kwargs
        message: bytes = kwargs["Message"]
        fake_sig = hashlib.sha256(b"FAKE" + message).digest()
        return {"Signature": fake_sig}

    def verify(self, **kwargs):
        self.calls["verify"] = kwargs
        message: bytes = kwargs["Message"]
        signature: bytes = kwargs["Signature"]
        expected = hashlib.sha256(b"FAKE" + message).digest()
        return {"SignatureValid": signature == expected}


def test_kms_signer_sign_and_verify_roundtrip() -> None:
    """
    Ensure KmsSigner signs (base64) and verify_hash returns True using the fake client.
    """
    config = KmsSignerConfig(key_id="arn:aws:kms:us-east-1:111:alias/test-key")
    fake_client = FakeKmsClient()
    signer = KmsSigner(config=config, client=fake_client)

    # 32 byte digest as example
    digest = bytes.fromhex("00" * 32)

    sig_b64 = signer.sign_hash(digest)
    assert isinstance(sig_b64, str)

    # Ensure the fake client received the expected parameters
    assert "sign" in fake_client.calls
    sign_kwargs = fake_client.calls["sign"]
    assert sign_kwargs["KeyId"] == config.key_id
    assert sign_kwargs["MessageType"] == "DIGEST"
    assert sign_kwargs["SigningAlgorithm"] == config.signing_algorithm
    assert sign_kwargs["Message"] == digest

    # verify via wrapper (which delegates to fake_client.verify)
    ok = signer.verify_hash(digest, sig_b64)
    assert ok

    # verify that verify was called with expected params
    assert "verify" in fake_client.calls
    verify_kwargs = fake_client.calls["verify"]
    assert verify_kwargs["KeyId"] == config.key_id
    assert verify_kwargs["MessageType"] == "DIGEST"
    assert verify_kwargs["SigningAlgorithm"] == config.signing_algorithm
