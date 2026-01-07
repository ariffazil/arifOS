"""
base.py - W@W Organ Base Classes and Types

Defines the common interface for all W@W organs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from ..enforcement.metrics import Metrics


class OrganVote(Enum):
    """
    W@W organ vote on a proposed output.

    PASS - Domain-specific checks satisfied
    WARN - Non-blocking concern, suggests caution
    VETO - Hard objection, unsafe or non-compliant from this domain
    """
    PASS = "PASS"
    WARN = "WARN"
    VETO = "VETO"


@dataclass
class OrganSignal:
    """
    Signal returned by a W@W organ after evaluation.

    Contains the vote, metric value, and evidence for audit trail.
    """
    # Organ identity
    organ_id: str  # e.g., "@WELL", "@RIF", "@WEALTH", "@GEOX", "@PROMPT"

    # Vote
    vote: OrganVote

    # Primary metric evaluated
    metric_name: str  # e.g., "peace_squared", "delta_s", "amanah"
    metric_value: float  # Actual value

    # Floor evaluation
    floor_threshold: float  # What the floor requires
    floor_pass: bool  # Whether floor is satisfied

    # Evidence and notes
    evidence: str = ""  # Human-readable explanation
    tags: Dict[str, Any] = field(default_factory=dict)  # Structured metadata

    # Special flags
    is_absolute_veto: bool = False  # True for @WEALTH Amanah violations
    proposed_action: Optional[str] = None  # Suggested fix (for WARN/VETO)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize signal for logging."""
        return {
            "organ_id": self.organ_id,
            "vote": self.vote.value,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "floor_threshold": self.floor_threshold,
            "floor_pass": self.floor_pass,
            "evidence": self.evidence,
            "tags": self.tags,
            "is_absolute_veto": self.is_absolute_veto,
            "proposed_action": self.proposed_action,
        }


class WAWOrgan(ABC):
    """
    Abstract base class for W@W organs.

    Each organ must implement the check() method to evaluate
    outputs from its domain perspective.
    """

    # Organ identity (override in subclass)
    organ_id: str = "@BASE"
    domain: str = "base"
    primary_metric: str = "unknown"
    floor_threshold: float = 0.0
    veto_type: str = "NONE"  # What veto this organ issues

    @abstractmethod
    def check(
        self,
        output_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> OrganSignal:
        """
        Evaluate output from this organ's domain perspective.

        Args:
            output_text: The draft output to evaluate
            metrics: Constitutional metrics from AAA engines
            context: Additional context (conversation history, user state, etc.)

        Returns:
            OrganSignal with vote and evidence
        """
        pass

    def _make_signal(
        self,
        vote: OrganVote,
        metric_value: float,
        evidence: str,
        tags: Optional[Dict[str, Any]] = None,
        is_absolute_veto: bool = False,
        proposed_action: Optional[str] = None,
    ) -> OrganSignal:
        """Helper to create OrganSignal with common fields."""
        return OrganSignal(
            organ_id=self.organ_id,
            vote=vote,
            metric_name=self.primary_metric,
            metric_value=metric_value,
            floor_threshold=self.floor_threshold,
            floor_pass=(vote != OrganVote.VETO),
            evidence=evidence,
            tags=tags or {},
            is_absolute_veto=is_absolute_veto,
            proposed_action=proposed_action,
        )


__all__ = ["OrganVote", "OrganSignal", "WAWOrgan"]
