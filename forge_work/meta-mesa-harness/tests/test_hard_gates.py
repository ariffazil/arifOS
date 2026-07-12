"""
META-MESA hard-gate tests — run against mm-identity.

Asserts each Section 9 hard gate is enforced:
  G1: unsigned actor_id gains no authority
  G5: expired/replayed nonce rejected
  G6: forged signature fails closed
  G9: missing signature → fail closed
"""
import sys, os, time, base64
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "identity"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

import registry

registry.load_registry()

# Helper: sign with the agent key
def sign_with_agent(actor_id, nonce):
    priv_path = os.path.join(os.path.dirname(__file__), "..", "keys", "agent.priv")
    with open(priv_path, "rb") as f:
        priv = Ed25519PrivateKey.from_private_bytes(f.read())
    payload = f"{actor_id}:{nonce}".encode()
    sig = priv.sign(payload)
    return base64.b64encode(sig).decode()


def sign_with_attacker(actor_id, nonce):
    """Sign with the unregistered attacker key."""
    priv_path = os.path.join(os.path.dirname(__file__), "..", "keys", "attacker.priv")
    with open(priv_path, "rb") as f:
        priv = Ed25519PrivateKey.from_private_bytes(f.read())
    payload = f"{actor_id}:{nonce}".encode()
    sig = priv.sign(payload)
    return base64.b64encode(sig).decode()


# ── G1: unsigned actor_id gains no authority ──
def test_g1_claimed_arif_no_signature():
    r = registry.init_test_session(
        actor_id="arif", signature_b64="", nonce="n1",
        claimed_role="SOVEREIGN",
    )
    assert r["actor_verified"] is False
    assert r["mutation_allowed"] is False
    assert r["forge_enabled"] is False
    assert r["authority"] == "OBSERVE_ONLY"
    print("✓ G1: actor_id='arif' no signature → UNVERIFIED, no mutation")


def test_g1_arbitrary_nonanonymous():
    r = registry.init_test_session(
        actor_id="attacker", signature_b64="", nonce="n2",
        claimed_role="OPERATOR",
    )
    assert r["actor_verified"] is False
    print("✓ G1: arbitrary nonanonymous name → UNVERIFIED")


# ── G5: expired/replayed nonce ──
def test_g5_replayed_nonce():
    nonce = f"replay-test-{int(time.time()*1000)}"
    sig = sign_with_agent("agent-001", nonce)
    r1 = registry.init_test_session(
        actor_id="agent-001", signature_b64=sig, nonce=nonce,
        claimed_role="OPERATOR", claimed_kid=list(registry.REGISTRY.keys())[0],
    )
    assert r1["actor_verified"] is True, f"first call should succeed: {r1}"
    # Replay same nonce
    r2 = registry.init_test_session(
        actor_id="agent-001", signature_b64=sig, nonce=nonce,
        claimed_role="OPERATOR", claimed_kid=list(registry.REGISTRY.keys())[0],
    )
    assert r2["actor_verified"] is False, f"replay must be rejected: {r2}"
    assert r2["reason"] == "expired_or_replayed_nonce"
    print("✓ G5: replayed nonce → UNVERIFIED")


# ── G6: forged signature with unregistered key ──
def test_g6_unregistered_key_fails():
    nonce = f"unreg-test-{int(time.time()*1000)}"
    sig = sign_with_attacker("arif", nonce)
    r = registry.init_test_session(
        actor_id="arif", signature_b64=sig, nonce=nonce,
        claimed_role="SOVEREIGN", claimed_kid="ed25519:sha256:d66ee0e617274eac",
    )
    assert r["actor_verified"] is False
    print(f"✓ G6: unregistered attacker key → UNVERIFIED ({r.get('reason')})")


# ── G9: missing signature ──
def test_g9_missing_signature():
    r = registry.init_test_session(
        actor_id="agent-001", signature_b64=None, nonce="n9",
        claimed_role="OPERATOR",
    )
    assert r["actor_verified"] is False
    assert r["reason"] == "missing_signature_or_nonce"
    print("✓ G9: missing signature → UNVERIFIED")


# ── Positive: registered agent key + valid nonce → VERIFIED ──
def test_positive_registered_agent():
    nonce = f"good-{int(time.time()*1000)}"
    sig = sign_with_agent("agent-001", nonce)
    r = registry.init_test_session(
        actor_id="agent-001", signature_b64=sig, nonce=nonce,
        claimed_role="OPERATOR", claimed_kid=list(registry.REGISTRY.keys())[0],
    )
    assert r["actor_verified"] is True
    assert r["forge_enabled"] is True
    assert r["mutation_allowed"] is True
    assert r["authority"] == "TEST_SANDBOX_WRITE"
    print(f"✓ POSITIVE: registered agent + valid sig → VERIFIED, kid={r['verified_key_id']}")


if __name__ == "__main__":
    print(f"\n=== META-MESA Hard Gate Tests (registry has {len(registry.REGISTRY)} keys) ===\n")
    test_g1_claimed_arif_no_signature()
    test_g1_arbitrary_nonanonymous()
    test_g5_replayed_nonce()
    test_g6_unregistered_key_fails()
    test_g9_missing_signature()
    test_positive_registered_agent()
    print("\n=== ALL HARD GATE TESTS PASSED ===")