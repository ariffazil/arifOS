import asyncio
import pytest
from arifosmcp.tools.vault import arif_vault_seal
from arifosmcp.runtime.sovereign_signer import sign, get_constitution_hash


@pytest.mark.asyncio
async def test_vault_seal_sig_flow():
    """Verify that arif_vault_seal correctly verifies the sovereign signature, accepting valid ones and rejecting invalid ones."""
    from arifosmcp.runtime.sovereign_signer import load_private_key

    try:
        load_private_key()
    except FileNotFoundError:
        pytest.skip("Private key not available")

    actor_id = "ariffazil"
    constitution_hash = get_constitution_hash()

    # 1. POSITIVE PATH: Call with a valid signature
    nonce_valid = f"test-vault-seal-nonce-ok-{int(asyncio.get_event_loop().time())}"
    sig_valid = sign(actor_id, constitution_hash, nonce_valid)
    assert sig_valid is not None

    res_valid = await arif_vault_seal(
        mode="seal",
        payload="Test sovereign ratification of F11 flow (valid signature)",
        session_id="test-session-sig-flow-ok",
        ack_irreversible=True,
        actor_id=actor_id,
        actor_signature=sig_valid,
        nonce=nonce_valid,
    )

    assert res_valid.status == "HOLD"
    reasons_valid = " ".join(res_valid.reasons or [])
    # Valid signature should NOT fail the L11 Ed25519 signature check
    assert "Ed25519 signature verification failed" not in reasons_valid
    assert "signature verification failed" not in reasons_valid.lower()

    # 2. NEGATIVE PATH: Call with an invalid signature
    nonce_invalid = f"test-vault-seal-nonce-bad-{int(asyncio.get_event_loop().time())}"
    sig_invalid = "AAAA" + sig_valid[4:]  # corrupt the signature

    res_invalid = await arif_vault_seal(
        mode="seal",
        payload="Test sovereign ratification of F11 flow (invalid signature)",
        session_id="test-session-sig-flow-bad",
        ack_irreversible=True,
        actor_id=actor_id,
        actor_signature=sig_invalid,
        nonce=nonce_invalid,
    )

    assert res_invalid.status == "HOLD"
    reasons_invalid = " ".join(res_invalid.reasons or [])
    # Invalid signature MUST fail the L11 Ed25519 signature check
    assert (
        "Ed25519 signature verification failed" in reasons_invalid
        or "verification failed" in reasons_invalid.lower()
    )
