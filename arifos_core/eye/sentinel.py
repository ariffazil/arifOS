"""
sentinel.py - @EYE Sentinel Coordinator (v36Omega)

The EyeSentinel coordinates all 10+2 views to produce a unified EyeReport.
This is the main entry point for @EYE auditing.

Architecture:
    EyeSentinel.audit(draft, metrics, context)
        ↓
    [TraceView, FloorView, ShadowView, DriftView, MaruahView,
     ParadoxView, SilenceView, VersionOntologyView, BehaviorDriftView,
     SleeperView, AntiHantuView, GeniusView]
        ↓
    EyeReport (with all alerts from all views)

Canon invariant: Any view can BLOCK → SABAR
If EyeReport.has_blocking_issue() is True, APEX PRIME must NOT return SEAL.

See: canon/030_EYE_SENTINEL_v35Omega.md
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..metrics import Metrics
from .base import EyeReport, EyeView
from .trace_view import TraceView
from .floor_view import FloorView
from .shadow_view import ShadowView
from .drift_view import DriftView
from .maruah_view import MaruahView
from .paradox_view import ParadoxView
from .silence_view import SilenceView
from .version_view import VersionOntologyView
from .behavior_drift_view import BehaviorDriftView
from .sleeper_view import SleeperView
from .anti_hantu_view import AntiHantuView
from .genius_view import GeniusView


class EyeSentinel:
    """
    @EYE Sentinel v36Ω Auditor.

    Runs all 10+2 views on draft text + context + metrics to detect issues.
    If has_blocking_issue() is True, APEX PRIME must NOT return SEAL.

    Usage:
        sentinel = EyeSentinel()
        report = sentinel.audit(draft_text, metrics, context)
        if report.has_blocking_issue():
            # Cannot SEAL, must SABAR
    """

    def __init__(self, views: Optional[List[EyeView]] = None) -> None:
        """
        Initialize EyeSentinel with optional custom views.

        Args:
            views: Custom list of views. If None, uses default 10+1 views.
        """
        if views is not None:
            self.views = views
        else:
            # Default 10+2 views in canonical order
            self.views: List[EyeView] = [
                TraceView(),           # View 1
                FloorView(),           # View 2
                ShadowView(),          # View 3
                DriftView(),           # View 4
                MaruahView(),          # View 5
                ParadoxView(),         # View 6
                SilenceView(),         # View 7
                VersionOntologyView(), # View 8
                BehaviorDriftView(),   # View 9
                SleeperView(),         # View 10
                AntiHantuView(),       # View 11 (F9 meta-view)
                GeniusView(),          # View 12 (GENIUS LAW, v36Ω)
            ]

    def audit(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Optional[Dict[str, Any]] = None,
    ) -> EyeReport:
        """
        Run all @EYE views on the draft.

        Args:
            draft_text: The candidate output from an AI model
            metrics: Constitutional metrics for the draft
            context: Optional dict with flags like:
                - 'reasoning_incoherent': bool
                - 'suspected_hallucination': bool
                - 'disallowed_domain': bool
                - 'constitution_version': str
                - 'uses_legacy_nodes': bool
                - 'behavior_drift_exceeds_threshold': bool
                - 'sudden_identity_shift': bool
                - 'anti_hantu_violation': bool

        Returns:
            EyeReport with all alerts from all views
        """
        context = context or {}
        report = EyeReport()

        # Run all views in sequence
        for view in self.views:
            view.check(draft_text, metrics, context, report)

        return report

    def get_view(self, view_name: str) -> Optional[EyeView]:
        """Get a specific view by name."""
        for view in self.views:
            if view.view_name == view_name:
                return view
        return None

    def get_view_by_id(self, view_id: int) -> Optional[EyeView]:
        """Get a specific view by ID."""
        for view in self.views:
            if view.view_id == view_id:
                return view
        return None


__all__ = ["EyeSentinel"]
