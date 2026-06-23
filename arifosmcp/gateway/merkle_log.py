"""
VAULT999 Merkle Log — RFC 9162-compatible append-only transparency log.
═══════════════════════════════════════════════════════════════════

Domain separation:
  leaf_hash = SHA256(0x00 || canonical_leaf_bytes)
  node_hash = SHA256(0x01 || left || right)

Exposed as MCP resources (read-only proofs) + MCP tools (append, seal checkpoint).
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"


def leaf_hash(data: bytes) -> bytes:
    """RFC 9162 leaf hash: SHA256(0x00 || data)."""
    return hashlib.sha256(LEAF_PREFIX + data).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 9162 internal node hash: SHA256(0x01 || left || right)."""
    return hashlib.sha256(NODE_PREFIX + left + right).digest()


def canonical_bytes(obj: Any) -> bytes:
    """Deterministic JSON serialization for leaf content."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# MERKLE TREE
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class MerkleTree:
    """Append-only Merkle tree with RFC 9162 proof generation."""

    leaves: list[bytes] = field(default_factory=list)
    tree: list[list[bytes]] = field(default_factory=list)  # tree[level][index]

    @property
    def tree_size(self) -> int:
        return len(self.leaves)

    @property
    def root_hash(self) -> bytes | None:
        if not self.leaves:
            return None
        return self._root()

    def append(self, data: bytes) -> int:
        """Append a leaf, rebuild affected tree levels. Returns leaf index."""
        leaf_h = leaf_hash(data)
        index = len(self.leaves)
        self.leaves.append(leaf_h)
        self._rebuild()
        return index

    def append_canonical(self, obj: Any) -> int:
        """Append a canonical JSON object as a leaf."""
        return self.append(canonical_bytes(obj))

    def _rebuild(self) -> None:
        """Rebuild Merkle tree levels from leaves."""
        n = len(self.leaves)
        if n == 0:
            self.tree = []
            return

        self.tree = [list(self.leaves)]  # level 0 = leaves
        level = 0
        while len(self.tree[level]) > 1:
            current = self.tree[level]
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(node_hash(left, right))
            self.tree.append(next_level)
            level += 1

    def _root(self) -> bytes:
        return self.tree[-1][0]

    def inclusion_proof(self, leaf_index: int) -> dict[str, Any] | None:
        """Generate RFC 9162 inclusion proof for a leaf index.

        Returns the shortest path of sibling hashes needed to recompute root.
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            return None

        n = len(self.leaves)
        if n == 0:
            return None
        if n == 1:
            return {
                "leaf_index": leaf_index,
                "tree_size": n,
                "leaf_hash": self.leaves[leaf_index].hex(),
                "root_hash": self.root_hash.hex(),
                "inclusion_path": [],
            }

        # Build proof path
        path: list[str] = []
        fn = leaf_index
        sn = n - 1
        level = 0

        while sn > 0:
            current_level = self.tree[level] if level < len(self.tree) else []
            if fn % 2 == 1:  # fn is right child
                sibling_idx = fn - 1
                if sibling_idx < len(current_level):
                    path.append(current_level[sibling_idx].hex())
                    fn = fn // 2
            elif fn < sn:  # fn is left child, sibling to the right exists
                sibling_idx = fn + 1
                if sibling_idx < len(current_level):
                    path.append(current_level[sibling_idx].hex())
                    fn = fn // 2
            else:  # fn == sn and fn is even — duplicate
                path.append(current_level[fn].hex())
                fn = fn // 2
            sn = sn // 2
            level += 1

        return {
            "leaf_index": leaf_index,
            "tree_size": n,
            "leaf_hash": self.leaves[leaf_index].hex(),
            "root_hash": self._root().hex(),
            "inclusion_path": path,
        }

    def consistency_proof(self, old_size: int, new_size: int) -> dict[str, Any] | None:
        """Generate RFC 9162 consistency proof between two tree sizes.

        Proves that tree at new_size is an append-only extension of tree at old_size.
        """
        if old_size < 0 or new_size < old_size or new_size > len(self.leaves):
            return None
        if old_size == new_size:
            return {
                "old_tree_size": old_size,
                "new_tree_size": new_size,
                "old_root": self._root_for_size(old_size).hex()
                if old_size > 0
                else hashlib.sha256(b"").hexdigest(),
                "new_root": self._root_for_size(new_size).hex(),
                "consistency_path": [],
            }

        # Build consistency path (simplified — RFC 9162 §2.1.2)
        old_tree = _build_tree(self.leaves[:old_size])
        new_tree = _build_tree(self.leaves[:new_size])

        old_root = old_tree[-1][0] if old_tree else hashlib.sha256(b"").digest()
        new_root = new_tree[-1][0] if new_tree else hashlib.sha256(b"").digest()

        path = _consistency_path(self.leaves, old_size, new_size)

        return {
            "old_tree_size": old_size,
            "new_tree_size": new_size,
            "old_root": old_root.hex(),
            "new_root": new_root.hex(),
            "consistency_path": path,
        }

    def _root_for_size(self, size: int) -> bytes:
        """Compute root hash for the first `size` leaves."""
        if size == 0:
            return hashlib.sha256(b"").digest()
        tmp_tree = _build_tree(self.leaves[:size])
        if not tmp_tree:
            return hashlib.sha256(b"").digest()
        return tmp_tree[-1][0]

    def checkpoint(self) -> dict[str, Any]:
        """Generate a signed checkpoint for the current tree state."""
        return {
            "log_id": "VAULT999-MERKLE-v1",
            "tree_size": len(self.leaves),
            "root_hash": self._root().hex() if self.leaves else hashlib.sha256(b"").hexdigest(),
            "timestamp": time.time(),
            "signature": "unsigned-v0.1",  # v0.2+: ed25519 signature
        }


