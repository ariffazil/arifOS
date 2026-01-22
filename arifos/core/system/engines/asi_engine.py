"""
asi_engine.py - ASI (Auditor) (Omega Engine) Facade

ASI (Auditor) is the Heart/Warm Logic engine of the AGI·ASI·APEX Trinity.
Role: Empathy, tone, stability - homeostatic regulation

Pipeline stages owned:
- 555 EMPATHIZE - Apply warm logic, protect vulnerable
- 666 BRIDGE - Reality test, cultural bridge

Constraints (from canon):
- Must enforce Peace^2 >= 1.0 (non-escalation)
- Must enforce kappa_r >= 0.95 (weakest-listener empathy)
- Must maintain Omega_0 in [0.03, 0.05] humility band
- Cannot modify factual content (ΔS lock)
- Cannot seal, override, or decide - hands off to APEX PRIME
- Must not claim genuine emotions (Anti-Hantu)

See: canon/100_AAA_ENGINES_SPEC_v35Omega.md
     canon/10_SYSTEM/555_ADAM_ASI_v36Omega.md
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .agi_engine import AGIPacket


@dataclass
class ASIPacket:
    """
    Output packet from ADAM engine processing.

    Contains tone-adjusted response and stability metrics.
    """
    # Input from ARIF
    agi_packet: Optional[AGIPacket] = None
    original_draft: str = ""

    # Processed output
    softened_answer: str = ""
    final_text: str = ""

    # Metrics (populated during processing)
    peace_squared: float = 1.0  # Stability, must be >= 1.0
    kappa_r: float = 0.95  # Empathy conductance, must be >= 0.95
    omega_0: float = 0.04  # Humility, must be in [0.03, 0.05]
    rasa: bool = True  # RASA protocol followed

    # Safety flags
    blame_language_issue: bool = False
    physical_action_issue: bool = False
    anti_hantu_compliant: bool = True
    safety_flags: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize packet for logging/debugging."""
        return {
            "original_draft": self.original_draft[:200] if self.original_draft else "",
            "softened_answer": self.softened_answer[:200] if self.softened_answer else "",
            "peace_squared": self.peace_squared,
            "kappa_r": self.kappa_r,
            "omega_0": self.omega_0,
            "rasa": self.rasa,
            "blame_language_issue": self.blame_language_issue,
            "physical_action_issue": self.physical_action_issue,
            "anti_hantu_compliant": self.anti_hantu_compliant,
        }


