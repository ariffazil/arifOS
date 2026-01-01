"""
memory_vault.py — READ from Vault-999 (L0 Immutable Canon)

Glass-box tool for retrieving constitutional law entries.
Confidence: 1.0 (Vault is law, not suggestion).

v45.2 Memory MCP Extension
"""

import json
import os
from typing import Any, Dict

# Canonical Vault Path (Directive 07)
VAULT_CANON_PATH = "vault_999/canon"


async def memory_get_vault(path: str) -> Dict[str, Any]:
    """
    Retrieve an entry from Vault-999 (Immutable Canon).

    Args:
        path: Relative path within vault_999/canon/ (e.g., "constitution.json")

    Returns:
        Dict with content and governance metadata.
        Confidence is always 1.0 (Vault is LAW).
    """
    full_path = os.path.join(VAULT_CANON_PATH, path)

    if not os.path.exists(full_path):
        return {
            "success": False,
            "error": f"Entry not found in Vault: {path}",
            "governance": {
                "source": "VAULT",
                "confidence": 0.0
            }
        }

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Attempt JSON parse if applicable
        if path.endswith(".json"):
            content = json.loads(content)

        return {
            "success": True,
            "content": content,
            "governance": {
                "source": "VAULT",
                "confidence": 1.0,  # Vault is LAW
                "band": "L0",
                "path": full_path
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "governance": {
                "source": "VAULT",
                "confidence": 0.0
            }
        }


def memory_get_vault_sync(path: str) -> Dict[str, Any]:
    """Synchronous wrapper for memory_get_vault."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(memory_get_vault(path))
