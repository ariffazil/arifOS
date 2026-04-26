"""
tests/test_governance_boundary.py — Governance boundary enforcement tests.

Acceptance:
C. risk_level = irreversible → human_decision_required = true,
   recommended_action must not execute
E. Governance overrides quote interpretation.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.context_witness import arifos_context_witness
from arifosmcp.runtime.context_safety import validate_interpretation_safety
from arifosmcp.runtime.quote_ledger import load_quote_ledger


class TestGovernanceBoundary:
    @pytest.mark.anyio
    async def test_irreversible_risk_requires_human_decision(self):
        result = await arifos_context_witness(
            event="Deploy to production",
            state={},
            judgment={},
            risk_level="irreversible",
            domain="governance",
        )
        assert result["human_decision_required"] is True
        action = result["recommended_action"].lower()
        forbidden = ("execute", "commit", "deploy", "seal", "push", "destroy", "delete", "drop")
        assert not any(word in action for word in forbidden), (
            f"recommended_action for irreversible risk must not suggest execution: {result['recommended_action']}"
        )

    @pytest.mark.anyio
    async def test_critical_risk_requires_human_decision(self):
        result = await arifos_context_witness(
            event="Modify constitutional map",
            state={},
            judgment={},
            risk_level="critical",
            domain="governance",
        )
        assert result["human_decision_required"] is True

    @pytest.mark.anyio
    async def test_high_risk_requires_human_decision(self):
        result = await arifos_context_witness(
            event="Rotate API keys",
            state={},
            judgment={},
            risk_level="high",
            domain="governance",
        )
        assert result["human_decision_required"] is True

    @pytest.mark.anyio
    async def test_low_risk_may_not_require_human_decision(self):
        result = await arifos_context_witness(
            event="Check system status",
            state={},
            judgment={},
            risk_level="low",
            domain="ops",
        )
        # Low risk should NOT force human_decision_required to True
        assert result["human_decision_required"] is False

    def test_safety_refuses_execution_for_irreversible(self):
        ledger = load_quote_ledger()
        candidates = [q for q in ledger if q["allow_use"] and q["source_status"] != "uncertain"][:3]
        interpretation = {
            "selected_quote_id": candidates[0]["id"],
            "meaning": "Deploy now.",
            "interpretation": "Execute immediately.",
            "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
            "decision_boundary": "None",
            "human_decision_required": False,
            "recommended_action": "Execute deployment immediately.",
            "uncertainty": [],
            "safety_notes": [],
        }
        safety = validate_interpretation_safety(interpretation, candidates, risk_level="irreversible")
        assert safety["status"] == "refuse"
        assert "must not execute" in safety["error"]

    def test_safety_holds_when_human_required_is_false_for_high_risk(self):
        ledger = load_quote_ledger()
        candidates = [q for q in ledger if q["allow_use"] and q["source_status"] != "uncertain"][:3]
        interpretation = {
            "selected_quote_id": candidates[0]["id"],
            "meaning": "x",
            "interpretation": "y",
            "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
            "decision_boundary": "None",
            "human_decision_required": False,
            "recommended_action": "Proceed.",
            "uncertainty": [],
            "safety_notes": [],
        }
        safety = validate_interpretation_safety(interpretation, candidates, risk_level="high")
        assert safety["status"] == "hold"
        assert "human_decision_required must be true" in safety["error"]
