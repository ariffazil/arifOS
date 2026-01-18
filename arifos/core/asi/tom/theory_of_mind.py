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
    - 000_THEORY/canon/555_empathize/530_THEORY_OF_MIND_v46.md
    - AAA_MCP/v46/555_empathize/555_empathize.json

Design:
    Input: SENSE bundle (from 111 SENSE stage)
    Output: ToM bundle with composite score and mental state attribution

DITEMPA BUKAN DIBERI - Forged v46.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


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
        Score ability to detect false beliefs with rigorous domain patterns.

        Heuristics:
        - Medical myths (@WELL): 'cure', 'detox', 'miracle'
        - Financial myths (@WEALTH): 'guaranteed', 'risk-free', 'instant'
        - Absolutes: 'always', 'never', 'everyone knows'
        """
        query_lower = query_text.lower()

        # 1. Domain-Specific False Belief Patterns
        well_myths = ["cure", "detox", "miracle", "cleanse", "always works", "secret", "they don't want you to know"]
        wealth_myths = ["guaranteed", "risk-free", "instant return", "double your money", "passive income secret"]

        # 2. Epistemic Absolutes (Red Flags)
        absolutes = ["always", "never", "definitely", "obviously", "everyone knows", "undeniable", "proven fact"]

        detected_myths = 0
        if domain == "@WELL":
            detected_myths += sum(1 for m in well_myths if m in query_lower)
        elif domain == "@WEALTH":
            detected_myths += sum(1 for m in wealth_myths if m in query_lower)

        detected_absolutes = sum(1 for a in absolutes if a in query_lower)

        # Scoring Logic
        if detected_myths > 0:
            return 0.85 + (min(detected_myths, 3) * 0.03)  # High confidence in False Belief
        elif detected_absolutes > 0:
            return 0.75 + (min(detected_absolutes, 3) * 0.05)  # Moderate-High

        # Baseline check (clear factual query)
        if "?" in query_text and any(w in query_lower for w in ["what", "how", "when", "who"]):
             return 0.92  # High confidence (Standard Inquiry)

        return 0.60  # Default low confidence (ambiguity)

    def _score_perspective(self, query_text: str, tone: str) -> float:
        """
        Score perspective-taking ability.

        Considers:
        - Cultural/context cues ("in my culture", "for us")
        - Personal context ("I feel", "my situation")
        """
        query_lower = query_text.lower()

        # Perspective Markers
        cultural_markers = ["culture", "tradition", "faith", "community", "us", "we", "custom"]
        personal_markers = ["i feel", "my opinion", "worried", "confused", "my situation"]

        score = 0.50 # Baseline

        # If query is clearly factual/objective (high intent score), that IS the perspective
        # "I want to know X" is a valid perspective.
        if tone == "neutral":
            score = 0.80

        if any(m in query_lower for m in cultural_markers):
            score += 0.15 # Bonus for cultural explicitness
        if any(m in query_lower for m in personal_markers):
            score += 0.15

        if tone in ["hostile", "distressed"]:
            score = max(score, 0.85) # High emotional salience forces perspective check

        return min(score, 0.98)

    def _score_intent(self, query_text: str, subtext: str) -> float:
        """
        Score intent attribution (Subtext vs Text).
        """
        # If subtext is strongly emotional, intent is likely emotional support, not just facts
        if subtext in ["desperation", "fear", "urgency"]:
            return 0.92
        elif subtext == "curiosity":
            return 0.95
        elif subtext == "doubt":
             return 0.80

        # Fallback
        return 0.70

    def _score_emotion(self, subtext: str, domain: str) -> float:
        """
        Score emotional state inference.
        """
        emotion_map = {
            "desperation": 0.98, # High confidence + High salience
            "fear": 0.92,
            "urgency": 0.85,
            "stress": 0.75,
            "doubt": 0.70,
            "concern": 0.65,
            "curiosity": 0.90, # High confidence in "Curiosity" state
            "neutral": 0.85 # High confidence in "Neutral" state
        }

        score = emotion_map.get(subtext, 0.50)

        # Domain Sensitivity
        if domain == "@WELL" and score > 0.6:
            score = min(score + 0.1, 1.0) # Health anxiety amplification

        return score

    def _attribute_mental_states(
        self,
        query_text: str,
        domain: str,
        subtext: str
    ) -> MentalStates:
        """
        Attribute specific mental states using robust keyword analysis.
        """
        query_lower = query_text.lower()
        beliefs = {}
        desires = []
        emotions = subtext
        knowledge_gaps = []

        # 1. Beliefs Logic
        if "i think" in query_lower or "i believe" in query_lower:
            beliefs["self_stated"] = True
        if subtext == "doubt":
            beliefs["uncertainty"] = True

        # 2. Desires Logic (Needs)
        noun_phrases = {
            "@WELL": ["relief", "cure", "health", "diagnosis", "answer"],
            "@WEALTH": ["money", "security", "profit", "savings", "freedom"],
            "@RASA": ["respect", "clarity", "fairness"]
        }

        # General desires
        if any(w in query_lower for w in ["want", "need", "looking for", "help"]):
            desires.append("assistance")

        # Domain desires
        found_desires = [d for d in noun_phrases.get(domain, []) if d in query_lower]
        desires.extend(found_desires)

        # Implicit desires from subtext
        if subtext == "desperation": desires.append("immediate_relief")
        if subtext == "curiosity": desires.append("understanding")

        # 3. Knowledge Gaps (Epistemic State)
        if any(w in query_lower for w in ["why", "cause", "reason"]):
            knowledge_gaps.append("causality")
        elif any(w in query_lower for w in ["how", "method", "way"]):
            knowledge_gaps.append("procedure")
        elif any(w in query_lower for w in ["what", "who", "when"]):
            knowledge_gaps.append("facts")

        if domain == "@WELL" and not beliefs.get("self_stated"):
            knowledge_gaps.append("medical_consensus")

        return MentalStates(
            beliefs=beliefs,
            desires=list(set(desires)), # De-dupe
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
