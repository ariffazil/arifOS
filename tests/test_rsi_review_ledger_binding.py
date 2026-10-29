"""P2 — record_rsi_review must be targetable at an explicit ledger.

Split per house practice:
  * BASELINE PINS  — behaviour that exists today; green before and after the change.
  * CAPABILITY     — the new explicit binding; red before, green after.

Never touches the live ledger: every write goes to tmp_path.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from arifosmcp.runtime.rsi_audit import (
    LEDGER_PATH,
    RSIDecisionRecord,
    RSILedger,
    _get_ledger,
    record_rsi_review,
)

try:  # P2 capability: not implemented until this change lands
    from arifosmcp.runtime.rsi_audit import open_ledger
except ImportError:  # pragma: no cover - the red phase

    def open_ledger(path=None):  # type: ignore[misc]
        raise NotImplementedError(
            "DESIGN_NOT_IMPLEMENTED: open_ledger() is the P2 explicit-ledger handle"
        )


def _rec(decision_id: str | None = None) -> RSIDecisionRecord:
    return RSIDecisionRecord(
        decision_id=decision_id or "00000000-0000-4000-8000-000000000001",
        tool="probe_tool",
        original_verdict="HOLD",
        reason_class="SAFETY",
    )


# ── BASELINE PINS ───────────────────────────────────────────────────────────
def test_module_entry_point_signature_is_unchanged():
    import inspect

    params = inspect.signature(record_rsi_review).parameters
    for name in ("decision_id", "review_outcome", "reviewed_by", "evidence_refs", "independent", "note"):
        assert name in params
        assert params[name].kind is inspect.Parameter.KEYWORD_ONLY


def test_default_ledger_is_the_live_ledger():
    assert Path(_get_ledger()._path) == Path(LEDGER_PATH)


def test_live_ledger_default_is_still_reachable_without_an_explicit_handle():
    # Backward compatibility: the module-level function must keep its old default.
    assert LEDGER_PATH.exists()
    assert Path(LEDGER_PATH).name == "rsi_ledger.jsonl"


# ── CAPABILITY ─────────────────────────────────────────────────────────────
def test_open_ledger_binds_an_explicit_path(tmp_path):
    target = tmp_path / "rsi_ledger.jsonl"
    led = open_ledger(target)
    assert isinstance(led, RSILedger)
    assert Path(led._path) == target


def test_open_ledger_without_argument_binds_the_live_ledger():
    assert Path(open_ledger()._path) == Path(LEDGER_PATH)


def test_review_can_be_appended_to_an_explicit_ledger(tmp_path):
    target = tmp_path / "rsi_ledger.jsonl"
    led = open_ledger(target)
    decision = _rec()
    led.record(decision)

    live_before = os.stat(LEDGER_PATH).st_size

    record_rsi_review(
        decision_id=decision.decision_id,
        review_outcome="CORRECT_HOLD",
        reviewed_by="555-verifier",
        evidence_refs=["probe:explicit-binding"],
        independent=True,
        ledger=led,
    )

    rows = [l for l in target.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(rows) == 2
    assert os.stat(LEDGER_PATH).st_size == live_before  # live untouched


def test_explicit_binding_does_not_fall_back_to_the_live_ledger(tmp_path):
    target = tmp_path / "rsi_ledger.jsonl"
    led = open_ledger(target)
    decision = _rec("00000000-0000-4000-8000-000000000002")
    led.record(decision)

    with pytest.raises(KeyError):
        record_rsi_review(
            decision_id="11111111-1111-4111-8111-111111111111",
            review_outcome="CORRECT_HOLD",
            reviewed_by="555-verifier",
            ledger=led,
        )
