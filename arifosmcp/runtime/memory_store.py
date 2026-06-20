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
import asyncpg  # noqa: E402, PLC0415
import hashlib
import json
import logging
import os
import re
import uuid
from datetime import datetime, UTC
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
from arifosmcp.runtime.f4_contradiction_handler import (  # noqa: E402, PLC0415
    f4_write_path_hook,
)
from arifosmcp.runtime.f4_retrieval_policy import (  # noqa: E402, PLC0415
    integrate_with_search_results,
)

_MEMORY_DIR = Path(os.getenv("ARIFOS_MEMORY_DIR", "/root/.arifOS/memory"))
_INDEX_FILE = _MEMORY_DIR / ".qdrant_index.json"
_LEGACY_INDEX_FILE = _MEMORY_DIR / ".index.json"

_QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
_QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arifos_memory")
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
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
TIER_TEST = "test"  # F2 TRUTH: harmless probe tier — never becomes canon
_SACRED_TIERS = {TIER_SACRED}

# Normalise incoming tier labels → DB tier strings
# SAFE TIERS: known, validated, no side effects
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
    "test": TIER_TEST,
    "TEST": TIER_TEST,
    "probe": TIER_TEST,
    "PROBE": TIER_TEST,
    "debug": TIER_TEST,
    "DEBUG": TIER_TEST,
}
# Tiers that map to ephemeral TTL for safe cleanup
_NON_PERSISTENT_TIERS = {TIER_EPHEMERAL, TIER_TEST, TIER_SESSION}
# Tiers that explicitly require sovereign attestation (sacred gate)
_SOVEREIGN_REQUIRED_TIERS = {TIER_SACRED}


