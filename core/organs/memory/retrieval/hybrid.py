"""
Hybrid Retrieval for Memory

Retrieval order:
1. Constitutional memory (exact lookup)
2. Exact key / symbolic lookup
3. Semantic vector search
4. Recency rerank
5. Human-intent rerank
6. Safety/governance filter

This avoids the "hantu problem" where vector recall feels clever but drifts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..types import MemoryRecord, MemoryQuery, MemoryType


@dataclass
class RetrievalResult:
    """Result of hybrid retrieval."""
    records: list[MemoryRecord]
    retrieval_path: str  # Which strategies were used
    total_candidates: int
    filtered_count: int


class HybridRetrieval:
    """
    Hybrid retrieval combining multiple strategies.
    
    Order:
    1. Constitutional (always check first)
    2. Exact key lookup (for facts)
    3. Semantic search (for concepts)
    4. Rerank by recency + importance
    5. Filter by governance
    """
    
    def __init__(
        self,
        constitutional_lane,
        semantic_lane,
        episodic_lane,
        working_lane,
        vector_store=None,
    ):
        self.constitutional = constitutional_lane
        self.semantic = semantic_lane
        self.episodic = episodic_lane
        self.working = working_lane
        self.vector_store = vector_store
    
    async def retrieve(self, query: MemoryQuery) -> RetrievalResult:
        """
        Execute hybrid retrieval.
        """
        candidates = []
        path_steps = []
        
        # 1. Constitutional memory (exact lookup)
        if not query.memory_types or MemoryType.CONSTITUTIONAL in query.memory_types:
            rules = self.constitutional.get_all_rules()
            # Filter by keyword match
            for rule in rules:
                if any(kw in query.query.lower() for kw in rule.retrieval.keywords):
                    candidates.append((rule, "constitutional_match", 1.0))
            path_steps.append("constitutional")
        
        # 2. Exact key lookup (for semantic facts)
        if "." in query.query:  # Looks like a fact key
            fact = self.semantic.get_fact(query.query)
            if fact:
                candidates.append((fact, "exact_key", 1.0))
                path_steps.append("exact_key")
        
        # 3. Semantic vector search
        if self.vector_store:
            vector_results = await self._vector_search(query)
            for record, score in vector_results:
                candidates.append((record, "vector", score))
            path_steps.append("vector")
        
        # 4. Working memory (for session context)
        if not query.memory_types or MemoryType.WORKING in query.memory_types:
            working = self.working.get_active()
            for mem in working:
                # Simple text match for working memory
                if query.query.lower() in mem.content.lower():
                    candidates.append((mem, "working_match", 0.9))
            path_steps.append("working")
        
        # 5. Episodic for events
        if not query.memory_types or MemoryType.EPISODIC in query.memory_types:
            events = self.episodic.find_events(query.query)
            for event in events[:5]:
                candidates.append((event, "episodic", 0.7))
            path_steps.append("episodic")
        
        # Deduplicate by memory_id
        seen = set()
        unique_candidates = []
        for record, source, score in candidates:
            if record.memory_id not in seen:
                seen.add(record.memory_id)
                unique_candidates.append((record, source, score))
        
        total_candidates = len(unique_candidates)
        
        # 6. Rerank
        reranked = self._rerank(unique_candidates, query)
        
        # 7. Governance filter
        filtered = self._filter_by_governance(reranked, query)
        filtered_count = total_candidates - len(filtered)
        
        # Return top results
        return RetrievalResult(
            records=[r for r, _ in filtered[:query.limit]],
            retrieval_path=" → ".join(path_steps),
            total_candidates=total_candidates,
            filtered_count=filtered_count,
        )
    
    async def _vector_search(self, query: MemoryQuery) -> list[tuple[MemoryRecord, float]]:
        """Search using vector embeddings."""
        if not self.vector_store:
            return []
        
        # Would call out to Qdrant/Pinecone/etc
        # For now, return empty
        return []
    
    def _rerank(
        self,
        candidates: list[tuple[MemoryRecord, str, float]],
        query: MemoryQuery,
    ) -> list[tuple[MemoryRecord, float]]:
        """
        Rerank by combining multiple signals.
        """
        scored = []
        
        for record, source, base_score in candidates:
            # Combine scores
            semantic_component = base_score * query.semantic_weight
            
            # Recency component
            recency = record.retrieval.recency_score
            recency_component = recency * query.recency_weight
            
            # Importance boost
            importance_boost = record.retrieval.importance_score * 0.2
            
            # Constitutional boost (always prioritize)
            if record.memory_type == MemoryType.CONSTITUTIONAL:
                importance_boost += 0.5
            
            final_score = semantic_component + recency_component + importance_boost
            
            # Confidence threshold
            if record.governance.confidence >= query.min_confidence:
                scored.append((record, final_score))
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def _filter_by_governance(
        self,
        candidates: list[tuple[MemoryRecord, float]],
        query: MemoryQuery,
    ) -> list[tuple[MemoryRecord, float]]:
        """Filter by governance rules."""
        filtered = []
        
        for record, score in candidates:
            # Skip expired
            if record.time.expires_at and record.time.expires_at < datetime.utcnow():
                continue
            
            # Skip low confidence
            if record.governance.confidence < query.min_confidence:
                continue
            
            # Scope check
            if query.scopes and record.scope.domain not in query.scopes:
                continue
            
            filtered.append((record, score))
        
        return filtered
    
    async def get_context_for_session(
        self,
        session_id: str,
        query: str,
    ) -> dict:
        """
        Get full context for a session query.
        
        Returns structured context from all lanes.
        """
        # Working memory first
        working = self.working.get_active()
        
        # Then hybrid search
        result = await self.retrieve(MemoryQuery(
            query=query,
            limit=10,
        ))
        
        # Organize by lane
        by_lane = {
            "constitutional": [],
            "semantic": [],
            "episodic": [],
            "working": [],
        }
        
        for record in result.records:
            lane = record.memory_type.value
            if lane in by_lane:
                by_lane[lane].append(record)
        
        return {
            "retrieval_path": result.retrieval_path,
            "working": working[:3],  # Most recent working memory
            "constitutional": by_lane["constitutional"][:2],
            "semantic": by_lane["semantic"][:3],
            "episodic": by_lane["episodic"][:3],
            "total_found": result.total_candidates,
        }


from datetime import datetime
