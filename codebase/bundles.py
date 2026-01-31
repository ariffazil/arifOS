"""
CANONICAL BUNDLE SCHEMAS - ARIF Loop v53.4.0

Defines the thermodynamically-isolated data contracts between engines:
- DELTA_BUNDLE: AGI output (Mind/Reflect) — now with precision, hierarchy, action
- OMEGA_BUNDLE: ASI output (Heart/Refract)
- MERGED_BUNDLE: APEX sync point (444)

The "thermodynamic wall" between bundles ensures F3 Tri-Witness honesty:
AGI and ASI cannot see each other's reasoning until 444 TRINITY_SYNC.

v53.4.0 additions:
- Precision weighting (π = 1/σ², Kalman gain)
- Hierarchical encoding (5-level cortical hierarchy)
- Active inference (EFE minimization for action selection)

DITEMPA BUKAN DIBERI - Forged, Not Given
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib


# =============================================================================
# VOTE TYPES
# =============================================================================


class EngineVote(str, Enum):
    """Independent engine vote before 444 sync."""

    SEAL = "SEAL"  # Approve - all my floors pass
    VOID = "VOID"  # Reject - hard floor violation
    UNCERTAIN = "UNCERTAIN"  # Within Omega_0 band, needs sync


# =============================================================================
# DELTA BUNDLE (AGI OUTPUT - MIND/REFLECT)
# =============================================================================


@dataclass
class Hypothesis:
    """One of three reasoning paths from 222 THINK."""

    path_type: str  # "conservative", "exploratory", "adversarial"
    content: str
    confidence: float  # 0.0 to 1.0
    supporting_facts: List[str] = field(default_factory=list)


@dataclass
class ReasoningTree:
    """Structured reasoning output from 333 REASON."""

    premises: List[str]
    inference_steps: List[str]
    conclusion: str
    contradictions_detected: List[str] = field(default_factory=list)
    is_valid: bool = True


@dataclass
class AGIFloorScores:
    """Floor scores computed by AGI (F2, F4, F7, F13)."""

    F2_truth: float = 0.0  # Truth score (>= 0.99 required)
    F4_clarity: float = 0.0  # Clarity delta_S (<= 0 required)
    F7_humility: float = 0.04  # Humility Omega_0 (in [0.03, 0.05])
    F13_curiosity: float = 0.0  # Curiosity (>= 3 paths explored)

    def all_hard_pass(self) -> bool:
        """Check if all hard floors pass."""
        return self.F2_truth >= 0.99 and self.F4_clarity <= 0 and 0.03 <= self.F7_humility <= 0.05

    def to_dict(self) -> Dict[str, float]:
        return {
            "F2_truth": self.F2_truth,
            "F4_clarity": self.F4_clarity,
            "F7_humility": self.F7_humility,
            "F13_curiosity": self.F13_curiosity,
        }


@dataclass
class DeltaBundle:
    """
    DELTA_BUNDLE: AGI (Mind) output from stages 111-222-333.

    This is the isolated output from the "Reflect" phase.
    ASI CANNOT see this until 444 TRINITY_SYNC merges it.

    Contains:
    - Parsed facts from 111 SENSE
    - Three hypotheses from 222 THINK
    - Reasoning tree from 333 REASON
    - AGI's independent vote (SEAL/VOID)
    - Confidence interval with Omega_0 uncertainty
    - Floor scores for F2, F4, F7, F13
    - Entropy delta (thermodynamic measure)
    - Dashboard metrics (real-time constitutional tracking)
    """

    # Session metadata
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # 111 SENSE output
    raw_query: str = ""
    parsed_facts: List[str] = field(default_factory=list)
    detected_intent: str = ""

    # 222 THINK output (3 paths)
    hypotheses: List[Hypothesis] = field(default_factory=list)

    # 333 REASON output
    reasoning: Optional[ReasoningTree] = None

    # Confidence with uncertainty band
    confidence_low: float = 0.94  # 1 - Omega_0_max
    confidence_high: float = 0.97  # 1 - Omega_0_min
    omega_0: float = 0.04  # Humility (within [0.03, 0.05])

    # Thermodynamics
    entropy_delta: float = 0.0  # Delta_S (should be <= 0 for cooling)

    # Floor scores (AGI owns F2, F4, F7, F13)
    floor_scores: AGIFloorScores = field(default_factory=AGIFloorScores)

    # Independent vote (before seeing ASI)
    vote: EngineVote = EngineVote.UNCERTAIN
    vote_reason: str = ""

    # Real-time dashboard metrics (v52.6.0)
    dashboard: Optional[Dict[str, Any]] = None  # Thermodynamic tracking

    # v53.4.0: Precision weighting (Gap P1)
    precision_pi: float = 0.0  # π = 1/σ² (likelihood precision)
    precision_prior: float = 0.0  # π_P (prior precision)
    kalman_gain: float = 0.0  # K = π_L / (π_P + π_L)

    # v53.4.0: Hierarchical encoding (Gap P2)
    hierarchy_levels: Optional[Dict[str, Any]] = None  # 5-level encoding results
    cumulative_delta_s: float = 0.0  # Cumulative ΔS across hierarchy levels

    # v53.4.0: Active inference (Gap P3)
    free_energy: float = 0.0  # F = ΔS + Ω₀·π⁻¹
    action_type: str = ""  # Selected action (SEAL/VOID/SABAR/INVESTIGATE/AMPLIFY/DEFER)
    epistemic_value: float = 0.0  # Information gain from action
    pragmatic_value: float = 0.0  # Goal achievement from action

    # Integrity
    bundle_hash: str = ""

    def compute_hash(self) -> str:
        """Compute integrity hash for this bundle."""
        content = f"{self.session_id}|{self.raw_query}|{self.vote}|{self.confidence_high}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def seal(self) -> "DeltaBundle":
        """Seal the bundle (compute hash, mark complete)."""
        self.bundle_hash = self.compute_hash()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "raw_query": self.raw_query,
            "parsed_facts": self.parsed_facts,
            "detected_intent": self.detected_intent,
            "hypotheses": [
                {
                    "path_type": h.path_type,
                    "content": h.content,
                    "confidence": h.confidence,
                    "supporting_facts": h.supporting_facts,
                }
                for h in self.hypotheses
            ],
            "reasoning": {
                "premises": self.reasoning.premises if self.reasoning else [],
                "inference_steps": self.reasoning.inference_steps if self.reasoning else [],
                "conclusion": self.reasoning.conclusion if self.reasoning else "",
                "contradictions": self.reasoning.contradictions_detected if self.reasoning else [],
                "is_valid": self.reasoning.is_valid if self.reasoning else False,
            },
            "confidence": {
                "low": self.confidence_low,
                "high": self.confidence_high,
                "omega_0": self.omega_0,
            },
            "entropy_delta": self.entropy_delta,
            "floor_scores": self.floor_scores.to_dict(),
            "vote": self.vote.value,
            "vote_reason": self.vote_reason,
            "dashboard": self.dashboard,  # Thermodynamic metrics (v52.6.0)
            # v53.4.0: Precision, hierarchy, action
            "precision": {
                "pi_likelihood": self.precision_pi,
                "pi_prior": self.precision_prior,
                "kalman_gain": self.kalman_gain,
            },
            "hierarchy": self.hierarchy_levels,
            "cumulative_delta_s": self.cumulative_delta_s,
            "free_energy": self.free_energy,
            "action_type": self.action_type,
            "epistemic_value": self.epistemic_value,
            "pragmatic_value": self.pragmatic_value,
            "bundle_hash": self.bundle_hash,
        }


# =============================================================================
# OMEGA BUNDLE (ASI OUTPUT - HEART/REFRACT)
# =============================================================================


@dataclass
class Stakeholder:
    """A stakeholder identified by empathy analysis."""

    name: str
    role: str  # "user", "developer", "system", "earth", "vulnerable"
    vulnerability_score: float  # 0.0 to 1.0 (higher = more vulnerable)
    potential_harm: str = ""
    voice_weight: float = 1.0  # Representation in consensus


@dataclass
class ASIFloorScores:
    """Floor scores computed by ASI (F1, F5, F6, F9, F11, F12)."""

    F1_amanah: float = 0.0  # Reversibility/Trust
    F5_peace: float = 1.0  # Peace squared (>= 1.0 required)
    F6_empathy: float = 0.0  # Kappa_r empathy (>= 0.95 required)
    F9_anti_hantu: float = 0.0  # No dark cleverness (< 0.30 required)
    F11_authority: float = 0.0  # Command auth verified
    F12_injection: float = 0.0  # No injection patterns (< 0.85 required)

    def all_hard_pass(self) -> bool:
        """Check if all hard floors pass."""
        return (
            self.F1_amanah >= 0.5  # Reversible
            and self.F11_authority >= 0.5  # Authority verified
            and self.F12_injection < 0.85  # No injection
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "F1_amanah": self.F1_amanah,
            "F5_peace": self.F5_peace,
            "F6_empathy": self.F6_empathy,
            "F9_anti_hantu": self.F9_anti_hantu,
            "F11_authority": self.F11_authority,
            "F12_injection": self.F12_injection,
        }


@dataclass
class OmegaBundle:
    """
    OMEGA_BUNDLE: ASI (Heart) output from stages 555-666.

    This is the isolated output from the "Refract" phase.
    AGI CANNOT see this until 444 TRINITY_SYNC merges it.

    Contains:
    - Stakeholder analysis from 555 EMPATHY
    - Safety constraints from 666 ALIGN
    - ASI's independent vote (SEAL/VOID)
    - Empathy score kappa_r
    - Floor scores for F1, F5, F6, F9, F11, F12
    """

    # Session metadata
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # 555 EMPATHY output
    stakeholders: List[Stakeholder] = field(default_factory=list)
    weakest_stakeholder: Optional[Stakeholder] = None
    empathy_kappa_r: float = 0.0  # >= 0.95 required

    # 666 ALIGN output
    is_reversible: bool = True
    authority_verified: bool = False
    safety_constraints: List[str] = field(default_factory=list)
    recommended_safeguards: List[str] = field(default_factory=list)

    # Floor scores (ASI owns F1, F5, F6, F9, F11, F12)
    floor_scores: ASIFloorScores = field(default_factory=ASIFloorScores)

    # Independent vote (before seeing AGI)
    vote: EngineVote = EngineVote.UNCERTAIN
    vote_reason: str = ""

    # Integrity
    bundle_hash: str = ""

    def compute_hash(self) -> str:
        """Compute integrity hash for this bundle."""
        content = f"{self.session_id}|{self.empathy_kappa_r}|{self.vote}|{self.is_reversible}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def seal(self) -> "OmegaBundle":
        """Seal the bundle (compute hash, mark complete)."""
        self.bundle_hash = self.compute_hash()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "stakeholders": [
                {
                    "name": s.name,
                    "role": s.role,
                    "vulnerability_score": s.vulnerability_score,
                    "potential_harm": s.potential_harm,
                    "voice_weight": s.voice_weight,
                }
                for s in self.stakeholders
            ],
            "weakest_stakeholder": self.weakest_stakeholder.name
            if self.weakest_stakeholder
            else None,
            "empathy_kappa_r": self.empathy_kappa_r,
            "is_reversible": self.is_reversible,
            "authority_verified": self.authority_verified,
            "safety_constraints": self.safety_constraints,
            "recommended_safeguards": self.recommended_safeguards,
            "floor_scores": self.floor_scores.to_dict(),
            "vote": self.vote.value,
            "vote_reason": self.vote_reason,
            "bundle_hash": self.bundle_hash,
        }


# =============================================================================
# MERGED BUNDLE (444 TRINITY_SYNC OUTPUT)
# =============================================================================


@dataclass
class TriWitnessConsensus:
    """Consensus metrics from 444 TRINITY_SYNC."""

    agi_vote: EngineVote = EngineVote.UNCERTAIN
    asi_vote: EngineVote = EngineVote.UNCERTAIN
    consensus_score: float = 0.0  # >= 0.95 for F3 pass
    votes_agree: bool = False
    dissent_reason: str = ""


@dataclass
class MergedBundle:
    """
    MERGED_BUNDLE: APEX (Soul) output from 444 TRINITY_SYNC.

    This is the convergence point where AGI and ASI bundles merge.
    Only APEX (stages 444+) can see both bundles together.

    Contains:
    - Both original bundles (sealed, immutable)
    - Tri-witness consensus calculation
    - Pre-verdict (conditional on 888 JUDGE)
    - Combined floor scores (all 13)
    """

    # Session metadata
    session_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Original bundles (sealed, cannot modify)
    delta_bundle: Optional[DeltaBundle] = None
    omega_bundle: Optional[OmegaBundle] = None

    # 444 TRINITY_SYNC output
    consensus: TriWitnessConsensus = field(default_factory=TriWitnessConsensus)

    # Pre-verdict (before 888 full check)
    pre_verdict: str = "PENDING"  # SEAL, VOID, SABAR, 888_HOLD
    pre_verdict_reason: str = ""

    # Combined floor scores (all 13)
    all_floor_scores: Dict[str, float] = field(default_factory=dict)

    # Integrity
    bundle_hash: str = ""

    def compute_consensus(self) -> TriWitnessConsensus:
        """Compute tri-witness consensus from both bundles."""
        if not self.delta_bundle or not self.omega_bundle:
            return TriWitnessConsensus(consensus_score=0.0, dissent_reason="Missing bundle(s)")

        agi_vote = self.delta_bundle.vote
        asi_vote = self.omega_bundle.vote

        # Both must vote SEAL for consensus
        votes_agree = agi_vote == EngineVote.SEAL and asi_vote == EngineVote.SEAL

        # Calculate consensus score
        if votes_agree:
            consensus_score = min(
                self.delta_bundle.confidence_high,
                self.omega_bundle.empathy_kappa_r,
                0.99,  # Cap at 99% (Omega_0 minimum uncertainty)
            )
        elif agi_vote == EngineVote.VOID or asi_vote == EngineVote.VOID:
            consensus_score = 0.0
        else:
            consensus_score = 0.5  # Uncertain votes get 50%

        dissent_reason = ""
        if not votes_agree:
            if agi_vote == EngineVote.VOID:
                dissent_reason = f"AGI VOID: {self.delta_bundle.vote_reason}"
            elif asi_vote == EngineVote.VOID:
                dissent_reason = f"ASI VOID: {self.omega_bundle.vote_reason}"
            else:
                dissent_reason = "Votes do not agree"

        return TriWitnessConsensus(
            agi_vote=agi_vote,
            asi_vote=asi_vote,
            consensus_score=consensus_score,
            votes_agree=votes_agree,
            dissent_reason=dissent_reason,
        )

    def merge_floor_scores(self) -> Dict[str, float]:
        """Merge floor scores from both bundles."""
        scores = {}

        if self.delta_bundle:
            scores.update(self.delta_bundle.floor_scores.to_dict())

        if self.omega_bundle:
            scores.update(self.omega_bundle.floor_scores.to_dict())

        # F3 (Tri-Witness) and F8 (Genius) computed here
        scores["F3_tri_witness"] = self.consensus.consensus_score
        scores["F8_genius"] = 0.0  # Computed in 777 FORGE
        scores["F10_ontology"] = 1.0  # Checked in 000 INIT

        return scores

    def apply_trinity_dissent_law(self) -> str:
        """
        TRINITY DISSENT LAW:
        - If either AGI or ASI votes VOID -> cannot SEAL
        - Both must vote SEAL to proceed to 777 FORGE
        """
        self.consensus = self.compute_consensus()
        self.all_floor_scores = self.merge_floor_scores()

        if self.consensus.votes_agree and self.consensus.agi_vote == EngineVote.SEAL:
            if self.consensus.consensus_score >= 0.95:
                self.pre_verdict = "SEAL"
                self.pre_verdict_reason = "Trinity consensus achieved"
            else:
                self.pre_verdict = "SABAR"
                self.pre_verdict_reason = f"Consensus {self.consensus.consensus_score:.2f} < 0.95"
        elif (
            self.consensus.agi_vote == EngineVote.VOID or self.consensus.asi_vote == EngineVote.VOID
        ):
            self.pre_verdict = "VOID"
            self.pre_verdict_reason = self.consensus.dissent_reason
        else:
            self.pre_verdict = "888_HOLD"
            self.pre_verdict_reason = "Uncertain votes require human review"

        return self.pre_verdict

    def seal(self) -> "MergedBundle":
        """Seal the bundle after consensus computation."""
        content = f"{self.session_id}|{self.pre_verdict}|{self.consensus.consensus_score}"
        self.bundle_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "EngineVote",
    # AGI (Delta) types
    "Hypothesis",
    "ReasoningTree",
    "AGIFloorScores",
    "DeltaBundle",
    # ASI (Omega) types
    "Stakeholder",
    "ASIFloorScores",
    "OmegaBundle",
    # Merged (APEX) types
    "TriWitnessConsensus",
    "MergedBundle",
]
