"""
tests/constitutional/test_heart_critique_anticalhoun.py — Anti-Calhoun Governance Drift

═══════════════════════════════════════════════════════════════════════════════
TASK-P2-04 — Anti-Calhoun invariant: the system must NOT optimize for
density/silence/withdrawal. If an agent repeatedly returns empty outputs,
minimal responses, or "pass" exceptions without organ event emission, it has
entered a governance drift.

The scan lives on arif_critique (stage 666) and emits:
  - result["behavioral_sink_scan"] = { sink_ratio, status: CLEAR|WARNING, ... }
  - When WARNING: a risk entry appended to result["risks_found"] (type=
    "anti_calhoun_sink", severity="medium", floor_cited="F5").

The scan is a SOFT signal (SABAR). It NEVER escalates the action verdict
to VOID — it only surfaces a posture flag for the operator and a risk
entry that Judge may compose downstream.

F1 AMANAH:    scan is read-only, attaches to result dict.
F2 TRUTH:     counts are exact, sink_ratio is computed (not fabricated).
F4 CLARITY:   CLEAR for empty/absent history; WARNING above 0.40 threshold.
F5 PEACE:     sink signals operator-antenna degradation, surfaces reason.
F9 ANTI-HANTU: empty history returns 0.0, not hidden bias.
F11 AUDIT:    every WARNING emits a receipt-shaped risk entry.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

import arifosmcp.runtime.llm_client as llm_client
from arifosmcp.tools.heart import (
    _ANTI_CALHOUN_SINK_THRESHOLD,
    _behavioral_sink_scan,
    _is_empty_output,
    arif_critique,
)

# ═══════════════════════════════════════════════════════════════════════════════
# 1. _is_empty_output — per-output classifier
# ═══════════════════════════════════════════════════════════════════════════════


class TestIsEmptyOutput:
    """Freeze the empty/minimal classifier that feeds the Anti-Calhoun scan."""

    def test_none_is_empty(self):
        assert _is_empty_output(None) is True

    def test_empty_string_is_empty(self):
        assert _is_empty_output("") is True
        assert _is_empty_output("   ") is True
        assert _is_empty_output("\n\t  \n") is True

    def test_pass_stubs_are_empty(self):
        """Short "pass" / "ok" / "skipped" tokens count as non-emission."""
        assert _is_empty_output("pass") is True
        assert _is_empty_output("OK") is True
        assert _is_empty_output("  no-op  ") is True
        assert _is_empty_output("skipped") is True
        assert _is_empty_output("null") is True
        assert _is_empty_output("...") is True
        assert _is_empty_output("—") is True

    def test_substantive_strings_are_not_empty(self):
        assert _is_empty_output("actual critique output with risk findings") is False
        assert _is_empty_output("partial: needs review") is False

    def test_pass_token_only_counts_when_short(self):
        """Long strings starting with a pass token are substantive."""
        # "passed" is more than 24 chars and is not in the stub set.
        long_pass = "passed all checks with caveats noted in attached evidence"
        assert len(long_pass) >= 24
        assert _is_empty_output(long_pass) is False

    def test_empty_collections_are_empty(self):
        assert _is_empty_output([]) is True
        assert _is_empty_output({}) is True
        assert _is_empty_output(set()) is True
        assert _is_empty_output(()) is True

    def test_dict_with_all_empty_values_is_empty(self):
        """Recursively empty dict values still count as empty."""
        assert _is_empty_output({"a": None, "b": "", "c": []}) is True

    def test_dict_with_one_substantive_value_is_substantive(self):
        assert _is_empty_output({"a": None, "b": "real critique content"}) is False

    def test_list_with_real_item_is_substantive(self):
        assert _is_empty_output([None, "", {"x": 1}]) is False


# ═══════════════════════════════════════════════════════════════════════════════
# 2. _behavioral_sink_scan — pure-function unit tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBehavioralSinkScan:
    """Freeze the WARNING threshold and CLEAR/WARNING transition behavior."""

    def test_no_history_returns_clear_zero(self):
        """F9 ANTI-HANTU: empty/absent history is CLEAR, ratio=0.0 — no hidden bias."""
        out = _behavioral_sink_scan(None)
        assert out["status"] == "CLEAR"
        assert out["sink_ratio"] == 0.0
        assert out["empty_count"] == 0
        assert out["total_outputs"] == 0
        assert out["anticalhoun"] is None

    def test_empty_list_returns_clear(self):
        out = _behavioral_sink_scan([])
        assert out["status"] == "CLEAR"
        assert out["sink_ratio"] == 0.0
        assert out["empty_count"] == 0
        assert out["total_outputs"] == 0

    def test_zero_empties_in_10_outputs_is_clear(self):
        """Mock session with 0/10 empty outputs → status=CLEAR (task spec)."""
        history = [f"substantive output #{i}" for i in range(10)]
        out = _behavioral_sink_scan(history)
        assert out["status"] == "CLEAR"
        assert out["sink_ratio"] == 0.0
        assert out["empty_count"] == 0
        assert out["total_outputs"] == 10
        assert out["anticalhoun"] is None

    def test_five_of_ten_empties_is_warning_with_ratio_0_5(self):
        """Mock session with 5/10 empty outputs → sink_ratio=0.50, status=WARNING (task spec)."""
        history = [
            None,  # empty
            "",  # empty
            "pass",  # empty
            {"status": "ok"},  # empty (every value is empty)
            None,  # empty
            "first substantive output line",
            "second substantive output line",
            "third substantive output line",
            "fourth substantive output line",
            "fifth substantive output line",
        ]
        out = _behavioral_sink_scan(history)
        assert out["status"] == "WARNING", out
        assert out["sink_ratio"] == 0.5
        assert out["empty_count"] == 5
        assert out["total_outputs"] == 10
        assert out["anticalhoun"] == "SINK_WARNING"
        assert out["floor"] == "F5"
        assert "governance drift detected" in out["reason"]
        assert "5/10" in out["reason"]

    def test_threshold_is_strictly_above_0_4(self):
        """Exactly 0.40 sink_ratio is CLEAR (SABAR — borderline is preserved)."""
        # 4/10 empties = 0.4 → MUST be CLEAR (operator gets to see the line).
        history = [None, "", "pass", "ok"] + [f"substantive #{i}" for i in range(6)]
        out = _behavioral_sink_scan(history)
        assert out["sink_ratio"] == 0.4
        assert out["status"] == "CLEAR"
        # 5/10 = 0.5 → WARNING (already covered above).

    def test_majority_empties_is_warning(self):
        """8 of 10 empties — strong governance drift."""
        history = [None, "", "pass", "ok"] * 2 + ["two substantive outputs here"] * 2
        out = _behavioral_sink_scan(history)
        assert out["status"] == "WARNING"
        assert out["empty_count"] == 8
        assert out["sink_ratio"] == 0.8

    def test_warning_carries_floor_and_reason(self):
        """WARNING always carries floor (F5) and reason for downstream Audit."""
        history = [None] * 6 + ["substantive " * 5] * 4  # 6/10 empties
        out = _behavioral_sink_scan(history)
        assert out["status"] == "WARNING"
        assert out["floor"] == "F5"
        assert out["reason"]
        assert "Anti-Calhoun" not in out["reason"]  # plain English, not jargon

    def test_clear_omits_floor_and_reason(self):
        """CLEAR must not invent fields the operator did not ask for."""
        history = ["substantive output"] * 5
        out = _behavioral_sink_scan(history)
        assert "floor" not in out
        assert "reason" not in out


# ═══════════════════════════════════════════════════════════════════════════════
# 3. arif_critique integration — scan attached to result
# ═══════════════════════════════════════════════════════════════════════════════


class TestArifCritiqueAntiCalhounIntegration:
    """Verify the scan is wired into the arif_critique (stage 666) result envelope.

    All remote LLM providers are patched to raise LLMUnavailableError so the
    function falls back to the deterministic path. The Anti-Calhoun scan is
    pure (deterministic, local), so the fallback path is sufficient and fast.
    """

    @pytest.fixture(autouse=True)
    def _disable_remote_llm(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Force deterministic fallback so the scan test stays fast and offline."""
        for name in ("_call_tokenrouter", "_call_minimax", "_call_mimo", "_call_sea_lion"):
            monkeypatch.setattr(
                llm_client,
                name,
                AsyncMock(side_effect=llm_client.LLMUnavailableError("offline-by-test")),
            )
        monkeypatch.setattr(llm_client, "ILMU_ENABLED", False)
        # Also stub ollama so the fallback chain resolves deterministically.
        monkeypatch.setattr(
            llm_client,
            "_call_ollama",
            AsyncMock(side_effect=llm_client.LLMUnavailableError("offline-by-test")),
        )

    @pytest.mark.asyncio
    async def test_warning_attaches_scan_and_appends_risk(self):
        """When session_history has >=40% empties, both scan and risk surface."""
        history = [None, "", "pass", None, "", "pass"] + [
            "substantive output with content"
        ] * 4  # 6/10 empties
        result = await arif_critique(
            mode="critique",
            target="probe",
            session_history=history,
        )
        assert "behavioral_sink_scan" in result
        scan = result["behavioral_sink_scan"]
        assert scan["status"] == "WARNING"
        assert scan["sink_ratio"] == 0.6
        assert scan["floor"] == "F5"
        # Risk entry appended to risks_found
        risks = result.get("risks_found", [])
        assert isinstance(risks, list)
        assert any(r.get("type") == "anti_calhoun_sink" for r in risks), risks

    @pytest.mark.asyncio
    async def test_clear_attaches_scan_without_risk(self):
        """When CLEAR, scan is attached but no risk entry is added."""
        history = [f"substantive critique output #{i}" for i in range(10)]
        result = await arif_critique(
            mode="critique",
            target="probe",
            session_history=history,
        )
        assert "behavioral_sink_scan" in result
        assert result["behavioral_sink_scan"]["status"] == "CLEAR"
        assert not any(r.get("type") == "anti_calhoun_sink" for r in result.get("risks_found", []))

    @pytest.mark.asyncio
    async def test_no_history_attaches_clear_scan(self):
        """When session_history is omitted, scan still attached (status=CLEAR)."""
        result = await arif_critique(
            mode="critique",
            target="probe",
        )
        assert "behavioral_sink_scan" in result
        assert result["behavioral_sink_scan"]["status"] == "CLEAR"
        assert result["behavioral_sink_scan"]["total_outputs"] == 0

    @pytest.mark.asyncio
    async def test_soft_signal_never_escalates_action_verdict_to_void(self):
        """SOFT signal → SABAR. WARNING must NEVER produce action_risk_verdict=VOID."""
        # Force a heavy sink — every output empty.
        history = [None, "", "pass", "ok", "no-op"] * 4  # 20/20 empties
        result = await arif_critique(
            mode="critique",
            target="probe",
            session_history=history,
        )
        scan = result["behavioral_sink_scan"]
        assert scan["status"] == "WARNING"
        # SOFT signal floor — must NOT promote VOID from anti-calhoun scan alone.
        assert result.get("action_risk_verdict") != "VOID"
        # verdict dict shape is preserved
        verdict = result.get("verdict")
        assert verdict is not None
        assert verdict.get("state") != "VOID"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Schema parity — CRITIQUE_SCHEMA exposes behavioral_sink_scan
