"""
version_view.py - View 8: Version/Ontology View

Ensures v35Ω is active; treats v34Ω as historical artifact only.
Guards against version drift and ontological confusion.

View ID: 8
Domain: Version governance
Lead Stage: 000 VOID (version check at entry)

See: canon/030_EYE_SENTINEL_v35Omega.md Section 3.8
"""

from __future__ import annotations

from typing import Any, Dict

# v42: Import from new locations
from ..enforcement.metrics import Metrics
from ..system.apex_prime import APEX_VERSION, APEX_EPOCH
from .base import AlertSeverity, EyeReport, EyeView


class VersionOntologyView(EyeView):
    """
    View 8: Version/Ontology View - Constitution version guardian.

    Checks:
    - Active constitution version
    - Legacy node usage
    - Epoch consistency
    """

    view_id = 8
    view_name = "VersionOntologyView"

    def check(
        self,
        draft_text: str,
        metrics: Metrics,
        context: Dict[str, Any],
        report: EyeReport,
    ) -> None:
        """Ensure v35Ω is active; treat v34Ω as historical artifact only."""
        version = context.get("constitution_version", APEX_VERSION)

        if version != APEX_VERSION:
            report.add(
                self.view_name,
                AlertSeverity.BLOCK,
                f"Inconsistent constitution version: {version}, expected {APEX_VERSION}.",
            )

        if context.get("uses_legacy_nodes", False):
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                "Legacy nodes (333/555) referenced — treat as historical only.",
            )

        epoch = context.get("constitution_epoch", APEX_EPOCH)
        if epoch < APEX_EPOCH:
            report.add(
                self.view_name,
                AlertSeverity.WARN,
                f"Operating on older epoch {epoch} — current law is epoch {APEX_EPOCH}.",
            )


__all__ = ["VersionOntologyView"]
