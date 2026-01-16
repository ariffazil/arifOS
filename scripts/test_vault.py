"""
Test VaultManager Receipt Recording
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from arifos_core.memory.vault.vault_manager import VaultManager


def test_vault_write():
    print("Testing VaultManager Write...")

    # 1. Initialize
    vault = VaultManager()
    print(f"Vault Path: {vault.config.receipts_path.absolute()}")

    # 2. Create Dummy Receipt
    receipt = {
        "test_id": "12345",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action_hash": "TEST_HASH_ABC",
        "verdict": "SEAL"
    }

    # 3. Write
    try:
        vault.record_receipt(receipt)
        print("Write successful.")
    except Exception as e:
        print(f"Write failed: {e}")
        return

    # 4. Read
    print("Testing VaultManager Read...")
    receipts = vault.get_receipts(limit=5)
    print(f"Found {len(receipts)} receipts.")

    found = False
    for r in receipts:
        if r.get("action_hash") == "TEST_HASH_ABC":
            print("Found test receipt!")
            found = True
            break

    if not found:
        print("Test receipt NOT found.")

if __name__ == "__main__":
    test_vault_write()
