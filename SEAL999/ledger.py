"""
LEDGER IMPLEMENTATION

Hash-chain and Merkle tree for VAULT-999 integrity.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .state import VaultEntry, SessionLedger, VaultConfig


class HashChain:
    """Simple hash chain for ledger integrity."""
    
    def __init__(self):
        """Initialize empty hash chain."""
        self.hashes: List[str] = []
        self.current_hash: Optional[str] = None
    
    def append(self, data_hash: str) -> str:
        """
        Append to hash chain.
        
        Args:
            data_hash: Hash of new entry
            
        Returns:
            Chain hash after appending
        """
        if not self.hashes:
            # Genesis block
            self.current_hash = data_hash
        else:
            # Chain: hash(prev_hash + data_hash)
            import hashlib
            combined = self.current_hash + data_hash
            self.current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        self.hashes.append(self.current_hash)
        return self.current_hash
    
    def verify(self, data_hash: str, expected_chain_hash: str) -> bool:
        """
        Verify data_hash produces expected_chain_hash.
        
        Args:
            data_hash: Hash of data to verify
            expected_chain_hash: Expected chain hash
            
        Returns:
            True if verification passes
        """
        if not self.hashes:
            return False
        
        import hashlib
        if len(self.hashes) == 1:
            # Only genesis block
            return data_hash == expected_chain_hash
        else:
            # Verify chain computation
            combined = self.hashes[-2] + data_hash
            computed = hashlib.sha256(combined.encode()).hexdigest()
            return computed == expected_chain_hash
    
    def get_head(self) -> Optional[str]:
        """Get current chain head hash."""
        return self.current_hash


class Ledger:
    """Main VAULT-999 ledger for storing and retrieving entries."""
    
    def __init__(self, config: VaultConfig):
        """Initialize ledger with configuration."""
        self.config = config
        self.hash_chain = HashChain()
        
        # Ensure ledger file exists
        os.makedirs(os.path.dirname(self.config.get_ledger_path()), exist_ok=True)
        if not os.path.exists(self.config.get_ledger_path()):
            with open(self.config.get_ledger_path(), "w"):
                pass  # Create empty file
    
    def append(self, entry: VaultEntry) -> bool:
        """
        Append entry to main ledger.
        
        Args:
            entry: Entry to append
            
        Returns:
            True if successful
        """
        try:
            # Add to hash chain
            entry_hash = entry.compute_hash()
            chain_hash = self.hash_chain.append(entry_hash)
            
            # Create ledger record
            record = {
                "entry_id": entry.entry_id,
                "session_id": entry.session_id,
                "stage": entry.stage,
                "timestamp": entry.timestamp.isoformat(),
                "verdict": entry.verdict,
                "merkle_root": entry.merkle_root,
                "chain_hash": chain_hash,
                "tier": entry.cooling_tier,
                "data_hash": entry_hash,
            }
            
            # Append to ledger file
            with open(self.config.get_ledger_path(), "a") as f:
                f.write(json.dumps(record) + "\n")
            
            return True
        except Exception as e:
            print(f"Error appending to ledger: {e}")
            return False
    
    def get_entry(self, entry_id: str) -> Optional[VaultEntry]:
        """
        Retrieve entry by ID from ledger.
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            VaultEntry if found, None otherwise
        """
        if not os.path.exists(self.config.get_ledger_path()):
            return None
        
        with open(self.config.get_ledger_path(), "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get("entry_id") == entry_id:
                        # Reconstruct entry from record
                        return self._reconstruct_entry(record)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def get_session(self, session_id: str) -> Optional[SessionLedger]:
        """
        Retrieve all entries for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionLedger with all entries, or None
        """
        if not os.path.exists(self.config.get_ledger_path()):
            return None
        
        entries = []
        
        with open(self.config.get_ledger_path(), "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    if record.get("session_id") == session_id:
                        entry = self._reconstruct_entry(record)
                        if entry:
                            entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        if not entries:
            return None
        
        # Sort by stage
        entries.sort(key=lambda e: e.stage)
        
        # Create session ledger
        ledger = SessionLedger(session_id=session_id, entries=entries)
        ledger.merkle_root = ledger.compute_merkle_root()
        
        # Get final verdict (usually from stage 888)
        final_entry = ledger.get_entry(888)
        if final_entry:
            ledger.final_verdict = final_entry.verdict
        
        return ledger
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get ledger statistics (counts, averages, etc.).
        
        Returns:
            Statistics dictionary
        """
        if not os.path.exists(self.config.get_ledger_path()):
            return {"total_entries": 0, "verdict_counts": {}}
        
        total_entries = 0
        verdict_counts = {}
        session_ids = set()
        
        with open(self.config.get_ledger_path(), "r") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    total_entries += 1
                    
                    verdict = record.get("verdict", "UNKNOWN")
                    verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
                    
                    session_id = record.get("session_id")
                    if session_id:
                        session_ids.add(session_id)
                except json.JSONDecodeError:
                    continue
        
        return {
            "total_entries": total_entries,
            "unique_sessions": len(session_ids),
            "verdict_counts": verdict_counts,
            "ledger_path": self.config.get_ledger_path(),
        }
    
    def _reconstruct_entry(self, record: Dict[str, Any]) -> Optional[VaultEntry]:
        """Reconstruct VaultEntry from ledger record."""
        try:
            return VaultEntry(
                entry_id=record["entry_id"],
                session_id=record["session_id"],
                stage=record["stage"],
                timestamp=datetime.fromisoformat(record["timestamp"]),
                verdict=record["verdict"],
                merkle_root=record["merkle_root"],
                floor_scores=record.get("floor_scores", {}),
                cooling_tier=record.get("tier", 0),
            )
        except (KeyError, ValueError):
            return None


