"""
arifosmcp/runtime/vault_postgres.py — Dual-Write VAULT999 (Supabase + Local)

Architecture (F2 Physics):
- Primary (Cloud Canon): Supabase (Persistent, Scalable)
- Witness (VPS Body): Local PostgreSQL + Filesystem (Mirror, Air-gap fallback)

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
from typing import Any, Optional

# Optional imports
try:
    import asyncpg

    ASYNCpg_AVAILABLE = True
except ImportError:
    ASYNCpg_AVAILABLE = False

try:
    from supabase import create_client, Client

    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Paths
_DEFAULT_VAULT_PATH = os.environ.get("VAULT999_PATH", "/root/VAULT999")
VAULT999_PATH = Path(_DEFAULT_VAULT_PATH)
VAULT_EVENTS_FILE = VAULT999_PATH / "SEALED_EVENTS.jsonl"


@dataclass
class VaultEvent:
    event_type: str
    session_id: str
    actor_id: str
    stage: str
    verdict: str
    payload: dict[str, Any] = field(default_factory=dict)
    risk_tier: str = "medium"
    merkle_leaf: str = ""
    prev_hash: str = ""
    chain_hash: str = ""
    sealed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SealResult:
    success: bool
    event_id: str
    chain_hash: str
    vault_id: str = ""
    error: str = ""
    ledger_id: str = ""  # Compat


class SupabaseVaultStore:
    """Supabase implementation of VAULT999."""

    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.client: Optional[Client] = None
        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception as e:
                logger.error(f"Supabase init error: {e}")

    async def get_last_hash(self) -> str:
        if not self.client:
            return "0" * 64
        try:
            # Query the dedicated chain_hash column for the most recent record
            res = (
                self.client.table("arifosmcp_vault_seals")
                .select("chain_hash")
                .order("created_at", desc=True)
                .limit(1)
                .maybe_single()
                .execute()
            )
            if res.data and res.data.get("chain_hash"):
                return res.data["chain_hash"]
        except Exception as e:
            logger.warning(f"Error fetching last hash: {e}")
        return "0" * 64

    async def seal(self, event: VaultEvent) -> bool:
        if not self.client:
            return False
        try:
            data = {
                "seal_id": event.event_id,
                "agent_id": event.actor_id,
                "action": event.event_type,
                "payload": event.payload,
                "confidence": 1.0,
                "epoch": event.sealed_at.isoformat(),
                "prev_hash": event.prev_hash,
                "chain_hash": event.chain_hash,
            }
            self.client.table("arifosmcp_vault_seals").insert(data).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase seal error: {e}")
            return False


class PostgresVaultStore:
    """Local PostgreSQL witness mirror."""

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn or os.environ.get("DATABASE_URL")
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self):
        if not ASYNCpg_AVAILABLE or not self.dsn:
            return None
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(self.dsn, min_size=1)
            except Exception:
                pass
        return self._pool

    async def get_last_hash(self) -> str:
        pool = await self._get_pool()
        if not pool:
            return "0" * 64
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT chain_hash FROM vault_events ORDER BY id DESC LIMIT 1"
                )
                return row["chain_hash"] if row else "0" * 64
        except Exception:
            return "0" * 64

    async def seal(self, event: VaultEvent) -> bool:
        pool = await self._get_pool()
        if not pool:
            return False
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO vault_events (event_id, event_type, session_id, actor_id, stage, verdict, payload, merkle_leaf, prev_hash, chain_hash, risk_tier) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)",
                    event.event_id,
                    event.event_type,
                    event.session_id,
                    event.actor_id,
                    event.stage,
                    event.verdict,
                    json.dumps(event.payload),
                    event.merkle_leaf,
                    event.prev_hash,
                    event.chain_hash,
                    event.risk_tier,
                )
            return True
        except Exception as e:
            logger.error(f"Local postgres seal error: {e}")
            return False

    async def open_session(
        self,
        agent_id: str,
        anchor_seal_id: str = None,
        declared_intent: str = None,
        risk_tier: str = None,
    ) -> str:
        """Initialize session in Postgres."""
        session_id = f"SESSION_{agent_id.upper()}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
        # For now, we return the generated ID; actual session table persistence can be added here
        return session_id

    async def load_constitution(self) -> dict:
        """Load the 13 Floors from the root CORE_SPEC file."""
        spec_path = Path("/root/arifOS_CORE_SPEC_v2.0.md")
        if not spec_path.exists():
            return {"error": "CORE_SPEC not found", "floors": []}
        
        # In a real implementation, we would parse the markdown
        # For now, return a status indicating the Spec is the source
        return {
            "source": str(spec_path),
            "version": "2.0",
            "status": "LOADED",
            "floors": ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13"]
        }


class VaultManager:
    """Orchestrates Dual-Write (Supabase + Local). Singleton pattern recommended."""

    def __init__(self):
        self.supabase = SupabaseVaultStore()
        self.postgres = PostgresVaultStore()
        self.fs_path = VAULT_EVENTS_FILE

    async def seal(self, event: VaultEvent) -> SealResult:
        # 1. Get previous hash from LOCAL postgres (PRIMARY)
        event.prev_hash = await self.postgres.get_last_hash()

        # 2. Compute Merkle Leaf and Chain Hash
        event.merkle_leaf = hashlib.sha256(
            json.dumps(event.payload, sort_keys=True).encode()
        ).hexdigest()
        event.chain_hash = hashlib.sha256(
            (event.prev_hash + event.merkle_leaf).encode()
        ).hexdigest()

        # 3. Write to LOCAL postgres FIRST (synchronous, blocking — source of truth)
        pg_success = await self.postgres.seal(event)
        if not pg_success:
            logger.error("VaultManager: local postgres write FAILED — aborting seal")
            return SealResult(
                success=False,
                event_id=event.event_id,
                chain_hash="",
                error="Local postgres write failed",
            )

        # 4. Async write to SUPABASE (fire-and-forget — non-blocking mirror)
        # Fire-and-forget: Supabase failure must NEVER fail the main operation
        try:
            import asyncio

            asyncio.create_task(self._supabase_async_seal(event))
        except Exception as sb_err:
            logger.warning(f"Supabase async seal task creation failed (non-fatal): {sb_err}")

        # 5. Filesystem witness (non-blocking)
        try:
            VAULT999_PATH.mkdir(parents=True, exist_ok=True)
            with open(self.fs_path, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "event_id": event.event_id,
                            "type": event.event_type,
                            "verdict": event.verdict,
                            "hash": event.chain_hash,
                            "ts": event.sealed_at.isoformat(),
                        }
                    )
                    + "\n"
                )
        except Exception:
            pass

        return SealResult(
            success=pg_success,
            event_id=event.event_id,
            chain_hash=event.chain_hash,
            ledger_id=event.event_id,
        )

    async def open_session(
        self,
        agent_id: str,
        anchor_seal_id: str = None,
        declared_intent: str = None,
        risk_tier: str = None,
    ) -> str:
        return await self.postgres.open_session(agent_id, anchor_seal_id, declared_intent, risk_tier)

    async def load_constitution(self) -> dict:
        return await self.postgres.load_constitution()


    async def _supabase_async_seal(self, event: VaultEvent) -> None:
        """Async Supabase mirror write — fire-and-forget, non-blocking."""
        try:
            sb_success = await self.supabase.seal(event)
            if sb_success:
                logger.info(f"[VaultManager] Supabase mirror OK: {event.event_id}")
            else:
                logger.warning(
                    f"[VaultManager] Supabase mirror FAILED (non-fatal): {event.event_id}"
                )
        except Exception as e:
            logger.warning(f"[VaultManager] Supabase async seal exception (non-fatal): {e}")


# Module-level Singleton
_vault_manager: VaultManager | None = None


def get_vault_manager() -> VaultManager:
    global _vault_manager
    if _vault_manager is None:
        _vault_manager = VaultManager()
    return _vault_manager


async def seal_to_vault(
    event_type: str,
    session_id: str,
    actor_id: str,
    stage: str,
    verdict: str,
    payload: dict[str, Any] | None = None,
    risk_tier: str = "medium",
) -> SealResult:
    mgr = get_vault_manager()
    event = VaultEvent(
        event_type=event_type,
        session_id=session_id,
        actor_id=actor_id,
        stage=stage,
        verdict=verdict,
        payload=payload or {},
        risk_tier=risk_tier,
    )
    return await mgr.seal(event)


class SupabaseStateStore:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        self.client = None
        if SUPABASE_AVAILABLE and self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
            except Exception:
                pass

    def read_state(self, agent_id: str, state_key: str) -> dict:
        if not self.client:
            return {}
        try:
            res = (
                self.client.table("arifosmcp_well_states")
                .select("state_value")
                .eq("agent_id", agent_id)
                .eq("state_key", state_key)
                .maybe_single()
                .execute()
            )
            return res.data["state_value"] if res.data else {}
        except Exception:
            return {}

    def write_state(self, agent_id: str, state_key: str, value: dict):
        if not self.client:
            return
        try:
            self.client.table("arifosmcp_well_states").upsert(
                {
                    "agent_id": agent_id,
                    "state_key": state_key,
                    "state_value": value,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
            ).execute()
        except Exception:
            pass


# ── HELPER ───────────────────────────────────────────────────


def get_supabase() -> Optional[Client]:
    """Helper to get a Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if SUPABASE_AVAILABLE and url and key:
        try:
            return create_client(url, key)
        except Exception:
            return None
    return None


