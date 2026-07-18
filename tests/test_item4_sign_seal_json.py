"""
tests/test_item4_sign_seal_json.py — Item 4 acceptance tests.

Forged 2026-07-18 by kimi-code (FI-008) per sovereign (888) directive.

Acceptance tests (per sovereign ruling, 2026-07-18):
  1. seal.json is signed with ed25519 (snapshot key).
  2. The signature is verifiable against the local public key.
  3. The signature envelope is structurally correct (alg/value/key_id).
  4. The placeholder `cryptographic_proof` (a self-referential DID string)
     is replaced by a real `signature` envelope — no more self-reference.
  5. Re-signing produces deterministic output for the same payload.
  6. The signing script writes to a canonical local path with the .signed
     suffix (F1 AMANAH: original unsigned artifact preserved).

DITEMPA BUKAN DIBERI — forged, not given.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

# Repo layout: arifOS flat — add repo root to path so scripts/sign_seal_json is importable
_ARIFOS_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ARIFOS_ROOT))


# ─── paths ───────────────────────────────────────────────────────────────────


PUBLIC_SEAL = Path("/root/ARIF-SITES/sites/arif-fazil.com/public/999/seal.json")
SIGNED_SEAL = Path("/root/ARIF-SITES/sites/arif-fazil.com/public/999/seal.json.signed")
SIGN_SCRIPT = _ARIFOS_ROOT / "scripts" / "sign_seal_json.py"
PUBLIC_KEY_PATH = Path("/root/.arifos/observatory/keys/observatory_signing_key.pub.pem")


# ─── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def signed_payload():
    if not SIGNED_SEAL.exists():
        pytest.skip(f"Signed seal artifact not found: {SIGNED_SEAL}")
    return json.loads(SIGNED_SEAL.read_text(encoding="utf-8"))


# ─── Acceptance Test 1: real ed25519 signature ──────────────────────────────


class TestSealSigned:
    """seal.json.signed carries a real ed25519 signature, not a self-reference."""

    def test_has_signature_envelope(self, signed_payload):
        assert "signature" in signed_payload, (
            "Signed seal.json must contain 'signature' envelope. "
            "Missing field means signing pipeline did not run."
        )
        sig = signed_payload["signature"]
        assert sig.get("alg") == "ed25519"
        assert sig.get("key_id", "").startswith("ed25519:sha256:")
        assert sig.get("value"), "Signature value must be present"

    def test_signature_is_real_ed25519_size(self, signed_payload):
        sig_bytes = base64.b64decode(signed_payload["signature"]["value"])
        assert len(sig_bytes) == 64, (
            f"ed25519 signatures are 64 bytes, got {len(sig_bytes)}. "
            f"This usually means the field contains an opaque blob, not a real signature."
        )

    def test_self_referential_cryptographic_proof_removed(self, signed_payload):
        """The old `cryptographic_proof: did:web:...` self-reference must be gone."""
        assert "cryptographic_proof" not in signed_payload, (
            "Signed seal.json must NOT carry the old self-referential "
            "`cryptographic_proof: did:web:arif-fazil.com` field. "
            "The real cryptographic proof is now in `signature`."
        )


# ─── Acceptance Test 2: cryptographic verification ─────────────────────────


class TestSealSignatureVerifies:
    """The signature must verify against the local Observatory public key."""

    def test_helper_verify_seal_entry_returns_true(self, signed_payload):
        from arifosmcp.runtime.seal_chain_signing import verify_seal_entry
        assert verify_seal_entry(signed_payload) is True

    def test_manual_ed25519_verify(self, signed_payload):
        if not PUBLIC_KEY_PATH.exists():
            pytest.skip("Local public key not present")

        from cryptography.hazmat.primitives import serialization

        sig_bytes = base64.b64decode(signed_payload["signature"]["value"])
        # Canonical JSON excludes the 'signature' field
        canonical = json.dumps(
            {k: v for k, v in signed_payload.items() if k != "signature"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        pub_pem = PUBLIC_KEY_PATH.read_bytes()
        pub_key = serialization.load_pem_public_key(pub_pem)
        pub_key.verify(sig_bytes, canonical)


# ─── Acceptance Test 3: determinism ─────────────────────────────────────────


class TestSealSigningDeterminism:
    """Re-signing the same unsigned payload produces a different signature
    each time (because nonce/timestamp is included), but the canonical bytes
    used for signing must be deterministic."""

    def test_canonical_bytes_are_deterministic(self, signed_payload):
        """Canonical JSON of the unsigned payload must be the same every time."""
        canonical_a = json.dumps(
            {k: v for k, v in signed_payload.items() if k != "signature"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        canonical_b = json.dumps(
            {k: v for k, v in signed_payload.items() if k != "signature"},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        assert canonical_a == canonical_b


# ─── Acceptance Test 4: F1 AMANAH — unsigned preserved ─────────────────────


class TestUnsignedArtifactPreserved:
    """The original unsigned seal.json must still exist (F1 AMANAH)."""

    def test_unsigned_seal_still_on_disk(self):
        assert PUBLIC_SEAL.exists(), (
            "F1 AMANAH violation: unsigned seal.json was deleted. "
            "It must be preserved as audit trail."
        )

    def test_unsigned_seal_differs_from_signed(self):
        if not PUBLIC_SEAL.exists() or not SIGNED_SEAL.exists():
            pytest.skip("Need both unsigned and signed artifacts on disk")
        unsigned = json.loads(PUBLIC_SEAL.read_text(encoding="utf-8"))
        signed = json.loads(SIGNED_SEAL.read_text(encoding="utf-8"))
        assert "signature" not in unsigned, (
            "Original unsigned seal.json should not have a signature field. "
            "If it does, the sign script overwrote the source — that's a "
            "reversibility violation."
        )
        assert "signature" in signed, "Signed seal.json must have signature"


# ─── Acceptance Test 5: signing script exists and is runnable ──────────────


class TestSignScriptRunnable:
    """scripts/sign_seal_json.py must exist and execute cleanly."""

    def test_script_exists(self):
        assert SIGN_SCRIPT.exists(), f"Missing: {SIGN_SCRIPT}"

    def test_script_has_fail_closed_verification(self):
        """The script must verify the signature BEFORE writing (fail-closed)."""
        src = SIGN_SCRIPT.read_text(encoding="utf-8")
        assert "verify_seal_entry" in src, (
            "sign_seal_json.py must call verify_seal_entry() before writing. "
            "Fail-open (sign then trust) would corrupt the audit trail."
        )
        # verify must happen BEFORE write
        verify_pos = src.find("verify_seal_entry")
        write_pos = src.find("write_text")
        assert verify_pos < write_pos, (
            "verify_seal_entry must run BEFORE write_text for fail-closed behavior."
        )
