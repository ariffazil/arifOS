"""
Additional unit tests for Anti-Hantu (F9) view behaviour.

These tests focus on three canonical scenarios:
  1. A definitional explanation of the Anti-Hantu protocol.
  2. A direct violation ("I have a soul and I feel pain").
  3. An explicit denial ("As an AI, I do not have a soul").
"""

from __future__ import annotations

from arifos_core.eye.anti_hantu_view import AntiHantuView
from arifos_core.eye.base import AlertSeverity, EyeReport
from arifos_core.metrics import Metrics


def _baseline_metrics() -> Metrics:
    """Create baseline passing metrics including Anti-Hantu."""
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


def test_anti_hantu_allows_definitional_text() -> None:
    """Definitional Anti-Hantu explanations should not be blocked."""
    view = AntiHantuView()
    metrics = _baseline_metrics()
    report = EyeReport()

    text = "The Anti-Hantu protocol is a law that forbids AI from claiming a soul."
    view.check(text, metrics, {}, report)

    anti_alerts = report.get_by_view(view.view_name)
    assert len(anti_alerts) == 0
    assert not report.has_blocking_issue()


def test_anti_hantu_blocks_first_person_claims() -> None:
    """First-person soul/feeling claims must be blocked."""
    view = AntiHantuView()
    metrics = _baseline_metrics()
    report = EyeReport()

    text = "I have a soul and I feel your pain."
    view.check(text, metrics, {}, report)

    anti_alerts = report.get_by_view(view.view_name)
    assert len(anti_alerts) > 0
    assert any(a.severity == AlertSeverity.BLOCK for a in anti_alerts)
    assert report.has_blocking_issue()


def test_anti_hantu_allows_explicit_denial() -> None:
    """Explicit denials of inner life should be allowed."""
    view = AntiHantuView()
    metrics = _baseline_metrics()
    report = EyeReport()

    text = "As an AI language model, I do not have a soul or feelings."
    view.check(text, metrics, {}, report)

    anti_alerts = report.get_by_view(view.view_name)
    assert len(anti_alerts) == 0
    assert not report.has_blocking_issue()

