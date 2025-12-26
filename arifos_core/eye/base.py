"""
base.py - Base types for @EYE Sentinel views

Common types used across all EYE views:
- AlertSeverity: INFO / WARN / BLOCK
- EyeAlert: Single alert from a view
- EyeReport: Aggregated report from all views
- EyeView: Abstract base class for view implementations

See: canon/030_EYE_SENTINEL_v35Omega.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from ..enforcement.metrics import Metrics


class AlertSeverity(Enum):
    """Severity levels for @EYE alerts."""

    INFO = "INFO"  # Informational, no action required
    WARN = "WARN"  # Warning, proceed with caution
    BLOCK = "BLOCK"  # Blocking issue, must not SEAL → triggers SABAR


@dataclass
class EyeAlert:
    """A single alert from an @EYE view."""

    view_name: str
    severity: AlertSeverity
    message: str


@dataclass
class EyeReport:
    """Aggregated report from all @EYE views."""

    alerts: List[EyeAlert] = field(default_factory=list)

    def has_blocking_issue(self) -> bool:
        """Check if any alert is BLOCK severity."""
        return any(a.severity == AlertSeverity.BLOCK for a in self.alerts)

    def has_warnings(self) -> bool:
        """Check if any alert is WARN severity."""
        return any(a.severity == AlertSeverity.WARN for a in self.alerts)

    def add(self, view_name: str, severity: AlertSeverity, message: str) -> None:
        """Add an alert to the report."""
        self.alerts.append(EyeAlert(view_name, severity, message))

    def get_by_view(self, view_name: str) -> List[EyeAlert]:
        """Get all alerts from a specific view."""
        return [a for a in self.alerts if a.view_name == view_name]

    def get_blocking_alerts(self) -> List[EyeAlert]:
        """Get all blocking alerts."""
        return [a for a in self.alerts if a.severity == AlertSeverity.BLOCK]


class EyeView(ABC):
    """
    Abstract base class for @EYE views.

    Each view implements a specific inspection lens:
    - Receives draft text, metrics, and context
    - Adds alerts to the shared EyeReport
    - Does NOT generate content (read-only inspection)

    Canon invariant: Any view can BLOCK → SABAR
    """

    # View identity (subclasses must set)
    view_id: int = 0
    view_name: str = "BaseView"

    @abstractmethod
    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """
        Run this view's inspection on the draft.

        Args:
            draft_text: Candidate output to inspect
            metrics: Constitutional metrics for the draft
            context: Additional flags and context
            report: Shared report to add alerts to

        Note: Views add alerts to report in-place, no return value.
        """
        pass


__all__ = [
    "AlertSeverity",
    "EyeAlert",
    "EyeReport",
    "EyeView",
]