def read_well_state(agent_id: str, state_key: str) -> dict:
    """Helper for reading WELL state."""
    store = SupabaseStateStore()
    return store.read_state(agent_id, state_key)


async def seal_vault(
    seal_id: str, agent_id: str, action: str, confidence: float, payload: dict, verdict: str
) -> dict:
    """Wrapper for seal_to_vault that matches the new signature."""
    res = await seal_to_vault(
        event_type=action,
        session_id=payload.get("session_id", "UNKNOWN"),
        actor_id=agent_id,
        stage="999_VAULT",
        verdict=verdict,
        payload=payload,
    )
    return {
        "seal_id": seal_id,
        "agent_id": agent_id,
        "action": action,
        "payload": payload,
        "verdict": verdict,
        "epoch": datetime.now(timezone.utc).isoformat(),
    }


# ── SESSIONS ──────────────────────────────────────────────────


async def open_session(
    agent_id: str,
    anchor_seal_id: str = None,
    declared_intent: str = None,
    risk_tier: str = None,
) -> str:
    """Call at init_anchor_session. Returns session_id."""
    sb = get_supabase()
    if not sb:
        return f"LOCAL_{uuid.uuid4()}"
    session_id = (
        f"SESSION_{agent_id.upper()}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}"
    )
    insert_row = {
        "session_id": session_id,
        "agent_id": agent_id,
        "anchor_seal_id": anchor_seal_id,
        "opened_at": "now()",
    }
    if declared_intent:
        insert_row["declared_intent"] = declared_intent
    if risk_tier:
        insert_row["risk_tier"] = risk_tier
    sb.table("arifosmcp_sessions").insert(insert_row).execute()
    return session_id


