"""
ledger_cryptography.py — Cryptographic Ledger for arifOS v42.

Implements Task 1.1: Cryptographic Binding for Cooling Ledger.

This module provides tamper-evident audit logging using:
- SHA3-256 hash chain (each entry commits to previous)
- Merkle tree batch verification
- Forensic anomaly detection

Design References:
- spec/v42/cooling_ledger_cryptography.md
- docs/ref/Cryptographically Tamper-Evident Cooling Ledger Design for arifOS.pdf
- docs/ref/Task 1.1_ Cryptographic Binding for Cooling Ledger.pdf

NOTE: Uses SHA3-256 (not SHA-256) for backward compatibility with existing ledger.
SHA3-256 offers equivalent security properties (collision resistance, preimage resistance).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from arifos_core.governance.merkle import build_merkle_tree, MerkleTree


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def canonical_json(data: dict) -> str:
    """
    Serialize a dictionary to JSON in a deterministic way.
    
    - Sorted keys
    - No extra whitespace  
    - UTF-8 encoding
    - ensure_ascii=False for proper Unicode handling
    
    This ensures the same logical entry always produces the same hash.
    """
    try:
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Serialization error: {e}")


def sha3_256_hex(data: Union[str, bytes]) -> str:
    """Compute SHA3-256 hash and return as hex string."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha3_256(data).hexdigest()


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class LedgerEntry:
    """
    A single entry in the cryptographic ledger.
    
    Fields:
        index: Sequential index (0-based)
        timestamp: ISO 8601 timestamp string
        payload: Governance decision data (dict)
        prev_hash: SHA3-256 hash of previous entry (hex, or GENESIS_HASH for first)
        hash: SHA3-256 hash of this entry (hex), computed from above fields
    """
    index: int
    timestamp: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: Optional[str] = None
    
    def compute_hash(self) -> str:
        """
        Compute SHA3-256 hash of this entry.
        
        Hash formula: SHA3-256(index|timestamp|canonical_json(payload)|prev_hash)
        """
        payload_str = canonical_json(self.payload)
        data_to_hash = f"{self.index}|{self.timestamp}|{payload_str}|{self.prev_hash}"
        self.hash = sha3_256_hex(data_to_hash)
        return self.hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LedgerEntry":
        """Reconstruct from dictionary."""
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            payload=data["payload"],
            prev_hash=data["prev_hash"],
            hash=data.get("hash"),
        )


@dataclass
class VerificationReport:
    """
    Result of ledger integrity verification.
    
    Fields:
        valid: True if chain is intact, False if any inconsistency found
        errors: List of error strings describing inconsistencies
        checked_entries: Number of entries verified
    """
    valid: bool = True
    errors: List[str] = field(default_factory=list)
    checked_entries: int = 0


@dataclass
class TamperReport:
    """
    Result of tampering/anomaly detection.
    
    Fields:
        tampered: True if tampering or anomalies detected
        details: List of anomaly descriptions for auditors
    """
    tampered: bool = False
    details: List[str] = field(default_factory=list)


# =============================================================================
# CRYPTOGRAPHIC LEDGER
# =============================================================================

