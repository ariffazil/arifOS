"""FIX 2026-10-27 — metabolic classifier: tool-aware step_type mapping.

Failure class: _build_arifflow_receipt mapped verdict→step_type only, so the
kernel's verification-native instruments (arif_observe) and organ dispatch
(arif_route) were ingested to arifFlow as Execute. Kernel-internal probe
actors accrued exec-without-verify (f006-edge-probe: 436 consecutive) and the
FQ engine — honestly — held them forever. Spec: FLOW_RECEIPT_v1 StepType —
Verify = "Verification, audit, floor check"; Route = "Routing — dispatch to
another organ"; engine counts Execute|Merge as work, Verify as verification,
Route neutral (receipt.rs is_work_execution / is_verification).
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.telemetry import _build_arifflow_receipt


def _classify(tool: str, verdict: str = "OK") -> str:
    receipt = _build_arifflow_receipt(
        tool_name=tool,
        verdict=verdict,
        latency_ms=1.0,
        session_id=None,
        actor_id="test-actor",
        metadata=None,
    )
    return receipt["step_type"]


class TestVerdictOverridesKeepPriority:
    """HOLD/VOID/SEAL/SABAR semantics survive the tool-aware refactor."""

    def test_hold_maps_cool_even_for_observe(self):
        assert _classify("arif_observe", "HOLD") == "Cool"

    def test_void_maps_cool(self):
        assert _classify("arif_observe", "VOID") == "Cool"

    def test_seal_maps_seal_even_for_observe(self):
        assert _classify("arif_observe", "SEAL") == "Seal"

    def test_sabar_maps_verify_even_for_non_observe(self):
        assert _classify("arif_forge", "SABAR") == "Verify"


class TestToolAwareClassification:
    """Verification-native tools classify per FLOW_RECEIPT_v1 spec."""

    def test_arif_observe_ok_is_verify(self):
        assert _classify("arif_observe", "OK") == "Verify"

    def test_arif_observe_pass_is_verify(self):
        assert _classify("arif_observe", "PASS") == "Verify"

    def test_arif_route_ok_is_route_neutral(self):
        assert _classify("arif_route", "OK") == "Route"

    def test_arif_init_ok_is_execute(self):
        # Session minting is setup work, not verification — stays Execute.
        assert _classify("arif_init", "OK") == "Execute"

    def test_arif_think_ok_is_execute(self):
        # Reasoning is work, not consequence-verification.
        assert _classify("arif_think", "OK") == "Execute"

    def test_arif_forge_ok_is_execute(self):
        assert _classify("arif_forge", "OK") == "Execute"

    def test_arif_seal_non_seal_verdict_untouched(self):
        assert _classify("arif_seal", "OK") == "Execute"

    def test_caution_observe_is_verify(self):
        assert _classify("arif_observe", "CAUTION") == "Verify"


class TestEpistemicLabelConsistency:
    """Observe receipts stay epistemically Observation even as step Verify."""

    def test_observe_verify_keeps_observation_label(self):
        receipt = _build_arifflow_receipt(
            tool_name="arif_observe",
            verdict="OK",
            latency_ms=1.0,
            session_id=None,
            actor_id="test-actor",
            metadata=None,
        )
        assert receipt["step_type"] == "Verify"
        assert receipt["epistemic_label"] == "Observation"


class TestProbeActorFlowShape:
    """Regression: a probe cycle (init→route→observe) must produce ≥1 Verify
    and its Route receipts must not inflate the execute denominator."""

    def test_probe_cycle_yields_verify_and_neutral_route(self):
        steps = [
            _classify("arif_init"),
            _classify("arif_route"),
            _classify("arif_observe"),
        ]
        assert steps == ["Execute", "Route", "Verify"]
        execute_count = sum(1 for s in steps if s in ("Execute", "Merge"))
        verify_count = sum(1 for s in steps if s == "Verify")
        assert verify_count / execute_count >= 0.5  # clears FQ floor band
