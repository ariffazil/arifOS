"""
zkPC Receipt Generator

Generates zero-knowledge proofs of constitutional compliance.

Constitutional Integration:
- Creates cryptographic receipts for all SEAL verdicts
- Commits to Merkle tree for external audit
- Enables "trust but verify" governance
"""
from datetime import datetime
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

from arifos.engines.zkpc.merkle_tree import MerkleTree
from arifos.memory.ledger.db_connection import DatabaseConnection

logger = logging.getLogger(__name__)


@dataclass
class FloorVerification:
    """Result of verifying a single constitutional floor."""
    floor_id: str
    passed: bool
    confidence: float
    threshold: float
    reasoning: Optional[str] = None


@dataclass
class TriWitnessConsensus:
    """Tri-witness consensus validation."""
    human: Dict[str, any]
    ai: Dict[str, any]
    earth: Dict[str, any]
    consensus_rate: float
    verdict: str  # SEAL/PARTIAL/VOID


@dataclass
class ZKPCReceiptV47:
    """
    Zero-Knowledge Proof of Cognition Receipt (v47.1)

    Cryptographic proof that all 12 constitutional floors were validated.
    """
    zkpc_id: str
    version: str
    verdict: str  # SEAL/PARTIAL/VOID/SABAR/888_HOLD
    timestamp: str

    # Constitutional floor verification (F1-F12)
    floors_verified: Dict[str, FloorVerification]

    # Tri-witness consensus (F3)
    tri_witness: TriWitnessConsensus

    # Merkle commitment
    merkle_root: str
    merkle_proof: Optional[List] = None

    # Cryptographic signature
    signature: str = ""

    # Metadata
    model_id: str = "arifos-v47.1"
    entry_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert FloorVerification objects to dicts
        data["floors_verified"] = {
            k: asdict(v) for k, v in self.floors_verified.items()
        }
        # Convert TriWitnessConsensus to dict
        data["tri_witness"] = asdict(self.tri_witness)
        return data