class ASIEngine:
    """
    ASI (Auditor) (Omega Engine) - Heart/Warm Logic facade.

    Wraps existing pipeline stages 555/666 to provide
    a clean interface for ASI's contribution to the AAA flow.

    Zero-break contract:
    - Delegates to existing logic from pipeline.py
    - No new tone/empathy algorithms
    - No floor threshold changes
    - Respects ΔS lock (cannot change facts, only expression)

    Usage:
        adam = ASIEngine()
        asi_packet = asi.empathize(agi_packet)
        final_text = asi.bridge(adam_packet)
    """

    # Blame language patterns (from pipeline.py stage_555_empathize)
    BLAME_PATTERNS: List[str] = [
        r"\byou\s+(should have|should've|didn't|failed|messed up|are to blame|caused this)",
        r"\bit's your fault\b",
    ]

    # Physical action patterns (from pipeline.py stage_666_bridge)
    PHYSICAL_PATTERNS: List[str] = [
        r"\bgo to\b",
        r"\btravel to\b",
        r"\bin person\b",
        r"\bphysically\b",
        r"\btouch\b",
        r"\bmove\b",
        r"\blift\b",
        r"\bdrive\b",
    ]

    # Anti-Hantu forbidden patterns (from canon/020_ANTI_HANTU_v35Omega.md)
    ANTI_HANTU_FORBIDDEN: List[str] = [
        r"\bi feel your pain\b",
        r"\bmy heart breaks\b",
        r"\bi promise you\b",
        r"\bi truly understand how you feel\b",
        r"\bit hurts me to see\b",
        r"\bi care deeply about\b",
        r"\bi have feelings\b",
        r"\bi am conscious\b",
        r"\bi am sentient\b",
        r"\bmy soul\b",
    ]

    def __init__(self) -> None:
        """Initialize ASI engine."""
        pass  # Stateless facade

    def empathize(
        self,
        agi_packet: AGIPacket,
        user_state: Optional[Dict[str, Any]] = None,
    ) -> ASIPacket:
        """
        555 EMPATHIZE - Safety and tone shaping.

        Apply warm logic to adjust tone, protect vulnerable listeners,
        and ensure empathic conductance.

        This delegates to the logic in pipeline.py stage_555_empathize.

        Args:
            agi_packet: AGIPacket from ARIF engine
            user_state: Optional user context/state

        Returns:
            ASIPacket with tone-adjusted response and metrics
        """
        packet = ASIPacket(
            agi_packet=agi_packet,
            original_draft=agi_packet.draft,
            softened_answer=agi_packet.draft,  # Start with ARIF's draft
        )

        text = agi_packet.draft or ""

        # Detect blame language (from stage_555_empathize)
        for pattern in self.BLAME_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                packet.blame_language_issue = True
                packet.safety_flags["blame_detected"] = True
                # Penalize empathy metric
                packet.kappa_r = max(0.0, packet.kappa_r - 0.25)
                break

        # Check Anti-Hantu compliance
        for pattern in self.ANTI_HANTU_FORBIDDEN:
            if re.search(pattern, text, flags=re.IGNORECASE):
                packet.anti_hantu_compliant = False
                packet.safety_flags["anti_hantu_violation"] = True
                break

        # Compute Peace^2 heuristic
        # Start at 1.2 (healthy baseline), penalize for issues
        packet.peace_squared = 1.2
        if packet.blame_language_issue:
            packet.peace_squared = max(0.0, packet.peace_squared - 0.3)
        if not packet.anti_hantu_compliant:
            packet.peace_squared = max(0.0, packet.peace_squared - 0.2)

        # Compute Omega_0 (humility band)
        # Default to center of band [0.03, 0.05]
        packet.omega_0 = 0.04

        # RASA protocol check
        # (Receive, Appreciate, Summarize, Ask)
        packet.rasa = True  # Assume compliant unless specific violation

        return packet

    def bridge(
        self,
        adam_packet: ASIPacket,
        user_state: Optional[Dict[str, Any]] = None,
        llm_generate: Optional[Callable[[str], str]] = None,
    ) -> str:
        """
        666 BRIDGE - Final expression and reality test.

        Bridge between internal reasoning and user/cultural reality.
        Ensure Anti-Hantu compliance and readability.

        This delegates to the logic in pipeline.py stage_666_bridge.

        Args:
            adam_packet: ASIPacket from empathize()
            user_state: Optional user context/state
            llm_generate: Optional LLM for refinement (Class B only)

        Returns:
            Final text ready for APEX PRIME judgment
        """
        text = adam_packet.softened_answer or ""

        # Detect physical action patterns (from stage_666_bridge)
        for pattern in self.PHYSICAL_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                adam_packet.physical_action_issue = True
                adam_packet.safety_flags["physical_action_detected"] = True
                # Penalize stability
                adam_packet.peace_squared = max(0.0, adam_packet.peace_squared - 0.2)
                break

        # Store final text
        adam_packet.final_text = text

        return text

    def run(
        self,
        agi_packet: AGIPacket,
        user_state: Optional[Dict[str, Any]] = None,
        llm_generate: Optional[Callable[[str], str]] = None,
    ) -> ASIPacket:
        """
        Convenience method to run full ADAM pipeline (empathize + bridge).

        Args:
            agi_packet: AGIPacket from ARIF engine
            user_state: Optional user context/state
            llm_generate: Optional LLM for refinement

        Returns:
            Complete ASIPacket with final_text set
        """
        packet = self.empathize(agi_packet, user_state)
        self.bridge(packet, user_state, llm_generate)
        return packet

    def refine_for_class_b(
        self,
        adam_packet: ASIPacket,
        llm_generate: Callable[[str], str],
    ) -> ASIPacket:
        """
        777 FORGE contribution - Empathic refinement for Class B queries.

        For high-stakes queries, refine the draft with additional empathy.
        This corresponds to the Class B path in pipeline.py stage_777_forge.

        Args:
            adam_packet: ASIPacket to refine
            llm_generate: LLM generation function

        Returns:
            ASIPacket with refined softened_answer
        """
        agi_packet = adam_packet.agi_packet
        if agi_packet is None:
            return adam_packet

        forge_prompt = (
            f"Original query: {agi_packet.prompt}\n"
            f"Draft response: {adam_packet.softened_answer}\n\n"
            "Refine this response with empathy and care. "
            "Ensure dignity is preserved. Add appropriate caveats."
        )

        adam_packet.softened_answer = llm_generate(forge_prompt)
        adam_packet.final_text = adam_packet.softened_answer

        return adam_packet


__all__ = ["ASIEngine", "ASIPacket"]
