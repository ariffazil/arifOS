"""
Semantic Memory Lane

Stable knowledge distilled from many episodes.

Characteristics:
- Canonical fact objects + embeddings
- Reusable patterns, schemas, doctrine
- Long-lived, updated by new evidence
- Generalized from specifics
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..types import MemoryRecord, MemoryType, Source, Scope, Governance, Time, RetentionClass


@dataclass
class SemanticMemoryLane:
    """
    Semantic memory stores stable knowledge.
    
    Examples:
    - "ARIF prefers governed mode"
    - "Vault is immutable"
    - "Memory is mutable and scoped"
    - Reusable schemas and patterns
    """
    
    _memories: dict[str, MemoryRecord] = field(default_factory=dict)
    _fact_index: dict[str, str] = field(default_factory=dict)  # fact_key -> memory_id
    
    def store_fact(
        self,
        title: str,
        content: str,
        fact_key: str,  # Canonical key for this fact (e.g., "arif.preferences.mode")
        source: Source,
        confidence: float = 0.9,
        embedding_id: Optional[str] = None,
    ) -> MemoryRecord:
        """
        Store a semantic fact.
        
        Facts are keyed for exact lookup and embedded for semantic search.
        """
        memory_id = f"mem_sem_{uuid.uuid4().hex[:12]}"
        
        # Check if fact already exists
        if fact_key in self._fact_index:
            old_id = self._fact_index[fact_key]
            # Mark old as superseded
            if old_id in self._memories:
                self._memories[old_id].lineage.superseded_by = memory_id
        
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=MemoryType.SEMANTIC,
            title=title,
            content=content,
            source=source,
            scope=Scope(
                owner="ARIF",
                domain="arifOS",
            ),
            governance=Governance(
                confidence=confidence,
                sensitivity="medium",
                requires_confirmation=False,
                promotable_to_vault=True,  # Core facts can become vault policy
                revocable=True,  # Facts can be updated
            ),
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=None,  # Semantic memories don't expire
            ),
            retrieval={
                "embedding_id": embedding_id,
                "keywords": fact_key.split("."),
                "entities": [fact_key.split(".")[0]] if "." in fact_key else [],
                "importance_score": confidence,
            },
            lane_data={
                "retention_class": RetentionClass.DURABLE.value,
                "fact_key": fact_key,
                "update_count": 0,
            }
        )
        
        self._memories[memory_id] = record
        self._fact_index[fact_key] = memory_id
        
        return record
    
    def get_fact(self, fact_key: str) -> Optional[MemoryRecord]:
        """Get fact by exact key lookup."""
        memory_id = self._fact_index.get(fact_key)
        if memory_id and memory_id in self._memories:
            mem = self._memories[memory_id]
            mem.time.last_accessed_at = datetime.utcnow()
            return mem
        return None
    
    def update_fact(
        self,
        fact_key: str,
        new_content: str,
        new_confidence: float,
        source: Source,
    ) -> Optional[MemoryRecord]:
        """
        Update a fact (supersede old version).
        
        Returns new record, marks old as superseded.
        """
        old_mem = self.get_fact(fact_key)
        if not old_mem:
            return None
        
        # Create new version
        new_mem = self.store_fact(
            title=old_mem.title,
            content=new_content,
            fact_key=fact_key,
            source=source,
            confidence=new_confidence,
        )
        
        # Update lane data
        new_mem.lane_data["update_count"] = old_mem.lane_data.get("update_count", 0) + 1
        
        return new_mem
    
    def get_schema(self, schema_type: str) -> list[MemoryRecord]:
        """Get all memories of a particular schema type."""
        results = []
        for mem in self._memories.values():
            if mem.lane_data.get("schema_type") == schema_type:
                results.append(mem)
        return results
    
    def get_doctrine(self) -> list[MemoryRecord]:
        """Get core doctrine (high importance semantic memories)."""
        results = []
        for mem in self._memories.values():
            if mem.retrieval.importance_score > 0.9:
                results.append(mem)
        return sorted(results, key=lambda m: m.retrieval.importance_score, reverse=True)
