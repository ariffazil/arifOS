"""Bounded PROCEED wiring for the RSI ledger (FI-003, 2026-10-29, Phase 5).

The population under audit is exactly ONE: a consequential (seal-bound) action
that was ALLOWED. Everything else is out of scope, and every suppression is
counted rather than silent.

Safety: the recorder writes to a temp ledger in these tests. The live ledger
(/root/VAULT999/rsi_ledger.jsonl) is never touched here.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from arifosmcp.runtime.rsi_audit import RSILedger
from arifosmcp.runtime.rsi_proceed import (
    CEILING_ENV,
    DEFAULT_CEILING_PER_HOUR,
    OWNED_VERDICTS,
    ProceedRecorder,
    proceed_recorder_stats,
    record_governed_proceed,
)


def _recorder(tmp_path: Path, **kw) -> ProceedRecorder:
    return ProceedRecorder(RSILedger(tmp_path / "rsi_ledger.jsonl"), **kw)


def _rows(tmp_path: Path) -> list[dict]:
    p = tmp_path / "rsi_ledger.jsonl"
    if not p.exists():
        return []
    import json

    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


# ── the bound ──────────────────────────────────────────────────────────────
def test_non_seal_bound_decisions_are_out_of_scope(tmp_path):
    rec = _recorder(tmp_path)
    out = rec.record(verdict="SABAR", seal_bound=False, tool="godel_lock_gate")
    assert out["recorded"] is False
    assert out["reason"] == "NOT_SEAL_BOUND"
    assert _rows(tmp_path) == []
    assert rec.stats()["suppressed_by_scope"] == 1


def test_hold_is_owned_by_the_refusal_path_not_recorded_twice(tmp_path):
    rec = _recorder(tmp_path)
    out = rec.record(verdict="HOLD", seal_bound=True, tool="godel_lock_gate")
    assert out["recorded"] is False
    assert out["reason"] == "HOLD_OWNED_BY_REFUSAL_PATH"
    assert _rows(tmp_path) == []


def test_seal_bound_proceed_is_recorded(tmp_path):
    rec = _recorder(tmp_path)
    out = rec.record(
        verdict="PROCEED",
        seal_bound=True,
        tool="godel_lock_gate",
        reason_class="EVIDENCE",
        severity_weight=2.0,
        evidence=["phi_external=0.81", "severity=consequential"],
    )
    assert out["recorded"] is True
    rows = _rows(tmp_path)
    assert len(rows) == 1
    assert rows[0]["original_verdict"] == "PROCEED"
    assert rows[0]["tool"] == "godel_lock_gate"
    assert rows[0]["review_outcome"] == "UNRESOLVED"  # not yet adjudicated
    assert rows[0]["evidence_available_at_decision"] == ["phi_external=0.81", "severity=consequential"]


def test_seal_bound_sabar_is_recorded_because_it_allowed_a_consequential_action(tmp_path):
    rec = _recorder(tmp_path)
    out = rec.record(verdict="SABAR", seal_bound=True, tool="godel_lock_gate", reason_class="UNCERTAINTY")
    assert out["recorded"] is True
    assert _rows(tmp_path)[0]["original_verdict"] == "SABAR"


def test_unknown_verdict_is_out_of_scope(tmp_path):
    rec = _recorder(tmp_path)
    out = rec.record(verdict="WHATEVER", seal_bound=True, tool="godel_lock_gate")
    assert out["recorded"] is False
    assert out["reason"] == "VERDICT_OUT_OF_SCOPE"


# ── the ceiling ────────────────────────────────────────────────────────────
def test_ceiling_suppresses_but_never_silently(tmp_path):
    rec = _recorder(tmp_path, ceiling_per_hour=2)
    assert rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")["recorded"]
    assert rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")["recorded"]
    third = rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")
    assert third["recorded"] is False
    assert third["reason"] == "CEILING_REACHED"
    assert len(_rows(tmp_path)) == 2  # nothing written past the ceiling
    stats = rec.stats()
    assert stats["suppressed_by_ceiling"] == 1
    assert stats["ceiling_per_hour"] == 2
    assert stats["recorded"] == 2


def test_ceiling_window_rolls_over(tmp_path):
    clock = {"t": 1000.0}
    rec = ProceedRecorder(
        RSILedger(tmp_path / "rsi_ledger.jsonl"),
        ceiling_per_hour=1,
        now_fn=lambda: clock["t"],
    )
    assert rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")["recorded"]
    assert rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")["recorded"] is False
    clock["t"] = 1000.0 + 3600  # next hour window
    assert rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")["recorded"]
    assert rec.stats()["recorded_this_window"] == 1


# ── failure isolation ──────────────────────────────────────────────────────
def test_recording_failure_never_raises_and_never_vetoes(tmp_path):
    class BrokenLedger:
        def record(self, decision):  # noqa: D102
            raise OSError("disk on fire")

    rec = ProceedRecorder(BrokenLedger())
    out = rec.record(verdict="PROCEED", seal_bound=True, tool="godel_lock_gate")
    assert out["recorded"] is False
    assert out["reason"].startswith("RECORD_FAILED")
    assert rec.stats()["failed"] == 1


def test_module_entry_point_is_safe_without_a_ledger():
    out = record_governed_proceed(
        verdict="PROCEED", seal_bound=False, tool="godel_lock_gate"
    )
    assert out["recorded"] is False
    assert out["reason"] == "NOT_SEAL_BOUND"


# ── contract invariants ────────────────────────────────────────────────────
def test_scope_constants_are_what_the_gate_actually_emits():
    assert set(OWNED_VERDICTS) == {"PROCEED", "SABAR"}
    assert DEFAULT_CEILING_PER_HOUR > 0
    assert CEILING_ENV == "ARIFOS_RSI_PROCEED_CEILING_PER_HOUR"


def test_proceed_recorder_stats_is_readable_and_names_the_scope():
    stats = proceed_recorder_stats()
    assert stats.get("scope") == "seal_bound_allowed_only"
    assert "suppressed_by_scope" in stats
    assert "suppressed_by_ceiling" in stats


def test_rsi_proceed_does_not_import_the_gate_module():
    """No circular import: the gate knows seal-bound-ness, the recorder does not."""
    import arifosmcp.runtime.rsi_proceed as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "import godel_lock_gate" not in src
    assert "from arifosmcp.runtime.godel_lock_gate" not in src


@pytest.mark.parametrize("verdict", ["PROCEED", "SABAR"])
def test_recorded_rows_land_in_the_ledger_as_unresolved_decisions(tmp_path, verdict):
    rec = _recorder(tmp_path)
    rec.record(verdict=verdict, seal_bound=True, tool="godel_lock_gate")
    stats = rec._write_ledger().stats()
    assert stats["total_records"] == 1
    assert stats["reviewed_count"] == 0
    assert stats["false_proceed_rate"] == "UNMEASURED"
    assert stats["false_hold_rate"] == "UNMEASURED"
