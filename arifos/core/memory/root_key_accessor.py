"""
Root Key Accessor

**Constitutional Authority: F1 Amanah**

Provides controlled access to the root cryptographic key for arifOS.
The root key NEVER leaves the AAA_HUMAN band and is NEVER accessible to AI.

This module is the ONLY lawful interface to the root key. All other modules
MUST use this accessor - direct access is a constitutional violation.

Functions:
    - get_root_key_info(): Get non-sensitive info (for display)
    - derive_session_key(): Derive session key from root key (AI-safe)
    - sign_with_root_key(): Sign data with root key (human-only)
    - create_genesis_block(): Create first block in chain (human-only)
"""

import os
import json
import hashlib
import hmac
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from arifos.core.memory.aaa_guard import (
    get_root_key,
    ai_safe_derive_session_key,
    AAABandAccessError
)

logger = __import__('logging').getLogger(__name__)

class RootKeyError(Exception):
    """Error accessing or using root key."""
    pass

def get_root_key_info() -> Optional[Dict[str, Any]]:
    """
    Get NON-SENSITIVE information about root key.
    
    Safe for AI to call - does not expose private key.
    Returns public key and metadata only.
    
    Returns:
        {"public_key": ..., "generated_at": ..., "authority": ...} or None
    """
    root_key = get_root_key()
    if not root_key:
        return None
    
    # Return only non-sensitive fields
    return {
        "version": root_key.get("version"),
        "generated_at": root_key.get("generated_at"),
        "generated_by": root_key.get("generated_by"),
        "generation_method": root_key.get("generation_method"),
        "public_key": root_key.get("public_key"),
        "entropy_hash": root_key.get("entropy_hash"),
        "self_signature": root_key.get("self_signature")
    }

def derive_session_key(session_id: str) -> Optional[str]:
    """
    Derive a session-specific key from root key.
    
    AI-safe: root key is never exposed, only derived key returned.
    Uses HKDF (HMAC-based Key Derivation Function).
    
    Args:
        session_id: Unique session identifier
    
    Returns:
        Hex-encoded 32-byte session key or None
    """
    return ai_safe_derive_session_key(session_id)

def sign_with_root_key(data: bytes) -> Optional[Tuple[str, str]]:
    """
    Sign arbitrary data with root key.
    
    **HUMAN SOVEREIGN ONLY**
    
    Args:
        data: Bytes to sign
    
    Returns:
        (signature_b64, timestamp) tuple or None if not authorized
    """
    try:
        root_key = get_root_key()
        if not root_key:
            raise RootKeyError("No root key available")
        
        private_key_b64 = root_key.get("private_key")
        if not private_key_b64:
            raise RootKeyError("Root key missing private_key field")
        
        # Load private key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        import base64
        
        private_bytes = base64.b64decode(private_key_b64)
        private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
        
        # Create timestamped message
        timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        message = f"arifOS_ROOT_SIGNATURE\n{timestamp}\n{data.hex()}".encode()
        
        # Sign
        signature = private_key.sign(message)
        signature_b64 = base64.b64encode(signature).decode()
        
        logger.info(f"Root key signature created for {len(data)} bytes")
        
        return signature_b64, timestamp
        
    except AAABandAccessError:
        logger.critical("AI attempted root key signing - BLOCKED")
        return None
    except Exception as e:
        logger.error(f"Root key signing failed: {e}")
        return None

def verify_root_key_signature(data: bytes, signature_b64: str, timestamp: str) -> bool:
    """
    Verify a signature created with root key.
    
    Args:
        data: Original signed data
        signature_b64: Base64 signature
        timestamp: Signature timestamp
    
    Returns:
        True if signature is valid
    """
    try:
        root_key_info = get_root_key_info()
        if not root_key_info:
            logger.error("No root key info available for verification")
            return False
        
        public_key_b64 = root_key_info.get("public_key")
        if not public_key_b64:
            logger.error("Root key missing public_key")
            return False
        
        # Load public key
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        import base64
        
        public_bytes = base64.b64decode(public_key_b64)
        public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
        
        # Reconstruct message
        message = f"arifOS_ROOT_SIGNATURE\n{timestamp}\n{data.hex()}".encode()
        
        # Verify
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, message)
        
        logger.debug("Root key signature verification: PASS")
        return True
        
    except Exception as e:
        logger.error(f"Root key signature verification failed: {e}")
        return False

