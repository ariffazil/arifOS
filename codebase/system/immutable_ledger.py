"""
Immutable Ledger - SHA256 Hash-Chained Measurement History
Ported to Codebase System

Constitutional Mandate:
- Every quantum measurement must be cryptographically sealed
- Ledger integrity must be provable (can't modify history)
- Entropy accounting: max N entries per epoch, then rotate
- F6 (Amanah): Trustworthy history requires immutable proof

Authority: v47 Constitutional Law Section 8 (Measurement Integrity)
Implementation: Engineer (Ω) under governance directive
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class LedgerRecord:
    """
    Single measurement record in the ledger.

    Immutability:
    - timestamp: When measurement occurred (ISO8601 UTC)
    - query_hash: SHA256 of query (privacy: don't store raw query)
    - verdict: Final collapsed verdict
    - agi_verdict: AGI particle verdict
    - asi_verdict: ASI particle verdict
    - apex_verdict: APEX particle verdict
    - omega_ortho: Orthogonality index (if available)
    - settlement_ms: Time to settle (if available)
    - prev_hash: Hash of previous record (chain link)
    - record_hash: SHA256 of this record (current link)
    """

    # Core fields
    timestamp: str
    query_hash: str
    verdict: str

    # Particle verdicts
    agi_verdict: Optional[str] = None
    asi_verdict: Optional[str] = None
    apex_verdict: Optional[str] = None

    # Governance metrics
    omega_ortho: Optional[float] = None
    settlement_ms: Optional[float] = None

    # Hash chain
    prev_hash: str = "GENESIS"
    record_hash: str = ""

    # Metadata
    epoch: int = 0
    sequence: int = 0


class ImmutableLedger:
    """
    Cryptographically-sealed ledger for quantum measurements.

    Constitutional Floors:
    - F1 (Amanah): Immutable history builds trust
    - F2 (Truth): Can prove what verdicts were rendered
    - F8 (Tri-Witness): Ledger serves as Earth witness

    Features:
    - SHA256 hash chain (tamper-evident)
    - Epoch rotation (max N records per epoch)
    - Export for external audit
    - Integrity verification
    """

    # Constitutional parameters
    MAX_RECORDS_PER_EPOCH = 1000  # Rotate after 1000 measurements
    GENESIS_HASH = "GENESIS"

    def __init__(self, persist_path: Optional[Path] = None):
        """
        Initialize immutable ledger.

        Args:
            persist_path: Optional path to persist ledger (for production use)
        """
        self.records: List[LedgerRecord] = []
        self.hash_chain: List[str] = [self.GENESIS_HASH]
        self.current_epoch = 0
        self.persist_path = persist_path

        self.total_appends = 0
        self.epoch_rotations = 0

    def append(
        self,
        query: str,
        verdict: str,
        agi_verdict: Optional[str] = None,
        asi_verdict: Optional[str] = None,
        apex_verdict: Optional[str] = None,
        omega_ortho: Optional[float] = None,
        settlement_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Append measurement to immutable ledger.

        Constitutional Process:
        1. Hash query (privacy: don't store raw queries)
        2. Create record with prev_hash
        3. Compute record_hash = SHA256(prev_hash + record_data)
        4. Append to chain
        5. Check if epoch rotation needed

        Returns:
            str: record_hash (proof of measurement)
        """

        # Check if epoch rotation needed
        if len(self.records) >= self.MAX_RECORDS_PER_EPOCH:
            self._rotate_epoch()

        # Hash query for privacy
        query_hash = hashlib.sha256(query.encode()).hexdigest()[:16]  # First 16 chars

        # Get previous hash
        prev_hash = self.hash_chain[-1] if self.hash_chain else self.GENESIS_HASH

        # Create record
        record = LedgerRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            query_hash=query_hash,
            verdict=verdict,
            agi_verdict=agi_verdict,
            asi_verdict=asi_verdict,
            apex_verdict=apex_verdict,
            omega_ortho=omega_ortho,
            settlement_ms=settlement_ms,
            prev_hash=prev_hash,
            epoch=self.current_epoch,
            sequence=len(self.records)
        )

        # Compute record hash
        record_hash = self._compute_record_hash(record)
        record.record_hash = record_hash

        # Append to chain
        self.records.append(record)
        self.hash_chain.append(record_hash)
        self.total_appends += 1

        # Persist if path configured
        if self.persist_path:
            self._persist_record(record)

        return record_hash

    def _compute_record_hash(self, record: LedgerRecord) -> str:
        """
        Compute SHA256 hash of record.

        Hash Input:
        - prev_hash (chain link)
        - timestamp
        - query_hash
        - verdict
        - particle verdicts
        - governance metrics

        This makes the chain tamper-evident:
        - Changing any field breaks the hash
        - Changing order breaks the chain
        - Deleting records breaks the chain
        """

        # Create deterministic JSON (sorted keys)
        record_dict = {
            "prev_hash": record.prev_hash,
            "timestamp": record.timestamp,
            "query_hash": record.query_hash,
            "verdict": record.verdict,
            "agi_verdict": record.agi_verdict,
            "asi_verdict": record.asi_verdict,
            "apex_verdict": record.apex_verdict,
            "omega_ortho": record.omega_ortho,
            "settlement_ms": record.settlement_ms,
            "epoch": record.epoch,
            "sequence": record.sequence
        }

        record_bytes = json.dumps(record_dict, sort_keys=True).encode()

        # SHA256 hash
        record_hash = hashlib.sha256(record_bytes).hexdigest()

        return record_hash

    def verify_integrity(self) -> tuple[bool, Optional[str]]:
        """
        Verify ledger integrity (detect tampering).

        Constitutional Audit:
        - Recompute all hashes
        - Verify chain links (each record points to correct prev_hash)
        - Check for gaps in sequence numbers

        Returns:
            tuple: (is_valid, error_message)
        """

        if not self.records:
            return True, None

        # Verify hash chain
        expected_prev_hash = self.GENESIS_HASH

        for i, record in enumerate(self.records):
            # Check prev_hash matches
            if record.prev_hash != expected_prev_hash:
                return False, f"Record {i}: prev_hash mismatch (expected {expected_prev_hash}, got {record.prev_hash})"

            # Recompute hash
            recomputed_hash = self._compute_record_hash(record)

            if recomputed_hash != record.record_hash:
                return False, f"Record {i}: hash mismatch (tampered?)"

            # Check sequence
            if record.sequence != i:
                return False, f"Record {i}: sequence mismatch (expected {i}, got {record.sequence})"

            # Update expected prev_hash for next iteration
            expected_prev_hash = record.record_hash

        return True, None

    def _rotate_epoch(self):
        """
        Rotate to new epoch (entropy management).

        Constitutional Process:
        1. Seal current epoch (export to archive)
        2. Reset records list (new epoch)
        3. Carry forward last hash (chain continuity)
        4. Increment epoch counter
        """

        if self.persist_path:
            # Export current epoch before rotation
            epoch_file = self.persist_path / f"ledger_epoch_{self.current_epoch}.json"
            self.export_ledger(epoch_file)

        # Rotate
        self.current_epoch += 1
        self.epoch_rotations += 1

        # Keep hash chain continuity
        last_hash = self.hash_chain[-1] if self.hash_chain else self.GENESIS_HASH

        # Reset records (new epoch)
        self.records = []
        self.hash_chain = [last_hash]

        print(f"📊 Epoch rotated: Now in epoch {self.current_epoch}")
        print(f"   Last hash: {last_hash[:16]}...")
        print(f"   Total rotations: {self.epoch_rotations}")

    def export_ledger(self, output_path: Path):
        """
        Export ledger to JSON for external audit.

        Format:
        {
            "epoch": N,
            "total_records": M,
            "genesis_hash": "...",
            "final_hash": "...",
            "records": [...]
        }
        """

        ledger_data = {
            "epoch": self.current_epoch,
            "total_records": len(self.records),
            "genesis_hash": self.GENESIS_HASH,
            "final_hash": self.hash_chain[-1] if self.hash_chain else self.GENESIS_HASH,
            "records": [asdict(r) for r in self.records]
        }

        with open(output_path, 'w') as f:
            json.dump(ledger_data, f, indent=2)

        print(f"📦 Ledger exported: {output_path}")

    def _persist_record(self, record: LedgerRecord):
        """
        Persist single record (append-only log).

        For production use: write each record immediately to disk.
        This allows recovery even if process crashes.
        """

        if not self.persist_path:
            return

        # Ensure directory exists
        self.persist_path.mkdir(parents=True, exist_ok=True)

        # Append-only log file for current epoch
        log_file = self.persist_path / f"ledger_epoch_{self.current_epoch}_append.jsonl"

        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')

    def get_ledger_metrics(self) -> Dict[str, Any]:
        """
        Return ledger governance metrics.

        Constitutional KPIs:
        - Total measurements recorded
        - Epoch status (current epoch, rotations)
        - Integrity status (last verification)
        - Hash chain summary
        """

        is_valid, error = self.verify_integrity()

        return {
            "total_appends": self.total_appends,
            "current_epoch": self.current_epoch,
            "epoch_rotations": self.epoch_rotations,
            "records_in_current_epoch": len(self.records),
            "max_records_per_epoch": self.MAX_RECORDS_PER_EPOCH,
            "integrity": {
                "is_valid": is_valid,
                "error": error,
                "last_verification": datetime.now(timezone.utc).isoformat()
            },
            "hash_chain": {
                "genesis_hash": self.GENESIS_HASH,
                "current_hash": self.hash_chain[-1] if self.hash_chain else self.GENESIS_HASH,
                "chain_length": len(self.hash_chain)
            }
        }
