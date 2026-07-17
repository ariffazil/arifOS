"""P1 acceptance tests for arifos.handoff.v1 semantic bridge.

These prove the contract, not full live organ federation.
"""

from __future__ import annotations

from arifosmcp.contracts.handoff_v1 import (
    EpistemicState,
    SessionAuthority,
    admit_handoff,
    chain_continuity,
    new_handoff,
    wealth_must_not_overwrite_geology,
)
from arifosmcp.runtime.semantic_edge import (
    classify_edge,
    simulate_priority_handoffs,
)


def test_geox_to_wealth_admitted():
    h = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id="arif",
        actor_verified=True,
        session_id="SEAL-1",
        authority=SessionAuthority.ADVISORY,
        claim_summary="OBSERVED volume range",
        epistemic_state=EpistemicState.OBSERVED,
        confidence=0.72,
        evidence=[
            {
                "ref": "geox://p/1",
                "type": "earth_measurement",
                "hash": "sha256:abc",
                "owner_organ": "GEOX",
            }
        ],
        requested_output="capital_scenario",
        trace_id="t1",
    )
    a = admit_handoff(h)
    assert a.admitted is True
    assert "geology" in h.claim.non_revision_bound


def test_wealth_cannot_overwrite_geology():
    h = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id="arif",
        actor_verified=True,
        session_id="SEAL-1",
        authority=SessionAuthority.ADVISORY,
        claim_summary="x",
        epistemic_state=EpistemicState.OBSERVED,
        confidence=0.7,
        evidence=[{"ref": "g", "type": "earth_measurement", "hash": "sha256:x"}],
        requested_output="capital_scenario",
        trace_id="t1",
    )
    ok = wealth_must_not_overwrite_geology(h, {"capital_consequence": {"npv": 1}})
    bad = wealth_must_not_overwrite_geology(h, {"geology": {"mutated": True}})
    assert ok == []
    assert any("geology" in v for v in bad)


def test_well_rejects_raw_capital_ledger():
    h = new_handoff(
        source_organ="WEALTH",
        target_organ="WELL",
        intent="reflect",
        actor_id="arif",
        actor_verified=True,
        session_id="SEAL-1",
        authority=SessionAuthority.REFLECT_ONLY,
        claim_summary="x",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.5,
        evidence=[
            {
                "ref": "w",
                "type": "raw_capital_ledger",
                "hash": "sha256:x",
            }
        ],
        requested_output="capacity_reflection",
        trace_id="t1",
    )
    a = admit_handoff(h)
    assert a.admitted is False
    assert a.verdict == "HOLD"
    assert any("well_forbidden" in r for r in a.reasons)


def test_missing_evidence_hold():
    h = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id="arif",
        actor_verified=True,
        session_id="SEAL-1",
        authority=SessionAuthority.ADVISORY,
        claim_summary="x",
        epistemic_state=EpistemicState.SPECULATIVE,
        confidence=0.3,
        evidence=[],
        requested_output="capital_scenario",
        trace_id="t1",
    )
    a = admit_handoff(h)
    assert a.verdict == "HOLD"
    assert "missing_evidence" in a.reasons


def test_aforge_blocked_without_judgment():
    h = new_handoff(
        source_organ="ARIFOS",
        target_organ="A-FORGE",
        intent="execute_mutation",
        actor_id="arif",
        actor_verified=True,
        session_id="SEAL-1",
        authority=SessionAuthority.OBSERVE_ONLY,
        claim_summary="x",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.5,
        evidence=[{"ref": "p", "type": "plan", "hash": "sha256:p"}],
        requested_output="mutation",
        trace_id="t1",
    )
    a = admit_handoff(h)
    assert a.admitted is False
    assert any("aforge_requires" in r for r in a.reasons)


def test_actor_session_trace_continuity():
    tid = "trace-continuous"
    sid = "SEAL-ROOT"
    h1 = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id="arif",
        actor_verified=True,
        session_id=sid,
        authority=SessionAuthority.ADVISORY,
        claim_summary="a",
        epistemic_state=EpistemicState.OBSERVED,
        confidence=0.7,
        evidence=[{"ref": "g", "type": "earth_measurement", "hash": "sha256:g"}],
        requested_output="capital_scenario",
        trace_id=tid,
    )
    h2 = new_handoff(
        source_organ="WEALTH",
        target_organ="WELL",
        intent="reflect",
        actor_id="arif",
        actor_verified=True,
        session_id=sid,
        authority=SessionAuthority.REFLECT_ONLY,
        claim_summary="b",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.6,
        evidence=[{"ref": "w", "type": "capital_scenario_summary", "hash": "sha256:w"}],
        requested_output="capacity_reflection",
        trace_id=tid,
    )
    cont = chain_continuity([h1, h2])
    assert cont["ok"] is True
    assert cont["actor_id"] == "arif"
    assert cont["trace_id"] == tid


def test_semantic_edge_colors_not_all_green():
    assert classify_edge(
        transport_ok=True,
        identity_matched="N/E",
        schema_accepted="N/E",
        session_propagated="N/E",
        actor_propagated="N/E",
        trace_propagated="N/E",
        epistemic_preserved="N/E",
        receipt_produced="N/E",
    ) == "TRANSPORT_ONLY"
    assert (
        classify_edge(
            transport_ok=True,
            identity_matched=True,
            schema_accepted=True,
            session_propagated=True,
            actor_propagated=True,
            trace_propagated=True,
            epistemic_preserved=True,
            receipt_produced=True,
            handoff_admitted=True,
        )
        == "GOVERNED"
    )


def test_simulate_priority_handoffs_acceptance_bundle():
    result = simulate_priority_handoffs()
    acc = result["acceptance"]
    assert acc["geox_accepted_by_wealth"] is True
    assert acc["wealth_cannot_overwrite_geology"] is True
    assert acc["well_min_fields"] is True
    assert acc["actor_continuous"] is True
    assert acc["session_continuous"] is True
    assert acc["trace_continuous"] is True
    assert acc["missing_evidence_hold"] is True
    assert acc["aforge_blocked_without_judgment"] is True
    assert result["priority_edge_semantic_states"]["GEOX→WEALTH"] in (
        "CONTEXT_ALIGNED",
        "GOVERNED",
        "SCHEMA_ALIGNED",
    )
    # A-FORGE path must not be falsely GOVERNED
    assert result["priority_edge_semantic_states"]["ARIFOS→A-FORGE"] != "GOVERNED"