async def close_session(
    session_id: str, close_seal_id: str, verdict: str, state_snapshot: dict = None
):
    """Call at session teardown."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("arifosmcp_sessions").update(
        {
            "closed_at": "now()",
            "close_seal_id": close_seal_id,
            "verdict": verdict,
            "state_snapshot": state_snapshot or {},
        }
    ).eq("session_id", session_id).execute()


# ── TOOL CALLS ────────────────────────────────────────────────


async def log_tool_call(
    tool_name: str,
    agent_id: str,
    session_id: str,
    input_hash: str,
    result_code: str,
    duration_ms: int,
    peace2: float = 1.0,
    error_msg: str = None,
):
    """Call from FastMCP tool middleware after every tool execution."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("arifosmcp_tool_calls").insert(
        {
            "tool_name": tool_name,
            "agent_id": agent_id,
            "session_id": session_id,
            "input_hash": input_hash,
            "result_code": result_code,
            "duration_ms": duration_ms,
            "peace2": peace2,
            "error_msg": error_msg,
        }
    ).execute()


# ── CANON RECORDS ─────────────────────────────────────────────


async def write_canon_record(
    record_type: str, reference_id: str, body: dict, verdict: str, witness: dict
):
    """ARCHIVIST agent calls this for every ADR / F13 decision."""
    sb = get_supabase()
    if not sb:
        return
    sb.table("arifosmcp_canon_records").insert(
        {
            "record_type": record_type,
            "reference_id": reference_id,
            "body": body,
            "verdict": verdict,
            "witness": witness,
        }
    ).execute()


