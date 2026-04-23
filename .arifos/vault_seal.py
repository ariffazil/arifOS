#!/usr/bin/env python3
"""
VAULT Seal — arifOS Autoresearch
Seals experiment results to VAULT999 using Merkle chain.

Usage:
    python vault_seal.py --input=/tmp/experiment.json
"""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

VAULT999 = Path("/root/arifOS/VAULT999")


def get_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def compute_merkle_leaf(data: dict) -> str:
    content = json.dumps(data, sort_keys=True)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def compute_merkle_root(leaves: list) -> str:
    if not leaves:
        return "0" * 64
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])
        new_level = []
        for i in range(0, len(leaves), 2):
            combined = leaves[i] + leaves[i + 1]
            new_level.append(hashlib.sha256(combined.encode()).hexdigest()[:16])
        leaves = new_level
    return leaves[0]


def load_chain() -> dict:
    chain_file = VAULT999 / "SEAL_CHAIN.txt"
    if not chain_file.exists():
        return {"seal": "GENESIS", "depth": 0, "root": "0" * 64}
    with open(chain_file) as f:
        return json.loads(f.read())


def save_chain(chain: dict):
    VAULT999.mkdir(exist_ok=True)
    chain_file = VAULT999 / "SEAL_CHAIN.txt"
    with open(chain_file, "w") as f:
        f.write(json.dumps(chain, indent=2))


def seal_experiment(experiment: dict) -> dict:
    VAULT999.mkdir(exist_ok=True)

    leaf = compute_merkle_leaf(experiment)
    chain = load_chain()

    new_depth = chain["depth"] + 1
    new_root = compute_merkle_root([chain["root"], leaf])

    new_chain = {
        "seal": f"{new_root[:8]}",
        "depth": new_depth,
        "root": new_root,
        "timestamp": get_timestamp(),
        "prev_seal": chain["seal"],
        "leaf": leaf,
    }

    save_chain(new_chain)

    exp_file = VAULT999 / "SEALED_EXPERIMENTS.jsonl"
    with open(exp_file, "a") as f:
        f.write(json.dumps({"experiment": experiment, "seal": new_chain}) + "\n")

    return new_chain


def verify_seal(experiment_index: int = None) -> dict:
    exp_file = VAULT999 / "SEALED_EXPERIMENTS.jsonl"
    if not exp_file.exists():
        return {"valid": False, "reason": "No sealed experiments found"}

    chain = load_chain()

    return {
        "valid": True,
        "seal": chain["seal"],
        "depth": chain["depth"],
        "root": chain["root"],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="VAULT Seal — arifOS")
    parser.add_argument("--input", help="Experiment JSON to seal")
    parser.add_argument("--verify", action="store_true", help="Verify seal")
    parser.add_argument("--index", type=int, help="Verify specific experiment")
    args = parser.parse_args()

    if args.verify:
        result = verify_seal(args.index)
        print(json.dumps(result, indent=2))
        return 0

    if not args.input:
        print("❌ --input required")
        return 1

    with open(args.input) as f:
        experiment = json.load(f)

    seal = seal_experiment(experiment)
    print("✅ Sealed experiment")
    print(f"   Seal: {seal['seal']}")
    print(f"   Depth: {seal['depth']}")
    print(f"   Root: {seal['root']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
