#!/usr/bin/env python3
"""
Initialize cooling ledger with genesis hash.

This script generates the genesis hash for arifOS deployment
and creates the initial cooling ledger structure.

Authority: Muhammad Arif bin Fazil
Version: v52.5.1-SEAL
"""

import hashlib
import json
import time
from pathlib import Path

def generate_genesis_hash():
    """Generate cryptographic genesis hash."""
    genesis_data = f"arifOS_v52.5.1_genesis_{int(time.time())}"
    genesis_hash = hashlib.sha256(genesis_data.encode()).hexdigest()
    return genesis_hash


def initialize_cooling_ledger(genesis_hash: str):
    """Initialize the cooling ledger structure."""
    cooling_ledger = {
        "version": "v52.5.1",
        "genesis_hash": genesis_hash,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "motto": "DITEMPA BUKAN DIBERI - Forged, Not Given",
        "description": "Constitutional cooling ledger for user governance state",
        "users": {
            "default": {
                "cooling_tier": 0,
                "void_count_30d": 0,
                "last_void_verdict": None,
                "threshold_adjustments": {},
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        },
        "cooling_tiers": {
            "0": {
                "description": "Default tier - no violations",
                "threshold_adjustments": {}
            },
            "1": {
                "description": "Tier 1 - Minor violations (42h cooling)",
                "hours": 42,
                "threshold_adjustments": {}
            },
            "2": {
                "description": "Tier 2 - Standard violations (72h cooling)",
                "hours": 72,
                "threshold_adjustments": {}
            },
            "3": {
                "description": "Tier 3 - Critical violations (168h cooling)",
                "hours": 168,
                "threshold_adjustments": {}
            }
        }
    }
    return cooling_ledger


def main():
    """Main entry point."""
    print("=" * 50)
    print("arifOS v52.5.1 Genesis Hash Generation")
    print("=" * 50)
    
    # Generate genesis hash
    genesis_hash = generate_genesis_hash()
    
    print(f"\n✅ Genesis Hash Generated:")
    print(f"   {genesis_hash}")
    print(f"\nSet in Railway environment variables:")
    print(f"   ARIFOS_GENESIS_HASH={genesis_hash}")
    
    # Initialize cooling ledger
    cooling_ledger = initialize_cooling_ledger(genesis_hash)
    
    # Ensure VAULT999 directory exists
    vault_dir = Path(__file__).parent.parent / "VAULT999"
    vault_dir.mkdir(exist_ok=True)
    
    # Write cooling ledger
    output_path = vault_dir / "cooling_ledger.json"
    with open(output_path, "w") as f:
        json.dump(cooling_ledger, f, indent=2)
    
    print(f"\n✅ Cooling ledger initialized:")
    print(f"   {output_path}")
    print(f"   Users: {len(cooling_ledger['users'])}")
    print(f"   Tiers: {len(cooling_ledger['cooling_tiers'])}")
    
    print("\n" + "=" * 50)
    print("Initialization Complete")
    print("=" * 50)


if __name__ == "__main__":
    main()
