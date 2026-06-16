from pathlib import Path
import pytest
from arifosmcp.runtime.sovereign_signer import load_private_key, sign, get_constitution_hash
from arifosmcp.runtime.sovereign_verify import verify_sovereign_signature

def test_pem_signing_and_verification():
    """Verify that we can successfully load the sovereign key (PEM, PKCS#8 or raw), sign a message, and verify it."""
    try:
        raw_key = load_private_key()
        assert len(raw_key) == 32
        
        actor_id = "ariffazil"
        constitution_hash = get_constitution_hash()
        nonce = "test-pem-nonce-999"
        
        sig = sign(actor_id, constitution_hash, nonce)
        assert sig is not None
        
        ok, reason = verify_sovereign_signature(actor_id, constitution_hash, nonce, sig)
        assert ok is True
        assert reason == "ed25519_signature_verified"
    except FileNotFoundError:
        # Fallback for environments where the actual private key is missing (e.g. strict sandbox or runner)
        pytest.skip("Sovereign private key file not available in this environment")
