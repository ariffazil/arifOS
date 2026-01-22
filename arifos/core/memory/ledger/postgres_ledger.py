"""
PostgreSQL Cooling Ledger - Dual-Write Pattern

Canonical Path: vault_999/INFRASTRUCTURE/cooling_ledger/
Architecture: File (jsonl immutable backup) + Postgres (queryable)
Authority: 888 Judge (CANON-2 §3 VAULT-999)
Version: v49.0.0

Pattern:
1. Write to Postgres (primary, queryable)
2. Write to JSONL (backup, immutable)
3. Fail-closed: If either fails, VOID verdict

Constitutional Alignment:
- F1 (Amanah): Dual-write = reversible (file backup)
- F2 (Truth): Postgres constraints ensure valid verdicts
- F3 (Tri-Witness): Audit trail for consensus verification
"""

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import psycopg2
from psycopg2.extras import Json


class PostgresLedger:
    """
    Dual-write cooling ledger (Postgres + JSONL).

    Canonical location: vault_999/INFRASTRUCTURE/cooling_ledger/
    """

    def __init__(
        self,
        db_url: Optional[str] = None,
        file_path: Optional[Path] = None
    ):
        """
        Initialize ledger with DB connection and file path.

        Args:
            db_url: PostgreSQL connection string (defaults to DATABASE_URL env)
            file_path: Path to JSONL backup (defaults to vault_999/INFRASTRUCTURE/)
        """
        self.db_url = db_url or os.getenv("DATABASE_URL", "postgresql://localhost:5432/arifos")
        self.file_path = file_path or Path("vault_999/INFRASTRUCTURE/cooling_ledger")
        self.file_path.mkdir(parents=True, exist_ok=True)

        # Connect to Postgres
        self.conn = psycopg2.connect(self.db_url)
        self.conn.autocommit = False  # Explicit transaction control

    async def write_entry(
        self,
        entry_id: str,
        verdict: str,
        floors: Dict[str, Any],
        user_id: str = "system",
        zkpc_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dual-write entry to Postgres + JSONL.

        Args:
            entry_id: Unique entry identifier
            verdict: SEAL/PARTIAL/VOID/SABAR/888_HOLD
            floors: Floor scores dict
            user_id: User identifier
            zkpc_hash: Optional zkPC receipt hash

        Returns:
            Written entry dict

        Raises:
            Exception: If either write fails (fail-closed)
        """
        timestamp = datetime.now(timezone.utc)

        entry = {
            "entry_id": entry_id,
            "timestamp": timestamp.isoformat(),
            "verdict": verdict,
            "floors": floors,
            "user_id": user_id,
            "zkpc_hash": zkpc_hash
        }

        try:
            # 1. Write to Postgres (primary)
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO cooling_ledger (entry_id, timestamp, verdict, floors, user_id, zkpc_hash)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (entry_id, timestamp, verdict, Json(floors), user_id, zkpc_hash)
            )
            self.conn.commit()
            cur.close()

            # 2. Write to JSONL (backup)
            date_str = timestamp.strftime("%Y-%m-%d")
            jsonl_file = self.file_path / f"{date_str}.jsonl"

            with open(jsonl_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")

            return entry

        except Exception as e:
            # Rollback on failure
            self.conn.rollback()
            raise Exception(f"Dual-write failed (F1 Amanah violation): {e}")

    async def query_by_verdict(self, verdict: str, limit: int = 100) -> list:
        """Query entries by verdict."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT entry_id, timestamp, verdict, floors, user_id, zkpc_hash
            FROM cooling_ledger
            WHERE verdict = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (verdict, limit)
        )
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "entry_id": row[0],
                "timestamp": row[1].isoformat(),
                "verdict": row[2],
                "floors": row[3],
                "user_id": row[4],
                "zkpc_hash": row[5]
            }
            for row in rows
        ]

    async def query_recent(self, limit: int = 50) -> list:
        """Query recent entries."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT entry_id, timestamp, verdict, floors, user_id, zkpc_hash
            FROM cooling_ledger
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,)
        )
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "entry_id": row[0],
                "timestamp": row[1].isoformat(),
                "verdict": row[2],
                "floors": row[3],
                "user_id": row[4],
                "zkpc_hash": row[5]
            }
            for row in rows
        ]

    def close(self):
        """Close DB connection."""
        self.conn.close()


# Singleton instance for server imports
_ledger_instance: Optional[PostgresLedger] = None


def get_ledger() -> PostgresLedger:
    """Get singleton ledger instance."""
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = PostgresLedger()
    return _ledger_instance
