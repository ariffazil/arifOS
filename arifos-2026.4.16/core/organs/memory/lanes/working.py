"""
Working Memory Lane

For the current session. Active task, immediate constraints, current plan.

Characteristics:
- Short TTL (session-scoped)
- Auto-expire
- High mutability
- Fast access
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

from ..types import MemoryRecord, MemoryType, Source, Scope, Governance, Time, RetentionClass


@dataclass
class WorkingMemoryLane:
    """
    Session-scoped working memory.
    
    Like human working memory: holds what's immediately relevant,
    discards when no longer needed.
    """
    session_id: str
    _memories: dict[str, MemoryRecord] = field(default_factory=dict)
    
    def store(
        self,
        title: str,
        content: str,
        source: Source,
        ttl_minutes: int = 60,
    ) -> MemoryRecord:
        """
        Store in working memory.
        
        Working memory items:
        - Active task
        - Immediate constraints
        - Current plan
        - Latest user intent
        - Unresolved ambiguity
        """
        memory_id = f"mem_work_{uuid.uuid4().hex[:12]}"
        
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=MemoryType.WORKING,
            title=title,
            content=content,
            source=Source(
                origin=source.origin,
                session_id=self.session_id,
                message_ref=source.message_ref,
            ),
            scope=Scope(
                owner="ARIF",
                visibility=source.origin.value == "user" and "private" or "shared",
                domain="arifOS",
            ),
            governance=Governance(
                confidence=0.9,  # Working memory is high-confidence immediate
                sensitivity="low",
                requires_confirmation=False,
                promotable_to_vault=False,  # Working memory never goes to vault
                revocable=True,
            ),
            time=Time(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
            ),
            retrieval={
                "keywords": title.lower().split(),
                "recency_score": 1.0,
            },
            lane_data={
                "retention_class": RetentionClass.SESSION.value,
                "access_count": 0,
            }
        )
        
        self._memories[memory_id] = record
        return record
    
    def get_active(self) -> list[MemoryRecord]:
        """Get all non-expired working memories for this session."""
        now = datetime.utcnow()
        active = []
        
        for mem in self._memories.values():
            if mem.time.expires_at and mem.time.expires_at > now:
                mem.time.last_accessed_at = now
                active.append(mem)
        
        # Sort by recency
        active.sort(key=lambda m: m.time.updated_at or m.time.created_at, reverse=True)
        return active
    
    def get_task(self) -> Optional[str]:
        """Get current active task if any."""
        for mem in self.get_active():
            if "task" in mem.title.lower():
                return mem.content
        return None
    
    def get_constraints(self) -> list[str]:
        """Get current constraints."""
        constraints = []
        for mem in self.get_active():
            if "constraint" in mem.title.lower():
                constraints.append(mem.content)
        return constraints
    
    def clear(self):
        """Clear all working memory (end of session)."""
        self._memories.clear()
    
    def expire_old(self):
        """Remove expired entries."""
        now = datetime.utcnow()
        expired = [
            mid for mid, mem in self._memories.items()
            if mem.time.expires_at and mem.time.expires_at <= now
        ]
        for mid in expired:
            del self._memories[mid]
