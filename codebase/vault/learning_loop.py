"""
canonical_core/vault/learning_loop.py — Learning Loop

Extracts patterns from the ledger to improve the next session.
"""

import json
import logging
import os
from typing import Dict, Any, List

logger = logging.getLogger("LEARNING_LOOP")

class VaultLearningLoop:
    """
    Extracts wisdom from the sealed vault.
    Updates baseline Omega_0 (Humility) for next session.
    """
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.vault_file = os.path.join(storage_path, "vault.jsonl")
        
    def process_session(self, session_result: Dict[str, Any]):
        """
        Analyze a just-sealed session.
        In a real system, this would trigger an async job to update models.
        """
        logger.info(f"Learning from session {session_result.get('session_id')}...")
        # Simulating pattern extraction
        # e.g., if many sessions are VOID due to F12, tighten injection filter
        pass
        
    def get_baseline_context(self) -> Dict[str, Any]:
        """
        Get learned context for 000 INIT.
        
        Returns:
            Dict containing updated humility bands, floor weights, etc.
        """
        # Analyze last N entries to determine entropy basin
        try:
            entries = self._read_last_entries(10)
            if not entries:
                return {"omega_0_band": [0.03, 0.05]} # Default
                
            # Simple heuristic: If last 3 were SEAL, we are in a "Stable Basin"
            # If last 3 were VOID, we are in a "Turbulent Basin"
            last_3_verdicts = [e.get("verdict") for e in entries[-3:]]
            
            if all(v == "SEAL" for v in last_3_verdicts):
                # High confidence, lower uncertainty floor? Or keep it healthy?
                # "Stable Basin"
                return {"omega_0_band": [0.02, 0.04], "basin": "STABLE"}
            elif "VOID" in last_3_verdicts:
                # "Turbulent Basin" - increase humility
                return {"omega_0_band": [0.05, 0.08], "basin": "TURBULENT"}
            else:
                return {"omega_0_band": [0.03, 0.05], "basin": "NORMAL"}
                
        except Exception as e:
            logger.warning(f"Error reading vault for learning: {e}")
            return {"omega_0_band": [0.03, 0.05]}

    def _read_last_entries(self, n: int) -> List[Dict[str, Any]]:
        """Read last N entries from JSONL."""
        if not os.path.exists(self.vault_file):
            return []
            
        # Inefficient for large files, but fine for prototype
        try:
            with open(self.vault_file, "r") as f:
                lines = f.readlines()
                return [json.loads(line) for line in lines[-n:]]
        except Exception:
            return []