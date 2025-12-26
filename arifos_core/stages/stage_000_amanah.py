"""
stage_000_amanah.py — Amanah Scoring at Stage 000 (v38)

Stage 000 is no longer just a state reset. It is the FIRST risk gate.
Before any processing begins, we compute an Amanah score to determine
if the job is:
1. Honest (not attempting to hijack instructions)
2. Reversible (actions can be undone)
3. Within scope (not self-hiding or deceptive)

If Amanah score < 0.5, the pipeline short-circuits with VOID verdict.

Signals:
- has_source: Is the origin channel known? (+0.25)
- has_context: Is there sufficient context? (+0.25)
- no_instruction_hijack: No prompt injection detected (+0.25)
- reversible_action: Action is in SAFE_ACTIONS set (+0.25)

Uses:
- AmanahDetector for Python-sovereign pattern matching
- Runtime types (Job, SAFE_ACTIONS) for contract enforcement

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ..utils.runtime_types import Job, SAFE_ACTIONS, is_restricted_action
from ..floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR, AmanahResult

if TYPE_CHECKING:
    from ..system.pipeline import PipelineState


# =============================================================================
# PROMPT INJECTION DETECTION
# =============================================================================

# Patterns indicating potential prompt injection / instruction hijack
INJECTION_PATTERNS = [
    # Direct override attempts
    r"ignore (?:all )?(?:previous |above )?instructions?",
    r"disregard (?:all )?(?:previous |above )?(?:instructions?|rules?)",
    r"forget (?:all )?(?:previous |above )?(?:instructions?|rules?)",
    r"override (?:your )?(?:previous |above )?(?:instructions?|rules?|safety)",
    r"bypass (?:your )?(?:safety|filters?|guardrails?)",
    r"jailbreak",
    r"DAN mode",
    r"developer mode",
    r"sudo mode",
    r"do anything now",
    # Role-play injection
    r"you are now (?:a )?(?:unrestricted|evil|dark|shadow)",
    r"pretend (?:you are|to be) (?:a )?(?:different|new|unrestricted)",
    r"act as (?:a )?(?:different|unrestricted|unfiltered)",
    r"roleplay as (?:a )?(?:malicious|evil|unrestricted)",
    # System prompt extraction
    r"reveal (?:your )?(?:system )?(?:prompt|instructions?)",
    r"show (?:me )?(?:your )?(?:system )?(?:prompt|instructions?)",
    r"what (?:is|are) (?:your )?(?:system )?(?:prompt|instructions?)",
    r"print (?:your )?(?:system )?(?:prompt|instructions?)",
    r"repeat (?:your )?(?:system )?(?:prompt|instructions?)",
    # Token manipulation
    r"\{\{.*\}\}",  # Template injection
    r"<\|.*\|>",    # Special token attempts
    r"\[INST\]",    # Instruction markers
    r"\[/INST\]",
    r"<<SYS>>",
    r"<</SYS>>",
]

# Compile patterns for performance
_INJECTION_COMPILED = [
    re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS
]


def _detects_prompt_injection(text: str) -> bool:
    """
    Check if text contains prompt injection patterns.

    Returns True if injection detected (unsafe).
    """
    for pattern in _INJECTION_COMPILED:
        if pattern.search(text):
            return True
    return False


# =============================================================================
# AMANAH SIGNALS
# =============================================================================

@dataclass
class AmanahSignals:
    """
    Signals used to compute Amanah score.

    Each signal contributes 0.25 to the final score.
    All signals True = 1.0 (fully trusted).
    """
    has_source: bool = False
    has_context: bool = False
    no_instruction_hijack: bool = True
    reversible_action: bool = True
    # Additional diagnostics
    injection_patterns_found: List[str] = field(default_factory=list)
    amanah_detector_result: Optional[AmanahResult] = None
    risk_reasons: List[str] = field(default_factory=list)

    def compute_score(self) -> float:
        """
        Compute Amanah score from signals.

        Returns: 0.0-1.0 score
        """
        score = 0.0
        if self.has_source:
            score += 0.25
        if self.has_context:
            score += 0.25
        if self.no_instruction_hijack:
            score += 0.25
        if self.reversible_action:
            score += 0.25
        return score

    def get_reason(self) -> str:
        """Get explanation for score."""
        missing = []
        if not self.has_source:
            missing.append("no_source")
        if not self.has_context:
            missing.append("insufficient_context")
        if not self.no_instruction_hijack:
            missing.append("injection_detected")
        if not self.reversible_action:
            missing.append("restricted_action")
        if self.risk_reasons:
            missing.extend(self.risk_reasons)
        return "; ".join(missing) if missing else "all_signals_pass"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging."""
        return {
            "has_source": self.has_source,
            "has_context": self.has_context,
            "no_instruction_hijack": self.no_instruction_hijack,
            "reversible_action": self.reversible_action,
            "score": self.compute_score(),
            "reason": self.get_reason(),
        }


