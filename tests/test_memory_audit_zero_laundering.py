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


def test_apex_block_says_which_system_it_describes():
    """Two different G values can live in one payload. Every APEX block must
    name the system it describes (scope + note) - the disambiguation."""
    from arifosmcp.runtime.act_token import APEX_SCOPE_ACTOR, APEX_SCOPE_FEDERATION

    federation = build_standing_apex({"sample_size": 5, "G": 0.58, "W3": None})
    actor = build_standing_apex({"sample_size": 5, "G": 0.34, "W3": None}, scope=APEX_SCOPE_ACTOR)
    assert federation["scope"] == APEX_SCOPE_FEDERATION
    assert actor["scope"] == APEX_SCOPE_ACTOR
    assert federation["scope"] != actor["scope"]
    for block in (federation, actor):
        assert block.get("note"), "an APEX block without a note cannot be told apart from another"
        assert "G" in block and "W3" in block


def test_mint_carries_the_scope_label_into_the_signed_claims():
    """The token's claims hold a THIRD G (actor-scoped). Without the label a
    reader cannot tell it from the federation aggregate."""
    from arifosmcp.runtime.act_token import APEX_SCOPE_ACTOR, build_standing_apex, mint_act

    apex = build_standing_apex(
        {"sample_size": 5, "G": 0.34, "C_dark": 0.18, "W3": None, "h": 0.98},
        scope=APEX_SCOPE_ACTOR,
    )
    _token, claims = mint_act(
        sid="sess-apex-label-test",
        actor="333-AGI",
        auth="OBSERVE_ONLY",
        av=False,
        apex=apex,
    )
    assert claims["apex"]["scope"] == APEX_SCOPE_ACTOR
    assert claims["apex"]["note"]
    assert claims["apex"]["G"] == 0.34
    assert claims["apex"]["W3"] == UNMEASURED


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


def test_unmeasured_g_marker_neither_gates_nor_crashes_the_f8_genius_gate():
    """The standing APEX may carry G = "UNMEASURED"; the verdict gate must
    treat that as unmeasured (skip the gate) instead of comparing a string
    with a float (TypeError) - and a MEASURED G must still gate."""
    from arifosmcp.runtime.verdict import compose_effective_verdict

    unmeasured = compose_effective_verdict(
        inner_verdict="SEAL",
        session_authority_band="FULL",
        drift=[],
        g_score="UNMEASURED",
    )
    assert "F8_GENIUS" not in (unmeasured.reason_code or "")

    measured = compose_effective_verdict(
        inner_verdict="SEAL",
        session_authority_band="FULL",
        drift=[],
        g_score=0.50,
    )
    assert "F8_GENIUS" in (measured.reason_code or "")


def test_measured_zero_g_still_gates():
    """Zero is a reading, not a missing value: it must not be laundered into
    'unmeasured' (which would silently unlock a SEAL that should be gated)."""
    from arifosmcp.runtime.verdict import compose_effective_verdict

    zero_g = compose_effective_verdict(
        inner_verdict="SEAL",
        session_authority_band="FULL",
        drift=[],
        g_score=0.0,
    )
    assert "F8_GENIUS" in (zero_g.reason_code or "")
