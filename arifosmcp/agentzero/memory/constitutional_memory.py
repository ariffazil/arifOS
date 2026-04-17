"""
arifosmcp.agentzero.memory.constitutional_memory — Constitutional Memory Store
Production-grade Qdrant-backed memory engine.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
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
    score: float = 1.0
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
            "metadata": kwargs.get("metadata", {})
        }
        
        client.upsert(
            collection_name=_QDRANT_COLLECTION,
            points=[PointStruct(id=memory_id, vector=vector, payload=payload)]
        )
        return True, memory_id, None

    async def vector_query(self, query: str, limit: int = 5, **kwargs) -> list[MemoryEntry]:
        """Query Qdrant for similar memory entries."""
        client = _get_qdrant_client()
        vector = _generate_embedding(query)
        
        results = client.query_points(
            collection_name=_QDRANT_COLLECTION,
            query=vector,
            limit=limit
        ).points
        
        entries = []
        for res in results:
            entries.append(MemoryEntry(
                content=res.payload.get("content", ""),
                id=str(res.id),
                score=0.0, # query_points score is nested or needs mapping
                metadata=res.payload.get("metadata", {})
            ))
        return entries

    async def recall(self, **kwargs) -> list[MemoryEntry]:
        # Alias for vector_query in this context
        query = kwargs.get("query") or kwargs.get("content")
        if not query:
            return []
        return await self.vector_query(query)

    async def search(self, **kwargs) -> list[MemoryEntry]:
        return await self.recall(**kwargs)
