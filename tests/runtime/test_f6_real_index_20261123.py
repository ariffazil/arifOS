"""F6 MARUAH — the REAL v0 index on the served surface (F13 GO A, 2026-11-23).

Base: the R1 implementation already live in arifOS (commit c8f5d9faa) — a covered
reading with no observable flow answers UNMEASURED with no score, instead of a
measured fail carrying the old hard-coded 0.5 placeholder.

This file pins the half that was still missing: **the flow leg is now OBSERVABLE**.
When the served /health carries consequence_flow (the age of the newest REAL
receipt) and dignity_surface, the producer computes the REAL v0 index

    f6_index = 0.5 + 0.5 * flow_factor,   flow_factor = 1 - age / band

recomputed here from the age it was given — a `covered` flag in the payload is
never trusted on its own. With the legs absent, the R1 branch is untouched.

Base commit: c8f5d9faa
Proposal: /root/forge_work/proposals/PROPOSAL-F6-REAL-INDEX-AND-HUMAN-CADENCE-20261123.md
"""

from __future__ import annotations

from arifosmcp.runtime.floor_producers import _f6_maruah


def _wh(
    truth: str = "OPERATOR_REPORTED",
    age: object = 600.0,
    cap: object = 14400.0,
    environment: str = "PROD",
    mock: bool = False,
    source_type: str = "OPERATOR_REPORTED",
    consequence_flow: dict | None = None,
    dignity_surface: dict | None = None,
    served_legs: bool = True,
) -> dict:
    payload = {
        "truth_status": truth,
        "environment": environment,
        "freshness": {
            "age_seconds": age,
            "stale_after_seconds": cap,
            "expired_after_seconds": cap,
        },
        "honesty": {"source_type": source_type, "is_mock_or_test": mock},
    }
    if consequence_flow is not None:
        payload["consequence_flow"] = consequence_flow
    elif served_legs:
        payload["consequence_flow"] = _flow(0.0)
    if dignity_surface is not None:
        payload["dignity_surface"] = dignity_surface
    elif served_legs:
        payload["dignity_surface"] = {
            "covered": True,
            "guard": "Ω-WELL-12 well_guard_dignity (canonical server.py)",
        }
    return payload


def _flow(age_s: float | None, band_s: float = 86400.0, covered: bool | None = None) -> dict:
    return {
        "covered": covered if covered is not None else (age_s is not None and age_s <= band_s),
        "last_receipt_age_s": age_s,
        "band_seconds": band_s,
    }


# ── the new capability: a served flow leg yields the REAL v0 index ─────────


def test_served_flow_leg_yields_the_real_v0_index() -> None:
    """0.5 + 0.5*flow, flow = 1 - age/band. A fresh receipt (age 0) -> 1.0."""
    sig = _f6_maruah({"well_health": _wh(consequence_flow=_flow(0.0))})
    assert sig["status"] == "MEASURED"
    assert sig["f6_index"] == 1.0
    assert sig["null_reasons"] == []
    cov = sig["coverage"]["consequence_flow"]
    assert cov["served"] is True
    assert cov["covered"] is True
    assert cov["flow_factor"] == 1.0


def test_served_flow_leg_index_decays_with_age() -> None:
    """A 12h-old receipt must land below a fresh one — the index is a
    measurement, not a painted constant."""
    fresh = _f6_maruah({"well_health": _wh(consequence_flow=_flow(0.0))})
    aged = _f6_maruah({"well_health": _wh(consequence_flow=_flow(12 * 3600.0))})
    assert aged["f6_index"] < fresh["f6_index"]
    assert aged["f6_index"] == 0.75  # 0.5 + 0.5 * (1 - 12/24)


def test_flow_is_recomputed_never_trusted() -> None:
    """The kernel recomputes covered/factor from the AGE it is given. A block
    that CLAIMS covered=True with a stale age must not unlock the floor."""
    sig = _f6_maruah(
        {"well_health": _wh(consequence_flow=_flow(30 * 3600.0, covered=True))}
    )
    assert sig["status"] == "UNMEASURED"
    assert sig["f6_index"] is None
    assert any("consequence_flow" in r for r in sig["null_reasons"]), sig["null_reasons"]


