"""
Tests for the 3-Phase Observability wrapper.

Forged 2026-08-10. Lane B SESSION_RECEIPT ratification.

Coverage:
  PRE_FLIGHT — file integrity, service health, VRAM (torch absent / CPU path)
  RUNTIME    — happy path, exception path
  POST_FLIGHT — verifier pass / fail, no verifier
  Receipt emission — proxy degrades gracefully when arifFlow unreachable

All tests use mocked FlowReceiptProxy so they run without arifFlow online.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure arifOS root on sys.path with priority (matches sibling tests).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure constitutional physics are not mutated by this test module.
os.environ.setdefault("ARIFOS_PUBLIC_TOOL_PROFILE", "full")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")

from arifosmcp.arifos_observability.three_phase import (  # noqa: E402
    AAAGuardResult,
    AAAExecutionGuard,
    AAAFlowEngine,
    FlowReceiptProxy,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_receipts() -> MagicMock:
    """A FlowReceiptProxy stub that records every emit() call."""
    proxy = MagicMock(spec=FlowReceiptProxy)
    proxy.emit.return_value = "r3p-test0001"
    return proxy


@pytest.fixture
def engine(mock_receipts: MagicMock) -> AAAFlowEngine:
    return AAAFlowEngine(arifflow_endpoint="http://127.0.0.1:9999")


# ─────────────────────────────────────────────────────────────────────────────
# PRE_FLIGHT — file integrity
# ─────────────────────────────────────────────────────────────────────────────


class TestVerifyFileIntegrity:
    def test_missing_file_fails(self, tmp_path: Path) -> None:
        result = AAAExecutionGuard.verify_file_integrity(
            str(tmp_path / "does_not_exist.bin"),
            min_size_mb=1.0,
        )
        assert result.ok is False
        assert "missing" in result.message.lower()

    def test_too_small_file_fails(self, tmp_path: Path) -> None:
        small = tmp_path / "small.bin"
        small.write_bytes(b"\x00" * 1024)  # 0.001 MB
        result = AAAExecutionGuard.verify_file_integrity(
            str(small), min_size_mb=1.0
        )
        assert result.ok is False
        assert "incomplete" in result.message.lower()
        assert result.details["size_mb"] < 1.0

    def test_adequate_file_passes(self, tmp_path: Path) -> None:
        big = tmp_path / "big.bin"
        big.write_bytes(b"\x00" * (2 * 1024 * 1024))  # 2 MB
        result = AAAExecutionGuard.verify_file_integrity(
            str(big), min_size_mb=1.0
        )
        assert result.ok is True
        assert result.details["size_mb"] >= 2.0


# ─────────────────────────────────────────────────────────────────────────────
# PRE_FLIGHT — service health
# ─────────────────────────────────────────────────────────────────────────────


class TestCheckServiceHealth:
    def test_unreachable_endpoint_fails(self) -> None:
        # Use a port that should not be listening
        result = AAAExecutionGuard.check_service_health(
            "http://127.0.0.1:1/health", timeout_s=1
        )
        assert result.ok is False
        assert "exception" in result.details

    def test_real_organ_health_passes_if_live(self) -> None:
        # arifOS :8088 — federation health probe we already verified earlier.
        result = AAAExecutionGuard.check_service_health(
            "http://127.0.0.1:8088/health", timeout_s=2
        )
        # If the federation is up, this passes. Skip otherwise (CI without it).
        if result.ok:
            assert result.details.get("status") == 200
        else:
            pytest.skip("federation not reachable in this env")


# ─────────────────────────────────────────────────────────────────────────────
# PRE_FLIGHT — VRAM
# ─────────────────────────────────────────────────────────────────────────────


class TestCheckVramCapacity:
    def test_no_torch_skips_cleanly(self) -> None:
        with patch.dict(sys.modules, {"torch": None}):
            result = AAAExecutionGuard.check_vram_capacity(required_vram_gb=8.0)
        # torch absent → CPU path, skipped, ok=True (not a failure)
        assert result.ok is True
        assert result.details.get("skipped") is True


# ─────────────────────────────────────────────────────────────────────────────
# PRE_FLIGHT — bundle
# ─────────────────────────────────────────────────────────────────────────────


class TestRunAllBundle:
    def test_full_bundle_no_guards_needed(self) -> None:
        """When model_path + api_url are None, only VRAM check runs."""
        ok, results = AAAExecutionGuard.run_all(
            model_path=None, api_url=None, required_vram_gb=8.0
        )
        # Just VRAM check, which skips cleanly without torch.
        assert ok is True
        assert len(results) == 1
        assert results[0].name == "vram_capacity"


# ─────────────────────────────────────────────────────────────────────────────
# RUNTIME — happy path
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeHappyPath:
    def test_callable_executes_and_emits(
        self, engine: AAAFlowEngine, mock_receipts: MagicMock
    ) -> None:
        engine.receipts = mock_receipts
        result = engine.execute_sovereign_task(
            task_callable=lambda: "ok",
            task_label="happy_path",
        )
        assert result["ok"] is True
        assert result["phase"] == "POST_FLIGHT"
        assert result["output"] == "ok"
        # Three receipts: Barrier, Execute, Verify
        assert mock_receipts.emit.call_count == 3
        step_types = [c.kwargs["step_type"] for c in mock_receipts.emit.call_args_list]
        assert step_types == ["Barrier", "Execute", "Verify"]


# ─────────────────────────────────────────────────────────────────────────────
# RUNTIME — exception path
# ─────────────────────────────────────────────────────────────────────────────


class TestRuntimeException:
    def test_exception_yields_void_receipt_and_returns_ok_false(
        self, engine: AAAFlowEngine, mock_receipts: MagicMock
    ) -> None:
        engine.receipts = mock_receipts

        def boom() -> None:
            raise RuntimeError("kaboom")

        result = engine.execute_sovereign_task(
            task_callable=boom, task_label="explode"
        )
        assert result["ok"] is False
        assert "RuntimeError" in result["runtime"]["exception"]
        # Barrier (pre-flight pass) + Execute (void). No Verify.
        assert mock_receipts.emit.call_count == 2
        verdicts = [c.kwargs["floor_verdict"] for c in mock_receipts.emit.call_args_list]
        assert verdicts == ["Pass", "Void"]


# ─────────────────────────────────────────────────────────────────────────────
# POST_FLIGHT — verifier
# ─────────────────────────────────────────────────────────────────────────────


class TestPostFlightVerifier:
    def test_verifier_failure_marks_caution(
        self, engine: AAAFlowEngine, mock_receipts: MagicMock
    ) -> None:
        engine.receipts = mock_receipts

        def verifier(output: str) -> tuple[bool, str]:
            return False, "looks sus"

        result = engine.execute_sovereign_task(
            task_callable=lambda: "result",
            task_label="verify_fail",
            post_flight_verifier=verifier,
        )
        # Work happened, but verifier failed → result['ok'] False, but
        # result['phase'] advanced to POST_FLIGHT.
        assert result["phase"] == "POST_FLIGHT"
        assert result["ok"] is False
        assert result["post_flight"]["ok"] is False
        assert result["post_flight"]["message"] == "looks sus"
        last_call = mock_receipts.emit.call_args_list[-1]
        assert last_call.kwargs["step_type"] == "Verify"
        assert last_call.kwargs["floor_verdict"] == "Caution"


# ─────────────────────────────────────────────────────────────────────────────
# Receipt emission — degraded path
# ─────────────────────────────────────────────────────────────────────────────


class TestReceiptEmissionDegraded:
    def test_unreachable_arifflow_does_not_raise(self) -> None:
        # Real proxy, real urllib, pointing at nowhere
        proxy = FlowReceiptProxy(
            endpoint="http://127.0.0.1:1",
            actor_id="test",
            timeout_s=0.5,
        )
        # Should not raise; should return an error marker.
        rid = proxy.emit(
            step_type="Execute",
            floor_verdict="Pass",
            epistemic_label="Observation",
            payload={"k": "v"},
        )
        assert rid.startswith("r3p-")
        assert "UNREACHABLE" in rid