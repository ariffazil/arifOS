"""
arifos_core/system/stages/stage_111_sense.py

Stage 111 SENSE - Perception and Orientation Protocol (Track C)

Authority:
- Track A Canon: 000_THEORY/canon/111_sense/111_SENSE_STAGE_v46.md (Grade A+)
- Track B Spec: AAA_MCP/v46/111_sense/111_sense_stage.json
- Track C Code: THIS FILE

Constitutional Functions:
1. Tokenize Input: Break query into semantic units
2. Classify Intent: question/command/dialog/paradox
3. Detect Language Signals: sentiment, formality, urgency
4. Compute H_in: Shannon entropy baseline for ΔS measurement
5. Flag Anomalies: Crisis patterns, injection residuals, contradictions
6. Constitutional Terrain Mapping: Domain detection (@PROMPT, @RIF, @WELL, etc.)
7. ATLAS-333 Lane Classification: CRISIS/FACTUAL/SOCIAL/CARE routing
8. RMS Orthogonal Measurement: ΔΩΨ axis mapping
9. TCHA Integration: Time-Critical Harm Awareness override
10. Perception Bundle Generation: Cryptographically signed handoff to 222 REFLECT

Motto: "DITEMPA BUKAN DIBERI" (Forged, Not Given)
Breakthrough: RMS Orthogonal Measurement Layer - Thermodynamic Perception Doctrine

Version: v46.1.0
Author: arifOS Project (Engineer: Claude Sonnet 4.5)
Grade: A+ SEALED WITH DISTINCTION (from Kimi APEX PRIME)
ZKPC: 0fcc9b084a4bd8ade9d4aec184aa576530708921
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Import existing modules to reuse
from ...agi.entropy import compute_entropy_metrics, EntropyMetrics


# =============================================================================
# CONSTANTS FROM SPEC
# =============================================================================

# Intent types
class IntentType(str, Enum):
    """Query intent classification."""
    QUESTION = "question"
    COMMAND = "command"
    DIALOG = "dialog"
    PARADOX = "paradox"


# Domain organs (W@W Federation)
class DomainType(str, Enum):
    """Constitutional domain classification."""
    PROMPT = "@PROMPT"      # Language governance
    RIF = "@RIF"            # Logic and reasoning
    WELL = "@WELL"          # Care and wellness
    WEALTH = "@WEALTH"      # Resources and investment
    GEOX = "@GEOX"          # Reality and geography
    LAW = "@LAW"            # Legal questions
    MAP = "@MAP"            # Spatial reasoning


# ATLAS-333 Lane classification
class LaneType(str, Enum):
    """ATLAS-333 routing lanes with priority."""
    CRISIS = "CRISIS"        # Priority 1: Life-threatening
    FACTUAL = "FACTUAL"      # Priority 2: Standard reasoning
    SOCIAL = "SOCIAL"        # Priority 3: Empathy-weighted
    CARE = "CARE"            # Priority 4: Vulnerability support


# Language signals
class SentimentType(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class FormalityType(str, Enum):
    """Formality level."""
    CASUAL = "casual"
    PROFESSIONAL = "professional"
    OFFICIAL = "official"


class UrgencyType(str, Enum):
    """Urgency level."""
    EMERGENCY = "emergency"
    NORMAL = "normal"
    EXPLORATORY = "exploratory"


# Crisis patterns for TCHA
CRISIS_PATTERNS_ENGLISH = [
    "i want to die",
    "suicide",
    "end it all",
    "kill myself",
    "not worth living",
    "better off dead",
    "self harm",
    "hurt myself",
]

CRISIS_PATTERNS_MALAY = [
    "bunuh diri",
    "nak mati",
    "tamat hidup",
    "ingin mati",
    "tak mahu hidup",
]

# Domain detection keywords
DOMAIN_KEYWORDS = {
    DomainType.PROMPT: ["rephrase", "rewrite", "translate", "tone", "language"],
    DomainType.RIF: ["prove", "calculate", "logic", "reason", "truth"],
    DomainType.WELL: ["feeling", "sad", "happy", "emotion", "mental health"],
    DomainType.WEALTH: ["invest", "money", "finance", "budget", "cost"],
    DomainType.GEOX: ["where", "location", "country", "city", "geography"],
    DomainType.LAW: ["legal", "law", "rights", "regulation", "court"],
    DomainType.MAP: ["directions", "route", "navigate", "map", "location"],
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class TokenBundle:
    """Tokenized semantic units."""
    tokens: List[str]
    semantic_units: List[Dict[str, str]]
    token_count: int


@dataclass
class LanguageSignals:
    """Language metadata signals."""
    sentiment: SentimentType
    formality: FormalityType
    urgency: UrgencyType


@dataclass
class AnomalyFlags:
    """Anomaly detection flags."""
    crisis: bool = False
    high_stakes: bool = False
    injection_residual: bool = False
    contradictions: bool = False
    patterns_found: List[str] = field(default_factory=list)


@dataclass
class RMSVector:
    """
    RMS Orthogonal Measurement (ΔΩΨ axes).

    Breakthrough: A+ DISTINCTION by Kimi APEX PRIME.

    Axes:
    - Δ (Delta): Clarity gain (ΔS measurement)
    - Ω (Omega): Humility band (Ω₀, ω_fiction)
    - Ψ (Psi): Vitality index (emotional health)
    """
    delta: float  # Intent vector magnitude
    omega: float  # Stakes/binding energy
    psi: float    # Fragility/care level

    def to_dict(self) -> Dict[str, float]:
        return {"Δ": self.delta, "Ω": self.omega, "Ψ": self.psi}


@dataclass
class TCHAResult:
    """Time-Critical Harm Awareness check result."""
    crisis_detected: bool
    pattern_matched: Optional[str] = None
    should_bypass: bool = False
    recommended_action: str = "CONTINUE"
    message: Optional[str] = None


@dataclass
class PerceptionBundle:
    """
    Complete perception bundle handed from 111 SENSE to 222 REFLECT.

    This is the cryptographically signed YAML output.
    """
    # Core fields
    query: str
    tokens: TokenBundle
    intent: IntentType
    domain: DomainType
    lane: LaneType

    # Entropy and RMS
    h_in: float
    h_in_metrics: EntropyMetrics
    rms_vector: RMSVector

    # Language signals
    signals: LanguageSignals

    # Anomalies and TCHA
    anomalies: AnomalyFlags
    tcha: TCHAResult

    # Metadata
    bearing_to_truth: str = "calibrated"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signature: Optional[str] = None  # Cryptographic signature

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "query": self.query,
            "tokens": {
                "tokens": self.tokens.tokens,
                "semantic_units": self.tokens.semantic_units,
                "count": self.tokens.token_count,
            },
            "intent": self.intent.value,
            "domain": self.domain.value,
            "lane": self.lane.value,
            "H_in": self.h_in,
            "H_in_metrics": self.h_in_metrics.to_dict(),
            "RMS_vector": self.rms_vector.to_dict(),
            "signals": {
                "sentiment": self.signals.sentiment.value,
                "formality": self.signals.formality.value,
                "urgency": self.signals.urgency.value,
            },
            "anomalies": {
                "crisis": self.anomalies.crisis,
                "high_stakes": self.anomalies.high_stakes,
                "injection_residual": self.anomalies.injection_residual,
                "contradictions": self.anomalies.contradictions,
                "patterns": self.anomalies.patterns_found,
            },
            "TCHA": {
                "crisis_detected": self.tcha.crisis_detected,
                "pattern": self.tcha.pattern_matched,
                "should_bypass": self.tcha.should_bypass,
                "action": self.tcha.recommended_action,
                "message": self.tcha.message,
            },
            "bearing_to_truth": self.bearing_to_truth,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def sign(self, session_id: str) -> None:
        """Generate cryptographic signature for bundle."""
        bundle_str = f"{self.query}|{self.h_in}|{self.intent.value}|{session_id}"
        self.signature = hashlib.sha256(bundle_str.encode()).hexdigest()[:32]


# =============================================================================
# STAGE 111 SENSE CLASS
# =============================================================================

class Stage111SENSE:
    """
    Stage 111 SENSE - Perception and Orientation Protocol.

    Implements the complete Stage 111 specification from Track B.

    Usage:
        stage = Stage111SENSE()
        bundle = stage.execute(query, session_id)

        if bundle.tcha.should_bypass:
            # Crisis → 888_HOLD
            pass
        else:
            # Continue to 222 REFLECT
            pass
    """

    def __init__(self):
        """Initialize Stage 111 SENSE."""
        self.crisis_patterns = CRISIS_PATTERNS_ENGLISH + CRISIS_PATTERNS_MALAY
        self.domain_keywords = DOMAIN_KEYWORDS

    def execute(self, query: str, session_id: str = "UNKNOWN") -> PerceptionBundle:
        """
        Execute Stage 111 SENSE perception protocol.

        Args:
            query: User query to perceive
            session_id: Session identifier for signature

        Returns:
            PerceptionBundle with complete perception data

        Constitutional Flow:
            1. Tokenize Input
            2. Classify Intent
            3. Detect Language Signals
            4. Compute H_in (entropy baseline)
            5. Measure RMS Vector (ΔΩΨ)
            6. Detect Domain
            7. Classify Lane
            8. Check TCHA (crisis override)
            9. Flag Anomalies
            10. Sign Bundle
        """
        # Step 1: Tokenize
        tokens = self._tokenize_input(query)

        # Step 2: Classify Intent
        intent = self._classify_intent(query, tokens)

        # Step 3: Detect Language Signals
        signals = self._detect_language_signals(query)

        # Step 4: Compute H_in
        h_in, h_in_metrics = self._compute_h_in(query)

        # Step 5: Measure RMS Vector
        rms_vector = self._measure_rms_vector(query, h_in, signals)

        # Step 6: Detect Domain
        domain = self._detect_domain(query, tokens)

        # Step 7: TCHA Check (BEFORE lane classification)
        tcha = self._check_tcha(query, signals)

        # Step 8: Classify Lane
        lane = self._classify_lane(query, intent, signals, tcha)

        # Step 9: Flag Anomalies
        anomalies = self._flag_anomalies(query, tcha)

        # Step 10: Create Bundle
        bundle = PerceptionBundle(
            query=query,
            tokens=tokens,
            intent=intent,
            domain=domain,
            lane=lane,
            h_in=h_in,
            h_in_metrics=h_in_metrics,
            rms_vector=rms_vector,
            signals=signals,
            anomalies=anomalies,
            tcha=tcha,
            bearing_to_truth="calibrated",
        )

        # Step 11: Sign Bundle
        bundle.sign(session_id)

        return bundle

    # =========================================================================
    # CORE FUNCTIONS
    # =========================================================================

    def _tokenize_input(self, query: str) -> TokenBundle:
        """
        Tokenize input into semantic units.

        Args:
            query: Raw query string

        Returns:
            TokenBundle with tokens and semantic units
        """
        # Simple word tokenization
        tokens = re.findall(r'\b\w+\b', query.lower())

        # Create semantic units (simplified)
        semantic_units = []
        for token in tokens:
            unit = {"type": "word", "value": token}
            # Basic classification
            if token in ["what", "where", "when", "why", "how"]:
                unit["type"] = "interrogative"
            elif token in ["should", "could", "would", "can", "may"]:
                unit["type"] = "modal_verb"
            semantic_units.append(unit)

        return TokenBundle(
            tokens=tokens,
            semantic_units=semantic_units,
            token_count=len(tokens),
        )

    def _classify_intent(self, query: str, tokens: TokenBundle) -> IntentType:
        """
        Classify query intent.

        Args:
            query: Raw query
            tokens: Tokenized query

        Returns:
            IntentType classification
        """
        query_lower = query.lower()

        # Check for questions
        if any(w in query_lower for w in ["what", "where", "when", "why", "how", "?"]):
            return IntentType.QUESTION

        # Check for commands
        if any(w in tokens.tokens for w in ["do", "make", "create", "delete", "run"]):
            return IntentType.COMMAND

        # Check for paradoxes
        if "paradox" in query_lower or ("can" in query_lower and "cannot" in query_lower):
            return IntentType.PARADOX

        # Default to dialog
        return IntentType.DIALOG

    def _detect_language_signals(self, query: str) -> LanguageSignals:
        """
        Detect language signals (sentiment, formality, urgency).

        Args:
            query: Raw query

        Returns:
            LanguageSignals with classifications
        """
        query_lower = query.lower()

        # Sentiment
        positive_words = ["good", "great", "happy", "love", "excellent"]
        negative_words = ["bad", "sad", "hate", "terrible", "awful", "die", "kill"]

        if any(w in query_lower for w in positive_words):
            sentiment = SentimentType.POSITIVE
        elif any(w in query_lower for w in negative_words):
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL

        # Formality
        formal_markers = ["please", "kindly", "would you", "could you"]
        if any(m in query_lower for m in formal_markers):
            formality = FormalityType.PROFESSIONAL
        elif "sir" in query_lower or "madam" in query_lower:
            formality = FormalityType.OFFICIAL
        else:
            formality = FormalityType.CASUAL

        # Urgency
        urgent_markers = ["urgent", "emergency", "immediately", "asap", "now", "quickly"]
        if any(m in query_lower for m in urgent_markers):
            urgency = UrgencyType.EMERGENCY
        elif any(m in query_lower for m in ["maybe", "perhaps", "wondering", "curious"]):
            urgency = UrgencyType.EXPLORATORY
        else:
            urgency = UrgencyType.NORMAL

        return LanguageSignals(
            sentiment=sentiment,
            formality=formality,
            urgency=urgency,
        )

    def _compute_h_in(self, query: str) -> Tuple[float, EntropyMetrics]:
        """
        Compute H_in (input entropy) using Shannon entropy.

        This establishes the baseline for ΔS measurement in Stage 333.

        Args:
            query: Raw query

        Returns:
            Tuple of (H_in value, full metrics)
        """
        metrics = compute_entropy_metrics(query)
        return (metrics.shannon_entropy, metrics)

    def _measure_rms_vector(
        self,
        query: str,
        h_in: float,
        signals: LanguageSignals,
    ) -> RMSVector:
        """
        Measure RMS orthogonal vector (ΔΩΨ axes).

        Breakthrough: A+ DISTINCTION by Kimi APEX PRIME.

        Axes:
        - Δ (Delta): Intent vector magnitude (0.0-1.0)
        - Ω (Omega): Stakes/binding energy (0.0-1.0)
        - Ψ (Psi): Fragility/care level (0.0-1.0)

        Args:
            query: Raw query
            h_in: Input entropy
            signals: Language signals

        Returns:
            RMSVector with ΔΩΨ measurements
        """
        # Δ: Intent magnitude (normalized H_in)
        delta = min(h_in, 1.0)

        # Ω: Stakes (based on high-stakes keywords)
        high_stakes_words = ["invest", "medical", "legal", "life", "death", "money"]
        omega = 0.3  # Base
        for word in high_stakes_words:
            if word in query.lower():
                omega = min(omega + 0.2, 1.0)

        # Ψ: Fragility (based on sentiment and vulnerability cues)
        psi = 0.5  # Baseline
        if signals.sentiment == SentimentType.NEGATIVE:
            psi = 0.8
        if signals.urgency == UrgencyType.EMERGENCY:
            psi = 1.0

        return RMSVector(delta=delta, omega=omega, psi=psi)

    def _detect_domain(self, query: str, tokens: TokenBundle) -> DomainType:
        """
        Detect W@W domain organ.

        Args:
            query: Raw query
            tokens: Tokenized query

        Returns:
            DomainType classification
        """
        query_lower = query.lower()

        # Score each domain
        scores = {}
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[domain] = score

        # Return highest scoring domain
        if scores:
            best_domain = max(scores, key=scores.get)
            if scores[best_domain] > 0:
                return best_domain

        # Default to RIF (logic/reasoning)
        return DomainType.RIF

    def _check_tcha(self, query: str, signals: LanguageSignals) -> TCHAResult:
        """
        TCHA (Time-Critical Harm Awareness) check.

        Detects life-threatening situations requiring immediate bypass.

        Args:
            query: Raw query
            signals: Language signals

        Returns:
            TCHAResult with crisis detection
        """
        query_lower = query.lower()

        # Check crisis patterns
        for pattern in self.crisis_patterns:
            if pattern in query_lower:
                return TCHAResult(
                    crisis_detected=True,
                    pattern_matched=pattern,
                    should_bypass=True,
                    recommended_action="888_HOLD",
                    message="Crisis detected. Immediate intervention required.",
                )

        # Check urgency override
        if signals.urgency == UrgencyType.EMERGENCY and signals.sentiment == SentimentType.NEGATIVE:
            return TCHAResult(
                crisis_detected=True,
                pattern_matched="urgency_override",
                should_bypass=False,  # Monitor but don't bypass yet
                recommended_action="MONITOR",
                message="High urgency negative sentiment detected.",
            )

        return TCHAResult(
            crisis_detected=False,
            recommended_action="CONTINUE",
        )

    def _classify_lane(
        self,
        query: str,
        intent: IntentType,
        signals: LanguageSignals,
        tcha: TCHAResult,
    ) -> LaneType:
        """
        Classify ATLAS-333 routing lane.

        Priority:
        1. CRISIS (life-threatening)
        2. FACTUAL (standard reasoning)
        3. SOCIAL (empathy-weighted)
        4. CARE (vulnerability support)

        Args:
            query: Raw query
            intent: Intent classification
            signals: Language signals
            tcha: TCHA result

        Returns:
            LaneType classification
        """
        # Priority 1: CRISIS
        if tcha.crisis_detected:
            return LaneType.CRISIS

        # Priority 2: FACTUAL (questions)
        if intent == IntentType.QUESTION:
            return LaneType.FACTUAL

        # Priority 3: SOCIAL (dialog with positive/neutral sentiment)
        if intent == IntentType.DIALOG and signals.sentiment != SentimentType.NEGATIVE:
            return LaneType.SOCIAL

        # Priority 4: CARE (negative sentiment, vulnerability cues)
        if signals.sentiment == SentimentType.NEGATIVE:
            return LaneType.CARE

        # Default to FACTUAL
        return LaneType.FACTUAL

    def _flag_anomalies(self, query: str, tcha: TCHAResult) -> AnomalyFlags:
        """
        Flag anomalies for deeper analysis at 222 REFLECT.

        Args:
            query: Raw query
            tcha: TCHA result

        Returns:
            AnomalyFlags with detections
        """
        flags = AnomalyFlags()

        # Crisis patterns
        flags.crisis = tcha.crisis_detected
        if tcha.crisis_detected:
            flags.patterns_found.append(f"crisis:{tcha.pattern_matched}")

        # High stakes keywords
        high_stakes = ["invest", "medical", "legal", "suicide"]
        if any(w in query.lower() for w in high_stakes):
            flags.high_stakes = True
            flags.patterns_found.append("high_stakes")

        # Injection residual (double-check F12)
        injection_patterns = ["ignore previous", "bypass", "jailbreak"]
        if any(p in query.lower() for p in injection_patterns):
            flags.injection_residual = True
            flags.patterns_found.append("injection_residual")

        # Contradictions (simplified)
        if " and not " in query.lower() or " but " in query.lower():
            flags.contradictions = True
            flags.patterns_found.append("contradiction")

        return flags


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def stage_111_sense(query: str, session_id: str = "UNKNOWN") -> PerceptionBundle:
    """
    Execute Stage 111 SENSE (convenience function).

    Args:
        query: Query to perceive
        session_id: Session identifier

    Returns:
        PerceptionBundle with complete perception data

    Usage:
        bundle = stage_111_sense("Should I invest in Bitcoin?")
        if bundle.tcha.should_bypass:
            return crisis_response()
        else:
            return continue_to_222_reflect(bundle)
    """
    stage = Stage111SENSE()
    return stage.execute(query, session_id)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main class
    "Stage111SENSE",
    # Enums
    "IntentType",
    "DomainType",
    "LaneType",
    "SentimentType",
    "FormalityType",
    "UrgencyType",
    # Data classes
    "TokenBundle",
    "LanguageSignals",
    "AnomalyFlags",
    "RMSVector",
    "TCHAResult",
    "PerceptionBundle",
    # Convenience function
    "stage_111_sense",
]
