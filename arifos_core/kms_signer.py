from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Protocol, Optional, Any

# boto3 is only required when actually using AWS KMS (not for unit tests)
try:
    import boto3  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - boto3 not required for tests using fake client
    boto3 = None


class KmsClientProtocol(Protocol):
    """
    Minimal protocol for AWS KMS client used by arifOS.
    This makes it easy to inject a fake/mock client in tests.
    """

    def sign(self, **kwargs) -> Any:  # pragma: no cover - exercised via wrapper
        ...

    def verify(self, **kwargs) -> Any:  # pragma: no cover - exercised via wrapper
        ...


@dataclass
class KmsSignerConfig:
    key_id: str
    signing_algorithm: str = "RSASSA_PSS_SHA_256"
    # Optionally add region_name, endpoint_url, etc.


class KmsSigner:
    """
    Thin wrapper around AWS KMS signing operations.

    Use a fake/mock client in tests by passing `client=...`.
    By default uses boto3.client('kms') when boto3 is available.
    """

    def __init__(
        self,
        config: KmsSignerConfig,
        client: Optional[KmsClientProtocol] = None,
    ) -> None:
        self.config = config
        if client is not None:
            self._client = client
        else:
            if boto3 is None:
                raise RuntimeError(
                    "boto3 not available. Pass a mock client for testing or install boto3."
                )
            self._client: KmsClientProtocol = boto3.client("kms")

    def sign_hash(self, hash_bytes: bytes) -> str:
        """
        Sign a precomputed digest using AWS KMS and return the base64-encoded signature.

        - hash_bytes must be the raw digest bytes (not hex).
        - Uses MessageType='DIGEST' because we sign the digest itself.
        """
        resp = self._client.sign(
            KeyId=self.config.key_id,
            Message=hash_bytes,
            MessageType="DIGEST",
            SigningAlgorithm=self.config.signing_algorithm,
        )
        signature: bytes = resp["Signature"]
        return base64.b64encode(signature).decode("ascii")

    def verify_hash(self, hash_bytes: bytes, signature_b64: str) -> bool:
        """
        Verify a signature using KMS Verify API.

        Returns True if signature valid, False otherwise.
        """
        signature = base64.b64decode(signature_b64)
        resp = self._client.verify(
            KeyId=self.config.key_id,
            Message=hash_bytes,
            MessageType="DIGEST",
            Signature=signature,
            SigningAlgorithm=self.config.signing_algorithm,
        )
        # KMS's Verify returns {"SignatureValid": True/False}
        return bool(resp.get("SignatureValid", False))
