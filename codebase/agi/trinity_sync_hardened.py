"""
TRINITY SYNC v53.4.0 - HARDENED

333 FORGE: Convergence point where AGI (Δ) + ASI (Ω) merge.

Geometry:
- AGI: Orthogonal (parallel independent paths)
- ASI: Fractal (self-similar stakeholder recursion)
- Trinity Sync: Toroidal (looping closure)

6-Paradox Synthesis:
1. Truth (Δ) ↔ Care (Ω) → Compassionate Truth
2. Clarity (Δ) ↔ Peace (Ω) → Clear Peace
3. Humility (Δ) ↔ Justice (Ω) → Humble Justice

Formula: Trinity = geometric_mean(paradox₁, paradox₂, paradox₃)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Import hardened engines
from .engine_hardened import AGIEngineHardened, DeltaBundle, execute_agi_hardened
from ..asi.engine_hardened import ASIEngineHardened, OmegaBundle, execute_asi_hardened


# ============ CONSTANTS ============

TRINITY_THRESHOLD = 0.85  # Minimum for SEAL
GEOMETRIC_SYNTHESIS = True  # Use geometric mean (not arithmetic)


# ============ DATA CLASSES ============

@dataclass
class ParadoxScore:
    """
    A synthesized paradox score.
    
    Each paradox combines one AGI virtue with one ASI virtue.
    """
    name: str
    agi_component: str
    asi_component: str
    synthesis: str
    score: float  # 0-1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "agi": self.agi_component,
            "asi": self.asi_component,
            "synthesis": self.synthesis,
            "score": round(self.score, 4)
        }


@dataclass
class TrinityBundle:
    """
    Final Trinity output after AGI + ASI convergence.
    """
    session_id: str
    query_hash: str
    
    # Individual votes
    agi_vote: str
    asi_vote: str
    
    # 6-Paradox synthesis
    paradoxes: Dict[str, ParadoxScore]
    
    # Final metrics
    trinity_score: float  # Geometric mean of paradoxes
    final_verdict: str    # SEAL, VOID, or SABAR
    
    # Component bundles (for inspection)
    delta_bundle: Optional[Dict[str, Any]] = None
    omega_bundle: Optional[Dict[str, Any]] = None
    
    # Reasoning
    synthesis_reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "trinity_score": round(self.trinity_score, 4),
            "final_verdict": self.final_verdict,
            "agi_vote": self.agi_vote,
            "asi_vote": self.asi_vote,
            "paradoxes": {k: v.to_dict() for k, v in self.paradoxes.items()},
            "synthesis": self.synthesis_reasoning,
            "timestamp": self.timestamp.isoformat()
        }


# ============ PARADOX SYNTHESIS ============

def synthesize_paradox(agi_value: float, asi_value: float, method: str = "geometric") -> float:
    """
    Synthesize AGI and ASI values into paradox score.
    
    Methods:
    - geometric: √(AGI × ASI)  [default, preserves multiplicative nature]
    - harmonic: 2/(1/AGI + 1/ASI)  [punishes imbalance]
    - arithmetic: (AGI + ASI)/2  [lenient]
    """
    # Clamp values
    agi = max(0.0, min(1.0, agi_value))
    asi = max(0.0, min(1.0, asi_value))
    
    if method == "geometric":
        return math.sqrt(agi * asi)
    elif method == "harmonic":
        if agi == 0 or asi == 0:
            return 0.0
        return 2 * agi * asi / (agi + asi)
    else:  # arithmetic
        return (agi + asi) / 2


def compute_trinity_score(paradox_scores: List[float], method: str = "geometric") -> float:
    """
    Compute overall Trinity score from paradox scores.
    """
    if not paradox_scores:
        return 0.0
    
    if method == "geometric":
        # Geometric mean
        product = 1.0
        for score in paradox_scores:
            product *= max(0.001, score)  # Avoid zero
        return product ** (1.0 / len(paradox_scores))
    else:
        return sum(paradox_scores) / len(paradox_scores)


# ============ MAIN SYNTHESIS ============

class TrinitySyncHardened:
    """
    Hardened Trinity Sync for AGI + ASI convergence.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"trinity_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        self.agi_engine = AGIEngineHardened(self.session_id)
        self.asi_engine = ASIEngineHardened(self.session_id)
    
    async def synchronize(self, query: str, context: Optional[Dict] = None) -> TrinityBundle:
        """
        Execute parallel AGI + ASI and synthesize at 333 FORGE.
        """
        # Parallel execution
        delta_task = asyncio.create_task(self.agi_engine.execute(query, context))
        omega_task = asyncio.create_task(self.asi_engine.execute(query, context))
        
        delta, omega = await asyncio.gather(delta_task, omega_task)
        
        # 333 FORGE: 6-Paradox Synthesis
        paradoxes = self._synthesize_paradoxes(delta, omega)
        
        # Compute Trinity score
        paradox_scores = [p.score for p in paradoxes.values()]
        trinity_score = compute_trinity_score(paradox_scores, method="geometric")
        
        # Determine final verdict
        verdict = self._determine_verdict(delta, omega, trinity_score, paradoxes)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(delta, omega, paradoxes, trinity_score)
        
        return TrinityBundle(
            session_id=self.session_id,
            query_hash=delta.query_hash,
            agi_vote=delta.vote.value,
            asi_vote=omega.vote.value,
            paradoxes=paradoxes,
            trinity_score=trinity_score,
            final_verdict=verdict,
            delta_bundle=delta.to_dict(),
            omega_bundle=omega.to_dict(),
            synthesis_reasoning=reasoning
        )
    
    def _synthesize_paradoxes(self, delta: DeltaBundle, omega: OmegaBundle) -> Dict[str, ParadoxScore]:
        """
        Synthesize 6 paradoxes (3 pairs of AGI↔ASI virtues).
        """
        paradoxes = {}
        
        # Paradox 1: Truth (AGI F2) ↔ Care (ASI κᵣ)
        truth_care = synthesize_paradox(
            delta.floor_scores.get("F2_truth", 0.5),
            omega.empathy.kappa_r,
            method="geometric"
        )
        paradoxes["truth_care"] = ParadoxScore(
            name="Truth ↔ Care",
            agi_component="F2 Truth",
            asi_component="Empathy (κᵣ)",
            synthesis="Compassionate Truth",
            score=truth_care
        )
        
        # Paradox 2: Clarity (AGI F4) ↔ Peace (ASI Peace²)
        clarity_peace = synthesize_paradox(
            delta.floor_scores.get("F4_clarity", 0.5),
            omega.system.peace_squared,
            method="geometric"
        )
        paradoxes["clarity_peace"] = ParadoxScore(
            name="Clarity ↔ Peace",
            agi_component="F4 Clarity (ΔS≤0)",
            asi_component="Peace²",
            synthesis="Clear Peace",
            score=clarity_peace
        )
        
        # Paradox 3: Humility (AGI F7) ↔ Justice (ASI Thermodynamic)
        humility_justice = synthesize_paradox(
            delta.floor_scores.get("F7_humility", 0.5),
            omega.society.thermodynamic_justice,
            method="geometric"
        )
        paradoxes["humility_justice"] = ParadoxScore(
            name="Humility ↔ Justice",
            agi_component="F7 Humility (Ω₀)",
            asi_component="Thermodynamic Justice",
            synthesis="Humble Justice",
            score=humility_justice
        )
        
        # Additional paradoxes for completeness
        
        # Paradox 4: Precision (AGI) ↔ Reversibility (ASI F1)
        precision_reversibility = synthesize_paradox(
            delta.precision.kalman_gain,
            omega.empathy.reversibility_score,
            method="geometric"
        )
        paradoxes["precision_reversibility"] = ParadoxScore(
            name="Precision ↔ Reversibility",
            agi_component="Kalman Gain (π)",
            asi_component="F1 Reversibility",
            synthesis="Careful Action",
            score=precision_reversibility
        )
        
        # Paradox 5: Hierarchy (AGI) ↔ Consent (ASI F11)
        hierarchy_consent = synthesize_paradox(
            abs(delta.cumulative_delta_s) if delta.cumulative_delta_s < 0 else 0.0,
            1.0 if omega.system.consent_verified else 0.0,
            method="geometric"
        )
        paradoxes["hierarchy_consent"] = ParadoxScore(
            name="Hierarchy ↔ Consent",
            agi_component="Hierarchical Clarity",
            asi_component="F11 Consent",
            synthesis="Structured Freedom",
            score=hierarchy_consent
        )
        
        # Paradox 6: Action (AGI EFE) ↔ Stakeholder (ASI weakest)
        action_stakeholder = synthesize_paradox(
            1.0 - (delta.action_policy.expected_free_energy if delta.action_policy else 1.0),
            omega.empathy.get_weakest().protection_priority / 10 if omega.empathy.get_weakest() else 0.0,
            method="geometric"
        )
        paradoxes["action_stakeholder"] = ParadoxScore(
            name="Action ↔ Stakeholder",
            agi_component="EFE Minimization",
            asi_component="Weakest Protection",
            synthesis="Protective Agency",
            score=action_stakeholder
        )
        
        return paradoxes
    
    def _determine_verdict(self, delta: DeltaBundle, omega: OmegaBundle, trinity_score: float, paradoxes: Dict[str, ParadoxScore]) -> str:
        """
        Determine final verdict based on all inputs.
        """
        # Both must agree for SEAL
        if delta.vote.value == "SEAL" and omega.vote.value == "SEAL":
            if trinity_score >= TRINITY_THRESHOLD:
                return "SEAL"
            else:
                return "SABAR"  # Close but not quite
        
        # Both VOID → VOID
        if delta.vote.value == "VOID" and omega.vote.value == "VOID":
            return "VOID"
        
        # Either SABAR → SABAR
        if delta.vote.value == "SABAR" or omega.vote.value == "SABAR":
            return "SABAR"
        
        # Disagreement → SABAR for review
        if delta.vote.value != omega.vote.value:
            return "SABAR"
        
        return "VOID"
    
    def _generate_reasoning(self, delta: DeltaBundle, omega: OmegaBundle, paradoxes: Dict[str, ParadoxScore], trinity_score: float) -> str:
        """Generate human-readable synthesis reasoning."""
        parts = []
        
        # Trinity score summary
        parts.append(f"Trinity Score: {trinity_score:.3f} (threshold: {TRINITY_THRESHOLD})")
        
        # Paradox highlights
        best_paradox = max(paradoxes.items(), key=lambda x: x[1].score)
        worst_paradox = min(paradoxes.items(), key=lambda x: x[1].score)
        
        parts.append(f"Strongest synthesis: {best_paradox[1].name} = {best_paradox[1].score:.3f}")
        parts.append(f"Weakest synthesis: {worst_paradox[1].name} = {worst_paradox[1].score:.3f}")
        
        # Component summaries
        parts.append(f"AGI: ΔS={delta.entropy_delta:.3f}, Ω₀={delta.omega_0:.3f}, π={delta.precision.pi_likelihood:.2f}")
        parts.append(f"ASI: κᵣ={omega.empathy.kappa_r:.2f}, Peace²={omega.system.peace_squared:.2f}, Ω={omega.omega_total:.3f}")
        
        return " | ".join(parts)


# ============ CONVENIENCE ============

async def trinity_sync_hardened(query: str, session_id: Optional[str] = None) -> TrinityBundle:
    """Convenience function for hardened Trinity sync."""
    sync = TrinitySyncHardened(session_id)
    return await sync.synchronize(query)


__all__ = [
    "TrinitySyncHardened",
    "TrinityBundle",
    "ParadoxScore",
    "synthesize_paradox",
    "compute_trinity_score",
    "trinity_sync_hardened"
]
