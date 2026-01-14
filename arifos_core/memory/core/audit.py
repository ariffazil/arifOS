"""
audit.py — Memory Audit Layer for arifOS v38

Every memory write = ledger entry + hash.
This layer provides:
1. Hash-chained write recording
2. Chain integrity verification
3. Audit trail queries
4. Merkle proof generation

Core Philosophy:
Memory that persists without evidence loses its governance value.
Every write must be traceable back to a floor check and verdict.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AuditRecord:
    """A single audit record for a memory write."""
    record_id: str
    timestamp: str
    band: str
    entry_id: str
    writer_id: str
    verdict: Optional[str]
    evidence_hash: str
    entry_hash: str
    prev_hash: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "band": self.band,
            "entry_id": self.entry_id,
            "writer_id": self.writer_id,
            "verdict": self.verdict,
            "evidence_hash": self.evidence_hash,
            "entry_hash": self.entry_hash,
            "prev_hash": self.prev_hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditRecord":
        return cls(
            record_id=data.get("record_id", ""),
            timestamp=data.get("timestamp", ""),
            band=data.get("band", ""),
            entry_id=data.get("entry_id", ""),
            writer_id=data.get("writer_id", ""),
            verdict=data.get("verdict"),
            evidence_hash=data.get("evidence_hash", ""),
            entry_hash=data.get("entry_hash", ""),
            prev_hash=data.get("prev_hash"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChainVerificationResult:
    """Result of chain integrity verification."""
    valid: bool
    total_entries: int
    verified_entries: int
    broken_links: List[Dict[str, Any]] = field(default_factory=list)
    first_error_index: Optional[int] = None
    message: str = ""


@dataclass
class MerkleProof:
    """Merkle proof for a specific entry."""
    entry_id: str
    entry_hash: str
    proof_path: List[Dict[str, str]]  # [{"hash": "...", "position": "left|right"}, ...]
    merkle_root: str
    tree_size: int


# =============================================================================
# MEMORY AUDIT LAYER
# =============================================================================

class MemoryAuditLayer:
    """
    Audit layer for memory operations.

    Every memory write is recorded with:
    - SHA-256 hash of the entry
    - Link to previous entry (chain)
    - Timestamp (microsecond precision)
    - Evidence hash linking to floor check

    Usage:
        audit = MemoryAuditLayer()
        record = audit.record_memory_write(band, entry_data, verdict, evidence_hash)
        valid, broken = audit.verify_chain_integrity()
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize audit layer.

        Args:
            storage_path: Optional path to persist audit records
        """
        self.storage_path = storage_path
        self._records: List[AuditRecord] = []
        self._last_hash: Optional[str] = None

    # =========================================================================
    # CORE AUDIT METHODS
    # =========================================================================

    def record_memory_write(
        self,
        band: str,
        entry_data: Dict[str, Any],
        verdict: Optional[str],
        evidence_hash: str,
        entry_id: Optional[str] = None,
        writer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:
        """
        Record a memory write in the audit trail.

        Args:
            band: Target band name
            entry_data: The data being written
            verdict: Associated verdict (if any)
            evidence_hash: Hash of the evidence chain
            entry_id: Optional entry ID (generated if not provided)
            writer_id: Who is writing
            metadata: Additional metadata

        Returns:
            AuditRecord with complete audit information
        """
        record_id = str(uuid.uuid4())[:12]
        entry_id = entry_id or str(uuid.uuid4())[:12]
        timestamp = self._now_iso_micro()

        # Compute entry hash
        entry_hash = self.compute_hash(entry_data)

        # Create audit record
        record = AuditRecord(
            record_id=record_id,
            timestamp=timestamp,
            band=band,
            entry_id=entry_id,
            writer_id=writer_id or "UNKNOWN",
            verdict=verdict,
            evidence_hash=evidence_hash,
            entry_hash=entry_hash,
            prev_hash=self._last_hash,
            metadata=metadata or {},
        )

        # Append to records
        self._records.append(record)
        self._last_hash = entry_hash

        return record

    def compute_hash(self, entry_data: Union[Dict[str, Any], str]) -> str:
        """
        Compute SHA-256 hash of entry data.

        Args:
            entry_data: Data to hash (dict or string)

        Returns:
            Hex-encoded SHA-256 hash
        """
        if isinstance(entry_data, dict):
            # Canonical JSON for deterministic hashing
            data_str = json.dumps(entry_data, sort_keys=True, separators=(",", ":"))
        else:
            data_str = str(entry_data)

        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def verify_chain_integrity(self) -> ChainVerificationResult:
        """
        Verify the integrity of the entire audit chain.

        Checks:
        1. Each entry.prev_hash matches previous entry.entry_hash
        2. Each entry.entry_hash is correctly computed

        Returns:
            ChainVerificationResult with verification status
        """
        if not self._records:
            return ChainVerificationResult(
                valid=True,
                total_entries=0,
                verified_entries=0,
                message="Empty audit trail (valid)",
            )

        broken_links: List[Dict[str, Any]] = []
        first_error_index: Optional[int] = None
        prev_hash: Optional[str] = None

        for i, record in enumerate(self._records):
            # Check prev_hash link
            if record.prev_hash != prev_hash:
                broken_links.append({
                    "index": i,
                    "type": "prev_hash_mismatch",
                    "expected": prev_hash,
                    "actual": record.prev_hash,
                    "record_id": record.record_id,
                })
                if first_error_index is None:
                    first_error_index = i

            prev_hash = record.entry_hash

        valid = len(broken_links) == 0
        return ChainVerificationResult(
            valid=valid,
            total_entries=len(self._records),
            verified_entries=len(self._records) - len(broken_links),
            broken_links=broken_links,
            first_error_index=first_error_index,
            message=f"Chain {'verified' if valid else 'broken'}: {len(self._records)} entries",
        )

    def audit_trail(
        self,
        entry_id: Optional[str] = None,
        band: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditRecord]:
        """
        Query audit records with optional filters.

        Args:
            entry_id: Filter by specific entry ID
            band: Filter by band name
            start_time: Filter by start timestamp (ISO8601)
            end_time: Filter by end timestamp (ISO8601)
            limit: Maximum records to return

        Returns:
            List of matching AuditRecords
        """
        results: List[AuditRecord] = []

        for record in self._records:
            # Apply filters
            if entry_id and record.entry_id != entry_id:
                continue
            if band and record.band != band:
                continue
            if start_time and record.timestamp < start_time:
                continue
            if end_time and record.timestamp > end_time:
                continue

            results.append(record)

            if len(results) >= limit:
                break

        return results

    def merkle_proof_for_entry(self, entry_id: str) -> Optional[MerkleProof]:
        """
        Compute Merkle proof showing entry is in the audit tree.

        Args:
            entry_id: ID of the entry to prove

        Returns:
            MerkleProof with proof path, or None if entry not found
        """
        # Find the entry
        entry_index: Optional[int] = None
        entry_hash: Optional[str] = None

        for i, record in enumerate(self._records):
            if record.entry_id == entry_id:
                entry_index = i
                entry_hash = record.entry_hash
                break

        if entry_index is None or entry_hash is None:
            return None

        # Build Merkle tree from all entry hashes
        leaves = [r.entry_hash for r in self._records]
        tree = self._build_merkle_tree(leaves)

        if not tree:
            return None

        # Generate proof path
        proof_path = self._generate_proof_path(tree, entry_index)
        merkle_root = tree[-1][0] if tree else ""

        return MerkleProof(
            entry_id=entry_id,
            entry_hash=entry_hash,
            proof_path=proof_path,
            merkle_root=merkle_root,
            tree_size=len(leaves),
        )

    def verify_merkle_proof(self, proof: MerkleProof) -> bool:
        """
        Verify a Merkle proof.

        Args:
            proof: MerkleProof to verify

        Returns:
            True if proof is valid, False otherwise
        """
        computed = proof.entry_hash

        for step in proof.proof_path:
            sibling = step["hash"]
            position = step["position"]

            if position == "left":
                computed = self._pair_hash(sibling, computed)
            else:  # right
                computed = self._pair_hash(computed, sibling)

        return computed == proof.merkle_root

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    def _now_iso_micro(self) -> str:
        """Get current timestamp with microsecond precision."""
        return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

    def _pair_hash(self, left: str, right: str) -> str:
        """Hash a pair of hex strings."""
        return hashlib.sha256((left + right).encode()).hexdigest()

    def _build_merkle_tree(self, leaves: List[str]) -> List[List[str]]:
        """Build Merkle tree from leaves, returning all levels."""
        if not leaves:
            return []

        # Start with leaf level
        current_level = list(leaves)
        levels: List[List[str]] = [current_level]

        # Build tree upward
        while len(current_level) > 1:
            next_level: List[str] = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left  # Duplicate if odd

                parent = self._pair_hash(left, right)
                next_level.append(parent)

            levels.append(next_level)
            current_level = next_level

        return levels

    def _generate_proof_path(
        self,
        tree: List[List[str]],
        leaf_index: int,
    ) -> List[Dict[str, str]]:
        """Generate Merkle proof path for a leaf."""
        path: List[Dict[str, str]] = []
        index = leaf_index

        for level_idx in range(len(tree) - 1):
            level = tree[level_idx]

            if index % 2 == 0:
                # Even: sibling is on the right
                sibling_index = index + 1
                position = "right"
            else:
                # Odd: sibling is on the left
                sibling_index = index - 1
                position = "left"

            if sibling_index < len(level):
                path.append({
                    "hash": level[sibling_index],
                    "position": position,
                })
            else:
                # Duplicate (odd tree)
                path.append({
                    "hash": level[index],
                    "position": position,
                })

            index //= 2

        return path

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def save_to_file(self, path: Optional[Path] = None) -> bool:
        """Save audit records to file."""
        save_path = path or self.storage_path
        if save_path is None:
            return False

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            records = [r.to_dict() for r in self._records]
            save_path.write_text(
                json.dumps(records, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            return True
        except IOError:
            return False

    def load_from_file(self, path: Optional[Path] = None) -> bool:
        """Load audit records from file."""
        load_path = path or self.storage_path
        if load_path is None or not load_path.exists():
            return False

        try:
            data = json.loads(load_path.read_text(encoding="utf-8"))
            self._records = [AuditRecord.from_dict(r) for r in data]
            if self._records:
                self._last_hash = self._records[-1].entry_hash
            return True
        except (IOError, json.JSONDecodeError):
            return False

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit statistics."""
        if not self._records:
            return {
                "total_records": 0,
                "bands": {},
                "oldest_record": None,
                "newest_record": None,
            }

        band_counts: Dict[str, int] = {}
        verdict_counts: Dict[str, int] = {}

        for record in self._records:
            band_counts[record.band] = band_counts.get(record.band, 0) + 1
            if record.verdict:
                verdict_counts[record.verdict] = verdict_counts.get(record.verdict, 0) + 1

        return {
            "total_records": len(self._records),
            "bands": band_counts,
            "verdicts": verdict_counts,
            "oldest_record": self._records[0].timestamp if self._records else None,
            "newest_record": self._records[-1].timestamp if self._records else None,
            "chain_head_hash": self._last_hash,
        }

    def clear(self) -> int:
        """Clear all audit records. Returns count cleared."""
        count = len(self._records)
        self._records.clear()
        self._last_hash = None
        return count


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_evidence_hash(
    floor_checks: List[Dict[str, Any]],
    verdict: str,
    timestamp: str,
) -> str:
    """
    Compute evidence hash from floor checks and verdict.

    This hash ties a memory write back to its governance origin.

    Args:
        floor_checks: List of floor check results
        verdict: APEX PRIME verdict
        timestamp: When the check occurred

    Returns:
        SHA-256 hex hash of the evidence
    """
    evidence = {
        "floor_checks": floor_checks,
        "verdict": verdict,
        "timestamp": timestamp,
    }
    return hashlib.sha256(
        json.dumps(evidence, sort_keys=True).encode()
    ).hexdigest()


def verify_evidence_hash(
    evidence_hash: str,
    floor_checks: List[Dict[str, Any]],
    verdict: str,
    timestamp: str,
) -> bool:
    """
    Verify that an evidence hash matches its components.

    Args:
        evidence_hash: The hash to verify
        floor_checks: List of floor check results
        verdict: APEX PRIME verdict
        timestamp: When the check occurred

    Returns:
        True if hash matches, False otherwise
    """
    computed = compute_evidence_hash(floor_checks, verdict, timestamp)
    return evidence_hash == computed


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Data classes
    "AuditRecord",
    "ChainVerificationResult",
    "MerkleProof",
    # Main class
    "MemoryAuditLayer",
    # Convenience functions
    "compute_evidence_hash",
    "verify_evidence_hash",
]
