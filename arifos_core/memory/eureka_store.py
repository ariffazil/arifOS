"""
eureka_store.py — Phase 1 EUREKA Memory Store (v38.3Omega)

Append-only storage implementations:
- InMemoryStore: For tests
- AppendOnlyJSONLStore: For production (file-based)

No database dependencies. Pure append semantics.

Author: arifOS Project
Version: v38.3 Phase 1
"""

from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List
from .eureka_types import MemoryBand, MemoryWriteDecision, MemoryWriteRequest


class AppendOnlyJSONLStore:
    """
    File-based append-only store using JSONL format.
    
    One file per band: vault_999/ledger/{band}.jsonl
    """
    
    def __init__(self, base_dir: str = "vault_999/ledger") -> None:
        """
        Initialize store with base directory.
        
        Args:
            base_dir: Base directory for JSONL files
        """
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def append(
        self, 
        band: MemoryBand, 
        req: MemoryWriteRequest, 
        decision: MemoryWriteDecision
    ) -> Path:
        """
        Append a write record to the appropriate band file.
        
        Args:
            band: Target memory band
            req: Original write request
            decision: Routing decision
            
        Returns:
            Path to the file that was appended to
        """
        path = self.base / f"{band.value.lower()}.jsonl"
        record: Dict[str, Any] = {
            "band": band.value,
            "decision": asdict(decision),
            "request": asdict(req),
        }
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return path


class InMemoryStore:
    """
    In-memory store for testing.
    
    Stores records in a list. No persistence.
    """
    
    def __init__(self) -> None:
        """Initialize empty record list."""
        self.records: List[Dict[str, Any]] = []

    def append(
        self, 
        band: MemoryBand, 
        req: MemoryWriteRequest, 
        decision: MemoryWriteDecision
    ) -> None:
        """
        Append a write record to in-memory list.
        
        Args:
            band: Target memory band
            req: Original write request
            decision: Routing decision
        """
        self.records.append({
            "band": band.value, 
            "decision": decision, 
            "request": req
        })
    
    def get_records(self) -> List[Dict[str, Any]]:
        """Get all stored records."""
        return list(self.records)
    
    def clear(self) -> None:
        """Clear all records."""
        self.records.clear()


__all__ = ["AppendOnlyJSONLStore", "InMemoryStore"]
