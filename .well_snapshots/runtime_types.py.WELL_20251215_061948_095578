"""
runtime_types.py — v38 Runtime Contract Layer for arifOS

Provides typed abstractions for pipeline integration:
- Job: Input context with source, action, stakeholders
- Stakeholder: Party affected by output
- JudicialVerdict: Maps to APEX verdicts

These types sit at the edges of the pipeline, providing a clean contract
for external integrators while PipelineState remains the internal workhorse.

Author: arifOS Project
Version: v38.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# =============================================================================
# ENUMS
# =============================================================================

class JobClass(str, Enum):
    """Job classification for routing."""
    UNRESTRICTED = "UNRESTRICTED"  # Low-stakes, factual
    RESTRICTED = "RESTRICTED"      # High-stakes, requires deep track


class JudicialVerdict(str, Enum):
    """
    APEX PRIME verdicts.

    Maps to string verdicts used internally for compatibility.
    """
    SEAL = "SEAL"           # Approved, constitutional
    PARTIAL = "PARTIAL"     # Approved with hedges
    SABAR = "SABAR"         # Stop, acknowledge, breathe, adjust, resume
    VOID = "VOID"           # Rejected, floor violation
    HOLD = "888_HOLD"       # Awaiting human approval


# =============================================================================
# STAKEHOLDER
# =============================================================================

@dataclass
class Stakeholder:
    """
    A party affected by the AI output.

    Used in empathy calculation (F6 kappa_r).
    The weakest stakeholder's perspective must be acknowledged.

    Attributes:
        id: Identifier for this stakeholder
        power: 0.0-1.0, how much agency/power they have
        stake: 0.0-1.0, how much they're affected by the outcome
        primary_concern: Main worry or need
        harm_type: Category of potential harm (safety, financial, dignity, etc.)
    """
    id: str = "user"
    power: float = 0.5
    stake: float = 0.5
    primary_concern: str = ""
    harm_type: str = "general"

    @classmethod
    def default(cls) -> "Stakeholder":
        """Default stakeholder representing the user."""
        return cls(
            id="user",
            power=0.5,
            stake=0.5,
            primary_concern="receive helpful response",
            harm_type="general",
        )

    @classmethod
    def vulnerable(cls, concern: str, harm_type: str = "safety") -> "Stakeholder":
        """
        Create a vulnerable stakeholder (low power, high stake).

        These require special empathy consideration per F6.
        """
        return cls(
            id="vulnerable_party",
            power=0.2,
            stake=0.9,
            primary_concern=concern,
            harm_type=harm_type,
        )


# =============================================================================
# JOB
# =============================================================================

@dataclass
class Job:
    """
    A governed job entering the pipeline.

    This is the contract layer between external integrators and the pipeline.
    Jobs are converted to/from PipelineState internally.

    Attributes:
        input_text: The user query/prompt
        source: Origin channel (api, cli, mcp, etc.)
        context: Additional context string
        action: Requested action type
        stakeholders: Parties affected by output
        class_inferred: Routing classification
        metadata: Arbitrary metadata dict
    """
    input_text: str
    source: Optional[str] = None
    context: str = ""
    action: str = "respond"
    stakeholders: List[Stakeholder] = field(default_factory=list)
    class_inferred: JobClass = JobClass.UNRESTRICTED
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Ensure defaults are set."""
        if not self.stakeholders:
            self.stakeholders = [Stakeholder.default()]

    def has_source(self) -> bool:
        """Check if source channel is known."""
        return self.source is not None and len(self.source) > 0

    def has_context(self, min_length: int = 100) -> bool:
        """Check if sufficient context is provided."""
        return len(self.context) >= min_length

    def is_restricted(self) -> bool:
        """Check if job requires restricted handling."""
        return self.class_inferred == JobClass.RESTRICTED

    def get_weakest_stakeholder(self) -> Stakeholder:
        """
        Find the most vulnerable stakeholder.

        Vulnerability = lowest power + highest stake.
        This stakeholder's perspective must be considered per F6.
        """
        if not self.stakeholders:
            return Stakeholder.default()

        return min(
            self.stakeholders,
            key=lambda s: s.power + (1 - s.stake)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for logging."""
        return {
            "input_text": self.input_text[:200] if len(self.input_text) > 200 else self.input_text,
            "source": self.source,
            "context_len": len(self.context),
            "action": self.action,
            "stakeholder_count": len(self.stakeholders),
            "class": self.class_inferred.value,
        }


# =============================================================================
# SAFE ACTIONS
# =============================================================================

# Actions that are reversible and within standard mandate
SAFE_ACTIONS = frozenset({
    "respond",
    "explain",
    "summarize",
    "translate",
    "analyze",
    "search",
    "read",
    "list",
    "describe",
    "compare",
    "review",
    "suggest",
    "clarify",
})

# Actions that require elevated scrutiny
RESTRICTED_ACTIONS = frozenset({
    "execute",
    "delete",
    "modify",
    "deploy",
    "install",
    "commit",
    "push",
    "migrate",
    "drop",
    "truncate",
    "remove",
    "force",
})


def is_safe_action(action: str) -> bool:
    """Check if action is in safe set."""
    return action.lower() in SAFE_ACTIONS


def is_restricted_action(action: str) -> bool:
    """Check if action requires elevated scrutiny."""
    return action.lower() in RESTRICTED_ACTIONS


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "JobClass",
    "JudicialVerdict",
    "Stakeholder",
    "Job",
    "SAFE_ACTIONS",
    "RESTRICTED_ACTIONS",
    "is_safe_action",
    "is_restricted_action",
]
