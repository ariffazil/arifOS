"""
Merkle Tree Vault Validation for arifOS
Using pymerkle for cryptographic vault integrity checking

References:
- pymerkle: https://pypi.org/project/pymerkle/
- Merkle Trees Tutorial: https://redandgreen.co.uk/understanding-merkle-trees-in-python-a-step-by-step-guide/
- HashiCorp Vault Merkle: https://developer.hashicorp.com/vault/docs/enterprise/replication/check-merkle-tree-corruption
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MerkleProof:
    """Proof that a file is in the Merkle tree"""
    file_path: str
    file_hash: str
    proof_path: List[str]  # Hashes needed to verify
    merkle_root: str
    timestamp: str


class SimpleMerkleTree:
    """
    Lightweight Merkle tree for vault validation

    Based on:
    - Bitcoin's Merkle tree design (SHA-256)
    - pymerkle library patterns
    - HashiCorp Vault replication checks
    """

    def __init__(self):
        self.leaves: List[bytes] = []
        self.tree: List[List[bytes]] = []
        self.root: Optional[bytes] = None

    def _hash(self, data: bytes) -> bytes:
        """SHA-256 hash with double-hashing for security"""
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()

    def add_leaf(self, data: bytes) -> None:
        """Add data as a leaf node"""
        leaf_hash = self._hash(data)
        self.leaves.append(leaf_hash)

    def build_tree(self) -> bytes:
        """
        Build Merkle tree from leaves
        Returns: Merkle root hash
        """
        if not self.leaves:
            raise ValueError("No leaves to build tree")

        # Start with leaf hashes
        current_level = self.leaves.copy()
        self.tree = [current_level]

        # Build tree upwards
        while len(current_level) > 1:
            next_level = []

            # Pair nodes and hash
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                # If odd number, duplicate last node
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                # Concatenate and hash
                combined = left + right
                parent_hash = self._hash(combined)
                next_level.append(parent_hash)

            self.tree.append(next_level)
            current_level = next_level

        self.root = current_level[0]
        return self.root

    def get_root_hex(self) -> str:
        """Get Merkle root as hex string"""
        if not self.root:
            self.build_tree()
        return self.root.hex()

    def generate_proof(self, leaf_index: int) -> List[str]:
        """
        Generate Merkle proof for a specific leaf

        Args:
            leaf_index: Index of the leaf to prove

        Returns:
            List of sibling hashes needed to verify the leaf
        """
        if leaf_index >= len(self.leaves):
            raise ValueError("Leaf index out of range")

        proof = []
        index = leaf_index

        # Traverse tree from bottom to top
        for level in self.tree[:-1]:  # Exclude root
            # Find sibling
            if index % 2 == 0:
                # Left node, need right sibling
                sibling_index = index + 1
            else:
                # Right node, need left sibling
                sibling_index = index - 1

            # Add sibling to proof (if exists)
            if sibling_index < len(level):
                proof.append(level[sibling_index].hex())

            # Move to parent level
            index = index // 2

        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[str], root_hash: str) -> bool:
        """
        Verify a Merkle proof

        Args:
            leaf_hash: Hash of the leaf to verify
            proof: List of sibling hashes
            root_hash: Expected Merkle root

        Returns:
            True if proof is valid
        """
        current_hash = bytes.fromhex(leaf_hash)

        # Traverse proof path
        for sibling_hex in proof:
            sibling = bytes.fromhex(sibling_hex)

            # Determine order (smaller hash first)
            if current_hash <= sibling:
                combined = current_hash + sibling
            else:
                combined = sibling + current_hash

            # Hash to next level
            current_hash = hashlib.sha256(hashlib.sha256(combined).digest()).digest()

        # Check if we reached the root
        return current_hash.hex() == root_hash


class VaultMerkleValidator:
    """
    Vault integrity validator using Merkle trees

    Validates vault_999 state against constitutional seal
    """

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.merkle_tree = SimpleMerkleTree()

    def hash_file(self, file_path: Path) -> bytes:
        """Hash a single file"""
        with open(file_path, 'rb') as f:
            content = f.read()
            return hashlib.sha256(content).digest()

    def scan_vault(self) -> Dict[str, str]:
        """
        Scan vault and build file hash map

        Returns:
            Dict mapping file paths to hashes
        """
        file_hashes = {}

        # Recursively hash all files
        for file_path in sorted(self.vault_path.rglob('*')):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.vault_path)
                file_hash = self.hash_file(file_path)
                file_hashes[str(relative_path)] = file_hash.hex()

                # Add to Merkle tree
                # Include filename in hash for uniqueness
                data = f"{relative_path}:{file_hash.hex()}".encode()
                self.merkle_tree.add_leaf(data)

        return file_hashes

    def compute_vault_root(self) -> str:
        """
        Compute Merkle root for entire vault

        Returns:
            Merkle root hash (hex)
        """
        self.scan_vault()
        return self.merkle_tree.get_root_hex()

    def create_seal(self, version: str, floors_validated: Dict[str, str]) -> Dict:
        """
        Create constitutional seal with Merkle proof

        Args:
            version: Version being sealed (e.g., "v50.0.0")
            floors_validated: Dict of floor results (e.g., {"F1": "PASS"})

        Returns:
            Seal data structure
        """
        file_hashes = self.scan_vault()
        merkle_root = self.merkle_tree.get_root_hex()

        seal = {
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "merkle_root": merkle_root,
            "file_count": len(file_hashes),
            "floors_validated": floors_validated,
            "file_hashes": file_hashes,
            "verification": {
                "algorithm": "SHA-256 double-hash",
                "tree_depth": len(self.merkle_tree.tree),
                "leaf_count": len(self.merkle_tree.leaves)
            }
        }

        return seal

    def verify_seal(self, seal: Dict) -> bool:
        """
        Verify vault matches seal

        Args:
            seal: Seal data structure

        Returns:
            True if vault integrity verified
        """
        # Compute current vault root
        current_root = self.compute_vault_root()

        # Compare with sealed root
        sealed_root = seal["merkle_root"]

        if current_root != sealed_root:
            print(f"❌ VOID - Vault tampered!")
            print(f"   Expected: {sealed_root}")
            print(f"   Found:    {current_root}")
            return False

        print(f"✅ SEAL - Vault integrity verified")
        print(f"   Merkle root: {current_root}")
        print(f"   Files: {len(self.merkle_tree.leaves)}")
        return True

    def prove_file_inclusion(self, file_path: str, seal: Dict) -> Optional[MerkleProof]:
        """
        Generate proof that a file is in the sealed vault

        Args:
            file_path: Relative path to file
            seal: Seal data structure

        Returns:
            MerkleProof or None if file not found
        """
        # Find file index in tree
        file_hashes = seal.get("file_hashes", {})
        if file_path not in file_hashes:
            return None

        # Rebuild tree to get proof
        self.scan_vault()

        # Find leaf index
        sorted_files = sorted(file_hashes.keys())
        leaf_index = sorted_files.index(file_path)

        # Generate proof
        proof_path = self.merkle_tree.generate_proof(leaf_index)

        return MerkleProof(
            file_path=file_path,
            file_hash=file_hashes[file_path],
            proof_path=proof_path,
            merkle_root=seal["merkle_root"],
            timestamp=seal["timestamp"]
        )


# Example usage
if __name__ == "__main__":
    # Example: Validate vault_999
    vault_path = Path("vault_999")
    validator = VaultMerkleValidator(vault_path)

    # Create seal
    seal = validator.create_seal(
        version="v50.0.0",
        floors_validated={
            "F1": "PASS",
            "F2": "PASS",
            "F4": "PASS",
            "F6": "PASS"
        }
    )

    print(f"Created seal for {seal['file_count']} files")
    print(f"Merkle root: {seal['merkle_root']}")

    # Verify seal
    is_valid = validator.verify_seal(seal)
    print(f"Seal valid: {is_valid}")
