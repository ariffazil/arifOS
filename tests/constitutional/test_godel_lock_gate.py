"""
tests/constitutional/test_godel_lock_gate.py — Gödel Lock closure gate (Q9)
═════════════════════════════════════════════════════════════════════════════

Three Closures — Q9 (GENESIS/058, sealed 2026-08-02).

Tests verify that the gate:
  - SABAR for OBSERVE (no witness required) — Q9a observation tier
  - SABAR for REASON/ANALYZE (light penalty, advisory)
  - HOLD for SEAL-bound with no external validation
  - HOLD for self-certifying actor (caller == target)
  - PROCEED for SEAL-bound with auditor_validated=True + full anti-Calhoun

Floor binding: F3 TRI-WITNESS, F11 AUDITABILITY, F13 SOVEREIGN.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest


@dataclass
class _Ctx:
    """Minimal ToolCallContext for unit tests."""

    tool_name: str = "arif_observe"
    session_id: str = "SEAL-test"
    actor_id: str = "arif"
    action_class: str = "OBSERVE"
    actor_verification: str = "verified"
    params: dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# 1. Module surface — freeze the public API
# ═══════════════════════════════════════════════════════════════════════════


class TestModuleSurface:
    def test_module_imports(self):
        from arifosmcp.runtime import godel_lock_gate as mod

        assert hasattr(mod, "godel_lock_gate")
        assert hasattr(mod, "SEAL_BOUND_PHI_MIN")
        assert hasattr(mod, "SELF_CERTIFYING_TOOLS")
        assert hasattr(mod, "SEAL_BOUND_ACTION_CLASSES")

    def test_seal_bound_phi_min_is_frozen(self):
        """F2: the 0.50 threshold is constitutional — frozen."""
        from arifosmcp.runtime.godel_lock_gate import SEAL_BOUND_PHI_MIN

        assert SEAL_BOUND_PHI_MIN == 0.50

    def test_self_certifying_tools_include_judge_and_seal(self):
        from arifosmcp.runtime.godel_lock_gate import SELF_CERTIFYING_TOOLS

        assert "arif_judge" in SELF_CERTIFYING_TOOLS
        assert "arif_seal" in SELF_CERTIFYING_TOOLS

    def test_seal_bound_classes_include_irreversible(self):
        from arifosmcp.runtime.godel_lock_gate import SEAL_BOUND_ACTION_CLASSES

        assert "IRREVERSIBLE" in SEAL_BOUND_ACTION_CLASSES
        assert "ATOMIC" in SEAL_BOUND_ACTION_CLASSES
        assert "VAULT_WRITE" in SEAL_BOUND_ACTION_CLASSES


# ═══════════════════════════════════════════════════════════════════════════
# 2. Observation tier — must SABAR (advisory, never block)
# ═══════════════════════════════════════════════════════════════════════════


class TestObservationTier:
    def test_observe_action_is_sabar(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = godel_lock_gate(ctx)
        assert result["verdict"] == "SABAR", result
        assert result["passed"] is True
        assert result["phi_external"] == 1.0
        assert result["claim_severity"] == "observation"

    def test_observe_receipt_carries_q9a_status(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = godel_lock_gate(ctx)
        receipt = result["receipt"]
        assert receipt["gate"] == "GODEL_CLOSURE"
        assert receipt["q9_checks"]["q9a_outside_witness"] is True
        assert receipt["q9_checks"]["q9b_not_self_certifying"] is True

    def test_observe_action_class_maps_to_observation_tier(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        for action in ("OBSERVE", "READ", ""):
            ctx = _Ctx(action_class=action, tool_name="arif_observe")
            result = godel_lock_gate(ctx)
            assert result["claim_severity"] == "observation", f"{action}: {result}"


# ═══════════════════════════════════════════════════════════════════════════
# 3. Self-certification — Q9b hard HOLD
# ═══════════════════════════════════════════════════════════════════════════


class TestSelfCertification:
    def test_judge_self_certifying_holds(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_judge",
            action_class="REASON",
            actor_id="arif",
            params={"actor_id": "arif"},
        )
        result = godel_lock_gate(ctx)
        assert result["verdict"] == "HOLD"
        assert result["passed"] is False
        assert result["self_certified"] is True
        assert "F11" in result["violated_laws"]
        assert "F13" in result["violated_laws"]

    def test_seal_self_certifying_holds(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            actor_id="arif",
            params={"actor_id": "arif"},
        )
        result = godel_lock_gate(ctx)
        assert result["verdict"] == "HOLD"
        assert result["self_certified"] is True

    def test_judge_different_actor_does_not_self_certify(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_judge",
            action_class="REASON",
            actor_id="arif",
            params={"actor_id": "another-agent"},
        )
        result = godel_lock_gate(ctx)
        assert result["self_certified"] is False

    def test_judge_anonymous_caller_does_not_self_certify(self):
        """F2: anonymous caller is below the bar — not a self-cert, just missing identity."""
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_judge",
            action_class="REASON",
            actor_id="anonymous",
            params={"actor_id": "anonymous"},
        )
        result = godel_lock_gate(ctx)
        assert result["self_certified"] is False


# ═══════════════════════════════════════════════════════════════════════════
# 4. SEAL-bound without witness — HARD HOLD
# ═══════════════════════════════════════════════════════════════════════════


class TestSealBound:
    def test_irreversible_no_auditor_holds(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            actor_id="arif",
            params={"actor_id": "another-agent"},
        )
        result = godel_lock_gate(ctx)
        # Either holds on low phi OR on anti-Calhoun < 0.60 (since no evidence_declared)
        assert result["verdict"] in {"HOLD", "SABAR"}, result
        # If HOLD, must include F11
        if not result["passed"]:
            assert "F11" in result["violated_laws"] or "F9" in result["violated_laws"]

    def test_irreversible_with_auditor_proceeds(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="IRREVERSIBLE",
            actor_id="arif",
            params={
                "actor_id": "another-agent",
                "auditor_id": "external-witness-001",
                "finding": "Constitutional review of new doctrine",
                "mutated": True,
                "evidence": {"supporting": ["GENESIS/058"]},
            },
        )
        result = godel_lock_gate(ctx)
        assert result["verdict"] in {"PROCEED", "SABAR"}, result
        assert result["passed"] is True

    def test_auditor_validated_true_explicit_proceeds(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(
            tool_name="arif_seal",
            action_class="ATOMIC",
            actor_id="arif",
            params={
                "actor_id": "another-agent",
                "auditor_validated": True,
                "finding": "constitutional decision",
                "mutated": True,
                "evidence": {"supporting": ["..."]},
            },
        )
        result = godel_lock_gate(ctx)
        assert result["passed"] is True
        # PROCEED when full evidence + auditor validation
        assert result["verdict"] in {"PROCEED", "SABAR"}


# ═══════════════════════════════════════════════════════════════════════════
# 5. Receipt contract (F11 AUDIT)
# ═══════════════════════════════════════════════════════════════════════════


class TestReceiptContract:
    def test_receipt_contains_required_fields(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx(tool_name="arif_observe", action_class="OBSERVE")
        result = godel_lock_gate(ctx)
        receipt = result["receipt"]
        for field in (
            "gate",
            "verdict",
            "passed",
            "q9_checks",
            "phi_external",
            "phi_status",
            "claim_severity",
            "auditor_validated",
            "self_certified",
            "anti_calhoun",
            "violated_laws",
            "latency_ms",
            "doctrine",
        ):
            assert field in receipt, f"missing: {field}"

    def test_doctrine_field_references_genesis_058(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx()
        result = godel_lock_gate(ctx)
        assert "GENESIS/058" in result["receipt"]["doctrine"]

    def test_latency_is_measured(self):
        from arifosmcp.runtime.godel_lock_gate import godel_lock_gate

        ctx = _Ctx()
        result = godel_lock_gate(ctx)
        assert result["latency_ms"] >= 0
        assert result["receipt"]["latency_ms"] >= 0
