"""
Tests for Vault999 BLS Phase A — BLSVaultSigner

Covers:
- Keypair derivation (deterministic)
- Individual sign + verify
- Supermajority aggregation (3-of-5)
- O(1) aggregate verify
- Tamper detection
- Quorum enforcement
- Payload hash consistency
- F1/F2/F11/F13 constitutional invariants
"""

import hashlib
import json
import time
from copy import deepcopy

import pytest

from core.shared.bls_vault import (
    BLS_AVAILABLE,
    JUROR_IDS,
    SUPERMAJORITY_THRESHOLD,
    BLSVaultSigner,
    JurorKeyPair,
    JurorSignature,
    VaultBLSSeal,
    _canonical_hash,
)

pytestmark = pytest.mark.skipif(
    not BLS_AVAILABLE, reason="py_ecc not installed — BLS tests skipped"
)

_PAYLOAD = {
    "verdict": "SEAL",
    "tool": "vault_ledger",
    "stage": "999_VAULT",
    "session_id": "test_001",
    "decision": "Constitutional amendment ratified",
}


@pytest.fixture(scope="module")
def signer() -> BLSVaultSigner:
    return BLSVaultSigner()


@pytest.fixture(scope="module")
def three_sigs(signer: BLSVaultSigner) -> list[JurorSignature]:
    return [signer.sign(_PAYLOAD, jid) for jid in JUROR_IDS[:3]]


@pytest.fixture(scope="module")
def valid_seal(signer: BLSVaultSigner, three_sigs: list[JurorSignature]) -> VaultBLSSeal:
    return signer.aggregate_seal(_PAYLOAD, three_sigs)


# ── Keypair derivation ────────────────────────────────────────────────────────


class TestJurorKeyPair:
    def test_deterministic_per_juror(self):
        """Same juror_id always yields same keypair."""
        kp1 = JurorKeyPair.from_juror_id("DELTA_MIND")
        kp2 = JurorKeyPair.from_juror_id("DELTA_MIND")
        assert kp1.public_key_hex == kp2.public_key_hex
        assert kp1.private_key_hex == kp2.private_key_hex

    def test_unique_per_juror(self):
        """Different juror_ids yield different keys."""
        keys = {JurorKeyPair.from_juror_id(jid).public_key_hex for jid in JUROR_IDS}
        assert len(keys) == len(JUROR_IDS)

    def test_public_key_length(self):
        """BLS12-381 G1 compressed pubkey is 48 bytes = 96 hex chars."""
        kp = JurorKeyPair.from_juror_id("PSI_SOUL")
        assert len(kp.public_key_hex) == 96

    def test_signer_exposes_public_keys(self, signer: BLSVaultSigner):
        for jid in JUROR_IDS:
            pk = signer.get_public_key(jid)
            assert len(pk) == 96  # 48 bytes compressed G1

    def test_unknown_juror_raises(self, signer: BLSVaultSigner):
        with pytest.raises(ValueError, match="Unknown juror"):
            signer.get_public_key("FAKE_AGENT")


# ── Individual signing ────────────────────────────────────────────────────────


