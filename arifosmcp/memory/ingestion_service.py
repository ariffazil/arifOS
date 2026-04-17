import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4

from .types import MemoryRecord, MemoryCandidate, MemoryType, MemoryStatus, RetentionClass, EmbeddingStatus
from .extractors import (
    FactExtractor, PreferenceExtractor, DecisionExtractor, 
    CorrectionDetector, ProcedureExtractor, SensitivityClassifier, AuthorityClassifier
)
from .policy_engine import MemoryPolicyEngine

class MemoryIngestionService:
    def __init__(self, db_client=None, qdrant_client=None):
        self.db = db_client
        self.qdrant = qdrant_client
        self.policy_engine = MemoryPolicyEngine()
        self.extractors = [
            FactExtractor(), PreferenceExtractor(), DecisionExtractor(),
            CorrectionDetector(), ProcedureExtractor()
        ]
        self.sensitivity_classifier = SensitivityClassifier()
        self.authority_classifier = AuthorityClassifier()

    def _compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()

    def _assign_retention(self, record: MemoryRecord):
        now = datetime.utcnow()
        if record.type == MemoryType.WORKING:
            record.expires_at = now + timedelta(hours=2)
            record.retention_class = RetentionClass.TRANSIENT
        elif record.type == MemoryType.EPISODIC:
            record.expires_at = now + timedelta(days=60)
            record.retention_class = RetentionClass.REVIEWABLE
        elif record.type == MemoryType.SEMANTIC:
            record.expires_at = None
            record.retention_class = RetentionClass.DURABLE
        elif record.type == MemoryType.PROCEDURAL:
            record.expires_at = None
            record.retention_class = RetentionClass.DURABLE
        elif record.type == MemoryType.POLICY:
            record.expires_at = None
            record.retention_class = RetentionClass.IMMUTABLE_AUDIT
            record.revocable = False

    async def ingest(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = []
        
        # 1. Extract candidates
        candidates = []
        for ext in self.extractors:
            candidates.extend(ext.extract(session_turn, ctx))
            
        for candidate in candidates:
            # 2. Classify
            candidate.sensitivity = self.sensitivity_classifier.classify(candidate)
            candidate.authority = self.authority_classifier.classify(candidate)
            candidate.hash = self._compute_hash(candidate.content)
            
            # 3. Policy Evaluation
            actor_role = ctx.get("actor_role", "user")
            allowed, reason, score = self.policy_engine.evaluate(candidate, actor_role, ctx)
            
            verdict = {
                "candidate": candidate.content[:50] + "...",
                "allowed": allowed,
                "reason": reason,
                "score": score,
                "memory_id": None
            }
            
            if allowed:
                # 4. Normalize and Persist
                record = MemoryRecord(
                    memory_id=uuid4(),
                    actor_id=ctx.get("actor_id", "anonymous"),
                    session_id=ctx.get("session_id", "unknown"),
                    type=candidate.type,
                    subject=candidate.subject,
                    content=candidate.content,
                    summary=candidate.summary,
                    source_type=candidate.source_type,
                    source_ref=candidate.source_ref,
                    confidence=candidate.confidence,
                    authority=candidate.authority,
                    sensitivity=candidate.sensitivity,
                    consent_level=candidate.consent_level,
                    tags=candidate.tags,
                    hash=candidate.hash
                )
                self._assign_retention(record)
                
                # Mock DB Persistence
                # await self.db.execute("INSERT INTO memory_records ...", record.__dict__)
                verdict["memory_id"] = str(record.memory_id)
                
                # 5. Queue Embedding
                if record.status == MemoryStatus.ACTIVE:
                    # await self.db.execute("INSERT INTO memory_write_queue ...", record.memory_id)
                    pass
                
                # 6. Audit
                # await audit_logger.log("MEMORY_WRITE_ALLOWED", record)
            else:
                # await audit_logger.log("MEMORY_WRITE_DENIED" if "DENIED" in reason else "MEMORY_WRITE_SKIPPED", candidate)
                pass
                
            results.append(verdict)
            
        return results
