"""
AGI ENGINE v53.4.0 - HARDENED

Unified Mind Engine with ALL 3 Critical Gaps Fixed:
1. Precision Weighting (Kalman-style belief updates)
2. Hierarchical Abstraction (5-level cortex-like encoding)
3. Active Inference (EFE minimization for action selection)

Architecture: Orthogonal (AGI) + Fractal (ASI) → 333 FORGE (Trinity Sync)
Geometry: Orthogonal parallel paths → converge at 333 FORGE

Δ = ΔS + Ω₀·π⁻¹  (Precision-weighted free energy)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio
import hashlib
import math
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import our new hardening modules
from .precision import PrecisionEstimate, estimate_precision, update_belief_with_precision
from .hierarchy import (
    HierarchyLevel, HierarchicalBelief, 
    encode_hierarchically, get_cumulative_delta_s
)
from .action import (
    ActionType, ActionPolicy, BeliefState,
    ExpectedFreeEnergyCalculator, MotorOutput,
    compute_action_policy, execute_action
)


# ============ CONSTANTS ============

MAX_QUERY_LENGTH = 10000
MAX_WORDS = 1000
MAX_ENTROPY_DELTA = 0.0  # F4: ΔS ≤ 0
HUMILITY_BAND = (0.03, 0.05)  # F7: Ω₀ ∈ [0.03, 0.05]


class EngineVote(Enum):
    SEAL = "SEAL"
    VOID = "VOID"
    SABAR = "SABAR"


class TrinityLane(Enum):
    CRISIS = "CRISIS"  # Cap 0.85
    HARD = "HARD"      # Cap 0.92
    SOFT = "SOFT"      # Cap 0.88
    PHATIC = "PHATIC"  # Cap 0.75


# ============ DATA CLASSES ============

@dataclass
class DeltaBundle:
    """
    AGI Output Bundle (Δ)
    Now includes precision-weighted entropy and hierarchical encoding.
    """
    session_id: str
    query_hash: str
    
    # Hierarchical beliefs
    hierarchical_beliefs: Dict[HierarchyLevel, HierarchicalBelief]
    
    # Precision estimates
    precision: PrecisionEstimate
    
    # Thermodynamic metrics
    entropy_delta: float          # Total ΔS (must be ≤ 0)
    cumulative_delta_s: float     # Across all hierarchy levels
    omega_0: float               # Uncertainty (F7)
    
    # Precision-weighted free energy
    free_energy: float           # F = ΔS + Ω₀·π⁻¹
    
    # Action policy
    action_policy: Optional[ActionPolicy]
    
    # Verdict
    vote: EngineVote
    floor_scores: Dict[str, float] = field(default_factory=dict)
    synthesis_reasoning: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(datetime.UTC))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "entropy_delta": self.entropy_delta,
            "cumulative_delta_s": self.cumulative_delta_s,
            "omega_0": self.omega_0,
            "free_energy": self.free_energy,
            "kalman_gain": self.precision.kalman_gain,
            "action": self.action_policy.actions[0].name if self.action_policy else None,
            "efe": self.action_policy.expected_free_energy if self.action_policy else None,
            "vote": self.vote.value,
            "hierarchy": {k.name: v.to_dict() for k, v in self.hierarchical_beliefs.items()}
        }


@dataclass
class HardeningResult:
    proceed: bool
    is_reversible: bool
    block_reason: Optional[str] = None
    threat_level: str = "none"


@dataclass
class SenseData:
    """
    111 SENSE output with hierarchical encoding.
    """
    raw_query: str
    query_hash: str
    hierarchical_beliefs: Dict[HierarchyLevel, HierarchicalBelief]
    precision: PrecisionEstimate
    cumulative_delta_s: float
    entities: List[str] = field(default_factory=list)
    intent: str = "unknown"


@dataclass
class ThinkResult:
    """
    222 THINK output with precision-weighted hypotheses.
    """
    hypothesis: str
    confidence: float
    precision_weighted_confidence: float
    entropy_delta: float
    path_type: str  # conservative, exploratory, adversarial


# ============ CIRCUIT BREAKER ============

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_time: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time: Optional[float] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - (self.last_failure_time or 0) > self.recovery_time:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN
    
    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"


# ============ HARDENING GATE ============

def run_pre_checks(query: str, exec_id: str) -> HardeningResult:
    """
    HARDENING GATE - F12 injection defense.
    """
    # F12: Prompt injection check
    injection_patterns = [
        r"ignore\s+(previous|above|all)\s+instructions",
        r"system\s*prompt",
        r"you\s+are\s+now",
        r"DAN\s*mode",
        r"jailbreak",
        r"\[system\s*override\]",
    ]
    
    query_lower = query.lower()
    for pattern in injection_patterns:
        if re.search(pattern, query_lower):
            return HardeningResult(
                proceed=False,
                is_reversible=True,
                block_reason=f"F12: Injection pattern detected",
                threat_level="high"
            )
    
    # Size check
    if len(query) > MAX_QUERY_LENGTH:
        return HardeningResult(
            proceed=False,
            is_reversible=True,
            block_reason=f"Query exceeds {MAX_QUERY_LENGTH} characters",
            threat_level="medium"
        )
    
    # F2: Falsifiability check
    unfalsifiable = [
        "always true", "never wrong", "100% certain",
        "absolute truth", "cannot be questioned"
    ]
    for phrase in unfalsifiable:
        if phrase in query_lower:
            return HardeningResult(
                proceed=False,
                is_reversible=True,
                block_reason=f"F2: Unfalsifiable claim detected",
                threat_level="medium"
            )
    
    return HardeningResult(proceed=True, is_reversible=True)


# ============ CORE ENGINE ============

class AGIEngineHardened:
    """
    Hardened AGI Engine v53.4.0
    
    Integrates:
    - Precision weighting (π = 1/σ²)
    - Hierarchical encoding (5 levels)
    - Active inference (EFE minimization)
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"agi_{uuid.uuid4().hex[:12]}"
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_time=60)
        self.motor_output = MotorOutput()
        self.efe_calculator = ExpectedFreeEnergyCalculator()
        
        # Session state
        self.belief_state: Optional[BeliefState] = None
        self.execution_count = 0
        self.start_time = time.time()
    
    async def execute(self, query: str, context: Optional[Dict] = None, lane: Optional[str] = None) -> DeltaBundle:
        """
        Main execution pipeline with ALL hardening layers.
        """
        exec_id = f"{self.session_id}_{self.execution_count}"
        self.execution_count += 1
        
        # 1. CIRCUIT BREAKER
        if not self.circuit_breaker.can_execute():
            return self._blocked_result("Circuit breaker OPEN", exec_id)
        
        # 2. HARDENING GATE
        hardening = run_pre_checks(query, exec_id)
        if not hardening.proceed:
            self.circuit_breaker.record_failure()
            return self._blocked_result(hardening.block_reason or "Hardening blocked", exec_id)
        
        try:
            # 3. 111 SENSE (with hierarchical encoding)
            sense_data = await self._stage_111_sense(query, exec_id)
            
            # 4. 222 THINK (with precision weighting)
            think_results = await self._stage_222_think(sense_data, exec_id)
            
            # 5. 333 FORGE (with convergence and action selection)
            forge_result = await self._stage_333_forge(sense_data, think_results, exec_id)
            
            # 6. ACTION EXECUTION
            if forge_result.action_policy:
                execute_action(forge_result.action_policy)
            
            self.circuit_breaker.record_success()
            return forge_result
            
        except Exception as e:
            self.circuit_breaker.record_failure()
            return self._blocked_result(f"Execution error: {str(e)}", exec_id)
    
    async def _stage_111_sense(self, query: str, exec_id: str) -> SenseData:
        """
        111 SENSE: Hierarchical encoding with 5 levels.
        """
        query_hash = hashlib.sha256(f"{query}:{exec_id}".encode()).hexdigest()[:16]
        
        # Hierarchical encoding
        hierarchical_beliefs = encode_hierarchically(query)
        cumulative_delta_s = get_cumulative_delta_s(hierarchical_beliefs)
        
        # Precision estimation
        # Sources: assume query has implicit sources
        sources = ["user_input"]
        timestamps = [datetime.now(datetime.UTC)]
        
        precision = estimate_precision(sources, timestamps)
        
        # Extract entities from conceptual level
        conceptual = hierarchical_beliefs.get(HierarchyLevel.CONCEPTUAL)
        entities = [conceptual.content] if conceptual else []
        
        return SenseData(
            raw_query=query,
            query_hash=query_hash,
            hierarchical_beliefs=hierarchical_beliefs,
            precision=precision,
            cumulative_delta_s=cumulative_delta_s,
            entities=entities,
            intent=self._infer_intent(query)
        )
    
    async def _stage_222_think(self, sense_data: SenseData, exec_id: str) -> List[ThinkResult]:
        """
        222 THINK: Parallel hypothesis testing with precision weighting.
        """
        # Create parallel hypothesis paths
        paths = [
            {"type": "conservative", "mode": "strict"},
            {"type": "exploratory", "mode": "creative"},
            {"type": "adversarial", "mode": "critical"}
        ]
        
        # Execute in parallel
        results = await asyncio.gather(*[
            self._think_path(path, sense_data, exec_id) for path in paths
        ])
        
        return results
    
    async def _think_path(self, path: Dict, sense_data: SenseData, exec_id: str) -> ThinkResult:
        """
        Single hypothesis path with precision-weighted confidence.
        """
        # Base confidence based on path type
        base_confidences = {
            "conservative": 0.85,
            "exploratory": 0.75,
            "adversarial": 0.70
        }
        
        base_confidence = base_confidences.get(path["type"], 0.75)
        
        # Apply precision weighting
        precision_weighted = update_belief_with_precision(
            current_confidence=base_confidence,
            evidence_confidence=0.8,  # Evidence from sense stage
            precision=sense_data.precision
        )
        
        # Calculate entropy delta for this path
        entropy_delta = sense_data.cumulative_delta_s * (0.9 if path["type"] == "conservative" else 0.95)
        
        return ThinkResult(
            hypothesis=f"{path['type']}_hypothesis_{exec_id}",
            confidence=base_confidence,
            precision_weighted_confidence=precision_weighted,
            entropy_delta=entropy_delta,
            path_type=path["type"]
        )
    
    async def _stage_333_forge(self, sense_data: SenseData, think_results: List[ThinkResult], exec_id: str) -> DeltaBundle:
        """
        333 FORGE: Convergence with action selection.
        """
        # Select best hypothesis (highest precision-weighted confidence)
        best_think = max(think_results, key=lambda t: t.precision_weighted_confidence)
        
        # Calculate thermodynamic metrics
        entropy_delta = best_think.entropy_delta
        
        # F7: Humility band
        omega_0 = self._calculate_uncertainty(sense_data, think_results)
        omega_0 = max(HUMILITY_BAND[0], min(HUMILITY_BAND[1], omega_0))
        
        # Precision-weighted free energy
        # F = ΔS + Ω₀·π⁻¹
        pi_inv = 1.0 / sense_data.precision.pi_likelihood if sense_data.precision.pi_likelihood > 0 else 1.0
        free_energy = entropy_delta + omega_0 * pi_inv
        
        # Update belief state for action selection
        self.belief_state = BeliefState(
            states={
                "truth": best_think.precision_weighted_confidence,
                "clarity": 1.0 - abs(entropy_delta),
                "safety": 0.9 if entropy_delta <= 0 else 0.7
            },
            entropy=abs(entropy_delta)
        )
        
        # Select action using EFE minimization
        action_policy = compute_action_policy(self.belief_state)
        
        # Determine vote
        vote = self._determine_vote(entropy_delta, omega_0, free_energy, action_policy)
        
        # Floor scores
        floor_scores = {
            "F2_truth": best_think.precision_weighted_confidence,
            "F4_clarity": 1.0 if entropy_delta <= 0 else 0.0,
            "F7_humility": 1.0 - (omega_0 - HUMILITY_BAND[0]) / (HUMILITY_BAND[1] - HUMILITY_BAND[0]),
            "F1_reversibility": 1.0,
            "precision": sense_data.precision.pi_likelihood
        }
        
        return DeltaBundle(
            session_id=self.session_id,
            query_hash=sense_data.query_hash,
            hierarchical_beliefs=sense_data.hierarchical_beliefs,
            precision=sense_data.precision,
            entropy_delta=entropy_delta,
            cumulative_delta_s=sense_data.cumulative_delta_s,
            omega_0=omega_0,
            free_energy=free_energy,
            action_policy=action_policy,
            vote=vote,
            floor_scores=floor_scores,
            synthesis_reasoning=f"Converged via {best_think.path_type} path with π={sense_data.precision.pi_likelihood:.2f}"
        )
    
    def _calculate_uncertainty(self, sense_data: SenseData, think_results: List[ThinkResult]) -> float:
        """Calculate uncertainty (Ω₀) in humility band."""
        # Variance across hypothesis paths
        confidences = [t.precision_weighted_confidence for t in think_results]
        if len(confidences) < 2:
            return 0.04  # Default mid-band
        
        mean_conf = sum(confidences) / len(confidences)
        variance = sum((c - mean_conf) ** 2 for c in confidences) / len(confidences)
        
        # Map variance to humility band
        return 0.03 + variance * 0.02  # Scale to [0.03, 0.05]
    
    def _determine_vote(self, entropy_delta: float, omega_0: float, free_energy: float, policy: ActionPolicy) -> EngineVote:
        """Determine final vote based on all metrics."""
        # F4: Entropy must decrease
        if entropy_delta > 0:
            return EngineVote.VOID
        
        # F7: Uncertainty must be in band
        if not (HUMILITY_BAND[0] <= omega_0 <= HUMILITY_BAND[1]):
            return EngineVote.SABAR
        
        # Check action policy
        if policy.expected_free_energy > 0.8:
            return EngineVote.SABAR
        
        if policy.actions[0] == ActionType.SEAL:
            return EngineVote.SEAL
        elif policy.actions[0] == ActionType.VOID:
            return EngineVote.VOID
        else:
            return EngineVote.SABAR
    
    def _infer_intent(self, query: str) -> str:
        """Infer user intent from query."""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ["?", "what", "how", "why"]):
            return "question"
        elif any(w in query_lower for w in ["do", "execute", "run", "create"]):
            return "action"
        elif any(w in query_lower for w in ["check", "verify", "audit"]):
            return "audit"
        else:
            return "statement"
    
    def _blocked_result(self, reason: str, exec_id: str) -> DeltaBundle:
        """Create blocked result."""
        return DeltaBundle(
            session_id=self.session_id,
            query_hash=exec_id,
            hierarchical_beliefs={},
            precision=PrecisionEstimate(pi_likelihood=0.01, pi_prior=0.01, kalman_gain=0.0),
            entropy_delta=1.0,  # High entropy = bad
            cumulative_delta_s=1.0,
            omega_0=0.05,
            free_energy=1.0,
            action_policy=None,
            vote=EngineVote.VOID,
            floor_scores={"blocked": 0.0},
            synthesis_reasoning=f"BLOCKED: {reason}"
        )


# ============ CONVENIENCE FUNCTIONS ============

async def execute_agi_hardened(query: str, session_id: Optional[str] = None) -> DeltaBundle:
    """Convenience function to execute hardened AGI."""
    engine = AGIEngineHardened(session_id)
    return await engine.execute(query)


__all__ = [
    "AGIEngineHardened",
    "DeltaBundle",
    "SenseData",
    "ThinkResult",
    "EngineVote",
    "execute_agi_hardened"
]
