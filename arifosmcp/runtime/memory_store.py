"""
arifosmcp/runtime/memory_store.py -- 555_MEMORY Canonical Backend v3

CONSOLIDATED: Qdrant (vector search) + Postgres (durable record) dual-write.
Every store() call writes to BOTH backends atomically:
  - Qdrant  → semantic search backbone (arifos_memory collection)
  - Postgres → durable audit record (memory_store table, soft-delete)

Tiers:
  SACRED    → 'sacred'    — immune to prune, never expires
  CANONICAL → 'canon'     — 90-day TTL
  SESSION   → 'session'   — 24-hour TTL
  EPHEMERAL → 'ephemeral' — 1-hour TTL

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_MEMORY_DIR = Path(os.getenv("ARIFOS_MEMORY_DIR", "/root/.arifOS/memory"))
_INDEX_FILE = _MEMORY_DIR / ".qdrant_index.json"
_LEGACY_INDEX_FILE = _MEMORY_DIR / ".index.json"

_QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
_QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arifos_memory")
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")
_PG_URL = os.getenv(
    "ARIFOS_MEMORY_POSTGRES_URL",
    "postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/vault999",
)

# Tier constants
TIER_SACRED = "sacred"
TIER_CANONICAL = "canon"
TIER_SESSION = "session"
TIER_EPHEMERAL = "ephemeral"
_SACRED_TIERS = {TIER_SACRED}

# Normalise incoming tier labels → DB tier strings
_TIER_MAP = {
    "sacred": TIER_SACRED,
    "SACRED": TIER_SACRED,
    "canonical": TIER_CANONICAL,
    "CANONICAL": TIER_CANONICAL,
    "canon": TIER_CANONICAL,
    "CANON": TIER_CANONICAL,
    "session": TIER_SESSION,
    "SESSION": TIER_SESSION,
    "ephemeral": TIER_EPHEMERAL,
    "EPHEMERAL": TIER_EPHEMERAL,
}


def _normalise_tier(tier: str | None) -> str:
    if not tier:
        return TIER_CANONICAL
    return _TIER_MAP.get(tier, TIER_CANONICAL)


# =============================================================================
# POSTGRES ASYNC HELPERS
# =============================================================================


def _pg_run(coro):
    """Run an async coroutine synchronously via a fresh event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _pg_write(
    memory_id: str,
    tier: str,
    text: str,
    metadata: dict,
    qdrant_id: str | None,
    session_id: str | None,
    phoenix_state: str = "cooling",
    cooldown_expiry: datetime | None = None,
    psi_utility: int = 0,
    tri_witness: str = "[false, false, false]",
) -> bool:
    """Insert a memory record into Postgres memory_store table with Phoenix metadata."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5)
        try:
            await conn.execute(
                """
                INSERT INTO memory_store (
                    id, tier, text, metadata, qdrant_id, session_id,
                    phoenix_state, phoenix_cooldown_expiry, phoenix_psi_utility, phoenix_tri_witness
                )
                VALUES ($1::uuid, $2, $3, $4::jsonb, $5::uuid, $6, $7, $8, $9, $10::jsonb)
                ON CONFLICT (id) DO NOTHING
                """,
                memory_id,
                tier,
                text,
                json.dumps(metadata, default=str),
                qdrant_id,
                session_id,
                phoenix_state,
                cooldown_expiry,
                psi_utility,
                tri_witness,
            )
            return True
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("Postgres write failed for %s: %s", memory_id, exc)
        return False


async def _pg_soft_delete(memory_id: str) -> bool:
    """Soft-delete a memory record in Postgres (set deleted_at)."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5)
        try:
            result = await conn.execute(
                "UPDATE memory_store SET deleted_at = now() WHERE id = $1::uuid AND deleted_at IS NULL",  # noqa: E501
                memory_id,
            )
            return result != "UPDATE 0"
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("Postgres soft-delete failed for %s: %s", memory_id, exc)
        return False