def test_stale_flow_leg_names_the_reason() -> None:
    """When the leg IS served but carries no receipt in band, the reason says
    that — not 'unobservable'. The served surface told us; what it told us was
    that no reality has entered the substrate."""
    sig = _f6_maruah({"well_health": _wh(consequence_flow=_flow(25 * 3600.0))})
    assert sig["status"] == "UNMEASURED"
    assert sig["f6_index"] is None
    joined = " ".join(sig["null_reasons"])
    assert "no real receipt" in joined, sig["null_reasons"]
    assert "unobservable" not in joined, sig["null_reasons"]


def test_missing_receipt_age_is_not_a_covered_flow() -> None:
    sig = _f6_maruah({"well_health": _wh(consequence_flow=_flow(None))})
    assert sig["status"] == "UNMEASURED"
    assert any("consequence_flow" in r for r in sig["null_reasons"])


# ── the dignity leg ────────────────────────────────────────────────────────


def test_dignity_surface_not_covered_blocks() -> None:
    sig = _f6_maruah(
        {
            "well_health": _wh(
                consequence_flow=_flow(0.0),
                dignity_surface={"covered": False, "guard": "Ω-WELL-12 well_guard_dignity"},
            )
        }
    )
    assert sig["status"] == "UNMEASURED"
    assert sig["f6_index"] is None
    assert any("dignity_surface" in r for r in sig["null_reasons"]), sig["null_reasons"]


def test_dignity_surface_covered_keeps_the_floor_covered() -> None:
    sig = _f6_maruah(
        {
            "well_health": _wh(
                consequence_flow=_flow(0.0),
                dignity_surface={"covered": True, "guard": "Ω-WELL-12 well_guard_dignity"},
            )
        }
    )
    assert sig["status"] == "MEASURED"
    assert sig["f6_index"] == 1.0


# ── the R1 fallback is untouched when the legs are absent ──────────────────


def test_absent_legs_keep_the_r1_fallback() -> None:
    """F13 R1: F6 UNMEASURED is not a measured fail. With no served legs the
    producer keeps the live R1 branch — UNMEASURED, no score, reason named."""
    sig = _f6_maruah({"well_health": _wh(served_legs=False)})
    assert sig["status"] == "UNMEASURED"
    assert sig["f6_index"] is None
    assert sig["verdict"] == "INSTRUMENTED_COVERAGE_INSUFFICIENT"
    assert sig["origin"] == "well_health:f6_v0_partial:evidence_missing@age=600s"
    assert any("unobservable" in r for r in sig["null_reasons"]), sig["null_reasons"]
    assert sig["coverage"]["consequence_flow"]["served"] is False
    assert sig["coverage"]["dignity_surface"]["served"] is False


def test_absent_legs_keep_stale_semantics() -> None:
    """A stale substrate still reads STALE (an honest age), with no score."""
    stale = _f6_maruah({"well_health": _wh(age=17803.6, served_legs=False)})
    assert stale["status"] == "STALE"
    assert stale["origin"] == "well_health:stale_substrate"
    assert stale["f6_index"] is None
    assert any("17804s" in r or "age" in r for r in stale["null_reasons"]), stale["null_reasons"]


def test_missing_truth_still_unmeasured_with_reason() -> None:
    uncovered = _f6_maruah({"well_health": _wh(truth="INSUFFICIENT_DATA", served_legs=False)})
    assert uncovered["status"] == "UNMEASURED"
    assert uncovered["origin"] == "well_health:coverage_insufficient"
    assert any("truth=INSUFFICIENT_DATA" in r for r in uncovered["null_reasons"])


def test_seal_coercion_still_wins_over_a_real_index() -> None:
    """A MEASURED, high index must never average away a declared coercion."""
    sig = _f6_maruah(
        {
            "well_health": _wh(consequence_flow=_flow(0.0)),
            "seals": [
                {
                    "actor": "888",
                    "payload": {"heart_critique": {"coercion": True}},
                }
            ],
        }
    )
    assert sig["status"] == "FAIL"
    assert sig["origin"] == "heart_critique"
    assert sig["reason"] == "coercion_present"
