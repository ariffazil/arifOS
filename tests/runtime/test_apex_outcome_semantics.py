"""apex_primitives v2 — outcome-semantics split + Gram observability.

F13 SAH 2026-10-06. Verdict-pollution fix: HOLD/SABAR are constitutional
verdicts, not execution failures. Gram block exposes the second-order
structure the geometric mean discards. EUREKA receipt:
/root/forge_work/2026-10-06-apex-linalg-eureka/
"""

import sqlite3

import pytest

import arifosmcp.runtime.apex_primitives as ap


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "_DB_DIR", tmp_path)
    monkeypatch.setattr(ap, "_DB_PATH", tmp_path / "apex_test.db")
    return tmp_path / "apex_test.db"


def test_derive_outcome_mapping():
    assert ap.derive_outcome(True, "") == ap.OUTCOME_EXECUTION_SUCCESS
    assert ap.derive_outcome(False, "") == ap.OUTCOME_EXECUTION_FAILURE
    assert ap.derive_outcome(False, "HOLD") == ap.OUTCOME_CONSTITUTIONAL_HOLD
    assert ap.derive_outcome(False, "sabar") == ap.OUTCOME_CONSTITUTIONAL_SABAR
    assert ap.derive_outcome(True, "HOLD") == ap.OUTCOME_CONSTITUTIONAL_HOLD


def test_record_stores_derived_outcome(tmp_db):
    ap.record_tool_call("t1", success=False, failure_code="HOLD", has_evidence=True)
    conn = sqlite3.connect(str(tmp_db))
    row = conn.execute("SELECT outcome FROM tool_calls ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row[0] == "constitutional_hold"


def test_E_excludes_verdicts_from_denominator(tmp_db):
    # 3 execution successes, 1 execution failure, 2 constitutional HOLDs.
    for _ in range(3):
        ap.record_tool_call("t", success=True, has_evidence=True, within_lease=True)
    ap.record_tool_call("t", success=False, failure_code="TIMEOUT")
    ap.record_tool_call("t", success=False, failure_code="HOLD")
    ap.record_tool_call("t", success=False, failure_code="HOLD")
    m = ap.compute_apex_from_metrics(window_seconds=3600)
    assert m["E"] == pytest.approx(3 / 4), "E must be 0.75, not the polluted 3/6=0.5"
    ob = m["outcome_breakdown"]
    assert ob["constitutional_hold"]["count"] == 2
    assert ob["execution_success"]["count"] == 3
    assert ob["execution_failure"]["count"] == 1


def test_E_unmeasured_when_only_verdict_traffic(tmp_db):
    ap.record_tool_call("t", success=False, failure_code="HOLD")
    m = ap.compute_apex_from_metrics(window_seconds=3600)
    assert m["E"] is None, "verdict-only window must leave E UNMEASURED"
    assert m["G"] is None, "nil must propagate to G, never coerce"


def test_legacy_rows_derive_at_read_time(tmp_db):
    conn = sqlite3.connect(str(tmp_db))
    ap._get_db()  # ensure schema + outcome column exist
    conn.execute(
        "INSERT INTO tool_calls (tool_name, timestamp, success, has_evidence,"
        " within_lease, dry_run_first, reversible, failure_code, outcome)"
        " VALUES ('legacy', '2026-10-06T00:00:00Z', 0, 1, 1, 0, 1, 'HOLD', '')"
    )
    conn.commit()
    conn.close()
    m = ap.compute_apex_from_metrics(window_seconds=10**9)
    assert m["outcome_breakdown"]["constitutional_hold"]["count"] == 1


def test_gram_block_reports_structure(tmp_db):
    # 40 rows where evidence co-travels with lease; execution_success varies.
    import random

    rng = random.Random(7)
    for i in range(40):
        healthy = rng.random() < 0.6
        ap.record_tool_call(
            "t",
            success=rng.random() < 0.5,
            has_evidence=healthy,
            within_lease=healthy,
            dry_run_first=rng.random() < 0.5,
        )
    m = ap.compute_apex_from_metrics(window_seconds=3600)
    g = m["gram"]
    assert "correlation" in g, f"gram missing: {g}"
    assert len(g["columns"]) == 4
    assert len(g["eigenvalues"]) == 4
    # ρ(lease, evidence) must be strongly positive by construction
    corr = g["correlation"]
    i_lease = g["columns"].index("A_within_lease")
    i_ev = g["columns"].index("P_has_evidence")
    assert corr[i_lease][i_ev] > 0.5
    assert "epistemic" in g


def test_gram_unmeasured_below_min_n(tmp_db):
    for _ in range(5):
        ap.record_tool_call("t", success=True)
    m = ap.compute_apex_from_metrics(window_seconds=3600)
    assert m["gram"]["measurement_status"] == "UNMEASURED"


def test_G_formula_unchanged_on_pure_execution_traffic(tmp_db):
    # When there is no verdict traffic, v2 E == v1 E and G is the same math.
    ap.record_tool_call("t", success=True, has_evidence=True, within_lease=True, dry_run_first=True)
    ap.record_tool_call("t", success=False, has_evidence=False, within_lease=True, dry_run_first=False)
    m = ap.compute_apex_from_metrics(window_seconds=3600)
    assert m["E"] == pytest.approx(0.5)
    expected_g = (1.0 * 0.5 * 0.5 * 0.5) ** 0.25  # A=1, P=.5, E=.5, X=.5
    assert m["G"] == pytest.approx(expected_g, rel=1e-3)