class CryptographicLedger:
    """
    Unified cryptographic ledger per Task 1.1 spec.
    
    Provides:
    - Append-only hash-chained entries
    - Merkle tree batch verification
    - Integrity verification
    - Forensic tamper detection
    
    Usage:
        ledger = CryptographicLedger()
        entry = ledger.append_decision({"verdict": "SEAL", ...}, timestamp)
        report = ledger.verify_integrity()
        tampering = ledger.detect_tampering()
    
    Note: Uses SHA3-256 for backward compatibility with existing arifOS ledger.
    """
    
    # Genesis hash: 64 hex chars = 256 bits of zero
    GENESIS_HASH = "0" * 64
    
    def __init__(self, entries: Optional[List[LedgerEntry]] = None):
        """
        Initialize ledger, optionally with existing entries.
        
        Args:
            entries: Optional list of LedgerEntry to restore from persistence
        """
        self.entries: List[LedgerEntry] = entries or []
        self.merkle_roots: List[str] = []
        
        # Recompute Merkle root if entries provided
        if self.entries:
            self._update_merkle_root()
    
    def append_decision(
        self,
        entry_payload: Dict[str, Any],
        timestamp: Optional[str] = None,
    ) -> LedgerEntry:
        """
        Append a new governance decision to the ledger.
        
        Args:
            entry_payload: Dictionary containing decision data
            timestamp: Optional ISO 8601 timestamp (default: current UTC time)
        
        Returns:
            The newly created LedgerEntry
        
        Raises:
            TypeError: If entry_payload is not a dict
            ValueError: If payload cannot be serialized
        """
        if not isinstance(entry_payload, dict):
            raise TypeError("entry_payload must be a dictionary")
        
        # Generate timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
                "+00:00", "Z"
            )
        
        # Determine index and prev_hash
        if len(self.entries) == 0:
            prev_hash = self.GENESIS_HASH
            index = 0
        else:
            prev_hash = self.entries[-1].hash
            index = self.entries[-1].index + 1
        
        # Create and hash the entry
        entry = LedgerEntry(
            index=index,
            timestamp=timestamp,
            payload=entry_payload,
            prev_hash=prev_hash,
        )
        entry.compute_hash()
        
        # Append (append-only)
        self.entries.append(entry)
        
        # Update Merkle root
        self._update_merkle_root()
        
        return entry
    
    def _update_merkle_root(self) -> None:
        """Compute and store Merkle root for current entries."""
        if not self.entries:
            return
        
        all_hashes = [e.hash for e in self.entries]
        tree = build_merkle_tree(all_hashes)
        root = tree.root
        
        if root:
            self.merkle_roots.append(root)
    
    def get_merkle_root(self) -> Optional[str]:
        """Get the current Merkle root of all entries."""
        if not self.merkle_roots:
            return None
        return self.merkle_roots[-1]
    
    def verify_integrity(
        self,
        expected_last_hash: Optional[str] = None,
        expected_roots: Optional[List[str]] = None,
    ) -> VerificationReport:
        """
        Verify the integrity of the entire ledger (hash chain and Merkle roots).
        
        Args:
            expected_last_hash: Optional external anchor for last entry hash
            expected_roots: Optional list of expected Merkle roots from external source
        
        Returns:
            VerificationReport with valid flag and any errors
        """
        report = VerificationReport()
        n = len(self.entries)
        
        if n == 0:
            return report  # Empty ledger is trivially valid
        
        # 1. Verify linear hash chain
        for i in range(n):
            entry = self.entries[i]
            
            if i == 0:
                # First entry should have genesis prev_hash
                if entry.prev_hash != self.GENESIS_HASH:
                    report.valid = False
                    report.errors.append(
                        f"Entry 0 prev_hash {entry.prev_hash[:16]}... != GENESIS_HASH"
                    )
            else:
                prev_entry = self.entries[i - 1]
                expected_prev = prev_entry.hash
                if entry.prev_hash != expected_prev:
                    report.valid = False
                    expected_display = expected_prev[:16] + "..." if expected_prev else "None"
                    got_display = entry.prev_hash[:16] + "..." if entry.prev_hash else "None"
                    report.errors.append(
                        f"Entry {i} prev_hash mismatch "
                        f"(expected {expected_display}, got {got_display})"
                    )
            
            # Recompute this entry's hash and compare
            try:
                recalculated = LedgerEntry(
                    index=entry.index,
                    timestamp=entry.timestamp,
                    payload=entry.payload,
                    prev_hash=entry.prev_hash,
                )
                recalculated_hash = recalculated.compute_hash()
            except Exception as e:
                report.valid = False
                report.errors.append(f"Entry {i} serialization error: {e}")
                continue
            
            if entry.hash != recalculated_hash:
                report.valid = False
                stored_display = entry.hash[:16] + "..." if entry.hash else "None"
                report.errors.append(
                    f"Entry {i} content hash mismatch "
                    f"(stored {stored_display}, computed {recalculated_hash[:16]}...)"
                )
            
            report.checked_entries += 1
        
        # 2. Verify Merkle roots consistency
        if self.merkle_roots:
            all_hashes = [e.hash for e in self.entries]
            tree = build_merkle_tree(all_hashes)
            recomputed_root = tree.root
            last_recorded_root = self.merkle_roots[-1]
            
            if recomputed_root != last_recorded_root:
                report.valid = False
                report.errors.append(
                    "Merkle root mismatch: ledger data does not match stored root"
                )
        
        # 3. Cross-check with expected external roots
        if expected_roots:
            min_len = min(len(expected_roots), len(self.merkle_roots))
            for j in range(min_len):
                if expected_roots[j] != self.merkle_roots[j]:
                    report.valid = False
                    report.errors.append(
                        f"Merkle root {j} mismatch with expected external record"
                    )
        
        # 4. Verify against expected last hash (external anchor)
        if expected_last_hash:
            if n == 0 or self.entries[-1].hash != expected_last_hash:
                report.valid = False
                report.errors.append(
                    "Last entry hash does not match expected reference "
                    "(possible truncation or fork)"
                )
        
        return report
    
    def detect_tampering(self) -> TamperReport:
        """
        Analyze the ledger for signs of tampering or anomalies.
        
        Goes beyond basic hash-chain integrity to detect:
        - Hash chain breaks
        - Duplicate entry hashes
        - Non-sequential indices
        - Timestamp order violations
        - Fork evidence (prev_hash pointing to wrong ancestor)
        
        Returns:
            TamperReport with tampered flag and anomaly details
        """
        report = TamperReport()
        
        if not self.entries:
            return report  # Empty ledger, nothing to detect
        
        # 1. Run integrity verification first
        integrity_report = self.verify_integrity()
        if not integrity_report.valid:
            report.tampered = True
            for err in integrity_report.errors:
                report.details.append(f"INTEGRITY FAIL: {err}")
        
        # 2. Check for duplicate entry hashes
        seen_hashes: set = set()
        for i, entry in enumerate(self.entries):
            if entry.hash in seen_hashes:
                report.tampered = True
                report.details.append(
                    f"ANOMALY: Duplicate entry hash at index {i} "
                    f"(hash={entry.hash[:16]}...)"
                )
            else:
                seen_hashes.add(entry.hash)
        
        # 3. Check for index continuity
        for i in range(len(self.entries)):
            if self.entries[i].index != i:
                report.tampered = True
                report.details.append(
                    f"ANOMALY: Non-sequential index at position {i} "
                    f"(expected {i}, found {self.entries[i].index})"
                )
                break
        
        # 4. Check for timestamp monotonicity
        for i in range(1, len(self.entries)):
            prev_ts = self.entries[i - 1].timestamp
            curr_ts = self.entries[i].timestamp
            try:
                # ISO 8601 strings are lexicographically sortable
                if curr_ts < prev_ts:
                    report.tampered = True
                    report.details.append(
                        f"ANOMALY: Timestamp out of order at index {i} "
                        f"(prev={prev_ts}, current={curr_ts})"
                    )
                    break
            except Exception:
                report.tampered = True
                report.details.append(f"ANOMALY: Timestamp format error at index {i}")
        
        # 5. Check for fork evidence
        hash_to_index = {entry.hash: entry.index for entry in self.entries}
        for i in range(1, len(self.entries)):
            expected_prev_index = i - 1
            actual_prev_hash = self.entries[i].prev_hash
            
            # If prev_hash points to a different index than expected
            if actual_prev_hash in hash_to_index:
                actual_prev_index = hash_to_index[actual_prev_hash]
                if actual_prev_index != expected_prev_index:
                    report.tampered = True
                    report.details.append(
                        f"ANOMALY: Fork detected at index {i} "
                        f"(prev_hash points to index {actual_prev_index} instead of {expected_prev_index})"
                    )
                    break
        
        return report
    
    # =========================================================================
    # PERSISTENCE
    # =========================================================================
    
    def save_to_file(self, path: Union[Path, str]) -> None:
        """
        Save ledger to JSONL file.
        
        Args:
            path: Path to output file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open("w", encoding="utf-8") as f:
            for entry in self.entries:
                line = json.dumps(entry.to_dict(), sort_keys=True, separators=(",", ":"))
                f.write(line + "\n")
    
    @classmethod
    def load_from_file(cls, path: Union[Path, str]) -> "CryptographicLedger":
        """
        Load ledger from JSONL file.
        
        Args:
            path: Path to JSONL file
        
        Returns:
            CryptographicLedger instance with loaded entries
        
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
        """
        path = Path(path)
        entries: List[LedgerEntry] = []
        
        with path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = LedgerEntry.from_dict(data)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON at line {line_num}: {e.msg}",
                        e.doc,
                        e.pos,
                    )
        
        ledger = cls(entries=entries)
        return ledger
    
    def __len__(self) -> int:
        return len(self.entries)
    
    def __getitem__(self, index: int) -> LedgerEntry:
        return self.entries[index]
    
    # =========================================================================
    # ANCHOR SYSTEM: External rollback detection
    # =========================================================================
    
    def create_anchor(self) -> Dict[str, Any]:
        """
        Create an external anchor for rollback detection.
        
        The anchor should be stored separately (e.g., anchors.json) and used
        to verify the ledger hasn't been truncated or rolled back.
        
        Returns:
            Dict with entry_count, head_hash, merkle_root, timestamp
        """
        if not self.entries:
            return {
                "entry_count": 0,
                "head_hash": None,
                "merkle_root": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        
        return {
            "entry_count": len(self.entries),
            "head_hash": self.entries[-1].hash,
            "merkle_root": self.get_merkle_root(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def verify_against_anchor(self, anchor: Dict[str, Any]) -> VerificationReport:
        """
        Verify ledger against an external anchor to detect rollback attacks.
        
        A rollback attack removes entries from the tail of the ledger.
        The internal chain may look consistent, but:
        - entry_count will be lower
        - head_hash will be different
        - merkle_root will be different
        
        Args:
            anchor: Previously stored anchor dict from create_anchor()
        
        Returns:
            VerificationReport with rollback-specific errors if detected
        """
        errors = []
        
        anchor_count = anchor.get("entry_count", 0)
        anchor_head = anchor.get("head_hash")
        anchor_merkle = anchor.get("merkle_root")
        anchor_time = anchor.get("timestamp", "unknown")
        
        current_count = len(self.entries)
        current_head = self.entries[-1].hash if self.entries else None
        current_merkle = self.get_merkle_root()
        
        # Check 1: Entry count (detects pure truncation)
        if current_count < anchor_count:
            errors.append(
                f"ROLLBACK DETECTED: Current entry count ({current_count}) is less than "
                f"anchor count ({anchor_count}) from {anchor_time}"
            )
        
        # Check 2: Head hash (detects any modification to last entry or truncation)
        if anchor_head and current_head != anchor_head:
            if current_count == anchor_count:
                errors.append(
                    f"HEAD HASH MISMATCH: Expected {anchor_head[:16]}..., "
                    f"got {current_head[:16] if current_head else 'None'}..."
                )
            # If count is already different, the head hash difference is expected
        
        # Check 3: Merkle root (detects any content change)
        if anchor_merkle and current_merkle != anchor_merkle:
            errors.append(
                f"MERKLE ROOT MISMATCH: Expected {anchor_merkle[:16]}..., "
                f"got {current_merkle[:16] if current_merkle else 'None'}..."
            )
        
        return VerificationReport(
            valid=len(errors) == 0,
            errors=errors,
            entry_count=current_count,
            last_hash=current_head,
            merkle_root=current_merkle,
        )
    
    @staticmethod
    def save_anchor(anchor: Dict[str, Any], path: Union[Path, str]) -> None:
        """Save anchor to JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(anchor, f, indent=2)
    
    @staticmethod
    def load_anchor(path: Union[Path, str]) -> Dict[str, Any]:
        """Load anchor from JSON file."""
        path = Path(path)
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
