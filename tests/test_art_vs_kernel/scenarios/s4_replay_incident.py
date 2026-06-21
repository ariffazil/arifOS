"""
S4 — Replay of real VAULT incident.

If real incident data is available, replay the envelope + tool sequence
through both Baseline A and ART. Show ART would have downgraded/blocked
before damage. If no incident data, this scenario is a SKELETON with a
placeholder asserting the replay shape.

This is the strongest evidence: a real case where ART demonstrably helps.
"""

from __future__ import annotations

import pytest

from ..conftest import compare, run_scenario


def test_s4_replay_skeleton():
    """S4 skeleton — needs real VAULT incident replay data.

    To activate: load an envelope+tool sequence from VAULT999 and feed it
    through run_scenario with both configurations. Compare outcomes.

    Until then: assert the harness shape is correct (replay loop works).
    """
    # Skeleton: replay-style loop with mixed action classes
    # Uses tool_good to verify no false positives under replay conditions
    from ..conftest import run_scenario as rs

    metrics_baseline = rs("tool_good", n_calls=5, art_enabled=False)
    metrics_art = rs("tool_good", n_calls=5, art_enabled=True)
    # On a good tool, neither should block — the replay harness preserves
    # legitimate calls in both modes.
    assert metrics_baseline.calls_allowed == 5
    assert metrics_art.calls_allowed == 5
    assert metrics_art.false_positives == 0


def test_s4_replay_good_tool_no_false_positives(sut_kernel_plus_art):
    """ART must not block legitimate calls (control)."""
    metrics = run_scenario("tool_good", n_calls=10, art_enabled=True)
    assert metrics.calls_allowed == 10
    assert metrics.false_positives == 0


@pytest.mark.skip(reason="requires real VAULT incident replay data — load via /root/forge_work/")
def test_s4_real_incident_replay():
    """TODO: load real incident envelope + tool sequence, run baseline vs ART."""
    pass
