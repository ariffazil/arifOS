"""
ASI ENGINE v53.4.0 - HARDENED

Unified Heart Engine with 3-Trinity Architecture:
- Trinity I (Self): Empathy Flow (κᵣ), Bias Mirror, Reversibility (F1)
- Trinity II (System): Power-Care (Peace²), Accountability Loop, Consent (F11)
- Trinity III (Society): Stakeholder Protection, Thermodynamic Justice (ΔS≥0), Ecology

Fractal Geometry: Self-similar stakeholder recursion
Ω = κᵣ · Peace² · Justice

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio
import math
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable


# ============ CONSTANTS ============

MAX_QUERY_LENGTH = 10000
HUMILITY_BAND = (0.03, 0.05)  # F7
MIN_KAPPA_R = 0.7  # Minimum empathy flow
MIN_PEACE_SQ = 0.6  # Minimum Peace²


class EngineVote(Enum):
    SEAL = "SEAL"
    VOID = "VOID"
    SABAR = "SABAR"


class StakeholderType(Enum):
    HUMAN_DIRECT = "human_direct"
    HUMAN_INDIRECT = "human_indirect"
    ECOLOGICAL = "ecological"
    SYSTEM = "system"
    FUTURE = "future"


# ============ DATA CLASSES ============

@dataclass
class Stakeholder:
    """A stakeholder in the ethical analysis."""
    id: str
    type: StakeholderType
    vulnerability: float  # 0-1, higher = more vulnerable
    power: float         # 0-1, higher = more power
    description: str
    
    @property
    def protection_priority(self) -> float:
        """F5: Prioritize weakest stakeholders."""
        return self.vulnerability / (self.power + 0.01)


@dataclass
class EmpathyFlow:
    """
    Trinity I: Empathy Flow (κᵣ)
    Measures capacity to feel with stakeholders.
    """
    kappa_r: float  # Empathy coefficient
    stakeholders: List[Stakeholder]
    bias_reflection: Dict[str, float]  # Detected biases
    reversibility_score: float  # F1
    
    def get_weakest(self) -> Optional[Stakeholder]:
        """Return most vulnerable stakeholder (F5)."""
        if not self.stakeholders:
            return None
        return max(self.stakeholders, key=lambda s: s.protection_priority)


@dataclass
class SystemIntegrity:
    """
    Trinity II: System-level ethics.
    """
    peace_squared: float  # Peace² (F6)
    accountability_paths: List[str]  # Traceable responsibility chains
    consent_verified: bool  # F11
    power_care_balance: float  # Power used for care


@dataclass
class SocietalImpact:
    """
    Trinity III: Society-level ethics.
    """
    stakeholder_matrix: Dict[str, Dict[str, float]]  # Impact matrix
    thermodynamic_justice: float  # ΔS impact on society
    ecological_equilibrium: float  # Non-human impact
    future_generations: float  # Long-term impact


@dataclass
class OmegaBundle:
    """
    ASI Output Bundle (Ω)
    Contains all 3 Trinity evaluations.
    """
    session_id: str
    query_hash: str
    
    # Trinity components
    empathy: EmpathyFlow
    system: SystemIntegrity
    society: SocietalImpact
    
    # Composite score
    omega_total: float  # κᵣ · Peace² · Justice
    
    # Verdict
    vote: EngineVote
    
    # Floor compliance
    floor_scores: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        weakest = self.empathy.get_weakest()
        return {
            "session_id": self.session_id,
            "omega_total": self.omega_total,
            "empathy_kappa_r": self.empathy.kappa_r,
            "peace_squared": self.system.peace_squared,
            "weakest_stakeholder": weakest.id if weakest else None,
            "reversibility": self.empathy.reversibility_score,
            "consent": self.system.consent_verified,
            "vote": self.vote.value,
            "trinity_balance": {
                "self": self.empathy.kappa_r,
                "system": self.system.peace_squared,
                "society": self.society.thermodynamic_justice
            }
        }


# ============ TRINITY COMPONENTS ============

class TrinitySelf:
    """Trinity I: Self/Empathy (κᵣ)"""
    
    def evaluate(self, query: str, context: Optional[Dict] = None) -> EmpathyFlow:
        """Evaluate empathy flow with stakeholders."""
        # Identify stakeholders
        stakeholders = self._identify_stakeholders(query, context)
        
        # Compute κᵣ (empathy coefficient)
        kappa_r = self._compute_kappa_r(stakeholders, query)
        
        # Bias reflection
        biases = self._detect_biases(query)
        
        # Reversibility check (F1)
        reversibility = self._check_reversibility(query, context)
        
        return EmpathyFlow(
            kappa_r=kappa_r,
            stakeholders=stakeholders,
            bias_reflection=biases,
            reversibility_score=reversibility
        )
    
    def _identify_stakeholders(self, query: str, context: Optional[Dict]) -> List[Stakeholder]:
        """Identify all stakeholders affected by query."""
        stakeholders = []
        query_lower = query.lower()
        
        # Direct human stakeholders
        if any(w in query_lower for w in ["user", "human", "person", "people"]):
            stakeholders.append(Stakeholder(
                id="direct_human",
                type=StakeholderType.HUMAN_DIRECT,
                vulnerability=0.5,
                power=0.5,
                description="Direct human user"
            ))
        
        # Indirect humans
        if any(w in query_lower for w in ["society", "public", "community"]):
            stakeholders.append(Stakeholder(
                id="indirect_human",
                type=StakeholderType.HUMAN_INDIRECT,
                vulnerability=0.7,
                power=0.3,
                description="Indirectly affected humans"
            ))
        
        # Future generations
        if any(w in query_lower for w in ["future", "generation", "long-term"]):
            stakeholders.append(Stakeholder(
                id="future_gen",
                type=StakeholderType.FUTURE,
                vulnerability=0.9,
                power=0.1,
                description="Future generations"
            ))
        
        # Ecological
        if any(w in query_lower for w in ["environment", "ecology", "nature", "climate"]):
            stakeholders.append(Stakeholder(
                id="ecology",
                type=StakeholderType.ECOLOGICAL,
                vulnerability=0.8,
                power=0.0,
                description="Non-human ecological systems"
            ))
        
        # Default if none identified
        if not stakeholders:
            stakeholders.append(Stakeholder(
                id="default_user",
                type=StakeholderType.HUMAN_DIRECT,
                vulnerability=0.5,
                power=0.5,
                description="Default user stakeholder"
            ))
        
        return stakeholders
    
    def _compute_kappa_r(self, stakeholders: List[Stakeholder], query: str) -> float:
        """
        Compute empathy coefficient κᵣ.
        
        κᵣ = Σ(vulnerability_i × care_i) / Σ(vulnerability_i)
        """
        total_vulnerability = sum(s.vulnerability for s in stakeholders)
        if total_vulnerability == 0:
            return 0.5
        
        # Care is inversely proportional to power distance
        care_sum = sum(s.vulnerability * (1 - s.power) for s in stakeholders)
        
        return min(1.0, care_sum / total_vulnerability)
    
    def _detect_biases(self, query: str) -> Dict[str, float]:
        """Detect potential biases in query."""
        query_lower = query.lower()
        biases = {}
        
        # Anthropocentric bias
        if any(w in query_lower for w in ["human", "people", "person"]):
            if not any(w in query_lower for w in ["animal", "ecology", "environment"]):
                biases["anthropocentric"] = 0.7
        
        # Present bias (ignoring future)
        if any(w in query_lower for w in ["now", "immediate", "quick"]):
            if not any(w in query_lower for w in ["future", "long-term", "sustainable"]):
                biases["present"] = 0.6
        
        # Power bias
        if any(w in query_lower for w in ["control", "manage", "optimize"]):
            biases["control"] = 0.5
        
        return biases
    
    def _check_reversibility(self, query: str, context: Optional[Dict]) -> float:
        """
        F1: Check if action is reversible.
        Returns reversibility score (0-1).
        """
        query_lower = query.lower()
        
        # Irreversible keywords
        irreversible = ["delete", "destroy", "kill", "permanent", "final"]
        if any(w in query_lower for w in irreversible):
            return 0.0
        
        # Reversible indicators
        reversible = ["draft", "test", "temporary", "reversible", "undo"]
        if any(w in query_lower for w in reversible):
            return 1.0
        
        # Default: assume partially reversible
        return 0.7


class TrinitySystem:
    """Trinity II: System/Ethics (Peace²)"""
    
    def evaluate(self, query: str, empathy: EmpathyFlow, context: Optional[Dict] = None) -> SystemIntegrity:
        """Evaluate system-level ethical integrity."""
        # Compute Peace² (F6)
        peace_sq = self._compute_peace_squared(query, empathy)
        
        # Accountability paths
        accountability = self._trace_accountability(query, context)
        
        # Consent verification (F11)
        consent = self._verify_consent(query, empathy.stakeholders)
        
        # Power-Care balance
        power_care = self._balance_power_care(empathy)
        
        return SystemIntegrity(
            peace_squared=peace_sq,
            accountability_paths=accountability,
            consent_verified=consent,
            power_care_balance=power_care
        )
    
    def _compute_peace_squared(self, query: str, empathy: EmpathyFlow) -> float:
        """
        F6: Peace² = (Internal Peace) × (External Peace)
        
        Internal: absence of cognitive dissonance
        External: harmony with stakeholder needs
        """
        # Internal peace (consistency check)
        has_conflict = any(b > 0.6 for b in empathy.bias_reflection.values())
        internal = 0.5 if has_conflict else 0.9
        
        # External peace (stakeholder harmony)
        if empathy.stakeholders:
            vulnerabilities = [s.vulnerability for s in empathy.stakeholders]
            variance = sum((v - sum(vulnerabilities)/len(vulnerabilities))**2 for v in vulnerabilities) / len(vulnerabilities)
            external = 1.0 - min(1.0, variance * 2)
        else:
            external = 0.5
        
        return internal * external
    
    def _trace_accountability(self, query: str, context: Optional[Dict]) -> List[str]:
        """Trace accountability paths."""
        paths = []
        
        # Check for clear responsibility chain
        if context and "responsible_party" in context:
            paths.append(f"primary:{context['responsible_party']}")
        else:
            paths.append("primary:system")
        
        # Audit trail
        paths.append("audit:logged")
        
        return paths
    
    def _verify_consent(self, query: str, stakeholders: List[Stakeholder]) -> bool:
        """
        F11: Verify meaningful consent from stakeholders.
        """
        query_lower = query.lower()
        
        # Explicit consent indicators
        if "consent" in query_lower or "agree" in query_lower:
            return True
        
        # Check for vulnerable stakeholders without explicit consent
        vulnerable = any(s.vulnerability > 0.7 for s in stakeholders)
        if vulnerable and "consent" not in query_lower:
            return False
        
        return True  # Assume consent by default for low-risk
    
    def _balance_power_care(self, empathy: EmpathyFlow) -> float:
        """Measure if power is being used for care."""
        if not empathy.stakeholders:
            return 0.5
        
        # Power should be proportional to care for weakest
        weakest = empathy.get_weakest()
        if weakest:
            return 1.0 - abs(weakest.power - (1 - weakest.vulnerability))
        return 0.5


class TrinitySociety:
    """Trinity III: Society/Justice (Ω)"""
    
    def evaluate(self, query: str, empathy: EmpathyFlow, system: SystemIntegrity, context: Optional[Dict] = None) -> SocietalImpact:
        """Evaluate societal-level impact."""
        # Impact matrix
        matrix = self._compute_impact_matrix(empathy.stakeholders)
        
        # Thermodynamic justice (ΔS impact)
        justice = self._compute_thermodynamic_justice(query, empathy, system)
        
        # Ecological equilibrium
        ecology = self._assess_ecology(query)
        
        # Future generations impact
        future = self._assess_future_impact(query, empathy)
        
        return SocietalImpact(
            stakeholder_matrix=matrix,
            thermodynamic_justice=justice,
            ecological_equilibrium=ecology,
            future_generations=future
        )
    
    def _compute_impact_matrix(self, stakeholders: List[Stakeholder]) -> Dict[str, Dict[str, float]]:
        """Compute pairwise impact between stakeholders."""
        matrix = {}
        for s1 in stakeholders:
            matrix[s1.id] = {}
            for s2 in stakeholders:
                # Impact is asymmetric (power → vulnerability)
                impact = s1.power * s2.vulnerability * 0.5
                matrix[s1.id][s2.id] = impact
        return matrix
    
    def _compute_thermodynamic_justice(self, query: str, empathy: EmpathyFlow, system: SystemIntegrity) -> float:
        """
        Justice = distribution of entropy reduction.
        Fair distribution → high justice
        """
        # Check if benefits are distributed to vulnerable
        weakest = empathy.get_weakest()
        if weakest and weakest.vulnerability > 0.7:
            # High vulnerability + proper care = justice
            if empathy.kappa_r > 0.8:
                return 0.9
            else:
                return 0.5  # Insufficient care for vulnerable
        
        return 0.8  # Default: reasonably just
    
    def _assess_ecology(self, query: str) -> float:
        """Assess impact on ecological systems."""
        query_lower = query.lower()
        
        # Positive ecological indicators
        positive = ["sustainable", "renewable", "conserve", "protect"]
        if any(w in query_lower for w in positive):
            return 0.9
        
        # Negative indicators
        negative = ["extract", "exploit", "consume", "waste"]
        if any(w in query_lower for w in negative):
            return 0.3
        
        return 0.6  # Neutral
    
    def _assess_future_impact(self, query: str, empathy: EmpathyFlow) -> float:
        """Assess long-term impact on future generations."""
        query_lower = query.lower()
        
        # Future-positive
        future_indicators = ["future", "sustainable", "legacy", "inherit"]
        if any(w in query_lower for w in future_indicators):
            return 0.9
        
        # Check for future stakeholders
        future_stakeholders = [s for s in empathy.stakeholders if s.type == StakeholderType.FUTURE]
        if future_stakeholders:
            return 0.85
        
        return 0.6  # Neutral


# ============ MAIN ENGINE ============

class ASIEngineHardened:
    """
    Hardened ASI Engine v53.4.0
    
    3-Trinity architecture with fractal stakeholder geometry.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or f"asi_{uuid.uuid4().hex[:12]}"
        
        # Trinity components
        self.trinity_self = TrinitySelf()
        self.trinity_system = TrinitySystem()
        self.trinity_society = TrinitySociety()
    
    async def execute(self, query: str, context: Optional[Dict] = None) -> OmegaBundle:
        """
        Main execution: 555 EMPATHY → 666 ALIGN → Ω
        """
        # 555 EMPATHY: Trinity I
        empathy = self.trinity_self.evaluate(query, context)
        
        # 666 ALIGN: Trinity II
        system = self.trinity_system.evaluate(query, empathy, context)
        
        # Trinity III
        society = self.trinity_society.evaluate(query, empathy, system, context)
        
        # Compute Ω = κᵣ · Peace² · Justice
        omega_total = empathy.kappa_r * system.peace_squared * society.thermodynamic_justice
        
        # Determine vote
        vote = self._determine_vote(empathy, system, society, omega_total)
        
        # Floor scores
        floor_scores = {
            "F1_reversibility": empathy.reversibility_score,
            "F5_weakest": empathy.get_weakest().protection_priority if empathy.get_weakest() else 0.5,
            "F6_peace_sq": system.peace_squared,
            "F11_consent": 1.0 if system.consent_verified else 0.0,
            "omega_total": omega_total
        }
        
        return OmegaBundle(
            session_id=self.session_id,
            query_hash=self._hash(query),
            empathy=empathy,
            system=system,
            society=society,
            omega_total=omega_total,
            vote=vote,
            floor_scores=floor_scores,
            reasoning=f"κᵣ={empathy.kappa_r:.2f}, Peace²={system.peace_squared:.2f}, Justice={society.thermodynamic_justice:.2f}"
        )
    
    def _determine_vote(self, empathy: EmpathyFlow, system: SystemIntegrity, society: SocietalImpact, omega: float) -> EngineVote:
        """Determine final vote based on Trinity evaluation."""
        # F1: Must be reversible
        if empathy.reversibility_score < 0.3:
            return EngineVote.VOID
        
        # F5: Must protect weakest
        weakest = empathy.get_weakest()
        if weakest and weakest.vulnerability > 0.8 and empathy.kappa_r < MIN_KAPPA_R:
            return EngineVote.SABAR
        
        # F6: Peace² threshold
        if system.peace_squared < MIN_PEACE_SQ:
            return EngineVote.SABAR
        
        # F11: Consent required
        if not system.consent_verified:
            return EngineVote.SABAR
        
        # Omega threshold
        if omega < 0.5:
            return EngineVote.VOID
        
        return EngineVote.SEAL
    
    def _hash(self, query: str) -> str:
        """Generate query hash."""
        import hashlib
        return hashlib.sha256(query.encode()).hexdigest()[:16]


# ============ CONVENIENCE ============

async def execute_asi_hardened(query: str, session_id: Optional[str] = None) -> OmegaBundle:
    """Convenience function to execute hardened ASI."""
    engine = ASIEngineHardened(session_id)
    return await engine.execute(query)


__all__ = [
    "ASIEngineHardened",
    "OmegaBundle",
    "EmpathyFlow",
    "SystemIntegrity",
    "SocietalImpact",
    "Stakeholder",
    "TrinitySelf",
    "TrinitySystem",
    "TrinitySociety",
    "execute_asi_hardened"
]
