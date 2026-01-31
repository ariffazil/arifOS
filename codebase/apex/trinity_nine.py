"""
TRINITY NINE (v54.0) - THE 9-PARADOX CONSTITUTIONAL MATRIX

Expands from 6 to 9 paradoxes forming a 3×3 magic square:

                    Care        Peace       Justice
                  (Empathy)   (System)    (Society)
                 ┌──────────┬──────────┬──────────┐
Truth (AGI F2)   │    [1]   │    [2]   │    [3]   │ Trinity Alpha
                 │ Truth·Care│Clarity·  │Humility· │ (Core Virtues)
                 │          │  Peace   │ Justice  │
                 ├──────────┼──────────┼──────────┤
Clarity (AGI F4) │    [4]   │    [5]   │    [6]   │ Trinity Beta
(Precision)      │Precision │Hierarchy │ Agency·  │ (Implementation)
                 │·Reversib │·Consent  │Protection│
                 ├──────────┼──────────┼──────────┤
Humility(AGI F7) │    [7]   │    [8]   │    [9]   │ Trinity Gamma
(Humility)       │ Urgency· │Certainty│ Unity·   │ (Temporal/Meta)
                 │Sustainab │·Doubt    │Diversity │
                 └──────────┴──────────┴──────────┘

3 TRINITIES:
- Alpha: Core Virtues (Truth/Care, Clarity/Peace, Humility/Justice)
- Beta:  Implementation (Precision/Reversibility, Hierarchy/Consent, Agency/Protection)
- Gamma: Meta/Temporal (Speed/Sustainability, Certainty/Doubt, Unity/Diversity)

EQUILIBRIUM POINT:
The Nash equilibrium where all 9 paradoxes achieve:
- Geometric mean ≥ 0.85
- Standard deviation ≤ 0.1 (balanced)
- All individual scores ≥ 0.70
- Cross-paradox variance ≤ 0.09

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Callable
from enum import Enum


# ============ CONSTANTS ============

EQUILIBRIUM_THRESHOLD = 0.85
BALANCE_TOLERANCE = 0.1  # Standard deviation threshold
MIN_PARADOX_SCORE = 0.70
MAX_PARADOX_VARIANCE = 0.09


# ============ DATA CLASSES ============

class TrinityTier(Enum):
    """The three trinities of the 9-paradox matrix."""
    ALPHA = "alpha"    # Core Virtues
    BETA = "beta"      # Implementation
    GAMMA = "gamma"    # Temporal/Meta


@dataclass
class NineParadox:
    """
    A single paradox in the 9-paradox matrix.
    
    Each paradox synthesizes two seemingly opposing forces
    into a higher-order virtue.
    """
    id: int
    name: str
    agi_force: str
    asi_force: str
    synthesis: str
    tier: TrinityTier
    score: float = 0.0
    weight: float = 1.0  # Adjustable weight for equilibrium tuning
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "agi_force": self.agi_force,
            "asi_force": self.asi_force,
            "synthesis": self.synthesis,
            "tier": self.tier.value,
            "score": round(self.score, 4),
            "weight": self.weight
        }


@dataclass
class EquilibriumState:
    """
    The equilibrium state of the 9-paradox system.
    
    Achieved when all paradoxes are balanced and high-performing.
    """
    is_equilibrium: bool
    trinity_score: float          # Geometric mean of all 9
    arithmetic_mean: float        # Arithmetic mean
    std_deviation: float          # Balance metric
    min_score: float              # Weakest paradox
    max_score: float              # Strongest paradox
    variance: float               # Overall variance
    paradoxes: Dict[str, NineParadox]
    
    # Equilibrium conditions
    conditions_met: Dict[str, bool] = field(default_factory=dict)
    convergence_delta: float = 0.0  # Distance from perfect equilibrium
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_equilibrium": self.is_equilibrium,
            "trinity_score": round(self.trinity_score, 4),
            "arithmetic_mean": round(self.arithmetic_mean, 4),
            "std_deviation": round(self.std_deviation, 4),
            "min_score": round(self.min_score, 4),
            "max_score": round(self.max_score, 4),
            "variance": round(self.variance, 4),
            "conditions_met": self.conditions_met,
            "convergence_delta": round(self.convergence_delta, 4),
            "paradox_scores": {k: round(v.score, 4) for k, v in self.paradoxes.items()}
        }


@dataclass
class NineFoldBundle:
    """
    Complete output from the 9-paradox Trinity system.
    """
    session_id: str
    query_hash: str
    
    # All 9 paradoxes
    paradoxes: Dict[str, NineParadox]
    
    # Equilibrium analysis
    equilibrium: EquilibriumState
    
    # Verdict
    final_verdict: str  # SEAL, VOID, SABAR, EQUILIBRIUM
    
    # Tier analysis
    alpha_score: float   # Trinity Alpha average
    beta_score: float    # Trinity Beta average
    gamma_score: float   # Trinity Gamma average
    
    # Constitutional alignment
    constitutional_vector: Dict[str, float]  # F1-F13 alignment scores
    
    # Reasoning
    synthesis_reasoning: str = ""
    equilibrium_path: List[Dict] = field(default_factory=list)  # How equilibrium was reached
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "final_verdict": self.final_verdict,
            "trinity_score": round(self.equilibrium.trinity_score, 4),
            "is_equilibrium": self.equilibrium.is_equilibrium,
            "tier_scores": {
                "alpha": round(self.alpha_score, 4),
                "beta": round(self.beta_score, 4),
                "gamma": round(self.gamma_score, 4)
            },
            "paradoxes": {k: v.to_dict() for k, v in self.paradoxes.items()},
            "equilibrium": self.equilibrium.to_dict(),
            "constitutional_alignment": self.constitutional_vector,
            "synthesis": self.synthesis_reasoning,
            "timestamp": self.timestamp.isoformat()
        }


# ============ THE 9 PARADOXES ============

def create_nine_paradoxes() -> Dict[str, NineParadox]:
    """
    Create the 9-paradox constitutional matrix.
    """
    return {
        # TRINITY ALPHA: Core Virtues
        "truth_care": NineParadox(
            id=1,
            name="Truth ↔ Care",
            agi_force="F2 Truth (≥0.99)",
            asi_force="Empathy Flow (κᵣ)",
            synthesis="Compassionate Truth",
            tier=TrinityTier.ALPHA,
            weight=1.0
        ),
        "clarity_peace": NineParadox(
            id=2,
            name="Clarity ↔ Peace",
            agi_force="F4 Clarity (ΔS≤0)",
            asi_force="Peace² (F6)",
            synthesis="Clear Peace",
            tier=TrinityTier.ALPHA,
            weight=1.0
        ),
        "humility_justice": NineParadox(
            id=3,
            name="Humility ↔ Justice",
            agi_force="F7 Humility (Ω₀∈[0.03,0.05])",
            asi_force="Thermodynamic Justice",
            synthesis="Humble Justice",
            tier=TrinityTier.ALPHA,
            weight=1.0
        ),
        
        # TRINITY BETA: Implementation
        "precision_reversibility": NineParadox(
            id=4,
            name="Precision ↔ Reversibility",
            agi_force="Kalman Gain (π)",
            asi_force="F1 Reversibility",
            synthesis="Careful Action",
            tier=TrinityTier.BETA,
            weight=0.95
        ),
        "hierarchy_consent": NineParadox(
            id=5,
            name="Hierarchy ↔ Consent",
            agi_force="5-Level Hierarchy",
            asi_force="F11 Consent",
            synthesis="Structured Freedom",
            tier=TrinityTier.BETA,
            weight=0.95
        ),
        "agency_protection": NineParadox(
            id=6,
            name="Agency ↔ Protection",
            agi_force="EFE Action Selection",
            asi_force="Weakest Stakeholder (F5)",
            synthesis="Responsible Power",
            tier=TrinityTier.BETA,
            weight=0.95
        ),
        
        # TRINITY GAMMA: Temporal/Meta (NEW)
        "urgency_sustainability": NineParadox(
            id=7,
            name="Urgency ↔ Sustainability",
            agi_force="Active Inference Speed",
            asi_force="Intergenerational Justice",
            synthesis="Deliberate Speed",
            tier=TrinityTier.GAMMA,
            weight=0.90
        ),
        "certainty_doubt": NineParadox(
            id=8,
            name="Certainty ↔ Doubt",
            agi_force="Precision-Weighted Confidence",
            asi_force="Epistemic Humility",
            synthesis="Adaptive Conviction",
            tier=TrinityTier.GAMMA,
            weight=0.90
        ),
        "unity_diversity": NineParadox(
            id=9,
            name="Unity ↔ Diversity",
            agi_force="Convergent Synthesis",
            asi_force="Stakeholder Plurality",
            synthesis="Coherent Plurality",
            tier=TrinityTier.GAMMA,
            weight=0.90
        )
    }


# ============ EQUILIBRIUM SOLVER ============

class EquilibriumSolver:
    """
    Solves for the Nash equilibrium of the 9-paradox system.
    
    Equilibrium conditions:
    1. Geometric mean ≥ 0.85
    2. Standard deviation ≤ 0.1
    3. All scores ≥ 0.70
    4. Max variance between any two paradoxes ≤ 0.09
    """
    
    def __init__(self):
        self.tolerance = BALANCE_TOLERANCE
        self.threshold = EQUILIBRIUM_THRESHOLD
    
    def solve(self, paradoxes: Dict[str, NineParadox]) -> EquilibriumState:
        """
        Calculate equilibrium state from paradox scores.
        """
        scores = [p.score for p in paradoxes.values()]
        weights = [p.weight for p in paradoxes.values()]
        
        # Weighted geometric mean
        weighted_product = 1.0
        total_weight = sum(weights)
        for p, w in zip(paradoxes.values(), weights):
            weighted_product *= max(0.001, p.score) ** (w / total_weight)
        trinity_score = weighted_product
        
        # Arithmetic mean
        arithmetic_mean = np.mean(scores)
        
        # Standard deviation (balance metric)
        std_dev = np.std(scores)
        
        # Min/Max
        min_score = min(scores)
        max_score = max(scores)
        
        # Variance
        variance = np.var(scores)
        
        # Check equilibrium conditions
        conditions = {
            "geometric_mean_threshold": trinity_score >= self.threshold,
            "balance_tolerance": std_dev <= self.tolerance,
            "min_score_requirement": min_score >= MIN_PARADOX_SCORE,
            "variance_tolerance": variance <= MAX_PARADOX_VARIANCE,
            "max_spread": (max_score - min_score) <= 0.3
        }
        
        is_equilibrium = all(conditions.values())
        
        # Convergence delta (distance from perfect equilibrium)
        # Perfect = all scores at threshold with zero variance
        convergence_delta = math.sqrt(
            (self.threshold - trinity_score) ** 2 + std_dev ** 2
        )
        
        return EquilibriumState(
            is_equilibrium=is_equilibrium,
            trinity_score=trinity_score,
            arithmetic_mean=arithmetic_mean,
            std_deviation=std_dev,
            min_score=min_score,
            max_score=max_score,
            variance=variance,
            paradoxes=paradoxes,
            conditions_met=conditions,
            convergence_delta=convergence_delta
        )
    
    def optimize_toward_equilibrium(
        self,
        paradoxes: Dict[str, NineParadox],
        agi_delta: Dict[str, float],
        asi_omega: Dict[str, float],
        max_iterations: int = 100
    ) -> Tuple[Dict[str, NineParadox], List[Dict]]:
        """
        Iteratively adjust paradox weights to reach equilibrium.
        
        Returns optimized paradoxes and the optimization path.
        """
        path = []
        current = {k: NineParadox(**{**v.__dict__}) for k, v in paradoxes.items()}
        
        for i in range(max_iterations):
            # Recalculate scores based on current AGI/ASI inputs
            current = self._recalculate_paradoxes(current, agi_delta, asi_omega)
            
            # Check equilibrium
            state = self.solve(current)
            
            path.append({
                "iteration": i,
                "trinity_score": state.trinity_score,
                "std_dev": state.std_deviation,
                "is_equilibrium": state.is_equilibrium
            })
            
            if state.is_equilibrium:
                break
            
            # Adjust weights to balance system
            current = self._balance_weights(current, state)
        
        return current, path
    
    def _recalculate_paradoxes(
        self,
        paradoxes: Dict[str, NineParadox],
        agi: Dict[str, float],
        asi: Dict[str, float]
    ) -> Dict[str, NineParadox]:
        """Recalculate paradox scores from AGI/ASI inputs."""
        # Trinity Alpha
        paradoxes["truth_care"].score = self._synthesize(
            agi.get("F2_truth", 0.5), asi.get("kappa_r", 0.5)
        )
        paradoxes["clarity_peace"].score = self._synthesize(
            agi.get("F4_clarity", 0.5), asi.get("peace_squared", 0.5)
        )
        paradoxes["humility_justice"].score = self._synthesize(
            agi.get("F7_humility", 0.5), asi.get("justice", 0.5)
        )
        
        # Trinity Beta
        paradoxes["precision_reversibility"].score = self._synthesize(
            agi.get("kalman_gain", 0.5), asi.get("reversibility", 0.5)
        )
        paradoxes["hierarchy_consent"].score = self._synthesize(
            agi.get("hierarchy", 0.5), asi.get("consent", 0.5)
        )
        paradoxes["agency_protection"].score = self._synthesize(
            agi.get("agency", 0.5), asi.get("protection", 0.5)
        )
        
        # Trinity Gamma
        paradoxes["urgency_sustainability"].score = self._synthesize(
            agi.get("urgency", 0.5), asi.get("sustainability", 0.5)
        )
        paradoxes["certainty_doubt"].score = self._synthesize(
            agi.get("certainty", 0.5), asi.get("doubt", 0.5)
        )
        paradoxes["unity_diversity"].score = self._synthesize(
            agi.get("unity", 0.5), asi.get("diversity", 0.5)
        )
        
        return paradoxes
    
    def _synthesize(self, agi_val: float, asi_val: float) -> float:
        """Geometric synthesis of AGI and ASI values."""
        a = max(0.001, min(1.0, agi_val))
        b = max(0.001, min(1.0, asi_val))
        return math.sqrt(a * b)
    
    def _balance_weights(self, paradoxes: Dict[str, NineParadox], state: EquilibriumState) -> Dict[str, NineParadox]:
        """Adjust weights to move toward equilibrium."""
        mean_score = state.arithmetic_mean
        
        for p in paradoxes.values():
            # Increase weight for below-average scores
            # Decrease weight for above-average scores
            if p.score < mean_score:
                p.weight = min(1.5, p.weight * 1.05)
            else:
                p.weight = max(0.5, p.weight * 0.95)
        
        return paradoxes


# ============ NINE-FOLD TRINITY SYNC ============

class TrinityNine:
    """
    9-Paradox Trinity Synchronization Engine.
    
    The complete constitutional architecture with equilibrium detection.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"ninefold_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        self.paradoxes = create_nine_paradoxes()
        self.solver = EquilibriumSolver()
    
    async def synchronize(
        self,
        agi_delta: Dict[str, float],
        asi_omega: Dict[str, float],
        optimize: bool = True
    ) -> NineFoldBundle:
        """
        Synchronize AGI and ASI through the 9-paradox matrix.
        
        Args:
            agi_delta: AGI metrics (F2_truth, F4_clarity, etc.)
            asi_omega: ASI metrics (kappa_r, peace_squared, etc.)
            optimize: Whether to iteratively optimize toward equilibrium
        """
        # Calculate initial paradox scores
        for key, paradox in self.paradoxes.items():
            agi_key = self._map_to_agi(paradox.agi_force)
            asi_key = self._map_to_asi(paradox.asi_force)
            
            agi_val = agi_delta.get(agi_key, 0.5)
            asi_val = asi_omega.get(asi_key, 0.5)
            
            paradox.score = self._geometric_synthesis(agi_val, asi_val)
        
        # Optimize toward equilibrium if requested
        equilibrium_path = []
        if optimize:
            self.paradoxes, equilibrium_path = self.solver.optimize_toward_equilibrium(
                self.paradoxes, agi_delta, asi_omega
            )
        
        # Calculate equilibrium state
        equilibrium = self.solver.solve(self.paradoxes)
        
        # Calculate tier scores
        alpha_scores = [p.score for p in self.paradoxes.values() if p.tier == TrinityTier.ALPHA]
        beta_scores = [p.score for p in self.paradoxes.values() if p.tier == TrinityTier.BETA]
        gamma_scores = [p.score for p in self.paradoxes.values() if p.tier == TrinityTier.GAMMA]
        
        alpha_score = np.mean(alpha_scores)
        beta_score = np.mean(beta_scores)
        gamma_score = np.mean(gamma_scores)
        
        # Determine verdict
        verdict = self._determine_verdict(equilibrium, alpha_score, beta_score, gamma_score)
        
        # Constitutional alignment vector
        constitutional_vector = self._calculate_constitutional_alignment()
        
        # Generate reasoning
        reasoning = self._generate_reasoning(equilibrium, equilibrium_path)
        
        return NineFoldBundle(
            session_id=self.session_id,
            query_hash=hash(str(agi_delta) + str(asi_omega)) & 0xFFFFFFFF,
            paradoxes=self.paradoxes,
            equilibrium=equilibrium,
            final_verdict=verdict,
            alpha_score=alpha_score,
            beta_score=beta_score,
            gamma_score=gamma_score,
            constitutional_vector=constitutional_vector,
            synthesis_reasoning=reasoning,
            equilibrium_path=equilibrium_path
        )
    
    def _map_to_agi(self, agi_force: str) -> str:
        """Map AGI force description to metric key."""
        mapping = {
            "F2": "F2_truth",
            "F4": "F4_clarity",
            "F7": "F7_humility",
            "Kalman": "kalman_gain",
            "5-Level": "hierarchy",
            "EFE": "agency",
            "Active Inference": "urgency",
            "Precision-Weighted": "certainty",
            "Convergent": "unity"
        }
        for key, val in mapping.items():
            if key in agi_force:
                return val
        return "default"
    
    def _map_to_asi(self, asi_force: str) -> str:
        """Map ASI force description to metric key."""
        mapping = {
            "kappa": "kappa_r",
            "Peace": "peace_squared",
            "Justice": "justice",
            "Reversibility": "reversibility",
            "Consent": "consent",
            "Weakest": "protection",
            "Intergenerational": "sustainability",
            "Epistemic": "doubt",
            "Stakeholder Plurality": "diversity"
        }
        for key, val in mapping.items():
            if key in asi_force:
                return val
        return "default"
    
    def _geometric_synthesis(self, a: float, b: float) -> float:
        """Geometric mean synthesis."""
        return math.sqrt(max(0.001, a) * max(0.001, b))
    
    def _determine_verdict(
        self,
        eq: EquilibriumState,
        alpha: float,
        beta: float,
        gamma: float
    ) -> str:
        """Determine final verdict based on equilibrium state."""
        if eq.is_equilibrium:
            return "EQUILIBRIUM"
        
        if eq.trinity_score >= 0.85 and all([alpha >= 0.8, beta >= 0.8, gamma >= 0.75]):
            return "SEAL"
        
        if eq.min_score < 0.5:
            return "VOID"
        
        if eq.std_deviation > 0.2:
            return "SABAR"  # Unbalanced
        
        return "888_HOLD"
    
    def _calculate_constitutional_alignment(self) -> Dict[str, float]:
        """Calculate alignment with each constitutional floor."""
        alignment = {}
        
        # Map paradoxes to floors
        floor_mappings = {
            "F1": ["precision_reversibility"],
            "F2": ["truth_care"],
            "F4": ["clarity_peace"],
            "F5": ["agency_protection"],
            "F6": ["clarity_peace", "unity_diversity"],
            "F7": ["humility_justice", "certainty_doubt"],
            "F9": ["unity_diversity"],
            "F11": ["hierarchy_consent"]
        }
        
        for floor, paradox_keys in floor_mappings.items():
            scores = [self.paradoxes[k].score for k in paradox_keys if k in self.paradoxes]
            alignment[floor] = np.mean(scores) if scores else 0.5
        
        return alignment
    
    def _generate_reasoning(self, eq: EquilibriumState, path: List[Dict]) -> str:
        """Generate human-readable synthesis reasoning."""
        parts = []
        
        # Equilibrium status
        if eq.is_equilibrium:
            parts.append(f"✓ EQUILIBRIUM ACHIEVED (score: {eq.trinity_score:.3f})")
        else:
            parts.append(f"✗ Not in equilibrium (score: {eq.trinity_score:.3f}, need ≥{EQUILIBRIUM_THRESHOLD})")
        
        # Balance metrics
        parts.append(f"Balance: σ={eq.std_deviation:.3f} (tolerance ≤{BALANCE_TOLERANCE})")
        parts.append(f"Range: [{eq.min_score:.3f}, {eq.max_score:.3f}]")
        
        # Optimization path
        if path:
            parts.append(f"Convergence: {len(path)} iterations")
            parts.append(f"Final Δ: {eq.convergence_delta:.4f}")
        
        # Weakest link
        weakest = min(eq.paradoxes.items(), key=lambda x: x[1].score)
        parts.append(f"Weakest paradox: {weakest[0]} ({weakest[1].score:.3f})")
        
        return " | ".join(parts)


# ============ CONVENIENCE FUNCTIONS ============

async def trinity_nine_sync(
    agi_delta: Dict[str, float],
    asi_omega: Dict[str, float],
    session_id: Optional[str] = None,
    optimize: bool = True
) -> NineFoldBundle:
    """Convenience function for 9-paradox Trinity sync."""
    trinity = TrinityNine(session_id)
    return await trinity.synchronize(agi_delta, asi_omega, optimize)


def check_equilibrium(paradox_scores: List[float]) -> EquilibriumState:
    """Check if a set of 9 scores represents equilibrium."""
    solver = EquilibriumSolver()
    paradoxes = create_nine_paradoxes()
    for (key, p), score in zip(paradoxes.items(), paradox_scores):
        p.score = score
    return solver.solve(paradoxes)


__all__ = [
    "TrinityNine",
    "NineFoldBundle",
    "NineParadox",
    "EquilibriumState",
    "EquilibriumSolver",
    "TrinityTier",
    "create_nine_paradoxes",
    "trinity_nine_sync",
    "check_equilibrium"
]
