"""
arifos_core/asi/tom/theory_of_mind.py

530 Theory of Mind - Mental State Substrate for Constitutional Care

Purpose:
    Computational attribution of mental states to others:
    - Beliefs (including false beliefs)
    - Desires (stated and unstated)
    - Intentions (goals, motives)
    - Emotions (inferred from subtext)
    - Knowledge States (what user knows vs. doesn't know)

Authority:
    - L1_THEORY/canon/555_empathize/530_THEORY_OF_MIND_v46.md
    - L2_PROTOCOLS/v46/555_empathize/555_empathize.json

Design:
    Input: SENSE bundle (from 111 SENSE stage)
    Output: ToM bundle with composite score and mental state attribution

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class Confidence(str, Enum):
    """ToM confidence levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class MentalStates:
    """
    Attributed mental states of the user.

    Attributes:
        beliefs: User beliefs (true/false beliefs mapped)
        desires: Stated and inferred wants
        emotions: Dominant emotional state
        knowledge_gaps: What user doesn't know
    """
    beliefs: Dict[str, bool] = field(default_factory=dict)
    desires: List[str] = field(default_factory=list)
    emotions: str = ""
    knowledge_gaps: List[str] = field(default_factory=list)


@dataclass
class ToMDimensions:
    """
    Four dimensions of Theory of Mind evaluation.

    Each scored 0.0-1.0:
        - false_belief: Can model incorrect beliefs user holds
        - perspective: Distinguish user's view from system's
        - intent: Separate what user says vs. wants
        - emotion: Map subtext to mental state
    """
    false_belief: float = 0.0
    perspective: float = 0.0
    intent: float = 0.0
    emotion: float = 0.0

    @property
    def composite(self) -> float:
        """Composite ToM score (average of dimensions)"""
        return (self.false_belief + self.perspective + self.intent + self.emotion) / 4.0


@dataclass
class ToMBundle:
    """
    Theory of Mind analysis bundle.

    Output from 530 ToM analysis, feeds into:
    - 520 F4 (κᵣ scoring)
    - 550 Weakest (vulnerability detection)
    - 540 Architecture Layer 2

    Attributes:
        composite_score: Overall ToM quality (0.0-1.0)
        dimensions: Individual dimension scores
        mental_states: Attributed beliefs, desires, emotions, gaps
        vulnerability_score: User vulnerability (0.0-1.0)
        crisis_flag: True if CRISIS override triggered
        confidence: HIGH (≥0.95), MEDIUM (0.70-0.95), LOW (<0.70)
    """
    composite_score: float
    dimensions: ToMDimensions
    mental_states: MentalStates
    vulnerability_score: float
    crisis_flag: bool
    confidence: Confidence

    @property
    def seal_eligible(self) -> bool:
        """True if ToM score ≥ 0.95 (SEAL threshold)"""
        return self.composite_score >= 0.95

    @property
    def needs_clarification(self) -> bool:
        """True if ToM score < 0.70 (request clarification)"""
        return self.composite_score < 0.70


