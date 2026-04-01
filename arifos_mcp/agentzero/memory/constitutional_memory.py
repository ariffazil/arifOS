"""
arifos_mcp/agentzero/memory/constitutional_memory.py
====================================================

Constitutional Memory Store — Qdrant-backed semantic memory with fallback.

Authority: A-ARCHITECT | A-ENGINEER
Purpose: Provides long-term semantic memory for agents with constitutional tagging.

Wired to:
- engineering_memory tool (via _get_constitutional_memory_store())
- A-ARCHITECT design context
- A-ENGINEER implementation memory

This module is loaded lazily by tools_internal.py only when needed.
Qdrant is the primary backend. Falls back to in-memory dict if Qdrant unavailable.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MemoryArea(Enum):
    """Memory areas for constitutional categorization."""
    
    GOVERNANCE = "governance"       # Constitutional decisions, floor activations
    INTELLIGENCE = "intelligence"   # Reasoning chains, proofs, verdicts
    IMPLEMENTATION = "implementation"  # Code, engineering decisions
    AUDIT = "audit"                 # VAULT999 records, compliance logs
    DESIGN = "design"               # Architecture decisions, specs
    SESSION = "session"            # Ephemeral session context
    
    @classmethod
    def from_string(cls, s: str) -> "MemoryArea":
        """Parse string to MemoryArea, defaulting to SESSION."""
        try:
            return cls(s.lower())
        except ValueError:
            return cls.SESSION


@dataclass
class MemoryRecord:
    """A single memory entry with constitutional metadata."""
    
    memory_id: str
    content: str
    area: MemoryArea
    project_id: str
    source: str                    # Which tool/agent created this
    source_agent: str              # Which session/agent stored this
    created_at: float              # Unix timestamp
    constitutional_tags: list[str]  # F-codes relevant to this memory
    content_hash: str              # SHA-256 of content for integrity
    metadata: dict = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        content: str,
        area: MemoryArea,
        project_id: str,
        source: str,
        source_agent: str,
        constitutional_tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> "MemoryRecord":
        """Factory method with auto-hashing and ID generation."""
        import uuid
        memory_id = f"mem_{uuid.uuid4().hex[:12]}"
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        return cls(
            memory_id=memory_id,
            content=content,
            area=area,
            project_id=project_id,
            source=source,
            source_agent=source_agent,
            created_at=time.time(),
            constitutional_tags=constitutional_tags or [],
            content_hash=content_hash,
            metadata=metadata or {},
        )
    
    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "area": self.area.value,
            "project_id": self.project_id,
            "source": self.source,
            "source_agent": self.source_agent,
            "created_at": self.created_at,
            "constitutional_tags": self.constitutional_tags,
            "content_hash": self.content_hash,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    """Result of a memory search."""
    memory_id: str
    content: str
    area: str
    score: float                   # Relevance score (0-1)
    created_at: float


class ConstitutionalMemoryStore:
    """
    Constitutional memory store with Qdrant backend.
    
    Stores semantic memories with constitutional tagging.
    Supports area-based filtering and semantic search.
    
    Falls back to in-memory dict if Qdrant is unavailable.
    """
    
    def __init__(self, qdrant_url: str = "qdrant:6333"):
        self.qdrant_url = qdrant_url
        self._qdrant_client = None
        self._qdrant_collection = "arifos_constitutional_memory"
        self._memory_store: dict[str, MemoryRecord] = {}  # Fallback + cache
        self._initialized = False
        self._init_qdrant()
    
    def _init_qdrant(self):
        """Try to connect to Qdrant. Silently fails if unavailable."""
        try:
            from qdrant_client import QdrantClient
            self._qdrant_client = QdrantClient(url=self.qdrant_url)
            # Test connection
            self._qdrant_client.get_collections()
            logger.info(f"ConstitutionalMemoryStore connected to Qdrant at {self.qdrant_url}")
        except Exception as exc:
            logger.warning(f"Qdrant unavailable ({exc}), using in-memory fallback")
            self._qdrant_client = None
    
    async def initialize_project(self, project_id: str) -> bool:
        """Initialize storage for a project. Idempotent."""
        if self._qdrant_client:
            try:
                from qdrant_client.models import Distance, VectorParams
                self._qdrant_client.recreate_collection(
                    collection_name=f"{self._qdrant_collection}_{project_id}",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
            except Exception as exc:
                logger.warning(f"Qdrant init failed for project {project_id}: {exc}")
        self._initialized = True
        return True
    
    async def store(
        self,
        content: str,
        area: MemoryArea,
        project_id: str,
        source: str,
        source_agent: str,
        constitutional_tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> tuple[bool, str | None, str | None]:
        """
        Store a memory with constitutional tagging.
        
        Returns:
            (success, memory_id, error)
        """
        record = MemoryRecord.create(
            content=content,
            area=area,
            project_id=project_id,
            source=source,
            source_agent=source_agent,
            constitutional_tags=constitutional_tags,
            metadata=metadata,
        )
        
        # Store in Qdrant if available
        if self._qdrant_client:
            try:
                await self._store_qdrant(record, project_id)
            except Exception as exc:
                logger.warning(f"Qdrant store failed, using fallback: {exc}")
                self._memory_store[record.memory_id] = record
        else:
            # Fallback to in-memory
            self._memory_store[record.memory_id] = record
        
        return True, record.memory_id, None
    
    async def _store_qdrant(self, record: MemoryRecord, project_id: str):
        """Store in Qdrant with vector embedding."""
        try:
            # Try to get embeddings (placeholder — requires embedding model)
            # For now, use simple hash as pseudo-vector
            import struct
            vector = [float(b) / 255.0 for b in record.content_hash.encode()[:128]]
            vector += [0.0] * (128 - len(vector))  # Pad to 128
            
            collection = f"{self._qdrant_collection}_{project_id}"
            self._qdrant_client.upsert(
                collection_name=collection,
                points=[{
                    "id": record.memory_id,
                    "vector": vector,
                    "payload": record.to_dict(),
                }],
            )
        except Exception:
            raise
    
    async def recall(
        self,
        memory_id: str,
        project_id: str | None = None,
    ) -> MemoryRecord | None:
        """Retrieve a specific memory by ID."""
        return self._memory_store.get(memory_id)
    
    async def search(
        self,
        query: str,
        project_id: str,
        area: MemoryArea | None = None,
        limit: int = 5,
        constitutional_tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """
        Search memories by content similarity.
        
        Args:
            query: Search text
            project_id: Project to search in
            area: Optional filter by memory area
            limit: Max results
            constitutional_tags: Optional filter by F-codes
        
        Returns:
            List of SearchResult sorted by relevance
        """
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        results: list[SearchResult] = []
        
        for record in self._memory_store.values():
            if record.project_id != project_id:
                continue
            if area and record.area != area:
                continue
            if constitutional_tags:
                if not any(tag in record.constitutional_tags for tag in constitutional_tags):
                    continue
            
            # Simple score based on content match
            score = sum(1 for word in query.lower().split() if word in record.content.lower()) / max(len(query.split()), 1)
            if score > 0:
                results.append(SearchResult(
                    memory_id=record.memory_id,
                    content=record.content[:200],  # Truncate
                    area=record.area.value,
                    score=min(score, 1.0),
                    created_at=record.created_at,
                ))
        
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]
    
    async def list_by_area(
        self,
        project_id: str,
        area: MemoryArea,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        """List recent memories by area."""
        records = [
            r for r in self._memory_store.values()
            if r.project_id == project_id and r.area == area
        ]
        records.sort(key=lambda r: r.created_at, reverse=True)
        return records[:limit]
    
    async def verify_integrity(self, memory_id: str) -> tuple[bool, str | None]:
        """Verify memory hasn't been tampered (using content hash)."""
        record = self._memory_store.get(memory_id)
        if not record:
            return False, "Memory not found"
        
        expected_hash = hashlib.sha256(record.content.encode()).hexdigest()
        if expected_hash != record.content_hash:
            return False, f"Hash mismatch: expected {expected_hash}, got {record.content_hash}"
        
        return True, None
    
    async def get_stats(self, project_id: str) -> dict:
        """Get memory statistics for a project."""
        records = [r for r in self._memory_store.values() if r.project_id == project_id]
        by_area: dict[str, int] = {}
        for r in records:
            by_area[r.area.value] = by_area.get(r.area.value, 0) + 1
        
        return {
            "project_id": project_id,
            "total_memories": len(records),
            "by_area": by_area,
            "backend": "qdrant" if self._qdrant_client else "memory",
            "qdrant_available": self._qdrant_client is not None,
        }


