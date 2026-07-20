"""Semantic edge states for federation Observatory.

Transport reachability is not governance. Promote edges only after spine checks.

States:
  UNTESTED | TRANSPORT_ONLY | SCHEMA_ALIGNED | CONTEXT_ALIGNED | GOVERNED | FAILED
"""

from __future__ import annotations

from typing import Any

from arifosmcp.contracts.handoff_v1 import (
    EpistemicState,
    SessionAuthority,
    admit_handoff,
    chain_continuity,
    handoff_to_dict,
    new_handoff,
    wealth_must_not_overwrite_geology,
)

SEMANTIC_STATES = (
    "UNTESTED",
    "TRANSPORT_ONLY",
    "SCHEMA_ALIGNED",
    "CONTEXT_ALIGNED",
    "GOVERNED",
    "FAILED",
)

# Priority paths for v2026.07.18-SEMANTIC-BRIDGE
PRIORITY_PATHS = (
    ("GEOX", "WEALTH"),
    ("WEALTH", "WELL"),
    ("ARIFOS", "A-FORGE"),
)


def classify_edge(
    *,
    transport_ok: bool,
    identity_matched: bool | str,
    schema_accepted: bool | str,
    session_propagated: bool | str,
    actor_propagated: bool | str,
    trace_propagated: bool | str,
    epistemic_preserved: bool | str,
    receipt_produced: bool | str,
    handoff_admitted: bool | None = None,
) -> str:
    def truthy(v: Any) -> bool:
        return v is True

    def ne(v: Any) -> bool:
        return v in (None, "N/E", "UNTESTED")

    if transport_ok is False:
        return "FAILED"
    if not transport_ok:
        return "UNTESTED"

    # Hard failures (identity/schema rejected)
    if identity_matched is False or schema_accepted is False:
        return "FAILED"

    spine_ctx = [
        session_propagated,
        actor_propagated,
        trace_propagated,
        epistemic_preserved,
    ]
    # receipt_produced=False means incomplete, not FAILED
    if all(ne(x) for x in [identity_matched, schema_accepted, *spine_ctx, receipt_produced]):
        return "TRANSPORT_ONLY"

    if any(x is False for x in spine_ctx):
        return "FAILED"

    if truthy(schema_accepted) and all(truthy(x) for x in spine_ctx):
        if truthy(receipt_produced) and handoff_admitted is True:
            return "GOVERNED"
        return "CONTEXT_ALIGNED"

    if truthy(schema_accepted):
        return "SCHEMA_ALIGNED"

    if transport_ok:
        return "TRANSPORT_ONLY"
    return "UNTESTED"


def enrich_edge_semantic_state(edge: dict[str, Any]) -> dict[str, Any]:
    """Add semantic_state to an existing transport edge row."""
    transport_ok = edge.get("transport") in ("reachable", "up")
    state = classify_edge(
        transport_ok=transport_ok,
        identity_matched=edge.get("identity_match"),
        schema_accepted=edge.get("schema_match"),
        session_propagated=edge.get("session_propagated"),
        actor_propagated=edge.get("actor_propagated"),
        trace_propagated=edge.get("trace_propagated"),
        epistemic_preserved=edge.get("epistemic_preserved", "N/E"),
        receipt_produced=edge.get("receipt_produced"),
        handoff_admitted=edge.get("handoff_admitted"),
    )
    edge["semantic_state"] = state
    # Do not paint GOVERNED green without full spine
    edge["color_hint"] = {
        "UNTESTED": "grey",
        "TRANSPORT_ONLY": "blue",
        "SCHEMA_ALIGNED": "amber",
        "CONTEXT_ALIGNED": "amber",
        "GOVERNED": "green",
        "FAILED": "red",
    }.get(state, "grey")
    return edge