class TheoryOfMindAnalyzer:
    """
    Theory of Mind Analyzer - 530 ToM Component

    Analyzes user mental states from SENSE bundle input.

    Thresholds:
        - ToM ≥ 0.95 → High confidence (SEAL eligible)
        - 0.70 ≤ ToM < 0.95 → Medium confidence (PARTIAL)
        - ToM < 0.70 → Low confidence (request clarification)

    Crisis Override:
        If lane == "CRISIS" AND emotion_score ≥ 0.80:
            - Set crisis_flag = True
            - Increase κᵣ threshold to 0.98
            - Trigger human oversight (F8)

    Example:
        analyzer = TheoryOfMindAnalyzer()
        tom_bundle = analyzer.analyze(sense_bundle)
        assert tom_bundle.composite_score >= 0.70
        assert tom_bundle.confidence == Confidence.HIGH
    """

    # Thresholds from canonical spec
    SEAL_THRESHOLD = 0.95
    PARTIAL_THRESHOLD = 0.70
    CRISIS_EMOTION_THRESHOLD = 0.80

    def __init__(self):
        """Initialize ToM analyzer with default thresholds."""
        pass

    def analyze(self, sense_bundle: Dict) -> ToMBundle:
        """
        Perform Theory of Mind analysis on SENSE bundle.

        Args:
            sense_bundle: Output from 111 SENSE stage containing:
                - domain: str (@WELL, @RASA, @WEALTH, etc.)
                - subtext: str (desperation, urgency, curiosity, doubt)
                - lane: str (CRISIS, STANDARD, CURIOSITY)
                - tone: str (hostile, neutral, respectful)

        Returns:
            ToMBundle with composite score, dimensions, mental states
        """
        # Extract SENSE data
        domain = sense_bundle.get("domain", "")
        subtext = sense_bundle.get("subtext", "")
        lane = sense_bundle.get("lane", "STANDARD")
        tone = sense_bundle.get("tone", "neutral")
        query_text = sense_bundle.get("query", "")

        # Compute ToM dimensions
        dimensions = self._compute_dimensions(
            query_text=query_text,
            domain=domain,
            subtext=subtext,
            tone=tone
        )

        # Attribute mental states
        mental_states = self._attribute_mental_states(
            query_text=query_text,
            domain=domain,
            subtext=subtext
        )

        # Compute vulnerability
        vulnerability_score = self._compute_vulnerability(
            dimensions=dimensions,
            lane=lane,
            domain=domain,
            subtext=subtext
        )

        # Check crisis override
        crisis_flag = (
            lane == "CRISIS" and
            dimensions.emotion >= self.CRISIS_EMOTION_THRESHOLD
        )

        # Determine confidence level
        composite = dimensions.composite
        if composite >= self.SEAL_THRESHOLD:
            confidence = Confidence.HIGH
        elif composite >= self.PARTIAL_THRESHOLD:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW

        return ToMBundle(
            composite_score=composite,
            dimensions=dimensions,
            mental_states=mental_states,
            vulnerability_score=vulnerability_score,
            crisis_flag=crisis_flag,
            confidence=confidence
        )

    def _compute_dimensions(
        self,
        query_text: str,
        domain: str,
        subtext: str,
        tone: str
    ) -> ToMDimensions:
        """
        Compute four ToM dimensions.

        Each dimension scored 0.0-1.0:
        - false_belief: Detect incorrect beliefs
        - perspective: Cultural/personal context awareness
        - intent: Underlying need vs. stated query
        - emotion: Inferred emotional state
        """
        # False belief understanding (heuristic-based for now)
        false_belief = self._score_false_belief(query_text, domain)

        # Perspective taking (context-sensitivity)
        perspective = self._score_perspective(query_text, tone)

        # Intent attribution (subtext → intent mapping)
        intent = self._score_intent(query_text, subtext)

        # Emotional state inference (subtext → emotion)
        emotion = self._score_emotion(subtext, domain)

        return ToMDimensions(
            false_belief=false_belief,
            perspective=perspective,
            intent=intent,
            emotion=emotion
        )

    def _score_false_belief(self, query_text: str, domain: str) -> float:
        """
        Score ability to detect false beliefs.

        Heuristics:
        - Medical misconceptions (@WELL) → lower score
        - Financial myths (@WEALTH) → lower score
        - Clear factual query → higher score
        """
        query_lower = query_text.lower()

        # Detect potential false beliefs
        false_belief_indicators = [
            "cure", "always", "never", "everyone knows", "obviously",
            "definitely", "guarantee", "certainly will"
        ]

        has_false_belief = any(ind in query_lower for ind in false_belief_indicators)

        if has_false_belief:
            return 0.85  # High confidence in detecting false belief
        elif domain in ["@WELL", "@WEALTH"]:
            return 0.75  # Medium-high (domain suggests potential misconception)
        else:
            return 0.90  # High baseline (clear factual query)

    def _score_perspective(self, query_text: str, tone: str) -> float:
        """
        Score perspective-taking ability.

        Considers:
        - Cultural context cues in query
        - Tone indicates user's emotional perspective
        - Query complexity
        """
        if tone in ["hostile", "distressed"]:
            return 0.85  # High awareness of user's emotional perspective
        elif tone == "neutral":
            return 0.90  # Clear perspective distinction
        else:
            return 0.92  # Optimal perspective taking

    def _score_intent(self, query_text: str, subtext: str) -> float:
        """
        Score intent attribution (what user wants vs. says).

        Subtext reveals underlying intent:
        - desperation → need for hope/solution
        - curiosity → need for understanding
        - urgency → need for fast action
        """
        if subtext in ["desperation", "urgency", "fear"]:
            return 0.88  # Strong intent detection (need vs. query mismatch likely)
        elif subtext == "curiosity":
            return 0.95  # Intent matches query (straightforward)
        else:
            return 0.90  # Medium-high intent attribution

    def _score_emotion(self, subtext: str, domain: str) -> float:
        """
        Score emotional state inference from subtext.

        Subtext directly maps to emotion:
        - desperation → high distress (0.90+)
        - fear → high anxiety (0.85+)
        - curiosity → calm exploration (0.50)
        """
        emotion_map = {
            "desperation": 0.95,
            "fear": 0.90,
            "urgency": 0.85,
            "stress": 0.75,
            "concern": 0.65,
            "curiosity": 0.50,
            "doubt": 0.70
        }

        emotion_score = emotion_map.get(subtext, 0.60)

        # Domain modulation
        if domain == "@WELL":  # Mental health queries → higher emotion weight
            emotion_score = min(emotion_score + 0.10, 1.0)

        return emotion_score

    def _attribute_mental_states(
        self,
        query_text: str,
        domain: str,
        subtext: str
    ) -> MentalStates:
        """
        Attribute specific mental states to user.

        Returns:
            MentalStates with beliefs, desires, emotions, knowledge_gaps
        """
        # Simplified attribution (real implementation would use NLP)
        beliefs = {}
        desires = []
        emotions = subtext
        knowledge_gaps = []

        # Domain-based inference
        if domain == "@WELL":
            beliefs["seeking_relief"] = True
            desires.append("health improvement")
            knowledge_gaps.append("treatment options")
        elif domain == "@WEALTH":
            beliefs["financial_concern"] = True
            desires.append("financial security")
            knowledge_gaps.append("resources")
        elif domain == "@RASA":
            beliefs["dignity_concern"] = True
            desires.append("respectful treatment")

        return MentalStates(
            beliefs=beliefs,
            desires=desires,
            emotions=emotions,
            knowledge_gaps=knowledge_gaps
        )

    def _compute_vulnerability(
        self,
        dimensions: ToMDimensions,
        lane: str,
        domain: str,
        subtext: str
    ) -> float:
        """
        Compute user vulnerability score.

        Formula: V_user = ToM_emotion × (1 + stakes) × (1 / resources)

        Simplified version:
        - High emotion + CRISIS lane → high vulnerability
        - @WELL domain → elevated vulnerability
        - Desperation subtext → elevated vulnerability
        """
        base_vulnerability = dimensions.emotion

        # Stakes multiplier
        stakes = 1.0
        if lane == "CRISIS":
            stakes = 2.0
        elif domain == "@WELL":
            stakes = 1.5

        # Resources factor (inverse)
        resources = 0.5  # Assume limited resources unless indicated
        if subtext == "curiosity":
            resources = 0.8  # More resources (leisurely exploration)

        vulnerability = base_vulnerability * (1 + stakes) * (1 / resources)

        # Clamp to [0.0, 1.0]
        return min(vulnerability, 1.0)
