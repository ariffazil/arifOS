"""
arifosmcp/memory/vector_memory_qdrant.py
========================================

Constitutional vector memory backed by Qdrant.
Implements 555_MEMORY vector modes with F10 Ontology + F2 Verification.

Embedding backend: Ollama bge-m3 (1024-dim, cosine) — matches all Qdrant collections.
Legacy sentence-transformers (all-MiniLM-L6-v2, 384-dim) removed: dimension mismatch fix.

Authority: Ω (A-ENGINEER) | Trinity: OMEGA
Floors: F10 (Ontology), F2 (Truth ≥ 0.99), F11 (Audit)
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid

logger = logging.getLogger(__name__)

# Qdrant configuration — prefer QDRANT_URL (set in docker-compose), fallback to host/port
_QDRANT_URL = os.getenv(
    "QDRANT_URL",
    "http://{}:{}".format(
        os.getenv("QDRANT_HOST", "qdrant_memory"),
        os.getenv("QDRANT_PORT", "6333"),
    ),
)
_QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arifos_memory")
# bge-m3 produces 1024-dim vectors — all Qdrant collections are created at 1024
_VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "1024"))

# Ollama embedding endpoint
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama_engine:11434")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3:latest")

# Constitutional thresholds
_F2_TRUTH_THRESHOLD = 0.99
_F10_ONTOLOGY_CHECK = True

_qdrant_client = None


def _get_qdrant_client():
    """Lazy initialization of Qdrant client."""
    global _qdrant_client
    if _qdrant_client is None:
        try:
            from qdrant_client import QdrantClient
            _qdrant_client = QdrantClient(url=_QDRANT_URL)
            logger.info(f"Connected to Qdrant at {_QDRANT_URL}")
        except Exception as exc:
            logger.error(f"Failed to connect to Qdrant: {exc}")
            raise
    return _qdrant_client


def _ensure_collection():
    """Ensure the memory collection exists and has the correct vector schema."""
    client = _get_qdrant_client()
    try:
        info = client.get_collection(_QDRANT_COLLECTION)
        existing_size = info.config.params.vectors.size
        if existing_size != _VECTOR_SIZE:
            raise RuntimeError(
                f"F10 SCHEMA: Collection '{_QDRANT_COLLECTION}' has dim={existing_size} "
                f"but VECTOR_SIZE={_VECTOR_SIZE}. Manual migration required."
            )
    except RuntimeError:
        raise
    except Exception:
        from qdrant_client.models import Distance, VectorParams
        client.create_collection(
            collection_name=_QDRANT_COLLECTION,
            vectors_config=VectorParams(size=_VECTOR_SIZE, distance=Distance.COSINE),
        )
        logger.info(f"Created collection: {_QDRANT_COLLECTION} (dim={_VECTOR_SIZE})")


def _generate_embedding(text: str) -> list[float]:
    """Generate 1024-dim embedding via Ollama bge-m3 (F10 Ontology encoded).

    Raises RuntimeError on failure — callers must handle; zero-vector fallback
    is intentionally removed to prevent silent pollution of Qdrant retrieval.
    """
    import httpx
    try:
        response = httpx.post(
            f"{_OLLAMA_URL}/api/embeddings",
            json={"model": _EMBEDDING_MODEL, "prompt": text},
            timeout=30.0,
        )
        response.raise_for_status()
        embedding = response.json().get("embedding", [])
        if embedding:
            return embedding
        raise ValueError("Ollama returned empty embedding")
    except Exception as exc:
        logger.error(f"Failed to generate embedding via Ollama bge-m3: {exc}")
        raise RuntimeError(f"Embedding unavailable: {exc}") from exc


def _compute_truth_score(content: str, context: dict | None = None) -> float:
    """F2: Compute truth score τ ∈ [0,1]."""
    score = 0.0
    if content and len(content.strip()) > 0:
        score += 0.5
    try:
        if content.strip().startswith("{"):
            json.loads(content)
            score += 0.25
        elif "#" in content or "-" in content:
            score += 0.15
    except json.JSONDecodeError:
        pass
    if context:
        if context.get("source") or context.get("reference"):
            score += 0.15
        if context.get("verified"):
            score += 0.10
    return min(score, 1.0)


def _f10_ontology_check(content: str, metadata: dict | None = None) -> dict:
    """F10: Ontology verification."""
    result = {
        "valid": True,
        "ontology_class": "general",
        "violations": [],
        "confidence": 1.0,
    }
    if not _F10_ONTOLOGY_CHECK:
        return result
    prohibited_patterns = [
        "consciousness claim", "i am sentient",
        "i feel emotions", "i have subjective experience",
    ]
    content_lower = content.lower()
    for pattern in prohibited_patterns:
        if pattern in content_lower:
            result["valid"] = False
            result["violations"].append(f"F9 ANTI-HANTU: Detected '{pattern}'")
            result["confidence"] *= 0.5
    if any(t in content_lower for t in ["code", "function", "class", "def "]):
        result["ontology_class"] = "code"
    elif any(t in content_lower for t in ["constitution", "floor ", "f1", "f2"]):
        result["ontology_class"] = "constitutional"
    elif any(t in content_lower for t in ["memory", "vector", "embedding"]):
        result["ontology_class"] = "memory"
    elif any(t in content_lower for t in ["http", "url", "api", "request"]):
        result["ontology_class"] = "web"
    return result


def _compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


async def vector_store(
    content: str,
    metadata: dict | None = None,
    session_id: str = "",
    actor_id: str = "",
    **kwargs,
) -> dict:
    """Store content with F10 ontology + F2 truth ≥ 0.99."""
    _ensure_collection()
    metadata = metadata or {}
    truth_score = _compute_truth_score(content, metadata)
    if truth_score < _F2_TRUTH_THRESHOLD:
        return {
            "ok": False,
            "error": ("F2 TRUTH: Content failed truth verification "
                      f"(τ={truth_score:.4f} < {_F2_TRUTH_THRESHOLD})"),
            "truth_score": truth_score,
            "policy_violation": True,
        }
    ontology = _f10_ontology_check(content, metadata)
    if not ontology["valid"]:
        return {
            "ok": False,
            "error": f"F10 ONTOLOGY: {', '.join(ontology['violations'])}",
            "ontology": ontology,
            "policy_violation": True,
        }
    try:
        vector = _generate_embedding(content)
    except RuntimeError as exc:
        return {"ok": False, "error": f"F10 EMBEDDING: {exc}", "embedding_unavailable": True}
    point_id = str(uuid.uuid4())
    content_hash = _compute_content_hash(content)
    payload = {
        "content": content,
        "content_hash": content_hash,
        "metadata": {
            **metadata,
            "ontology_class": ontology["ontology_class"],
            "truth_score": truth_score,
            "session_id": session_id,
            "actor_id": actor_id,
            "timestamp": time.time(),
        },
    }
    client = _get_qdrant_client()
    client.upsert(
        collection_name=_QDRANT_COLLECTION,
        points=[{"id": point_id, "vector": vector, "payload": payload}],
    )
    logger.info(f"Vector stored: {point_id[:8]}... "
                f"(class={ontology['ontology_class']}, τ={truth_score:.4f})")
    return {
        "ok": True,
        "point_id": point_id,
        "content_hash": content_hash,
        "ontology_class": ontology["ontology_class"],
        "truth_score": truth_score,
        "vector_size": len(vector),
    }


async def vector_query(
    query: str,
    top_k: int = 5,
    session_id: str = "",
    actor_id: str = "",
    filters: dict | None = None,
    **kwargs,
) -> dict:
    """Query vector memory with F10/F2 constitutional filtering."""
    _ensure_collection()
    try:
        vector = _generate_embedding(query)
    except RuntimeError as exc:
        return {"ok": False, "error": f"F10 EMBEDDING: {exc}", "embedding_unavailable": True}
    query_filter = None
    if filters:
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        conditions = []
        if "ontology_class" in filters:
            conditions.append(FieldCondition(
                key="metadata.ontology_class",
                match=MatchValue(value=filters["ontology_class"]),
            ))
        if "session_id" in filters:
            conditions.append(FieldCondition(
                key="metadata.session_id",
                match=MatchValue(value=filters["session_id"]),
            ))
        if conditions:
            query_filter = Filter(must=conditions)
    client = _get_qdrant_client()
    hits = client.query_points(
        collection_name=_QDRANT_COLLECTION,
        query=vector,
        limit=top_k,
        query_filter=query_filter,
        with_payload=True,
    ).points
    filtered_results = []
    for hit in hits:
        md = hit.payload.get("metadata", {})
        if md.get("truth_score", 0.0) >= _F2_TRUTH_THRESHOLD:
            filtered_results.append({
                "point_id": hit.id,
                "score": hit.score,
                "content": hit.payload.get("content", "")[:500],
                "content_hash": hit.payload.get("content_hash"),
                "metadata": md,
            })
    logger.info(f"Vector query: '{query[:50]}...' → {len(filtered_results)} results")
    return {
        "ok": True,
        "query": query,
        "results": filtered_results,
        "total_hits": len(hits),
        "filtered_hits": len(filtered_results),
        "f2_threshold": _F2_TRUTH_THRESHOLD,
    }


async def vector_forget(
    point_id: str | None = None,
    content_hash: str | None = None,
    session_id: str = "",
    actor_id: str = "",
    **kwargs,
) -> dict:
    """Remove vector with F1 reversibility + F13 sovereign check."""
    client = _get_qdrant_client()
    if not point_id and not content_hash:
        return {"ok": False, "error": "Must provide point_id or content_hash"}
    try:
        if point_id:
            if _F10_ONTOLOGY_CHECK and session_id:
                point = client.retrieve(
                    collection_name=_QDRANT_COLLECTION,
                    ids=[point_id],
                    with_payload=True,
                )
                if point and point[0].payload.get("metadata", {}).get(
                    "session_id"
                ) != session_id:
                    return {
                        "ok": False,
                        "error": "F13 KHILAFAH: Cannot delete another session's memory",
                        "policy_violation": True,
                    }
            client.delete(collection_name=_QDRANT_COLLECTION, points_selector=[point_id])
            logger.info(f"Vector forgotten: {point_id[:8]}...")
            return {
                "ok": True,
                "deleted_id": point_id,
                "session_id": session_id,
                "actor_id": actor_id,
            }
        return {"ok": False, "error": "Content hash deletion not implemented"}
    except Exception as exc:
        logger.error(f"Failed to delete: {exc}")
        return {"ok": False, "error": str(exc)}


async def vector_health() -> dict:
    """Check vector memory health and F8 vitality."""
    try:
        client = _get_qdrant_client()
        collection = client.get_collection(_QDRANT_COLLECTION)
        return {
            "ok": True,
            "status": "healthy",
            "collection": _QDRANT_COLLECTION,
            "vectors_count": collection.points_count,
            "config": {
                "vector_size": _VECTOR_SIZE,
                "qdrant_url": _QDRANT_URL,
                "embedding_model": _EMBEDDING_MODEL,
                "ollama_url": _OLLAMA_URL,
            },
            "floors": {
                "F2_truth_threshold": _F2_TRUTH_THRESHOLD,
                "F10_ontology_check": _F10_ONTOLOGY_CHECK,
            },
        }
    except Exception as exc:
        return {"ok": False, "status": "unhealthy", "error": str(exc)}
