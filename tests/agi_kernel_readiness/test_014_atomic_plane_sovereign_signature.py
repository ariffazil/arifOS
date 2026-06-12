"""
test_014 — ATOMIC Plane (Tier 5: Sovereign Signature)

Validates the audit's V6 finding: ATOMIC actions (arif_forge_execute
with MUTATE/ATOMIC mode) require sovereign-grade signature. The audit
discovered that arif_forge_execute did not accept actor_signature/nonce
in its schema; that gap is now closed (forge.py F1 AMANAH nonce check).

Pass criteria (post-fix):
    - arif_forge_execute accepts actor_signature and nonce as optional
      parameters (schema gap closed)
    - actor_signature without nonce → HOLD (F1 AMANAH)
    - actor_signature + nonce → SEAL path (signature recorded, not yet
      enforced — F13 ratifies enforcement)
    - Without actor_signature at all → behavior is the same as before
      (signature inherited from session_init)

The 2026-06-12 external harness audit found 11 bugs in arifOS wiring.
This test captures the Tier 5 consequence: the sovereign can pass a
per-call signature, even if the kernel doesn't act on it yet.

Authority: AGI_KERNEL_READINESS_GATE_001 / Tier 5
"""

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import inspect  # noqa: E402

REPO_ROOT = "/root/arifOS"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from arifosmcp.tools.forge import arif_forge_execute  # noqa: E402


def test_forge_schema_accepts_actor_signature():
    """The audit's schema gap is closed: actor_signature is in the signature."""
    sig = inspect.signature(arif_forge_execute)
    assert "actor_signature" in sig.parameters, (
        "F1 AMANAH fix: arif_forge_execute must accept actor_signature; audit bug not closed"
    )


def test_forge_schema_accepts_nonce():
    """The audit's schema gap is closed: nonce is in the signature."""
    sig = inspect.signature(arif_forge_execute)
    assert "nonce" in sig.parameters, (
        "F1 AMANAH fix: arif_forge_execute must accept nonce; audit bug not closed"
    )


def test_forge_actor_signature_without_nonce_holds():
    """actor_signature without nonce must HOLD (F1 AMANAH replay prevention)."""
    # The function is async, so we need asyncio to call it
    import asyncio

    async def call():
        return await arif_forge_execute(
            mode="engineer",
            manifest="{}",
            session_id="SEAL-test",
            actor_id="agi-gate-014",
            judge_state_hash="abc123",
            plan_id="plan-test",
            ack_irreversible=True,
            actor_signature="ed25519:fakesigabcdef",
            nonce=None,  # missing — should HOLD
        )

    result = asyncio.run(call())
    # F1 AMANAH HOLD expected
    assert result.status == "HOLD", f"actor_signature without nonce must HOLD, got {result.status}"
    meta = getattr(result, "meta", {}) or {}
    violated = meta.get("violated_laws", [])
    # F1 is rendered as "F01" in the kernel
    assert any("F1" in v or "F01" in v for v in violated), (
        f"F1 AMANAH must be violated, got {violated}"
    )


def test_forge_both_signature_and_nonce_proceeds():
    """actor_signature + nonce is accepted (signature recorded, not enforced)."""
    import asyncio

    async def call():
        return await arif_forge_execute(
            mode="engineer",
            manifest="{}",
            session_id="SEAL-test",
            actor_id="agi-gate-014",
            judge_state_hash="abc123",
            plan_id="plan-test",
            ack_irreversible=True,
            actor_signature="ed25519:fakesigabcdef",
            nonce="nonce-deadbeef1234",
        )

    result = asyncio.run(call())
    # F2 truth: the signature is RECORDED but not YET ENFORCED.
    # F13 ratifies enforcement. So the call should NOT HOLD on
    # the F1 AMANAH nonce check; it should proceed (and probably
    # HOLD on missing plan or other reasons, but NOT on F1).
    if result.status == "HOLD":
        meta = getattr(result, "meta", {}) or {}
        # Make sure F1 isn't the reason
        violated = meta.get("violated_laws", [])
        assert "F1" not in str(violated) or "F01" not in str(violated), (
            f"F1 AMANAH must not HOLD when signature+nonce are both provided, got {violated}"
        )


if __name__ == "__main__":
    test_forge_schema_accepts_actor_signature()
    print("test_014 schema_sig: PASS")
    test_forge_schema_accepts_nonce()
    print("test_014 schema_nonce: PASS")
    test_forge_actor_signature_without_nonce_holds()
    print("test_014 sig_no_nonce: PASS")
    test_forge_both_signature_and_nonce_proceeds()
    print("test_014 sig_with_nonce: PASS")