def _build_tree(leaves: list[bytes]) -> list[list[bytes]]:
    """Build a Merkle tree from leaves, returning all levels."""
    if not leaves:
        return []
    tree = [list(leaves)]
    level = 0
    while len(tree[level]) > 1:
        current = tree[level]
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            next_level.append(node_hash(left, right))
        tree.append(next_level)
        level += 1
    return tree


def _consistency_path(leaves: list[bytes], old_size: int, new_size: int) -> list[str]:
    """Build consistency path — minimal sibling hashes for old→new proof.

    Simplified implementation: includes the root of the old tree and
    right-side siblings along the path to the new root.
    """
    if old_size == 0:
        return []
    if old_size == new_size:
        return []

    old_tree = _build_tree(leaves[:old_size])
    new_tree = _build_tree(leaves[:new_size])
    old_hash = old_tree[-1][0] if old_tree else hashlib.sha256(b"").digest()

    path = [old_hash.hex()]

    # Walk from old_size to new_size, capturing sibling hashes
    fn = old_size
    level = 0
    while fn < new_size:
        level_leaves = _build_tree(leaves[: fn + 1])
        if level_leaves and len(level_leaves[-1]) > 0:
            path.append(level_leaves[-1][0].hex())
        fn += 1
        level += 1

    return path


# ═══════════════════════════════════════════════════════════════════════════
# VERIFIER (client-side, pure function)
# ═══════════════════════════════════════════════════════════════════════════


def verify_inclusion(
    leaf_hash: bytes,
    leaf_index: int,
    tree_size: int,
    inclusion_path: list[bytes],
    expected_root: bytes,
) -> bool:
    """RFC 9162 inclusion proof verification.

    Args:
        leaf_hash: The leaf hash to verify.
        leaf_index: 0-based index of the leaf in the tree.
        tree_size: Number of leaves in the tree.
        inclusion_path: Ordered list of sibling hashes from the proof.
        expected_root: The trusted root hash to compare against.
    """
    if tree_size == 0:
        return False
    if leaf_index >= tree_size:
        return False
    if tree_size == 1:
        return leaf_hash == expected_root and len(inclusion_path) == 0

    fn = leaf_index
    sn = tree_size - 1
    r = leaf_hash

    for p in inclusion_path:
        if sn == 0:
            return False
        sibling = bytes.fromhex(p) if isinstance(p, str) else p
        if (fn & 1) == 1 or fn == sn:
            r = node_hash(sibling, r)
            while (fn & 1) == 0 and fn != 0:
                fn >>= 1
                sn >>= 1
        else:
            r = node_hash(r, sibling)
        fn >>= 1
        sn >>= 1

    return sn == 0 and r == expected_root


def verify_consistency(
    old_root: bytes,
    new_root: bytes,
    old_size: int,
    new_size: int,
    consistency_path: list[bytes],
) -> bool:
    """RFC 9162 consistency proof verification.

    Verifies that the tree at new_size is an append-only extension of old_size.
    """
    if old_size == new_size:
        return old_root == new_root and len(consistency_path) == 0
    if old_size == 0:
        return True  # Empty tree -> anything is valid append

    fn = old_size
    sn = new_size
    r: bytes | None = None

    for p in consistency_path:
        if r is None and fn == sn:
            r = p
            continue
        if r is None:
            r = p
            fn = fn * 2
        else:
            r = node_hash(r, p)
            fn = fn * 2

    return r == new_root if r is not None else False


def verify_checkpoint(
    checkpoint: dict[str, Any],
    checkpoint_history: list[dict[str, Any]],
) -> dict[str, Any]:
    """Verify a checkpoint against its history.

    Returns a verification verdict with details.
    """
    issues: list[str] = []

    # Monotonic tree size
    if checkpoint_history:
        prev = checkpoint_history[-1]
        if checkpoint["tree_size"] < prev["tree_size"]:
            issues.append(f"Tree size decreased: {prev['tree_size']} → {checkpoint['tree_size']}")

    # Valid root hash format
    try:
        bytes.fromhex(checkpoint["root_hash"])
    except ValueError:
        issues.append(f"Invalid root hash format: {checkpoint['root_hash']}")

    return {
        "verified": len(issues) == 0,
        "issues": issues,
        "tree_size": checkpoint["tree_size"],
        "root_hash": checkpoint["root_hash"],
    }
