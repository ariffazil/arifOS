"""
arifosmcp/runtime/wisdom_sea_lion.py — DEPRECATED / QUARANTINED

This module is QUARANTINED as of the Meaning Witness v2 rebuild.

generate_nusantara_wisdom() asks the LLM to *generate* quotes, which violates
the arifOS doctrine that SEA-LION may only *interpret* approved quotes from
the locked ledger.

The canonical replacement is:
  arifosmcp/runtime/sea_lion_interpreter.py  —  interpret_with_sea_lion()

Do not use generate_nusantara_wisdom() in new code.
It is retained only to avoid breaking legacy callers; it returns an error.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# --- Configuration ---
API_KEY = os.getenv("SEA_LION_API_KEY")
BASE_URL = os.getenv("SEA_LION_BASE_URL", "https://api.sea-lion.ai/v1")
MODEL = "aisingapore/Qwen-SEA-LION-v4-32B-IT"

async def generate_nusantara_wisdom(
    context: str, 
    agent_intent: str | None = None
) -> dict[str, Any]:
    """
    DEPRECATED — Do not use.

    This function previously asked SEA-LION to *generate* quotes, which violates
    arifOS Meaning Witness doctrine. Use sea_lion_interpreter.interpret_with_sea_lion()
    instead.
    """
    logger.warning(
        "generate_nusantara_wisdom() is QUARANTINED. "
        "Use arifosmcp.runtime.sea_lion_interpreter.interpret_with_sea_lion() instead."
    )
    return {
        "error": "QUARANTINED: generate_nusantara_wisdom() is deprecated. "
                 "SEA-LION may not generate quotes. Use interpret_with_sea_lion() with approved candidates.",
        "status": "888-HOLD",
        "floor": "F02_TRUTH",
    }

if __name__ == "__main__":
    # Quick test
    import asyncio
    res = asyncio.run(generate_nusantara_wisdom("arif_vault_seal", "Hardening the Merkle trail"))
    print(json.dumps(res, indent=2))
