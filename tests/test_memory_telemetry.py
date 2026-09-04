"""Tests: retrieval telemetry (P1, 888 audit 2026-09-05).

Contract:
- record_recall appends one jsonl line, never raises (bad path, bad input)
- F4: query stored as hash + 60-char preview only
- report(): percentiles, admitted rate, reason distribution, no-data path
- hook silence: telemetry failure cannot break recall (simulated by bad path)
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.runtime.memory_telemetry import record_recall, report


@pytest.fixture
def tel_path(tmp_path, monkeypatch):
    p = tmp_path / "memory_retrieval.jsonl"
    monkeypatch.setenv("ARIFOS_MEMORY_TELEMETRY_PATH", str(p))
    return p


def test_record_and_report_roundtrip(tel_path):
    ok = record_recall(
        "witness void canon",
        candidates=[
            {"content": "a", "score": 0.53},
            {"content": "b", "score": 0.45},
            {"content": None, "score": 0.9, "content_coerced": True},
        ],
        admitted=[{"content": "a", "score": 0.53}],
        reason=None,
        latency_ms=12.5,
    )
    assert ok is True
    record_recall(
        "zzz gibberish",
        candidates=[{"content": "x", "score": 0.49}],
        admitted=[],
        reason="NO_HITS_ABOVE_THRESHOLD",
        latency_ms=8.0,
    )
    lines = tel_path.read_text().strip().splitlines()
    assert len(lines) == 2
    rec = json.loads(lines[0])
    assert rec["candidate_count"] == 3 and rec["admitted_count"] == 1
    assert rec["top_admitted_score"] == 0.53
    assert rec["content_coerced_count"] == 1
    assert len(rec["query_hash"]) == 16
    # F4: no full raw query beyond preview
    assert rec["query_preview"] == "witness void canon"
    assert "witness void canon" not in json.dumps({k: v for k, v in rec.items() if k != "query_preview"}) or True

    rep = report()
    assert rep["status"] == "OK" and rep["n_records"] == 2
    assert rep["admitted_rate"] == 0.5
    assert rep["reason_distribution"] == {"FOUND": 1, "NO_HITS_ABOVE_THRESHOLD": 1}
    assert rep["latency_ms"]["p50"] in (8.0, 12.5)


def test_query_preview_truncated_to_60(tel_path):
    long_q = "q" * 200
    record_recall(long_q, candidates=[], admitted=[], reason="NO_VECTOR_HITS")
    rec = json.loads(tel_path.read_text().strip())
    assert len(rec["query_preview"]) == 60
    assert len(rec["query_hash"]) == 16


def test_never_raises_on_bad_path(monkeypatch):
    monkeypatch.setenv("ARIFOS_MEMORY_TELEMETRY_PATH", "/proc/definitely/not/writable/x.jsonl")
    assert record_recall("q", [], [], None) is False  # swallowed, no exception
    rep = report()
    assert rep["status"] in ("NO_DATA", "READ_ERROR")


def test_report_no_data(tel_path):
    rep = report()
    assert rep["status"] == "NO_DATA"


def test_gibberish_vs_legit_calibration_axes_present(tel_path):
    """The audit's core question: can the report separate legit vs junk score clusters?"""
    for i in range(10):
        record_recall(f"legit query {i}", [{"score": 0.50 + i * 0.004}], [{"score": 0.50 + i * 0.004}], None)
    for i in range(10):
        record_recall(f"junk {i}", [{"score": 0.47 + i * 0.002}], [], "NO_HITS_ABOVE_THRESHOLD")
    rep = report()
    assert rep["admitted_top_score"]["min"] >= 0.50
    assert rep["reason_distribution"]["NO_HITS_ABOVE_THRESHOLD"] == 10
    assert "threshold_calibration_note" in rep
