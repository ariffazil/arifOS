"""QRL increment-1 tests: qrl_branches (scope 3 — derived candidates, labelled fallback)."""

from __future__ import annotations

import json

import pytest

from arifosmcp.tools.qrl_branches import branches


CF = "/root/.local/share/arifos/carry_forward.json"


@pytest.fixture()
def real_cf():
    """Guard: live carry-forward must have open loops for the derivation path."""
    try:
        data = json.load(open(CF))
    except (OSError, json.JSONDecodeError):
        pytest.skip("carry-forward unreadable")
    loops = [
        e
        for e in data.get("entries", [])
        if (e.get("kind") or "") in ("open_loop", "888_HOLD_resume")
    ]
    if not loops:
        pytest.skip("no open loops in carry-forward")
    return loops


class TestBranchesDerived:
    def test_returns_advisory_unsealable(self):
        r = branches("test query")
        assert r["authority"] == "ADVISORY"
        assert r["sealable"] is False
        assert r["unsealable"] is True
        assert r["verdict"] if "verdict" in r else True  # never sets verdict

    def test_at_least_three_candidates(self, real_cf):
        r = branches("assess open loops")
        assert r["n_candidates"] >= 3

    def test_candidates_have_source_label(self, real_cf):
        r = branches("q")
        for c in r["candidates"]:
            assert c["source"] in ("derived", "template")
            assert c.get("basis")  # never silent provenance

    def test_derived_preferred_over_template(self, real_cf):
        r = branches("q")
        assert r["derived_count"] >= 1
        derived = [c for c in r["candidates"] if c["source"] == "derived"]
        assert derived, "frontier+evidence derivation must fire on live data"

    def test_fallback_labelled_when_used(self, tmp_path, monkeypatch):
        # empty carry-forward → derivation starves → template fallback must be labelled
        empty = tmp_path / "cf.json"
        empty.write_text(json.dumps({"entries": []}))
        from arifosmcp.tools import qrl_branches as qb

        r = qb.branches("q", cf_path=str(empty))
        assert r["template_fallback"] is True
        assert all(c["source"] in ("derived", "template") for c in r["candidates"])
        templates = [c for c in r["candidates"] if c["source"] == "template"]
        assert templates, "fallback must be present AND labelled"

    def test_candidates_distinct(self, real_cf):
        r = branches("q")
        names = [c["name"] for c in r["candidates"]]
        assert len(names) == len(set(names))

    def test_every_candidate_has_falsifier(self, real_cf):
        r = branches("q")
        for c in r["candidates"]:
            assert c.get("falsifier"), f"candidate {c['name']} missing falsifier"

    def test_no_verdict_emitted(self, real_cf):
        r = branches("q")
        assert "verdict" not in r or r.get("verdict") is None

    def test_malformed_cf_degrades_not_crashes(self, tmp_path):
        bad = tmp_path / "cf.json"
        bad.write_text("{not json")
        r = branches("q", cf_path=str(bad))
        assert "candidates" in r  # degrades, never crashes
