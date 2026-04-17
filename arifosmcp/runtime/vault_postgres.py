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
    ledger_id: str = "" # Compat

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

    async def seal(self, event: VaultEvent) -> bool:
        if not self.client: return False
        try:
            data = {
                "seal_id": event.event_id,
                "agent_id": event.actor_id,
                "action": event.event_type,
                "payload": event.payload,
                "confidence": 1.0, 
                "epoch": event.sealed_at.isoformat(),
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
        if not ASYNCpg_AVAILABLE or not self.dsn: return None
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(self.dsn, min_size=1)
            except Exception: pass
        return self._pool

    async def seal(self, event: VaultEvent) -> bool:
        pool = await self._get_pool()
        if not pool: return False
        try:
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO vault_events (event_id, event_type, session_id, actor_id, stage, verdict, payload, chain_hash) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                    event.event_id, event.event_type, event.session_id, event.actor_id, event.stage, event.verdict, json.dumps(event.payload), event.chain_hash
                )
            return True
        except Exception: return False

class VaultManager:
    """Orchestrates Dual-Write (Supabase + Local)."""
    def __init__(self):
        self.supabase = SupabaseVaultStore()
        self.postgres = PostgresVaultStore()
        self.fs_path = VAULT_EVENTS_FILE

    async def _get_last_hash(self) -> str:
        return "0" * 64

    async def seal(self, event: VaultEvent) -> SealResult:
        event.merkle_leaf = hashlib.sha256(json.dumps(event.payload, sort_keys=True).encode()).hexdigest()
        prev = await self._get_last_hash()
        event.chain_hash = hashlib.sha256((prev + event.merkle_leaf).encode()).hexdigest()

        sb_success = await self.supabase.seal(event)
        pg_success = await self.postgres.seal(event)

        try:
            VAULT999_PATH.mkdir(parents=True, exist_ok=True)
            with open(self.fs_path, "a") as f:
                f.write(json.dumps({
                    "event_id": event.event_id,
                    "type": event.event_type,
                    "verdict": event.verdict,
                    "hash": event.chain_hash,
                    "ts": event.sealed_at.isoformat()
                }) + "\n")
        except Exception: pass

        return SealResult(
            success=sb_success or pg_success,
            event_id=event.event_id,
            chain_hash=event.chain_hash,
            ledger_id=event.event_id if sb_success else "LOCAL"
        )

async def seal_to_vault(
    event_type: str,
    session_id: str,
    actor_id: str,
    stage: str,
    verdict: str,
    payload: dict[str, Any] | None = None,
    risk_tier: str = "medium",
) -> SealResult:
    mgr = VaultManager()
    event = VaultEvent(
        event_type=event_type,
        session_id=session_id,
        actor_id=actor_id,
        stage=stage,
        verdict=verdict,
        payload=payload or {},
        risk_tier=risk_tier
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
            except Exception: pass

    def read_state(self, agent_id: str, state_key: str) -> dict:
        if not self.client: return {}
        try:
            res = self.client.table("arifosmcp_well_states").select("state_value").eq("agent_id", agent_id).eq("state_key", state_key).maybe_single().execute()
            return res.data["state_value"] if res.data else {}
        except Exception: return {}

    def write_state(self, agent_id: str, state_key: str, value: dict):
        if not self.client: return
        try:
            self.client.table("arifosmcp_well_states").upsert({
                "agent_id": agent_id,
                "state_key": state_key,
                "state_value": value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except Exception: pass