# ─────────────────────────────────────────────────────────────
# Agent Context Integration
# ─────────────────────────────────────────────────────────────

class AgentContext:
    """
    Agent's memory context — wires ConstitutionalMemoryStore to agent sessions.
    
    Usage:
        ctx = AgentContext(agent_id="A-ENGINEER", session_id="session_001")
        await ctx.store_implementation(code="def foo(): pass", description="...")
        results = await ctx.recall_implementations(query="foo function")
    """
    
    def __init__(self, agent_id: str, session_id: str):
        self.agent_id = agent_id
        self.session_id = session_id
        self._store = ConstitutionalMemoryStore()
        self._initialized = False
    
    async def initialize(self, project_id: str = "arifOS"):
        await self._store.initialize_project(project_id)
        self._initialized = True
    
    async def store_implementation(
        self,
        content: str,
        description: str,
        constitutional_tags: list[str] | None = None,
    ) -> tuple[bool, str | None]:
        """Store implementation memory with F1-F13 tagging."""
        return await self._store.store(
            content=f"{description}\n\n{content}",
            area=MemoryArea.IMPLEMENTATION,
            project_id="arifOS",
            source="agentzero_engineer",
            source_agent=self.agent_id,
            constitutional_tags=constitutional_tags or ["F1", "F2"],
        )
    
    async def recall_implementations(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchResult]:
        """Recall past implementations relevant to query."""
        return await self._store.search(
            query=query,
            project_id="arifOS",
            area=MemoryArea.IMPLEMENTATION,
            limit=limit,
        )
    
    async def store_design(
        self,
        content: str,
        description: str,
        constitutional_tags: list[str] | None = None,
    ) -> tuple[bool, str | None]:
        """Store architecture/design memory."""
        return await self._store.store(
            content=f"{description}\n\n{content}",
            area=MemoryArea.DESIGN,
            project_id="arifOS",
            source="a-architect",
            source_agent=self.agent_id,
            constitutional_tags=constitutional_tags or ["F2", "F4", "F7"],
        )
    
    async def recall_designs(
        self,
        query: str,
        limit: int = 5,
    ) -> list[SearchResult]:
        """Recall past designs relevant to query."""
        return await self._store.search(
            query=query,
            project_id="arifOS",
            area=MemoryArea.DESIGN,
            limit=limit,
        )
