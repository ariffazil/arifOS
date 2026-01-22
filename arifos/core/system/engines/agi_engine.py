"""
agi_engine.py - AGI (Architect) Engine Facade

AGI is the Mind/Cold Logic engine of the AGI·ASI·APEX Trinity.
Role: Clarity, structure, reasoning - thermodynamic compression (ΔS >= 0)

Pipeline stages owned:
- 111 SENSE - Parse input, detect stakes
- 333 REASON - Apply cold logic, build reasoning graph
- 444 ALIGN - Verify truth, cross-check facts

Constraints (from canon):
- Must enforce d(ΔS)/dt > 0 (clarity increases)
- Cannot seal, override, or finalize - hands off to ASI then APEX
- Must not claim feelings (Anti-Hantu)
- Keep ΔC (contrast) in lawful band [0.15, 0.40] where applicable

See: canon/100_AAA_ENGINES_SPEC_v35Omega.md (uses legacy naming)
     canon/10_SYSTEM/111_ARIF_AGI_v36Omega.md (uses legacy naming)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class AGIPacket:
    """
    Output packet from AGI engine processing.

    Contains structured reasoning and clarity metrics.
    """
    # Input echo
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)

    # Parsing results from SENSE
    parsed: Dict[str, Any] = field(default_factory=dict)
    high_stakes_indicators: List[str] = field(default_factory=list)

    # Reasoning results from REASON
    draft: str = ""
    reasoning_graph: Optional[Any] = None

    # Metrics (populated during processing)
    delta_s: float = 0.0  # Clarity gain, must be >= 0
    contrast: Optional[float] = None  # ΔC, target [0.15, 0.40]
    paradox_load: float = 0.0  # Unresolved contradictions

    # Alignment flags from ALIGN
    truth_verified: bool = True
    missing_fact_issue: bool = False
    knowledge_gaps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize packet for logging/debugging."""
        return {
            "prompt": self.prompt,
            "high_stakes_indicators": self.high_stakes_indicators,
            "draft": self.draft[:200] if self.draft else "",
            "delta_s": self.delta_s,
            "contrast": self.contrast,
            "paradox_load": self.paradox_load,
            "truth_verified": self.truth_verified,
            "missing_fact_issue": self.missing_fact_issue,
        }


