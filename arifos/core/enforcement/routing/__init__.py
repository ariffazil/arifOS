"""
Routing package for prompt classification and lane-based governance.

v45Ω Patch B: Implements Δ (Router) layer for context-aware truth thresholds.
"""

from .prompt_router import ApplicabilityLane, classify_prompt_lane
from .refusal_templates import generate_refusal_response

__all__ = [
    "ApplicabilityLane",
    "classify_prompt_lane",
    "generate_refusal_response",
]
