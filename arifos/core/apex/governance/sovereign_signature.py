"""
arifOS v45 - Sovereign Signatures (Ed25519)
Cryptographic non-repudiation for Tier-4 Verdicts.
"""

from typing import Optional, Tuple
import hashlib
import os

# Try to import VerifyKey/SigningKey from nacl (PyNaCl)
# If unavailable, we provide a placeholder wrapper that fails securely or warns
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    from nacl.exceptions import BadSignatureError

    HAS_NACL = True
except ImportError:
    HAS_NACL = False


class SovereignSigner:
    """
    Wraps Ed25519 signing logic.
    """

    def __init__(self, private_key_hex: Optional[str] = None):
        if not HAS_NACL:
            # During development without deps, we might simulate or raise
            pass

        if private_key_hex:
            self._signing_key = SigningKey(private_key_hex, encoder=HexEncoder)
        else:
            # Generate new ephemeral key if none provided (for testing sessions)
            if HAS_NACL:
                self._signing_key = SigningKey.generate()
            else:
                self._signing_key = None

    def sign_verdict(self, verdict_hash: str, tier: str = "T1") -> str:
        """Sign a hash with Ed25519."""
        if not HAS_NACL:
            # TIER-4 LOCK: Critical tasks require real crypto
            if tier == "T4":
                raise RuntimeError(
                    "SECURITY_VIOLATION: Cannot sign T4 verdict without PyNaCl library."
                )

            # Deterministic Mock: Hash(Msg + Secret)
            mock_payload = f"{verdict_hash}:MOCK_SECRET_KEY"
            return f"mock_sig:{hashlib.sha256(mock_payload.encode()).hexdigest()}"

        # Sign the bytes of the hash string
        signed = self._signing_key.sign(verdict_hash.encode())
        return signed.signature.hex()

    def get_public_key(self) -> str:
        """Return public key in hex."""
        if not HAS_NACL:
            return "MOCK_PUB_KEY"
        return self._signing_key.verify_key.encode(encoder=HexEncoder).decode()


class SignatureVerifier:
    """
    Verifies Ed25519 signatures.
    """

    @staticmethod
    def verify(public_key_hex: str, message_hash: str, signature_hex: str) -> bool:
        """
        Verify that signature matches message_hash for public_key.
        """
        if not HAS_NACL:
            # Deterministic Mock Verification
            if not signature_hex.startswith("mock_sig:"):
                return False

            expected_payload = f"{message_hash}:MOCK_SECRET_KEY"
            expected_hash = hashlib.sha256(expected_payload.encode()).hexdigest()
            expected_sig = f"mock_sig:{expected_hash}"

            return signature_hex == expected_sig

        try:
            verify_key = VerifyKey(public_key_hex, encoder=HexEncoder)
            # check signature
            verify_key.verify(message_hash.encode(), bytes.fromhex(signature_hex))
            return True
        except (BadSignatureError, ValueError):
            return False
