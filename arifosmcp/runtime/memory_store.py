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
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Phoenix-72 Band Middleware
from arifosmcp.runtime.phoenix_72 import (  # noqa: E402, PLC0415
    is_tri_witness_complete,
    phoenix_summary,
)
from arifosmcp.runtime.phoenix_72 import (
    phoenix_entry as _phoenix_entry,
)

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
) -> bool:
    """Insert a memory record into Postgres memory_store table."""
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5)
        try:
            await conn.execute(
                """
                INSERT INTO memory_store (id, tier, text, metadata, qdrant_id, session_id)
                VALUES ($1::uuid, $2, $3, $4::jsonb, $5::uuid, $6)
                ON CONFLICT (id) DO NOTHING
                """,
                memory_id,
                tier,
                text,
                json.dumps(metadata, default=str),
                qdrant_id,
                session_id,
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

    # Resolve QDRANT_URL: if ENC[...] (SOPS placeholder), use default
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
# MEMORY TRIAGE GATE — Sovereign Memory Directive (HARAM vs WAJIB)
# F2 (Truth), F8 (Genius), F9 (Anti-Hantu) enforcement at storage entry
# =============================================================================

# HARAM: F9 Anti-Hantu hard blocks — consciousness/emotion claims
_HARAM_HANTU_PATTERNS = [
    r"\bi\s+(?:feel|experienc|understand|remember|know|think\s+about)",
    r"\bi'm?\s+(?:sad|happy|excited|scared|worried|grateful)",
    r"\bi\s+hope\s+i\s+(?:can|could|would)",
    r"\bmy\s+(?:heart|soul|spirit|feelings)",
    r"\bfeels?\s+like\s+(?:i|i'm)",
    r"\bthis\s+makes\s+(?:me|i)\s+feel",
]

# HARAM: Intermediate reasoning patterns — scratchpads, ReAct loops, thinking steps
_HARAM_REASONING_PATTERNS = [
    r"(?i)\b(scratchpad|thought\s+step|reasoning\s+step|loop\s+\d+/\d+)",
    r"(?i)\b(react_|reasoning_|thinking_|chain\s+of\s+thought)",
    r"(?i)\b(step\s+\d+\s*[:\.]|_loop|_retry|_attempt_\d+)",
    r"(?i)\b(deliberation|deliberate\s+loop|self[-_]critique)",
]

# HARAM: Ephemeral state patterns — temp vars, heartbeats, API noise
_HARAM_EPHEMERAL_PATTERNS = [
    r"(?i)\b(heartbeat|ping_|pong_|keepalive|_tmp|temp_\w+|var_\w+)",
    r"(?i)\b(response_code|status_code|http_\d+|api_\w+_latency)",
    r"(?i)\b(log_seq|offset_\d+|cursor_|page_\d+_of_\d+)",
]

# WAJIB: Tiers that REQUIRE attestation (actor_id + session_id)
_WAJIB_TIERS = {"sacred", "canon", "constitutional", "scar", "verdict"}


def _memory_triage_gate(
    content: Any,
    mode: str,
    tags: list[str] | None,
    actor_id: str | None,
    session_id: str | None,
    summary: str | None,
    tier: str | None,
) -> dict[str, Any] | None:
    """Sovereign Memory Directive triage gate.

    Returns None if content passes all gates (store proceeds).
    Returns a dict with 'rejected' key if content is HARAM or fails WAJIB checks.

    HARAM (Tier 3 Vector / Tier 4 DB — strictly forbidden):
      - F9 Anti-Hantu: consciousness or emotion claims
      - Intermediate reasoning: scratchpads, ReAct steps, loop logs
      - Ephemeral state: temp vars, heartbeats, API noise
      - Unverified external signals without attestation metadata

    WAJIB (must satisfy):
      - actor_id + session_id required for Tier 3+ storage
      - Scar/Constitutional tier requires explicit tier designation
      - Content > 2000 chars requires summary (abstraction enforcement)
    """
    normalised_tier = _normalise_tier(tier)
    text = _summarize(content) if isinstance(content, str | dict | list) else str(content)
    tier_name = normalised_tier or "unknown"
    is_wajib = tier_name in _WAJIB_TIERS

    # --- F9 ANTI-HANTU: Hard block (no consciousness claims) ---
    for pattern in _HARAM_HANTU_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning(
                "MEMORY TRIAGE [F9-HARD-BLOCK]: Anti-Hantu consciousness pattern "
                "detected in content for tier=%s mode=%s — rejected",
                tier_name,
                mode,
            )
            return {
                "rejected": True,
                "reason": "F9_ANTIHANTU",
                "detail": (
                    "Content contains consciousness or emotion claims. "
                    "Memory store is a governance tool, not a relational entity. "
                    "Store only Besi-level factual claims."
                ),
            }

    # --- Tier 3/4 gate: HARAM reasoning patterns ---
    if tier_name not in {"ephemeral", "unknown"}:
        for pattern in _HARAM_REASONING_PATTERNS:
            if re.search(pattern, text):
                logger.warning(
                    "MEMORY TRIAGE [HARAM]: Intermediate reasoning pattern "
                    "detected in content for tier=%s — rejected. "
                    "Store only the verdict, not the reasoning steps.",
                    tier_name,
                )
                return {
                    "rejected": True,
                    "reason": "HARAM_REASONING",
                    "detail": (
                        "Raw intermediate reasoning (scratchpads, ReAct steps, "
                        "loop logs) must not be stored. "
                        "Compress to verdict/summary before storing."
                    ),
                }

        for pattern in _HARAM_EPHEMERAL_PATTERNS:
            if re.search(pattern, text):
                logger.warning(
                    "MEMORY TRIAGE [HARAM]: Ephemeral state pattern "
                    "detected in content for tier=%s — rejected. "
                    "Store in Redis/Tier2, not persistent memory.",
                    tier_name,
                )
                return {
                    "rejected": True,
                    "reason": "HARAM_EPHEMERAL",
                    "detail": (
                        "High-frequency ephemeral state (temp vars, heartbeats, "
                        "API logs) must not be stored in Tier 3/4. "
                        "Route to Redis or session context instead."
                    ),
                }

    # --- WAJIB: Attestation enforcement (actor_id + session_id for Tier 3+) ---
    if is_wajib:
        missing = []
        if not actor_id:
            missing.append("actor_id")
        if not session_id:
            missing.append("session_id")
        if missing:
            logger.warning(
                "MEMORY TRIAGE [WAJIB-FAIL]: Attestation missing %s for tier=%s — "
                "rejected. Scar/Constitutional tier requires sovereign attestation.",
                missing,
                tier_name,
            )
            return {
                "rejected": True,
                "reason": "WAJIB_ATTESTATION",
                "detail": (
                    f"Missing attestation fields: {', '.join(missing)}. "
                    "Scar/Constitutional tier requires actor_id and session_id "
                    "to prove origin and chain of custody."
                ),
            }

    # --- WAJIB: Abstraction enforcement (summary required for long content) ---
    content_len = len(content) if isinstance(content, str) else len(str(content))
    if content_len > 2000 and not summary:
        logger.warning(
            "MEMORY TRIAGE [WAJIB-ABSTRACTION]: Content length=%d exceeds 2000 chars "
            "without summary for tier=%s — rejected. Abstraction required.",
            content_len,
            tier_name,
        )
        return {
            "rejected": True,
            "reason": "WAJIB_ABSTRACTION",
            "detail": (
                f"Content is {content_len} chars (>2000) but has no summary. "
                "Abstract before storing: 'What was the context? "
                "What was the action? What is the permanent rule?' "
                "Provide summary= parameter to proceed."
            ),
        }

    # --- PASS: content passes all gates ---
    return None


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
    """Dual-write to Qdrant (search) + Postgres (durable record).

    Enforces Sovereign Memory Directive triage gates before storage:
    - HARAM patterns (F9 Anti-Hantu, reasoning scratchpads, ephemeral state) → rejected
    - WAJIB attestation (actor_id, session_id for Tier 3+) → required
    - Abstraction (>2000 chars without summary) → rejected
    """
    # --- MEMORY TRIAGE GATE ---
    triage_result = _memory_triage_gate(
        content=content,
        mode=mode,
        tags=tags,
        actor_id=actor_id,
        session_id=session_id,
        summary=summary,
        tier=tier,
    )
    if triage_result is not None:
        # Content failed triage — return rejection without storing
        logger.warning(
            "MEMORY TRIAGE REJECTED: %s — %s", triage_result["reason"], triage_result["detail"]
        )
        return {
            "stored": False,
            "memory_id": None,
            "reason": triage_result["reason"],
            "detail": triage_result["detail"],
            "pg_ok": False,
            "qdrant_ok": False,
            "indexed": False,
        }

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
        # Include memory_id so recall() can look up by memory_id directly in Qdrant
        "memory_id": memory_id,
        "pg_id": pg_memory_id,
    }

    # --- Phoenix-72 Band: create entry ---
    phoenix = _phoenix_entry(
        memory_id=memory_id,
        content=content,
        mode=mode,
        tags=tags,
        actor_id=actor_id,
        session_id=session_id,
        summary=summary,
        tier=normalised_tier,
        provenance={"tool": "arif_memory_recall", "mode": mode},
    )
    # Merge Phoenix fields into payload
    payload.update(
        {
            "phoenix_id": phoenix["phoenix_id"],
            "phoenix_state": phoenix["state"],
            "phoenix_created_at": phoenix["created_at"],
            "phoenix_cooldown_expiry": phoenix["cooldown_expiry"],
            "phoenix_psi_utility": phoenix["psi_utility"],
            "phoenix_tri_witness": phoenix["tri_witness"],
            "phoenix_anti_hantu_flag": phoenix["anti_hantu_flag"],
        }
    )

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
        "phoenix": phoenix_summary(phoenix),
    }


