"""
arifos_mcp/runtime/vault_postgres.py — PostgreSQL-backed VAULT999

Primary source of truth for constitutional audit ledger.
Implements dual-write: PostgreSQL (canonical) + Filesystem (mirror)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Optional asyncpg import - will gracefully degrade if not available
try:
    import asyncpg
    ASYNCpg_AVAILABLE = True
except ImportError:
    ASYNCpg_AVAILABLE = False

logger = logging.getLogger(__name__)

# Default paths
VAULT999_PATH = Path("/root/VAULT999")
VAULT_EVENTS_FILE = VAULT999_PATH / "SEALED_EVENTS.jsonl"
VAULT_CHAIN_FILE = VAULT999_PATH / "SEAL_CHAIN.txt"


@dataclass
class VaultEvent:
    """A single vault event record."""
    event_type: str                           # 'seal', 'verify', 'sabar', 'void'
    session_id: str
    actor_id: str
    stage: str                                # '999_VAULT', '888_JUDGE', etc.
    verdict: str                              # 'SEAL', 'SABAR', 'VOID', 'HOLD'
    payload: dict[str, Any] = field(default_factory=dict)
    risk_tier: str = "medium"
    
    # Merkle chain fields (computed on seal)
    merkle_leaf: str = ""
    prev_hash: str = ""
    chain_hash: str = ""
    
    # Optional 888 signature
    signature: str = ""
    signed_by: str = ""
    
    # Timing
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Generated fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass  
class VaultSeal:
    """A batch seal with Merkle root."""
    tree_size: int
    merkle_root: str
    prev_root: str
    first_event_id: int
    last_event_id: int
    signature: str
    signed_by: str = "888_AUDITOR"
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    archive_path: str = ""


@dataclass
class SealResult:
    """Result of a seal operation."""
    success: bool
    event_id: str
    chain_hash: str
    db_id: int = 0
    error: str = ""


class PostgresVaultStore:
    """
    PostgreSQL-backed VAULT999 with filesystem mirror.
    
    Architecture:
    - PostgreSQL = source of truth (transactional, durable)
    - Filesystem = mirror/backup (JSONL exports)
    - Both written on every seal (dual-write)
    """
    
    def __init__(
        self,
        dsn: str | None = None,
        vault_path: Path | None = None,
    ):
        # Connection params - passwordless for trusted VPS
        self.dsn = dsn
        self._connection_params = {
            "host": "localhost",
            "port": 5432,
            "user": "arifos_admin",
            "password": "",  # Passwordless - trust auth
            "database": "arifos_vault",
        }
        self.vault_path = vault_path or VAULT999_PATH
        self._pool: Any | None = None
        self._lock = asyncio.Lock()
        
        # Ensure vault directory exists
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        if not ASYNCpg_AVAILABLE:
            logger.warning("asyncpg not available. Running in filesystem-only mode.")
    
    async def _get_pool(self) -> Any:
        """Lazy connection pool initialization."""
        if not ASYNCpg_AVAILABLE:
            return None
            
        if self._pool is None:
            try:
                # Use DSN if provided, otherwise use connection params
                if self.dsn:
                    self._pool = await asyncpg.create_pool(
                        self.dsn,
                        min_size=2,
                        max_size=10,
                    )
                else:
                    # Default connection for arifOS docker-compose setup
                    self._pool = await asyncpg.create_pool(
                        host=os.environ.get("POSTGRES_HOST", "localhost"),
                        port=int(os.environ.get("POSTGRES_PORT", "5432")),
                        user=os.environ.get("POSTGRES_USER", "arifos_admin"),
                        password=os.environ.get("POSTGRES_PASSWORD", ""),
                        database=os.environ.get("POSTGRES_DB", "arifos_vault"),
                        min_size=2,
                        max_size=10,
                    )
                logger.info("PostgreSQL vault pool initialized")
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                self._pool = None
                
        return self._pool
    
    def _compute_merkle_leaf(self, event: VaultEvent) -> str:
        """Compute SHA-256 leaf hash for an event."""
        content = json.dumps({
            "event_type": event.event_type,
            "session_id": event.session_id,
            "actor_id": event.actor_id,
            "stage": event.stage,
            "verdict": event.verdict,
            "payload": event.payload,
            "risk_tier": event.risk_tier,
            "sealed_at": event.sealed_at.isoformat(),
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _get_last_chain_hash(self, conn: Any | None = None) -> str:
        """Get the last chain hash from PostgreSQL or filesystem."""
        # Try PostgreSQL first
        if ASYNCpg_AVAILABLE and conn is not None:
            try:
                row = await conn.fetchval(
                    "SELECT chain_hash FROM vault_events ORDER BY id DESC LIMIT 1"
                )
                if row:
                    return row
            except Exception as e:
                logger.warning(f"Failed to get last hash from DB: {e}")
        
        # Fallback to filesystem
        try:
            if VAULT_CHAIN_FILE.exists():
                with open(VAULT_CHAIN_FILE) as f:
                    chain = json.load(f)
                    return chain.get("root", "0" * 64)
        except Exception as e:
            logger.warning(f"Failed to get last hash from file: {e}")
        
        return "0" * 64
    
    async def _write_to_postgres(self, event: VaultEvent) -> tuple[int, str]:
        """
        Write event to PostgreSQL.
        
        Returns:
            (db_id, chain_hash)
        """
        pool = await self._get_pool()
        if pool is None:
            raise RuntimeError("PostgreSQL not available")
        
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Get previous hash
                prev_hash = await self._get_last_chain_hash(conn)
                
                # Compute this event's hash
                merkle_leaf = self._compute_merkle_leaf(event)
                
                # Compute chain hash (simple chain: hash(prev + current))
                chain_content = prev_hash + merkle_leaf
                chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
                
                # Insert event
                row = await conn.fetchrow(
                    """
                    INSERT INTO vault_events (
                        event_type, session_id, actor_id, stage, verdict, risk_tier,
                        payload, merkle_leaf, prev_hash, chain_hash, signature, signed_by
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    RETURNING id, chain_hash
                    """,
                    event.event_type,
                    uuid.UUID(event.session_id) if event.session_id else uuid.uuid4(),
                    event.actor_id,
                    event.stage,
                    event.verdict,
                    event.risk_tier,
                    json.dumps(event.payload),
                    merkle_leaf,
                    prev_hash,
                    chain_hash,
                    event.signature,
                    event.signed_by,
                )
                
                return row["id"], row["chain_hash"]
    
    async def _write_to_filesystem(self, event: VaultEvent, db_id: int = 0) -> None:
        """Mirror event to filesystem JSONL."""
        try:
            # Append to events file
            event_dict = {
                "db_id": db_id,
                "event_id": event.event_id,
                "event_type": event.event_type,
                "session_id": event.session_id,
                "actor_id": event.actor_id,
                "stage": event.stage,
                "verdict": event.verdict,
                "risk_tier": event.risk_tier,
                "payload": event.payload,
                "merkle_leaf": event.merkle_leaf,
                "prev_hash": event.prev_hash,
                "chain_hash": event.chain_hash,
                "signature": event.signature,
                "signed_by": event.signed_by,
                "sealed_at": event.sealed_at.isoformat(),
            }
            
            with open(VAULT_EVENTS_FILE, "a") as f:
                f.write(json.dumps(event_dict, default=str) + "\n")
            
            # Update chain file
            chain = {
                "seal": event.chain_hash[:8] if event.chain_hash else "GENESIS",
                "depth": db_id,
                "root": event.chain_hash or "0" * 64,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prev_seal": event.prev_hash[:8] if event.prev_hash else "00000000",
                "leaf": event.merkle_leaf[:16] if event.merkle_leaf else "0" * 16,
            }
            
            with open(VAULT_CHAIN_FILE, "w") as f:
                f.write(json.dumps(chain, indent=2))
                
        except Exception as e:
            logger.error(f"Failed to write to filesystem: {e}")
            raise
    
    async def seal(self, event: VaultEvent) -> SealResult:
        """
        Seal an event to VAULT999.
        
        Dual-write: PostgreSQL (canonical) + Filesystem (mirror)
        If PostgreSQL fails, falls back to filesystem-only mode.
        """
        async with self._lock:
            try:
                # Try PostgreSQL first (canonical)
                if ASYNCpg_AVAILABLE:
                    try:
                        db_id, chain_hash = await self._write_to_postgres(event)
                        event.chain_hash = chain_hash
                        
                        # Mirror to filesystem
                        await self._write_to_filesystem(event, db_id)
                        
                        return SealResult(
                            success=True,
                            event_id=event.event_id,
                            chain_hash=chain_hash,
                            db_id=db_id,
                        )
                    except Exception as e:
                        logger.warning(f"PostgreSQL seal failed, falling back to filesystem: {e}")
                
                # Filesystem-only mode (fallback)
                prev_hash = await self._get_last_chain_hash(None)
                merkle_leaf = self._compute_merkle_leaf(event)
                chain_content = prev_hash + merkle_leaf
                chain_hash = hashlib.sha256(chain_content.encode()).hexdigest()
                
                event.prev_hash = prev_hash
                event.merkle_leaf = merkle_leaf
                event.chain_hash = chain_hash
                
                await self._write_to_filesystem(event, 0)
                
                return SealResult(
                    success=True,
                    event_id=event.event_id,
                    chain_hash=chain_hash,
                    db_id=0,  # No DB id in fallback mode
                )
                
            except Exception as e:
                logger.error(f"Seal failed completely: {e}")
                return SealResult(
                    success=False,
                    event_id=event.event_id,
                    chain_hash="",
                    error=str(e),
                )
    
    async def get_chain(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent vault entries from PostgreSQL."""
        pool = await self._get_pool()
        if pool is None:
            # Fallback to filesystem
            return await self._get_chain_from_filesystem(limit)
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, event_id, event_type, session_id, actor_id, stage, verdict,
                       payload, merkle_leaf, prev_hash, chain_hash, sealed_at
                FROM vault_events
                ORDER BY id DESC
                LIMIT $1
                """,
                limit,
            )
            
            return [
                {
                    "id": row["id"],
                    "event_id": str(row["event_id"]),
                    "event_type": row["event_type"],
                    "session_id": str(row["session_id"]),
                    "actor_id": row["actor_id"],
                    "stage": row["stage"],
                    "verdict": row["verdict"],
                    "payload": row["payload"],
                    "merkle_leaf": row["merkle_leaf"],
                    "prev_hash": row["prev_hash"],
                    "chain_hash": row["chain_hash"],
                    "sealed_at": row["sealed_at"].isoformat() if row["sealed_at"] else None,
                }
                for row in reversed(rows)  # Oldest first
            ]
    
    async def _get_chain_from_filesystem(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fallback: Get chain from filesystem."""
        if not VAULT_EVENTS_FILE.exists():
            return []
        
        try:
            with open(VAULT_EVENTS_FILE) as f:
                lines = f.readlines()
            
            events = []
            for line in lines[-limit:]:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            
            return events
        except Exception as e:
            logger.error(f"Failed to read from filesystem: {e}")
            return []
    
    async def verify_chain(self) -> tuple[bool, str]:
        """
        Verify the integrity of the vault chain.
        
        Returns:
            (is_valid, message)
        """
        pool = await self._get_pool()
        if pool is None:
            return await self._verify_chain_filesystem()
        
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT id, prev_hash, chain_hash FROM vault_events ORDER BY id"
                )
                
                if not rows:
                    return True, "Empty chain (valid)"
                
                expected_prev = "0" * 64
                for row in rows:
                    if row["prev_hash"] != expected_prev:
                        return False, f"Chain broken at id={row['id']}: expected {expected_prev[:16]}..., got {row['prev_hash'][:16]}..."
                    expected_prev = row["chain_hash"]
                
                return True, f"Chain verified: {len(rows)} entries intact"
                
        except Exception as e:
            logger.error(f"Chain verification failed: {e}")
            return False, f"Verification error: {e}"
    
    async def _verify_chain_filesystem(self) -> tuple[bool, str]:
        """Fallback: Verify chain from filesystem."""
        if not VAULT_EVENTS_FILE.exists():
            return True, "Empty chain (valid)"
        
        try:
            with open(VAULT_EVENTS_FILE) as f:
                lines = f.readlines()
            
            expected_prev = "0" * 64
            for i, line in enumerate(lines):
                event = json.loads(line)
                if event.get("prev_hash") != expected_prev:
                    return False, f"Chain broken at line {i+1}"
                expected_prev = event.get("chain_hash", "0" * 64)
            
            return True, f"Chain verified: {len(lines)} entries intact"
            
        except Exception as e:
            return False, f"Verification error: {e}"
    
    async def get_session_events(self, session_id: str) -> list[dict[str, Any]]:
        """Get all events for a specific session."""
        pool = await self._get_pool()
        if pool is None:
            # Fallback: filter from filesystem
            chain = await self.get_chain(10000)  # Get all
            return [e for e in chain if e.get("session_id") == session_id]
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT * FROM vault_events
                WHERE session_id = $1
                ORDER BY id
                """,
                uuid.UUID(session_id),
            )
            
            return [
                {
                    "id": row["id"],
                    "event_id": str(row["event_id"]),
                    "event_type": row["event_type"],
                    "session_id": str(row["session_id"]),
                    "actor_id": row["actor_id"],
                    "verdict": row["verdict"],
                    "payload": row["payload"],
                    "chain_hash": row["chain_hash"],
                    "sealed_at": row["sealed_at"].isoformat() if row["sealed_at"] else None,
                }
                for row in rows
            ]
    
    async def close(self):
        """Close the connection pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None


# Global singleton instance
_vault_store: PostgresVaultStore | None = None


def get_vault_store() -> PostgresVaultStore:
    """Get singleton Postgres vault store."""
    global _vault_store
    if _vault_store is None:
        _vault_store = PostgresVaultStore()
    return _vault_store


__all__ = [
    "PostgresVaultStore",
    "VaultEvent",
    "VaultSeal",
    "SealResult",
    "get_vault_store",
]
