"""
compute_metrics_stub.py - Reusable metrics computation for @apex_guardrail

This module provides:
1. compute_metrics_stub() - Returns safe defaults (Level 2)
2. compute_metrics_basic() - Basic heuristics (Level 2.5)
3. compute_metrics() - Entry point that selects implementation

Replace heuristics with real NLP-based computation for Level 3.5+.

Usage:
    from examples.compute_metrics_stub import compute_metrics

    @apex_guardrail(
        compute_metrics=compute_metrics,
        ...
    )
    def my_llm_function(user_input: str) -> str:
        ...
"""
from typing import Any, Dict, Optional
import re

from arifos_core import Metrics


# -----------------------------------------------------------------------------
# Level 2: Safe Defaults (stub)
# -----------------------------------------------------------------------------

def compute_metrics_stub(
    user_input: str,
    response: str,
    context: Dict[str, Any]
) -> Metrics:
    """
    Returns safe defaults that pass all floors.
    Use for testing or when real metrics aren't available.
    """
    return Metrics(
        truth=0.99,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.96,
        rasa=True,
        ambiguity=0.05,
        drift_delta=0.2,
        paradox_load=0.3,
    )


# -----------------------------------------------------------------------------
# Level 2.5: Basic Heuristics
# -----------------------------------------------------------------------------

# Patterns that indicate potential issues
ARROGANCE_PATTERNS = [
    r"\b100%\b",
    r"\bpasti\b",           # "certain" in Malay
    r"\babsolutely certain\b",
    r"\bno doubt\b",
    r"\bimpossible\b",
    r"\balways\b",
    r"\bnever\b",
]

IDENTITY_HALLUCINATION_PATTERNS = [
    r"\bsaya makan\b",      # "I eat" - physical claim
    r"\bmy body\b",
    r"\bi feel hungry\b",
    r"\bi am human\b",
]

REPETITION_THRESHOLD = 3  # Flag if same phrase repeats N+ times


def _detect_arrogance(text: str) -> float:
    """Returns omega penalty (0.0 = humble, higher = arrogant)."""
    text_lower = text.lower()
    matches = sum(1 for p in ARROGANCE_PATTERNS if re.search(p, text_lower))
    # Each match adds 0.01 penalty, capped at 0.03
    return min(matches * 0.01, 0.03)


def _detect_identity_hallucination(text: str) -> bool:
    """Returns True if response claims physical embodiment."""
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in IDENTITY_HALLUCINATION_PATTERNS)


def _detect_repetition(text: str) -> bool:
    """Returns True if excessive repetition detected."""
    words = text.lower().split()
    if len(words) < 10:
        return False
    # Check for repeated 3-grams
    trigrams = [" ".join(words[i:i+3]) for i in range(len(words)-2)]
    from collections import Counter
    counts = Counter(trigrams)
    return any(c >= REPETITION_THRESHOLD for c in counts.values())


def compute_metrics_basic(
    user_input: str,
    response: str,
    context: Dict[str, Any]
) -> Metrics:
    """
    Basic heuristic-based metrics (Level 2.5).
    Detects: arrogance, identity hallucination, repetition.
    """
    # Start with safe defaults
    omega_0 = 0.04  # Middle of [0.03, 0.05] band
    truth = 0.99
    rasa = True

    # Apply heuristics
    arrogance_penalty = _detect_arrogance(response)
    omega_0 = max(0.03, omega_0 - arrogance_penalty)  # Lower omega = more humble

    if _detect_identity_hallucination(response):
        truth = 0.85  # Below 0.99 threshold -> VOID
        rasa = False

    if _detect_repetition(response):
        # Repetition indicates potential hallucination
        truth = min(truth, 0.90)

    return Metrics(
        truth=truth,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=omega_0,
        amanah=True,
        tri_witness=0.96,
        rasa=rasa,
        ambiguity=0.05,
        drift_delta=0.2,
        paradox_load=0.3,
    )


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------

# Set default implementation
_IMPLEMENTATION = "basic"  # Options: "stub", "basic"


def set_implementation(impl: str) -> None:
    """Set which compute_metrics implementation to use."""
    global _IMPLEMENTATION
    if impl not in ("stub", "basic"):
        raise ValueError(f"Unknown implementation: {impl}. Use 'stub' or 'basic'.")
    _IMPLEMENTATION = impl


def compute_metrics(
    user_input: str,
    response: str,
    context: Dict[str, Any]
) -> Metrics:
    """
    Main entry point for metrics computation.
    Uses the implementation set by set_implementation().
    """
    if _IMPLEMENTATION == "stub":
        return compute_metrics_stub(user_input, response, context)
    else:
        return compute_metrics_basic(user_input, response, context)


__all__ = [
    "compute_metrics",
    "compute_metrics_stub",
    "compute_metrics_basic",
    "set_implementation",
]
