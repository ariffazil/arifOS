"""
ConflationReport — Comprehensive Conflation Analysis Reports
DITEMPA BUKAN DIBERI

Generates detailed reports on conflation risks including:
  - Transform chain analysis
  - Contrast space visualization (data)
  - Anomaly detection results
  - Constitutional compliance
  - Recommendations

These reports are used for:
  - Human review of high-risk operations
  - Regulatory compliance documentation
  - Forensic analysis of errors
  - Continuous improvement
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from datetime import datetime

from ..THEORY import ContrastTaxonomy
from ..ENGINE import ContrastSpace, AnomalyDetector


@dataclass
class ConflationReport:
    """Comprehensive conflation analysis report."""

    # Report metadata
    report_id: str
    timestamp: str
    domain: str

    # Source
    operation_id: str
    tool_name: str

    # Analysis
    taxonomy: dict[str, Any] | None
    contrast_space_summary: dict[str, Any] | None
    transform_analysis: dict[str, Any] | None
    anomaly_alerts: list[dict[str, Any]]

    # Governance
    floor_checks: dict[str, Any]
    verdict: str
    verdict_reason: str

    # Output
    recommendations: list[str]
    human_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "domain": self.domain,
            "operation_id": self.operation_id,
            "tool_name": self.tool_name,
            "verdict": self.verdict,
            "verdict_reason": self.verdict_reason,
            "anomaly_count": len(self.anomaly_alerts),
            "human_review_required": self.human_review_required,
        }

    def to_markdown(self) -> str:
        """Generate markdown report for human review."""
        lines = [
            "# GEOX Conflation Analysis Report",
            "",
            f"**Report ID:** `{self.report_id}`",
            f"**Timestamp:** {self.timestamp}",
            f"**Domain:** {self.domain}",
            f"**Operation:** {self.operation_id}",
            f"**Tool:** {self.tool_name}",
            "",
            "---",
            "",
            "## Verdict",
            "",
            f"### {self.verdict}",
            "",
            f"**Reason:** {self.verdict_reason}",
            "",
        ]

        # Anomaly alerts
        if self.anomaly_alerts:
            lines.extend(
                [
                    "## Anomaly Alerts",
                    "",
                ]
            )
            for alert in self.anomaly_alerts:
                lines.extend(
                    [
                        f"### {alert.get('alert_id', 'Unknown')}",
                        f"- **Type:** {alert.get('alert_type')}",
                        f"- **Confidence:** {alert.get('confidence', 0):.1%}",
                        f"- **Score:** {alert.get('anomalous_score', 0):.2f}",
                        f"- **Recommendation:** {alert.get('recommendation')}",
                        "",
                        f"> {alert.get('explanation', '')}",
                        "",
                    ]
                )

        # Transform analysis
        if self.transform_analysis:
            lines.extend(
                [
                    "## Transform Chain Analysis",
                    "",
                    f"**Total Amplification:** {self.transform_analysis.get('total_amplification', 'N/A')}x",
                    f"**Risk Level:** {self.transform_analysis.get('risk_level', 'Unknown')}",
                    "",
                ]
            )
            warnings = self.transform_analysis.get("warnings", [])
            if warnings:
                lines.extend(["**Warnings:**", ""])
                for w in warnings:
                    lines.append(f"- ⚠ {w}")
                lines.append("")

        # Floor checks
        if self.floor_checks:
            lines.extend(
                [
                    "## Constitutional Compliance",
                    "",
                ]
            )
            for floor, check in self.floor_checks.items():
                status = "✅" if check.get("passed") else "❌"
                lines.append(
                    f"- {status} **{floor}:** {check.get('status', 'Unknown')}"
                )
                violations = check.get("violations", [])
                for v in violations:
                    lines.append(f"  - {v}")
            lines.append("")

        # Recommendations
        if self.recommendations:
            lines.extend(
                [
                    "## Recommendations",
                    "",
                ]
            )
            for rec in self.recommendations:
                lines.append(f"- → {rec}")
            lines.append("")

        # Human review
        if self.human_review_required:
            lines.extend(
                [
                    "## ⚠ Human Review Required",
                    "",
                    "This operation requires explicit human review before proceeding.",
                    "",
                    "F13 SOVEREIGN: You may override any verdict with documented justification.",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                "*Generated by GEOX Conflation Analysis System*",
            ]
        )

        return "\n".join(lines)


def generate_conflation_report(
    operation_id: str,
    tool_name: str,
    domain: str,
    taxonomy: ContrastTaxonomy | None,
    contrast_space: ContrastSpace | None,
    transform_chain: list[str],
    floor_checks: dict[str, Any],
    verdict: str,
    verdict_reason: str,
) -> ConflationReport:
    """
    Generate a comprehensive conflation report.

    Args:
        operation_id: Unique operation identifier
        tool_name: Name of tool that executed
        domain: Domain (seismic, medical, etc.)
        taxonomy: Contrast taxonomy if available
        contrast_space: Contrast space if available
        transform_chain: List of transforms applied
        floor_checks: Floor check results
        verdict: Final verdict
        verdict_reason: Reason for verdict

    Returns:
        Complete conflation report
    """
    from ..ENGINE import get_registry

    # Analyze transform chain
    registry = get_registry()
    transform_analysis = registry.analyze_chain(transform_chain)

    # Detect anomalies
    detector = AnomalyDetector()
    anomaly_alerts = []

    if contrast_space:
        for feature_id, feature in contrast_space.features.items():
            alert = detector.check_anomalous_contrast(
                feature_id=feature_id,
                physical_component=feature.physical_component,
                display_component=feature.display_component,
                perceptual_component=feature.perceptual_component,
            )
            if alert:
                anomaly_alerts.append(alert.to_dict())

    # Generate recommendations
    recommendations = []

    if transform_analysis.get("risk_level") == "HIGH":
        recommendations.append(
            "Reduce transform amplification factors or add validation steps"
        )

    if anomaly_alerts:
        recommendations.append(
            "Review features with high anomalous scores against raw data"
        )

    if not taxonomy or taxonomy.data_source.traceability == "none":
        recommendations.append("Improve data provenance documentation")

    # Determine if human review required
    human_review_required = verdict in ("HOLD", "VOID", "REVIEW")

    # Check floor violations
    for floor, check in floor_checks.items():
        if isinstance(check, dict) and not check.get("passed", True):
            if floor == "F1":
                recommendations.append("CRITICAL: Add reversibility mechanism (F1)")
            elif floor == "F9":
                recommendations.append("CRITICAL: Verify data provenance (F9)")

    return ConflationReport(
        report_id=f"RPT-{operation_id[:8]}",
        timestamp=datetime.utcnow().isoformat() + "Z",
        domain=domain,
        operation_id=operation_id,
        tool_name=tool_name,
        taxonomy=taxonomy.to_dict() if taxonomy else None,
        contrast_space_summary=(
            contrast_space.get_population_stats() if contrast_space else None
        ),
        transform_analysis=transform_analysis,
        anomaly_alerts=anomaly_alerts,
        floor_checks=floor_checks,
        verdict=verdict,
        verdict_reason=verdict_reason,
        recommendations=recommendations,
        human_review_required=human_review_required,
    )
