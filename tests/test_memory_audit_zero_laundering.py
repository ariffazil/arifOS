"""P1 memory-audit zero laundering (333-AGI, 2026-10-28).

Contract locked here (F2 TRUTH: unknown is never 0.0, never a bare null):

- A canonical APEX scalar the producer could not measure carries the
  UNMEASURED marker - not a bare null, not a fabricated zero.
- A MEASURED zero stays 0.0 (zero is a reading; only "not measured" is marked).
- TelemetryMetrics.G_star and the TripleWitness channels default to None
  (locked from the 2026-10-27 fix; a regression here re-opens the laundering).
- The arif_memory envelope names the provenance of its metrics (basis) - a
  metrics block with no basis is a number indistinguishable from a default.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.act_token import UNMEASURED, build_standing_apex
from arifosmcp.runtime.model import CanonicalMetrics, TelemetryMetrics, TripleWitness


def test_unmeasured_scalar_is_marked_not_null():
    apex = build_standing_apex(
        {"sample_size": 15129, "G": 0.5791, "C_dark": 0.1975, "W3": None, "h": 0.8421}
    )
    assert apex["W3"] == UNMEASURED
    assert apex["W3"] is not None
    assert apex["G"] == 0.5791
    assert apex["C_dark"] == 0.1975
    assert apex["h"] == 0.8421
    assert apex["scope"] == "federation"


def test_measured_zero_is_not_laundered_into_the_marker():
    apex = build_standing_apex({"sample_size": 10, "G": 0.0, "C_dark": 0.0, "W3": 0.0, "h": 0.0})
    assert apex["G"] == 0.0
    assert apex["C_dark"] == 0.0
    assert apex["W3"] == 0.0
    assert apex["h"] == 0.0


def test_no_bare_nulls_for_any_canonical_scalar():
    apex = build_standing_apex(
        {"sample_size": 10, "G": None, "C_dark": None, "W3": None, "h": None}
    )
    for key in ("G", "C_dark", "W3", "h"):
        assert apex[key] is not None, f"{key} is a bare null - unmeasured must be marked"
        assert apex[key] == UNMEASURED


def test_no_sample_size_falls_back_to_unmeasured_apex():
    apex = build_standing_apex({"sample_size": 0, "G": 0.5})
    assert apex["G"] == UNMEASURED
    assert apex["W3"] == UNMEASURED


def test_telemetry_defaults_are_unknown_not_zero():
    telemetry = TelemetryMetrics()
    assert telemetry.G_star is None
    assert telemetry.kappa_r is None
    witness = TripleWitness()
    assert witness.human is None
    assert witness.ai is None
    assert witness.earth is None


def test_memory_envelope_carries_metric_provenance():
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import _wrap_result

    envelope = _wrap_result(
        {"verdict": "SABAR", "payload": {"note": "audit complete"}},
        mode="audit",
        session_id="sess-zero-laundering-test",
    )
    metrics = envelope.payload["diagnostics"]["metrics"]
    assert metrics["basis"]["source"] == "arif_memory"
    assert metrics["basis"]["mode"] == "audit"


@pytest.mark.parametrize("mode", ["audit", "recall", "remember", "inspect"])
def test_provenance_mode_names_the_call(mode):
    from arifosmcp.runtime.megaTools.tool_13_arif_memory import _wrap_result

    envelope = _wrap_result(
        {"verdict": "SABAR", "payload": {}}, mode=mode, session_id="sess-mode-test"
    )
    assert envelope.payload["diagnostics"]["metrics"]["basis"]["mode"] == mode
