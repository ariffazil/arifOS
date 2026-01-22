"""
LedgerStore - Abstract interface for cooling ledger storage.

Both MCP surfaces (L4_MCP black-box, arifos/mcp glass-box)
depend on this abstraction for audit logging.

Version: v45.1.0
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class LedgerStore(ABC):
    """
    Abstract interface for cooling ledger storage (append-only).

    Implementations:
    - SQLiteLedgerStore: ACID transactions, fail-closed (L4_MCP default)
    - JSONLMerkleLedger: Cryptographic proofs, portable (arifos/mcp default)
    """

    @abstractmethod
    def append_atomic(self, **record: Any) -> str:
        """
        Atomically append a record to the ledger.

        Must be all-or-nothing: either the full record is written,
        or nothing is written (no partial records).

        Args:
            **record: Arbitrary fields to log (request, verdict, reasons, etc.)

        Returns:
            str: Unique ledger ID for the stored record

        Raises:
            Exception: If the append fails (ensuring no partial write)
        """
        raise NotImplementedError

    @abstractmethod
    def get_entry(self, ledger_id: str) -> Optional[dict]:
        """
        Retrieve a ledger entry by ID.

        Args:
            ledger_id: Unique identifier from append_atomic()

        Returns:
            dict: The stored record, or None if not found
        """
        raise NotImplementedError

    def close(self) -> None:
        """Close any open resources. Optional for implementations."""
        pass
