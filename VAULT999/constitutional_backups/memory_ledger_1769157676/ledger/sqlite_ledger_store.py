"""
SQLiteLedgerStore - ACID ledger backend for L4_MCP (Black-box authority).

Features:
- Atomic transactions (BEGIN IMMEDIATE)
- Fail-closed design (exception on failure)
- No partial writes guaranteed

Version: v45.1.0
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from arifos.core.memory.ledger_store import LedgerStore


class SQLiteLedgerStore(LedgerStore):
    """
    Reference implementation of cooling ledger using SQLite.

    Used by L4_MCP for ACID-compliant audit logging with fail-closed semantics.
    """

    def __init__(self, path: str = "cooling_ledger.sqlite3"):
        """
        Initialize SQLite ledger store.

        Args:
            path: Path to SQLite database file
        """
        self.path = path
        self._init_db()

    def _init_db(self) -> None:
        """Create ledger table if it doesn't exist."""
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS cooling_ledger (
                ledger_id   TEXT PRIMARY KEY,
                timestamp   TEXT NOT NULL,
                record_json TEXT NOT NULL
            )
            """)
            conn.commit()

    def append_atomic(self, **record: Any) -> str:
        """
        Atomically append a record to the ledger.

        Uses BEGIN IMMEDIATE for exclusive lock during write.
        Rolls back on any failure (no partial writes).
        """
        ledger_id = f"ledger_{uuid.uuid4().hex[:12]}"
        timestamp = record.get("timestamp", datetime.now(timezone.utc).isoformat())

        # Serialize record to JSON
        payload = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)

        with sqlite3.connect(self.path) as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "INSERT INTO cooling_ledger (ledger_id, timestamp, record_json) VALUES (?, ?, ?)",
                    (ledger_id, timestamp, payload),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

        return ledger_id

    def get_entry(self, ledger_id: str) -> Optional[dict]:
        """Retrieve a ledger entry by ID."""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.execute(
                "SELECT record_json FROM cooling_ledger WHERE ledger_id = ?", (ledger_id,)
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None

    def close(self) -> None:
        """SQLite connections are auto-closed via context manager."""
        pass
        pass
