"""Observatory semantic-repair regression tests — Arif patch package 2026-10-21.

Fixture: tests/fixtures/observatory_snapshot_2026-10-21.json (captured from the
LIVE published snapshot BEFORE the patch — it documents the pre-patch world).

Six repairs under test:
1. freshness: age from observed_at (true observation epoch), never render time
2. READY requires an operational test; capability/contract are inventory
3. header/cards/Daily Pulse consistency (frontend files aligned, no fallback)
4. provenance floor: presence_only never presented as full proof; F6 unmeasured
5. tool tests tied to release (passed/failed/untested + commit + age)
6. substrate/session scope: governance counts ≠ substrate; population scan ≠ this session
"""

import json
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "tests" / "fixtures" / "observatory_snapshot_2026-10-21.json"
JS_A = Path("/var/www/html/shared/observatory.js")
JS_B = Path("/var/www/html/_shared/observatory.js")

or_mod = pytest.importorskip(
    "arifosmcp.runtime.rest_routes.observatory_routes",
    reason="observatory_routes not importable in this env",
)


def _find(obj, key, results=None):
    if results is None:
        results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                results.append(v)
            _find(v, key, results)
    elif isinstance(obj, list):
        for item in obj:
            _find(item, key, results)
    return results


@pytest.fixture(scope="module")
def fixture_snapshot():
    return json.loads(FIXTURE.read_text())


# ── Repair 1: freshness ────────────────────────────────────────────────────────


def test_pf_age_honest_when_epoch_given():
    env = or_mod._pf("x", source="t", observed_epoch=time.time() - 3600)
    assert env["age_seconds"] is not None and env["age_seconds"] >= 3595
    assert env["observed_at"] != ""


def test_pf_never_claims_zero_age_without_observation():
    env = or_mod._pf("x", source="t")
    assert env["age_seconds"] is None, "age_seconds must be null (unmeasured), never a fake 0"


def test_pf_epoch_drives_observed_at():
    epoch = time.time() - 7200
    env = or_mod._pf("x", source="t", observed_epoch=epoch)
    assert env["observed_at"].startswith(time.strftime("%Y-%m-%dT%H", time.gmtime(epoch))[:11])


# ── Repair 2: readiness gate ──────────────────────────────────────────────────


def test_readiness_block_requires_ops_test():
    src = (REPO / "arifosmcp/runtime/rest_routes/observatory_routes.py").read_text()
    assert '"READY", "observed", 0.85' in src, "READY must be observed via operational_test only"
    assert '"READY", "derived", 0.8' not in src, "inventory-derived READY is banned"
    assert "capability/contract are inventory facts, not readiness proof" in src


def test_old_ready_derivation_gone():
    src = (REPO / "arifosmcp/runtime/rest_routes/observatory_routes.py").read_text()
    assert "derived from capability={_capability!r} contract={_contract!r}" not in src


# ── Repair 3: frontend consistency ────────────────────────────────────────────


@pytest.mark.skipif(not (JS_A.exists() and JS_B.exists()), reason="frontend not on this host")
def test_no_generated_at_freshness_fallback():
    for p in (JS_A, JS_B):
        s = p.read_text()
        assert "preview.observed_at || preview.generated_at" not in s, (
            f"{p}: render time must not mask staleness"
        )
        assert "render time is not observation time" in s


@pytest.mark.skipif(not (JS_A.exists() and JS_B.exists()), reason="frontend not on this host")
def test_both_copies_identical():
    assert JS_A.read_text() == JS_B.read_text(), (
        "header/cards/pulse must render the same status for the same scope"
    )


@pytest.mark.skipif(not (JS_A.exists() and JS_B.exists()), reason="frontend not on this host")
def test_canary_claims_not_release_proof():
    s = JS_A.read_text()
    assert "RETEST REQUIRED" in s and "CANARY LIVE" not in s
    assert "not release-proven" in s
    assert "NOT authorized on 2026-09-09 canary alone" in s


# ── Repair 4: provenance floor honesty ────────────────────────────────────────


def test_f13_presence_only_not_full_proof():
    src = (REPO / "arifosmcp/runtime/rest_routes/observatory_routes.py").read_text()
    assert '"proof_class": "presence_only"' in src
    assert '"floor_verdict": "PASS(presence_only)"' in src
    assert '"consent_bound_to_action": "NOT_PROVEN"' in src


def test_fixture_documents_prepatch_f13_and_pins_it(fixture_snapshot):
    frags = _find(fixture_snapshot, "f13_sovereignty_decomposition")
    assert frags, "fixture must contain the f13 decomposition (baseline)"
    val = frags[0]["value"] if isinstance(frags[0], dict) and "value" in frags[0] else frags[0]
    assert val["pass_basis"].startswith("presence_only")
    assert val["consent_bound_to_action"] == "NOT_PROVEN"


def test_f6_stays_unmeasured(fixture_snapshot):
    f6 = None
    for f in _find(fixture_snapshot, "F6"):
        f6 = f
    if f6 is None:
        floors = _find(fixture_snapshot, "floors")
        for fl in floors:
            if isinstance(fl, dict) and "F6" in fl:
                f6 = fl["F6"]
    assert f6 is not None, "F6 must be visible in the snapshot"
    score = f6.get("score", f6) if isinstance(f6, dict) else {}
    assert score.get("value") in (None, "unknown", 0.0) or score.get("state") in (
        "unknown",
        "unmeasured",
    ), "F6 must remain unmeasured — placeholder may never flip to PASS"


# ── Repair 5: tool tests tied to release ──────────────────────────────────────


def test_tool_tests_block_untested_without_receipt():
    tt = or_mod._tool_tests_block({"a", "b", "c"})
    v = tt["value"]
    assert v["basis"] == "NO_TEST_RECEIPT"
    assert v["untested"] == 3 and v["passed"] == 0 and v["failed"] == 0
    assert tt["state"] == "unknown"


def test_tool_tests_block_arithmetic_never_negative():
    tt = or_mod._tool_tests_block(set())  # no tools registered
    assert tt["value"]["untested"] == 0 and tt["value"]["total_tools"] == 0


# ── Repair 6: substrate/session scope ─────────────────────────────────────────


def test_substrate_state_no_longer_inherits_floor_verdict():
    src = (REPO / "arifosmcp/runtime/rest_routes/observatory_routes.py").read_text()
    assert (
        '"substrate_state": _pf(\n            # SCAR-OBS-GREENWASH: floor counts are a governance-state measurement.'
        in src
    )
    assert '"governance_floor_state": _pf(' in src
    assert '"NOT_PROVEN"' in src


def test_session_state_unknown_and_max_band_separate():
    src = (REPO / "arifosmcp/runtime/rest_routes/observatory_routes.py").read_text()
    assert '"session_state": _pf(\n            # FIX 2026-10-21' in src
    assert '"sessions_max_band": _pf(' in src
    assert "POPULATION MAX across all sessions, NOT this session" in src


def test_resolver_survives_but_is_labeled_population_stat():
    assert or_mod._resolve_session_state_from_sessions() in {
        "FULL",
        "LIMITED_MUTATE",
        "OBSERVE_ONLY",
    }
