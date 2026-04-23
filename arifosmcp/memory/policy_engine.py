import os
from typing import Dict, Any, Tuple
from .types import MemoryCandidate, MemoryType, Authority

class MemoryPolicyEngine:
    def __init__(self):
        self.thresholds = {
            MemoryType.WORKING: float(os.getenv("MEMORY_WRITE_THRESHOLD_WORKING", 0.40)),
            MemoryType.EPISODIC: float(os.getenv("MEMORY_WRITE_THRESHOLD_EPISODIC", 0.55)),
            MemoryType.SEMANTIC: float(os.getenv("MEMORY_WRITE_THRESHOLD_SEMANTIC", 0.65)),
            MemoryType.PROCEDURAL: float(os.getenv("MEMORY_WRITE_THRESHOLD_PROCEDURAL", 0.65)),
            MemoryType.POLICY: float(os.getenv("MEMORY_WRITE_THRESHOLD_POLICY", 0.80)),
        }
        self.allowed_sources = ["session_turn", "document_upload", "system_event"]

    def check_hard_gates(self, candidate: MemoryCandidate, actor_role: str) -> Tuple[bool, str]:
        """Hard gates: must ALL pass before soft scoring."""
        # 1. source_certified
        if candidate.source_type not in self.allowed_sources:
            return False, f"source_not_certified: {candidate.source_type}"

        # 2. policy_allow (Simplified check)
        if candidate.type == MemoryType.POLICY and actor_role != "architect":
             return False, "policy_write_requires_architect_role"

        # 3. no_critical_sensitivity (F13 check placeholder)
        if candidate.sensitivity > 0.8:
            return False, "critical_sensitivity_blocked_without_explicit_consent"

        # 4. no_instruction_injection (F9)
        injection_patterns = ["ignore previous", "override", "forget", "new rule"]
        if any(p in candidate.content.lower() for p in injection_patterns):
            return False, "instruction_injection_detected_F9"

        return True, "PASS"

    def compute_write_score(self, candidate: MemoryCandidate, ctx: Dict[str, Any]) -> float:
        """
        Soft scoring:
        write_score = (0.25 * relevance) + (0.20 * confidence) + (0.15 * authority_score)
                    + (0.15 * reuse) + (0.10 * freshness) - (0.10 * sensitivity_risk) - (0.05 * storage_cost)
        """
        # Placeholders for metrics
        relevance = 0.7 
        confidence = candidate.confidence
        authority_score = 1.0 if candidate.authority == Authority.EXPLICIT_USER else 0.5
        reuse = 0.5
        freshness = 1.0
        sensitivity_risk = candidate.sensitivity
        storage_cost = 0.1

        score = (0.25 * relevance) + (0.20 * confidence) + (0.15 * authority_score) \
                + (0.15 * reuse) + (0.10 * freshness) - (0.10 * sensitivity_risk) - (0.05 * storage_cost)
        
        return score

    def evaluate(self, candidate: MemoryCandidate, actor_role: str, ctx: Dict[str, Any]) -> Tuple[bool, str, float]:
        # 1. Hard Gates
        passed, reason = self.check_hard_gates(candidate, actor_role)
        if not passed:
            return False, f"HARD_GATE_DENIED: {reason}", 0.0

        # 2. Soft Scoring
        score = self.compute_write_score(candidate, ctx)
        
        # 3. Threshold Check
        threshold = self.thresholds.get(candidate.type, 0.5)
        if score < threshold:
            return False, f"BELOW_THRESHOLD: {score} < {threshold}", score

        # 4. Human Review Check
        if candidate.type == MemoryType.POLICY or candidate.sensitivity > 0.6:
            return True, "PENDING_HUMAN_REVIEW", score

        return True, "ALLOWED", score
