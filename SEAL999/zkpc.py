"""
ZKPC (Zero-Knowledge Proof of Constitutionality)

Cryptographic proofs for VAULT-999 entries.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .state import VaultEntry


@dataclass
class ZKPCProof:
    """ZKPC proof structure."""
    commitment_hash: str
    merkle_root: str
    witness_signature: str
    floors_validated: Dict[str, float]
    stage: int
    session_id: str


class ZKPCGenerator:
    """Generate ZKPC proofs for constitutional entries."""
    
    def __init__(self, sovereign_key: Optional[str] = None):
        """Initialize ZKPC generator with sovereign key."""
        self.sovereign_key = sovereign_key or "888_JUDGE"
    
    def generate_proof(self, entry: VaultEntry, hash_chain) -> Dict[str, Any]:
        """
        Generate ZKPC proof for a vault entry.
        
        Args:
            entry: The vault entry
            hash_chain: Current hash chain state
            
        Returns:
            ZKPC proof dictionary
        """
        # Compute commitment hash
        commitment_data = {
            "session_id": entry.session_id,
            "stage": entry.stage,
            "merkle_root": entry.merkle_root,
            "timestamp": entry.timestamp.isoformat(),
            "hash_chain_head": hash_chain.get_head()
        }
        
        sorted_data = json.dumps(commitment_data, sort_keys=True, separators=(",", ":"))
        commitment_hash = hashlib.sha256(sorted_data.encode()).hexdigest()
        
        # Generate witness signature (simplified)
        witness_signature = self._generate_signature(entry, commitment_hash)
        
        return {
            "commitment_hash": commitment_hash,
            "merkle_root": entry.merkle_root,
            "witness_signature": witness_signature,
            "floors_validated": entry.floor_scores,
            "stage": entry.stage,
            "session_id": entry.session_id,
            "type": "zkpc_constitutional_proof_v1"
        }
    
    def verify_proof(self, entry: VaultEntry, proof: Dict[str, Any]) -> bool:
        """
        Verify ZKPC proof for a vault entry.
        
        Args:
            entry: The vault entry
            proof: The ZKPC proof to verify
            
        Returns:
            True if proof is valid
        """
        try:
            # Verify proof structure
            required_fields = ["commitment_hash", "merkle_root", "witness_signature", "floors_validated"]
            if not all(field in proof for field in required_fields):
                return False
            
            # Verify merkle_root matches
            if proof["merkle_root"] != entry.merkle_root:
                return False
            
            # Verify floors match
            if proof["floors_validated"] != entry.floor_scores:
                return False
            
            # Verify witness signature
            expected_signature = self._generate_signature(entry, proof["commitment_hash"])
            if proof["witness_signature"] != expected_signature:
                return False
            
            return True
        except Exception:
            return False
    
    def _generate_signature(self, entry: VaultEntry, commitment_hash: str) -> str:
        """
        Generate sovereign witness signature (simplified).
        
        In production, this would use Ed25519 with actual sovereign key.
        """
        # Combine commitment hash with metadata
        signature_data = {
            "commitment_hash": commitment_hash,
            "session_id": entry.session_id,
            "stage": entry.stage,
            "verdict": entry.verdict,
            "authority": self.sovereign_key
        }
        
        sorted_data = json.dumps(signature_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(sorted_data.encode()).hexdigest()[:16]
    
    def compute_commitment(self, session_id: str, stage: int, 
                          merkle_root: str, hash_chain_head: str) -> str:
        """
        Compute ZKPC commitment for a stage transition.
        
        Args:
            session_id: Session identifier
            stage: Current stage (0-999)
            merkle_root: Merkle root for this stage
            hash_chain_head: Current hash chain head
            
        Returns:
            Commitment hash
        """
        data = {
            "session_id": session_id,
            "stage": stage,
            "merkle_root": merkle_root,
            "hash_chain_head": hash_chain_head
        }
        
        sorted_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(sorted_data.encode()).hexdigest()
