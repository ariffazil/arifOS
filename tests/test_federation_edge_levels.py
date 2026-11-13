# S3a (PLAN-2026-11-10-Q1, ARIF GO S3a): observation-level rendering honesty
from arifosmcp.runtime.federation_edges import _finish_edge_fields


def _base():
    return {"session_propagated": None, "actor_propagated": None,
            "trace_propagated": None, "receipt_produced": None,
            "epistemic_preserved": None}


def test_l0_when_nothing_proven():
    e = _base(); e.update({"transport": "timeout"})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L0_DECLARED"


def test_l1_transport_only():
    e = _base(); e.update({"transport": "reachable"})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L1_TRANSPORT"


def test_l2_identity_present_relabelled_both_semantics():
    e = _base(); e.update({"transport": "up", "identity_match": True})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L2_IDENTITY_PRESENT"
    assert e["identity_semantics"] == "IDENTITY_PRESENT_BOTH"


def test_l3_session_actor_bound_without_receipt():
    e = _base(); e.update({"transport": "up", "identity_match": True,
                           "session_propagated": True, "actor_propagated": True})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L3_SESSION_ACTOR_BOUND"


def test_l4_receipt_chained_semantic():
    e = _base(); e.update({"transport": "up", "identity_match": True,
                           "session_propagated": True, "actor_propagated": True,
                           "trace_propagated": True, "receipt_produced": True})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L4_RECEIPT_CHAINED"


def test_never_borrows_higher_green():
    e = _base(); e.update({"transport": "up", "identity_match": True,
                           "session_propagated": True, "actor_propagated": "N/E"})
    _finish_edge_fields(e)
    assert e["observed_level"] == "L2_IDENTITY_PRESENT"


def test_telemetry_produced_honest_not_in_schema():
    for tpl in ({"transport": "up"}, {"transport": "up", "identity_match": True}):
        e = _base(); e.update(tpl)
        _finish_edge_fields(e)
        assert e["telemetry_produced"] == "NOT_IN_SCHEMA"