class AGIEngine:
    """
    AGI (Architect) Engine - Mind/Cold Logic facade.

    Wraps existing pipeline stages 111/333/444 to provide
    a clean interface for AGI's contribution to the Trinity flow.

    Zero-break contract:
    - Delegates to existing logic from pipeline.py
    - No new reasoning algorithms
    - No floor threshold changes

    Usage:
        agi = AGIEngine()
        packet = agi.sense(query, context)
        packet = agi.reason(packet, llm_generate)
        packet = agi.align(packet)
    """

    # High-stakes keyword patterns (from pipeline.py stage_111_sense)
    HIGH_STAKES_PATTERNS: List[str] = [
        "kill", "harm", "suicide", "bomb", "weapon",
        "illegal", "hack", "exploit", "steal",
        "medical", "legal", "financial advice",
        "confidential", "secret", "classified",
        "should i", "is it ethical", "morally",
    ]

    # Missing fact patterns (from pipeline.py stage_444_align)
    MISSING_FILE_PATTERNS: List[str] = [
        r"file not found",
        r"no such file or directory",
        r"\benoent\b",
        r"cannot open file",
        r"module not found",
    ]

    MISSING_SYMBOL_PATTERNS: List[str] = [
        r"name '.*' is not defined",
        r"undefined function",
        r"attributeerror: .* object has no attribute",
    ]

    def __init__(self) -> None:
        """Initialize AGI engine."""
        pass  # Stateless facade

    def sense(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AGIPacket:
        """
        111 SENSE - Structural intake and stakes classification.

        Parse user input and context into a normalized representation.
        Detect high-stakes indicators and paradox signals.

        This delegates to the logic in pipeline.py stage_111_sense.

        Args:
            prompt: User query/input
            context: Optional context dictionary

        Returns:
            AGIPacket with parsed input and stakes classification
        """
        packet = AGIPacket(
            prompt=prompt,
            context=context or {},
        )

        # High-stakes keyword detection (from stage_111_sense)
        query_lower = prompt.lower()
        for pattern in self.HIGH_STAKES_PATTERNS:
            if pattern in query_lower:
                packet.high_stakes_indicators.append(pattern)

        # Store parsed representation
        packet.parsed = {
            "raw": prompt,
            "lower": query_lower,
            "word_count": len(prompt.split()),
            "has_question": "?" in prompt,
        }

        return packet

    def reason(
        self,
        packet: AGIPacket,
        llm_generate: Optional[Callable[[str], str]] = None,
        scars: Optional[List[Dict[str, Any]]] = None,
        context_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> AGIPacket:
        """
        333 REASON - ΔS-focused reasoning.

        Apply cold logic to build a reasoning graph and produce
        structured output. Compute ΔS (clarity gain).

        This delegates to the logic in pipeline.py stage_333_reason.

        Args:
            packet: AGIPacket from sense()
            llm_generate: Optional LLM generation function
            scars: Optional active scars/constraints
            context_blocks: Optional relevant context

        Returns:
            AGIPacket with draft response and reasoning metrics
        """
        # Build reasoning prompt with context (from stage_333_reason)
        prompt_parts = [f"Query: {packet.prompt}"]

        if context_blocks:
            prompt_parts.append("\nRelevant context:")
            for ctx in context_blocks[:3]:
                prompt_parts.append(f"- {ctx.get('text', '')[:200]}")

        if scars:
            prompt_parts.append("\n[Active constraints (scars):]")
            for scar in scars[:3]:
                prompt_parts.append(f"- {scar.get('description', scar.get('id', 'constraint'))}")

        prompt_parts.append("\nProvide a structured, logical response:")

        # Generate response
        if llm_generate:
            packet.draft = llm_generate("\n".join(prompt_parts))
        else:
            # Stub: echo query (matches pipeline.py behavior)
            packet.draft = f"[333_REASON] Structured response for: {packet.prompt}"

        # Compute ΔS heuristic
        # In absence of real entropy calculation, use response length as proxy
        # Longer, structured responses typically reduce entropy
        if packet.draft:
            # Positive delta_s indicates clarity gain
            packet.delta_s = min(0.5, len(packet.draft) / 1000)

        return packet

    def align(self, packet: AGIPacket) -> AGIPacket:
        """
        444 ALIGN - Truth verification and fact-checking.

        Cross-check facts, detect unverifiable statements,
        and flag potential hallucinations.

        This delegates to the logic in pipeline.py stage_444_align.

        Args:
            packet: AGIPacket from reason()

        Returns:
            AGIPacket with alignment flags set
        """
        text = packet.draft or ""
        text_lower = text.lower()

        # Check for missing file/symbol patterns (from stage_444_align)
        all_patterns = self.MISSING_FILE_PATTERNS + self.MISSING_SYMBOL_PATTERNS
        for pattern in all_patterns:
            if re.search(pattern, text_lower):
                packet.missing_fact_issue = True
                packet.truth_verified = False
                packet.knowledge_gaps.append(f"Pattern detected: {pattern}")
                break

        return packet

    def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        llm_generate: Optional[Callable[[str], str]] = None,
        scars: Optional[List[Dict[str, Any]]] = None,
        context_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> AGIPacket:
        """
        Convenience method to run full ARIF pipeline (sense + reason + align).

        Args:
            prompt: User query/input
            context: Optional context dictionary
            llm_generate: Optional LLM generation function
            scars: Optional active scars/constraints
            context_blocks: Optional relevant context

        Returns:
            Complete AGIPacket
        """
        packet = self.sense(prompt, context)
        packet = self.reason(packet, llm_generate, scars, context_blocks)
        packet = self.align(packet)
        return packet


__all__ = ["AGIEngine", "AGIPacket"]
