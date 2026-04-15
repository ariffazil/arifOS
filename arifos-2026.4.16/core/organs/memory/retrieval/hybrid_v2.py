"""
Hybrid Retrieval v2 — Hardened

Features:
- Source weighting (confidence classes)
- Lane weighting
- Vault-backed rerank bonus
- Constitutional priority floor
- Vault outranks memory for governed truth
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ..types_v2 import MemoryRecord, MemoryQuery, MemoryType, ConfidenceClass, ContestedStatus


@dataclass
class RetrievalResult:
    """Result of hybrid retrieval."""
    records: list[MemoryRecord]
    retrieval_path: str
    total_candidates: int
    filtered_count: int
    vault_backed_count: int


class HybridRetrieval:
    """
    Hardened hybrid retrieval.
    
    Key principle: VAULT outranks MEMORY for governed truth.
    """
    
    # Lane priorities (higher = checked first)
    LANE_PRIORITY = {
        MemoryType.CONSTITUTIONAL: 100,
        MemoryType.SEMANTIC: 80,
        MemoryType.EPISODIC: 60,
        MemoryType.WORKING: 40,
    }
    
    # Source weights for scoring
    SOURCE_WEIGHTS = {
        ConfidenceClass.SEALED_FROM_VAULT: 1.0,
        ConfidenceClass.ASSERTED_BY_HUMAN: 0.9,
        ConfidenceClass.OBSERVED: 0.7,
        ConfidenceClass.DERIVED: 0.5,
        ConfidenceClass.INFERRED: 0.3,
    }
    
    def __init__(
        self,
        constitutional_lane,
        semantic_lane,
        episodic_lane,
        working_lane,
        vault_organ=None,  # For vault-backed verification
        vector_store=None,
    ):
        self.constitutional = constitutional_lane
        self.semantic = semantic_lane
        self.episodic = episodic_lane
        self.working = working_lane
        self.vault = vault_organ
        self.vector_store = vector_store
    
    async def retrieve(self, query: MemoryQuery) -> RetrievalResult:
        """
        Execute hardened hybrid retrieval.
        """
        candidates = []
        path_steps = []
        
        # 1. CONSTITUTIONAL FIRST (always, if available)
        if not query.memory_types or MemoryType.CONSTITUTIONAL in query.memory_types:
            rules = self.constitutional.get_all_rules()
            for rule in rules:
                if not rule.governance.superseded_by:  # Current rules only
                    score = self._score_constitutional(rule, query)
                    if score > 0:
                        candidates.append((rule, "constitutional", score))
            path_steps.append("constitutional")
        
        # 2. VAULT-BACKED SEMANTIC (highest trust)
        if not query.memory_types or MemoryType.SEMANTIC in query.memory_types:
            for mem in self.semantic._memories.values():
                if mem.governance.confidence_class == ConfidenceClass.SEALED_FROM_VAULT:
                    score = self._score_vault_backed(mem, query)
                    if score > 0.7:
                        candidates.append((mem, "vault_backed_semantic", score))
            path_steps.append("vault_backed")
        
        # 3. EXACT KEY LOOKUP
        if "." in query.query:
            fact = self.semantic.get_fact(query.query)
            if fact:
                # Check if contested
                if fact.governance.contested == ContestedStatus.UNCONTESTED:
                    candidates.append((fact, "exact_key", 0.95))
                elif fact.governance.contested == ContestedStatus.VAULT_OVERRULES:
                    # Lower score — vault has different truth
                    candidates.append((fact, "exact_key_contested", 0.5))
                path_steps.append("exact_key")
        
        # 4. SEMANTIC SEARCH
        if self.vector_store:
            vector_results = await self._vector_search(query)
            for record, score in vector_results:
                candidates.append((record, "vector", score))
            path_steps.append("vector")
        
        # 5. WORKING MEMORY (session context)
        if not query.memory_types or MemoryType.WORKING in query.memory_types:
            working = self.working.get_active()
            for mem in working:
                if query.query.lower() in mem.content.lower():
                    candidates.append((mem, "working_match", 0.8))
            path_steps.append("working")
        
        # 6. EPISODIC
        if not query.memory_types or MemoryType.EPISODIC in query.memory_types:
            events = self.episodic.find_events(query.query)
            for event in events[:5]:
                # Deprioritize contested events
                if event.governance.contested == ContestedStatus.UNCONTESTED:
                    candidates.append((event, "episodic", 0.6))
                else:
                    candidates.append((event, "episodic_contested", 0.3))
            path_steps.append("episodic")
        
        # Deduplicate
        seen = set()
        unique_candidates = []
        for record, source, score in candidates:
            if record.memory_id not in seen:
                seen.add(record.memory_id)
                unique_candidates.append((record, source, score))
        
        total_candidates = len(unique_candidates)
        vault_backed_count = sum(1 for r, _, _ in unique_candidates if r.retrieval.vault_backed)
        
        # Rerank with source weighting
        reranked = self._rerank(unique_candidates, query)
        
        # Filter
        filtered = self._filter_by_governance(reranked, query)
        filtered_count = total_candidates - len(filtered)
        
        return RetrievalResult(
            records=[r for r, _ in filtered[:query.limit]],
            retrieval_path=" → ".join(path_steps),
            total_candidates=total_candidates,
            filtered_count=filtered_count,
            vault_backed_count=vault_backed_count,
        )
    
    def _score_constitutional(self, rule: MemoryRecord, query: MemoryQuery) -> float:
        """Score constitutional rule match."""
        query_lower = query.query.lower()
        
        # Exact keyword match
        for kw in rule.retrieval.keywords:
            if kw in query_lower:
                return 1.0
        
        # Title match
        if query_lower in rule.title.lower():
            return 0.95
        
        return 0.0
    
    def _score_vault_backed(self, mem: MemoryRecord, query: MemoryQuery) -> float:
        """Score vault-backed memory with bonus."""
        query_lower = query.query.lower()
        
        # Base score from content match
        score = 0.0
        if query_lower in mem.title.lower():
            score = 0.9
        elif query_lower in mem.content.lower():
            score = 0.7
        
        # Vault-backed bonus
        if query.prefer_vault_backed and mem.retrieval.vault_backed:
            score += 0.2
        
        return min(1.0, score)
    
    def _rerank(
        self,
        candidates: list[tuple[MemoryRecord, str, float]],
        query: MemoryQuery,
    ) -> list[tuple[MemoryRecord, float]]:
        """
        Rerank with source weighting and lane priority.
        """
        scored = []
        
        for record, source, base_score in candidates:
            # Source weight from confidence class
            source_weight = self.SOURCE_WEIGHTS.get(
                record.governance.confidence_class, 0.5
            )
            
            # Lane priority bonus
            lane_priority = self.LANE_PRIORITY.get(record.memory_type, 50) / 100
            
            # Combine scores
            # Formula: base * source_weight * lane_priority
            final_score = base_score * source_weight * lane_priority
            
            # Recency boost (small)
            recency = record.retrieval.recency_score
            final_score += recency * query.recency_weight * 0.1
            
            # Importance boost
            importance = record.retrieval.importance_score
            final_score += importance * 0.1
            
            # Vault-backed bonus (extra)
            if record.retrieval.vault_backed and query.prefer_vault_backed:
                final_score += 0.15
            
            # Contested penalty
            if record.governance.contested != ContestedStatus.UNCONTESTED:
                final_score *= 0.5
            
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
            
            # Skip superseded
            if record.governance.superseded_by:
                continue
            
            # Scope check
            if query.scopes and record.scope.domain not in query.scopes:
                continue
            
            # Update access count
            record.time.access_count += 1
            record.time.last_accessed_at = datetime.utcnow()
            
            filtered.append((record, score))
        
        return filtered
    
    async def _vector_search(self, query: MemoryQuery) -> list[tuple[MemoryRecord, float]]:
        """Search using vector embeddings."""
        if not self.vector_store:
            return []
        return []
    
    async def get_context_for_session(
        self,
        session_id: str,
        query: str,
    ) -> dict:
        """Get full context for a session query."""
        # Working memory first
        working = self.working.get_active()
        
        # Then hybrid search
        result = await self.retrieve(MemoryQuery(
            query=query,
            limit=10,
            prefer_vault_backed=True,
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
                by_lane[lane].append({
                    "memory_id": record.memory_id,
                    "title": record.title,
                    "vault_backed": record.retrieval.vault_backed,
                    "confidence_class": record.governance.confidence_class.value,
                })
        
        return {
            "retrieval_path": result.retrieval_path,
            "working": [{"title": m.title, "content": m.content} for m in working[:3]],
            "constitutional": by_lane["constitutional"][:2],
            "semantic": by_lane["semantic"][:3],
            "episodic": by_lane["episodic"][:3],
            "stats": {
                "total_found": result.total_candidates,
                "vault_backed": result.vault_backed_count,
            },
        }
    
    def resolve_conflict(self, memories: list[MemoryRecord]) -> Optional[MemoryRecord]:
        """
        Resolve conflicting memories.
        
        Doctrine: Vault outranks memory for governed truth.
        """
        if not memories:
            return None
        
        # Separate vault-backed from regular
        vault_backed = [m for m in memories if m.retrieval.vault_backed]
        regular = [m for m in memories if not m.retrieval.vault_backed]
        
        # If any vault-backed, use highest confidence vault-backed
        if vault_backed:
            return max(vault_backed, key=lambda m: m.governance.confidence)
        
        # Otherwise, prefer human-asserted
        human_asserted = [
            m for m in regular 
            if m.governance.confidence_class == ConfidenceClass.ASSERTED_BY_HUMAN
        ]
        if human_asserted:
            return max(human_asserted, key=lambda m: m.governance.confidence)
        
        # Otherwise, highest confidence
        return max(regular, key=lambda m: m.governance.confidence)


from datetime import datetime