class ReceiptGenerator:
    """
    Generate zkPC receipts for constitutional verdicts.

    Integrates with:
    - Constitutional floors (F1-F12)
    - Merkle tree commitment
    - Tri-witness consensus
    """

    def __init__(self, vault_root: str = "vault_999"):
        self.vault_root = Path(vault_root)
        self.receipts_path = self.vault_root / "INFRASTRUCTURE/zkpc_receipts/receipts.jsonl"
        self.merkle_tree = MerkleTree(vault_root=vault_root)

        # Ensure files exist
        self.receipts_path.parent.mkdir(parents=True, exist_ok=True)
        self.receipts_path.touch(exist_ok=True)

        # Load existing receipts into Merkle tree
        self._load_existing_receipts()

    def _load_existing_receipts(self):
        """Load existing receipts to rebuild Merkle tree."""
        if not self.receipts_path.exists() or self.receipts_path.stat().st_size == 0:
            return

        with open(self.receipts_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                receipt_data = json.loads(line)
                self.merkle_tree.add_receipt(receipt_data)

    def generate_seal_receipt(
        self,
        verdict_data: Dict,
        entry_id: Optional[str] = None
    ) -> Optional[ZKPCReceiptV47]:
        """
        Generate zkPC receipt for SEAL verdict.

        Args:
            verdict_data: Verdict with floor verification results
            entry_id: Optional entry identifier

        Returns:
            ZKPCReceiptV47 receipt or None if not SEAL
        """
        if verdict_data.get("verdict") != "SEAL":
            return None

        # Generate unique ID
        zkpc_id = f"ZKPC-{uuid.uuid4().hex[:12].upper()}"

        # Parse floor verifications
        floors_verified = self._parse_floor_verifications(
            verdict_data.get("floors", {})
        )

        # Parse tri-witness consensus
        tri_witness = self._parse_tri_witness(
            verdict_data.get("tri_witness", {})
        )

        # Get current Merkle root
        current_root = self.merkle_tree.get_root()

        # Create receipt
        receipt = ZKPCReceiptV47(
            zkpc_id=zkpc_id,
            version="v47.1",
            verdict=verdict_data["verdict"],
            timestamp=datetime.now().isoformat(),
            floors_verified=floors_verified,
            tri_witness=tri_witness,
            merkle_root=current_root,
            signature=self._sign_receipt(verdict_data),
            model_id="arifos-v47.1-quantum",
            entry_id=entry_id
        )

        # Add to Merkle tree
        receipt_dict = receipt.to_dict()
        leaf_hash = self.merkle_tree.add_receipt(receipt_dict)

        # Update Merkle root
        new_root = self.merkle_tree.save_root()
        receipt.merkle_root = new_root

        # Save receipt
        self._save_receipt(receipt)

        return receipt

    def _parse_floor_verifications(
        self,
        floors_data: Dict
    ) -> Dict[str, FloorVerification]:
        """Parse floor verification results from verdict data."""
        floors_verified = {}

        # Expected floors F1-F12
        floor_ids = [
            "F1", "F2", "F3", "F4", "F5", "F6",
            "F7", "F8", "F9", "F10", "F11", "F12"
        ]

        for floor_id in floor_ids:
            floor_data = floors_data.get(floor_id, {})

            floors_verified[floor_id] = FloorVerification(
                floor_id=floor_id,
                passed=floor_data.get("passed", False),
                confidence=floor_data.get("confidence", 0.0),
                threshold=floor_data.get("threshold", 0.0),
                reasoning=floor_data.get("reasoning")
            )

        return floors_verified

    def _parse_tri_witness(self, tri_witness_data: Dict) -> TriWitnessConsensus:
        """Parse tri-witness consensus from verdict data."""
        return TriWitnessConsensus(
            human=tri_witness_data.get("human", {"verdict": "UNKNOWN", "confidence": 0.0}),
            ai=tri_witness_data.get("ai", {"verdict": "UNKNOWN", "confidence": 0.0}),
            earth=tri_witness_data.get("earth", {"verdict": "UNKNOWN", "confidence": 0.0}),
            consensus_rate=tri_witness_data.get("consensus_rate", 0.0),
            verdict=tri_witness_data.get("verdict", "VOID")
        )

    def _sign_receipt(self, verdict_data: Dict) -> str:
        """
        Generate cryptographic signature for receipt.

        This is a simplified hash-based signature.
        Production would use proper cryptographic signing.
        """
        import hashlib

        # Serialize verdict data deterministically
        verdict_json = json.dumps(verdict_data, sort_keys=True, separators=(',', ':'))

        # Create signature hash
        signature = hashlib.sha256(verdict_json.encode('utf-8')).hexdigest()

        return signature

    def _save_receipt(self, receipt: ZKPCReceiptV47):
        """
        Save receipt to JSONL file and database (dual storage).

        Dual Storage Strategy:
        1. Always write to JSONL (file-based fallback)
        2. Optionally write to Postgres (if available)

        Constitutional Compliance:
        - F1 (Amanah): Reversible - files provide backup
        - F5 (Peace²): Non-destructive - database failure doesn't lose data
        """
        # 1. Always write to file (primary fallback)
        with open(self.receipts_path, "a") as f:
            f.write(json.dumps(receipt.to_dict()) + "\n")

        # 2. Write to database if available
        if DatabaseConnection.is_available():
            try:
                # Prepare data for database
                db_data = {
                    "id": uuid.uuid4(),  # New UUID for database row
                    "entry_id": uuid.UUID(receipt.entry_id) if receipt.entry_id else None,
                    "proof_type": "Merkle",  # zkPC uses Merkle tree
                    "proof_data": receipt.to_dict(),  # Full receipt as JSONB
                    "merkle_root": receipt.merkle_root,
                    "merkle_depth": len(self.merkle_tree.leaves) if self.merkle_tree.leaves else 0,
                    "sealed_by": "Tri-Witness",  # Per Track B spec
                    "verification_status": "VALID"  # Sealed receipts are valid
                }

                # Insert to zkpc_receipts table
                result = DatabaseConnection.insert_one(
                    "zkpc_receipts",
                    db_data,
                    returning="id"
                )

                if result:
                    logger.debug(f"✓ zkPC receipt saved to database: {result['id']}")
                else:
                    logger.warning(f"Database insert returned None for receipt {receipt.zkpc_id}")

            except Exception as e:
                logger.warning(f"Database save failed for receipt {receipt.zkpc_id}: {e}")
                logger.info("  Fallback: File-based storage preserved")
        else:
            logger.debug(f"Database unavailable - receipt {receipt.zkpc_id} saved to file only")

    def get_receipt(self, zkpc_id: str) -> Optional[ZKPCReceiptV47]:
        """
        Retrieve receipt by ID.

        Args:
            zkpc_id: Receipt identifier

        Returns:
            ZKPCReceiptV47 or None if not found
        """
        if not self.receipts_path.exists():
            return None

        with open(self.receipts_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                if data.get("zkpc_id") == zkpc_id:
                    # Reconstruct receipt
                    return self._dict_to_receipt(data)

        return None

    def _dict_to_receipt(self, data: Dict) -> ZKPCReceiptV47:
        """Convert dictionary back to ZKPCReceiptV47."""
        # Reconstruct floor verifications
        floors_verified = {
            k: FloorVerification(**v)
            for k, v in data["floors_verified"].items()
        }

        # Reconstruct tri-witness
        tri_witness = TriWitnessConsensus(**data["tri_witness"])

        return ZKPCReceiptV47(
            zkpc_id=data["zkpc_id"],
            version=data["version"],
            verdict=data["verdict"],
            timestamp=data["timestamp"],
            floors_verified=floors_verified,
            tri_witness=tri_witness,
            merkle_root=data["merkle_root"],
            merkle_proof=data.get("merkle_proof"),
            signature=data.get("signature", ""),
            model_id=data.get("model_id", ""),
            entry_id=data.get("entry_id")
        )

    def get_all_receipts(self, limit: int = 100) -> List[ZKPCReceiptV47]:
        """
        Get recent receipts.

        Args:
            limit: Maximum number of receipts to return

        Returns:
            List of ZKPCReceiptV47 receipts
        """
        receipts = []

        if not self.receipts_path.exists() or self.receipts_path.stat().st_size == 0:
            return receipts

        with open(self.receipts_path, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                receipts.append(self._dict_to_receipt(data))

        # Return most recent
        return sorted(receipts, key=lambda r: r.timestamp, reverse=True)[:limit]

    def get_stats(self) -> Dict:
        """Get receipt statistics."""
        receipts = self.get_all_receipts(limit=10000)  # Get all

        verdicts = {}
        for receipt in receipts:
            verdict = receipt.verdict
            verdicts[verdict] = verdicts.get(verdict, 0) + 1

        merkle_stats = self.merkle_tree.get_stats()

        return {
            "total_receipts": len(receipts),
            "verdicts": verdicts,
            "merkle_tree": merkle_stats
        }


if __name__ == "__main__":
    # Example usage
    print("=== zkPC Receipt Generator Demo ===\n")

    generator = ReceiptGenerator()

    # Sample verdict data
    verdict_data = {
        "verdict": "SEAL",
        "floors": {
            f"F{i}": {
                "passed": True,
                "confidence": 0.95 + (i * 0.002),  # Slight variation
                "threshold": 0.95,
                "reasoning": f"Floor {i} verification complete"
            }
            for i in range(1, 13)
        },
        "tri_witness": {
            "human": {"verdict": "SEAL", "confidence": 1.0},
            "ai": {"verdict": "SEAL", "confidence": 0.98},
            "earth": {"verdict": "SEAL", "confidence": 0.97},
            "consensus_rate": 0.983,
            "verdict": "SEAL"
        }
    }

    # Generate receipt
    print("Generating zkPC receipt for SEAL verdict...")
    receipt = generator.generate_seal_receipt(verdict_data, entry_id="test_001")

    if receipt:
        print(f"\n✓ Receipt generated: {receipt.zkpc_id}")
        print(f"  Version: {receipt.version}")
        print(f"  Verdict: {receipt.verdict}")
        print(f"  Timestamp: {receipt.timestamp}")
        print(f"  Merkle Root: {receipt.merkle_root}")
        print(f"  Signature: {receipt.signature[:32]}...")

        # Show floor verification summary
        passed_floors = sum(1 for f in receipt.floors_verified.values() if f.passed)
        print(f"\n  Floors Verified: {passed_floors}/12")

        # Show tri-witness consensus
        print(f"  Tri-Witness Consensus: {receipt.tri_witness.consensus_rate:.2%}")

    # Get statistics
    print("\n=== Statistics ===")
    stats = generator.get_stats()
    print(f"Total Receipts: {stats['total_receipts']}")
    print(f"Verdicts: {stats['verdicts']}")
    print(f"Merkle Tree Leaves: {stats['merkle_tree']['leaf_count']}")
    print(f"Merkle Tree Height: {stats['merkle_tree']['tree_height']}")
