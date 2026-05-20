"""
arifosmcp/runtime/a_rif/abduction.py — Hypothesis Generation
════════════════════════════════════════════════════════════

Abduction creates hypotheses, not conclusions.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.runtime.a_rif.models import AbductiveHypothesis

__all__ = ["generate_hypothesis", "falsification_tests"]


def generate_hypothesis(
    observations: list[str],
    missing_evidence: list[str] | None = None,
    confidence: float = 0.0,
) -> AbductiveHypothesis:
    """Generate a bounded hypothesis from observations."""
    hypothesis_text = (
        f"Best explanation for {len(observations)} observation(s): "
        "further evidence required before acceptance."
    )

    return AbductiveHypothesis(
        hypothesis=hypothesis_text,
        explains=observations,
        missing_evidence=missing_evidence or [],
        falsification_tests=falsification_tests(observations),
        status="hypothesis",
        confidence=confidence,
    )


def falsification_tests(observations: list[str]) -> list[str]:
    """Suggest tests that could falsify the hypothesis."""
    tests = []
    if not observations:
        tests.append("No observations — hypothesis is unfalsifiable")
        return tests

    tests.append("Seek independent source contradicting primary observation")
    tests.append("Check temporal consistency of observations")
    tests.append("Verify measurement methodology is reproducible")
    return tests
