"""Phase 1 · Lane 3 + Lane 4 — honest labels and a declared judge affordance.

Lane 3: apex_scalars attached by arif_judge must carry the same
        "federation baseline, not this session's score" provenance that
        arif_init already attaches.
Lane 4: the judge must resolve to its declared constitutional affordance even
        when the caller uses the transport-prefixed MCP name.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.tools import get_full_affordance
from arifosmcp.tools.judge import _apex_measurement_contracts, _tag_apex_scope


def test_apex_scalars_carry_federation_scope():
    tagged = _tag_apex_scope({"G": 0.5799, "h": 0.8428})

    assert tagged["scope"] == "federation"
    assert "not this session" in tagged["note"].lower()
    # Values must not be rewritten — only labelled.
    assert tagged["G"] == 0.5799 and tagged["h"] == 0.8428


def test_apex_scope_label_is_idempotent():
    once = _tag_apex_scope({"G": 0.5})
    twice = _tag_apex_scope(once)
    assert twice["note"] == once["note"] and twice["scope"] == "federation"


@pytest.mark.parametrize("name", ["arif_judge", "arifos_arif_judge", "arifos.arif_judge"])
def test_judge_affordance_is_known_on_every_transport_name(name: str):
    affordance = get_full_affordance(name)

    assert affordance.get("known") is True, f"{name} resolved to the _default contract"
    assert "not yet declared" not in str(affordance.get("purpose", "")).lower()
    assert affordance.get("output_is_approval") is False


_FIVE_FIELDS = (
    "measurement_id",
    "unit",
    "measurement_method",
    "monotonic_drivers",
    "falsification_test",
    "provenance_class",
    "calibration_status",
    "decision_eligibility",
)


def test_judge_wire_publishes_kx010_contracts_as_sibling_key():
    """KX-010: a physics-labelled scalar on the judge wire must carry its contract.

    /health publishes per-scalar contracts; the judge standing echo flattened
    apex_scalars to bare numbers. The fix adds a SIBLING map, so the numbers keep
    their shape (no consumer breaks) while the contract reaches the wire.
    """
    apex = {"G": 0.5808, "C_dark": 0.18, "W3": 0.6057, "h": 0.84, "sample_size": 100}
    contracts = _apex_measurement_contracts(apex)

    assert set(contracts) == {"G", "C_dark", "W3", "h"}, "container keys must not get contracts"
    for scalar, contract in contracts.items():
        missing = [f for f in _FIVE_FIELDS if not contract.get(f)]
        assert not missing, f"{scalar} contract missing {missing}"
        assert contract["calibration_status"] == "PHASE_1_HEURISTIC_UNCALIBRATED"


def test_scoped_authorization_copy_is_never_decision_eligible():
    contracts = _apex_measurement_contracts({"g_authorization": 0.58, "G": 0.58})
    assert contracts["g_authorization"]["decision_eligibility"] == "NONE"
    assert contracts["G"]["decision_eligibility"] == "ADVISORY"
