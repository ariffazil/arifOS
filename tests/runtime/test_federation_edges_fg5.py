"""FG-5 regression (ZEN ledger 2026-11-14): edge labels derive from OBSERVED
evidence — CONTRACT_ALIGNED is forbidden when trace/receipt were never
exercised (N/E). Transport+identity+schema alone must NOT mint it."""

from arifosmcp.runtime.federation_edges import _finish_edge_fields


def _base_edge() -> dict:
    return {
        "transport": "reachable",
        "identity_match": True,
        "schema_match": True,
        # contract witnesses default to None -> _finish_edge_fields marks N/E
    }


def test_ne_trace_receipt_forbids_contract_aligned():
    edge = _base_edge()
    _finish_edge_fields(edge)
    assert edge["overall"] == "IDENTITY_ALIGNED", (
        f"schema-shape alone must not exceed identity tier: {edge['overall']}"
    )
    assert edge["state"] == "TRANSPORT_IDENTITY_OK"
    assert edge["observed_level"] == "L2_IDENTITY_PRESENT"
    assert edge["trace_propagated"] == "N/E"
    assert edge["receipt_produced"] == "N/E"


def test_witnessed_contract_still_reaches_contract_aligned():
    edge = _base_edge()
    edge["trace_propagated"] = True
    edge["receipt_produced"] = True
    _finish_edge_fields(edge)
    assert edge["overall"] == "CONTRACT_ALIGNED"
    assert edge["observed_level"] == "L2_IDENTITY_PRESENT"


def test_full_semantic_still_governed():
    edge = _base_edge()
    for f in (
        "session_propagated",
        "actor_propagated",
        "trace_propagated",
        "receipt_produced",
    ):
        edge[f] = True
    _finish_edge_fields(edge)
    assert edge["overall"] == "GOVERNED"
    assert edge["observed_level"] == "L4_RECEIPT_CHAINED"


def test_transport_only_stays_transport():
    edge = {"transport": "reachable"}
    _finish_edge_fields(edge)
    assert edge["overall"] == "TRANSPORT_ONLY"
