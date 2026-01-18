"""
arifos_ledger - Shared Ledger Abstraction for arifOS MCP Surfaces.

This module provides a unified ledger interface used by both:
- L4_MCP/ (Black-box authority) - SQLite backend
- arifos_core/mcp/ (Glass-box debugging) - JSONL+Merkle backend

Version: v45.1.0
Status: PRODUCTION
"""

from .store import LedgerStore

__all__ = ["LedgerStore"]
__version__ = "45.1.0"
