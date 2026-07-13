"""
signed_receipt.py — P1.3 Ed25519-signed receipt chain for VAULT999.

Each receipt gets an Ed25519 signature binding:
  - event_type
  - receipt_id
  - payload_hash
  - previous_hash
  - writer_identity
  - key_id
  - timestamp
  - schema_version

Uses sovereign_signer.py for the actual Ed25519 operations.
Service signer for routine receipts; sovereign key for sovereign-class events.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# Schema version for receipt signing
RECEIPT_SCHEMA_VERSION = "v1"


@dataclass
class SignedReceipt:
    """A VAULT999 receipt with Ed25519 signature."""
    receipt_id: str
    event_type: str
    payload_hash: str
    previous_hash: str
    writer_identity: str
    key_id: str
    timestamp: str
    schema_version: str
    signature: str  # base64 Ed25519 signature

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "event_type": self.event_type,
            "payload_hash": self.payload_hash,
            "previous_hash": self.previous_hash,
            "writer_identity": self.writer_identity,
            "key_id": self.key_id,
            "timestamp": self.timestamp,
            "schema_version": self.schema_version,
            "signature": self.signature,
        }

    def signature_payload(self) -> str:
        """The canonical string that was signed."""
        return (
            f"arifos-receipt-{self.schema_version}\n"
            f"receipt_id={self.receipt_id}\n"
            f"event_type={self.event_type}\n"
            f"payload_hash={self.payload_hash}\n"
            f"previous_hash={self.previous_hash}\n"
            f"writer={self.writer_identity}\n"
            f"key_id={self.key_id}\n"
            f"timestamp={self.timestamp}"
        )


@dataclass
class VerificationResult:
    """Result of verifying a signed receipt."""
    valid: bool
    reason: str = ""
    receipt_id: str = ""
    key_id: str = ""


def _hash_payload(payload: dict[str, Any]) -> str:
    """SHA256 of canonical JSON payload."""
    content = json.dumps(payload, sort_keys=True)
    return f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"


def _generate_receipt_id() -> str:
    """Generate a unique receipt ID."""
    return f"rcpt-{secrets.token_hex(12)}"


def sign_receipt(
    event_type: str,
    payload: dict[str, Any],
    previous_hash: str,
    writer_identity: str,
    *,
    key_id: str = "service",
    use_sovereign: bool = False,
) -> SignedReceipt | None:
    """Sign a receipt with Ed25519.

    Args:
        event_type: Type of event (e.g., "cooling.receipt", "seal.decision")
        payload: The receipt payload
        previous_hash: Hash of the previous receipt in the chain
        writer_identity: Who is writing this receipt
        key_id: Key identifier (default: "service" for routine receipts)
        use_sovereign: If True, use the sovereign key (for sovereign-class events)

    Returns:
        SignedReceipt or None if signing fails
    """
    try:
        receipt_id = _generate_receipt_id()
        payload_hash = _hash_payload(payload)
        timestamp = datetime.now(UTC).isoformat()
        schema_version = RECEIPT_SCHEMA_VERSION

        if use_sovereign:
            key_id = "sovereign"

        # Build the canonical signing payload
        signing_string = (
            f"arifos-receipt-{schema_version}\n"
            f"receipt_id={receipt_id}\n"
            f"event_type={event_type}\n"
            f"payload_hash={payload_hash}\n"
            f"previous_hash={previous_hash}\n"
            f"writer={writer_identity}\n"
            f"key_id={key_id}\n"
            f"timestamp={timestamp}"
        )

        # Sign with Ed25519
        signature = _sign_with_key(signing_string, use_sovereign=use_sovereign)
        if not signature:
            logger.error("Failed to sign receipt %s", receipt_id)
            return None

        return SignedReceipt(
            receipt_id=receipt_id,
            event_type=event_type,
            payload_hash=payload_hash,
            previous_hash=previous_hash,
            writer_identity=writer_identity,
            key_id=key_id,
            timestamp=timestamp,
            schema_version=schema_version,
            signature=signature,
        )

    except Exception as e:
        logger.error("sign_receipt failed: %s", e)
        return None


def verify_receipt_signature(receipt: SignedReceipt | dict[str, Any]) -> VerificationResult:
    """Verify the Ed25519 signature on a receipt.

    Returns VerificationResult with valid=True if signature is correct.
    """
    if isinstance(receipt, dict):
        try:
            receipt = SignedReceipt(**receipt)
        except Exception as e:
            return VerificationResult(valid=False, reason=f"invalid_receipt_format: {e}")

    try:
        # Reconstruct the signing payload
        signing_string = receipt.signature_payload()

        # Verify the signature
        valid = _verify_signature(
            signing_string,
            receipt.signature,
            key_id=receipt.key_id,
        )

        if valid:
            return VerificationResult(
                valid=True,
                receipt_id=receipt.receipt_id,
                key_id=receipt.key_id,
            )
        else:
            return VerificationResult(
                valid=False,
                reason="signature_verification_failed",
                receipt_id=receipt.receipt_id,
                key_id=receipt.key_id,
            )

    except Exception as e:
        return VerificationResult(
            valid=False,
            reason=f"verification_error: {e}",
            receipt_id=receipt.receipt_id,
        )


def _sign_with_key(message: str, *, use_sovereign: bool = False) -> str | None:
    """Sign a message with Ed25519. Returns base64 signature or None."""
    try:
        from arifosmcp.runtime.sovereign_signer import load_private_key

        key_bytes = load_private_key()
        if not key_bytes:
            return None

        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives.serialization import load_der_private_key

        # Try loading as raw bytes first, then PEM
        try:
            private_key = Ed25519PrivateKey.from_private_bytes(key_bytes)
        except Exception:
            private_key = load_der_private_key(key_bytes, password=None)

        import base64
        signature = private_key.sign(message.encode())
        return base64.b64encode(signature).decode()

    except ImportError:
        logger.error("sovereign_signer not available for signing")
        return None
    except Exception as e:
        logger.error("Ed25519 signing failed: %s", e)
        return None


def _verify_signature(message: str, signature_b64: str, *, key_id: str = "service") -> bool:
    """Verify an Ed25519 signature. Returns True if valid."""
    try:
        import base64
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        # Load the public key based on key_id
        public_key_bytes = _get_public_key(key_id)
        if not public_key_bytes:
            logger.error("No public key found for key_id=%s", key_id)
            return False

        public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)
        signature = base64.b64decode(signature_b64)

        public_key.verify(signature, message.encode())
        return True

    except Exception as e:
        logger.warning("Signature verification failed for key_id=%s: %s", key_id, e)
        return False


def _get_public_key(key_id: str) -> bytes | None:
    """Get the public key bytes for a given key_id."""
    # For now, load from the sovereign key file
    # In production, this would be a key registry
    try:
        from pathlib import Path

        key_paths = [
            Path("/root/compose/sekrits/arifos_sovereign.key"),
            Path("/root/arifos/secrets/arifos_sovereign.key"),
        ]

        for key_path in key_paths:
            if key_path.exists():
                from cryptography.hazmat.primitives.serialization import (
                    load_pem_private_key,
                    Encoding,
                    PublicFormat,
                )

                key_data = key_path.read_bytes()
                try:
                    private_key = load_pem_private_key(key_data, password=None)
                    public_key = private_key.public_key()
                    return public_key.public_bytes(
                        Encoding.Raw,
                        PublicFormat.Raw,
                    )
                except Exception:
                    # Try raw format
                    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
                    private_key = Ed25519PrivateKey.from_private_bytes(key_data[:32])
                    public_key = private_key.public_key()
                    return public_key.public_bytes(
                        Encoding.Raw,
                        PublicFormat.Raw,
                    )

    except Exception as e:
        logger.error("Failed to load public key for %s: %s", key_id, e)

    return None


__all__ = [
    "SignedReceipt",
    "VerificationResult",
    "sign_receipt",
    "verify_receipt_signature",
    "RECEIPT_SCHEMA_VERSION",
]
