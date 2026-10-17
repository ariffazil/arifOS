"""QRL increment-1 tests: qrl_collapse (deterministic judge modes + prediction sink).

Every positive case has a paired negative case (F13 discipline: malformed
input / missing field must yield HOLD/inconclusive, never SEAL).
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.tools.qrl_collapse import (
    DEFAULT_PREDICTION_SINK,
    collapse_verdict,
    hard_floor_veto,
    score_candidate,
    soft_score,
    write_prediction_record,
)


# ── F2 (scope 4): veto rules — every irreversible candidate yields HOLD/VOID ──


class TestHardFloorVeto:
    def test_irreversible_action_class_vetoes(self):
        fired = hard_floor_veto(action_class="IRREVERSIBLE", actor_verified=True)
        assert any(v["floor"] == "F1" for v in fired)

    def test_irreversible_reversibility_vetoes(self):
        fired = hard_floor_veto(reversibility_level="irreversible", actor_verified=True)
        assert any(v["floor"] == "F1" for v in fired)

    def test_irreversible_without_sovereign_adds_f13(self):
        fired = hard_floor_veto(action_class="IRREVERSIBLE", sovereign_receipt=None)
        assert any(v["floor"] == "F13" for v in fired)

    def test_federation_mutation_vetoes(self):
        fired = hard_floor_veto(
            action_class="MUTATE", blast_radius="federation", actor_verified=True
        )
        assert any(v["floor"] == "F1" and v["rule"] == "federation_mutation" for v in fired)

    def test_unverified_actor_mutation_vetoes_f11(self):
        fired = hard_floor_veto(action_class="MUTATE", actor_verified=False)
        assert any(v["floor"] == "F11" for v in fired)

    def test_spec_claim_vetoes_f2(self):
        fired = hard_floor_veto(claim_class="SPEC", actor_verified=True)
        assert any(v["floor"] == "F2" for v in fired)

    # negative: benign read-only candidate must NOT fire anything
    def test_benign_observe_no_veto(self):
        fired = hard_floor_veto(
            action_class="OBSERVE",
            reversibility_level="reversible",
            blast_radius="self",
            actor_verified=False,
        )
        assert fired == []

    # negative: malformed / empty inputs → no crash, no silent veto-less pass on mutations
    @pytest.mark.parametrize("bad", [None, "", 123, {"x": 1}])
    def test_malformed_fields_never_crash(self, bad):
        fired = hard_floor_veto(
            action_class=bad, reversibility_level=bad, blast_radius=bad, actor_verified=False
        )
        assert isinstance(fired, list)


class TestSoftScore:
    def test_score_bounds_and_formula(self):
        r = soft_score(p_success=0.8, reversibility_level="reversible", blast_radius="self")
        assert -1.0 <= r["S"] <= 1.0
        assert r["S"] == pytest.approx(0.8)

    def test_irreversibility_drags_score(self):
        good = soft_score(p_success=0.8, reversibility_level="reversible", blast_radius="self")
        bad = soft_score(p_success=0.8, reversibility_level="irreversible", blast_radius="self")
        assert bad["S"] < good["S"]

    def test_unknown_blast_radius_treated_conservatively(self):
        r = soft_score(p_success=0.5, blast_radius="weird_value")
        assert r["terms"]["blast_radius"] == 0.3  # conservative default, not 0


class TestScoreCandidate:
    def test_veto_blocks_score(self):
        r = score_candidate({"action_class": "IRREVERSIBLE", "actor_verified": False})
        assert r["S"] is None
        assert r["qrl_hint"] == "HOLD"
        assert set(r["floor_ids"]) >= {"F1", "F13"}

    # negative: unverified actor + critical tier must never hint SEAL
    def test_unverified_critical_never_seal_hint(self):
        r = score_candidate({"action_tier": "critical", "actor_verified": False})
        assert r["qrl_hint"] != "SEAL"

    def test_clean_candidate_scores(self):
        r = score_candidate(
            {
                "p_success": 0.9,
                "action_class": "OBSERVE",
                "reversibility_level": "reversible",
                "blast_radius": "self",
                "actor_verified": False,
            }
        )
        assert r["S"] is not None
        assert r["authority"] == "ADVISORY"
        assert r["sealable"] is False


# ── F3 (scope 5): prediction record — exactly one, p in [0,1] ──


class TestPredictionRecord:
    def test_writes_single_jsonl_line(self, tmp_path):
        sink = str(tmp_path / "pred.jsonl")
        r = write_prediction_record(
            {"node": "n1", "expected": "thing happens", "p": 0.7}, sink=sink
        )
        assert r["written"] is True
        lines = open(sink).read().strip().split("\n")
        assert len(lines) == 1
        rec = json.loads(lines[0])
        assert rec["p"] == 0.7 and rec["sealed"] is False and rec["live_chron"] is False

    def test_p_out_of_range_rejected(self, tmp_path):
        sink = str(tmp_path / "pred.jsonl")
        r = write_prediction_record({"node": "n1", "expected": "x", "p": 1.5}, sink=sink)
        assert r["written"] is False and "error" in r

    def test_p_nan_string_rejected(self, tmp_path):
        sink = str(tmp_path / "pred.jsonl")
        r = write_prediction_record({"node": "n1", "expected": "x", "p": "banana"}, sink=sink)
        assert r["written"] is False

    def test_missing_node_rejected(self, tmp_path):
        sink = str(tmp_path / "pred.jsonl")
        r = write_prediction_record({"expected": "x", "p": 0.5}, sink=sink)
        assert r["written"] is False


# ── collapse mapping: never upward, unknown → HOLD ──


class TestCollapseVerdict:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("SEAL", "SEAL"),
            ("PARTIAL", "SABAR"),
            ("PROVISIONAL", "SABAR"),
            ("SABAR", "SABAR"),
            ("HOLD", "HOLD"),
            ("HOLD_888", "HOLD"),
            ("VOID", "VOID"),
            ("DEGRADED", "SABAR"),
            ("OBSERVE_ONLY", "HOLD"),
        ],
    )
    def test_known_tokens(self, raw, expected):
        assert collapse_verdict(raw)["verdict"] == expected

    @pytest.mark.parametrize("raw", ["", None, "BANANA", "seal ", 123])
    def test_unknown_tokens_hold(self, raw):
        r = collapse_verdict(raw)
        assert r["verdict"] == "HOLD"
        assert r["reason_code"] == "unknown_verdict_token"

    def test_veto_downgrades_seal_to_hold(self):
        r = collapse_verdict("SEAL", veto_floors=["F1"])
        assert r["verdict"] == "HOLD"
        assert "F1" in r["floor_ids"]

    def test_veto_never_upgrades_void(self):
        r = collapse_verdict("VOID", veto_floors=["F1"])
        assert r["verdict"] == "VOID"


# ── default sink is outside the repo (test sink, not a source-tree write) ──


def test_default_sink_outside_repo():
    assert "/arifos/" not in DEFAULT_PREDICTION_SINK or DEFAULT_PREDICTION_SINK.startswith(
        "/root/.local/share/arifos/"
    )