async def _pg_load_canonical(actor_id: str, limit: int = 5) -> list[dict]:
    """Load last N canonical memories for an actor from Postgres."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5)
        try:
            rows = await conn.fetch(
                """
                SELECT id::text, tier, text, metadata, session_id, created_at
                FROM memory_store
                WHERE tier IN ('canon', 'sacred')
                  AND deleted_at IS NULL
                  AND (
                    metadata->>'actor_id' = $1
                    OR metadata->>'actor_id' IS NULL
                    OR $1 = 'anonymous'
                  )
                ORDER BY created_at DESC
                LIMIT $2
                """,
                actor_id,
                limit,
            )
            result = []
            for row in rows:
                meta = {}
                try:
                    meta = json.loads(row["metadata"]) if row["metadata"] else {}
                except Exception:
                    pass
                result.append(
                    {
                        "memory_id": row["id"],
                        "tier": row["tier"],
                        "summary": row["text"][:120],
                        "session_id": row["session_id"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "tags": meta.get("tags", []),
                    }
                )
            return result
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("Postgres canonical load failed for %s: %s", actor_id, exc)
        return []


async def _pg_ping() -> bool:
    """Check if Postgres is reachable."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=3)
        await conn.fetchval("SELECT 1")
        await conn.close()
        return True
    except Exception:
        return False


# =============================================================================
# QDRANT HELPERS
# =============================================================================


def _ensure_dir() -> None:
    _MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not _INDEX_FILE.exists():
        _index_write({})


