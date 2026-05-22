import pytest
import base64
import hashlib
from nacl.signing import SigningKey

# ─────────────────────────────────────────────────────────────────────────────
# SHIM — mock external arifosmcp.core.governance dependencies
# ─────────────────────────────────────────────────────────────────────────────


class _MockThermodynamicMetrics:
    def __init__(self, **kwargs):
        self.floor_13_signal = 0.0
        self.floor_12_signal = 0.0
        self.floor_11_signal = 0.0
        self.floor_10_signal = 0.0
        self.floor_9_signal = 0.0
        self.floor_8_signal = 0.0
        self.__dict__.update(kwargs)


class _MockAppendVault999Event:
    def __call__(self, event_type, payload, operator_id, session_id):
        return "mock_hash"


class _MockGovernedReturn:
    def __call__(self, tool_name, report, metrics, operator_id, session_id, **kwargs):
        return report


# Inject mocks BEFORE importing the modules
import arifosmcp.core.governance as _mock_gov

_mock_gov.ThermodynamicMetrics = _MockThermodynamicMetrics
_mock_gov.append_vault999_event = _MockAppendVault999Event()
_mock_gov.governed_return = _MockGovernedReturn()

from arifosmcp.security import msap
from arifosmcp.tools import _888_judge, _999_vault

# Test key pair
TEST_SEED = b"test_seed_1234567890123456789012"  # 32 bytes
_sk = SigningKey(TEST_SEED)
TEST_PUBKEY_B64 = base64.urlsafe_b64encode(_sk.verify_key.encode()).decode().rstrip("=")


@pytest.fixture
def signing_key():
    return _sk


@pytest.fixture
def registered_keys():
    return {"ARIF": TEST_PUBKEY_B64}


def sign_packet(packet, signing_key):
    canonical_str = msap.get_canonical_digest_string(packet)
    digest = hashlib.sha256(canonical_str.encode("utf-8")).digest()
    sig = signing_key.sign(digest).signature
    return base64.urlsafe_b64encode(sig).decode().rstrip("=")


@pytest.mark.asyncio
async def test_valid_msap_ack(signing_key, registered_keys):
    actor_id = "ARIF"
    session_id = "SESS-123"
    payload_hash = "sha256:payload123"
    judge_hash = "sha256:judge123"
    chain_id = "CHAIN-123"

    challenge = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)

    packet = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id=session_id,
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge.nonce,
        expires_at=str(int(challenge.expires_at)),
    )

    packet.signature = sign_packet(packet, signing_key)

    res = msap.verify_sovereign_ack(packet.__dict__, registered_keys)
    assert res.signed_ack_valid is True
    assert res.zkpc_level == 1
    assert res.reason == "ACK_OK_BUT_ZKPC_QUARANTINED_TOY_CIRCUIT_NO_AUTHORITY"


@pytest.mark.asyncio
async def test_replay_attack(signing_key, registered_keys):
    actor_id = "ARIF"
    session_id = "SESS-123"
    payload_hash = "sha256:payload123"
    judge_hash = "sha256:judge123"
    chain_id = "CHAIN-123"

    challenge = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)
    packet = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id=session_id,
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge.nonce,
        expires_at=str(int(challenge.expires_at)),
    )
    packet.signature = sign_packet(packet, signing_key)

    # First time OK
    res1 = msap.verify_sovereign_ack(packet.__dict__, registered_keys)
    assert res1.signed_ack_valid is True

    # Second time FAIL
    res2 = msap.verify_sovereign_ack(packet.__dict__, registered_keys)
    assert res2.signed_ack_valid is False
    assert res2.reason == "REPLAY_ATTEMPT"


