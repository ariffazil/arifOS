"""
arifOS Attestation Layer — Supply-chain trust primitives.

Per the executive verdict (2026-06-15):
"SLSA gives supply-chain integrity controls; Sigstore signs and verifies artifacts
using transparency logs and identity-based signing. This matters because MCP
expands tool/action blast radius."

This package provides:
- sigstore_verify.py: Verify Sigstore-signed artifacts
- slsa_verify.py: SLSA provenance verification
- sbom_scan.py: CycloneDX SBOM scanner
- manifest_hash.py: BLAKE3 manifest hashing (already in deps)
"""

from .manifest_hash import ManifestHasher
from .sbom_scan import SBOMScanner
from .sigstore_verify import SigstoreVerifier, VerificationResult
from .slsa_verify import SLSAVerifier

__all__ = ["SigstoreVerifier", "VerificationResult", "SLSAVerifier", "SBOMScanner", "ManifestHasher"]