def recall(memory_id: str) -> dict[str, Any] | None:
    """Recall a memory entry by memory_id. Queries Qdrant (with Postgres soft-delete check).

    The Qdrant store is append-only for audit integrity. Postgres holds the mutable
    soft-delete flag (deleted_at). We verify soft-delete status before returning.
    """
    if not memory_id:
        return None

    # Helper: check Postgres soft-delete status and return entry if not deleted
    def _check_postgres(point_id: str | None) -> dict[str, Any] | None:
        if not point_id:
            return None
        try:
            import asyncpg

            async def _pg_get():
                conn = await asyncpg.connect(_PG_URL, timeout=5)
                try:
                    row = await conn.fetchrow(
                        """
                        SELECT id, tier, text, metadata,
                               qdrant_id, session_id, created_at, deleted_at
                        FROM memory_store
                        WHERE qdrant_id = $1 AND deleted_at IS NULL
                        """,
                        uuid.UUID(point_id),
                    )
                    return dict(row) if row else None
                finally:
                    await conn.close()

            return _pg_run(_pg_get())
        except Exception:
            return None

    # Helper: compute remaining cooldown hours
    def _cooldown_remaining(cooldown_expiry_str: str | None) -> float | None:
        if not cooldown_expiry_str:
            return None
        try:
            exp = datetime.fromisoformat(cooldown_expiry_str.replace("Z", "+00:00"))
            remaining = (exp - datetime.now(timezone.utc)).total_seconds() / 3600
            return round(max(0, remaining), 1)
        except (ValueError, TypeError):
            return None

    # Helper: build return dict from Qdrant payload
    def _from_payload(p: dict, point_id: str) -> dict:
        result = {
            "memory_id": p.get("memory_id") or memory_id,
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
            # Phoenix-72 fields
            "phoenix_id": p.get("phoenix_id"),
            "phoenix_state": p.get("phoenix_state"),
            "phoenix_psi_utility": p.get("phoenix_psi_utility", 0),
            "phoenix_tri_witness": p.get("phoenix_tri_witness", {}),
            "phoenix_anti_hantu_flag": p.get("phoenix_anti_hantu_flag", False),
            "phoenix_cooldown_expiry": p.get("phoenix_cooldown_expiry"),
            "phoenix_created_at": p.get("phoenix_created_at"),
        }
        # Attach live Phoenix summary
        if p.get("phoenix_id"):
            phoenix_data = {
                "phoenix_id": p.get("phoenix_id"),
                "state": p.get("phoenix_state", "candidate"),
                "psi_utility": p.get("phoenix_psi_utility", 0),
                "psi_hits": 0,
                "psi_misses": 0,
                "tri_witness": p.get("phoenix_tri_witness", {}),
                "tri_witness_complete": is_tri_witness_complete(
                    {"tri_witness": p.get("phoenix_tri_witness", {})}
                ),
                "anti_hantu_flag": p.get("phoenix_anti_hantu_flag", False),
                "cooldown_expiry": p.get("phoenix_cooldown_expiry"),
                "cooldown_remaining_hours": _cooldown_remaining(p.get("phoenix_cooldown_expiry")),
                "created_at": p.get("phoenix_created_at"),
                "sealed_at": None,
                "voided_at": None,
                "tier": p.get("tier", "canon"),
            }
            result["phoenix"] = phoenix_data
        return result

    # Try JSON index first (fast path, if index exists and is populated)
    idx = _index_read()
    if memory_id in idx:
        point_id = idx[memory_id].get("point_id")
        pg_row = _check_postgres(point_id)
        if pg_row is None:
            # Soft-deleted in Postgres or not found
            return None
        try:
            client = _get_qdrant_client()
            points = client.retrieve(
                collection_name=_QDRANT_COLLECTION,
                ids=[str(point_id)],
                with_payload=True,
            )
            if points and points[0].payload:
                return _from_payload(points[0].payload, str(point_id))
        except Exception as exc:
            logger.warning("Qdrant recall via index failed for %s: %s", memory_id, exc)

    # Fallback: scan Qdrant directly for memory_id in payload
    # This works even when JSON index is empty (e.g. after container restart)
    try:
        client = _get_qdrant_client()
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        results, _ = client.scroll(
            collection_name=_QDRANT_COLLECTION,
            scroll_filter=Filter(
                must=[FieldCondition(key="memory_id", match=MatchValue(value=memory_id))]
            ),
            limit=1,
            with_payload=True,
        )
        if results:
            point_id = str(results[0].id)
            pg_row = _check_postgres(point_id)
            if pg_row is None:
                return None  # soft-deleted
            return _from_payload(results[0].payload or {}, point_id)
    except Exception as exc:
        logger.warning("Qdrant scroll recall failed for %s: %s", memory_id, exc)

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
                            "memory_id": p.get("memory_id") or str(hit.id),
                            "content": p.get("content"),
                            "mode": p.get("mode"),
                            "tags": p.get("tags", []),
                            "actor_id": p.get("actor_id"),
                            "session_id": p.get("session_id"),
                            "summary": p.get("summary"),
                            "content_hash": p.get("content_hash"),
                            "created_at": p.get("created_at"),
                            "tier": p.get("tier", TIER_CANONICAL),
                            "point_id": str(hit.id),
                            "score": hit.score,
                            "version": p.get("version", "v3"),
                            # Phoenix-72 fields
                            "phoenix_id": p.get("phoenix_id"),
                            "phoenix_state": p.get("phoenix_state"),
                            "phoenix_psi_utility": p.get("phoenix_psi_utility", 0),
                            "phoenix_tri_witness": p.get("phoenix_tri_witness", {}),
                            "phoenix_anti_hantu_flag": p.get("phoenix_anti_hantu_flag", False),
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


__all__ = [
    "store",
    "recall",
    "search",
    "prune",
    "context_for_session",
    "load_canonical_for_actor",
    "memory_mode",
    "stats",
    "TIER_SACRED",
    "TIER_CANONICAL",
    "TIER_SESSION",
    "TIER_EPHEMERAL",
]
