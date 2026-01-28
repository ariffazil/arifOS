"""
999 VAULT - Immutable Cooling Ledger (Native v53)
Append-only JSONL ledger for session auditing.
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CoolingLedgerNative:
    """
    Native Immutable Ledger (Cooling).
    Stores Merkle-hashed session verdicts.
    """
    
    def __init__(self, ledger_path: str = ".arifos/ledger.jsonl"):
        self.ledger_path = ledger_path
        self._ensure_ledger_exists()
        
    def _ensure_ledger_exists(self):
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w") as f:
                pass # Create empty file

    def write_entry(self, entry: Dict[str, Any]) -> str:
        """
        Write a new entry to the ledger and return its hash.
        """
        timestamp = datetime.now().isoformat()
        entry["timestamp"] = timestamp
        
        # Compute entry hash (Merkle leaf)
        content = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(content.encode()).hexdigest()
        entry["entry_hash"] = entry_hash
        
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        logger.info(f"[VAULT-999] Sealed entry: {entry_hash[:16]} for session {entry.get('session_id')}")
        return entry_hash

    def read_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Read all entries for a specific session."""
        entries = []
        if not os.path.exists(self.ledger_path):
            return entries
            
        with open(self.ledger_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("session_id") == session_id:
                    entries.append(entry)
        return entries