# ── AGENT TELEMETRY ───────────────────────────────────────────
# metabolic_guard trigger is already installed — peace2 < 0.5 BLOCKED at DB level


async def write_telemetry(
    agent_id: str,
    peace2: float,
    kappa_r: float,
    dS: float,
    shadow: bool,
    psi_le: float,
    confidence: float,
    tags: dict = None,
):
    """Write constitutional vitals per agent action.
    DB trigger will RAISE EXCEPTION if peace2 < 0.5."""
    sb = get_supabase()
    if not sb:
        return
    metrics = [
        ("peace2", peace2),
        ("kappa_r", kappa_r),
        ("dS", dS),
        ("shadow", 1.0 if shadow else 0.0),
        ("psi_le", psi_le),
        ("confidence", confidence),
    ]
    rows = [
        {"agent_id": agent_id, "metric_name": m, "value": v, "tags": tags or {}} for m, v in metrics
    ]
    sb.table("arifosmcp_agent_telemetry").insert(rows).execute()


async def init_anchor_session(agent_id: str) -> dict:
    """
    Full init sequence:
    1. Read WELL state from Postgres
    2. Read last vault seal for Merkle continuity
    3. Open session record
    4. Write INIT vault seal
    5. Write telemetry
    6. Return anchor context to agent
    """
    sb = get_supabase()
    if not sb:
        return {"error": "Supabase not available"}

    # 1. WELL state
    well = read_well_state(agent_id, "session_context")

    # 2. Last seal
    last_seal = (
        sb.table("arifosmcp_vault_seals")
        .select("id, seal_id, prev_hash, epoch, verdict")
        .order("id", desc=True)
        .limit(1)
        .maybe_single()
        .execute()
    )
    last = last_seal.data or {}

    # 3. Open session
    session_id = await open_session(agent_id, anchor_seal_id=last.get("seal_id"))

    # 4. Init seal
    anchor_seal = await seal_vault(
        seal_id=f"SESSION_INIT_{agent_id.upper()}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        agent_id=agent_id,
        action="SESSION_ANCHOR",
        confidence=1.0,
        payload={
            "session_id": session_id,
            "prev_seal_id": last.get("seal_id"),
            "well_state": well,
            "sealed_by": "Muhammad Arif bin Fazil",
            "motto": "DITEMPA BUKAN DIBERI",
        },
        verdict="SESSION_ANCHORED",
    )

    # 5. Telemetry
    await write_telemetry(
        agent_id=agent_id,
        peace2=1.0,
        kappa_r=0.04,
        dS=0.02,
        shadow=False,
        psi_le=0.02,
        confidence=1.0,
    )

    # 6. Return context
    return {
        "session_id": session_id,
        "anchor_seal": anchor_seal,
        "prev_seal_id": last.get("seal_id"),
        "prev_seal_epoch": last.get("epoch"),
        "well_state": well,
        "constitutional": {"peace2": 1.0, "shadow": False, "floors": "F01-F13 ACTIVE"},
    }