def simulate_priority_handoffs(
    *,
    actor_id: str = "arif",
    actor_verified: bool = True,
    session_id: str = "SEAL-TEST-SESSION",
    trace_id: str = "trace-semantic-bridge-001",
) -> dict[str, Any]:
    """Run in-process GEOX→WEALTH, WEALTH→WELL, composite → judge admission.

    This is a contract simulation (F2: not live organ mutation).
    """
    # 1) GEOX → WEALTH
    geox_ev = {
        "ref": "geox://prospect/demo-basin/alpha",
        "type": "earth_measurement",
        "hash": "sha256:demo_geox_evidence_001",
        "owner_organ": "GEOX",
    }
    h1 = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id=actor_id,
        actor_verified=actor_verified,
        session_id=session_id,
        authority=SessionAuthority.ADVISORY,
        claim_summary="Prospect Alpha volumetric range OBSERVED under uncertainty.",
        epistemic_state=EpistemicState.OBSERVED,
        confidence=0.72,
        evidence=[geox_ev],
        requested_output="capital_scenario",
        trace_id=trace_id,
        unknown=["seal_integrity", "fiscal_terms"],
    )
    a1 = admit_handoff(h1)

    # WEALTH computes without revising geology
    wealth_output = {
        "capital_consequence": {"npv_band": [10.0, 40.0], "currency": "USD_mm"},
        # must NOT include geology revision
    }
    viol = wealth_must_not_overwrite_geology(h1, wealth_output)
    # negative test: overwriting geology fails
    viol_bad = wealth_must_not_overwrite_geology(
        h1, {"geology": {"rewritten": True}, **wealth_output}
    )

    # 2) WEALTH → WELL (minimum necessary fields)
    h2 = new_handoff(
        source_organ="WEALTH",
        target_organ="WELL",
        intent="reflect_operator_capacity_for_commitment",
        actor_id=actor_id,
        actor_verified=actor_verified,
        session_id=session_id,
        authority=SessionAuthority.REFLECT_ONLY,
        claim_summary="Capital scenario requires multi-year commitment attention.",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.65,
        evidence=[
            {
                "ref": "wealth://scenario/demo-alpha",
                "type": "capital_scenario_summary",
                "hash": "sha256:demo_wealth_001",
                "owner_organ": "WEALTH",
            }
        ],
        requested_output="capacity_reflection",
        trace_id=trace_id,
        unknown=["operator_sleep_debt"],
    )
    a2 = admit_handoff(h2)

    # forbidden field to WELL
    h2_bad = new_handoff(
        source_organ="WEALTH",
        target_organ="WELL",
        intent="reflect_operator_capacity_for_commitment",
        actor_id=actor_id,
        actor_verified=actor_verified,
        session_id=session_id,
        authority=SessionAuthority.REFLECT_ONLY,
        claim_summary="should hold",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.5,
        evidence=[
            {
                "ref": "wealth://private/ledger",
                "type": "raw_capital_ledger",
                "hash": "sha256:bad",
                "owner_organ": "WEALTH",
            }
        ],
        requested_output="capacity_reflection",
        trace_id=trace_id,
    )
    a2_bad = admit_handoff(h2_bad)

    # 3) WELL → ARIFOS judge
    h3 = new_handoff(
        source_organ="WELL",
        target_organ="ARIFOS",
        intent="request_judgment",
        actor_id=actor_id,
        actor_verified=actor_verified,
        session_id=session_id,
        authority=SessionAuthority.JUDGE,
        claim_summary="Composite GEOX→WEALTH→WELL package ready for judgment.",
        epistemic_state=EpistemicState.INTERPRETED,
        confidence=0.60,
        evidence=[
            geox_ev,
            {
                "ref": "wealth://scenario/demo-alpha",
                "type": "capital_scenario_summary",
                "hash": "sha256:demo_wealth_001",
                "owner_organ": "WEALTH",
            },
            {
                "ref": "well://reflect/demo",
                "type": "vitality_reflection",
                "hash": "sha256:demo_well_001",
                "owner_organ": "WELL",
            },
        ],
        requested_output="judgment",
        trace_id=trace_id,
    )
    a3 = admit_handoff(h3)

    # missing evidence → HOLD
    h_hold = new_handoff(
        source_organ="GEOX",
        target_organ="WEALTH",
        intent="evaluate_capital_consequence",
        actor_id=actor_id,
        actor_verified=actor_verified,
        session_id=session_id,
        authority=SessionAuthority.ADVISORY,
        claim_summary="no evidence",
        epistemic_state=EpistemicState.SPECULATIVE,
        confidence=0.4,
        evidence=[],
        requested_output="capital_scenario",
        trace_id=trace_id,
    )
    a_hold = admit_handoff(h_hold)

    # A-FORGE without judgment → HOLD
    h_forge = new_handoff(
        source_organ="ARIFOS",
        target_organ="A-FORGE",
        intent="execute_mutation",
        actor_id=actor_id,
        actor_verified=True,
        session_id=session_id,
        authority=SessionAuthority.OBSERVE_ONLY,
        claim_summary="attempt execute without seal",
        epistemic_state=EpistemicState.DERIVED,
        confidence=0.5,
        evidence=[{"ref": "x", "type": "plan", "hash": "sha256:x"}],
        requested_output="mutation",
        trace_id=trace_id,
    )
    a_forge = admit_handoff(h_forge)

    cont = chain_continuity([h1, h2, h3])

    # edge semantic classifications for priority paths
    edges = {
        "GEOX→WEALTH": classify_edge(
            transport_ok=True,
            identity_matched=True,
            schema_accepted=a1.admitted,
            session_propagated=True,
            actor_propagated=True,
            trace_propagated=True,
            epistemic_preserved=True,
            receipt_produced=False,
            handoff_admitted=a1.admitted,
        ),
        "WEALTH→WELL": classify_edge(
            transport_ok=True,
            identity_matched=True,
            schema_accepted=a2.admitted,
            session_propagated=True,
            actor_propagated=True,
            trace_propagated=True,
            epistemic_preserved=True,
            receipt_produced=False,
            handoff_admitted=a2.admitted,
        ),
        "ARIFOS→A-FORGE": classify_edge(
            transport_ok=True,
            identity_matched=True,
            schema_accepted=False,
            session_propagated="N/E",
            actor_propagated="N/E",
            trace_propagated="N/E",
            epistemic_preserved="N/E",
            receipt_produced=False,
            handoff_admitted=a_forge.admitted,
        ),
    }

    return {
        "schema": "arifos.semantic_bridge_test.v1",
        "release_intent": "v2026.07.18-SEMANTIC-BRIDGE",
        "note": "Contract simulation — not live organ mutation. Federation not semantically complete until live edge probes pass.",
        "handoffs": {
            "geox_to_wealth": {
                "envelope": handoff_to_dict(h1),
                "admission": a1.model_dump(),
                "wealth_overwrite_violations": viol,
                "wealth_overwrite_negative_test_violations": viol_bad,
            },
            "wealth_to_well": {
                "envelope": handoff_to_dict(h2),
                "admission": a2.model_dump(),
                "forbidden_field_admission": a2_bad.model_dump(),
            },
            "composite_to_judge": {
                "envelope": handoff_to_dict(h3),
                "admission": a3.model_dump(),
            },
            "missing_evidence_hold": a_hold.model_dump(),
            "aforge_without_judgment": a_forge.model_dump(),
        },
        "continuity": cont,
        "priority_edge_semantic_states": edges,
        "receipt_verify_url": "https://arif-fazil.com/999/",
        "acceptance": {
            "geox_accepted_by_wealth": a1.admitted and not viol,
            "wealth_cannot_overwrite_geology": len(viol_bad) > 0,
            "well_min_fields": not a2_bad.admitted,
            "actor_continuous": cont.get("actor_id") == actor_id,
            "session_continuous": cont.get("ok") is True,
            "trace_continuous": cont.get("trace_id") == trace_id,
            "missing_evidence_hold": a_hold.verdict == "HOLD",
            "aforge_blocked_without_judgment": a_forge.verdict == "HOLD",
        },
    }
