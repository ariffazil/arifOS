"""
SEAL-999 State Management

Core state classes for immutable constitutional memory.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib
import json


@dataclass
class VaultEntry:
    """
    Single entry in SEAL-999 constitutional ledger.
    
    Immutable once written. Represents one stage transition (000→999).
    """
    entry_id: str
    session_id: str
    stage: int  # 000-999
    timestamp: datetime
    verdict: str  # SEAL, VOID, 888_HOLD, PARTIAL, SABAR
    merkle_root: str
    floor_scores: Dict[str, float]
    delta_bundle: Optional[Dict[str, Any]] = None
    omega_bundle: Optional[Dict[str, Any]] = None
    merkle_proof: Optional[Dict[str, Any]] = None
    cooling_tier: int = 0  # 0=L0, 1=L1, 2=L2, 3=L3, 4=L4, 5=L5
    
    def compute_hash(self) -> str:
        """Compute SHA256 hash of entry for hash-chaining."""
        data = {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat(),
            "verdict": self.verdict,
            "merkle_root": self.merkle_root,
            "floor_scores": self.floor_scores,
        }
        if self.delta_bundle:
            data["delta_bundle"] = self.delta_bundle
        if self.omega_bundle:
            data["omega_bundle"] = self.omega_bundle
        
        sorted_data = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_id": self.entry_id,
            "session_id": self.session_id,
            "stage": self.stage,
            "timestamp": self.timestamp.isoformat(),
            "verdict": self.verdict,
            "merkle_root": self.merkle_root,
            "floor_scores": self.floor_scores,
            "delta_bundle": self.delta_bundle,
            "omega_bundle": self.omega_bundle,
            "merkle_proof": self.merkle_proof,
            "cooling_tier": self.cooling_tier,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VaultEntry":
        """Create VaultEntry from dictionary."""
        return cls(
            entry_id=data["entry_id"],
            session_id=data["session_id"],
            stage=data["stage"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            verdict=data["verdict"],
            merkle_root=data["merkle_root"],
            floor_scores=data["floor_scores"],
            delta_bundle=data.get("delta_bundle"),
            omega_bundle=data.get("omega_bundle"),
            merkle_proof=data.get("merkle_proof"),
            cooling_tier=data.get("cooling_tier", 0),
        )


@dataclass
class SessionLedger:
    """
    Complete ledger for one session (000→999).
    
    Contains all 11 stage entries for a metabolic loop.
    """
    session_id: str
    entries: List[VaultEntry] = field(default_factory=list)
    merkle_root: Optional[str] = None
    final_verdict: Optional[str] = None
    
    def add_entry(self, entry: VaultEntry) -> None:
        """Add entry to session ledger."""
        if entry.session_id != self.session_id:
            raise ValueError("Entry session_id mismatch")
        self.entries.append(entry)
    
    def compute_merkle_root(self) -> str:
        """Compute Merkle root from all entries."""
        if not self.entries:
            return ""
        
        # Sort by stage to ensure deterministic order
        sorted_entries = sorted(self.entries, key=lambda e: e.stage)
        hashes = [e.compute_hash() for e in sorted_entries]
        
        return self._compute_merkle_tree(hashes)
    
    def _compute_merkle_tree(self, hashes: List[str]) -> str:
        """Compute Merkle root from list of hashes."""
        if not hashes:
            return ""
        
        # Simple Merkle tree implementation (micro version)
        # In production, use pymerkle library
        
        current_level = hashes
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest()[:16])
            current_level = next_level
        
        return current_level[0] if current_level else ""
    
    def get_entry(self, stage: int) -> Optional[VaultEntry]:
        """Get entry for specific stage."""
        for entry in self.entries:
            if entry.stage == stage:
                return entry
        return None
    
    def verify_integrity(self) -> bool:
        """Verify all entries belong to this session and are ordered."""
        if not self.entries:
            return True
        
        # Check all entries have same session_id
        if not all(e.session_id == self.session_id for e in self.entries):
            return False
        
        # Check stages are sequential (000, 111, 222, ...)
        stages = sorted([e.stage for e in self.entries])
        expected_stages = [0, 111, 222, 333, 444, 555, 666, 777, 888, 889, 999]
        
        for i, stage in enumerate(stages):
            if i < len(expected_stages) and stage != expected_stages[i]:
                return False
        
        return True


@dataclass
class VaultConfig:
    """Configuration for SEAL-999 storage."""
    base_path: str = "./VAULT999"
    ledger_file: str = "vault.jsonl"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    cooling_tiers = {
        0: {"name": "L0_HOT", "ttl": 1800},  # 30 minutes
        1: {"name": "L1_DAILY", "ttl": 86400},  # 24 hours
        2: {"name": "L2_PHOENIX", "ttl": 259200},  # 72 hours
        3: {"name": "L3_WEEKLY", "ttl": 604800},  # 7 days
        4: {"name": "L4_MONTHLY", "ttl": 2592000},  # 30 days
        5: {"name": "L5_ETERNAL", "ttl": None},  # Never expires
    }
    
    def get_tier_path(self, tier: int) -> str:
        """Get storage path for a cooling tier."""
        tier_info = self.cooling_tiers.get(tier, {"name": "UNKNOWN"})
        return f"{self.base_path}/{tier_info['name']}"
    
    def get_ledger_path(self) -> str:
        """Get path to main ledger file."""
        return f"{self.base_path}/{self.ledger_file}"
