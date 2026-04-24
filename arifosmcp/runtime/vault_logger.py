"""
VAULT999 Postgres Writer Stub
══════════════════════════════

Async VAULT999 ledger persistence layer.
Production: connect to PostgreSQL via asyncpg.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

_VAULT_ENABLED = os.getenv("ARIFOS_VAULT_ENABLED", "false").lower() == "true"
_VAULT_DSN = os.getenv("ARIFOS_VAULT_DSN", "postgresql://localhost/arifos")


class VaultLogger:
    """
    Async VAULT999 Postgres writer.

    Stub implementation: logs to stdout unless ARIFOS_VAULT_ENABLED=true.
    """

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or _VAULT_DSN
        self._pool: Any = None

    async def connect(self) -> None:
        if not _VAULT_ENABLED:
            logger.info("[VaultLogger] Vault persistence disabled (ARIFOS_VAULT_ENABLED=false)")
            return
        try:
            import asyncpg  # type: ignore[import-untyped]
            self._pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=4)
            logger.info("[VaultLogger] Postgres pool created")
        except ImportError:
            logger.warning("[VaultLogger] asyncpg not installed; vault writes will log only")
        except Exception as e:
            logger.error(f"[VaultLogger] Failed to connect: {e}")

    async def write(self, entry: dict[str, Any]) -> str | None:
        """Persist a vault entry. Returns entry_id or None."""
        entry_id = entry.get("id")
        if not _VAULT_ENABLED or self._pool is None:
            logger.info(f"[VaultLogger] LOG {entry_id}: {entry}")
            return entry_id
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO vault_ledger (entry_id, payload, session_id, created_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (entry_id) DO NOTHING
                    """,
                    entry_id,
                    entry.get("payload", ""),
                    entry.get("session_id"),
                    entry.get("timestamp"),
                )
            logger.info(f"[VaultLogger] WROTE {entry_id}")
            return entry_id
        except Exception as e:
            logger.error(f"[VaultLogger] Write failed for {entry_id}: {e}")
            return None

    async def read_recent(self, limit: int = 10) -> list[dict[str, Any]]:
        """Read recent vault entries."""
        if not _VAULT_ENABLED or self._pool is None:
            return []
        try:
            import asyncpg
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT entry_id, payload, session_id, created_at FROM vault_ledger ORDER BY created_at DESC LIMIT $1",
                    limit,
                )
                return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"[VaultLogger] Read failed: {e}")
            return []

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
            logger.info("[VaultLogger] Pool closed")
