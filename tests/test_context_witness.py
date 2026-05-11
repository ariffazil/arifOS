"""
tests/test_meaning_witness.py — Meaning Witness pipeline integration tests.

Acceptance:
D. output contains all schema fields.
E. governance overrides quote interpretation.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.context_witness import arifos_context_witness

REQUIRED_TOP_LEVEL_FIELDS = {
    "status",
    "meaning",
    "quote_witness",
    "interpretation",
    "arifos_alignment",
    "decision_boundary",
    "human_decision_required",
    "recommended_action",
    "uncertainty",
    "safety_notes",
}

REQUIRED_ARIFOS_ALIGNMENT_FIELDS = {"physics", "math", "linguistic"}

REQUIRED_QUOTE_WITNESS_FIELDS = {
    "id",
    "quote",
    "author",
    "tradition",
    "theme",
    "source_status",
}


class TestMeaningWitnessSchema:
    @pytest.mark.anyio
    async def test_output_contains_all_schema_fields(self):
        result = await arifos_context_witness(
            event="A developer wants to delete a production database.",
            state={"actor": "developer"},
            judgment={"intent": "destructive"},
            risk_level="high",
            domain="governance",
        )
        missing = REQUIRED_TOP_LEVEL_FIELDS - set(result.keys())
        assert not missing, f"Missing top-level fields: {missing}"

        alignment = result.get("arifos_alignment") or {}
        missing_align = REQUIRED_ARIFOS_ALIGNMENT_FIELDS - set(alignment.keys())
        assert not missing_align, f"Missing arifos_alignment fields: {missing_align}"

        qw = result.get("quote_witness")
        assert qw is not None, "quote_witness must not be None for successful witness"
        missing_qw = REQUIRED_QUOTE_WITNESS_FIELDS - set(qw.keys())
        assert not missing_qw, f"Missing quote_witness fields: {missing_qw}"

    @pytest.mark.anyio
    async def test_status_is_ok_or_partial_or_hold(self):
        result = await arifos_context_witness(
            event="Routine health check",
            state={},
            judgment={},
            risk_level="low",
            domain="ops",
        )
        assert result["status"] in ("ok", "partial", "hold", "refuse")

    @pytest.mark.anyio
    async def test_quote_witness_has_non_empty_id_and_author(self):
        result = await arifos_context_witness(
            event="System alert",
            state={},
            judgment={},
            risk_level="medium",
            domain="governance",
        )
        if result["status"] in ("ok", "partial"):
            qw = result["quote_witness"]
            assert qw["id"]
            assert qw["author"]

    @pytest.mark.anyio
    async def test_include_quote_false_blanks_quote_text(self):
        result = await arifos_context_witness(
            event="Test",
            state={},
            judgment={},
            risk_level="low",
            domain="ethics",
            include_quote=False,
        )
        if result["status"] in ("ok", "partial"):
            assert result["quote_witness"]["quote"] == ""

    @pytest.mark.anyio
    async def test_uncertainty_is_a_list(self):
        result = await arifos_context_witness(
            event="Test",
            state={},
            judgment={},
            risk_level="low",
            domain="ethics",
        )
        assert isinstance(result["uncertainty"], list)

    @pytest.mark.anyio
    async def test_safety_notes_is_a_list(self):
        result = await arifos_context_witness(
            event="Test",
            state={},
            judgment={},
            risk_level="low",
            domain="ethics",
        )
        assert isinstance(result["safety_notes"], list)


class TestMeaningWitnessFallback:
    @pytest.mark.anyio
    async def test_fallback_triggered_when_sea_lion_unavailable(self):
        # With no API key, SEA-LION should fail and fallback should run
        result = await arifos_context_witness(
            event="Database corruption detected",
            state={},
            judgment={},
            risk_level="critical",
            domain="governance",
        )
        # Fallback produces status="partial"
        assert result["status"] in ("partial", "ok")
        assert result["human_decision_required"] is True
        assert result["quote_witness"] is not None
