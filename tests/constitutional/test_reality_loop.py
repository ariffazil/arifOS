"""
tests/constitutional/test_reality_loop.py — FalsifiablePrediction + Reality Loop gate (Q9c)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q9c (GENESIS/058, sealed 2026-08-02).

Tests verify:
  - `prediction_id` is content-addressed (sha256[:12]), stable across calls.
  - `FalsifiablePrediction` rejects invalid status / missing deadline.
  - `register_prediction` dedupes by canonical id (no overwrites on F11 audit).
  - `check_prediction` scores CORROBORATED / FALSIFIED.
  - `expire_overdue` flips OPEN → EXPIRED past deadline.
  - `reality_loop_gate` is ADVISORY — never blocks SEAL.
  - Reality Loop attaches prediction_id when inline FalsifiablePrediction
    is supplied, SABAR when SEAL-bound without one (gap recorded, not blocked).

Floor binding: F1 AMANAH (reversible), F2 TRUTH (falsifier named),
F4 CLARITY (claim/check separated), F11 AUDIT (receipt on every event).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest


@dataclass
class _Ctx:
    tool_name: str = "arif_seal"
    session_id: str = "SEAL-test"
    actor_id: str = "arif"
    action_class: str = "IRREVERSIBLE"
    params: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Module surface
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleSurface:
    def test_module_imports(self):
        from arifosmcp.runtime import reality_loop as mod

        assert hasattr(mod, "FalsifiablePrediction")
        assert hasattr(mod, "RealityReceipt")
        assert hasattr(mod, "prediction_id")
        assert hasattr(mod, "register_prediction")
        assert hasattr(mod, "check_prediction")
        assert hasattr(mod, "expire_overdue")
        assert hasattr(mod, "reality_loop_gate")
        assert hasattr(mod, "ledger_snapshot")
        assert hasattr(mod, "reset_ledger")

    def test_status_constants_frozen(self):
        from arifosmcp.runtime.reality_loop import (
            STATUS_CHECKED,
            STATUS_CORROBORATED,
            STATUS_EXPIRED,
            STATUS_FALSIFIED,
            STATUS_OPEN,
        )

        assert STATUS_OPEN == "OPEN"
        assert STATUS_CHECKED == "CHECKED"
        assert STATUS_CORROBORATED == "CORROBORATED"
        assert STATUS_FALSIFIED == "FALSIFIED"
        assert STATUS_EXPIRED == "EXPIRED"


# ═══════════════════════════════════════════════════════════════════════════
# 2. Content-addressed ID
# ═══════════════════════════════════════════════════════════════════════════


class TestPredictionID:
    def test_same_tuple_same_id(self):
        from arifosmcp.runtime.reality_loop import prediction_id

        a = prediction_id("X by Y", "X is not Y", "2026-12-31T00:00:00Z")
        b = prediction_id("X by Y", "X is not Y", "2026-12-31T00:00:00Z")
        assert a == b

    def test_different_statement_different_id(self):
        from arifosmcp.runtime.reality_loop import prediction_id

        a = prediction_id("X by Y", "X is not Y", "2026-12-31T00:00:00Z")
        b = prediction_id("Z by Y", "X is not Y", "2026-12-31T00:00:00Z")
        assert a != b

    def test_id_has_fp_prefix(self):
        from arifosmcp.runtime.reality_loop import prediction_id

        pid = prediction_id("X by Y", "X is not Y", "2026-12-31T00:00:00Z")
        assert pid.startswith("fp_")
        # 12 hex chars after prefix
        assert len(pid) == 3 + 12


# ═══════════════════════════════════════════════════════════════════════════
# 3. FalsifiablePrediction dataclass
# ═══════════════════════════════════════════════════════════════════════════


class TestFalsifiablePredictionDataclass:
    def test_minimal_construction(self):
        from arifosmcp.runtime.reality_loop import FalsifiablePrediction

        pred = FalsifiablePrediction(
            statement="X will be Y",
            falsifier="X is not Y",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        assert pred.prediction_id.startswith("fp_")
        assert pred.status == "OPEN"
        assert pred.check_method == "arif_observe"  # default

    def test_invalid_status_raises(self):
        from arifosmcp.runtime.reality_loop import FalsifiablePrediction

        with pytest.raises(ValueError, match="Invalid status"):
            FalsifiablePrediction(
                statement="X",
                falsifier="not X",
                check_by_iso="2026-12-31T00:00:00Z",
                status="BOGUS",
            )

    def test_missing_deadline_raises(self):
        from arifosmcp.runtime.reality_loop import FalsifiablePrediction

        with pytest.raises(ValueError, match="check_by_iso is required"):
            FalsifiablePrediction(
                statement="X",
                falsifier="not X",
                check_by_iso="",
            )

    def test_to_dict_includes_id(self):
        from arifosmcp.runtime.reality_loop import FalsifiablePrediction

        pred = FalsifiablePrediction(
            statement="X by Y",
            falsifier="X is not Y",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        d = pred.to_dict()
        assert d["prediction_id"] == pred.prediction_id
        assert d["statement"] == "X by Y"


# ═══════════════════════════════════════════════════════════════════════════
# 4. Register / Check lifecycle
# ═══════════════════════════════════════════════════════════════════════════


class TestRegisterCheck:
    def setup_method(self):
        from arifosmcp.runtime.reality_loop import reset_ledger

        reset_ledger()

    def test_register_appends_to_ledger(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            ledger_snapshot,
            register_prediction,
        )

        pred = FalsifiablePrediction(
            statement="kernel tests will pass",
            falsifier="kernel tests will fail",
            check_by_iso="2026-12-31T00:00:00Z",
            source_tool="arif_think",
        )
        receipt = register_prediction(pred, session_id="SEAL-x", actor_id="arif")
        assert receipt.event == "REGISTER"
        assert receipt.status_after == "OPEN"
        snap = ledger_snapshot()
        assert snap["count"] == 1
        assert pred.prediction_id in snap["predictions"]

    def test_register_dedup_by_canonical_id(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            ledger_snapshot,
            register_prediction,
        )

        pred1 = FalsifiablePrediction(
            statement="A",
            falsifier="not A",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        pred2 = FalsifiablePrediction(
            statement="A",
            falsifier="not A",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        assert pred1.prediction_id == pred2.prediction_id
        register_prediction(pred1)
        register_prediction(pred2)
        snap = ledger_snapshot()
        # Dedup: still only 1 prediction, 2 receipts
        assert snap["count"] == 1
        assert len(snap["receipts"]) == 2
        # Second receipt should be REGISTER-EXISTS
        assert snap["receipts"][1]["event"] == "REGISTER-EXISTS"

    def test_check_corroborates_on_truthy_observation(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            check_prediction,
            ledger_snapshot,
            register_prediction,
        )

        pred = FalsifiablePrediction(
            statement="X by Y",
            falsifier="not X",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        register_prediction(pred)
        receipt = check_prediction(pred.prediction_id, observed_value="confirmed")
        assert receipt.event == "CHECK"
        assert receipt.status_after == "CORROBORATED"
        snap = ledger_snapshot()
        assert snap["predictions"][pred.prediction_id]["status"] == "CORROBORATED"

    def test_check_falsifies_on_falsy_observation(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            check_prediction,
            register_prediction,
        )

        pred = FalsifiablePrediction(
            statement="X by Y",
            falsifier="not X",
            check_by_iso="2026-12-31T00:00:00Z",
        )
        register_prediction(pred)
        receipt = check_prediction(pred.prediction_id, observed_value=None)
        assert receipt.status_after == "FALSIFIED"

    def test_check_unknown_id_is_noop(self):
        from arifosmcp.runtime.reality_loop import check_prediction

        receipt = check_prediction("fp_doesnotexist", observed_value=True)
        assert receipt.status_before == "UNKNOWN"
        assert receipt.status_after == "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════
# 5. Expire overdue
# ═══════════════════════════════════════════════════════════════════════════


class TestExpireOverdue:
    def setup_method(self):
        from arifosmcp.runtime.reality_loop import reset_ledger

        reset_ledger()

    def test_overdue_becomes_expired(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            expire_overdue,
            register_prediction,
        )

        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        pred = FalsifiablePrediction(
            statement="stale prediction",
            falsifier="not stale",
            check_by_iso=past,
        )
        register_prediction(pred)
        receipts = expire_overdue()
        assert len(receipts) == 1
        assert receipts[0].event == "EXPIRE"
        assert receipts[0].status_after == "EXPIRED"

    def test_future_deadline_not_expired(self):
        from arifosmcp.runtime.reality_loop import (
            FalsifiablePrediction,
            expire_overdue,
            register_prediction,
        )

        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        pred = FalsifiablePrediction(
            statement="future prediction",
            falsifier="not future",
            check_by_iso=future,
        )
        register_prediction(pred)
        receipts = expire_overdue()
        assert receipts == []


# ═══════════════════════════════════════════════════════════════════════════
# 6. Reality Loop gate — ADVISORY, never blocks SEAL
# ═══════════════════════════════════════════════════════════════════════════


class TestRealityLoopGate:
    def setup_method(self):
        from arifosmcp.runtime.reality_loop import reset_ledger

        reset_ledger()

    def test_observe_without_prediction_proceeds(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = reality_loop_gate(ctx)
        assert result["verdict"] == "PROCEED"
        assert result["passed"] is True
        assert result["commitment_missing"] is True

    def test_seal_without_prediction_advisory_sabar(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        ctx = _Ctx(tool_name="arif_seal", action_class="IRREVERSIBLE")
        result = reality_loop_gate(ctx)
        # Advisory SABAR, not HOLD
        assert result["verdict"] == "SABAR"
        assert result["passed"] is True  # ALWAYS passes
        assert result["commitment_missing"] is True
        assert result["violated_laws"] == []  # Reality Loop never violates floors

    def test_seal_with_inline_prediction_registers(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            params={
                "falsifiable_prediction": {
                    "statement": "seal will pass the gate",
                    "falsifier": "seal will be blocked",
                    "check_by_iso": future,
                    "check_method": "arif_observe",
                    "floor_basis": ["F2", "F4"],
                }
            },
        )
        result = reality_loop_gate(ctx)
        assert result["verdict"] == "PROCEED"
        assert result["passed"] is True
        assert result["commitment_missing"] is False
        assert result["prediction_id"] is not None
        assert result["prediction_id"].startswith("fp_")

    def test_malformed_inline_prediction_flags_missing(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            params={"falsifiable_prediction": {"statement": "no falsifier, no deadline"}},
        )
        result = reality_loop_gate(ctx)
        # FalsifiablePrediction raises on missing check_by_iso → caught, flagged
        assert result["commitment_missing"] is True
        assert result["prediction_id"] is None

    def test_gate_never_blocks_even_on_seal_bound(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        # Worst case: SEAL-bound, no prediction, no inline payload
        ctx = _Ctx(tool_name="arif_seal", action_class="ATOMIC", params={})
        result = reality_loop_gate(ctx)
        # SABAR, but still passed=True (advisory)
        assert result["passed"] is True
        # violated_laws is always empty for Reality Loop
        assert result["violated_laws"] == []


# ═══════════════════════════════════════════════════════════════════════════
# 7. Receipt contract (F11 AUDIT)
# ═══════════════════════════════════════════════════════════════════════════


class TestReceiptContract:
    def setup_method(self):
        from arifosmcp.runtime.reality_loop import reset_ledger

        reset_ledger()

    def test_receipt_contains_q9c_metadata(self):
        from arifosmcp.runtime.reality_loop import reality_loop_gate

        ctx = _Ctx()
        result = reality_loop_gate(ctx)
        receipt = result["receipt"]
        assert receipt["gate"] == "REALITY_LOOP"
        assert receipt["passed"] is True
        assert "q9c" in receipt
        assert "falsifiable_linked" in receipt["q9c"]
        assert "commitment_missing" in receipt["q9c"]
        assert "doctrine" in receipt
        assert "GENESIS/058" in receipt["doctrine"]