class MerkleTree:
    """
    Merkle tree for VAULT-999 cryptographic integrity.
    
    Production would use pymerkle, but this is micro version.
    """
    
    def __init__(self):
        """Initialize empty Merkle tree."""
        self.leaves: List[str] = []
        self.layers: List[List[str]] = []
    
    def add_leaf(self, data: str) -> None:
        """Add leaf to Merkle tree."""
        self.leaves.append(hashlib.sha256(data.encode()).hexdigest())
        self._rebuild()
    
    def _rebuild(self) -> None:
        """Rebuild Merkle tree from leaves."""
        if not self.leaves:
            self.layers = []
            return
        
        self.layers = [self.leaves]
        current = self.leaves
        
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                if i + 1 < len(current):
                    combined = current[i] + current[i + 1]
                else:
                    combined = current[i] + current[i]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            self.layers.append(next_level)
            current = next_level
    
    def get_root(self) -> Optional[str]:
        """Get Merkle root."""
        if not self.layers:
            return None
        return self.layers[-1][0] if self.layers[-1] else None
    
    def get_proof(self, leaf_index: int) -> List[str]:
        """Get Merkle proof for leaf at index."""
        proof = []
        
        for layer in self.layers[:-1]:
            if leaf_index % 2 == 0:
                # Leaf is left child
                if leaf_index + 1 < len(layer):
                    proof.append(f"R:{layer[leaf_index + 1]}")
            else:
                # Leaf is right child
                proof.append(f"L:{layer[leaf_index - 1]}")
            leaf_index //= 2
        
        return proof
    
    def verify(self, leaf_data: str, proof: List[str], root: str) -> bool:
        """Verify leaf data against root using proof."""
        current = hashlib.sha256(leaf_data.encode()).hexdigest()
        
        for step in proof:
            side, hash_val = step.split(":")
            if side == "L":
                combined = hash_val + current
            else:  # side == "R"
                combined = current + hash_val
            current = hashlib.sha256(combined.encode()).hexdigest()
        
        return current == root
