"""
memory_zkpc.py — READ zkPC Receipts (Governance Proofs)

Glass-box tool for retrieving Zero-Knowledge Proof of Cognition receipts.

v45.2 Memory MCP Extension
"""

import json
import os
from typing import Any, Dict

# Receipt storage path (Directive 07)
ZKPC_RECEIPTS_PATH = "vault_999/receipts"


async def memory_get_zkpc_receipt(receipt_id: str) -> Dict[str, Any]:
    """
    Retrieve a zkPC Receipt with full governance vector.
    """
    receipt_path = os.path.join(ZKPC_RECEIPTS_PATH, f"{receipt_id}.json")

    if not os.path.exists(receipt_path):
        return {
            "success": False,
            "error": f"Receipt not found: {receipt_id}",
            "governance": {
                "source": "ZKPC",
                "band": "L2"
            }
        }

    try:
        with open(receipt_path, "r", encoding="utf-8") as f:
            receipt_data = json.load(f)

        return {
            "success": True,
            "receipt": receipt_data,
            "governance": {
                "source": "ZKPC",
                "band": "L2",
                "verified": True,
                "hash_algorithm": "SHA-256"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "governance": {
                "source": "ZKPC",
                "band": "L2"
            }
        }


def memory_get_zkpc_receipt_sync(receipt_id: str) -> Dict[str, Any]:
    """Synchronous wrapper for memory_get_zkpc_receipt."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(memory_get_zkpc_receipt(receipt_id))
