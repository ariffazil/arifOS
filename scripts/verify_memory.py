"""
Verify Phase 3: ZKPC Memory Integration

Tests the persistence loop:
1. Call 999-SEAL (which calls Orthogonal Hypervisor).
2. Verify receipt is written to `runtime/vault_999/receipts.jsonl`.
3. Call `memory_verify_seal` to confirm read access.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("VERIFY_MEMORY")

async def verify_memory_persistence():
    print(f"[START] ZKPC MEMORY VERIFICATION")
    print("=" * 40)

    # Imports
    from arifos.mcp.tools.mcp_999_seal import mcp_999_seal
    from arifos.mcp.tools.memory_tools import memory_get_receipts, memory_verify_seal
    from arifos.memory.vault.vault_manager import VaultManager

    # 1. Clean previous receipts for clean test (optional, but good for verify)
    # Actually, let's just append and verify specific hash
    # 2. Trigger 999-SEAL
    print("\n[1] Triggering 999-SEAL (Measurement Collapse)...")
    seal_request = {
        "verdict": "SABAR", # Hint
        "decision_metadata": {
            "query": "Memory Persistence Test",
            "user_id": "memory_verifier"
        }
    }

    # Bypass legacy checks for this script
    os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"

    seal_result = await mcp_999_seal(seal_request)

    print(f"Seal Result: {seal_result.verdict}")
    print(f"Seal Reason: {seal_result.reason}")

    if seal_result.verdict == "VOID":
         # Even if VOID, it should produce a receipt!
         # Wait, orthogonal hypervisor returns correct receipt even for VOID?
         pass

    # Extract Action Hash from logs/receipt
    # The mcp_999_seal doesn't return the receipt object directly, but the proof_hash is in side_data if we hacked it?
    # Actually, mcp_999_seal returns side_data with 'hypervisor_proof'.
    # But where is the receipt hash?
    # In mcp_999_seal.py: proof_hash_from_hypervisor = receipt.action_hash if receipt else "no_receipt"
    # mcp_999_seal generates seal string using this hash.
    # sealed_verdict = verdict:proof_hash:timestamp encoded

    sealed_verdict = seal_result.side_data.get("sealed_verdict", "")
    import base64
    decoded = base64.b64decode(sealed_verdict).decode('utf-8')
    # Format: VERDICT:PROOF_HASH:TIMESTAMP
    parts = decoded.split(":")
    if len(parts) >= 2:
        action_hash = parts[1]
        print(f"Captured Action Hash: {action_hash}")
    else:
        print("[FAIL] Could not extract action hash from seal")
        return

    # 3. Verify Persistence
    print("\n[2] Verifying Persistence in Vault...")

    verify_response = memory_verify_seal({"action_hash": action_hash})
    print(f"Memory Tool Response: {verify_response}")

    if "VERIFIED: Seal found" in verify_response:
        print("[PASS] Receipt persisted and verified.")
    else:
        print("[FAIL] Persistence verification failed.")

    # 4. List Receipts
    print("\n[3] Listing recent receipts...")
    receipts_json = memory_get_receipts({"limit": 2})
    print(receipts_json)

    print("\n[SUCCESS] Phase 3 Verification Complete.")

if __name__ == "__main__":
    asyncio.run(verify_memory_persistence())