class TestIndividualSign:
    def test_sign_returns_signature(self, signer: BLSVaultSigner):
        sig = signer.sign(_PAYLOAD, "DELTA_MIND")
        assert isinstance(sig, JurorSignature)
        assert sig.juror_id == "DELTA_MIND"
        assert len(sig.signature_hex) == 192  # 96 bytes G2 point

    def test_signature_covers_payload_hash(self, signer: BLSVaultSigner):
        sig = signer.sign(_PAYLOAD, "OMEGA_HEART")
        expected_hash = _canonical_hash(_PAYLOAD)
        assert sig.payload_hash == expected_hash

    def test_verify_valid_signature(self, signer: BLSVaultSigner):
        sig = signer.sign(_PAYLOAD, "PSI_SOUL")
        assert signer.verify_individual(sig) is True

    def test_verify_fails_wrong_juror(self, signer: BLSVaultSigner):
        """Signature from DELTA_MIND cannot be verified against OMEGA_HEART's key."""
        sig = signer.sign(_PAYLOAD, "DELTA_MIND")
        # Swap juror_id
        tampered = JurorSignature(
            juror_id="OMEGA_HEART",
            payload_hash=sig.payload_hash,
            signature_hex=sig.signature_hex,
        )
        assert signer.verify_individual(tampered) is False

    def test_verify_fails_tampered_hash(self, signer: BLSVaultSigner):
        sig = signer.sign(_PAYLOAD, "A_AUDITOR")
        tampered = JurorSignature(
            juror_id=sig.juror_id,
            payload_hash="a" * 64,
            signature_hex=sig.signature_hex,
        )
        assert signer.verify_individual(tampered) is False

    def test_unknown_juror_raises_on_sign(self, signer: BLSVaultSigner):
        with pytest.raises(ValueError, match="Unknown juror"):
            signer.sign(_PAYLOAD, "GHOST_AGENT")

    def test_deterministic_signature(self, signer: BLSVaultSigner):
        """Same juror signing same payload always produces same signature (BLS is deterministic)."""
        s1 = signer.sign(_PAYLOAD, "A_VALIDATOR")
        s2 = signer.sign(_PAYLOAD, "A_VALIDATOR")
        assert s1.signature_hex == s2.signature_hex


# ── Aggregation ───────────────────────────────────────────────────────────────


class TestAggregation:
    def test_seal_structure(self, valid_seal: VaultBLSSeal):
        assert valid_seal.verdict == "SEAL"
        assert len(valid_seal.juror_ids) == 3
        assert valid_seal.quorum_fraction == 0.6
        assert valid_seal.seal_id.startswith("seal_")
        assert len(valid_seal.aggregate_signature_hex) == 192
        assert len(valid_seal.aggregate_pubkey_hex) == 96

    def test_aggregate_verify_true(self, signer: BLSVaultSigner, valid_seal: VaultBLSSeal):
        """O(1) aggregate verify must pass for a valid seal."""
        assert signer.verify_seal(valid_seal) is True

    def test_aggregate_verify_all_5_jurors(self, signer: BLSVaultSigner):
        sigs = [signer.sign(_PAYLOAD, jid) for jid in JUROR_IDS]
        seal = signer.aggregate_seal(_PAYLOAD, sigs)
        assert seal.quorum_fraction == 1.0
        assert signer.verify_seal(seal) is True

    def test_tampered_payload_hash_fails(self, signer: BLSVaultSigner, valid_seal: VaultBLSSeal):
        """F2 TRUTH: modifying payload_hash must break verify."""
        bad = deepcopy(valid_seal)
        bad.payload_hash = "b" * 64
        assert signer.verify_seal(bad) is False

    def test_tampered_aggregate_sig_fails(
        self, signer: BLSVaultSigner, valid_seal: VaultBLSSeal
    ):
        bad = deepcopy(valid_seal)
        bad.aggregate_signature_hex = "cc" * 96
        assert signer.verify_seal(bad) is False

    def test_tampered_aggregate_pubkey_fails(
        self, signer: BLSVaultSigner, valid_seal: VaultBLSSeal
    ):
        bad = deepcopy(valid_seal)
        bad.aggregate_pubkey_hex = "dd" * 48
        assert signer.verify_seal(bad) is False

    def test_seal_serialisation_roundtrip(self, valid_seal: VaultBLSSeal):
        """Seal must survive dict → JSON → dict without loss."""
        as_dict = valid_seal.to_dict()
        restored = VaultBLSSeal.from_dict(as_dict)
        assert restored.seal_id == valid_seal.seal_id
        assert restored.aggregate_signature_hex == valid_seal.aggregate_signature_hex
        assert restored.payload_hash == valid_seal.payload_hash

    def test_chain_hash_deterministic(self, valid_seal: VaultBLSSeal):
        h1 = valid_seal.chain_hash()
        h2 = valid_seal.chain_hash()
        assert h1 == h2
        assert len(h1) == 64


