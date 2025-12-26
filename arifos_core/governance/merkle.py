# arifos_core/merkle.py
"""
Merkle tree utilities for Cooling Ledger / zkPC (v36Ω).

- Uses SHA-256 hex hashes for leaves and internal nodes.
- Works with the `sha256_hex` helper from ledger_hashing.py.
- Designed for:
    - computing a Merkle root over ledger entries,
    - generating membership proofs,
    - verifying proofs.

This is v0.1 (non-zk). It is Merkle/zkPC-ready for future zk integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Iterable, Optional

from arifos_core.governance.ledger_hashing import sha256_hex


@dataclass
class MerkleProofItem:
    """
    A single step in a Merkle proof.

    - sibling: the sibling hash at this level
    - position: 'left' or 'right' relative to the current hash
    """
    sibling: str
    position: str  # 'left' or 'right'


@dataclass
class MerkleTree:
    """
    Merkle tree represented as levels of hashes.

    levels[0] = leaves (list of hex strings)
    levels[-1][0] = root hash (if there is at least one leaf)
    """
    levels: List[List[str]]

    @property
    def root(self) -> Optional[str]:
        if not self.levels:
            return None
        if not self.levels[-1]:
            return None
        return self.levels[-1][0]


def _pair_hash(left: str, right: str) -> str:
    """
    Hash a pair of hex strings by concatenating them and applying SHA-256.

    Note: this is a simple concatenation; we do not double-hash.
    """
    return sha256_hex(left + right)


def build_merkle_tree(leaves: Iterable[str]) -> MerkleTree:
    """
    Build a Merkle tree from a list/iterable of leaf hashes (hex-encoded).

    If there are no leaves, the tree will have levels = [] and root = None.
    If there is one leaf, the root = that leaf.
    For odd numbers of nodes at a level, the last node is duplicated (Bitcoin-style).
    """
    current_level = list(leaves)
    if not current_level:
        return MerkleTree(levels=[])

    levels: List[List[str]] = [current_level]

    while len(current_level) > 1:
        next_level: List[str] = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            if i + 1 < len(current_level):
                right = current_level[i + 1]
            else:
                # Duplicate last element if odd number of nodes
                right = left
            parent = _pair_hash(left, right)
            next_level.append(parent)
        levels.append(next_level)
        current_level = next_level

    return MerkleTree(levels=levels)


def get_merkle_proof(tree: MerkleTree, leaf_index: int) -> List[MerkleProofItem]:
    """
    Generate a Merkle membership proof for a given leaf index.

    Assumes:
    - tree.levels[0] is the leaf level.
    - 0 <= leaf_index < len(tree.levels[0])

    Returns:
        A list of MerkleProofItem from leaf level up to (but not including) the root.

    If the tree has 0 or 1 leaf, the proof will be empty.
    """
    if not tree.levels:
        raise ValueError("Cannot generate proof for empty Merkle tree")

    if leaf_index < 0 or leaf_index >= len(tree.levels[0]):
        raise IndexError(f"Leaf index {leaf_index} out of range")

    proof: List[MerkleProofItem] = []
    index = leaf_index

    for level_idx in range(0, len(tree.levels) - 1):
        level = tree.levels[level_idx]
        # Determine sibling index
        if index % 2 == 0:
            # even index: sibling is index + 1 if exists, else duplicate
            sibling_index = index + 1
            position = "right"  # sibling is on the right
        else:
            # odd index: sibling is index - 1
            sibling_index = index - 1
            position = "left"  # sibling is on the left

        if sibling_index >= len(level):
            sibling_index = index  # duplicate last

        sibling_hash = level[sibling_index]
        proof.append(MerkleProofItem(sibling=sibling_hash, position=position))

        # Move to next level index
        index //= 2

    return proof


def verify_merkle_proof(
    leaf_hash: str,
    proof: List[MerkleProofItem],
    root: str,
) -> bool:
    """
    Verify a Merkle membership proof.

    - leaf_hash: hex-encoded SHA-256 hash for the leaf.
    - proof: list of MerkleProofItem as returned by get_merkle_proof.
    - root: expected Merkle root (hex).

    Returns:
        True if proof is valid and leads to `root`, False otherwise.
    """
    computed = leaf_hash
    for item in proof:
        if item.position == "right":
            # sibling is on the right: H(computed + sibling)
            computed = _pair_hash(computed, item.sibling)
        elif item.position == "left":
            # sibling is on the left: H(sibling + computed)
            computed = _pair_hash(item.sibling, computed)
        else:
            raise ValueError(f"Invalid proof position: {item.position}")

    return computed == root
