"""
L4_MCP Core Utilities Package.

Shared helper functions for the apex.verdict implementation.
All functions are internal and not exposed externally.
"""

from .classify import classify_action
from .identity import extract_caller
from .red_patterns import check_red_patterns
from .explain import generate_explanation
from .tri_witness import required_evidence_for
from .policy import policy_lookup_for

__all__ = [
    "classify_action",
    "extract_caller",
    "check_red_patterns",
    "generate_explanation",
    "required_evidence_for",
    "policy_lookup_for",
]