@pytest.mark.asyncio
async def test_wrong_binding(signing_key, registered_keys):
    actor_id = "ARIF"
    session_id = "SESS-123"
    payload_hash = "sha256:payload123"
    judge_hash = "sha256:judge123"
    chain_id = "CHAIN-123"

    challenge = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)

    # Packet with wrong session_id
    packet = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id="WRONG-SESS",
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge.nonce,
        expires_at=str(int(challenge.expires_at)),
    )
    packet.signature = sign_packet(packet, signing_key)

    res = msap.verify_sovereign_ack(packet.__dict__, registered_keys)
    assert res.signed_ack_valid is False
    assert res.reason == "SESSION_MISMATCH"


@pytest.mark.asyncio
async def test_dev_override(signing_key, registered_keys, monkeypatch):
    monkeypatch.setenv("ARIFOS_DEV_ALLOW_MSAP_LEVEL2", "true")

    actor_id = "ARIF"
    session_id = "SESS-123"
    payload_hash = "sha256:payload123"
    judge_hash = "sha256:judge123"
    chain_id = "CHAIN-123"

    challenge = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)
    packet = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id=session_id,
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge.nonce,
        expires_at=str(int(challenge.expires_at)),
    )
    packet.signature = sign_packet(packet, signing_key)

    res = msap.verify_sovereign_ack(packet.__dict__, registered_keys)
    assert res.signed_ack_valid is True
    assert res.zkpc_level == 1
    assert "ZKPC_QUARANTINED" in res.reason


@pytest.mark.asyncio
async def test_judge_blocking_level1(signing_key, registered_keys):
    # MSAP v0.1 by default returns level 1.
    # Judge requires level 2 for irreversible actions.
    evidence_bundle = {
        "metrics": {
            "truth_score": 1.0,
            "delta_s": 0.0,
            "omega_0": 0.04,
            "peace_squared": 1.0,
            "amanah_lock": True,
            "tri_witness_score": 1.0,
            "stakeholder_safety": 1.0,
        },
        "is_irreversible": True,
        "zkpc_level": 1,  # Level 1 from MSAP
    }

    res = await _888_judge.execute(evidence_bundle)
    assert res["verdict"] == "888_HOLD"
    assert "F1_AMANAH_ZKPC" in res["rationale"]


@pytest.mark.asyncio
async def test_vault_seal_integration(signing_key, registered_keys, monkeypatch):
    # Set ARIF_PUBKEY for vault fallback
    monkeypatch.setenv("ARIF_PUBKEY", TEST_PUBKEY_B64)

    actor_id = "ARIF"
    session_id = "SESS-123"
    payload_hash = "sha256:payload123"
    judge_hash = "sha256:judge123"
    chain_id = "CHAIN-123"

    challenge = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)
    packet = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id=session_id,
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge.nonce,
        expires_at=str(int(challenge.expires_at)),
    )
    packet.signature = sign_packet(packet, signing_key)

    # Irreversible action with level 1 should HOLD
    res = await _999_vault.execute(
        action="seal",
        payload={"data": "test"},
        operator_id=actor_id,
        session_id=session_id,
        ack_packet=packet.__dict__,
    )

    assert res["verdict"] == "888_HOLD"
    assert res["ack_irreversible_received"] is False

    # Now allow Level 2 promote
    monkeypatch.setenv("ARIFOS_DEV_ALLOW_MSAP_LEVEL2", "true")

    # Need new challenge because previous one was marked used
    challenge2 = msap.create_challenge(actor_id, session_id, payload_hash, judge_hash, chain_id)
    packet2 = msap.SovereignAckPacket(
        actor_id=actor_id,
        session_id=session_id,
        constitutional_chain_id=chain_id,
        payload_hash=payload_hash,
        judge_state_hash=judge_hash,
        nonce=challenge2.nonce,
        expires_at=str(int(challenge2.expires_at)),
    )
    packet2.signature = sign_packet(packet2, signing_key)

    res2 = await _999_vault.execute(
        action="seal",
        payload={"data": "test"},
        operator_id=actor_id,
        session_id=session_id,
        ack_packet=packet2.__dict__,
    )

    assert res2["verdict"] == "888_HOLD"
    assert res2["ack_irreversible_received"] is False
    assert res2["zkpc_metadata"]["zkpc_level"] == 1
