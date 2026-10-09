"""
arifosmcp.hexagon.memory.constitutional_memory — Constitutional Memory Store
Production-grade Qdrant-backed memory engine.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

# Import the real Qdrant backend
from arifosmcp.memory.vector_memory_qdrant import (
    _QDRANT_COLLECTION,
    _ensure_collection,
    _generate_embedding,
    _get_qdrant_client,
)

logger = logging.getLogger(__name__)


class MemoryArea(Enum):
    MAIN = "main"
    TASK = "task"
    VAULT = "vault"
    SESSION = "session"

    @classmethod
    def from_string(cls, name: str) -> "MemoryArea":
        try:
            return cls(name.lower())
        except ValueError:
            return cls.MAIN


@dataclass
class MemoryEntry:
    content: str
    id: str | None = None
    area: MemoryArea = MemoryArea.MAIN
    project_id: str = "default"
    source: str = "unknown"
    source_agent: str = "unknown"
    timestamp: datetime = field(default_factory=datetime.now)
    # FIX 2026-09-05 (bug #2): score may be None = retrieval signal unavailable.
    # Never coerce None to 0.0 — that fabricates a known-bad signal (F2/F9).
    score: float | None = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "area": self.area.value,
            "project_id": self.project_id,
            "source": self.source,
            "source_agent": self.source_agent,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "metadata": self.metadata,
        }


class ConstitutionalMemoryStore:
    """Real Qdrant-backed constitutional memory store."""

    def __init__(self):
        self.initialized = False
        try:
            _ensure_collection()
            self.initialized = True
            logger.info("ConstitutionalMemoryStore initialized with Qdrant.")
        except Exception as exc:
            logger.error(f"Failed to initialize ConstitutionalMemoryStore: {exc}")

    async def initialize_project(self, project_id: str) -> bool:
        return True

    async def store(self, content: str, **kwargs) -> tuple[bool, str | None, str | None]:
        """Store a new memory entry in Qdrant."""
        import uuid

        from qdrant_client.models import PointStruct

        client = _get_qdrant_client()
        vector = _generate_embedding(content)
        memory_id = str(uuid.uuid4())

        payload = {
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "area": kwargs.get("area", "main"),
            "metadata": kwargs.get("metadata", {}),
        }

        client.upsert(
            collection_name=_QDRANT_COLLECTION,
            points=[PointStruct(id=memory_id, vector=vector, payload=payload)],
        )
        return True, memory_id, None

    async def vector_query(self, query: str, limit: int = 5, **kwargs) -> list[MemoryEntry]:
        """Query Qdrant for similar memory entries.

        FIX 2026-09-05 (bug #2, scar_1788553451571 follow-up): map res.score —
        it exists on every query_points hit (verified live: 0.5289/0.8967 etc.)
        and was previously discarded with score=0.0 ("needs mapping" — it
        doesn't). Fail closed: missing score → None, never 0.0. Attach
        retrieval provenance (F2/F3/F4) so downstream policy can audit the
        signal instead of trusting a constant.
        """
        client = _get_qdrant_client()
        vector = _generate_embedding(query)
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")

        results = client.query_points(
            collection_name=_QDRANT_COLLECTION, query=vector, limit=limit
        ).points

        entries = []
        for res in results:
            payload = res.payload or {}
            raw_score = getattr(res, "score", None)
            meta = dict(payload.get("metadata", {}) or {})
            # POLICY 2026-09-05 (888 decision): text-schema fallback — 57/99 dossier/canon
            # points carry 'text'/'subject' instead of 'content' and were invisible to
            # recall. Fallback exposes them; provenance records which family served the hit.
            content = payload.get("content")
            content_source = "content"
            if content is None or (isinstance(content, str) and not content.strip()):
                text = payload.get("text")
                if isinstance(text, str) and text.strip():
                    subject = payload.get("subject")
                    content = f"[{subject}] {text}" if isinstance(subject, str) and subject else text
                    content_source = "text_fallback"
            meta["score_raw"] = raw_score
            meta["score_metric"] = "cosine"
            meta["collection"] = _QDRANT_COLLECTION
            meta["embedding_model"] = embedding_model
            meta["query_hash"] = query_hash
            meta["retrieved_at"] = datetime.now(timezone.utc).isoformat()
            meta["content_source"] = content_source
            entries.append(
                MemoryEntry(
                    content=content if content is not None else "",
                    id=str(res.id),
                    score=float(raw_score) if raw_score is not None else None,
                    metadata=meta,
                )
            )
        return entries

    async def recall(self, **kwargs) -> list[MemoryEntry]:
        # Alias for vector_query in this context
        query = kwargs.get("query") or kwargs.get("content")
        if not query:
            return []
        return await self.vector_query(query)

    async def search(self, **kwargs) -> list[MemoryEntry]:
        return await self.recall(**kwargs)

    async def delete(self, memory_id: str, project_id: str = "default") -> bool:
        """Delete a memory by memory_id from Qdrant."""
        from arifosmcp.memory.vector_memory_qdrant import vector_forget
        res = await vector_forget(point_id=memory_id)
        return res.get("ok", False)
