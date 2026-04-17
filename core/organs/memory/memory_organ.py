"""
arifOS.memory — The Governed, Revisable Persistence Layer for Relevance

Main organ that coordinates the 4 lanes and provides unified interface.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .lanes.constitutional import ConstitutionalMemoryLane
from .lanes.episodic import EpisodicMemoryLane
from .lanes.semantic import SemanticMemoryLane
from .lanes.working import WorkingMemoryLane
from .retrieval.hybrid import HybridRetrieval
from .types import (
    Governance,
    MemoryQuery,
    MemoryRecord,
    MemoryType,
    Scope,
    Source,
    Time,
    WriteReceipt,
)


@dataclass
class WriteGateResult:
    """Result of write gate check."""
    allowed: bool
    reason: str
    retention_class: str
    promotable: bool


class MemoryOrgan:
    """
    The memory organ coordinates 4 lanes:
    - Working: Session-scratch, short TTL
    - Episodic: Event history, timestamped
    - Semantic: Stable knowledge, facts
    - Constitutional: Core rules, read often, write rarely
    
    Lifecycle: capture → normalize → classify → embed → store → retrieve → compress → decay → promote or prune
    """
    
    def __init__(self, session_id: str | None = None):
        # Initialize lanes
        self.working = WorkingMemoryLane(session_id=session_id or "global")
        self.episodic = EpisodicMemoryLane()
        self.semantic = SemanticMemoryLane()
        self.constitutional = ConstitutionalMemoryLane()
        
        # Initialize retrieval
        self.retrieval = HybridRetrieval(
            constitutional_lane=self.constitutional,
            semantic_lane=self.semantic,
            episodic_lane=self.episodic,
            working_lane=self.working,
        )
        
        self.session_id = session_id
    
    # ===================== WRITE GATES =====================
    
    def _check_write_gate(self, record: MemoryRecord) -> WriteGateResult:
        """
        Judgment gate: Should this memory be written?
        
        Write only if:
        - Durable user preference
        - Recurring architectural rule
        - Important project event
        - Reusable technical pattern
        - Failure with future value
        - Explicit human decision
        
        Do NOT write:
        - Trivial chatter
        - Unstable guesses
        - Unverified claims
        - Emotionally loaded interpretations
        - Duplicate fragments with no new value
        """
        content = record.content.lower()
        title = record.title.lower()
        
        # Check for prohibited content
        prohibited = [
            "i think", "maybe", "probably", "guess",
            "feels like", "seems like", "i believe",
        ]
        for phrase in prohibited:
            if phrase in content and record.governance.confidence > 0.7:
                return WriteGateResult(
                    allowed=False,
                    reason=f"Unstable language detected: '{phrase}'",
                    retention_class="rejected",
                    promotable=False,
                )
        
        # Check for high-value signals
        high_value_signals = [
            "decided", "decision", "approved", "hold", "refused",
            "architecture", "pattern", "rule", "schema",
            "preference", "configured", "set to",
        ]
        
        has_high_value = any(sig in title or sig in content for sig in high_value_signals)
        
        # Determine retention class
        if record.memory_type == MemoryType.CONSTITUTIONAL:
            retention_class = "constitutional"
            promotable = True
        elif has_high_value and record.governance.confidence > 0.8:
            retention_class = "durable"
            promotable = True
        elif record.source.origin.value == "user" and record.governance.confidence > 0.7:
            retention_class = "project"
            promotable = True
        else:
            retention_class = "session"
            promotable = False
        
        return WriteGateResult(
            allowed=True,
            reason="Meets write criteria",
            retention_class=retention_class,
            promotable=promotable,
        )
    
    # ===================== WRITE OPERATIONS =====================
    
    async def write(
        self,
        title: str,
        content: str,
        memory_type: MemoryType,
        source: Source,
        confidence: float = 0.8,
        fact_key: str | None = None,
        **kwargs
    ) -> WriteReceipt | None:
        """
        Write to memory with judgment gate.
        """
        # Build candidate record
        memory_id = f"mem_{uuid.uuid4().hex[:16]}"
        
        record = MemoryRecord(
            memory_id=memory_id,
            memory_type=memory_type,
            title=title,
            content=content,
            source=source,
            scope=Scope(
                owner="ARIF",
                domain="arifOS",
                project=kwargs.get("project"),
            ),
            governance=Governance(
                confidence=confidence,
                sensitivity=kwargs.get("sensitivity", "low"),
                promotable_to_vault=False,  # Set by gate
                revocable=True,
            ),
            time=Time(created_at=datetime.utcnow()),
        )
        
        # Apply write gate
        gate = self._check_write_gate(record)
        if not gate.allowed:
            return None
        
        record.governance.promotable_to_vault = gate.promotable
        
        # Route to appropriate lane
        if memory_type == MemoryType.WORKING:
            stored = self.working.store(title, content, source)
        elif memory_type == MemoryType.EPISODIC:
            stored = self.episodic.record_event(
                title, content, source,
                project=kwargs.get("project")
            )
        elif memory_type == MemoryType.SEMANTIC and fact_key:
            stored = self.semantic.store_fact(
                title, content, fact_key, source, confidence
            )
        elif memory_type == MemoryType.CONSTITUTIONAL:
            # Constitutional only via amendment
            return None
        else:
            return None
        
        return WriteReceipt(
            memory_id=stored.memory_id,
            stored=True,
            embedding_created=False,  # Would be True if vector stored
            expires_at=stored.time.expires_at,
        )
    
    async def write_working(
        self,
        title: str,
        content: str,
        ttl_minutes: int = 60,
    ) -> MemoryRecord:
        """Convenience: Write to working memory."""
        return self.working.store(
            title=title,
            content=content,
            source=Source(origin="system", session_id=self.session_id),
            ttl_minutes=ttl_minutes,
        )
    
    async def write_episodic(
        self,
        title: str,
        content: str,
        project: str | None = None,
    ) -> MemoryRecord:
        """Convenience: Write episodic event."""
        return self.episodic.record_event(
            title=title,
            content=content,
            source=Source(origin="system", session_id=self.session_id),
            project=project,
        )
    
    async def write_semantic(
        self,
        title: str,
        content: str,
        fact_key: str,
        confidence: float = 0.9,
    ) -> MemoryRecord:
        """Convenience: Write semantic fact."""
        return self.semantic.store_fact(
            title=title,
            content=content,
            fact_key=fact_key,
            source=Source(origin="system", session_id=self.session_id),
            confidence=confidence,
        )
    
    # ===================== RETRIEVAL OPERATIONS =====================
    
    async def query(self, query_str: str, limit: int = 10) -> list[MemoryRecord]:
        """Query memory with hybrid retrieval."""
        result = await self.retrieval.retrieve(MemoryQuery(
            query=query_str,
            limit=limit,
        ))
        return result.records
    
    async def get_context(self, query: str) -> dict[str, Any]:
        """Get full context for query."""
        return await self.retrieval.get_context_for_session(self.session_id, query)
    
    def get_fact(self, fact_key: str) -> MemoryRecord | None:
        """Get semantic fact by exact key."""
        return self.semantic.get_fact(fact_key)
    
    def get_working(self) -> list[MemoryRecord]:
        """Get current working memory."""
        return self.working.get_active()
    
    def get_timeline(self, project: str | None = None) -> list[MemoryRecord]:
        """Get episodic timeline."""
        return self.episodic.get_timeline(project)
    
    # ===================== LIFECYCLE OPERATIONS =====================
    
    async def decay(self) -> dict[str, int]:
        """
        Apply decay to memory.
        
        Returns count of pruned memories by lane.
        """
        pruned = {"working": 0, "episodic": 0, "semantic": 0}
        
        # Working: clear expired
        before = len(self.working._memories)
        self.working.expire_old()
        pruned["working"] = before - len(self.working._memories)
        
        # Episodic: reduce recency scores
        for mem in self.episodic._memories.values():
            mem.retrieval.recency_score *= 0.99  # Slow decay
        
        # Semantic: no decay, but update importance
        
        return pruned
    
    async def promote_to_vault_candidate(self, memory_id: str) -> dict | None:
        """
        Check if memory can be promoted to vault.
        
        Returns promotion candidate or None if not promotable.
        """
        # Find memory in any lane
        record = None
        for lane in [self.working, self.episodic, self.semantic]:
            mem = lane._memories.get(memory_id)
            if mem:
                record = mem
                break
        
        if not record:
            return None
        
        # Check if promotable
        if not record.governance.promotable_to_vault:
            return None
        
        # Build promotion candidate
        return {
            "memory_id": memory_id,
            "title": record.title,
            "content": record.content,
            "memory_type": record.memory_type.value,
            "confidence": record.governance.confidence,
            "reason": "High confidence decision with governance impact",
        }


# Singleton
_memory_organ: MemoryOrgan | None = None


def get_memory_organ(session_id: str | None = None) -> MemoryOrgan:
    """Get or create memory organ."""
    global _memory_organ
    if _memory_organ is None:
        _memory_organ = MemoryOrgan(session_id=session_id)
    return _memory_organ