def _index_read() -> dict[str, dict[str, Any]]:
    try:
        with open(_INDEX_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _index_write(idx: dict[str, dict[str, Any]]) -> None:
    with open(_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, default=str)


def _get_qdrant_client():
    from qdrant_client import QdrantClient  # noqa: PLC0415

    # Resolve QDRANT_URL
    qdrant_url = _QDRANT_URL
    if qdrant_url.startswith("ENC["):
        qdrant_url = "http://qdrant:6333"
    return QdrantClient(url=qdrant_url)


def _generate_embedding(text: str) -> list[float]:
    import httpx  # noqa: PLC0415

    response = httpx.post(
        f"{_OLLAMA_URL}/api/embeddings",
        json={"model": _EMBEDDING_MODEL, "prompt": text},
        timeout=30.0,
    )
    response.raise_for_status()
    embedding = response.json().get("embedding", [])
    if not embedding:
        raise RuntimeError("Ollama returned empty embedding")
    return embedding


def _summarize(content: Any) -> str:
    if isinstance(content, str):
        return content[:120].strip()
    if isinstance(content, dict):
        for key in ("synthesis", "verdict", "composed", "summary", "output"):
            if key in content and content[key]:
                val = content[key]
                if isinstance(val, str):
                    return f"[{key}] {val}"[:120].strip()
        return f"dict with keys: {', '.join(list(content.keys())[:5])}"
    if isinstance(content, list):
        return f"list of {len(content)} items"
    return str(type(content).__name__)


def _content_hash(content: Any) -> str:
    return hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()[
        :16
    ]


# =============================================================================
# PUBLIC API
# =============================================================================


def store(
    content: Any,
    mode: str = "unknown",
    tags: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    summary: str | None = None,
    tier: str | None = None,
) -> dict[str, Any]:
    """Dual-write to Qdrant (search) + Postgres (durable record)."""
    _ensure_dir()
    memory_id = uuid.uuid4().hex[:12]
    pg_memory_id = str(uuid.uuid4())  # separate proper UUID for Postgres
    text = _summarize(content)
    normalised_tier = _normalise_tier(tier)

    try:
        vector = _generate_embedding(text)
    except Exception as exc:
        logger.warning("Embedding generation failed: %s", exc)
        vector = []

    payload = {
        "content": content,
        "mode": mode,
        "tags": tags or [],
        "actor_id": actor_id,
        "session_id": session_id,
        "summary": summary or text,
        "content_hash": _content_hash(content),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "tier": normalised_tier,
        "version": "v3",
    }

    # --- Qdrant write ---
    point_id = str(uuid.uuid4())
    qdrant_ok = False
    try:
        from qdrant_client.models import PointStruct  # noqa: PLC0415

        client = _get_qdrant_client()
        client.upsert(
            collection_name=_QDRANT_COLLECTION,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )
        qdrant_ok = True
    except Exception as exc:
        logger.error("Qdrant store failed: %s", exc)

    # --- Phoenix-72 Metadata ---
    # Non-sacred tiers default to 'cooling' state with 72-hour expiry
    is_sacred = normalised_tier in _SACRED_TIERS
    phoenix_state = "sealed" if is_sacred else "cooling"
    cooldown_expiry = None if is_sacred else (datetime.now(timezone.utc) + timedelta(hours=72))

    # --- Postgres dual-write (non-blocking failure) ---
    pg_ok = False
    try:
        pg_ok = _pg_run(
            _pg_write(
                memory_id=pg_memory_id,
                tier=normalised_tier,
                text=text,
                metadata=payload,
                qdrant_id=point_id,
                session_id=session_id,
                phoenix_state=phoenix_state,
                cooldown_expiry=cooldown_expiry,
            )
        )
    except Exception as exc:
        logger.warning("Postgres dual-write skipped: %s", exc)

    # --- JSON index (search assist) ---
    idx = _index_read()
    idx[memory_id] = {
        "point_id": point_id,
        "pg_id": pg_memory_id,
        "mode": mode,
        "tier": normalised_tier,
        "tags": tags or [],
        "summary": payload["summary"],
        "content_hash": payload["content_hash"],
        "created_at": payload["created_at"],
        "session_id": session_id,
    }
    _index_write(idx)

    if not qdrant_ok:
        return {"stored": False, "memory_id": memory_id, "error": "qdrant_write_failed"}

    return {
        "stored": True,
        "memory_id": memory_id,
        "indexed": True,
        "point_id": point_id,
        "pg_id": pg_memory_id,
        "pg_ok": pg_ok,
        "tier": normalised_tier,
        "backends": {"qdrant": qdrant_ok, "postgres": pg_ok},
    }


def recall(memory_id: str) -> dict[str, Any] | None:
    _ensure_dir()
    idx = _index_read()

    if memory_id in idx:
        point_id = idx[memory_id].get("point_id")
        if point_id:
            try:
                client = _get_qdrant_client()
                points = client.retrieve(
                    collection_name=_QDRANT_COLLECTION,
                    ids=[point_id],
                    with_payload=True,
                )
                if points and points[0].payload:
                    p = points[0].payload
                    return {
                        "memory_id": memory_id,
                        "content": p.get("content"),
                        "mode": p.get("mode"),
                        "tags": p.get("tags", []),
                        "actor_id": p.get("actor_id"),
                        "session_id": p.get("session_id"),
                        "summary": p.get("summary"),
                        "content_hash": p.get("content_hash"),
                        "created_at": p.get("created_at"),
                        "tier": p.get("tier", TIER_CANONICAL),
                        "point_id": point_id,
                        "version": p.get("version", "v3"),
                    }
            except Exception as exc:
                logger.warning("Qdrant recall failed for %s: %s", memory_id, exc)

    # Legacy file fallback
    legacy_path = _MEMORY_DIR / f"{memory_id}.json"
    if legacy_path.exists():
        try:
            with open(legacy_path, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    return None


def search(
    query: str | None = None,
    tags: list[str] | None = None,
    mode: str | None = None,
    session_id: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    _ensure_dir()
    idx = _index_read()
    results: list[tuple[float, dict[str, Any]]] = []

    if query and query.strip():
        try:
            vector = _generate_embedding(query)
            client = _get_qdrant_client()
            response = client.query_points(
                collection_name=_QDRANT_COLLECTION,
                query=vector,
                limit=limit * 2,
                with_payload=True,
            )
            for hit in response.points:
                p = hit.payload or {}
                if mode and p.get("mode") != mode:
                    continue
                if session_id and p.get("session_id") != session_id:
                    continue
                if tags and not all(t in p.get("tags", []) for t in tags):
                    continue
                results.append(
                    (
                        hit.score,
                        {
                            "memory_id": "",
                            "content": p.get("content"),
                            "mode": p.get("mode"),
                            "tags": p.get("tags", []),
                            "actor_id": p.get("actor_id"),
                            "session_id": p.get("session_id"),
                            "summary": p.get("summary"),
                            "content_hash": p.get("content_hash"),
                            "created_at": p.get("created_at"),
                            "tier": p.get("tier", TIER_CANONICAL),
                            "point_id": hit.id,
                            "score": hit.score,
                            "version": p.get("version", "v3"),
                        },
                    )
                )
        except Exception as exc:
            logger.warning("Vector search failed: %s", exc)
    else:
        for memory_id, meta in idx.items():
            if mode and meta.get("mode") != mode:
                continue
            if session_id and meta.get("session_id") != session_id:
                continue
            if tags and not all(t in meta.get("tags", []) for t in tags):
                continue
            record = recall(memory_id)
            if record:
                results.append((1.0, record))

    results.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in results[:limit]]


def prune(
    memory_id: str | None = None,
    before: str | None = None,
    reason: str = "manual",
    allow_sacred: bool = False,
) -> dict[str, Any]:
    """Soft-delete memories. SACRED tier is immune unless allow_sacred=True."""
    _ensure_dir()
    idx = _index_read()
    pruned: list[str] = []
    blocked_sacred: list[str] = []

    to_delete: list[str] = []
    if memory_id:
        to_delete = [memory_id]
    elif before:
        for mid, meta in idx.items():
            created = meta.get("created_at", "")
            if created and created < before:
                to_delete.append(mid)

    for mid in to_delete:
        meta = idx.get(mid)
        if not meta:
            continue

        # SACRED tier protection
        tier = meta.get("tier", TIER_CANONICAL)
        if tier in _SACRED_TIERS and not allow_sacred:
            blocked_sacred.append(mid)
            continue

        # Soft-delete in Postgres via pg_id
        pg_id = meta.get("pg_id")
        if pg_id:
            try:
                _pg_run(_pg_soft_delete(pg_id))
            except Exception as exc:
                logger.warning("Postgres soft-delete failed for %s: %s", pg_id, exc)

        # Remove from JSON index (Qdrant point kept for audit, just unlinked)
        if mid in idx:
            del idx[mid]
            pruned.append(mid)

    _index_write(idx)
    return {
        "pruned": pruned,
        "count": len(pruned),
        "reason": reason,
        "blocked_sacred": blocked_sacred,
        "sacred_protected": len(blocked_sacred) > 0,
    }


def context_for_session(
    session_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return search(session_id=session_id, limit=limit)


def load_canonical_for_actor(actor_id: str, limit: int = 5) -> list[dict]:
    """Load last N canonical/sacred memories for an actor. Used at session bootstrap."""
    try:
        return _pg_run(_pg_load_canonical(actor_id, limit))
    except Exception as exc:
        logger.warning("load_canonical_for_actor failed: %s", exc)
        return []


def memory_mode() -> str:
    """Return 'persistent' if both Qdrant and Postgres are reachable, else 'degraded'."""
    qdrant_ok = False
    pg_ok = False

    try:
        client = _get_qdrant_client()
        client.get_collection(_QDRANT_COLLECTION)
        qdrant_ok = True
    except Exception:
        pass

    try:
        pg_ok = _pg_run(_pg_ping())
    except Exception:
        pass

    if qdrant_ok and pg_ok:
        return "persistent"
    if qdrant_ok:
        return "qdrant_only"
    if pg_ok:
        return "postgres_only"
    return "unavailable"


def stats() -> dict[str, Any]:
    _ensure_dir()
    idx = _index_read()
    qdrant_count = 0
    pg_count = 0
    try:
        client = _get_qdrant_client()
        info = client.get_collection(_QDRANT_COLLECTION)
        qdrant_count = info.points_count
    except Exception as exc:
        logger.warning("Qdrant stats unavailable: %s", exc)

    try:
        import asyncpg  # noqa: PLC0415

        async def _pg_stats():
            conn = await asyncpg.connect(_PG_URL, timeout=3)
            try:
                return await conn.fetchval(
                    "SELECT count(*) FROM memory_store WHERE deleted_at IS NULL"
                )
            finally:
                await conn.close()

        pg_count = _pg_run(_pg_stats()) or 0
    except Exception as exc:
        logger.warning("Postgres stats unavailable: %s", exc)

    return {
        "total_records": len(idx),
        "qdrant_vectors": qdrant_count,
        "postgres_records": pg_count,
        "legacy_files": len(list(_MEMORY_DIR.glob("*.json")))
        - (1 if _INDEX_FILE.exists() else 0)
        - (1 if _LEGACY_INDEX_FILE.exists() else 0),
        "by_mode": _mode_counts(idx),
        "by_session": _session_counts(idx),
        "backend": "qdrant_postgres_v3",
        "memory_mode": memory_mode(),
    }


def _mode_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        m = meta.get("mode", "unknown")
        counts[m] = counts.get(m, 0) + 1
    return counts


def _session_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        s = meta.get("session_id") or "none"
        counts[s] = counts.get(s, 0) + 1
    return counts


# =============================================================================
# CLASS INTERFACE (FOR JANITOR & SERVICES)
# =============================================================================


class MemoryStore:
    """Structured interface for arifOS Memory Tiers."""

    def __init__(self):
        self.qdrant = None
        try:
            self.qdrant = _get_qdrant_client()
        except Exception:
            pass
        self._pg_url = _PG_URL

    async def get_pg_conn(self):
        import asyncpg  # noqa: PLC0415

        return await asyncpg.connect(self._pg_url, timeout=5)

    async def get_expired_cooling_entries(self) -> list[dict[str, Any]]:
        """Fetch Phoenix entries where cooling has expired."""
        try:
            conn = await self.get_pg_conn()
            try:
                rows = await conn.fetch(
                    """
                    SELECT id, tier, text, metadata, qdrant_id,
                           phoenix_psi_utility, phoenix_anti_hantu_flag
                    FROM memory_store
                    WHERE phoenix_state = 'cooling'
                      AND phoenix_cooldown_expiry <= NOW()
                      AND deleted_at IS NULL
                    """
                )
                return [dict(r) for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.error("Janitor: Expired fetch failed: %s", exc)
            return []

    async def get_entry(self, memory_id: str) -> dict[str, Any] | None:
        """Fetch memory record by ID."""
        try:
            conn = await self.get_pg_conn()
            try:
                row = await conn.fetchrow(
                    "SELECT id, text, metadata, tier, session_id, "
                    "phoenix_state FROM memory_store WHERE id = $1::uuid",
                    memory_id,
                )
                return dict(row) if row else None
            finally:
                await conn.close()
        except Exception as exc:
            logger.error("Janitor: Fetch failed for %s: %s", memory_id, exc)
            return None

    async def seal_entry(self, memory_id: str) -> bool:
        """Promote entry to CANON and SEALED state with Tier 5 Vault-999 commitment."""
        try:
            # 1. Fetch metadata for vault commitment
            entry = await self.get_entry(memory_id)
            if not entry:
                logger.error("Janitor: Cannot seal missing memory %s", memory_id)
                return False

            # 2. Update Postgres state
            conn = await self.get_pg_conn()
            try:
                await conn.execute(
                    """
                    UPDATE memory_store
                    SET phoenix_state = 'sealed',
                        tier = 'canon',
                        phoenix_sealed_at = NOW()
                    WHERE id = $1::uuid
                    """,
                    memory_id,
                )
            finally:
                await conn.close()

            # 3. ── Tier 5 Vault-999 Sealing (Merkle chain + JSONL) ──
            try:
                from arifosmcp.runtime.vault_postgres import seal_to_vault

                # Extract actor_id from metadata
                metadata = entry.get("metadata") or {}
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except Exception:
                        metadata = {}

                actor_id = metadata.get("actor_id") or "arifOS_janitor"
                session_id = entry.get("session_id") or "system"

                await seal_to_vault(
                    event_type="MEMORY_CANON_SEAL",
                    session_id=session_id,
                    actor_id=actor_id,
                    stage="999_SEAL",
                    verdict="SEAL",
                    payload={
                        "memory_id": str(memory_id),
                        "text_hash": hashlib.sha256(entry.get("text", "").encode()).hexdigest(),
                        "original_tier": entry.get("tier"),
                        "action": "PHOENIX_72_PROMOTION",
                        "sealed_by": "arifOS_janitor",
                    },
                )
                logger.info("Janitor: Tier 5 Vault SEAL complete for %s", memory_id)
            except Exception as v_err:
                logger.warning("Janitor: Vault sealing failed (non-fatal): %s", v_err)

            return True
        except Exception as exc:
            logger.error("Janitor: Seal failed for %s: %s", memory_id, exc)
            return False

    async def void_entry(self, memory_id: str) -> bool:
        """Purge entry from Postgres (soft-delete) and Qdrant."""
        try:
            # 1. Soft delete in Postgres
            await _pg_soft_delete(memory_id)
            logger.info("Janitor: VOIDED %s", memory_id)
            return True
        except Exception as exc:
            logger.error("Janitor: Void failed for %s: %s", memory_id, exc)
            return False


_instance: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    global _instance
    if _instance is None:
        _instance = MemoryStore()
    return _instance


async def _pg_get_all_for_audit(limit: int = 1000, include_deleted: bool = False) -> list[dict]:
    """Fetch all memories from Postgres for auditing purposes."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5)
        try:
            query = """
                SELECT id::text, tier, text, metadata, session_id, created_at, phoenix_state
                FROM memory_store
                WHERE (deleted_at IS NULL OR $1)
                ORDER BY created_at DESC
                LIMIT $2
            """
            rows = await conn.fetch(query, include_deleted, limit)
            result = []
            for row in rows:
                meta = {}
                try:
                    metadata_val = row["metadata"]
                    if isinstance(metadata_val, str):
                        meta = json.loads(metadata_val)
                    else:
                        meta = metadata_val or {}
                except Exception:
                    pass

                # Format to match retrieval gate expectations in f4_retrieval_policy.py
                result.append(
                    {
                        "memory_id": row["id"],
                        "tier": row["tier"],
                        "content": meta.get("content") or row["text"],
                        "summary": row["text"],
                        "tags": meta.get("tags", []),
                        "actor_id": meta.get("actor_id"),
                        "session_id": row["session_id"],
                        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                        "score": 1.0,  # Audit uses base records, no search score
                        "phoenix_state": row["phoenix_state"],
                        "contradiction_signals": meta.get("contradiction_signals", []),
                        "valid_until": meta.get("valid_until"),
                        "sensitivity": meta.get("sensitivity", "public"),
                        "temporal_marker": meta.get("temporal_marker", "active"),
                    }
                )
            return result
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("Audit load failed: %s", exc)
        return []


def get_all_memories_for_audit(limit: int = 1000, include_deleted: bool = False) -> list[dict]:
    """Synchronous wrapper for audit memory retrieval."""
    return _pg_run(_pg_get_all_for_audit(limit, include_deleted))


__all__ = [
    "store",
    "recall",
    "search",
    "prune",
    "context_for_session",
    "load_canonical_for_actor",
    "get_all_memories_for_audit",
    "memory_mode",
    "stats",
    "get_memory_store",
    "MemoryStore",
    "TIER_SACRED",
    "TIER_CANONICAL",
    "TIER_SESSION",
    "TIER_EPHEMERAL",
]
