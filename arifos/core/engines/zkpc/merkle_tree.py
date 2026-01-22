"""
Merkle Tree for zkPC Receipt Commitment

Enables external audit without revealing content.

Constitutional Integration:
- Creates immutable audit trail (F2 Truth)
- Enables verification without disclosure (F6 Amanah)
- Supports cryptographic accountability (F8 Tri-Witness)
"""
import hashlib
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class MerkleTree:
    """
    Merkle Tree implementation for zkPC receipts.

    Provides cryptographic commitment to all SEAL verdicts
    without revealing individual receipt contents.
    """

    def __init__(self, vault_root: str = "vault_999"):
        self.vault_root = Path(vault_root)
        self.root_file = self.vault_root / "INFRASTRUCTURE/zkpc_receipts/merkle_root.txt"
        self.leaves: List[str] = []

        # Ensure directory exists
        self.root_file.parent.mkdir(parents=True, exist_ok=True)

    def hash_data(self, data: str) -> str:
        """Hash data using SHA-256."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def hash_pair(self, left: str, right: str) -> str:
        """Hash a pair of hashes together."""
        combined = left + right
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()

    def add_receipt(self, receipt_data: Dict) -> str:
        """
        Add receipt hash as leaf to the tree.

        Args:
            receipt_data: Receipt dictionary (will be JSON serialized)

        Returns:
            Leaf hash that was added
        """
        # Serialize receipt deterministically
        receipt_json = json.dumps(receipt_data, sort_keys=True, separators=(',', ':'))
        leaf_hash = self.hash_data(receipt_json)

        # Add to leaves
        self.leaves.append(leaf_hash)

        return leaf_hash

    def build_tree(self, leaves: Optional[List[str]] = None) -> str:
        """
        Build Merkle tree from leaves and return root hash.

        Args:
            leaves: Optional list of leaf hashes (uses self.leaves if None)

        Returns:
            Merkle root hash
        """
        if leaves is None:
            leaves = self.leaves

        if not leaves:
            # Empty tree
            return "0" * 64

        # Single leaf is its own root
        if len(leaves) == 1:
            return leaves[0]

        # Build tree bottom-up
        current_level = leaves[:]

        while len(current_level) > 1:
            next_level = []

            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]

                # If odd number, duplicate last element
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left

                parent = self.hash_pair(left, right)
                next_level.append(parent)

            current_level = next_level

        # Root is the final remaining hash
        return current_level[0]

    def get_root(self) -> str:
        """
        Calculate current Merkle root from all leaves.

        Returns:
            Merkle root hash (64-char hex string)
        """
        return self.build_tree()

    def save_root(self, root: Optional[str] = None) -> str:
        """
        Save Merkle root to file.

        Args:
            root: Optional root hash (auto-calculated if None)

        Returns:
            Saved root hash
        """
        if root is None:
            root = self.get_root()

        # Save to file
        self.root_file.write_text(root)

        return root

    def load_root(self) -> Optional[str]:
        """
        Load Merkle root from file.

        Returns:
            Loaded root hash or None if file doesn't exist
        """
        if not self.root_file.exists():
            return None

        return self.root_file.read_text().strip()

    def generate_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        """
        Generate Merkle proof for a specific leaf.

        Args:
            leaf_index: Index of leaf to generate proof for

        Returns:
            List of (hash, position) tuples for proof path
            position is "left" or "right"
        """
        if leaf_index >= len(self.leaves):
            raise ValueError(f"Leaf index {leaf_index} out of range")

        proof = []
        current_level = self.leaves[:]
        current_index = leaf_index

        while len(current_level) > 1:
            next_level = []

            # Process pairs and track proof path
            for i in range(0, len(current_level), 2):
                left = current_level[i]

                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                else:
                    right = left

                # If current index is in this pair, record sibling
                if i == current_index:
                    # We're the left node, sibling is right
                    proof.append((right, "right"))
                    current_index = i // 2
                elif i + 1 == current_index:
                    # We're the right node, sibling is left
                    proof.append((left, "left"))
                    current_index = i // 2

                parent = self.hash_pair(left, right)
                next_level.append(parent)

            current_level = next_level

        return proof

    def verify_proof(self, leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """
        Verify a Merkle proof.

        Args:
            leaf_hash: Hash of the leaf to verify
            proof: List of (sibling_hash, position) tuples
            root: Expected Merkle root

        Returns:
            True if proof is valid, False otherwise
        """
        current_hash = leaf_hash

        # Traverse proof path
        for sibling_hash, position in proof:
            if position == "left":
                # Sibling is on the left, we're on the right
                current_hash = self.hash_pair(sibling_hash, current_hash)
            else:
                # Sibling is on the right, we're on the left
                current_hash = self.hash_pair(current_hash, sibling_hash)

        # Check if we arrived at the expected root
        return current_hash == root

    def get_stats(self) -> Dict:
        """
        Get statistics about the Merkle tree.

        Returns:
            Dictionary with tree statistics
        """
        leaf_count = len(self.leaves)
        root = self.get_root()
        saved_root = self.load_root()

        # Calculate tree height
        height = 0
        if leaf_count > 0:
            height = (leaf_count - 1).bit_length()

        return {
            "leaf_count": leaf_count,
            "tree_height": height,
            "current_root": root,
            "saved_root": saved_root,
            "root_synced": root == saved_root if saved_root else False
        }


if __name__ == "__main__":
    # Example usage
    print("=== Merkle Tree Demo ===\n")

    tree = MerkleTree()

    # Add some sample receipts
    receipts = [
        {"zkpc_id": "ZKPC-001", "verdict": "SEAL", "timestamp": "2026-01-17T10:00:00Z"},
        {"zkpc_id": "ZKPC-002", "verdict": "SEAL", "timestamp": "2026-01-17T11:00:00Z"},
        {"zkpc_id": "ZKPC-003", "verdict": "SEAL", "timestamp": "2026-01-17T12:00:00Z"},
    ]

    print("Adding receipts...")
    for receipt in receipts:
        leaf_hash = tree.add_receipt(receipt)
        print(f"  Added {receipt['zkpc_id']}: {leaf_hash[:16]}...")

    # Build tree and get root
    root = tree.get_root()
    print(f"\nMerkle root: {root}")

    # Save root
    saved_root = tree.save_root()
    print(f"Saved root:  {saved_root}")

    # Generate proof for second receipt
    print("\n=== Proof Generation ===")
    proof = tree.generate_proof(1)
    print(f"Generated proof for ZKPC-002 (index 1):")
    for i, (hash_val, position) in enumerate(proof):
        print(f"  Step {i+1}: {hash_val[:16]}... (sibling on {position})")

    # Verify proof
    leaf_hash = tree.leaves[1]
    is_valid = tree.verify_proof(leaf_hash, proof, root)
    print(f"\nProof verification: {'✓ VALID' if is_valid else '✗ INVALID'}")

    # Get statistics
    print("\n=== Tree Statistics ===")
    stats = tree.get_stats()
    print(f"Total leaves: {stats['leaf_count']}")
    print(f"Tree height:  {stats['tree_height']}")
    print(f"Root synced:  {'✓' if stats['root_synced'] else '✗'}")