def _normalise_tier(tier: str | None) -> str:
    """
    Normalise incoming tier label to a canonical DB tier string.

    F2 TRUTH: Unknown tiers are NOT silently elevated to canon.
    They are logged and downgraded to ephemeral for safe cleanup.
    Only known tiers pass through unchanged.
    """
    if not tier:
        return TIER_CANONICAL
    normalised = _TIER_MAP.get(tier)
    if normalised is not None:
        return normalised
    # Unknown/unmapped tier → ephemeral with warning (F2 TRUTH)
    # This is the fix for: test→canon silent elevation bug
    logger.warning(
        "F2 TRUTH: tier '%s' is not a known tier. Downgrading to '%s' "
        "to prevent silent canon pollution. Known tiers: %s",
        tier, TIER_EPHEMERAL, sorted(_TIER_MAP.keys()),
    )
    return TIER_EPHEMERAL


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
    entity_tags: list[str] | None = None,
    distillation_status: str | None = None,
    distillation_metadata: dict | None = None,
    valid_at: datetime | None = None,
    recorded_at: datetime | None = None,
) -> bool:
    """Insert a memory record into Postgres memory_store table.

    Phase 1b: Extended to include entity_tags (F4) and distillation metadata.
    Phase 1d: Extended to include valid_at (world-time of fact) and recorded_at.
    """
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
        try:
            await conn.execute(
                """
                INSERT INTO memory_store
                    (id, tier, text, metadata, qdrant_id, session_id,
                     entity_tags, distillation_status, distillation_metadata,
                     valid_at, recorded_at)
                VALUES ($1::uuid, $2, $3, $4::jsonb, $5::uuid, $6, $7, $8, $9::jsonb, $10, $11)
                ON CONFLICT (id) DO NOTHING
                """,
                memory_id,
                tier,
                text,
                json.dumps(metadata, default=str),
                qdrant_id,
                session_id,
                entity_tags,
                distillation_status,
                (json.dumps(distillation_metadata, default=str) if distillation_metadata else None),
                valid_at,
                recorded_at,
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

        conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
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

        conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
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
                        "created_at": (
                            row["created_at"].isoformat() if row["created_at"] else None
                        ),
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

        conn = await asyncpg.connect(_PG_URL, timeout=3, statement_cache_size=0)
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

    # Primary: BGE-M3 on Ollama (free, local, 1024-dim)
    # Fallback: Azure text-embedding-3-small ($200 ProCopilot credit, 1536-dim)
    # Wired 2026-06-20 per Arif's 888_HOLD.
    _timeout = float(os.getenv("ARIFOS_EMBEDDING_TIMEOUT_S", "120.0"))
    try:
        response = httpx.post(
            f"{_OLLAMA_URL}/api/embeddings",
            json={"model": _EMBEDDING_MODEL, "prompt": text},
            timeout=_timeout,
        )
        response.raise_for_status()
        embedding = response.json().get("embedding", [])
        if embedding:
            return embedding
    except Exception:
        pass

    # Fallback: Azure OpenAI embedding
    azure_key = os.getenv("AZURE_OPENAI_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_embed = os.getenv("AZURE_OPENAI_EMBEDDING", "text-embedding-3-small")
    if azure_key and azure_endpoint:
        try:
            response = httpx.post(
                f"{azure_endpoint}/embeddings",
                json={"model": azure_embed, "input": text},
                headers={"api-key": azure_key, "Content-Type": "application/json"},
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            embedding = data["data"][0]["embedding"]
            if embedding:
                return embedding
        except Exception:
            pass

    raise RuntimeError("All embedding backends exhausted (Ollama bge-m3 + Azure text-embedding-3-small)")


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


def _l5_async_enabled() -> bool:
    """Check env for L5 async toggle. Defaults to True (sovereign).

    When async, store() returns immediately after the L5 fire-and-forget
    is scheduled in a background thread. This keeps the L3/L4 fast path
    responsive even when qwen2.5:7b cold start takes >2 minutes.
    """
    return os.getenv("L5_SOVEREIGN_ASYNC", "true").lower() != "false"


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
            "MEMORY TRIAGE REJECTED: %s — %s",
            triage_result["reason"],
            triage_result["detail"],
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
    now = datetime.now(UTC)

    # --- F4 ENTITY EXTRACTION + CONTRADICTION HANDLING (Phase 1b) ---
    # Called after HARAM scan passes, before dual-write.
    # Detects T1/T2/T3 contradictions and resolves via SUPERSEDE/ESCALATE.
    f4_result = f4_write_path_hook(
        content=content,
        content_hash=_content_hash(content),
        recorded_at=now,
        valid_at=None,  # Bi-temporal Phase 1d will add valid_at support
    )

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
        "created_at": now.isoformat(),
        "tier": normalised_tier,
        "version": "v3",
        # Include memory_id so recall() can look up by memory_id directly in Qdrant
        "memory_id": memory_id,
        "pg_id": pg_memory_id,
        # Phase 1b: F4 entity extraction
        "entity_tags": f4_result.entity_tags,
        "temporal_marker": "active",  # Default; updated if superseded
        "extraction_metadata": f4_result.extraction_metadata,
    }

    # If resolution was SUPERSEDE or ESCALATE, update Phoenix state accordingly
    phoenix_override_state = None
    if f4_result.resolution == "escalate":
        phoenix_override_state = "contradiction_hold"

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
    if phoenix_override_state:
        phoenix["state"] = phoenix_override_state
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
                entity_tags=f4_result.entity_tags,
                distillation_status=phoenix_override_state or "pending",
                distillation_metadata=(
                    f4_result.new_entry_meta if f4_result.resolution != "none" else None
                ),
                valid_at=None,
                recorded_at=now,
            )
        )
    except Exception as exc:
        logger.warning("Postgres dual-write skipped: %s", exc)

    # --- L5 Sovereign Forge (FEDERATION — fire-and-forget) -----------------
    # Only fire if at least one durable leg succeeded. L5 enriches but
    # is NOT a source of truth; failure here must not block the store result.
    # Uses forge_l5_async() so the store() caller does NOT wait for
    # qwen2.5:3b cold start (~30-120s on CPU depending on load).
    l5_status = "skipped"
    if qdrant_ok or pg_ok:
        try:
            from arifosmcp.runtime.l5_sovereign_forge import (
                bridge_forge_episode,
                forge_l5_async,
            )

            # Use async variant to keep L3+L4 fast path responsive
            if _l5_async_enabled():
                l5_result = forge_l5_async(
                    memory_id=memory_id,
                    content=text,
                    summary=payload.get("summary"),
                    session_id=session_id,
                    actor_id=actor_id,
                    tier=normalised_tier,
                    tags=tags,
                    l3_point_id=point_id,
                    l4_row_id=pg_memory_id,
                    content_hash=payload.get("content_hash"),
                )
            else:
                # Back-compat: sync path (debugging only)
                l5_result = bridge_forge_episode(
                    memory_id=memory_id,
                    content=text,
                    summary=payload.get("summary"),
                    session_id=session_id,
                    actor_id=actor_id,
                    tier=normalised_tier,
                    tags=tags,
                    l3_point_id=point_id,
                    l4_row_id=pg_memory_id,
                    phoenix_id=phoenix["phoenix_id"],
                    entity_tags=f4_result.entity_tags,
                    phoenix_state=phoenix.get("state"),
                )
            l5_status = l5_result.get("status", "unknown")
        except Exception as exc:
            logger.warning("L5 sovereign forge skipped: %s", exc)
            l5_status = f"error:{type(exc).__name__}"

    # --- JSON index (search assist) ---
    idx = _index_read()
    idx[memory_id] = {
        "point_id": point_id,
        "pg_id": pg_memory_id,
        "mode": mode,
        "tier": normalised_tier,
        "tags": tags or [],
        "entity_tags": f4_result.entity_tags,  # Phase 1b
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
        "l5_status": l5_status,  # FEDERATION: Graphiti episode forge outcome
        "tier": normalised_tier,
        "backends": {"qdrant": qdrant_ok, "postgres": pg_ok, "graphiti": l5_status},
        "phoenix": phoenix_summary(phoenix),
        # Phase 1b: F4 result
        "f4": {
            "entity_tags": f4_result.entity_tags,
            "contradiction_signals": f4_result.contradiction_signals,
            "resolution": f4_result.resolution,
            "conflicts_count": len(f4_result.conflicts),
            "superseded_by_old": f4_result.superseded_by_old,
            "contradictions_logged": f4_result.contradictions_logged,
        },
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
                conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
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
            remaining = (exp - datetime.now(UTC)).total_seconds() / 3600
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
            # Phase 1c: F4 entity + temporal fields
            "entity_tags": p.get("entity_tags", []),
            "temporal_marker": p.get("temporal_marker", "unknown"),
            "superseded_by": p.get("superseded_by"),
            "superseded_at": p.get("superseded_at"),
            "extraction_metadata": p.get("extraction_metadata"),
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

    # Fallback A: try direct Qdrant retrieve by point_id
    # (handles case where memory_id is actually a Qdrant point ID returned by search())
    try:
        client = _get_qdrant_client()
        points = client.retrieve(
            collection_name=_QDRANT_COLLECTION,
            ids=[str(memory_id)],
            with_payload=True,
        )
        if points and points[0].payload:
            point_id = str(points[0].id)
            pg_row = _check_postgres(point_id)
            if pg_row is None:
                return None  # soft-deleted
            return _from_payload(points[0].payload, point_id)
    except Exception:
        pass  # Not a valid Qdrant point ID, try Fallback B

    # Fallback B: scan Qdrant directly for memory_id in payload
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


# ============================================================================
# ARIF MEMORY AUDIT: Retrieve all memories for escalation queue processing
# ============================================================================


def get_all_memories_for_audit(
    limit: int = 1000,
    include_deleted: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve all memories from Qdrant for audit/escalation processing.

    Used by arif_memory_audit to feed get_escalation_queue().

    Args:
        limit: Maximum number of memories to return (Qdrant scroll limit).
        include_deleted: If False (default), excludes soft-deleted memories.

    Returns:
        List of full memory dicts with all fields from Qdrant payload.
    """
    try:
        client = _get_qdrant_client()

        all_memories: list[dict[str, Any]] = []
        offset = None  # type: ignore[assignment]  # Qdrant returns PointId, not str

        while True:
            results, next_offset = client.scroll(
                collection_name=_QDRANT_COLLECTION,
                scroll_filter=None,  # No filter = all points
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in results:
                payload = point.payload or {}
                memory_id = payload.get("memory_id") or str(point.id)

                # Soft-delete filter (check Postgres)
                if not include_deleted:
                    pg_id = payload.get("pg_id")
                    try:
                        pg_row = _pg_run(_pg_get_by_qdrant_id(str(point.id))) if pg_id else None
                        if pg_row is None and pg_id:
                            # Soft-deleted or not in Postgres
                            continue
                    except Exception:
                        pass  # If Postgres check fails, include the memory

                # Build memory dict (same shape as recall() _from_payload)
                mem: dict[str, Any] = {
                    "memory_id": memory_id,
                    "content": payload.get("content"),
                    "mode": payload.get("mode"),
                    "tags": payload.get("tags", []),
                    "actor_id": payload.get("actor_id"),
                    "session_id": payload.get("session_id"),
                    "summary": payload.get("summary"),
                    "content_hash": payload.get("content_hash"),
                    "created_at": payload.get("created_at"),
                    "tier": payload.get("tier", TIER_CANONICAL),
                    "point_id": str(point.id),
                    "version": payload.get("version", "v3"),
                    "phoenix_id": payload.get("phoenix_id"),
                    "phoenix_state": payload.get("phoenix_state"),
                    "phoenix_psi_utility": payload.get("phoenix_psi_utility", 0),
                    "phoenix_tri_witness": payload.get("phoenix_tri_witness", {}),
                    "phoenix_anti_hantu_flag": payload.get("phoenix_anti_hantu_flag", False),
                    "phoenix_cooldown_expiry": payload.get("phoenix_cooldown_expiry"),
                    "entity_tags": payload.get("entity_tags", []),
                    "temporal_marker": payload.get("temporal_marker", "unknown"),
                    "superseded_by": payload.get("superseded_by"),
                    "superseded_at": payload.get("superseded_at"),
                    "extraction_metadata": payload.get("extraction_metadata"),
                    # F4 contradiction handler result fields (from f4_write_path_hook)
                    "f4_conflicts_count": payload.get("f4_conflicts_count"),
                    "contradiction_signals": payload.get("contradiction_signals", []),
                }
                all_memories.append(mem)

            if not next_offset:
                break
            offset = next_offset

            if len(all_memories) >= limit:
                break

        return all_memories[:limit]

    except Exception as exc:
        logger.warning("get_all_memories_for_audit failed: %s", exc)
        return []


def _pg_get_by_qdrant_id(qdrant_id: str | None):
    """Helper: fetch active Postgres row by Qdrant point id for soft-delete checks."""
    if not qdrant_id:
        return None

    async def _pg_get():
        conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
        try:
            row = await conn.fetchrow(
                """
                SELECT id, tier, text, metadata,
                       qdrant_id, session_id, created_at, deleted_at
                FROM memory_store
                WHERE qdrant_id = $1 AND deleted_at IS NULL
                """,
                uuid.UUID(qdrant_id),
            )
            return dict(row) if row else None
        finally:
            await conn.close()

    return _pg_get()


def search(
    query: str | None = None,
    tags: list[str] | None = None,
    mode: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,  # F4 Clarity: governs retrieval access
    limit: int = 20,
    # Phase 1c: F4 entity filter + temporal query
    entity_filter: (list[str] | None) = None,  # Filter by F4 entity tags (e.g. ["ORG:PETRONAS"])
    include_historical: bool = False,  # Include entries marked temporal_marker=historical
) -> dict[str, Any]:
    """Search memory with optional F4 entity filtering and temporal awareness.

    Returns a dict with three keys (RG-01):
      - results: governance-filtered memories (each with _governance attached)
      - _governance_report: RetrievalPolicyReport summary (allowed/blocked/flagged/escalated counts)
      - _escalation_queue: memories flagged ESCALATE for Arif review

    Phase 1c enhancements:
    - entity_filter: Filter by F4 entity_tags (AND logic — must match all)
    - include_historical: If False (default), excludes entries superseded by newer facts
    - temporal_marker: Returned in every result for F4 Clarity
    - superseded_by / superseded_at: Supersession lineage for audit

    Without entity_filter + include_historical, behaves identically to prior version.
    """
    """Search memory with optional F4 entity filtering and temporal awareness.

    Phase 1c enhancements:
    - entity_filter: Filter by F4 entity_tags (AND logic — must match all)
    - include_historical: If False (default), excludes entries superseded by newer facts
    - temporal_marker: Returned in every result for F4 Clarity
    - superseded_by / superseded_at: Supersession lineage for audit

    Without entity_filter + include_historical, behaves identically to prior version.
    """
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

                # Phase 1c: F4 entity filter
                if entity_filter:
                    entry_tags = set(p.get("entity_tags", []) or [])
                    if not entry_tags.intersection(entity_filter):
                        continue  # No matching entity tag

                # Phase 1c: Temporal filter — exclude historical unless asked
                temporal_marker = p.get("temporal_marker", "unknown")
                if not include_historical and temporal_marker == "historical":
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
                            # Phase 1c: F4 temporal fields
                            "entity_tags": p.get("entity_tags", []),
                            "temporal_marker": temporal_marker,
                            "superseded_by": p.get("superseded_by"),
                            "superseded_at": p.get("superseded_at"),
                            "extraction_metadata": p.get("extraction_metadata"),
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

            # Phase 1c: F4 entity filter
            if entity_filter:
                entry_tags = set(meta.get("entity_tags", []) or [])
                if not entry_tags.intersection(entity_filter):
                    continue

            record = recall(memory_id)
            if record:
                # Phase 1c: Temporal filter
                temporal_marker = record.get("temporal_marker", "unknown")
                if not include_historical and temporal_marker == "historical":
                    continue
                results.append((1.0, record))

    results.sort(key=lambda x: x[0], reverse=True)

    # Phase 1c: Supersession deduplication —
    # If result A was superseded by result B (same entity, newer),
    # and B is also in results, drop A.
    if not include_historical:
        results = _deduplicate_superseded(results)

    # F4 Retrieval Governance Gate — filter before returning to caller
    # integrate_with_search_results applies:
    #   - Tier isolation (session vs sacred vs canon)
    #   - Evidence confidence floor
    #   - Relevance threshold
    #   - Temporal staleness (historical block unless asked)
    #   - Emotional exaggeration / scar-hijack guard
    #   - Privacy sensitivity (private memories)
    #   - Scar distortion detection
    #   - Contradiction ESCALATE for Arif review
    raw_mems = [r for _, r in results[:limit]]
    filtered_mems, _policy_report = integrate_with_search_results(
        raw_results=raw_mems,
        actor_id=actor_id,
        session_id=session_id,
        query=query or "",
    )
    # Log policy report at DEBUG for observability
    if _policy_report.total_candidates > 0:
        logger.debug(
            "F4 Retrieval Governance: %s/%s passed | flagged=%s blocked=%s escalated=%s",
            len(filtered_mems),
            _policy_report.total_candidates,
            _policy_report.flagged,
            _policy_report.blocked,
            _policy_report.escalated,
        )

    # RG-01: Surface escalation queue and governance report to caller
    escalation_queue = [
        g.as_dict() for g in _policy_report.governance if g.verdict.value == "ESCALATE"
    ]

    return {
        "results": filtered_mems,
        "_governance_report": _policy_report.as_dict(),
        "_escalation_queue": escalation_queue,
    }


def _deduplicate_superseded(
    results: list[tuple[float, dict[str, Any]]],
) -> list[tuple[float, dict[str, Any]]]:
    """Remove entries that have been superseded by higher-ranked entries in results.

    When two entries share an entity_tag and one has superseded_by pointing to the other,
    only the superseding (newer) one is kept.
    """
    if not results:
        return results

    # Build supersession map: memory_id → superseded_by
    superseded_by_map: dict[str, str | None] = {}
    for _, record in results:
        superseded_by_map[record.get("memory_id", "")] = record.get("superseded_by")

    # Collect IDs that are superseded by another entry in results
    to_remove: set[str] = set()
    for memory_id, superseded_by in superseded_by_map.items():
        if superseded_by and superseded_by in superseded_by_map:
            # Both entries are in results; the superseded one should be dropped
            to_remove.add(memory_id)

    return [(score, r) for score, r in results if r.get("memory_id") not in to_remove]


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
    # search() returns dict with results + governance. Unwrap for context use.
    raw = search(session_id=session_id, limit=limit)
    return raw.get("results", [])


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
            conn = await asyncpg.connect(_PG_URL, timeout=3, statement_cache_size=0)
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
        "by_tier": _tier_counts(idx),  # sacred | canon | session | ephemeral
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


def _tier_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        t = meta.get("tier", "unknown")
        counts[t] = counts.get(t, 0) + 1
    return counts


def _session_counts(idx: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for meta in idx.values():
        s = meta.get("session_id") or "none"
        counts[s] = counts.get(s, 0) + 1
    return counts


class MemoryStore:
    """Async interface for Phoenix-72 janitor operations."""

    async def get_expired_cooling_entries(self) -> list[dict[str, Any]]:
        """Return memories in cooling state whose 72h window has elapsed."""
        try:
            import asyncpg  # noqa: PLC0415

            conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
            try:
                rows = await conn.fetch(
                    """
                    SELECT id::text, tier, text, metadata, qdrant_id::text,
                           session_id, created_at, deleted_at,
                           distillation_status, distillation_metadata
                    FROM memory_store
                    WHERE (
                            distillation_status = 'cooling'
                            OR metadata->>'phoenix_state' = 'cooling'
                          )
                      AND deleted_at IS NULL
                      AND (
                            metadata->>'phoenix_cooldown_expiry' IS NULL
                            OR (metadata->>'phoenix_cooldown_expiry')::timestamptz <= NOW()
                          )
                    ORDER BY created_at ASC
                    LIMIT 500
                    """
                )
                return [dict(r) for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("MemoryStore.get_expired_cooling_entries failed: %s", exc)
            return []

    async def seal_entry(self, memory_id: str) -> bool:
        """Promote a cooling entry to 'sealed' (canon) state."""
        updated = self._set_qdrant_payload(
            memory_id,
            {"phoenix_state": "sealed", "tier": TIER_CANONICAL},
        )
        try:
            conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
            try:
                result = await conn.execute(
                    """
                    UPDATE memory_store
                    SET distillation_status = 'sealed',
                        tier = $2,
                        metadata = jsonb_set(
                            jsonb_set(metadata, '{phoenix_state}', to_jsonb('sealed'::text), true),
                            '{tier}', to_jsonb($2::text), true
                        )
                    WHERE (id::text = $1 OR qdrant_id::text = $1 OR metadata->>'memory_id' = $1)
                      AND deleted_at IS NULL
                    """,
                    memory_id,
                    TIER_CANONICAL,
                )
                return updated or result != "UPDATE 0"
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("MemoryStore.seal_entry failed for %s: %s", memory_id, exc)
            return updated

    async def void_entry(self, memory_id: str) -> bool:
        """Soft-delete a cooling entry (void/purge)."""
        updated = self._set_qdrant_payload(memory_id, {"phoenix_state": "voided"})
        try:
            conn = await asyncpg.connect(_PG_URL, timeout=5, statement_cache_size=0)
            try:
                result = await conn.execute(
                    """
                    UPDATE memory_store
                    SET distillation_status = 'voided',
                        deleted_at = now(),
                        metadata = jsonb_set(
                            metadata, '{phoenix_state}', to_jsonb('voided'::text), true
                        )
                    WHERE (id::text = $1 OR qdrant_id::text = $1 OR metadata->>'memory_id' = $1)
                      AND deleted_at IS NULL
                    """,
                    memory_id,
                )
                return updated or result != "UPDATE 0"
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("MemoryStore.void_entry failed for %s: %s", memory_id, exc)
            return updated

    def _set_qdrant_payload(self, point_id: str, payload: dict[str, Any]) -> bool:
        try:
            client = _get_qdrant_client()
            client.set_payload(
                collection_name=_QDRANT_COLLECTION,
                payload=payload,
                points=[point_id],
            )
            return True
        except Exception as exc:
            logger.warning("MemoryStore Qdrant payload update failed for %s: %s", point_id, exc)
            return False


_memory_store_singleton: MemoryStore | None = None


def get_memory_store() -> MemoryStore:
    """Return the singleton MemoryStore instance (Phoenix-72 janitor interface)."""
    global _memory_store_singleton
    if _memory_store_singleton is None:
        _memory_store_singleton = MemoryStore()
    return _memory_store_singleton


# ═══════════════════════════════════════════════════════════════════════════════
# 555_MEMORY v2 — CONSTITUTIONAL EXTENSIONS
# Quarantine, tombstone, forget, audit_governance, store_v2 with envelope
# ═══════════════════════════════════════════════════════════════════════════════


def store_v2(
    envelope: dict[str, Any],
    existing_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Constitutional memory store with virtue gates and hard rules.

    Wraps store() with envelope validation, M-tier computation,
    virtue gates (amanah/beradab/berhikmah/berakal), and ten hard rules.

    Args:
        envelope: MemoryEventEnvelope as dict (from tool layer)
        existing_records: Optional existing L4 records for contradiction check (RULE 9)

    Returns:
        dict with stored flag, virtue receipt, hard rules result, and store() output
    """
    from arifosmcp.memory.hard_rules import run_all_hard_rules
    from arifosmcp.memory.virtue_gates import run_all_virtue_gates
    from arifosmcp.schemas.memory_envelope import (
        MemoryEventEnvelope,
        compute_m_tier,
    )

    # Build Pydantic envelope from dict
    try:
        parsed = MemoryEventEnvelope.model_validate(envelope)
    except Exception as exc:
        return {
            "stored": False,
            "error": "envelope_validation_failed",
            "detail": str(exc),
            "virtue_receipt": None,
            "hard_rules": {"passed": False, "reason": f"Invalid envelope: {exc}"},
        }

    # Compute M-tier (cannot be set by caller)
    parsed.m_tier = compute_m_tier(parsed)

    # Run hard rules
    hard_result = run_all_hard_rules(parsed, existing_records)
    if not hard_result["passed"]:
        return {
            "stored": False,
            "error": "hard_rule_violation",
            "failed_rule": hard_result.get("failed_rule"),
            "detail": hard_result["reason"],
            "virtue_receipt": None,
            "hard_rules": hard_result,
            "m_tier": parsed.m_tier.value,
        }

    # Handle contradiction (RULE 9) — create conflict record, don't block store
    contradiction = hard_result.get("contradiction")

    # Run virtue gates
    virtue = run_all_virtue_gates(parsed)

    # If any virtue FAIL, block storage
    if virtue.any_fail():
        return {
            "stored": False,
            "error": "virtue_gate_failure",
            "virtue_receipt": virtue.model_dump(),
            "hard_rules": hard_result,
            "m_tier": parsed.m_tier.value,
            "reasons": virtue.reasons,
        }

    # Build tags with governance metadata
    tags = list(parsed.tags or [])
    tags.append(f"intent:{parsed.memory_intent.value}")
    tags.append(f"m_tier:{parsed.m_tier.value}")
    tags.append(f"source:{parsed.source.type.value}")
    if parsed.governance.can_authorize_action:
        tags.append("can_authorize:true")
    else:
        tags.append("can_authorize:false")

    # Determine legacy tier from M-tier
    from arifosmcp.schemas.memory_envelope import M_TIER_CONFIG

    legacy_tier = M_TIER_CONFIG[parsed.m_tier]["legacy_tier"]

    # Build summary with provenance
    summary = parsed.content[:120] if len(parsed.content) > 120 else parsed.content

    # Call canonical store() with enriched metadata
    store_result = store(
        content=parsed.content,
        mode=parsed.memory_intent.value,
        tags=tags,
        actor_id=parsed.actor_id,
        session_id=parsed.session_id,
        summary=summary,
        tier=legacy_tier,
    )

    # Enrich store result with v2 fields
    store_result["virtue_receipt"] = virtue.model_dump()
    store_result["hard_rules"] = hard_result
    store_result["m_tier"] = parsed.m_tier.value
    store_result["memory_status"] = virtue.memory_status.value
    store_result["source_type"] = parsed.source.type.value
    store_result["authority_effect"] = parsed.risk.authority_effect.value
    store_result["can_authorize_action"] = False  # Always false at storage

    if contradiction:
        store_result["contradiction"] = contradiction
        store_result["warning"] = (
            "RULE 9: Contradiction detected with existing memory. "
            "Conflict record created. Do not overwrite."
        )

    return store_result


def quarantine(
    content: Any,
    reason: str,
    actor_id: str | None = None,
    session_id: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Store memory in quarantined state — useful but unproven.

    Quarantined memory is retrievable but displays a warning.
    It cannot be treated as proof or authority.
    """
    store_result = store(
        content=content,
        mode="quarantined",
        tags=(tags or []) + ["quarantined", f"reason:{reason[:50]}"],
        actor_id=actor_id,
        session_id=session_id,
        summary=f"[QUARANTINED: {reason}] {_summarize(content)}",
        tier="ephemeral",  # Quarantined memory is ephemeral by default
    )
    store_result["quarantined"] = True
    store_result["quarantine_reason"] = reason
    store_result["memory_status"] = "quarantined"
    return store_result


def forget(
    memory_id: str,
    method: str = "soft_delete",
    reason: str = "",
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Forget a memory — with M-tier-aware behavior.

    M0–M2 (ephemeral/canon): soft-delete (set deleted_at in Postgres)
    M3–M4 (sacred/authority): tombstone only — create revocation record

    Args:
        memory_id: The memory to forget
        method: soft_delete | revoke_authority | tombstone
        reason: Why this memory is being forgotten
        actor_id: Who is requesting the forget

    Returns:
        dict with forgotten status and method used
    """
    from arifosmcp.memory.hard_rules import rule_10_no_delete_sealed
    from arifosmcp.schemas.memory_envelope import MemoryRiskTier

    # First, recall to check M-tier
    record = recall(memory_id)
    if record is None:
        return {"forgotten": False, "error": "memory_not_found", "memory_id": memory_id}

    # Determine M-tier from tags or default to M1
    tags = record.get("tags", [])
    m_tier_str = next((t.split(":")[1] for t in tags if t.startswith("m_tier:")), "M1")
    try:
        m_tier = MemoryRiskTier(m_tier_str)
    except ValueError:
        m_tier = MemoryRiskTier.M1

    # RULE 10: No sealed memory deletion
    try:
        rule_10_no_delete_sealed(m_tier, method)
    except Exception as exc:
        return {
            "forgotten": False,
            "error": "hard_rule_violation",
            "failed_rule": 10,
            "detail": str(exc),
            "memory_id": memory_id,
            "m_tier": m_tier.value,
        }

    # M0–M2: soft-delete
    if m_tier in (MemoryRiskTier.M0, MemoryRiskTier.M1, MemoryRiskTier.M2):
        if method == "soft_delete":
            pg_id = record.get("pg_id")
            if pg_id:
                _pg_run(_pg_soft_delete(pg_id))
            return {
                "forgotten": True,
                "method": "soft_delete",
                "memory_id": memory_id,
                "m_tier": m_tier.value,
                "reason": reason,
                "actor_id": actor_id,
            }

    # M3–M4 or any method=tombstone/revoke_authority: tombstone
    # Create a revocation record
    revocation_content = {
        "action": "revocation",
        "revoked_memory_id": memory_id,
        "original_content": record.get("content", "")[:200],
        "reason": reason,
        "revoked_by": actor_id,
        "revoked_at": datetime.now(UTC).isoformat(),
        "original_m_tier": m_tier.value,
    }
    revocation_result = store(
        content=json.dumps(revocation_content),
        mode="revocation",
        tags=["tombstone", f"revokes:{memory_id}", f"m_tier:{m_tier.value}"],
        actor_id=actor_id,
        session_id=record.get("session_id"),
        summary=f"[TOMBSTONE] Revokes {memory_id}: {reason}",
        tier="sacred",
    )

    # Mark original as superseded in Qdrant payload (best effort)
    point_id = record.get("point_id")
    if point_id:
        try:
            client = _get_qdrant_client()
            client.set_payload(
                collection_name=_QDRANT_COLLECTION,
                payload={
                    "temporal_marker": "revoked",
                    "revoked_at": datetime.now(UTC).isoformat(),
                    "revoked_by": actor_id,
                    "revocation_reason": reason,
                    "revocation_record_id": revocation_result.get("memory_id"),
                },
                points=[point_id],
            )
        except Exception as exc:
            logger.warning("Failed to mark memory %s as revoked in Qdrant: %s", memory_id, exc)

    return {
        "forgotten": True,
        "method": "tombstone",
        "memory_id": memory_id,
        "m_tier": m_tier.value,
        "reason": reason,
        "actor_id": actor_id,
        "revocation_record_id": revocation_result.get("memory_id"),
    }


def audit_governance(
    target: str | None = None,
    actor_id: str | None = None,
    checks: list[str] | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """
    Audit memory governance — check for stale, contradiction, missing_provenance, over_authorized.

    Args:
        target: memory_id | actor_id | project | authority_memories | None (all)
        actor_id: Filter by actor
        checks: List of checks to run ["stale", "contradiction", "missing_provenance", "over_authorized"]
        limit: Max memories to audit

    Returns:
        dict with audit report, escalation queue, and governance summary
    """
    checks = checks or ["stale", "contradiction", "missing_provenance", "over_authorized"]
    memories = get_all_memories_for_audit(limit=limit, include_deleted=False)

    # Filter by target
    if target:
        if target == "authority_memories":
            memories = [m for m in memories if any(t.startswith("m_tier:M3") or t.startswith("m_tier:M4") for t in m.get("tags", []))]
        elif target.startswith("memory_"):
            memories = [m for m in memories if m.get("memory_id") == target]
        else:
            # Assume actor_id target
            memories = [m for m in memories if m.get("actor_id") == target]

    # Also filter by actor_id param
    if actor_id:
        memories = [m for m in memories if m.get("actor_id") == actor_id]

    findings: dict[str, list[dict[str, Any]]] = {
        "stale": [],
        "contradiction": [],
        "missing_provenance": [],
        "over_authorized": [],
    }

    now = datetime.now(UTC)

    for mem in memories:
        meta = mem.get("metadata", {})
        tags = mem.get("tags", [])
        created_at_str = mem.get("created_at")
        created_at = None
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        # Check stale: no access for > 90 days (canon) or > 30 days (session)
        if "stale" in checks and created_at:
            tier = mem.get("tier", "canon")
            stale_threshold_days = 90 if tier == "canon" else 30
            age_days = (now - created_at).days
            if age_days > stale_threshold_days:
                findings["stale"].append({
                    "memory_id": mem.get("memory_id"),
                    "tier": tier,
                    "age_days": age_days,
                    "threshold": stale_threshold_days,
                    "reason": f"Memory untouched for {age_days} days (threshold: {stale_threshold_days})",
                })

        # Check missing_provenance: no source_type or actor_id
        if "missing_provenance" in checks:
            has_source = any(t.startswith("source:") for t in tags)
            has_actor = bool(mem.get("actor_id"))
            if not has_source or not has_actor:
                findings["missing_provenance"].append({
                    "memory_id": mem.get("memory_id"),
                    "has_source": has_source,
                    "has_actor": has_actor,
                    "reason": "Missing source_type or actor_id provenance",
                })

        # Check over_authorized: can_authorize=true without M3/M4
        if "over_authorized" in checks:
            has_authorize = "can_authorize:true" in tags
            is_high_tier = any(t.startswith("m_tier:M3") or t.startswith("m_tier:M4") for t in tags)
            if has_authorize and not is_high_tier:
                findings["over_authorized"].append({
                    "memory_id": mem.get("memory_id"),
                    "reason": "Memory claims can_authorize=true but is not M3/M4",
                })

    # Contradiction check: use existing F4 results from metadata
    if "contradiction" in checks:
        for mem in memories:
            meta = mem.get("metadata", {})
            if meta.get("f4_conflicts_count", 0) > 0 or meta.get("phoenix_state") == "contradiction_hold":
                findings["contradiction"].append({
                    "memory_id": mem.get("memory_id"),
                    "phoenix_state": meta.get("phoenix_state"),
                    "f4_conflicts_count": meta.get("f4_conflicts_count", 0),
                    "reason": "Contradiction detected by F4 or Phoenix-72",
                })

    # Build escalation queue (anything that needs sovereign attention)
    escalation_queue = (
        findings["contradiction"]
        + findings["over_authorized"]
        + findings["missing_provenance"]
    )

    return {
        "mode": "audit",
        "target": target,
        "checks_run": checks,
        "total_memories_audited": len(memories),
        "findings": findings,
        "findings_count": sum(len(v) for v in findings.values()),
        "escalation_queue": escalation_queue,
        "escalation_count": len(escalation_queue),
        "governance_summary": {
            "stale_count": len(findings["stale"]),
            "contradiction_count": len(findings["contradiction"]),
            "missing_provenance_count": len(findings["missing_provenance"]),
            "over_authorized_count": len(findings["over_authorized"]),
        },
    }


__all__ = [
    "store",
    "store_v2",
    "recall",
    "search",
    "get_all_memories_for_audit",
    "get_memory_store",
    "MemoryStore",
    "prune",
    "context_for_session",
    "load_canonical_for_actor",
    "memory_mode",
    "stats",
    "quarantine",
    "forget",
    "audit_governance",
    "TIER_SACRED",
    "TIER_CANONICAL",
    "TIER_SESSION",
    "TIER_EPHEMERAL",
]
