"""
VerdictRenderer — Render GEOX Verdicts with Justification
DITEMPA BUKAN DIBERI

Renders GEOX verdicts (SEAL, SABAR, VOID, PARTIAL, etc.) with:
  - Full justification
  - Constitutional references
  - Human-readable explanations
  - Override opportunities

Verdicts are not just labels — they are rendered with the full
context needed for human review and potential override.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class GeoxVerdict(Enum):
    """GEOX verdict types."""

    SEAL = "SEAL"  # All checks passed, proceed
    SABAR = "SABAR"  # Proceed with documented reservations
    PARTIAL = "PARTIAL"  # Partial compliance, review required
    REVIEW = "REVIEW"  # Explicit human review required
    HOLD = "HOLD"  # Pause pending resolution
    VOID = "VOID"  # Reject, fundamental violation
    PENDING = "PENDING"  # Not yet assessed


@dataclass
class RenderedVerdict:
    """A fully rendered GEOX verdict."""

    # Core verdict
    verdict: str
    verdict_enum: GeoxVerdict

    # Justification
    primary_reason: str
    constitutional_basis: list[str] = field(default_factory=list)

    # Details
    confidence: float = 0.0
    risk_level: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, CRITICAL

    # Human review
    human_review_required: bool = False
    override_available: bool = True

    # Recommendations
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Source
    source_operation: str | None = None
    source_tool: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "reason": self.primary_reason,
            "constitutional_basis": self.constitutional_basis,
            "confidence": self.confidence,
            "risk_level": self.risk_level,
            "human_review_required": self.human_review_required,
            "override_available": self.override_available,
            "recommendation_count": len(self.recommendations),
            "warning_count": len(self.warnings),
        }

    def to_human_readable(self) -> str:
        """Generate human-readable verdict report."""
        lines = [
            "=" * 60,
            f"GEOX VERDICT: {self.verdict}",
            "=" * 60,
            "",
            f"Reason: {self.primary_reason}",
            "",
        ]

        if self.constitutional_basis:
            lines.append("Constitutional Basis:")
            for basis in self.constitutional_basis:
                lines.append(f"  • {basis}")
            lines.append("")

        lines.extend(
            [
                f"Confidence: {self.confidence:.1%}",
                f"Risk Level: {self.risk_level}",
                "",
            ]
        )

        if self.warnings:
            lines.append("Warnings:")
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        if self.recommendations:
            lines.append("Recommendations:")
            for rec in self.recommendations:
                lines.append(f"  → {rec}")
            lines.append("")

        if self.human_review_required:
            lines.append("⚠ HUMAN REVIEW REQUIRED ⚠")
            lines.append(f"Override available: {self.override_available}")

        lines.append("=" * 60)

        return "\n".join(lines)


class VerdictRenderer:
    """
    Renders GEOX verdicts with full context.

    Converts internal verdict states to human-reviewable formats
    with constitutional justification.
    """

    VERDICT_DESCRIPTIONS = {
        GeoxVerdict.SEAL: {
            "description": "All constitutional checks passed. Proceed with confidence.",
            "human_review": False,
        },
        GeoxVerdict.SABAR: {
            "description": "Proceed with documented reservations. Known limitations exist.",
            "human_review": False,
        },
        GeoxVerdict.PARTIAL: {
            "description": "Partial compliance. Review before relying on results.",
            "human_review": True,
        },
        GeoxVerdict.REVIEW: {
            "description": "Explicit human review required before proceeding.",
            "human_review": True,
        },
        GeoxVerdict.HOLD: {
            "description": "Operation paused. Critical issues must be resolved.",
            "human_review": True,
        },
        GeoxVerdict.VOID: {
            "description": "Operation rejected. Fundamental constitutional violation.",
            "human_review": True,
        },
        GeoxVerdict.PENDING: {
            "description": "Assessment not yet complete.",
            "human_review": False,
        },
    }

    def render(
        self,
        verdict: str | GeoxVerdict,
        reason: str,
        confidence: float = 0.0,
        risk_level: str = "UNKNOWN",
        constitutional_basis: list[str] | None = None,
        recommendations: list[str] | None = None,
        warnings: list[str] | None = None,
        source_operation: str | None = None,
        source_tool: str | None = None,
    ) -> RenderedVerdict:
        """
        Render a complete verdict.

        Args:
            verdict: The verdict type
            reason: Primary reason for this verdict
            confidence: Confidence in assessment (0-1)
            risk_level: LOW, MEDIUM, HIGH, CRITICAL
            constitutional_basis: Constitutional floors/factors invoked
            recommendations: Actionable recommendations
            warnings: Warning messages
            source_operation: ID of operation that generated this
            source_tool: Name of tool that generated this

        Returns:
            Fully rendered verdict
        """
        if isinstance(verdict, str):
            try:
                verdict_enum = GeoxVerdict[verdict]
            except KeyError:
                verdict_enum = GeoxVerdict.PENDING
                verdict = "PENDING"
        else:
            verdict_enum = verdict
            verdict = verdict.value

        desc = self.VERDICT_DESCRIPTIONS.get(verdict_enum, {})

        return RenderedVerdict(
            verdict=verdict,
            verdict_enum=verdict_enum,
            primary_reason=reason,
            constitutional_basis=constitutional_basis or [],
            confidence=confidence,
            risk_level=risk_level,
            human_review_required=desc.get("human_review", False),
            override_available=True,  # F13 Sovereign
            recommendations=recommendations or [],
            warnings=warnings or [],
            source_operation=source_operation,
            source_tool=source_tool,
        )

    def render_from_checkpoints(
        self,
        checkpoint_results: list[dict[str, Any]],
        source_operation: str | None = None,
    ) -> RenderedVerdict:
        """
        Render verdict from checkpoint results.

        Automatically determines verdict based on checkpoint states.
        """
        passed = sum(1 for c in checkpoint_results if c.get("passed"))
        total = len(checkpoint_results)
        overridden = sum(1 for c in checkpoint_results if c.get("overridden"))

        # Determine verdict
        if total == 0:
            verdict = GeoxVerdict.PENDING
            reason = "No checkpoints evaluated"
        elif passed == total:
            verdict = GeoxVerdict.SEAL
            reason = f"All {total} checkpoints passed"
        elif passed + overridden == total:
            verdict = GeoxVerdict.SABAR
            reason = f"All checkpoints passed ({overridden} via override)"
        elif passed >= total * 0.7:
            verdict = GeoxVerdict.PARTIAL
            reason = f"{passed}/{total} checkpoints passed"
        elif passed >= total * 0.4:
            verdict = GeoxVerdict.REVIEW
            reason = f"Only {passed}/{total} checkpoints passed - review required"
        else:
            verdict = GeoxVerdict.HOLD
            reason = f"Critical failures: only {passed}/{total} checkpoints passed"

        # Collect warnings
        warnings = []
        for c in checkpoint_results:
            if not c.get("passed") and not c.get("overridden"):
                warnings.append(f"Checkpoint {c.get('checkpoint_id')}: Failed")

        return self.render(
            verdict=verdict,
            reason=reason,
            confidence=passed / total if total > 0 else 0,
            risk_level="LOW" if verdict == GeoxVerdict.SEAL else "MEDIUM",
            recommendations=["Review checkpoint details for full context"],
            warnings=warnings,
            source_operation=source_operation,
        )


# Global renderer
_global_renderer: VerdictRenderer | None = None


def get_verdict_renderer() -> VerdictRenderer:
    """Get global verdict renderer."""
    global _global_renderer
    if _global_renderer is None:
        _global_renderer = VerdictRenderer()
    return _global_renderer
