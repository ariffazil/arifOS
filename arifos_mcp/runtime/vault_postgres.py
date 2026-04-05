"""
arifos_mcp/runtime/vault_postgres.py — PostgreSQL-backed VAULT999

Primary source of truth for constitutional audit ledger.
Implements dual-write: PostgreSQL (canonical) + Filesystem (mirror)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Optional asyncpg import - will gracefully degrade if not available
try:
    import asyncpg
    ASYNCpg_AVAILABLE = True
except ImportError:
    ASYNCpg_AVAILABLE = False

logger = logging.getLogger(__name__)

# Default paths — configurable via environment for container deployments
# In Docker: /usr/src/app/VAULT999 (matches docker-compose volume mount)
# On host: /root/VAULT999 (legacy path)
_DEFAULT_VAULT_PATH = os.environ.get("VAULT999_PATH", "/root/VAULT999")
VAULT999_PATH = Path(_DEFAULT_VAULT_PATH)
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
        """
        Initialize vault store.
        
        Args:
            dsn: PostgreSQL connection string. If None, uses DATABASE_URL env var.
            vault_path: Filesystem path for JSONL mirror. Defaults to VAULT999_PATH.
        """
        self.dsn = dsn or os.environ.get(
            "DATABASE_URL",
            "postgresql://arifos_admin:arifos_vault@localhost:5432/arifos_vault"
        )
        self.vault_path = vault_path or VAULT999_PATH
        self._pool: asyncpg.Pool | None = None
        
    async def _get_pool(self) -> asyncpg.Pool | None:
        """Lazy initialization of connection pool."""
        if not ASYNCpg_AVAILABLE:
            return None
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    self.dsn,
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                )
                # Initialize schema if needed
                await self._init_schema()
            except Exception as e:
                logger.warning(f"PostgreSQL vault unavailable: {e}")
                return None
        return self._pool
    
    async def _init_schema(self):
        """Create vault tables if they don't exist."""
        pool = await self._get_pool()
        if not pool:
            return
        
        async with pool.acquire() as conn:
            # Main events table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vault_events (
                    id SERIAL PRIMARY KEY,
                    event_id UUID UNIQUE NOT NULL,
                    event_type VARCHAR(32) NOT NULL,
                    session_id VARCHAR(128) NOT NULL,
                    actor_id VARCHAR(128) NOT NULL,
                    stage VARCHAR(32) NOT NULL,
                    verdict VARCHAR(32) NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}',
                    risk_tier VARCHAR(16) NOT NULL DEFAULT 'medium',
                    merkle_leaf VARCHAR(64) NOT NULL DEFAULT '',
                    prev_hash VARCHAR(64) NOT NULL DEFAULT '',
                    chain_hash VARCHAR(64) NOT NULL DEFAULT '',
                    signature VARCHAR(128) NOT NULL DEFAULT '',
                    signed_by VARCHAR(64) NOT NULL DEFAULT '',
                    sealed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            
            # Merkle chain seals
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS vault_seals (
                    id SERIAL PRIMARY KEY,
                    tree_size INTEGER NOT NULL,
                    merkle_root VARCHAR(64) NOT NULL,
                    prev_root VARCHAR(64) NOT NULL DEFAULT '',
                    first_event_id INTEGER NOT NULL,
                    last_event_id INTEGER NOT NULL,
                    signature VARCHAR(256) NOT NULL,
                    signed_by VARCHAR(64) NOT NULL DEFAULT '888_AUDITOR',
                    sealed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
            
            # Indexes for common queries
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vault_events_session 
                ON vault_events(session_id)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vault_events_sealed_at 
                ON vault_events(sealed_at DESC)
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_vault_events_chain_hash 
                ON vault_events(chain_hash)
            """)
    
    def _compute_merkle_leaf(self, event: VaultEvent) -> str:
        """Compute SHA-256 leaf hash for an event."""
        data = {
            "event_type": event.event_type,
            "session_id": event.session_id,
            "actor_id": event.actor_id,
            "stage": event.stage,
            "verdict": event.verdict,
            "payload": event.payload,
            "risk_tier": event.risk_tier,
            "sealed_at": event.sealed_at.isoformat(),
            "event_id": event.event_id,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    async def _get_last_chain_hash(self) -> str:
        """Get the chain hash of the most recent event."""
        pool = await self._get_pool()
        if pool:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT chain_hash FROM vault_events ORDER BY id DESC LIMIT 1"
                )
                if row:
                    return row["chain_hash"]
        
        # Fallback to filesystem
        if self.vault_path.exists():
            events_file = self.vault_path / "SEALED_EVENTS.jsonl"
            if events_file.exists():
                lines = events_file.read_text().strip().split("\n")
                if lines:
                    try:
                        last_event = json.loads(lines[-1])
                        return last_event.get("chain_hash", "")
                    except json.JSONDecodeError:
                        pass
        return ""
    
    async def seal(self, event: VaultEvent) -> SealResult:
        """
        Seal an event to VAULT999 (PostgreSQL + filesystem).
        
        This is the core dual-write operation:
        1. Compute Merkle leaf hash
        2. Get previous chain hash
        3. Compute new chain hash (SHA256(prev + leaf))
        4. Write to PostgreSQL
        5. Mirror to filesystem (JSONL append)
        """
        # Compute hashes
        event.merkle_leaf = self._compute_merkle_leaf(event)
        event.prev_hash = await self._get_last_chain_hash()
        
        chain_data = event.prev_hash + event.merkle_leaf
        event.chain_hash = hashlib.sha256(chain_data.encode()).hexdigest()
        
        # Ensure vault directory exists
        try:
            self.vault_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Cannot create vault directory {self.vault_path}: {e}")
            return SealResult(
                success=False,
                event_id=event.event_id,
                chain_hash="",
                error=f"Permission denied creating vault directory: {self.vault_path}. "
                      f"Ensure VAULT999_PATH environment variable is set correctly "
                      f"or the directory is writable by the current user."
            )
        
        db_id = 0
        db_error = None
        
        # Write to PostgreSQL (canonical)
        pool = await self._get_pool()
        if pool:
            try:
                async with pool.acquire() as conn:
                    row = await conn.fetchrow("""
                        INSERT INTO vault_events (
                            event_id, event_type, session_id, actor_id, stage, verdict,
                            payload, risk_tier, merkle_leaf, prev_hash, chain_hash,
                            signature, signed_by, sealed_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        RETURNING id
                    """,
                        event.event_id, event.event_type, event.session_id,
                        event.actor_id, event.stage, event.verdict,
                        json.dumps(event.payload), event.risk_tier,
                        event.merkle_leaf, event.prev_hash, event.chain_hash,
                        event.signature, event.signed_by, event.sealed_at
                    )
                    db_id = row["id"]
                    logger.debug(f"Sealed event {event.event_id} to PostgreSQL (id={db_id})")
            except Exception as e:
                db_error = str(e)
                logger.warning(f"PostgreSQL vault write failed: {e}")
        
        # Mirror to filesystem (always attempt, even if DB fails)
        try:
            events_file = self.vault_path / "SEALED_EVENTS.jsonl"
            chain_file = self.vault_path / "SEAL_CHAIN.txt"
            
            # Append event to JSONL
            event_dict = {
                "id": db_id,
                "event_id": event.event_id,
                "event_type": event.event_type,
                "session_id": event.session_id,
                "actor_id": event.actor_id,
                "stage": event.stage,
                "verdict": event.verdict,
                "payload": event.payload,
                "risk_tier": event.risk_tier,
                "merkle_leaf": event.merkle_leaf,
                "prev_hash": event.prev_hash,
                "chain_hash": event.chain_hash,
                "signature": event.signature,
                "signed_by": event.signed_by,
                "sealed_at": event.sealed_at.isoformat(),
            }
            
            with open(events_file, "a") as f:
                f.write(json.dumps(event_dict, separators=(",", ":")) + "\n")
            
            # Update chain file (latest hash)
            chain_file.write_text(
                f"{event.chain_hash}\n"
                f"event_id: {event.event_id}\n"
                f"sealed_at: {event.sealed_at.isoformat()}\n"
                f"db_id: {db_id}\n"
            )
            
            logger.debug(f"Mirrored event {event.event_id} to filesystem")
            
        except Exception as e:
            logger.error(f"Filesystem vault write failed: {e}")
            if db_error:
                return SealResult(
                    success=False,
                    event_id=event.event_id,
                    chain_hash=event.chain_hash,
                    error=f"Both PostgreSQL and filesystem writes failed. PG: {db_error}, FS: {e}"
                )
            # If DB succeeded but FS failed, we still consider it a success
            # (PostgreSQL is canonical)
        
        return SealResult(
            success=True,
            event_id=event.event_id,
            chain_hash=event.chain_hash,
            db_id=db_id,
        )
    
    async def verify_chain(self) -> dict[str, Any]:
        """Verify the integrity of the Merkle chain."""
        pool = await self._get_pool()
        if not pool:
            return {"ok": False, "error": "PostgreSQL not available"}
        
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id, chain_hash, prev_hash, merkle_leaf FROM vault_events ORDER BY id"
            )
        
        if not rows:
            return {"ok": True, "message": "Empty chain (no events)", "events_checked": 0}
        
        errors = []
        prev_hash = ""
        
        for row in rows:
            # Verify chain hash computation
            expected_data = prev_hash + row["merkle_leaf"]
            expected_hash = hashlib.sha256(expected_data.encode()).hexdigest()
            
            if row["chain_hash"] != expected_hash:
                errors.append({
                    "id": row["id"],
                    "error": "chain_hash_mismatch",
                    "expected": expected_hash,
                    "stored": row["chain_hash"],
                })
            
            if row["prev_hash"] != prev_hash:
                errors.append({
                    "id": row["id"],
                    "error": "prev_hash_mismatch",
                    "expected": prev_hash,
                    "stored": row["prev_hash"],
                })
            
            prev_hash = row["chain_hash"]
        
        if errors:
            return {
                "ok": False,
                "error": f"Chain verification failed: {len(errors)} errors",
                "errors": errors,
                "events_checked": len(rows),
            }
        
        return {
            "ok": True,
            "message": "Chain integrity verified",
            "events_checked": len(rows),
            "latest_hash": prev_hash,
        }


# Convenience function for external callers
async def seal_to_vault(
    event_type: str,
    session_id: str,
    actor_id: str,
    stage: str,
    verdict: str,
    payload: dict[str, Any] | None = None,
    risk_tier: str = "medium",
) -> SealResult:
    """Convenience wrapper to seal an event without managing the store."""
    store = PostgresVaultStore()
    event = VaultEvent(
        event_type=event_type,
        session_id=session_id,
        actor_id=actor_id,
        stage=stage,
        verdict=verdict,
        payload=payload or {},
        risk_tier=risk_tier,
    )
    return await store.seal(event)
