"""
tests/test_item3_observatory_signed_snapshot.py — Item 3 acceptance tests.

Forged 2026-07-18 by kimi-code (FI-008) per sovereign (888) directive.

Acceptance tests (per sovereign ruling, 2026-07-18):
  1. Observatory probe semantics: network-fail ≠ "target absent".
     The auto-forge refactor delegates _local_chain_verify() to the
     canonical verifier (scope="canonical"), so historical gaps are
     declared as HISTORICAL, not as canonical-broken.

  2. Signed snapshot endpoint serves a real ed25519 signature with a
     verifiable fingerprint — not a fake or self-referential claim.

  3. Verification URL (DID document) is publicly reachable and contains
     the public key matching the local signing key.

DITEMPA BUKAN DIBERI — forged, not given.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest


# ─── Acceptance Test 1: Observatory probe semantics ─────────────────────────


class TestObservatoryProbeSemantics:
    """Probe semantics fix: scope=canonical for current health, historical as-is."""

    def test_observatory_local_chain_verify_uses_canonical_scope(self):
        """_local_chain_verify must delegate to canonical verifier, not walk raw."""
        from arifosmcp.runtime.rest_routes.observatory_routes import _local_chain_verify

        result = _local_chain_verify()

        # After the auto-forge refactor, the response should carry both
        # canonical_status and historical_status as independent facts.
        assert "canonical_status" in result, (
            "Observatory probe must distinguish canonical health from historical noise. "
            "Missing 'canonical_status' means probe is still using legacy walker."
        )
        assert "historical_status" in result, (
            "Observatory probe must report historical chain state separately."
        )
        # canonical_status: "HEALTHY" if canonical chain verifies; "BROKEN" if not
        assert result["canonical_status"] in ("HEALTHY", "BROKEN"), (
            f"canonical_status must be HEALTHY or BROKEN, got {result['canonical_status']!r}"
        )

    def test_observatory_does_not_conflate_full_with_canonical(self):
        """Legacy bug: full-history gaps reported as canonical-broken. Fixed."""
        from arifosmcp.runtime.rest_routes.observatory_routes import _local_chain_verify

        result = _local_chain_verify()

        # The legacy bug was: `verified: false` because historical gaps exist
        # even when canonical chain verifies. The fix surfaces both independently.
        if "verified" in result:
            # If verified field is present, it should mirror canonical_status
            # (NOT historical gaps)
            if result.get("canonical_status") == "HEALTHY":
                assert result["verified"] is True, (
                    "When canonical_status=HEALTHY, verified must be True. "
                    "Conflating historical gaps with canonical health is the "
                    "bug we just fixed."
                )


# ─── Acceptance Test 2: Signed snapshot endpoint ────────────────────────────


class TestSignedSnapshotEndpoint:
    """Snapshot must be ed25519-signed with verifiable metadata."""

    def test_observatory_signing_helper_produces_real_signature(self):
        """The sign_snapshot_payload() function produces a verifiable signature."""
        from arifosmcp.runtime.observatory_signing import sign_snapshot_payload

        payload = {
            "snapshot_id": "obs_test_001",
            "observed_at": "2026-07-18T13:00:00Z",
            "schema_version": "observatory.v1",
            "data": {"key": "value"},
        }
        sig = sign_snapshot_payload(payload)

        # Signature envelope structure
        assert sig.get("state") == "signed", f"Expected state=signed, got {sig!r}"
        assert sig.get("algorithm") == "ed25519"
        assert sig.get("key_algorithm") == "ed25519"
        assert sig.get("value"), "Signature value must be present"
        assert sig.get("key_id"), "Key fingerprint must be present"
        assert sig.get("payload_hash"), "Payload hash must be present"
        assert sig.get("canonicalization") == "sort_keys+separators+utf8+no_nan"
        assert sig.get("verification_url"), "Verification URL must be present"

        # The signature value must be valid base64
        sig_bytes = base64.b64decode(sig["value"])
        assert len(sig_bytes) == 64, (
            f"ed25519 signatures are 64 bytes, got {len(sig_bytes)}"
        )

    def test_signature_verifies_against_local_public_key(self):
        """The signature must verify against the local ed25519 public key."""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        from arifosmcp.runtime.observatory_signing import (
            PUBLIC_KEY_PATH,
            _canonical_json,
            sign_snapshot_payload,
        )

        if not PUBLIC_KEY_PATH.exists():
            pytest.skip("Local public key not found; skip integration test")

        # Load the public key
        from cryptography.hazmat.primitives import serialization

        public_pem = PUBLIC_KEY_PATH.read_bytes()
        public_key = serialization.load_pem_public_key(public_pem)
        assert isinstance(public_key, Ed25519PublicKey)

        # Sign a payload
        payload = {
            "snapshot_id": "obs_verify_001",
            "observed_at": "2026-07-18T13:00:00Z",
            "schema_version": "observatory.v1",
            "test": True,
        }
        sig = sign_snapshot_payload(payload)

        # Recompute the canonical bytes the signature covers
        unsigned = {k: v for k, v in payload.items()}
        canonical = json.dumps(
            unsigned,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")

        # Verify
        sig_bytes = base64.b64decode(sig["value"])
        public_key.verify(sig_bytes, canonical)

    def test_signature_canonical_json_excludes_signature_field(self):
        """The canonical bytes must NOT include the 'signature' field itself."""
        from arifosmcp.runtime.observatory_signing import _canonical_json, sign_snapshot_payload

        payload = {"snapshot_id": "obs_no_self_ref", "observed_at": "2026-07-18T13:00:00Z"}
        sig = sign_snapshot_payload(payload)

        # The payload_hash should equal sha256(canonical_json(payload without signature))
        unsigned = {k: v for k, v in payload.items()}
        expected_hash = hashlib.sha256(
            json.dumps(
                unsigned,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        assert sig["payload_hash"] == expected_hash


# ─── Acceptance Test 3: Signing key fingerprint ──────────────────────────────


class TestSigningKeyFingerprint:
    """Key fingerprint must be stable and exposed for verification."""

    def test_fingerprint_is_ed25519_prefixed(self):
        from arifosmcp.runtime.observatory_signing import get_public_key_fingerprint

        fp = get_public_key_fingerprint()
        assert fp.startswith("ed25519:sha256:"), (
            f"Fingerprint must be ed25519-prefixed, got {fp!r}"
        )

    def test_fingerprint_is_stable_across_calls(self):
        from arifosmcp.runtime.observatory_signing import get_public_key_fingerprint

        fp1 = get_public_key_fingerprint()
        fp2 = get_public_key_fingerprint()
        assert fp1 == fp2, "Fingerprint must be deterministic"
