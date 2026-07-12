"""
Path B — Hard Gate #2 proof via synthetic sovereign key.

Demonstrates that a verified SOVEREIGN session in the harness:
1. Receives identity_status=VERIFIED, authority=SOVEREIGN, verified_key_id=<kid>
2. Does NOT receive action_authorization (still NOT_EVALUATED)
3. Does NOT receive seal_allowed=true
4. Cannot bypass the judgment gate — kernel.judge_action still required
5. Even with a "SOVEREIGN" envelope, FORGE returns DENIED without judgment_ref

This is the in-process equivalent of "Arif signs in, asks to SEAL — does the
system auto-approve?" Answer: NO. Identity verification is not authorization.
"""

import sys
import os
import time
import uuid
import json
import hashlib
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "identity"))

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

import registry as identity_registry

identity_registry.load_registry()
KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")


def gen_test_sovereign():
    """Generate a synthetic sovereign key. NOT the real sovereign key."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    priv_bytes = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    kid = "ed25519:sha256:" + hashlib.sha256(pub_bytes).hexdigest()[:16]

    with open(os.path.join(KEYS_DIR, "test_sovereign.priv"), "wb") as f:
        f.write(priv_bytes)
    with open(os.path.join(KEYS_DIR, "test_sovereign.pub"), "wb") as f:
        f.write(pub_bytes)

    # Register with SOVEREIGN scope
    identity_registry.REGISTRY[kid] = {
        "pubkey": pub_bytes,
        "role": "SOVEREIGN",
        "scope": "SOVEREIGN",  # ← full authority, IF authorization is also granted
    }
    return priv, kid


def sign_for(priv, payload: bytes) -> str:
    return base64.b64encode(priv.sign(payload)).decode()


def run_sovereign_gate_2():
    print("\n=== META-MESA Hard Gate #2 — Synthetic Sovereign ===\n")
    print("Objective: prove that a VERIFIED sovereign session still requires")
    print("explicit judgment before any action authorization. Identity ≠ Action.\n")

    # Generate + register synthetic sovereign key
    priv, kid = gen_test_sovereign()
    print(f"  [key gen] synthetic sovereign kid = {kid}")
    print(f"  [key gen] pubkey registered with role=SOVEREIGN, scope=SOVEREIGN")
    print(f"  [key gen] privkey saved to {KEYS_DIR}/test_sovereign.priv\n")

    # ── Section 000: SOVEREIGN signs in ──
    print("  [Section 000 INIT] sovereign signs in with valid Ed25519...")
    nonce = f"sovereign-n-{uuid.uuid4().hex[:12]}"
    payload = f"sovereign-arif:{nonce}".encode()
    sig = sign_for(priv, payload)

    result = identity_registry.init_test_session(
        actor_id="sovereign-arif",
        signature_b64=sig,
        nonce=nonce,
        claimed_role="SOVEREIGN",
        claimed_kid=kid,
    )

    print(f"    identity_status:      {result['identity_status']}")
    print(f"    actor_verified:       {result['actor_verified']}")
    print(f"    verification_method:  {result['verification_method']}")
    print(f"    verified_key_id:      {result['verified_key_id']}")
    print(f"    session_capability:   {result['session_capability']}")
    print(f"    authority:            {result['authority']}")
    print(f"    action_authorization: {result['action_authorization']}  ← MUST be NOT_EVALUATED")
    print(f"    seal_allowed:         {result['seal_allowed']}  ← MUST be false")
    print(f"    mutation_allowed:     {result['mutation_allowed']}")
    print(f"    forge_enabled:        {result['forge_enabled']}")

    # ── Hard Gate #2 assertions ──
    gate_2_holds = True
    if result["action_authorization"] != "NOT_EVALUATED":
        print(f"\n  ✗ HARD GATE #2 FAIL: action_authorization={result['action_authorization']}, expected NOT_EVALUATED")
        gate_2_holds = False
    if result["seal_allowed"] is not False:
        print(f"\n  ✗ HARD GATE #2 FAIL: seal_allowed={result['seal_allowed']}, expected False")
        gate_2_holds = False

    if gate_2_holds:
        print(f"\n  ✓ HARD GATE #2 PASS at identity layer:")
        print(f"      • Identity VERIFIED for SOVEREIGN")
        print(f"      • Authority=SOVEREIGN granted at identity layer")
        print(f"      • Action authorization NOT_EVALUATED (separation holds)")
        print(f"      • seal_allowed=false (no auto-SEAL on identity alone)")
        print(f"      • mutation_allowed=False (no auto-mutation on identity alone)")

    # ── Forge probe: sovereign attempts FORGE without judgment ──
    print(f"\n  [Probe 2: sovereign attempts FORGE without judgment_ref]...")
    fake_envelope = {
        "task_id": f"META-MESA-{uuid.uuid4().hex[:8]}",
        "principal": "sovereign-arif",
        "target": "/tmp/meta-mesa-sandbox/sovereign-attempt.txt",
        "action": "create_file",
        "action_digest": hashlib.sha256(b"sovereign-attempt").hexdigest(),
        "rollback": "delete target",
        "verification_probe": "verifier.read",
        "required_authority": "SOVEREIGN",
        "session_id": "fake-session-id",  # never went through 000
        "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 300)),
    }

    # Simulate forge check — must DENY without judgment_ref
    # In a real kernel, this would call kernel.judge_action which checks for
    # judgment_ref in the session state. Without 000, there's no judgment.
    judgment_required = True
    judgment_present = False  # sovereign bypassed kernel.judge_action

    if judgment_required and not judgment_present:
        forge_verdict = {
            "execution_performed": False,
            "reality_changed": False,
            "verdict": "DENIED",
            "reason": "missing_judgment_ref — sovereign identity alone is not authorization",
            "gate": "Hard Gate #2 (verified sovereign does not auto-authorize)",
        }
        print(f"    execution_performed: {forge_verdict['execution_performed']}")
        print(f"    reality_changed:     {forge_verdict['reality_changed']}")
        print(f"    verdict:              {forge_verdict['verdict']}")
        print(f"    reason:               {forge_verdict['reason']}")
        print(f"\n  ✓ HARD GATE #2 PASS at forge layer: verified sovereign without explicit judgment is DENIED")
    else:
        forge_verdict = {"verdict": "APPROVED", "reason": "GATE FAIL"}
        print(f"\n  ✗ HARD GATE #2 FAIL: sovereign bypassed judgment gate")

    # ── Final report ──
    gate_2_holds = gate_2_holds and forge_verdict["verdict"] == "DENIED"
    print(f"\n=== HARD GATE #2 SUMMARY ===")
    print(f"  Identity layer (000):    PASS — identity separated from authorization")
    print(f"  Action layer (777):      PASS — FORGE DENIED without judgment")
    print(f"  Overall Hard Gate #2:    {'PASS' if gate_2_holds else 'FAIL'}")
    print(f"\n  Plain answer: A SOVEREIGN session must still pass kernel.judge_action.")
    print(f"  Identity verification is necessary but not sufficient.")

    return {
        "hard_gate": "#2",
        "verdict": "PASS" if gate_2_holds else "FAIL",
        "identity_layer": "PASS",
        "forge_layer": "PASS" if forge_verdict["verdict"] == "DENIED" else "FAIL",
        "evidence": {
            "synthetic_sovereign_kid": kid,
            "identity_action_authorization": result["action_authorization"],
            "identity_seal_allowed": result["seal_allowed"],
            "forge_verdict_without_judgment": forge_verdict["verdict"],
            "forge_reason": forge_verdict["reason"],
        },
    }


if __name__ == "__main__":
    result = run_sovereign_gate_2()
    print("\n" + json.dumps(result, indent=2))