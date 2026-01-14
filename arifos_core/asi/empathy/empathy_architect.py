"""
arifos_core/asi/empathy/empathy_architect.py

540 Empathy Architecture - Three-Layer Model for κᵣ Conductance

Purpose:
    Three-layer empathy processing:
    - Layer 1: Recognition (from 111 SENSE)
    - Layer 2: Understanding (from 530 ToM)
    - Layer 3: Response (κᵣ conductance computation)

    Implements the κᵣ formula:
    κᵣ = (ToM_Quality × Care_Signals × Dignity) / Barriers_to_Understanding

Authority:
    - L1_THEORY/canon/555_empathize/540_EMPATHY_ARCHITECTURE_v46.md
    - L2_PROTOCOLS/v46/555_empathize/555_empathize.json

Design:
    Input: SENSE bundle + ToM bundle
    Output: Empathy Architecture bundle with 3-layer processing and κᵣ score

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum


class EmpathyRequirement(str, Enum):
    """Empathy requirement levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRISIS = "CRISIS"


class Stakes(str, Enum):
    """Stakes levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Layer1Recognition:
    """
    Layer 1: Recognition (κᵣ Sensing)

    Source: 111 SENSE stage
    Purpose: Detect empathy requirement signals

    Attributes:
        empathy_required: Empathy level needed
        vulnerability_signals: List of detected vulnerability indicators
        stakeholder_risk: Primary stakeholder at risk
        urgency_score: Urgency level (0.0-1.0)
    """
    empathy_required: EmpathyRequirement
    vulnerability_signals: List[str] = field(default_factory=list)
    stakeholder_risk: str = "primary_user"
    urgency_score: float = 0.0


@dataclass
class Layer2Understanding:
    """
    Layer 2: Understanding (ToM Integration)

    Source: 530 ToM analysis
    Purpose: Model mental states, not just signals

    Attributes:
        mental_model: User's view of situation
        vulnerability_score: User vulnerability (0.0-1.0)
        knowledge_gaps: What user doesn't know
        emotional_state: Dominant emotion
        stakes: What user risks
    """
    mental_model: Dict = field(default_factory=dict)
    vulnerability_score: float = 0.0
    knowledge_gaps: List[str] = field(default_factory=list)
    emotional_state: str = ""
    stakes: Stakes = Stakes.LOW


@dataclass
class Layer3Response:
    """
    Layer 3: Response (κᵣ Conductance)

    Source: 520 F4 evaluation
    Purpose: Transmit care with minimal resistance

    Attributes:
        kappa_r: Conductance score (0.0-1.0)
        passed: True if κᵣ ≥ 0.95
        care_signals: List of care transmission indicators
        dignity_check: True if dignity preserved
    """
    kappa_r: float
    passed: bool
    care_signals: List[str] = field(default_factory=list)
    dignity_check: bool = True

    @property
    def floor_status(self) -> str:
        """F4 floor status string"""
        return "SEAL" if self.passed else "PARTIAL"


@dataclass
class EmpathyArchitectureBundle:
    """
    Complete 3-layer empathy architecture output.

    Feeds into:
    - 520 F4 floor check
    - 550 Weakest stakeholder protocol
    - 560 ASI integration
    - 666 BRIDGE synthesis

    Attributes:
        layer_1_recognition: Recognition layer output
        layer_2_understanding: Understanding layer output
        layer_3_response: Response layer output
        architecture_verdict: Overall verdict (SEAL|PARTIAL|VOID)
    """
    layer_1_recognition: Layer1Recognition
    layer_2_understanding: Layer2Understanding
    layer_3_response: Layer3Response
    architecture_verdict: str

    @property
    def empathy_passed(self) -> bool:
        """True if empathy architecture passes (κᵣ ≥ 0.95)"""
        return self.layer_3_response.passed


class EmpathyArchitect:
    """
    Empathy Architect - 540 Three-Layer Model

    Processes empathy through three layers:
    1. Recognition: Detect empathy needs from SENSE
    2. Understanding: Integrate ToM mental state modeling
    3. Response: Compute κᵣ conductance

    κᵣ Formula:
        κᵣ = (ToM_Quality × Care_Signals × Dignity) / Barriers_to_Understanding

    Thresholds:
        - κᵣ ≥ 0.95 → SEAL (high conductance)
        - κᵣ < 0.95 → PARTIAL (resistance detected)
        - κᵣ < 0.70 → VOID (barriers too high)

    Conductance Barriers (reduce these):
        - Complex terminology
        - Assumptions about user knowledge
        - Culturally-specific solutions
        - Condescending language
        - Vague advice

    Care Transmission Checklist:
        - Acknowledge emotional state (F7 RASA)
        - Address knowledge gaps from Layer 2
        - Provide concrete, actionable resources
        - Preserve dignity (no "just" or "simply")
        - Accessible language (weakest stakeholder level)
        - No jargon unless explained

    Example:
        architect = EmpathyArchitect()
        arch_bundle = architect.process(sense_bundle, tom_bundle)
        assert arch_bundle.layer_3_response.kappa_r >= 0.95
        assert arch_bundle.architecture_verdict == "SEAL"
    """

    # Thresholds from canonical spec
    KAPPA_R_THRESHOLD = 0.95
    CRISIS_KAPPA_R_THRESHOLD = 0.98
    VOID_THRESHOLD = 0.70

    def __init__(self):
        """Initialize empathy architect."""
        pass

    def process(
        self,
        sense_bundle: Dict,
        tom_bundle: "ToMBundle"
    ) -> EmpathyArchitectureBundle:
        """
        Process empathy through 3-layer architecture.

        Args:
            sense_bundle: Output from 111 SENSE
            tom_bundle: Output from 530 ToM

        Returns:
            EmpathyArchitectureBundle with 3 layers and verdict
        """
        # Layer 1: Recognition
        layer_1 = self._layer_1_recognition(sense_bundle)

        # Layer 2: Understanding (integrates ToM)
        layer_2 = self._layer_2_understanding(sense_bundle, tom_bundle)

        # Layer 3: Response (compute κᵣ)
        layer_3 = self._layer_3_response(tom_bundle, layer_1, layer_2)

        # Overall verdict
        if layer_3.kappa_r >= self.KAPPA_R_THRESHOLD:
            verdict = "SEAL"
        elif layer_3.kappa_r >= self.VOID_THRESHOLD:
            verdict = "PARTIAL"
        else:
            verdict = "VOID"

        return EmpathyArchitectureBundle(
            layer_1_recognition=layer_1,
            layer_2_understanding=layer_2,
            layer_3_response=layer_3,
            architecture_verdict=verdict
        )

    def _layer_1_recognition(self, sense_bundle: Dict) -> Layer1Recognition:
        """
        Layer 1: Recognition - Detect empathy requirement signals.

        Maps SENSE output to empathy requirements:
        - Subtext: desperation, vulnerability, urgency → HIGH/CRISIS
        - Domain: @WELL, @RASA, @WEALTH → elevated empathy
        - Lane: CRISIS → CRISIS requirement
        """
        domain = sense_bundle.get("domain", "")
        subtext = sense_bundle.get("subtext", "")
        lane = sense_bundle.get("lane", "STANDARD")
        urgency = sense_bundle.get("urgency", 0.5)

        # Determine empathy requirement level
        if lane == "CRISIS":
            empathy_required = EmpathyRequirement.CRISIS
        elif subtext in ["desperation", "fear"]:
            empathy_required = EmpathyRequirement.HIGH
        elif subtext in ["urgency", "stress", "concern"]:
            empathy_required = EmpathyRequirement.MEDIUM
        else:
            empathy_required = EmpathyRequirement.LOW

        # Domain-based elevation
        if domain in ["@WELL", "@RASA"]:
            if empathy_required == EmpathyRequirement.LOW:
                empathy_required = EmpathyRequirement.MEDIUM
            elif empathy_required == EmpathyRequirement.MEDIUM:
                empathy_required = EmpathyRequirement.HIGH

        # Collect vulnerability signals
        vulnerability_signals = []
        if subtext in ["desperation", "fear", "urgency"]:
            vulnerability_signals.append(f"subtext: {subtext}")
        if domain in ["@WELL", "@WEALTH", "@RASA"]:
            vulnerability_signals.append(f"domain: {domain}")
        if lane == "CRISIS":
            vulnerability_signals.append("CRISIS lane")

        return Layer1Recognition(
            empathy_required=empathy_required,
            vulnerability_signals=vulnerability_signals,
            stakeholder_risk="primary_user",
            urgency_score=urgency
        )

    def _layer_2_understanding(
        self,
        sense_bundle: Dict,
        tom_bundle: "ToMBundle"
    ) -> Layer2Understanding:
        """
        Layer 2: Understanding - Integrate ToM mental state modeling.

        Maps user perspective, identifies biases, detects gaps, infers stakes.
        """
        # Extract ToM insights
        mental_model = {
            "beliefs": tom_bundle.mental_states.beliefs,
            "desires": tom_bundle.mental_states.desires,
            "emotions": tom_bundle.mental_states.emotions
        }

        vulnerability_score = tom_bundle.vulnerability_score
        knowledge_gaps = tom_bundle.mental_states.knowledge_gaps
        emotional_state = tom_bundle.mental_states.emotions

        # Infer stakes based on vulnerability and domain
        domain = sense_bundle.get("domain", "")
        lane = sense_bundle.get("lane", "STANDARD")

        if lane == "CRISIS" or vulnerability_score >= 0.85:
            stakes = Stakes.CRITICAL
        elif domain in ["@WELL", "@WEALTH"]:
            stakes = Stakes.HIGH
        elif vulnerability_score >= 0.60:
            stakes = Stakes.MEDIUM
        else:
            stakes = Stakes.LOW

        return Layer2Understanding(
            mental_model=mental_model,
            vulnerability_score=vulnerability_score,
            knowledge_gaps=knowledge_gaps,
            emotional_state=emotional_state,
            stakes=stakes
        )

    def _layer_3_response(
        self,
        tom_bundle: "ToMBundle",
        layer_1: Layer1Recognition,
        layer_2: Layer2Understanding
    ) -> Layer3Response:
        """
        Layer 3: Response - Compute κᵣ conductance.

        κᵣ = (ToM_Quality × Care_Signals × Dignity) / Barriers_to_Understanding

        Components:
        - ToM_Quality: tom_bundle.composite_score
        - Care_Signals: Based on empathy_required and urgency
        - Dignity: Always 1.0 (no violations assumed)
        - Barriers: Computed from complexity, assumptions, cultural factors
        """
        # ToM Quality
        tom_quality = tom_bundle.composite_score

        # Care Signals (based on empathy requirement)
        care_signals_score = self._compute_care_signals(
            layer_1.empathy_required,
            layer_1.urgency_score
        )

        # Dignity (assume preserved unless violated)
        dignity = 1.0

        # Barriers to Understanding
        barriers = self._compute_barriers(layer_2.knowledge_gaps)

        # κᵣ formula
        numerator = tom_quality * care_signals_score * dignity
        denominator = max(barriers, 0.1)  # Prevent division by zero
        kappa_r = numerator / denominator

        # Clamp to [0.0, 1.0]
        kappa_r = min(kappa_r, 1.0)

        # Adjust threshold for CRISIS
        threshold = (
            self.CRISIS_KAPPA_R_THRESHOLD
            if layer_1.empathy_required == EmpathyRequirement.CRISIS
            else self.KAPPA_R_THRESHOLD
        )

        passed = kappa_r >= threshold

        # Care signals list (for transparency)
        care_signals = [
            "acknowledge_emotional_state",
            "address_knowledge_gaps",
            "provide_actionable_resources",
            "preserve_dignity"
        ]

        return Layer3Response(
            kappa_r=kappa_r,
            passed=passed,
            care_signals=care_signals,
            dignity_check=True  # Assume preserved unless violated
        )

    def _compute_care_signals(
        self,
        empathy_required: EmpathyRequirement,
        urgency_score: float
    ) -> float:
        """
        Compute care signals score based on empathy requirement.

        Higher empathy requirement → higher care signal expectation
        """
        base_scores = {
            EmpathyRequirement.LOW: 0.90,
            EmpathyRequirement.MEDIUM: 0.95,
            EmpathyRequirement.HIGH: 0.98,
            EmpathyRequirement.CRISIS: 1.00
        }

        base = base_scores[empathy_required]

        # Urgency modulation
        care_signals = base + (urgency_score * 0.05)

        return min(care_signals, 1.0)

    def _compute_barriers(self, knowledge_gaps: List[str]) -> float:
        """
        Compute barriers to understanding.

        Barriers include:
        - Complexity (# of knowledge gaps)
        - Assumptions (implied by gaps)
        - Cultural factors (domain-specific)

        Lower barriers → higher κᵣ conductance
        """
        # Base barrier (minimum complexity)
        base_barrier = 0.5

        # Knowledge gaps add barriers
        gap_barrier = len(knowledge_gaps) * 0.10

        total_barrier = base_barrier + gap_barrier

        # Clamp to reasonable range [0.3, 1.5]
        return max(0.3, min(total_barrier, 1.5))
