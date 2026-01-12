#!/usr/bin/env python3
"""
zkpc_seal.py - Generate ZKPC Pre-Commitment Seal for arifOS v46.1

This script performs the "Pre-Commitment" step of the ZKPC Protocol.
It walks the L1_THEORY/canon and L2_PROTOCOLS/v46 directories,
calculates SHA-256 hashes of all authoritative files, and binds them
into a single "Constitution Root Hash".

Output:
    L1_THEORY/canon/999_vault/CONSTITUTIONAL_SEAL_v46.1.json
"""

import datetime
import hashlib
import json
import os
from pathlib import Path


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        # Read in chunks to handle large files efficiently
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def walk_and_hash(root_dir: Path, base_path: Path) -> dict:
    """Recursively walk directory and hash files, returning a dict tree."""
    tree = {}

    # Sort for deterministic output
    items = sorted(os.listdir(root_dir))

    for item in items:
        item_path = root_dir / item

        # Skip hidden files and non-essential directories
        if item.startswith('.') or item == "__pycache__":
            continue

        if item_path.is_dir():
            # Recursive call
            subtree = walk_and_hash(item_path, base_path)
            if subtree:  # Only add if not empty
                tree[item] = subtree
        elif item_path.is_file():
            # Calculate hash
            relative_path = item_path.relative_to(base_path).as_posix()
            file_hash = calculate_file_hash(item_path)
            tree[item] = {
                "hash": file_hash,
                "path": relative_path,
                "size": item_path.stat().st_size
            }

    return tree

def flatten_hashes(tree: dict) -> list:
    """Flatten the tree into a list of (path, hash) tuples for root calculation."""
    flat = []
    for key, value in tree.items():
        if "hash" in value:
            flat.append((value["path"], value["hash"]))
        else:
            flat.extend(flatten_hashes(value))
    return flat

def main():
    repo_root = Path.cwd()

    # Define authoritative directories
    canon_dir = repo_root / "L1_THEORY" / "canon"
    protocols_dir = repo_root / "L2_PROTOCOLS" / "v46"

    print(f"🔒 Initiating ZKPC Seal Generator...")
    print(f"   Repo Root: {repo_root}")
    print(f"   Canon:     {canon_dir}")
    print(f"   Protocols: {protocols_dir}")

    # 1. Digest Canon
    print("\n📜 Digesting L1 Canon...")
    canon_tree = walk_and_hash(canon_dir, repo_root)

    # 2. Digest Protocols
    print("🤖 Digesting L2 Protocols...")
    protocols_tree = walk_and_hash(protocols_dir, repo_root)

    # 3. Calculate Roots
    canon_flat = sorted(flatten_hashes(canon_tree))
    protocols_flat = sorted(flatten_hashes(protocols_tree))

    # Simple Merkle-like root: Hash of all sorted (path+hash) strings
    canon_manifest = "".join([f"{p}{h}" for p, h in canon_flat])
    canon_root = hashlib.sha256(canon_manifest.encode()).hexdigest()

    protocols_manifest = "".join([f"{p}{h}" for p, h in protocols_flat])
    protocols_root = hashlib.sha256(protocols_manifest.encode()).hexdigest()

    # 4. Master Seal
    master_manifest = f"CANON:{canon_root}|PROTOCOLS:{protocols_root}"
    master_seal = hashlib.sha256(master_manifest.encode()).hexdigest()

    seal_data = {
        "meta": {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "generator": "zkpc_seal.py",
            "version": "v46.1",
            "type": "ZKPC_PRE_COMMITMENT"
        },
        "roots": {
            "master_seal": master_seal,
            "canon_root": canon_root,
            "protocols_root": protocols_root
        },
        "counts": {
            "canon_files": len(canon_flat),
            "protocols_files": len(protocols_flat)
        },
        "content_map": {
            "L1_THEORY/canon": canon_tree,
            "L2_PROTOCOLS/v46": protocols_tree
        }
    }

    # 5. Write to Vault
    vault_path = canon_dir / "999_vault"
    output_path = vault_path / "CONSTITUTIONAL_SEAL_v46.1.json"

    # Ensure vault exists
    os.makedirs(vault_path, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(seal_data, f, indent=2)

    print("\n" + "="*60)
    print("✅ ZKPC CONSTITUTIONAL SEAL FORGED")
    print("="*60)
    print(f"Master Seal: {master_seal}")
    print(f"Canon Root:  {canon_root}")
    print(f"Proto Root:  {protocols_root}")
    print(f"Output File: {output_path}")
    print("="*60)

if __name__ == "__main__":
    main()
