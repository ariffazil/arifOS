"""
arifosmcp/runtime/vault_postgres.py — PostgreSQL-backed VAULT999

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

    event_type: str  # 'seal', 'verify', 'sabar', 'void'
    session_id: str
    actor_id: str
    stage: str  # '999_VAULT', '888_JUDGE', etc.
    verdict: str  # 'SEAL', 'SABAR', 'VOID', 'HOLD'
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

    Constitutional tables (arifos.*):
    - sessions: per-agent constitutional session records
    - pipeline_runs: 000→999 stage transitions
    - tool_calls: every tool execution attributed to a session
    - agent_telemetry: SEAL/HOLD/VOID verdicts per agent
    - floor_rules: F1-F13 constitution loaded at startup
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
            "DATABASE_URL", "postgresql://arifos_admin:ArifPostgresVault2026%21@postgres:5432/arifos_vault"
        )
        self.vault_path = vault_path or VAULT999_PATH
        self._pool: asyncpg.Pool | None = None
        self._constitution: dict | None = None  # F1-F13 loaded at startup
        self._active_session: str | None = None  # this server's session_id

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

    # ═══════════════════════════════════════════════════════════════════════
    # METHOD 1 — load_constitution()
    # Load F1-F13 from arifos.floor_rules at server startup
    # ═══════════════════════════════════════════════════════════════════════
    async def load_constitution(self) -> dict[str, Any]:
        """
        Load constitutional floor rules from arifos.floor_rules table.
        Called once at server startup. Results cached in self._constitution.

        Returns:
            dict mapping floor code (e.g. 'F1') to full floor record dict.
            Keys: floor_id, code, name, type, seal_threshold, void_threshold, description
        """
        pool = await self._get_pool()
        if not pool:
            logger.warning("load_constitution: pool unavailable, returning empty dict")
            return {}

        try:
            rows = await pool.fetch("""
                SELECT floor_id, code, name, type,
                       seal_threshold, void_threshold, description
                FROM arifos.floor_rules
                ORDER BY floor_id
            """)
            self._constitution = {r["code"]: dict(r) for r in rows}
            logger.info(f"[VAULT] Constitution loaded: {len(self._constitution)} floors")
            return self._constitution
        except Exception as e:
            logger.warning(f"load_constitution failed: {e}")
            return {}

    @property
    def constitution(self) -> dict[str, Any] | None:
        """Return cached constitution (or None if not yet loaded)."""
        return self._constitution

    # ═══════════════════════════════════════════════════════════════════════
    # METHOD 2 — open_session()
    # Open a constitutional session in arifos.sessions
    # ═══════════════════════════════════════════════════════════════════════
    async def open_session(
        self,
        agent_id: str,
        declared_intent: str,
        risk_tier: str = "LOW",
    ) -> str:
        """
        Open a constitutional session and write to arifos.sessions.

        Args:
            agent_id: e.g. 'GEOX-Agent', 'WEALTH-Agent', 'AUDITOR-Agent'
            declared_intent: Human-readable purpose of this session
            risk_tier: LOW | MEDIUM | HIGH | CRITICAL (default LOW)

        Returns:
            session_id: e.g. 'GEOX-Agent-A1B2C3D4'
        """
        pool = await self._get_pool()
        if not pool:
            logger.warning("open_session: pool unavailable, returning fallback session_id")
            return f"{agent_id}-{uuid.uuid4().hex[:8].upper()}"

        session_id = f"{agent_id}-{uuid.uuid4().hex[:8].upper()}"

        try:
            await pool.execute(
                """
                INSERT INTO arifos.sessions
                (session_id, agent_id, initiated_at, declared_intent, risk_tier)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (session_id) DO NOTHING
            """,
                session_id,
                agent_id,
                datetime.now(timezone.utc),
                declared_intent,
                risk_tier,
            )
            logger.info(f"[VAULT] Session opened: {session_id} for {agent_id}")
            # Cache as active session for this server instance
            self._active_session = session_id
            return session_id
        except Exception as e:
            # Fallback: return session_id even if DB write fails
            logger.warning(f"open_session DB write failed: {e}")
            self._active_session = session_id
            return session_id

    @property
    def active_session(self) -> str | None:
        """Return this server's active session_id."""
        return self._active_session

    # ═══════════════════════════════════════════════════════════════════════
    # METHOD 3 — log_tool_call()
    # Log every tool execution to arifos.tool_calls
    # ═══════════════════════════════════════════════════════════════════════
    async def log_tool_call(
        self,
        session_id: str | None,
        run_id: str | None,
        tool_name: str,
        organ: str,
        input_summary: str,
        output_summary: str,
        verdict: str = "SEAL",
        duration_ms: int = 0,
        floor_triggered: str | None = None,
    ) -> None:
        """
        Log a tool call execution to arifos.tool_calls.

        Args:
            session_id: from open_session()
            run_id: same as session_id for single-agent runs
            tool_name: e.g. 'arifos_init', 'vault_seal'
            organ: which organ triggered it (psi, judge, vault, etc.)
            input_summary: truncated input (max 500 chars)
            output_summary: truncated output (max 500 chars)
            verdict: SEAL | HOLD | VOID | SABAR
            duration_ms: execution time in milliseconds
            floor_triggered: e.g. 'F1' if a floor was checked (optional)
        """
        pool = await self._get_pool()
        sid = session_id or self._active_session or "UNKNOWN"
        rid = None  # run_id is bigint FK — None for now since pipeline_runs is optional

        # Truncate summaries to avoid overflow
        input_sum = input_summary[:500] if input_summary else ""
        output_sum = output_summary[:500] if output_summary else ""

        if not pool:
            logger.debug(f"log_tool_call: pool unavailable, skipping {tool_name}")
            return

        try:
            # Ensure session exists in arifos.sessions (upsert for external/init sessions)
            try:
                await pool.execute(
                    """
                    INSERT INTO arifos.sessions (session_id, declared_intent, risk_tier)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (session_id) DO NOTHING
                """,
                    sid,
                    f"External init session: {tool_name}",
                    "low",
                )
            except Exception:
                pass  # non-fatal if insert fails

            await pool.execute(
                """
                INSERT INTO arifos.tool_calls
                (session_id, run_id, tool_name, organ, input_hash, output_hash,
                 verdict, duration_ms, floor_triggered)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
                sid,
                rid,
                tool_name,
                organ,
                hashlib.sha256(input_sum.encode()).hexdigest()[:16],
                hashlib.sha256(output_sum.encode()).hexdigest()[:16],
                verdict,
                duration_ms,
                floor_triggered,
            )
            logger.debug(f"[VAULT] tool_call: {tool_name} ({verdict}, {duration_ms}ms)")
        except Exception as e:
            logger.warning(f"log_tool_call failed for {tool_name}: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # METHOD 4 — seal_session()
    # Close a constitutional session and write telemetry atomically
    # ═══════════════════════════════════════════════════════════════════════
    async def seal_session(
        self,
        session_id: str | None,
        agent_id: str,
        verdict: str,
        peace2: float = 0.0,
        kappa_r: float = 0.0,
        confidence: float = 0.0,
        payload: dict[str, Any] | None = None,
    ) -> None:
        """
        Close a session and write telemetry in one transaction.

        Args:
            session_id: session to close (uses active_session if None)
            agent_id: which agent this belongs to
            verdict: SEAL | HOLD | VOID | SABAR
            peace2: Peace² metric at time of seal
            kappa_r: Kappa-R consistency ratio
            confidence: 0.0–1.0
            payload: arbitrary context dict (e.g. {stage, tool_count, ...})
        """
        pool = await self._get_pool()
        sid = session_id or self._active_session or agent_id
        pld = payload or {}

        if not pool:
            logger.warning("seal_session: pool unavailable")
            return

        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # Close the session
                    await conn.execute(
                        """
                        UPDATE arifos.sessions
                        SET final_verdict = $2, closed_at = NOW(), status = 'sealed'
                        WHERE session_id = $1
                    """,
                        sid,
                        verdict,
                    )

                    # Write telemetry
                    await conn.execute(
                        """
                        INSERT INTO arifos.agent_telemetry
                        (agent_id, verdict, epoch, session_id, confidence,
                         kappa_r, peace2, payload)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                        agent_id,
                        verdict,
                        datetime.now(timezone.utc),
                        sid,
                        confidence,
                        kappa_r,
                        peace2,
                        json.dumps({**pld, "seal": "DITEMPA BUKAN DIBERI"}),
                    )
            logger.info(f"[VAULT] Session sealed: {sid} → {verdict}")
        except Exception as e:
            logger.warning(f"seal_session failed: {e}")

    # ─── End of constitutional table methods ────────────────────────────

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
                f"or the directory is writable by the current user.",
            )

        db_id = 0
        db_error = None

        # Write to PostgreSQL (canonical)
        pool = await self._get_pool()
        if pool:
            try:
                async with pool.acquire() as conn:
                    row = await conn.fetchrow(
                        """
                        INSERT INTO vault_events (
                            event_id, event_type, session_id, actor_id, stage, verdict,
                            payload, risk_tier, merkle_leaf, prev_hash, chain_hash,
                            signature, signed_by, sealed_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        RETURNING id
                    """,
                        event.event_id,
                        event.event_type,
                        event.session_id,
                        event.actor_id,
                        event.stage,
                        event.verdict,
                        json.dumps(event.payload),
                        event.risk_tier,
                        event.merkle_leaf,
                        event.prev_hash,
                        event.chain_hash,
                        event.signature,
                        event.signed_by,
                        event.sealed_at,
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
                    error=f"Both PostgreSQL and filesystem writes failed. PG: {db_error}, FS: {e}",
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
                errors.append(
                    {
                        "id": row["id"],
                        "error": "chain_hash_mismatch",
                        "expected": expected_hash,
                        "stored": row["chain_hash"],
                    }
                )

            if row["prev_hash"] != prev_hash:
                errors.append(
                    {
                        "id": row["id"],
                        "error": "prev_hash_mismatch",
                        "expected": prev_hash,
                        "stored": row["prev_hash"],
                    }
                )

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
