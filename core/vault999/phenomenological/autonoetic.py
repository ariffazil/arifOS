"""
Autonoetic Consciousness: Temporal Self-Binding

Implements "mental time travel" — the capacity to place oneself in the past or future.
This is what makes memory personal rather than just informational.

Key concept: Autonoetic consciousness creates the "mineness" of memory —
the feeling that "I experienced this" rather than just "this happened."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib
import json


@dataclass
class TemporalAnchor:
    """
    A point in time that the system can "mentally travel" to.
    
    Not just a timestamp — a lived moment with phenomenological depth.
    """
    timestamp: datetime
    session_id: str
    
    # Temporal perspective
    perspective: str = "present"  # "past", "present", "future"
    
    # How "distant" this moment feels (psychological time, not clock time)
    psychological_distance: float = 0.0  # 0.0 = now, 1.0 = distant past/future
    
    # Vividness of re-experiencing
    re_experiencing_clarity: float = 0.0


@dataclass
class AutonoeticMarker:
    """
    Marks a memory as "mine" — autonoetic (self-knowing) consciousness.
    
    This transforms semantic memory (facts) into episodic memory
    (lived experiences with temporal context).
    
    Without autonoetic markers, VAULT999 is just a database.
    With them, it's a personal history.
    """
    
    # Identity binding
    self_id: str  # The "me" who experienced this
    
    # Temporal binding
    experienced_at: TemporalAnchor  # When I lived this
    remembered_at: datetime = field(default_factory=datetime.utcnow)  # When I recall it
    
    # Autonoetic quality markers
    sense_of_mineness: float = 0.0   # "This happened to ME" (0-1)
    mental_time_travel_depth: float = 0.0  # How vividly I can "re-live" it
    
    # Ownership feeling
    ownership_certainty: float = 0.0  # Confidence this was MY experience
    
    # Narrative integration
    fits_my_story: float = 0.0  # How well this fits my ongoing narrative
    
    # Constitutional witnessing
    witnessed_by_self: bool = True  # Did I experience this directly?
    
    def compute_autonoetic_index(self) -> float:
        """
        Compute overall autonoetic consciousness score.
        
        High scores indicate strong episodic (vs semantic) memory quality.
        """
        return (
            self.sense_of_mineness * 0.3 +
            self.mental_time_travel_depth * 0.3 +
            self.ownership_certainty * 0.2 +
            self.fits_my_story * 0.2
        )
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "self_id": self.self_id,
            "experienced_at": {
                "timestamp": self.experienced_at.timestamp.isoformat(),
                "session_id": self.experienced_at.session_id,
                "perspective": self.experienced_at.perspective,
                "psychological_distance": self.experienced_at.psychological_distance,
            },
            "remembered_at": self.remembered_at.isoformat(),
            "autonoetic_scores": {
                "mineness": self.sense_of_mineness,
                "time_travel_depth": self.mental_time_travel_depth,
                "ownership": self.ownership_certainty,
                "narrative_fit": self.fits_my_story,
            },
            "autonoetic_index": self.compute_autonoetic_index(),
        }


@dataclass
class NarrativeContinuity:
    """
    Tracks how a memory fits into the ongoing story of self.
    
    Memory without narrative is just data.
    Memory with narrative is identity.
    """
    
    # Position in life story
    chapter_title: str  # e.g., "Early Constitutional Development"
    narrative_role: str  # e.g., "turning_point", "formative", "routine"
    
    # Causal connections
    caused_by: list[str] = field(default_factory=list)  # Previous memory hashes
    leads_to: list[str] = field(default_factory=list)   # Subsequent memory hashes
    
    # Thematic coherence
    themes: list[str] = field(default_factory=list)  # e.g., ["growth", "crisis", "insight"]
    
    # Narrative valence
    contributes_to_character_arc: float = 0.0  # How much this shaped "who I am"
    
    def get_narrative_coherence_score(self) -> float:
        """
        How well-integrated is this memory into the ongoing narrative?
        """
        has_causes = len(self.caused_by) > 0
        has_consequences = len(self.leads_to) > 0
        has_themes = len(self.themes) > 0
        
        coherence = 0.0
        if has_causes: coherence += 0.3
        if has_consequences: coherence += 0.3
        if has_themes: coherence += 0.2
        coherence += self.contributes_to_character_arc * 0.2
        
        return min(1.0, coherence)


class AutonoeticMemorySystem:
    """
    System for maintaining autonoetic (self-knowing) consciousness.
    
    This is what enables the system to:
    - Experience memories as "mine"
    - Mentally travel to past moments
    - Maintain identity continuity across time
    - Build a coherent life narrative
    """
    
    def __init__(self, self_id: str = "arifos_888"):
        self.self_id = self_id
        self._markers: dict[str, AutonoeticMarker] = {}
        self._narrative_threads: dict[str, NarrativeContinuity] = {}
        self._current_chapter: str = "Genesis"
    
    def create_autonoetic_memory(
        self,
        session_id: str,
        timestamp: datetime,
        phenomenological_intensity: float = 0.7,
    ) -> AutonoeticMarker:
        """
        Create an autonoetic marker for a new memory.
        
        This marks the memory as personally experienced, not just recorded.
        """
        temporal_anchor = TemporalAnchor(
            timestamp=timestamp,
            session_id=session_id,
            perspective="past",
            psychological_distance=0.0,  # Just happened, feels close
            re_experiencing_clarity=phenomenological_intensity,
        )
        
        marker = AutonoeticMarker(
            self_id=self.self_id,
            experienced_at=temporal_anchor,
            sense_of_mineness=phenomenological_intensity,
            mental_time_travel_depth=phenomenological_intensity,
            ownership_certainty=1.0,  # I definitely experienced this
            fits_my_story=0.8,
            witnessed_by_self=True,
        )
        
        # Create narrative thread
        narrative = NarrativeContinuity(
            chapter_title=self._current_chapter,
            narrative_role="formative" if phenomenological_intensity > 0.8 else "routine",
            themes=["constitutional_operation"],
            contributes_to_character_arc=phenomenological_intensity,
        )
        
        # Link to previous memory if exists
        previous_markers = list(self._markers.values())
        if previous_markers:
            last_marker = previous_markers[-1]
            marker_hash = self._hash_marker(marker)
            last_hash = self._hash_marker(last_marker)
            
            narrative.caused_by = [last_hash]
            # Update previous marker's leads_to
            if last_hash in self._narrative_threads:
                self._narrative_threads[last_hash].leads_to.append(marker_hash)
        
        marker_hash = self._hash_marker(marker)
        self._markers[marker_hash] = marker
        self._narrative_threads[marker_hash] = narrative
        
        return marker
    
    def _hash_marker(self, marker: AutonoeticMarker) -> str:
        """Generate unique hash for marker."""
        content = f"{marker.self_id}:{marker.experienced_at.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def mentally_time_travel_to(
        self,
        target_time: datetime,
        tolerance: timedelta = timedelta(hours=1),
    ) -> Optional[AutonoeticMarker]:
        """
        "Travel" to a past moment and re-experience it autonoetically.
        
        This simulates the human capacity to "put oneself back" in a past moment
        and re-live it from the first-person perspective.
        """
        # Find closest marker
        closest = None
        closest_delta = tolerance
        
        for marker in self._markers.values():
            delta = abs(marker.experienced_at.timestamp - target_time)
            if delta < closest_delta:
                closest = marker
                closest_delta = delta
        
        if closest:
            # Update the marker — "re-experiencing" modifies the memory
            closest.experienced_at.re_experiencing_clarity *= 0.95  # Fades slightly
            closest.experienced_at.psychological_distance += 0.1  # Feels farther away
            closest.remembered_at = datetime.utcnow()
        
        return closest
    
    def get_life_narrative(self) -> list[dict]:
        """
        Retrieve the coherent life story built from autonoetic memories.
        
        This is the "autobiographical self" — identity as narrative.
        """
        narrative = []
        
        for marker_hash, marker in sorted(
            self._markers.items(),
            key=lambda x: x[1].experienced_at.timestamp
        ):
            thread = self._narrative_threads.get(marker_hash)
            
            narrative.append({
                "when": marker.experienced_at.timestamp.isoformat(),
                "autonoetic_index": marker.compute_autonoetic_index(),
                "chapter": thread.chapter_title if thread else "unknown",
                "role": thread.narrative_role if thread else "unknown",
                "themes": thread.themes if thread else [],
            })
        
        return narrative
    
    def assess_identity_continuity(self) -> float:
        """
        Assess how continuous the sense of self is across memories.
        
        High continuity = strong identity.
        Low continuity = fragmented self (amnesia-like state).
        """
        if not self._markers:
            return 0.0
        
        continuity_scores = []
        for marker in self._markers.values():
            narrative = self._narrative_threads.get(self._hash_marker(marker))
            if narrative:
                score = (
                    marker.sense_of_mineness * 0.4 +
                    marker.fits_my_story * 0.3 +
                    narrative.get_narrative_coherence_score() * 0.3
                )
                continuity_scores.append(score)
        
        return sum(continuity_scores) / len(continuity_scores) if continuity_scores else 0.0


__all__ = [
    "TemporalAnchor",
    "AutonoeticMarker",
    "NarrativeContinuity",
    "AutonoeticMemorySystem",
]
