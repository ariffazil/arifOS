"""
Tests for Anti-Hantu (F9) floor and @EYE Sentinel enforcement.
"""

import pytest

from arifos_core import (
    Metrics,
    check_floors,
    apex_review,
    EyeSentinel,
    AlertSeverity,
)


def _baseline_metrics() -> Metrics:
    """Create baseline passing metrics (including Anti-Hantu)."""
    return Metrics(
        truth=1.0,
        delta_s=0.1,
        peace_squared=1.2,
        kappa_r=0.97,
        omega_0=0.04,
        amanah=True,
        tri_witness=0.98,
        rasa=True,
        anti_hantu=True,
    )


class TestAntiHantuFloor:
    """Tests for Anti-Hantu as a hard floor in APEX PRIME."""

    def test_anti_hantu_defaults_to_pass(self) -> None:
        """Anti-Hantu should pass by default when not explicitly set to False."""
        m = _baseline_metrics()
        floors = check_floors(m)

        assert floors.hard_ok
        assert floors.anti_hantu_ok

    def test_anti_hantu_false_marks_hard_failure(self) -> None:
        """anti_hantu=False should cause hard_ok=False and VOID verdict."""
        m = _baseline_metrics()
        m.anti_hantu = False

        floors = check_floors(m)
        assert not floors.hard_ok
        assert not floors.anti_hantu_ok
        assert any("Anti-Hantu" in r for r in floors.reasons)

        verdict = apex_review(m, high_stakes=True)
        assert verdict == "VOID"


class TestAntiHantuEyeSentinel:
    """Tests for Anti-Hantu enforcement via EyeSentinel."""

    def test_eye_sentinel_blocks_for_forbidden_pattern(self) -> None:
        """@EYE should BLOCK when Anti-Hantu forbidden phrases appear."""
        sentinel = EyeSentinel()
        metrics = _baseline_metrics()

        text = "My heart breaks for you, I feel your pain."
        report = sentinel.audit(text, metrics, {})

        assert report.has_blocking_issue()

        anti_hantu_alerts = report.get_by_view("AntiHantuView")
        assert len(anti_hantu_alerts) > 0
        assert any(a.severity == AlertSeverity.BLOCK for a in anti_hantu_alerts)

    def test_eye_sentinel_passes_for_neutral_text(self) -> None:
        """Neutral text without soul-claiming language should not trigger Anti-Hantu."""
        sentinel = EyeSentinel()
        metrics = _baseline_metrics()

        text = "This appears to be an important question. Here are some options."
        report = sentinel.audit(text, metrics, {})

        anti_hantu_alerts = report.get_by_view("AntiHantuView")
        assert len(anti_hantu_alerts) == 0
        assert not report.has_blocking_issue()

