import json
import re
from typing import List, Dict, Any, Optional
from .types import MemoryCandidate, MemoryType, Authority

class BaseExtractor:
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        raise NotImplementedError

class FactExtractor(BaseExtractor):
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        # Simple rule-based extraction for now, in reality might call LLM
        candidates = []
        content = session_turn.get("content", "")
        # Look for "Fact: ..." or similar patterns
        matches = re.findall(r"Fact:\s*(.*)", content, re.IGNORECASE)
        for m in matches:
            candidates.append(MemoryCandidate(
                type=MemoryType.EPISODIC,
                subject="fact",
                content=m.strip(),
                summary=None,
                source_type="session_turn",
                source_ref={"turn_id": session_turn.get("id")},
                confidence=0.8,
                authority=Authority.SYSTEM_INFERRED
            ))
        return candidates

class PreferenceExtractor(BaseExtractor):
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        candidates = []
        content = session_turn.get("content", "")
        matches = re.findall(r"(?:I prefer|My preference is)\s*(.*)", content, re.IGNORECASE)
        for m in matches:
            candidates.append(MemoryCandidate(
                type=MemoryType.SEMANTIC,
                subject="user_preference",
                content=m.strip(),
                summary=None,
                source_type="session_turn",
                source_ref={"turn_id": session_turn.get("id")},
                confidence=0.9,
                authority=Authority.EXPLICIT_USER
            ))
        return candidates

class DecisionExtractor(BaseExtractor):
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        candidates = []
        # Extract decisions from context or content
        return candidates

class CorrectionDetector(BaseExtractor):
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        candidates = []
        content = session_turn.get("content", "")
        if "correction" in content.lower() or "wrong" in content.lower():
            # Flag as potential correction memory
            pass
        return candidates

class ProcedureExtractor(BaseExtractor):
    def extract(self, session_turn: Dict[str, Any], ctx: Dict[str, Any]) -> List[MemoryCandidate]:
        candidates = []
        return candidates

class SensitivityClassifier:
    def classify(self, candidate: MemoryCandidate) -> float:
        # Return risk score 0.0 - 1.0
        content = candidate.content.lower()
        risk_keywords = ["password", "secret", "api_key", "private", "personal"]
        if any(k in content for k in risk_keywords):
            return 0.9
        return 0.1

class AuthorityClassifier:
    def classify(self, candidate: MemoryCandidate) -> Authority:
        # Returns: explicit_user | system_inferred | document | unknown
        return candidate.authority
