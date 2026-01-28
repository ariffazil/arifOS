"""
Stage 999: Seal - Final immutable audit.
"""

import logging
from typing import Any, Dict
from codebase.vault.ledger_native import CoolingLedgerNative
from codebase.bundle_store import get_store

logger = logging.getLogger(__name__)

async def execute_seal_stage(session_id: str) -> Dict[str, Any]:
    """
    Metabolic Stage 999: Seal.
    Writes the final MergedBundle to the immutable ledger.
    """
    store = get_store(session_id)
    merged = store.get_merged()
    
    if not merged:
        logger.error(f"[STAGE-999] Missing MergedBundle for session {session_id}")
        return {"status": "VOID", "reason": "No bundle to seal"}
        
    ledger = CoolingLedgerNative()
    entry = merged.model_dump() # Full bundle state
    
    entry_hash = ledger.write_entry(entry)
    
    return {
        "stage": "999_seal",
        "status": "SEALED",
        "hash": entry_hash,
        "session_id": session_id
    }