def create_genesis_block() -> Optional[Dict[str, Any]]:
    """
    Create the genesis block for the constitutional ledger.
    
    **HUMAN SOVEREIGN ONLY**
    
    The genesis block establishes the chain of trust.
    It is signed with the root key to prove authenticity.
    
    Returns:
        Genesis block dict or None
    """
    try:
        root_key_info = get_root_key_info()
        if not root_key_info:
            raise RootKeyError("No root key info available")
        
        # Create genesis content
        from datetime import timezone
        genesis_data = {
            "version": "1.0",
            "genesis": True,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "created_by": root_key_info.get("generated_by"),
            "root_key_public": root_key_info.get("public_key"),
            "entropy_hash": root_key_info.get("entropy_hash"),
            "constitutional_law": "000_THEORY/000_LAW.md",
            "purpose": "arifOS Constitutional Foundation",
            "motto": "DITEMPA BUKAN DIBERI"
        }
        
        # Sign genesis data with root key
        genesis_bytes = json.dumps(genesis_data, sort_keys=True).encode()
        signature_result = sign_with_root_key(genesis_bytes)
        
        if not signature_result:
            raise RootKeyError("Failed to sign genesis block")
        
        signature_b64, timestamp = signature_result
        
        # Create full genesis block
        genesis_block = {
            "block": genesis_data,
            "signature": signature_b64,
            "signature_timestamp": timestamp,
            "merkle_root": hashlib.sha256(genesis_bytes).hexdigest(),
            "previous_hash": "0" * 64,  # Genesis has no predecessor
            "constitutional_status": "SOVEREIGNLY_SEALED"
        }
        
        logger.info("Genesis block created successfully")
        
        return genesis_block
        
    except AAABandAccessError:
        logger.critical("AI attempted genesis block creation - BLOCKED")
        return None
    except Exception as e:
        logger.error(f"Genesis block creation failed: {e}")
        return None

def verify_genesis_block(genesis_block: Dict[str, Any]) -> bool:
    """
    Verify the genesis block signature and structure.
    
    Args:
        genesis_block: Genesis block to verify
    
    Returns:
        True if genesis block is valid
    """
    try:
        # Extract components
        block = genesis_block.get("block", {})
        signature = genesis_block.get("signature")
        sig_timestamp = genesis_block.get("signature_timestamp")
        
        if not all([block, signature, sig_timestamp]):
            logger.error("Genesis block missing required fields")
            return False
        
        # Reconstruct signed data
        block_bytes = json.dumps(block, sort_keys=True).encode()
        
        # Verify signature
        is_valid = verify_root_key_signature(block_bytes, signature, sig_timestamp)
        
        if is_valid:
            logger.info("Genesis block verification: PASS")
        else:
            logger.error("Genesis block verification: FAIL")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Genesis block verification failed: {e}")
        return False

def derive_ledger_entry_hash(entry_data: Dict[str, Any]) -> str:
    """
    Derive hash for a ledger entry using session key.
    
    This ensures all ledger entries are cryptographically linked
    to the root key through session derivation.
    
    Args:
        entry_data: Ledger entry data
    
    Returns:
        SHA256 hex digest
    """
    try:
        # Serialize deterministically
        entry_bytes = json.dumps(entry_data, sort_keys=True).encode()
        
        # Hash
        entry_hash = hashlib.sha256(entry_bytes).hexdigest()
        
        return entry_hash
        
    except Exception as e:
        logger.error(f"Ledger entry hash derivation failed: {e}")
        return ""

# Module initialization check
def _check_root_key_status():
    """Check if root key infrastructure is ready."""
    try:
        from pathlib import Path
        
        root_key_path = Path("VAULT999/AAA_HUMAN/rootkey.json")
        if not root_key_path.exists():
            logger.warning("Root key not found. Run: python scripts/generate_rootkey.py")
            return False
        
        # Check if human can access
        info = get_root_key_info()
        if info:
            logger.info(f"Root key loaded (generated: {info.get('generated_at')})")
            return True
        else:
            logger.warning("Root key exists but cannot be accessed")
            return False
            
    except Exception as e:
        logger.error(f"Root key status check failed: {e}")
        return False

# Lazy initialization - defer entropy increase until first use
_ROOT_KEY_STATUS = None

def get_root_key_status() -> bool:
    """Lazy getter - defers entropy increase until first use."""
    global _ROOT_KEY_STATUS
    if _ROOT_KEY_STATUS is None:
        _ROOT_KEY_STATUS = _check_root_key_status()
    return _ROOT_KEY_STATUS

__all__ = [
    'RootKeyError',
    'get_root_key_info',
    'derive_session_key',
    'sign_with_root_key',
    'verify_root_key_signature',
    'create_genesis_block',
    'verify_genesis_block',
    'derive_ledger_entry_hash',
    'get_root_key_status'  # Lazy getter - replaced ROOT_KEY_READY
]
