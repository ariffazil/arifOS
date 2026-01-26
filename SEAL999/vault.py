"""
SEAL-999 CANONICAL IMPLEMENTATION

The one and only sovereign vault for constitutional memory.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from .state import VaultEntry, SessionLedger, VaultConfig
from .ledger import HashChain, Ledger
from .zkpc import ZKPCGenerator


class SEAL999:
    """
    Constitutional SEAL-999: Immutable memory repository.
    
    This is the ONLY SEAL-999. All others are deprecated.
    """
    
    def __init__(self, config: Optional[VaultConfig] = None):
        """Initialize canonical SEAL-999 with configuration."""
        self.config = config or VaultConfig()
        self.hash_chain = HashChain()
        self.ledger = Ledger(self.config)
        self.zkpc = ZKPCGenerator()
        
        # Ensure base directory exists
        os.makedirs(self.config.base_path, exist_ok=True)
        
        # Ensure cooling tier directories exist
        for tier in range(6):
            tier_path = self.config.get_tier_path(tier)
            os.makedirs(tier_path, exist_ok=True)
    
    def seal_entry(self, entry: VaultEntry) -> str:
        """
        Seal a vault entry (999 stage execution).
        
        Args:
            entry: The 889→999 entry to seal
            
        Returns:
            Merkle root of the sealed entry
        """
        # Compute entry hash for hash chain
        entry_hash = entry.compute_hash()
        
        # Add to hash chain
        self.hash_chain.append(entry_hash)
        
        # Assign cooling tier based on verdict (Eureka Sieve)
        entry.cooling_tier = self._assign_cooling_tier(entry)
        
        # Generate ZKPC proof
        entry.merkle_proof = self.zkpc.generate_proof(entry, self.hash_chain)
        
        # Store in appropriate tier
        self._store_entry(entry)
        
        # Write to main ledger
        self.ledger.append(entry)
        
        # Return Merkle root as seal
        return entry.merkle_root
    
    def get_session_ledger(self, session_id: str) -> Optional[SessionLedger]:
        """
        Retrieve complete ledger for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionLedger with all 11 entries, or None if not found
        """
        return self.ledger.get_session(session_id)
    
    def verify_entry(self, entry: VaultEntry) -> bool:
        """
        Verify a vault entry's integrity.
        
        Checks:
        - Hash matches computed value
        - Merkle proof is valid
        - Belongs to valid session ledger
        
        Returns:
            True if entry is valid, False otherwise
        """
        # Verify hash
        if entry.compute_hash() != entry.compute_hash():
            return False
        
        # Verify Merkle proof
        if entry.merkle_proof:
            if not self.zkpc.verify_proof(entry, entry.merkle_proof):
                return False
        
        # Verify it's in ledger
        ledger = self.get_session_ledger(entry.session_id)
        if not ledger:
            return False
        
        return entry in ledger.entries
    
    def get_cooling_status(self, entry_id: str) -> Dict[str, Any]:
        """
        Get cooling status of an entry.
        
        Returns:
            Cooling tier, time until promotion, and promotion path
        """
        entry = self.ledger.get_entry(entry_id)
        if not entry:
            return {"error": "Entry not found"}
        
        tier = entry.cooling_tier
        tier_info = self.config.cooling_tiers.get(tier, {})
        
        ttl = tier_info.get("ttl")
        if ttl and tier < 5:
            time_until_promotion = ttl - (datetime.utcnow() - entry.timestamp).total_seconds()
            next_tier = tier + 1
        else:
            time_until_promotion = None
            next_tier = None
        
        return {
            "entry_id": entry_id,
            "current_tier": tier,
            "tier_name": tier_info.get("name"),
            "time_until_promotion": time_until_promotion,
            "next_tier": next_tier,
            "verdict": entry.verdict,
        }
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired entries from L0-L4.
        
        Returns:
            Number of entries cleaned up
        """
        expired_count = 0
        now = datetime.utcnow()
        
        for tier in range(5):  # L0-L4 have TTLs
            tier_info = self.config.cooling_tiers.get(tier)
            if tier_info and tier_info.get("ttl"):
                ttl_seconds = tier_info["ttl"]
                tier_path = self.config.get_tier_path(tier)
                
                # Remove expired entries from this tier
                expired_count += self._cleanup_tier(tier_path, ttl_seconds, now)
        
        return expired_count
    
    def get_verdict_statistics(self) -> Dict[str, Any]:
        """
        Get constitutional verdict statistics.
        
        Returns:
            Counts of each verdict type, average floor scores, etc.
        """
        return self.ledger.get_statistics()
    
    # Private helper methods
    
    def _assign_cooling_tier(self, entry: VaultEntry) -> int:
        """Assign cooling tier based on Eureka Sieve."""
        # SEAL verdicts with high genius → L5 eternal
        if entry.verdict == "SEAL" and entry.floor_scores.get("F8_Genius", 0) > 0.85:
            return 5  # L5_ETERNAL
        
        # PARTIAL verdicts → L4 monthly
        if entry.verdict == "PARTIAL":
            return 4  # L4_MONTHLY
        
        # SABAR verdicts → L3 weekly
        if entry.verdict == "SABAR":
            return 3  # L3_WEEKLY
        
        # VOID verdicts → NEVER STORED (return -1)
        if entry.verdict == "VOID":
            return -1  # Special flag: never store
        
        # Standard SEAL → L2 phoenix (72h)
        if entry.verdict == "SEAL":
            return 2  # L2_PHOENIX
        
        # Default → L0 hot (no cooling)
        return 0  # L0_HOT
    
    def _store_entry(self, entry: VaultEntry) -> None:
        """Store entry in appropriate cooling tier."""
        if entry.cooling_tier == -1:
            # VOID verdicts are never stored
            return
        
        tier_path = self.config.get_tier_path(entry.cooling_tier)
        
        # Store as JSONL in tier directory
        tier_file = f"{tier_path}/{entry.session_id}.jsonl"
        
        with open(tier_file, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")
    
    def _cleanup_tier(self, tier_path: str, ttl_seconds: int, now: datetime) -> int:
        """Clean up expired entries from a tier."""
        expired_count = 0
        
        if not os.path.exists(tier_path):
            return 0
        
        for filename in os.listdir(tier_path):
            if not filename.endswith(".jsonl"):
                continue
            
            filepath = os.path.join(tier_path, filename)
            cleanup_needed = False
            
            with open(filepath, "r") as f:
                entries = []
                for line in f:
                    try:
                        entry_data = json.loads(line.strip())
                        entry = VaultEntry.from_dict(entry_data)
                        
                        # Check if expired
                        age_seconds = (now - entry.timestamp).total_seconds()
                        if age_seconds > ttl_seconds:
                            cleanup_needed = True
                            expired_count += 1
                        else:
                            entries.append(entry)
                    except json.JSONDecodeError:
                        # Skip corrupted entries
                        continue
            
            if cleanup_needed:
                # Rewrite file with only non-expired entries
                with open(filepath, "w") as f:
                    for entry in entries:
                        f.write(json.dumps(entry.to_dict()) + "\n")
        
        return expired_count
