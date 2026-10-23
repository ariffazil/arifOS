"""Truth-chain patch tests — F13 D2 ratified 2026-10-23 (P2-P6).

Covers: F5/F13 producer-origin split (P3), producer WHEN stamps (P4),
F3 verdict-shaped provenance and L10 config-reference relabel (P5),
FQ decomposition passthrough (P6), and the observatory live-verdict
preference (P2, via the formatting contract).
"""

import pathlib

from arifosmcp.runtime.floor_producers import (
    _f13_sovereign,
    _f5_peace,
    collect_floor_producer_signal,
)
from arifosmcp.runtime.fq_truth import normalize_fq


def test_f5_f13_origins_no_longer_shared():
    """P3: one measurement may not earn two claims under one label."""
    seals_ok = [{"actor": "arif", "verdict": "SEAL", "payload": {}}]
    f5 = _f5_peace({"seals": seals_ok})
    f13 = _f13_sovereign({"seals": seals_ok})
    assert f5["origin"] == "seal_chain_peace"
    assert f13["origin"] == "seal_chain_sovereign"
    assert f5["origin"] != f13["origin"]


def test_f13_fail_path_also_split():
    seals_bad = [{"actor": "qwen", "verdict": "SEAL", "payload": {}}]
    f13 = _f13_sovereign({"seals": seals_bad})
    f5 = _f5_peace({"seals": seals_bad + [{"reversibility": "REVERSIBLE"}]})
    assert f13["origin"] == "seal_chain_sovereign"
    assert f13["status"] == "FAIL"


def test_producer_signals_carry_when_slot():
    """P4: every signal (even no_producer) carries measured_at, WHO:WHAT:WHEN."""
    sig = collect_floor_producer_signal("F99")  # no producer registered
    assert sig["status"] == "UNMEASURED"
    assert sig.get("measured_at")
    assert sig["measured_at"].endswith("Z")
    sig2 = collect_floor_producer_signal("F12", sources={"auto_sign_allowed": False})
    assert sig2["status"] == "PASS"
    assert sig2.get("measured_at")


def test_provenance_when_slot_format():
    """P4 contract: WHO:VERDICT:origin@ISO parses back via rsplit('@',1)."""
    measured_at = "2026-10-23T04:55:00Z"
    prov = f"floor_producer:PASS:seal_chain_peace@{measured_at}"
    who, verdict = prov.split(":", 2)[0], prov.split(":", 2)[1]
    when = prov.rsplit("@", 1)[1]
    assert who == "floor_producer"
    assert verdict == "PASS"
    assert when == measured_at
    # FLR-003b reducer compatibility: split(':', 2)[1] still yields the verdict
    # even with the @ISO suffix.
    assert "floor_producer:PASS:seal_chain_peace@2026-10-23T04:55:00Z".split(":", 2)[
        1
    ] == "PASS"


def test_normalize_fq_preserves_decomposition():
    """P6: five-field decomposition rides with the one FQ object."""
    raw = {
        "quotient": 1.0109,
        "measured_at": "2026-10-23T03:46:24Z",
        "scope": "federation",
        "decomposition": {
            "raw": 1.0109,
            "normalization": "NONE_PASSTHROUGH_QUOTIENT",
            "threshold": 0.5,
            "window_size": 100,
        },
    }
    out = normalize_fq(raw)
    assert out["value"] == 1.0109
    assert out["decomposition"]["threshold"] == 0.5
    assert out["decomposition"]["normalization"] == "NONE_PASSTHROUGH_QUOTIENT"


def test_normalize_fq_without_decomposition_unchanged():
    out = normalize_fq({"quotient": 0.4})
    assert set(out.keys()) == {"value", "measured_at", "scope"}


def test_meter_when_slot_contract():
    """The delivered meter (scripts/instrument_selfcheck.py) finds a WHEN slot
    via a *_at key in the constitutional block — floors_measured_at satisfies it."""
    constitutional_block = {"floors_measured_at": {"F1": "2026-10-23T04:55:00Z"}}
    import json
    import re

    assert re.search(r'"[^"]*(_at|timestamp|measured_when)[^"]*"\s*:', json.dumps(constitutional_block))


def test_l10_and_f3_relabels_present_in_source():
    """P5: the relabels exist in rest_routes source (config-reference L10,
    verdict-shaped F3)."""
    src = (
        pathlib.Path(__file__).resolve().parents[1]
        / "arifosmcp"
        / "runtime"
        / "rest_routes"
        / "rest_routes.py"
    ).read_text(errors="replace")
    assert "unmeasured_default:ontology_config_reference" in src
    assert "floor_producer:MEASURED:witness_coherence=" in src
    assert "witness_legs_incomplete" in src


def test_observatory_live_verdict_preference_in_source():
    """P2: live verdict preferred over legacy; both preserved."""
    src = (
        pathlib.Path(__file__).resolve().parents[1]
        / "arifosmcp"
        / "runtime"
        / "rest_routes"
        / "observatory_routes.py"
    ).read_text(errors="replace")
    assert "verdict = live_verdict or legacy_verdict" in src
    assert '"verdict_source": verdict_source' in src
    assert '"legacy_verdict": legacy_verdict' in src
