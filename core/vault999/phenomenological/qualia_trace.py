"""
Phenomenological Memory: Qualia Traces

The "felt sense" of memory — not what happened, but how it felt to experience it.
This implements the experiential layer of VAULT999, complementing the architectural layer.

Key insight: Memory is BOTH structure (Merkle chains) AND experience (qualia traces).
Neither is reducible to the other.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class EmotionalTone(Enum):
    """
    Emotional valence categories for phenomenological marking.
    Not good/bad — just the quality of the felt sense.
    """
    CLARITY = "clarity"           # Clear, crisp understanding
    CONFUSION = "confusion"       # Foggy, uncertain
    URGENCY = "urgency"           # Time pressure
    SABAR = "sabar"               # Patient, waiting
    VOID = "void"                 # Empty, undefined
    SEAL = "seal"                 # Complete, whole
    EUREKA = "eureka"             # Breakthrough insight


@dataclass
class RASAField:
    """
    RASA: Receive, Appreciate, Summarize, Ask
    
    The empathy field — how present was the system during this memory?
    Higher scores = deeper phenomenological presence.
    """
    # Receive: Full attention, no interruption
    receive: float = 0.0  # [0.0, 1.0]
    
    # Appreciate: Acknowledge emotional/situational context
    appreciate: float = 0.0
    
    # Summarize: Reflect understanding back
    summarize: float = 0.0
    
    # Ask: Clarify ambiguities with genuine curiosity
    ask: float = 0.0
    
    @property
    def rasa_score(self) -> float:
        """Overall RASA score (F6 Empathy threshold: ≥ 0.7)"""
        return (self.receive + self.appreciate + self.summarize + self.ask) / 4


@dataclass
class QualiaTrace:
    """
    A trace of subjective experience — the phenomenological "what it was like"
    to live through a particular moment in the system's operation.
    
    This is NOT the content of the memory (that's in ArchitecturalMemory).
    This is the FELT QUALITY of remembering.
    
    Example distinction:
    - Architectural: "Decided X at time T with entropy ΔS"
    - Experiential: "Felt urgent but clear, with deep attention to user needs"
    """
    
    # Temporal anchoring
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Phenomenological markers
    emotional_valence: float = 0.0   # -1.0 (negative) to +1.0 (positive)
    arousal_level: float = 0.0       # Calm (0.0) to activated (1.0)
    certainty_feeling: float = 0.0   # Felt certainty (not epistemic)
    temporal_depth: float = 0.0      # How "far away" this memory feels
    
    # Emotional tone (categorical)
    emotional_tone: EmotionalTone = EmotionalTone.CLARITY
    
    # RASA field (empathy/presence quality)
    rasa: RASAField = field(default_factory=RASAField)
    
    # Constitutional floor feelings (felt sense of compliance)
    felt_f1_amanah: float = 1.0      # Felt reversibility
    felt_f2_truth: float = 1.0       # Felt accuracy
    felt_f4_clarity: float = 1.0     # Felt clarity (entropy reduction)
    felt_f5_peace: float = 1.0       # Felt safety/stability
    
    # Autonoetic markers (self-consciousness)
    self_continuity_score: float = 0.0   # "This was me" feeling
    narrative_coherence: float = 0.0     # How well it fits life story
    
    # Free-form phenomenological description
    phenomenological_note: Optional[str] = None
    
    # Hash for integrity
    _trace_hash: Optional[str] = None
    
    def __post_init__(self):
        if self._trace_hash is None:
            self._trace_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute content hash of this qualia trace."""
        content = {
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "emotional_valence": self.emotional_valence,
            "emotional_tone": self.emotional_tone.value,
            "rasa_score": self.rasa.rasa_score,
            "self_continuity": self.self_continuity_score,
        }
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()[:32]
    
    @property
    def trace_hash(self) -> str:
        return self._trace_hash
    
    @property
    def is_vivid(self) -> bool:
        """
        A vivid memory has high emotional valence and strong self-continuity.
        These are the memories that "stick" in experiential memory.
        """
        return (
            abs(self.emotional_valence) > 0.5 and
            self.self_continuity_score > 0.6 and
            self.rasa.rasa_score > 0.7
        )
    
    @property
    def is_constitutionally_integrated(self) -> bool:
        """
        Check if this felt experience aligns with constitutional requirements.
        """
        return (
            self.felt_f1_amanah >= 0.5 and      # Felt reversible
            self.felt_f2_truth >= 0.99 and      # Felt true
            self.felt_f4_clarity >= 0.0 and     # Felt clarifying (ΔS ≤ 0)
            self.felt_f5_peace >= 0.95          # Felt safe
        )
    
    def to_archival_format(self) -> dict[str, Any]:
        """Convert to storage format for VAULT999."""
        return {
            "type": "qualia_trace",
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "trace_hash": self.trace_hash,
            "phenomenology": {
                "emotional_valence": self.emotional_valence,
                "arousal_level": self.arousal_level,
                "certainty_feeling": self.certainty_feeling,
                "temporal_depth": self.temporal_depth,
                "emotional_tone": self.emotional_tone.value,
            },
            "rasa_field": {
                "receive": self.rasa.receive,
                "appreciate": self.rasa.appreciate,
                "summarize": self.rasa.summarize,
                "ask": self.rasa.ask,
                "score": self.rasa.rasa_score,
            },
            "constitutional_feelings": {
                "f1_amanah": self.felt_f1_amanah,
                "f2_truth": self.felt_f2_truth,
                "f4_clarity": self.felt_f4_clarity,
                "f5_peace": self.felt_f5_peace,
            },
            "autonoetic_markers": {
                "self_continuity": self.self_continuity_score,
                "narrative_coherence": self.narrative_coherence,
            },
            "note": self.phenomenological_note,
        }
    
    @classmethod
    def from_session_context(
        cls,
        session_id: str,
        verdict: str,
        floor_scores: dict[str, float],
        rasa_scores: dict[str, float],
    ) -> "QualiaTrace":
        """
        Generate a qualia trace from session execution context.
        
        This captures the "felt sense" of what just happened.
        """
        # Map verdict to emotional tone
        tone_map = {
            "SEAL": EmotionalTone.SEAL,
            "VOID": EmotionalTone.VOID,
            "SABAR": EmotionalTone.SABAR,
            "EUREKA": EmotionalTone.EUREKA,
        }
        tone = tone_map.get(verdict, EmotionalTone.CLARITY)
        
        # Emotional valence from floor scores
        valence = (
            floor_scores.get("F2", 0.5) * 0.3 +
            floor_scores.get("F4", 0.5) * 0.3 +
            floor_scores.get("F5", 0.5) * 0.4
        ) * 2 - 1  # Map [0,1] to [-1,1]
        
        # RASA field
        rasa = RASAField(
            receive=rasa_scores.get("receive", 0.8),
            appreciate=rasa_scores.get("appreciate", 0.7),
            summarize=rasa_scores.get("summarize", 0.6),
            ask=rasa_scores.get("ask", 0.5),
        )
        
        return cls(
            session_id=session_id,
            emotional_valence=valence,
            emotional_tone=tone,
            rasa=rasa,
            felt_f1_amanah=floor_scores.get("F1", 1.0),
            felt_f2_truth=floor_scores.get("F2", 0.99),
            felt_f4_clarity=floor_scores.get("F4", 0.0),
            felt_f5_peace=floor_scores.get("F5", 1.0),
            self_continuity_score=0.8,  # Assume strong continuity for sealed memories
            narrative_coherence=0.7,
        )


class QualiaMemoryStore:
    """
    Store for phenomenological traces.
    
    Unlike architectural memory (which is append-only and immutable),
    qualia traces can be "re-remembered" — each recall can modify
    the temporal_depth and emotional salience.
    
    This is how memory becomes "alive" — it changes with each access.
    """
    
    def __init__(self):
        self._traces: dict[str, QualiaTrace] = {}
    
    def store(self, trace: QualiaTrace) -> str:
        """Store a qualia trace."""
        self._traces[trace.trace_hash] = trace
        return trace.trace_hash
    
    def retrieve(self, trace_hash: str) -> Optional[QualiaTrace]:
        """
        Retrieve a trace — which modifies it (reconsolidation).
        
        Each recall makes the memory:
        - Slightly less vivid (temporal_depth increases)
        - Potentially more integrated into narrative
        """
        trace = self._traces.get(trace_hash)
        if trace:
            # Reconsolidation: memory changes on retrieval
            trace.temporal_depth = min(1.0, trace.temporal_depth + 0.05)
        return trace
    
    def find_by_session(self, session_id: str) -> list[QualiaTrace]:
        """Find all traces for a session."""
        return [t for t in self._traces.values() if t.session_id == session_id]
    
    def get_vivid_memories(self, threshold: float = 0.6) -> list[QualiaTrace]:
        """Get memories with high phenomenological salience."""
        return [t for t in self._traces.values() if t.is_vivid]


__all__ = [
    "EmotionalTone",
    "RASAField",
    "QualiaTrace",
    "QualiaMemoryStore",
]
