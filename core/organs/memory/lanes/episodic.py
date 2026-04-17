"""
Episodic Memory Lane

Event/history memory. "On date X, user decided Y."

Characteristics:
- Timestamped event records
- Immutable once written (but can be superseded)
- Personal history
- Time-sequenced
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from ..types import (
    Governance,
    Lineage,
    MemoryRecord,
    MemoryType,
    RetentionClass,
    Scope,
    Source,
    Time,
)


@dataclass
class EpisodicMemoryLane:
    """
    Episodic memory stores events and decisions.
    
    Format: timestamped event records
    Examples:
    - "On 2026-04-06, ARIF decided to split memory and vault"
    - "This architecture changed from A to B"
    - "Tool call failed with error Z"
    """
    
    _memories: dict[str, MemoryRecord] = field(default_factory=dict)
    _chronological: list[str] = field(default_factory=list)  # memory_ids in time order
    
    def record_event(
        self,
        title: str,
        content: str,
        source: Source,
        event_timestamp: datetime | None = None,
        project: str | None = None,
    ) -> MemoryRecord:
        """
        Record an episodic memory (event).
        
        Events are immutable once recorded, but can be superseded
        by later understanding.
        """
        memory_id = f"mem_ep_{uuid.uuid4().hex[:12]}"
        
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=MemoryType.EPISODIC,
            title=title,
            content=content,
            source=source,
            scope=Scope(
                owner="ARIF",
                domain="arifOS",
                project=project,
            ),
            governance=Governance(
                confidence=0.95,  # Episodic is witnessed
                sensitivity="medium",
                requires_confirmation=False,
                promotable_to_vault=True,  # Important events can go to vault
                revocable=False,  # Episodic is immutable (but can be superseded)
            ),
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                # Episodic memories last until explicitly superseded
                expires_at=None,
            ),
            retrieval={
                "keywords": self._extract_keywords(title, content),
                "recency_score": 0.5,  # Episodic decays slower than working
            },
            lineage=Lineage(
                derived_from=[source.message_ref] if source.message_ref else []
            ),
            lane_data={
                "retention_class": RetentionClass.PROJECT.value,
                "event_timestamp": event_timestamp.isoformat() if event_timestamp else None,
                "importance_decay_rate": 0.01,  # Very slow decay
            }
        )
        
        self._memories[memory_id] = record
        self._chronological.append(memory_id)
        
        return record
    
    def get_timeline(
        self,
        project: str | None = None,
        limit: int = 50,
    ) -> list[MemoryRecord]:
        """Get chronological timeline of events."""
        results = []
        
        for mem_id in reversed(self._chronological[-limit:]):
            mem = self._memories.get(mem_id)
            if mem and (not project or mem.scope.project == project):
                results.append(mem)
        
        return results
    
    def find_events(
        self,
        keyword: str,
        project: str | None = None,
    ) -> list[MemoryRecord]:
        """Find events matching keyword."""
        results = []
        keyword_lower = keyword.lower()
        
        for mem in self._memories.values():
            if mem.memory_type != MemoryType.EPISODIC:
                continue
            if project and mem.scope.project != project:
                continue
            
            if (keyword_lower in mem.title.lower() or 
                keyword_lower in mem.content.lower()):
                results.append(mem)
        
        # Sort by timestamp
        results.sort(key=lambda m: m.time.created_at, reverse=True)
        return results
    
    def get_decisions(self, project: str | None = None) -> list[MemoryRecord]:
        """Get decision events."""
        return self.find_events("decided", project) + self.find_events("decision", project)
    
    def _extract_keywords(self, title: str, content: str) -> list[str]:
        """Extract keywords from event text."""
        # Simple extraction - would use NLP in production
        text = f"{title} {content}".lower()
        words = text.split()
        # Filter for meaningful words
        stopwords = {"the", "a", "an", "to", "of", "in", "on", "with"}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return list(set(keywords))[:10]  # Top 10 unique keywords