# ── Quorum enforcement (F1 AMANAH) ───────────────────────────────────────────


class TestQuorumEnforcement:
    def test_below_threshold_raises(self, signer: BLSVaultSigner):
        """F1 AMANAH: fewer than 3 signatures must not produce a seal."""
        sigs = [signer.sign(_PAYLOAD, jid) for jid in JUROR_IDS[:2]]
        with pytest.raises(ValueError, match="888_HOLD"):
            signer.aggregate_seal(_PAYLOAD, sigs, require_supermajority=True)

    def test_below_threshold_allowed_when_disabled(self, signer: BLSVaultSigner):
        """When require_supermajority=False (testing), aggregation proceeds."""
        sigs = [signer.sign(_PAYLOAD, jid) for jid in JUROR_IDS[:2]]
        seal = signer.aggregate_seal(_PAYLOAD, sigs, require_supermajority=False)
        assert len(seal.juror_ids) == 2

    def test_exactly_at_threshold_succeeds(self, signer: BLSVaultSigner):
        sigs = [signer.sign(_PAYLOAD, jid) for jid in JUROR_IDS[:SUPERMAJORITY_THRESHOLD]]
        seal = signer.aggregate_seal(_PAYLOAD, sigs)
        assert signer.verify_seal(seal) is True

    def test_mismatched_payload_raises(self, signer: BLSVaultSigner):
        """F2 TRUTH: jurors cannot sign different payloads."""
        different_payload = dict(_PAYLOAD, session_id="different_session")
        sig_good = signer.sign(_PAYLOAD, "DELTA_MIND")
        sig_bad = signer.sign(different_payload, "OMEGA_HEART")
        sig_ok2 = signer.sign(_PAYLOAD, "PSI_SOUL")
        with pytest.raises(ValueError, match="F2 TRUTH"):
            signer.aggregate_seal(_PAYLOAD, [sig_good, sig_bad, sig_ok2])

    def test_verify_seal_below_recorded_quorum_fails(
        self, signer: BLSVaultSigner, valid_seal: VaultBLSSeal
    ):
        """F11 AUDITABILITY: recorded quorum below threshold → verify returns False."""
        bad = deepcopy(valid_seal)
        bad.quorum_fraction = 0.1  # clearly below threshold
        assert signer.verify_seal(bad) is False


# ── Constitutional invariants ─────────────────────────────────────────────────


class TestConstitutionalInvariants:
    def test_floor_compliance_present(self, valid_seal: VaultBLSSeal):
        """F11 AUDITABILITY: floor compliance must be recorded in every seal."""
        assert valid_seal.floor_compliance["F1_AMANAH"] is True
        assert valid_seal.floor_compliance["F2_TRUTH"] is True
        assert valid_seal.floor_compliance["F11_AUDITABILITY"] is True
        assert valid_seal.floor_compliance["F13_ADAPTABILITY"] is True

    def test_canonical_hash_deterministic(self):
        """F2 TRUTH: hash must be order-independent."""
        p1 = {"a": 1, "b": 2}
        p2 = {"b": 2, "a": 1}
        assert _canonical_hash(p1) == _canonical_hash(p2)

    def test_canonical_hash_different_payloads(self):
        assert _canonical_hash({"x": 1}) != _canonical_hash({"x": 2})

    def test_individual_pubkeys_present_in_seal(self, valid_seal: VaultBLSSeal):
        """F11 AUDITABILITY: individual pubkeys must be preserved for external audit."""
        assert len(valid_seal.individual_pubkeys_hex) == 3
        for pk_hex in valid_seal.individual_pubkeys_hex:
            assert len(pk_hex) == 96
