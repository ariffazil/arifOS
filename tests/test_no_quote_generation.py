"""
tests/test_no_quote_generation.py — SEA-LION must never invent quotes.

Acceptance:
A. Mock SEA-LION returns quote not in ledger → status=hold, error=quote_not_in_approved_ledger
B. Mock SEA-LION mutates quote text → status=hold, error=quote_integrity_failed
"""

from __future__ import annotations

import pytest
from unittest.mock import patch

from arifosmcp.runtime.context_witness import arifos_context_witness


async def _fake_sea_lion_not_in_ledger(*args, **kwargs):
    return {
        "selected_quote_id": "FAKE_QUOTE_999",
        "meaning": "Fake meaning.",
        "interpretation": "Fake interpretation.",
        "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
        "decision_boundary": "None",
        "human_decision_required": False,
        "recommended_action": "Proceed.",
        "uncertainty": [],
        "safety_notes": [],
    }


async def _fake_sea_lion_mutated_text(*args, **kwargs):
    candidates = kwargs.get("candidate_quotes", [])
    if not candidates:
        raise RuntimeError("No candidates")
    q = candidates[0]
    return {
        "selected_quote_id": q["id"],
        "quote": q["quote"] + " MUTATED",  # stray mutated quote text
        "meaning": "Fake meaning.",
        "interpretation": "Fake interpretation.",
        "arifos_alignment": {"physics": "p", "math": "m", "linguistic": "l"},
        "decision_boundary": "None",
        "human_decision_required": False,
        "recommended_action": "Proceed.",
        "uncertainty": [],
        "safety_notes": [],
    }


class TestNoQuoteGeneration:
    @pytest.mark.anyio
    @patch("arifosmcp.runtime.context_witness.interpret_with_sea_lion", _fake_sea_lion_not_in_ledger)
    async def test_mock_sea_lion_returns_unknown_quote(self):
        result = await arifos_context_witness(
            event="Test event",
            state={},
            judgment={},
            risk_level="medium",
            domain="ethics",
        )
        assert result["status"] == "hold"
        assert "quote_not_in_approved_ledger" in str(result.get("safety_notes", [])) or "quote_not_in_approved_ledger" in result.get("meaning", "")

    @pytest.mark.anyio
    @patch("arifosmcp.runtime.context_witness.interpret_with_sea_lion", _fake_sea_lion_mutated_text)
    async def test_mock_sea_lion_mutates_quote_text(self):
        result = await arifos_context_witness(
            event="Test event",
            state={},
            judgment={},
            risk_level="medium",
            domain="ethics",
        )
        assert result["status"] == "hold"
        assert "quote_integrity_failed" in str(result.get("safety_notes", [])) or "quote_integrity_failed" in result.get("meaning", "")
