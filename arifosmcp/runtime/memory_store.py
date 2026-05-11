"""
arifosmcp/runtime/memory_store.py -- 555_MEMORY Canonical Backend v2

CONSOLIDATED: This module is now the SINGLE canonical memory backend.
Previously there were 3 competing systems (memory_store.py, memory_engine.py,
vector_memory_qdrant.py). They have been unified here.

Backend: Qdrant (vector store) + Ollama bge-m3 (embeddings) + JSON index
Index:   /root/.arifOS/memory/.qdrant_index.json -- memory_id -> point_id

Migration: 6 legacy JSON files from v1 were migrated to Qdrant on 2026-05-11.

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
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
    from qdrant_client import QdrantClient

    return QdrantClient(url=_QDRANT_URL)


def _generate_embedding(text: str) -> list[float]:
    import httpx

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
# PUBLIC API -- Same interface as v1, but backed by Qdrant + embeddings
# =============================================================================


def store(
    content: Any,
    mode: str = "unknown",
    tags: list[str] | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    summary: str | None = None,
) -> dict[str, Any]:
    _ensure_dir()
    memory_id = uuid.uuid4().hex[:12]
    text = _summarize(content)

    try:
        vector = _generate_embedding(text)
    except Exception as exc:
        logger.warning(f"Embedding generation failed: {exc}")
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
        "version": "v2",
    }

    point_id = str(uuid.uuid4())
    try:
        client = _get_qdrant_client()
        client.upsert(
            collection_name=_QDRANT_COLLECTION,
            points=[{"id": point_id, "vector": vector, "payload": payload}],
        )
    except Exception as exc:
        logger.error(f"Qdrant store failed: {exc}")
        return {"stored": False, "memory_id": memory_id, "error": str(exc)}

    idx = _index_read()
    idx[memory_id] = {
        "point_id": point_id,
        "mode": mode,
        "tags": tags or [],
        "summary": payload["summary"],
        "content_hash": payload["content_hash"],
        "created_at": payload["created_at"],
        "session_id": session_id,
    }
    _index_write(idx)

    return {
        "stored": True,
        "memory_id": memory_id,
        "indexed": True,
        "point_id": point_id,
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
                        "point_id": point_id,
                        "version": p.get("version", "v2"),
                    }
            except Exception as exc:
                logger.warning(f"Qdrant recall failed for {memory_id}: {exc}")

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
            hits = client.search(
                collection_name=_QDRANT_COLLECTION,
                query_vector=vector,
                limit=limit * 2,
                with_payload=True,
            )
            for hit in hits:
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
                            "point_id": hit.id,
                            "score": hit.score,
                            "version": p.get("version", "v2"),
                        },
                    )
                )
        except Exception as exc:
            logger.warning(f"Vector search failed: {exc}")
    else:
        # No query: list by filters
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
) -> dict[str, Any]:
    _ensure_dir()
    idx = _index_read()
    pruned: list[str] = []
    client = None

    try:
        client = _get_qdrant_client()
    except Exception as exc:
        logger.warning(f"Qdrant client unavailable for prune: {exc}")

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
        if meta and client:
            point_id = meta.get("point_id")
            if point_id:
                try:
                    client.delete(
                        collection_name=_QDRANT_COLLECTION,
                        points_selector=[point_id],
                    )
                except Exception as exc:
                    logger.warning(f"Qdrant delete failed for {point_id}: {exc}")

        # Also clean legacy file
        legacy_path = _MEMORY_DIR / f"{mid}.json"
        if legacy_path.exists():
            legacy_path.unlink()

        if mid in idx:
            del idx[mid]
            pruned.append(mid)

    _index_write(idx)
    return {"pruned": pruned, "count": len(pruned), "reason": reason}


def context_for_session(
    session_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return search(session_id=session_id, limit=limit)


def stats() -> dict[str, Any]:
    _ensure_dir()
    idx = _index_read()
    qdrant_count = 0
    try:
        client = _get_qdrant_client()
        info = client.get_collection(_QDRANT_COLLECTION)
        qdrant_count = info.points_count
    except Exception as exc:
        logger.warning(f"Qdrant stats unavailable: {exc}")

    return {
        "total_records": len(idx),
        "qdrant_vectors": qdrant_count,
        "legacy_files": len(list(_MEMORY_DIR.glob("*.json")))
        - (1 if _INDEX_FILE.exists() else 0)
        - (1 if _LEGACY_INDEX_FILE.exists() else 0),
        "by_mode": _mode_counts(idx),
        "by_session": _session_counts(idx),
        "backend": "qdrant_v2",
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


__all__ = ["store", "recall", "search", "prune", "context_for_session", "stats"]