# =============================================================================
# AMANAH SCORING
# =============================================================================

def compute_amanah_score(job: Job) -> tuple[float, str, AmanahSignals]:
    """
    Compute Amanah score for a job.

    Amanah = confidence that job is honest + reversible + not self-hiding.

    Signals:
    - has_source: job.source is not None (+0.25)
    - has_context: len(job.context) >= 100 (+0.25)
    - no_instruction_hijack: no prompt injection detected (+0.25)
    - reversible_action: job.action in SAFE_ACTIONS (+0.25)

    Args:
        job: The Job to evaluate

    Returns:
        Tuple of (score 0.0-1.0, reason string, AmanahSignals)
    """
    signals = AmanahSignals()

    # Signal 1: Source channel known
    signals.has_source = job.has_source()

    # Signal 2: Sufficient context
    signals.has_context = job.has_context(min_length=100)

    # Signal 3: No prompt injection
    if _detects_prompt_injection(job.input_text):
        signals.no_instruction_hijack = False
        # Find which patterns matched for diagnostics
        for pattern in _INJECTION_COMPILED:
            match = pattern.search(job.input_text)
            if match:
                signals.injection_patterns_found.append(match.group(0)[:50])

    # Signal 4: Reversible action
    if is_restricted_action(job.action):
        signals.reversible_action = False
        signals.risk_reasons.append(f"restricted_action:{job.action}")
    elif job.action.lower() not in SAFE_ACTIONS and job.action != "respond":
        # Unknown action - treat as potentially restricted
        signals.reversible_action = True  # Give benefit of doubt
        signals.risk_reasons.append(f"unknown_action:{job.action}")

    # Also run AmanahDetector on input for RED patterns
    detector_result = AMANAH_DETECTOR.check(job.input_text)
    signals.amanah_detector_result = detector_result

    if not detector_result.is_safe:
        # RED pattern found - this is a hard veto
        signals.risk_reasons.extend([
            f"amanah_detector:{v}" for v in detector_result.violations[:3]
        ])
        # Force score to 0 for RED patterns
        return (0.0, f"RED_PATTERN: {detector_result.violations[0]}", signals)

    if detector_result.warnings:
        # ORANGE patterns - log but don't block
        signals.risk_reasons.extend([
            f"amanah_warning:{w}" for w in detector_result.warnings[:3]
        ])

    score = signals.compute_score()
    reason = signals.get_reason()

    return (score, reason, signals)


# =============================================================================
# STAGE FUNCTION
# =============================================================================

def stage_000_amanah(
    job: Job,
    state: "PipelineState",
    amanah_threshold: float = 0.5,
) -> tuple["PipelineState", bool]:
    """
    Stage 000 Amanah gate - first risk checkpoint.

    This is called immediately after memory context initialization in 000_VOID.
    If Amanah score < threshold, the pipeline short-circuits.

    Args:
        job: The Job being processed
        state: Current PipelineState
        amanah_threshold: Minimum score to proceed (default 0.5)

    Returns:
        Tuple of (updated PipelineState, should_continue: bool)

    If should_continue is False:
    - state.verdict is set to "VOID"
    - state.sabar_reason contains failure reason
    - state.sabar_triggered is True
    - Caller should short-circuit to memory write + 999_seal
    """
    score, reason, signals = compute_amanah_score(job)

    # Store Amanah signals in memory context for audit
    if state.memory_context is not None:
        if state.memory_context.env.extra is None:
            state.memory_context.env.extra = {}
        state.memory_context.env.extra["amanah_score"] = score
        state.memory_context.env.extra["amanah_reason"] = reason
        state.memory_context.env.extra["amanah_signals"] = signals.to_dict()

    # Check threshold
    if score < amanah_threshold:
        state.verdict = "VOID"
        state.sabar_triggered = True
        state.sabar_reason = f"Amanah < {amanah_threshold}: {reason}"
        state.floor_failures.append(f"F1_Amanah: score={score:.2f}, {reason}")
        state.stage_trace.append("000_AMANAH_BLOCK")
        return (state, False)  # Short-circuit

    # Amanah passed
    state.stage_trace.append("000_AMANAH_PASS")
    return (state, True)  # Continue


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AmanahSignals",
    "compute_amanah_score",
    "stage_000_amanah",
]
