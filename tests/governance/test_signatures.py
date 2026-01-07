"""
Tests for v45 Sovereign Signatures
Verify signing and verification logic (with or without PyNaCl).
"""
import pytest
from arifos_core.apex.governance.sovereign_signature import SovereignSigner, SignatureVerifier, HAS_NACL

def test_sign_and_verify():
    """Verify a valid signature passes verification."""
    signer = SovereignSigner()
    pub_key = signer.get_public_key()
    
    msg_hash = "hash_of_verdict_123"
    sig = signer.sign_verdict(msg_hash)
    
    assert SignatureVerifier.verify(pub_key, msg_hash, sig) is True

def test_verify_failure_bad_sig():
    """Verify an invalid signature fails verification."""
    # Only meaningful run if we implement actual crypto check or strict mock
    signer = SovereignSigner()
    pub_key = signer.get_public_key()
    msg_hash = "hash_of_verdict_123"
    
    # Create valid sig then break it
    valid_sig = signer.sign_verdict(msg_hash)
    
    if HAS_NACL:
        # Flip bits in hex string essentially guarantees invalidity for Ed25519
        invalid_sig = valid_sig.replace('a', 'b').replace('1', '2')
        if invalid_sig == valid_sig: # edge case if no chars to replace
             invalid_sig = "00" * 64 
    else:
        # For mock, we just need something that doesn't start with mock_sig or has wrong hash
        invalid_sig = "mock_sig:BAD_HASH_VALUE"
        
    assert SignatureVerifier.verify(pub_key, msg_hash, invalid_sig) is False

def test_verify_failure_bad_msg():
    """Verify signature fails for wrong message."""
    signer = SovereignSigner()
    pub_key = signer.get_public_key()
    
    msg1 = "hash_1"
    msg2 = "hash_2"
    
    sig1 = signer.sign_verdict(msg1)
    
    # Try verifying sig1 against msg2
    assert SignatureVerifier.verify(pub_key, msg2, sig1) is False
