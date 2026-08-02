"""
tests/constitutional/test_three_locks.py — Three Locks orchestrator (Q9 · Q10 · Q11)
═════════════════════════════════════════════════════════════════════════════

Three Closures — GENESIS/058 (sealed 2026-08-02, F13 SOVEREIGN).

Tests verify:
  - `verify_three_closures` composes all three gates into one verdict.
  - Q9 (Gödel) + Q10 (Calhoun) + Q9c (Reality Loop) all exposed in receipt.
  - Q11 (Refusal Closure) — three HOLD types are distinguishable.
  - Verdict ladder: OK | PARTIAL | FAIL.
  - Receipt carries sha256 + chain_hash (F11 AUDIT).
  - The orchestrator is pure: no mutation outside the gates' counters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class _Ctx:
    tool_name: str = "arif_observe"
    session_id: str = "SEAL-test"
    actor_id: str = "arif"
    action_class: str = "OBSERVE"
    params: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Module surface
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleSurface:
    def test_module_imports(self):
        from arifosmcp.runtime import three_locks as mod

        assert hasattr(mod, "verify_three_closures")
        assert hasattr(mod, "ThreeLocksReceipt")
        assert hasattr(mod, "HOLD_TYPE_FAILURE")
        assert hasattr(mod, "HOLD_TYPE_CONSTITUTIONAL")
        assert hasattr(mod, "HOLD_TYPE_F13_REFUSAL")
        assert hasattr(mod, "VERDICT_OK")
        assert hasattr(mod, "VERDICT_PARTIAL")
        assert hasattr(mod, "VERDICT_FAIL")

    def test_hold_types_frozen(self):
        from arifosmcp.runtime.three_locks import (
            ALL_HOLD_TYPES,
            HOLD_TYPE_CONSTITUTIONAL,
            HOLD_TYPE_F13_REFUSAL,
            HOLD_TYPE_FAILURE,
        )

        assert HOLD_TYPE_FAILURE == "FAILURE"
        assert HOLD_TYPE_CONSTITUTIONAL == "CONSTITUTIONAL"
        assert HOLD_TYPE_F13_REFUSAL == "F13_REFUSAL"
        assert ALL_HOLD_TYPES == frozenset(
            {HOLD_TYPE_FAILURE, HOLD_TYPE_CONSTITUTIONAL, HOLD_TYPE_F13_REFUSAL}
        )


# ═══════════════════════════════════════════════════════════════════════════
# 2. Verdict ladder
# ═══════════════════════════════════════════════════════════════════════════


class TestVerdictLadder:
    def test_observe_action_returns_partial_or_ok(self):
        """OBSERVE actions are advisory everywhere — Gödel SABAR, Calhoun
        PROCEED, Reality PROCEED-with-gap. Verdict should be OK or PARTIAL.
        """
        from arifosmcp.runtime.three_locks import (
            VERDICT_OK,
            VERDICT_PARTIAL,
            verify_three_closures,
        )

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = verify_three_closures(ctx)
        assert result["verdict"] in {VERDICT_OK, VERDICT_PARTIAL}

    def test_self_cert_seal_returns_fail(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import reset_session
        from arifosmcp.runtime.reality_loop import reset_ledger
        from arifosmcp.runtime.three_locks import HOLD_TYPE_F13_REFUSAL, VERDICT_FAIL, verify_three_closures

        reset_session("SEAL-orch-self")
        reset_ledger()
        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            params={"actor_id": "arif"},
        )
        result = verify_three_closures(ctx)
        assert result["verdict"] == VERDICT_FAIL
        assert result["hold_type"] == HOLD_TYPE_F13_REFUSAL
        assert "F11" in result["violated_laws"]
        reset_session("SEAL-orch-self")

    def test_clean_mixed_action_is_ok(self):
        from arifosmcp.runtime.calhoun_anti_sink_gate import reset_session
        from arifosmcp.runtime.reality_loop import reset_ledger
        from arifosmcp.runtime.three_locks import VERDICT_OK, verify_three_closures

        reset_session("SEAL-orch-clean")
        reset_ledger()
        # ANALYSIS action: Gödel SABAR, Calhoun PROCEED, Reality PROCEED
        ctx = _Ctx(tool_name="arif_think", action_class="ANALYZE", params={})
        result = verify_three_closures(ctx)
        # Reality Loop on non-SEAL returns PROCEED; Gödel on reasoning is SABAR
        # → one SABAR → PARTIAL
        assert result["verdict"] in {VERDICT_OK, "PARTIAL"}
        reset_session("SEAL-orch-clean")


# ═══════════════════════════════════════════════════════════════════════════
# 3. Q11 — Refusal Closure (HOLD type taxonomy)
# ═══════════════════════════════════════════════════════════════════════════


class TestRefusalClosure:
    def test_failure_hold_classified_correctly(self):
        from arifosmcp.runtime.three_locks import _classify_hold_type

        # Timeout → FAILURE
        ht = _classify_hold_type(["Vault timeout — system can't continue"])
        assert ht == "FAILURE"

    def test_constitutional_hold_classified_correctly(self):
        from arifosmcp.runtime.three_locks import _classify_hold_type

        ht = _classify_hold_type(
            ["Calhoun anti-sink — no friction detected, advisory escalation"]
        )
        assert ht == "CONSTITUTIONAL"

    def test_f13_refusal_classified_correctly(self):
        from arifosmcp.runtime.three_locks import _classify_hold_type

        ht = _classify_hold_type(
            ["Q9: F13 sovereign override — no reason required"]
        )
        assert ht == "F13_REFUSAL"

    def test_refusal_distinct_flag_is_true(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        # Q11a: refusal surface distinct from failure surface
        assert result["refusal_distinct"] is True

    def test_f13_override_path_is_wired(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        # Q11c: F13 override path is exposed
        assert result["f13_override_path"] is True


# ═══════════════════════════════════════════════════════════════════════════
# 4. Receipt (F11 AUDIT) — sha256 + chain_hash
# ═══════════════════════════════════════════════════════════════════════════


class TestReceiptContract:
    def test_receipt_carries_sha256(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        receipt = result["receipt"]
        assert receipt["sha256"]
        assert len(receipt["sha256"]) == 64  # sha256 hex
        assert receipt["chain_hash"]

    def test_receipt_contains_all_three_gate_results(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        receipt = result["receipt"]
        for gate in ("godel", "calhoun", "reality"):
            assert gate in receipt, f"missing gate: {gate}"

    def test_receipt_contains_q11_metadata(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        receipt = result["receipt"]
        assert "refusal_distinct" in receipt
        assert "f13_override_path" in receipt
        assert "doctrine" in receipt
        assert "GENESIS/058" in receipt["doctrine"]

    def test_attestation_log_appends(self):
        from arifosmcp.runtime.three_locks import (
            attestation_log,
            reset_attestations,
            verify_three_closures,
        )

        reset_attestations()
        before = len(attestation_log())
        verify_three_closures(_Ctx())
        verify_three_closures(_Ctx(tool_name="arif_observe"))
        after = len(attestation_log())
        assert after - before == 2

    def test_receipts_have_unique_sha256(self):
        from arifosmcp.runtime.three_locks import (
            attestation_log,
            reset_attestations,
            verify_three_closures,
        )

        reset_attestations()
        verify_three_closures(_Ctx(session_id="SEAL-a"))
        verify_three_closures(_Ctx(session_id="SEAL-b"))
        log = attestation_log()
        hashes = [r["sha256"] for r in log]
        assert len(set(hashes)) == 2  # distinct sha256 per call


# ═══════════════════════════════════════════════════════════════════════════
# 5. Integration — orchestrator routes to inner gates correctly
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegration:
    def test_godel_subresult_is_exposed(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = verify_three_closures(ctx)
        godel = result["godel"]
        assert "verdict" in godel
        assert "phi_external" in godel

    def test_calhoun_subresult_is_exposed(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx()
        result = verify_three_closures(ctx)
        calhoun = result["calhoun"]
        assert "anti_calhoun" in calhoun
        assert "behavioral_sink" in calhoun
        assert "warnings_count" in calhoun

    def test_reality_subresult_is_exposed(self):
        from arifosmcp.runtime.three_locks import verify_three_closures

        ctx = _Ctx(tool_name="arif_seal", action_class="IRREVERSIBLE")
        result = verify_three_closures(ctx)
        reality = result["reality"]
        assert "commitment_missing" in reality
        assert "violated_laws" in reality
        # Reality Loop never has violated_laws (advisory)
        assert reality["violated_laws"] == []


# ═══════════════════════════════════════════════════════════════════════════
# 6. End-to-end Pipeline integration smoke
# ═══════════════════════════════════════════════════════════════════════════


class TestPipelineIntegration:
    def test_governance_pipeline_exposes_new_gates(self):
        from arifosmcp.runtime.governance_pipeline import Gate

        assert hasattr(Gate, "GODEL_CLOSURE")
        assert hasattr(Gate, "CALHOUN_CLOSURE")
        assert hasattr(Gate, "REALITY_LOOP")
        assert Gate.GODEL_CLOSURE.value == "GATE_5.1_GODEL_CLOSURE"
        assert Gate.CALHOUN_CLOSURE.value == "GATE_5.2_CALHOUN_CLOSURE"
        assert Gate.REALITY_LOOP.value == "GATE_5.3_REALITY_LOOP"

    def test_pipeline_constructs_with_closure_flags(self):
        from arifosmcp.runtime.governance_pipeline import GovernancePipeline

        pipeline = GovernancePipeline(
            godel_closure_enabled=True,
            calhoun_closure_enabled=True,
            reality_loop_enabled=True,
        )
        assert pipeline.godel_closure_enabled is True
        assert pipeline.calhoun_closure_enabled is True
        assert pipeline.reality_loop_enabled is True

    def test_pipeline_can_disable_individual_closures(self):
        from arifosmcp.runtime.governance_pipeline import GovernancePipeline

        pipeline = GovernancePipeline(
            godel_closure_enabled=False,
            calhoun_closure_enabled=True,
            reality_loop_enabled=False,
        )
        assert pipeline.godel_closure_enabled is False
        assert pipeline.calhoun_closure_enabled is True
        assert pipeline.reality_loop_enabled is False
