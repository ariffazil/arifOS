"""
Sigstore Verifier — Verify Sigstore-signed artifacts.

Sigstore = keyless signing with transparency log (Rekor) + certificate authority (Fulcio).

Constitutional binding:
- F1 AMANAH: Fail-closed on signature mismatch
- F8 LAW: No unverified artifact can be invoked by a tool
- F11 AUDIT: Every verification is recorded with witness identity

References:
- https://www.sigstore.dev/
- https://github.com/sigstore/sigstore-python
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Optional

import structlog

log = structlog.get_logger("arifos.attestation.sigstore")

# Defer sigstore import to avoid hard dep if not used
try:
    from sigstore.verify import Verifier as _SigstoreNativeVerifier
    SIGSTORE_AVAILABLE = True
except ImportError:
    SIGSTORE_AVAILABLE = False


@dataclass
class VerificationResult:
    """Outcome of a Sigstore verification."""

    verified: bool
    artifact_sha256: str
    signature_present: bool
    certificate_identity: Optional[str]
    transparency_log_entry: Optional[str]
    error: Optional[str]
    timestamp: str

    def __str__(self) -> str:
        return f"VerificationResult(verified={self.verified}, identity={self.certificate_identity or 'none'})"


class SigstoreVerifier:
    """
    Verify Sigstore-signed artifacts.

    Use case: When a new MCP tool is added from an external source, verify
    that the source signed it with a recognized identity (e.g., the organ's
    release key).

    F8 LAW: An unverified artifact cannot be invoked by a tool.
    """

    def __init__(self, trust_root: str = "sigstore"):
        self.trust_root = trust_root
        self._verifier = None
        if SIGSTORE_AVAILABLE:
            try:
                self._verifier = _SigstoreNativeVerifier.trust_root(trust_root)
            except Exception as e:
                log.warning("sigstore_init_failed", error=str(e))

    def is_available(self) -> bool:
        return self._verifier is not None

    def verify_artifact(
        self,
        artifact_path: str,
        certificate_identity: Optional[str] = None,
    ) -> VerificationResult:
        """
        Verify a signed artifact at artifact_path.

        If sigstore is not available or signature is missing, returns verified=False.
        """
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Compute SHA256
        try:
            with open(artifact_path, "rb") as f:
                digest = hashlib.sha256(f.read()).hexdigest()
        except OSError as e:
            return VerificationResult(
                verified=False,
                artifact_sha256="",
                signature_present=False,
                certificate_identity=None,
                transparency_log_entry=None,
                error=str(e),
                timestamp=ts,
            )

        if self._verifier is None:
            return VerificationResult(
                verified=False,
                artifact_sha256=digest,
                signature_present=False,
                certificate_identity=None,
                transparency_log_entry=None,
                error="sigstore verifier not available",
                timestamp=ts,
            )

        # TODO: wire full sigstore-python verification
        # For now, we record the SHA256 and mark as unverified until
        # the artifact is signed and the signature bundle is provided.
        return VerificationResult(
            verified=False,
            artifact_sha256=digest,
            signature_present=False,
            certificate_identity=None,
            transparency_log_entry=None,
            error="sigstore-python verification not yet wired (Phase 2)",
            timestamp=ts,
        )
