"""
MCP Memory Tools (Phase 3)

Provides constitutional read access to the ZKPC Vault.
Replaces legacy stub memory tools.
"""

from typing import Any, Dict, List

from arifos.memory.vault.vault_manager import VaultManager


def memory_get_receipts(request: Dict[str, Any]) -> str:
    """
    Retrieve recent Constitutional Receipts from the ZKPC Vault.

    Args:
        request: { "limit": int (optional, default 10) }

    Returns:
        JSON string of receipts.
    """
    limit = request.get("limit", 10)

    try:
        vault = VaultManager()
        receipts = vault.get_receipts(limit=limit)

        # Format for readability
        import json
        return json.dumps(receipts, indent=2)
    except Exception as e:
        return f"Error retrieving receipts: {str(e)}"


def memory_verify_seal(request: Dict[str, Any]) -> str:
    """
    Verify if a specific action hash exists in the constitutional ledger.

    Args:
        request: { "action_hash": str }

    Returns:
        Verification status string.
    """
    target_hash = request.get("action_hash")
    if not target_hash:
        return "Error: action_hash is required"

    try:
        vault = VaultManager()
        # Scan receipts (this assumes reasonable volume, optimization needed for large vaults)
        # Leveraging get_receipts with large limit for now
        receipts = vault.get_receipts(limit=1000)

        found = next((r for r in receipts if r.get("action_hash") == target_hash), None)

        if found:
            return f"VERIFIED: Seal found.\nTimestamp: {found.get('timestamp')}\nStatus: {found.get('constitutional_validity')}"
        else:
            return "NOT FOUND: Seal hash not present in active ledger."

    except Exception as e:
        return f"Error verifying seal: {str(e)}"