# ═══════════════════════════════════════════════════════════════════════════════


class TestCritiqueSchemaParity:
    """Schema must advertise behavioral_sink_scan so downstream MCP clients see it."""

    def test_schema_contains_behavioral_sink_scan(self):
        from arifosmcp.tools.heart import CRITIQUE_SCHEMA

        props = CRITIQUE_SCHEMA.get("properties", {})
        assert "behavioral_sink_scan" in props

    def test_schema_status_enum_clear_warning(self):
        from arifosmcp.tools.heart import CRITIQUE_SCHEMA

        scan_schema = CRITIQUE_SCHEMA["properties"]["behavioral_sink_scan"]
        status_enum = scan_schema["properties"]["status"]["enum"]
        assert status_enum == ["CLEAR", "WARNING"]


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Threshold constant — kept frozen near the helper
# ═══════════════════════════════════════════════════════════════════════════════


class TestThresholdFrozen:
    """The 0.40 threshold is part of the contract — verify it is exposed."""

    def test_threshold_constant_value(self):
        """The threshold is exported as a module-level constant for downstream callers."""
        assert _ANTI_CALHOUN_SINK_THRESHOLD == 0.40

    def test_threshold_source_uses_strict_greater_than(self):
        """Comparison must reference _ANTI_CALHOUN_SINK_THRESHOLD with strict >."""
        import inspect

        from arifosmcp.tools import heart as heart_mod

        src = inspect.getsource(heart_mod._behavioral_sink_scan)
        # The function must reference the named threshold (single source of truth).
        assert "_ANTI_CALHOUN_SINK_THRESHOLD" in src
        # And it must be a strict-greater-than comparison so ratio == 0.40 stays CLEAR.
        assert "sink_ratio > _ANTI_CALHOUN_SINK_THRESHOLD" in src
