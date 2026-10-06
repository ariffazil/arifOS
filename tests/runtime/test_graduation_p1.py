"""P1 graduation queue — W³ rank machinery · metric residual · E-letter honesty.

F13 directive "teruskan queue P1" (2026-10-06). Companions:
tests/runtime/test_apex_outcome_semantics.py (the v2 base), receipts in
/root/forge_work/2026-10-06-apex-linalg-eureka/ (GRADUATION-THEORY-v0.1.md).
"""

import sqlite3
import time

import pytest

import arifosmcp.runtime.apex_primitives as ap


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(ap, "_DB_DIR", tmp_path)
    monkeypatch.setattr(ap, "_DB_PATH", tmp_path / "apex_test.db")
    return tmp_path / "apex_test.db"


def _insert_raw(db_path, ts, success, ev, lease, dry, fc=""):
    ap._get_db()  # ensure schema + outcome column exist in the patched tmp path
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO tool_calls (tool_name, timestamp, success, has_evidence,"
        " within_lease, dry_run_first, reversible, failure_code, outcome)"
        " VALUES ('t', ?, ?, ?, ?, ?, 1, ?, '')",
        (ts, int(success), int(ev), int(lease), int(dry), fc),
    )
    conn.commit()
    conn.close()


class TestGramRank:
    def test_rank_field_present_and_bounded(self, tmp_db):
        import random

        rng = random.Random(3)
        for _ in range(40):
            ap.record_tool_call(
                "t",
                success=rng.random() < 0.5,
                has_evidence=rng.random() < 0.5,
                within_lease=rng.random() < 0.5,
                dry_run_first=rng.random() < 0.5,
            )
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        g = m["gram"]
        assert "rank" in g and "effective_dimension" in g and "rank_note" in g
        assert 1 <= g["rank"] <= 4
        assert g["effective_dimension"] == g["rank"]

    def test_collinear_observables_drop_rank(self, tmp_db):
        # evidence always equals lease -> perfect collinearity -> rank < 4
        import random

        rng = random.Random(5)
        for _ in range(60):
            v = rng.random() < 0.5
            ap.record_tool_call(
                "t",
                success=rng.random() < 0.5,
                has_evidence=v,
                within_lease=v,
                dry_run_first=rng.random() < 0.5,
            )
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        g = m["gram"]
        assert "correlation" in g
        # duplicate column -> singular correlation -> rank < columns
        assert g["rank"] == 3
        assert "collinear" in g["rank_note"]


class TestResidualBlock:
    def test_residual_unmeasured_on_empty_prior(self, tmp_db):
        ap.record_tool_call("t", success=True, has_evidence=True)
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        r = m["residual"]
        assert r["measurement_status"] == "UNMEASURED"
        assert r["current_n"] >= 1

    def test_residual_delta_sign(self, tmp_db):
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        past = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 5400)  # inside [−2h, −1h)
        )
        # prior window: low evidence; current window: high evidence
        for _ in range(20):
            _insert_raw(tmp_db, past, True, 0, 1, 1)
        for _ in range(20):
            _insert_raw(tmp_db, now, True, 1, 1, 1)
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        r = m["residual"]
        assert "delta" in r, f"residual={r}"
        assert r["prior"]["P"] == 0.0
        assert r["current"]["P"] == 1.0
        assert r["delta"]["P"] == pytest.approx(1.0)
        assert r["basis"].startswith("persistence")

    def test_residual_G_none_propagates_when_verdict_only_prior(self, tmp_db):
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        past = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 5400)
        )
        _insert_raw(tmp_db, past, False, 0, 1, 0, fc="HOLD")  # verdict-only prior
        for _ in range(10):
            _insert_raw(tmp_db, now, True, 1, 1, 1)
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        r = m["residual"]
        assert r["prior"]["E"] is None and r["prior"]["G"] is None
        assert r["delta"]["G"] is None  # nil propagates, never coerces


class TestEHonesty:
    def test_E_semantics_carries_canon_derived_note(self, tmp_db):
        ap.record_tool_call("t", success=True)
        m = ap.compute_apex_from_metrics(window_seconds=3600)
        assert "CANON_DERIVED" in m["E_semantics"]

    def test_docstring_rename_landed(self):
        import inspect

        doc = inspect.getdoc(ap)
        assert "execution success rate" in doc
        assert "CANON_DERIVED" in doc


class TestW3RankCheck:
    def test_pass_on_independent_streams(self):
        w1 = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7]
        w2 = [0.9, 0.1, 0.8, 0.2, 0.7, 0.3]
        w3 = [0.5, 0.5, 0.1, 0.9, 0.4, 0.6]
        out = ap.w3_rank_check(w1, w2, w3)
        assert out["witnesses_declared"] == 3
        assert out["witnesses_effective"] == 3
        assert out["independence"] == "PASS"

    def test_fail_on_collinear_witnesses(self):
        w1 = [0.1, 0.9, 0.2, 0.8]
        w2 = [x + 0.01 for x in w1]
        w3 = [x - 0.01 for x in w1]
        out = ap.w3_rank_check(w1, w2, w3)
        assert out["witnesses_effective"] < 3
        assert out["independence"] == "FAIL"
        assert "not independence" in out["note"]

    def test_unmeasured_on_single_stream(self):
        assert ap.w3_rank_check([0.1, 0.2])["independence"] == "UNMEASURED"

    def test_fail_on_constant_stream(self):
        out = ap.w3_rank_check([1, 1, 1], [0.1, 0.9, 0.5])
        assert out["independence"] == "FAIL"
