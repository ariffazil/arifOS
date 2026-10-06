"""SCAR-OBS-GREENWASH regression guard (2026-10-03, FI-003).

Pins the removal of the synthetic-evidence injection that lived in
``rest_routes._build_governance_status_payload()``. That block fired whenever
four or more runtime signals were visible and did three things:

    apply_temporal_grounding(human=0.42, ai=0.99, earth=0.99)   # two hardcoded
    record_event("action", {...})  + record_event("success", {...})  # synthetic
    floors/telemetry/witness/qdf/verdict = <re-read state>       # overwrite

Measured effect on the public observatory: F2 0.5->1.0, F3 0.0->0.9299,
F5 0.5->1.0, F6 0.5->1.0, substrate_state FAIL->PASS, floors 9/4 -> 13/0.
F3 is reproducible in closed form as
``3*(0.42*0.99*0.99)**(1/3)/(0.42+0.99+0.99) = 0.929858``.

Two properties made it worse than a display bug: ``GovernanceKernel._event_log``
is never cleared, so the process-global singleton ratcheted and one call
poisoned every later call; and ``reality_scoring.probe_governance_kernel_events``
detects flat scores via ``event_count == 0 and peace2 == 0.5``, so the injected
events silenced the federation's own emptiness detector.

Every test here fails if any part of that returns.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.rest_routes import rest_routes as rr
from core.governance_kernel import clear_governance_kernel, get_governance_kernel

# The fabricated tri-witness coherence, in closed form, from the two hardcoded
# witness values the injection used (ai=0.99, earth=0.99) plus the sovereign
# default for human (0.42). Rounded to what the API published.
FABRICATED_WITNESS_COHERENCE = 0.9299
HARDCODED_WITNESS_TRIPLE = {"human": 0.42, "ai": 0.32, "earth": 0.26}


@pytest.fixture(autouse=True)
def _pristine_global_kernel():
    """Start and end from an empty global kernel so assertions are not polluted
    by other tests in the session (the singleton is process-wide)."""
    clear_governance_kernel()
    yield
    clear_governance_kernel()


def test_building_payload_does_not_grow_the_global_event_log():
    """The ratchet. A display endpoint must not write governance state.

    Previously each call appended 1 + 2*len(live_signals) synthetic events to the
    process-global kernel and never cleared them, so floor scores rose with
    every read and could never decay back to honest.
    """
    kernel = get_governance_kernel()
    before = len(kernel._event_log)

    rr._build_governance_status_payload()
    rr._build_governance_status_payload()

    after = len(kernel._event_log)
    assert after == before, (
        f"_build_governance_status_payload() mutated the global governance "
        f"kernel event log ({before} -> {after} events). A DISPLAY endpoint "
        f"must never inject evidence into constitutional state."
    )


def test_witness_is_never_substituted_with_the_hardcoded_triple():
    """_WITNESS_DEFAULTS is a documented sovereign split, not a measurement.

    The old comprehension substituted it whenever a real witness was missing OR
    exactly 0.0, so 'no witness at all' published as a healthy 42/32/26 split.
    """
    payload = rr._build_governance_status_payload()
    witness = payload["witness"]
    provenance = payload["witness_provenance"]

    injected = {k: round(float(witness.get(k, 0.0)), 4) for k in HARDCODED_WITNESS_TRIPLE}
    assert injected != HARDCODED_WITNESS_TRIPLE, (
        f"published witness equals the hardcoded _WITNESS_DEFAULTS triple "
        f"{HARDCODED_WITNESS_TRIPLE} — fabricated weight, not a measurement"
    )
    # With an empty kernel there is no witness signal, and the payload must say so.
    assert set(provenance) == set(HARDCODED_WITNESS_TRIPLE)
    for key, origin in provenance.items():
        if float(witness.get(key) or 0.0) == 0.0:
            assert origin == "unmeasured", (
                f"witness.{key} is 0.0 but labelled '{origin}' — absence must be "
                f"labelled unmeasured, never dressed as a real weight"
            )


def test_no_floor_publishes_the_fabricated_coherence_constant():
    """Tripwire on the exact number the injection produced."""
    payload = rr._build_governance_status_payload()
    for fid, score in (payload.get("floors") or {}).items():
        if score is None:
            continue
        assert abs(float(score) - FABRICATED_WITNESS_COHERENCE) > 1e-4, (
            f"floor {fid} published {score}, the closed-form output of the "
            f"hardcoded (0.42, 0.99, 0.99) witness triple"
        )


def test_empty_signal_floors_are_labelled_unmeasured(monkeypatch):
    """A structural baseline is a placeholder, not a score.

    On an empty event log evaluate_floors returns tau_truth 0.5, peace2 0.5,
    kappa_r 0.5, witness_coherence 0.0, shadow 0.0. Those must be labelled so no
    consumer renders them green.

    Hermetic (2026-10-06): human-witness ledgers now EXIST on this machine
    (landed 2026-10-05 via F13 directive, /var/lib/*/human_witness.jsonl),
    so collect_witness_legs() returns live legs and F3 is legitimately
    attributed to witness_producers — this test must CONSTRUCT the
    empty-signal scenario, not inherit whatever the machine has on disk.
    """
    import arifosmcp.runtime.witness_producers as _wp

    monkeypatch.setattr(
        _wp,
        "collect_witness_legs",
        lambda: {
            "legs": {},
            "coherence": None,
            "measured": 0,
            "total": 3,
            "complete": False,
            "blocking_legs": ["human", "ai", "earth"],
        },
    )
    payload = rr._build_governance_status_payload()
    provenance = payload["floor_provenance"]
    basis = payload["measurement_basis"]

    assert basis["event_count"] == 0
    assert basis["witness_sum"] == 0.0
    for fid in ("F2", "F3", "F5", "F6"):
        assert fid in basis["unmeasured_floors"], (
            f"{fid} has no input signal but is not listed unmeasured"
        )
        assert provenance[fid].startswith("unmeasured_default"), (
            f"{fid} provenance is '{provenance[fid]}' — an empty-signal floor "
            f"must never be attributed to a live measurement"
        )


def test_threshold_placeholder_floors_are_labelled_unmeasured():
    """_FLOOR_DEFAULTS comes from _representative_floor_score(), which returns
    the floor's own passing threshold, so it can never fail. Floors that fall
    back to it must be labelled rather than published as measured."""
    payload = rr._build_governance_status_payload()
    provenance = payload["floor_provenance"]

    placeholders = [f for f, o in provenance.items() if o.startswith("unmeasured_default")]
    assert placeholders, "expected at least one threshold-placeholder floor on an empty kernel"
    # L10/L11/L13 have no producer in evaluate_floors at all, so they always fall
    # back to the auto-pass threshold.
    for fid in ("L10", "L11", "L13"):
        assert provenance[fid].startswith("unmeasured_default"), (
            f"{fid} has no producer but is labelled '{provenance[fid]}'"
        )


def test_observatory_renders_unmeasured_not_pass():
    """End-to-end: the published observatory block must be three-state, and
    substrate_state must not read PASS while floors are unmeasured."""
    from arifosmcp.runtime.rest_routes import observatory_routes as obs

    block = obs._governance_block()
    statuses = {fid: f["status"]["value"] for fid, f in block["floors"].items()}

    assert "unmeasured" in statuses.values(), (
        f"no floor rendered 'unmeasured' — statuses were {statuses}"
    )
    for fid, status in statuses.items():
        if status == "unmeasured":
            assert block["floors"][fid]["score"]["value"] is None, (
                f"{fid} is unmeasured but still publishes a numeric score"
            )

    assert block["floors_unmeasured"]["value"] > 0
    substrate = block["verdict_decomposition"]["substrate_state"]["value"]
    assert substrate != "PASS", (
        f"substrate_state is PASS while "
        f"{block['floors_unmeasured']['value']} floors are unmeasured — "
        f"'no data' must never render as 'all clear' (Void Guard)"
    )
