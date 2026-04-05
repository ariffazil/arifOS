"""
tests/core/kernel/test_stage_orchestrator.py

888_JUDGE FORGE: Test coverage for core/kernel/stage_orchestrator.py
Target: 80%+ coverage of 199 lines

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.kernel.stage_orchestrator import (
    _as_dict,
    _build_asi_output,
    _collect_floor_failures_from_scores,
    _collect_floor_failures_from_violations,
    _default_get_stage_result,
    _default_store_stage_result,
    _extract_query_from_stage_inputs,
    _get_first_stage_result,
    _store_stage_with_aliases,
    run_metabolic_pipeline,
    run_stage_444_trinity_sync,
    run_stage_555_empathy,
    run_stage_666_align,
    run_stage_777_forge,
    run_stage_888_judge,
    run_stage_999_seal,
)


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestDefaultFunctions:
    """Test default helper functions."""

    def test_default_get_stage_result(self):
        """Test default getter returns empty dict."""
        assert _default_get_stage_result("session", "stage") == {}

    def test_default_store_stage_result(self):
        """Test default setter returns None."""
        assert _default_store_stage_result("session", "stage", {}) is None


class TestGetFirstStageResult:
    """Test _get_first_stage_result function."""

    def test_returns_first_non_empty_result(self):
        """Test returns first non-empty result from stage names."""
        def mock_get(session_id, stage):
            if stage == "stage_b":
                return {"data": "found"}
            return {}
        
        result = _get_first_stage_result(mock_get, "session", "stage_a", "stage_b", "stage_c")
        assert result == {"data": "found"}

    def test_returns_empty_if_all_empty(self):
        """Test returns empty dict if all stages empty."""
        def mock_get(session_id, stage):
            return {}
        
        result = _get_first_stage_result(mock_get, "session", "stage_a", "stage_b")
        assert result == {}

    def test_returns_first_immediately(self):
        """Test returns first result without checking others."""
        call_count = 0
        def mock_get(session_id, stage):
            nonlocal call_count
            call_count += 1
            if stage == "stage_a":
                return {"first": True}
            return {"other": True}
        
        result = _get_first_stage_result(mock_get, "session", "stage_a", "stage_b")
        assert result == {"first": True}
        assert call_count == 1  # Should not check stage_b


class TestStoreStageWithAliases:
    """Test _store_stage_with_aliases function."""

    def test_stores_to_all_aliases(self):
        """Test stores result to all stage name aliases."""
        stored = []
        def mock_store(session_id, stage, payload):
            stored.append((session_id, stage, payload))
        
        result = {"data": "test"}
        _store_stage_with_aliases(mock_store, "session-123", result, "alias_a", "alias_b")
        
        assert len(stored) == 2
        assert stored[0] == ("session-123", "alias_a", result)
        assert stored[1] == ("session-123", "alias_b", result)


class TestAsDict:
    """Test _as_dict function."""

    def test_dict_input(self):
        """Test dict input returns unchanged."""
        data = {"key": "value"}
        assert _as_dict(data) == data

    def test_pydantic_model(self):
        """Test Pydantic model conversion."""
        mock_model = MagicMock()
        mock_model.model_dump.return_value = {"field": "value"}
        assert _as_dict(mock_model) == {"field": "value"}

    def test_dict_method(self):
        """Test object with dict() method."""
        class MockObj:
            def dict(self):
                return {"data": "test"}
        assert _as_dict(MockObj()) == {"data": "test"}

    def test_plain_object(self):
        """Test plain object returns empty dict."""
        assert _as_dict("string") == {}
        assert _as_dict(123) == {}


class TestExtractQueryFromStageInputs:
    """Test _extract_query_from_stage_inputs function."""

    def test_extracts_from_agi_first(self):
        """Test extracts query from AGI result first."""
        agi = {"query": "agi query"}
        asi = {"query": "asi query"}
        result = _extract_query_from_stage_inputs(agi, asi, "test_stage")
        assert result == "agi query"

    def test_falls_back_to_asi(self):
        """Test falls back to ASI if AGI empty."""
        agi = {}
        asi = {"query": "asi query"}
        result = _extract_query_from_stage_inputs(agi, asi, "test_stage")
        assert result == "asi query"

    def test_raises_if_both_empty(self):
        """Test raises ValueError if both empty."""
        with pytest.raises(ValueError, match="Missing query for stage test_stage"):
            _extract_query_from_stage_inputs({}, {}, "test_stage")


class TestBuildAsiOutput:
    """Test _build_asi_output function."""

    def test_builds_complete_output(self):
        """Test builds ASI output from result."""
        asi_result = {
            "kappa_r": 0.85,
            "peace_squared": 0.95,
            "is_reversible": False,
            "verdict": "HOLD",
        }
        result = _build_asi_output(asi_result)
        assert result["kappa_r"] == 0.85
        assert result["peace_squared"] == 0.95
        assert result["is_reversible"] is False
        assert result["verdict"] == "HOLD"

    def test_uses_defaults_for_missing(self):
        """Test uses defaults for missing fields."""
        asi_result = {}
        result = _build_asi_output(asi_result)
        assert result["kappa_r"] == 0.7  # Default
        assert result["peace_squared"] == 1.0  # Default
        assert result["is_reversible"] is True  # Default
        assert result["verdict"] == "SEAL"  # Default

    def test_uses_empathy_kappa_r_fallback(self):
        """Test uses empathy_kappa_r if kappa_r missing."""
        asi_result = {"empathy_kappa_r": 0.9}
        result = _build_asi_output(asi_result)
        assert result["kappa_r"] == 0.9


class TestCollectFloorFailures:
    """Test floor failure collection functions."""

    def test_collect_from_scores(self):
        """Test collecting failures from floor scores."""
        floor_scores = {
            "f1_amanah": 0.3,  # Below threshold
            "f5_peace": 0.8,   # Above threshold
            "f6_empathy": 0.4, # Below threshold
            "f9_anti_hantu": 0.9,  # Above threshold
        }
        failed = _collect_floor_failures_from_scores(floor_scores, threshold=0.5)
        assert "F1" in failed
        assert "F6" in failed
        assert "F5" not in failed
        assert "F9" not in failed

    def test_collect_from_scores_ignores_unknown(self):
        """Test ignores unknown floor keys."""
        floor_scores = {"unknown_floor": 0.1, "f1_amanah": 0.9}
        failed = _collect_floor_failures_from_scores(floor_scores)
        assert "F1" not in failed  # Passed (0.9 >= 0.5)
        assert len(failed) == 0

    def test_collect_from_violations(self):
        """Test collecting failures from violation strings."""
        violations = ["F1_breach: some issue", "F5_warning: peace low", "random text"]
        failed = _collect_floor_failures_from_violations(violations)
        assert "F1" in failed
        assert "F5" in failed
        assert "F6" not in failed

    def test_collect_no_duplicates(self):
        """Test no duplicate floor IDs."""
        violations = ["F1_issue1", "F1_issue2", "F1_issue3"]
        failed = _collect_floor_failures_from_violations(violations)
        assert failed == ["F1"]  # Only one F1


# =============================================================================
# STAGE RUNNER TESTS
# =============================================================================

class TestStage444TrinitySync:
    """Test run_stage_444_trinity_sync function."""

    @pytest.mark.asyncio
    async def test_successful_sync(self):
        """Test successful trinity sync."""
        mock_sync_out = MagicMock()
        mock_sync_out.verdict.value = "SEAL"
        mock_sync_out.floor_scores.f3_tri_witness = 0.96
        
        stored_results = []
        def mock_store(sid, stage, payload):
            stored_results.append((stage, payload))
        
        with patch("core.kernel.stage_orchestrator.core_organs.sync", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = mock_sync_out
            result = await run_stage_444_trinity_sync(
                session_id="test-session",
                agi_result={"query": "test"},
                asi_result={"query": "test"},
                store_stage_result_fn=mock_store,
            )
        
        assert result["stage"] == "444"
        assert result["pre_verdict"] == "SEAL"
        assert result["consensus_score"] == 0.96
        assert result["status"] == "completed"
        assert any(s[0] == "stage_444" for s in stored_results)

    @pytest.mark.asyncio
    async def test_sync_failure(self):
        """Test sync with core organs failure."""
        with patch("core.kernel.stage_orchestrator.core_organs.sync", new_callable=AsyncMock) as mock_sync:
            mock_sync.side_effect = Exception("Sync failed")
            result = await run_stage_444_trinity_sync(
                session_id="test-session",
                agi_result={"query": "test"},
                asi_result={"query": "test"},
            )
        
        assert result["stage"] == "444"
        assert result["pre_verdict"] == "VOID"
        assert result["status"] == "failed"
        assert "error" in result


class TestStage555Empathy:
    """Test run_stage_555_empathy function."""

    @pytest.mark.asyncio
    async def test_successful_empathy(self):
        """Test successful empathy stage."""
        # Use dict-like mock to work with _as_dict
        mock_emp_out = {
            "floor_scores": {"f6_empathy": 0.88},
            "assessment": {"stakeholders": [{"role": "user", "impact": "positive"}]},
            "verdict": "SEAL",
        }
        
        log_calls = []
        async def mock_log(**kwargs):
            log_calls.append(kwargs)
        
        with patch("core.kernel.stage_orchestrator.core_organs.empathize", new_callable=AsyncMock) as mock_emp:
            mock_emp.return_value = mock_emp_out
            result = await run_stage_555_empathy(
                session_id="test-session",
                query="help users",
                log_asi_decision_fn=mock_log,
            )
        
        assert result["stage"] == "555"
        assert result["empathy_kappa_r"] == 0.88
        assert result["verdict"] == "SEAL"
        assert len(result["stakeholders"]) == 1

    @pytest.mark.asyncio
    async def test_empathy_failure(self):
        """Test empathy stage failure."""
        with patch("core.kernel.stage_orchestrator.core_organs.empathize", new_callable=AsyncMock) as mock_emp:
            mock_emp.side_effect = Exception("Empathy failed")
            result = await run_stage_555_empathy(
                session_id="test-session",
                query="test",
            )
        
        assert result["stage"] == "555"
        assert result["verdict"] == "VOID"
        assert result["status"] == "failed"


class TestStage666Align:
    """Test run_stage_666_align function."""

    @pytest.mark.asyncio
    async def test_successful_align(self):
        """Test successful align stage."""
        mock_align_out = {
            "floor_scores": {"f6_empathy": 0.9, "f5_peace": 0.95},
            "verdict": "SEAL",
            "violations": [],
        }
        
        stored_results = []
        def mock_store(sid, stage, payload):
            stored_results.append((stage, payload))
        
        with patch("core.kernel.stage_orchestrator.core_organs.align", new_callable=AsyncMock) as mock_align:
            mock_align.return_value = mock_align_out
            result = await run_stage_666_align(
                session_id="test-session",
                query="test query",
                store_stage_result_fn=mock_store,
            )
        
        assert result["stage"] == "666"
        assert result["verdict"] == "SEAL"
        assert "omega_bundle" in result
        assert any(s[0] == "stage_666" for s in stored_results)


class TestStage777Forge:
    """Test run_stage_777_forge function."""

    @pytest.mark.asyncio
    async def test_successful_forge(self):
        """Test successful forge stage."""
        mock_forge_out = MagicMock()
        mock_forge_out.synthesis = "test synthesis"
        
        stored_results = []
        def mock_store(sid, stage, payload):
            stored_results.append((stage, payload))
        
        with patch("core.kernel.stage_orchestrator.core_organs.forge", new_callable=AsyncMock) as mock_forge:
            mock_forge.return_value = mock_forge_out
            result = await run_stage_777_forge(
                session_id="test-session",
                agi_result={"query": "test"},
                asi_result={"query": "test"},
                store_stage_result_fn=mock_store,
            )
        
        assert result["stage"] == "777"
        assert result["status"] == "completed"
        assert "forge_result" in result
        assert any(s[0] == "stage_777" for s in stored_results)

    @pytest.mark.asyncio
    async def test_forge_failure(self):
        """Test forge stage failure."""
        with patch("core.kernel.stage_orchestrator.core_organs.forge", new_callable=AsyncMock) as mock_forge:
            mock_forge.side_effect = Exception("Forge failed")
            result = await run_stage_777_forge(
                session_id="test-session",
                agi_result={"query": "test"},
                asi_result={"query": "test"},
            )
        
        assert result["stage"] == "777"
        assert result["status"] == "failed"
        assert "error" in result


class TestStage888Judge:
    """Test run_stage_888_judge function."""

    @pytest.mark.asyncio
    async def test_judge_seal(self):
        """Test judge returns SEAL when both inputs SEAL."""
        mock_judge_out = {"verdict": "SEAL"}
        
        with patch("core.kernel.stage_orchestrator.core_organs.judge", new_callable=AsyncMock) as mock_judge:
            mock_judge.return_value = mock_judge_out
            result = await run_stage_888_judge(
                session_id="test-session",
                agi_result={"verdict": "SEAL"},
                asi_result={"verdict": "SEAL"},
            )
        
        assert result["stage"] == "888"
        assert result["verdict"] == "SEAL"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_judge_void_priority(self):
        """Test judge returns VOID if either input is VOID."""
        mock_judge_out = {"verdict": "VOID"}
        
        with patch("core.kernel.stage_orchestrator.core_organs.judge", new_callable=AsyncMock) as mock_judge:
            mock_judge.return_value = mock_judge_out
            result = await run_stage_888_judge(
                session_id="test-session",
                agi_result={"verdict": "SEAL"},
                asi_result={"verdict": "VOID"},  # One VOID should trigger VOID
            )
        
        # The candidate should be VOID before calling judge
        assert result["verdict"] == "VOID"

    @pytest.mark.asyncio
    async def test_judge_hold_priority(self):
        """Test judge returns HOLD if one input is HOLD (no VOID)."""
        mock_judge_out = {"verdict": "HOLD_888"}
        
        with patch("core.kernel.stage_orchestrator.core_organs.judge", new_callable=AsyncMock) as mock_judge:
            mock_judge.return_value = mock_judge_out
            result = await run_stage_888_judge(
                session_id="test-session",
                agi_result={"verdict": "HOLD"},
                asi_result={"verdict": "SEAL"},
            )
        
        assert result["stage"] == "888"
        assert result["verdict"] == "HOLD_888"


class TestStage999Seal:
    """Test run_stage_999_seal function."""

    @pytest.mark.asyncio
    async def test_successful_seal(self):
        """Test successful seal stage."""
        mock_receipt = {"status": "SUCCESS", "hash": "0xabc123"}
        
        with patch("core.kernel.stage_orchestrator.core_organs.seal", new_callable=AsyncMock) as mock_seal:
            mock_seal.return_value = mock_receipt
            result = await run_stage_999_seal(
                session_id="test-session",
                judge_result={"verdict": "SEAL"},
                agi_result={"query": "test summary"},
            )
        
        assert result["stage"] == "999"
        assert result["status"] == "SUCCESS"
        assert "hash" in result

    @pytest.mark.asyncio
    async def test_seal_failure(self):
        """Test seal stage failure."""
        with patch("core.kernel.stage_orchestrator.core_organs.seal", new_callable=AsyncMock) as mock_seal:
            mock_seal.side_effect = Exception("Seal failed")
            result = await run_stage_999_seal(
                session_id="test-session",
                judge_result={"verdict": "SEAL"},
            )
        
        assert result["stage"] == "999"
        assert result["status"] == "VOID"
        assert result["error"] == "Seal failed"


# =============================================================================
# FULL PIPELINE TEST
# =============================================================================

class TestMetabolicPipeline:
    """Test run_metabolic_pipeline function."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test running full 444-999 pipeline."""
        stored_stages = {}
        def mock_store(sid, stage, payload):
            stored_stages[stage] = payload
        
        def mock_get(sid, stage):
            return stored_stages.get(stage, {})
        
        with patch("core.kernel.stage_orchestrator.core_organs.sync", new_callable=AsyncMock) as mock_sync, \
             patch("core.kernel.stage_orchestrator.core_organs.empathize", new_callable=AsyncMock) as mock_emp, \
             patch("core.kernel.stage_orchestrator.core_organs.align", new_callable=AsyncMock) as mock_align, \
             patch("core.kernel.stage_orchestrator.core_organs.forge", new_callable=AsyncMock) as mock_forge, \
             patch("core.kernel.stage_orchestrator.core_organs.judge", new_callable=AsyncMock) as mock_judge, \
             patch("core.kernel.stage_orchestrator.core_organs.seal", new_callable=AsyncMock) as mock_seal:
            
            # Setup mocks with dict-like returns
            mock_sync.return_value = {"verdict": "SEAL", "floor_scores": {"f3_tri_witness": 0.95}}
            mock_emp.return_value = {"floor_scores": {"f6_empathy": 0.9}, "assessment": {"stakeholders": []}, "verdict": "SEAL"}
            mock_align.return_value = {"floor_scores": {"f6_empathy": 0.9}, "verdict": "SEAL", "violations": []}
            mock_forge.return_value = {"synthesis": "test"}
            mock_judge.return_value = {"verdict": "SEAL"}
            mock_seal.return_value = {"status": "SUCCESS", "hash": "0xabc"}
            
            result = await run_metabolic_pipeline(
                session_id="pipeline-test",
                query="test query",
                get_stage_result_fn=mock_get,
                store_stage_result_fn=mock_store,
            )
        
        assert result["session_id"] == "pipeline-test"
        assert "stages" in result
        assert all(stage in result["stages"] for stage in ["444", "555", "666", "777", "888", "999"])
        assert result["final_verdict"] == "SEAL"

    @pytest.mark.asyncio
    async def test_pipeline_skips_already_run(self):
        """Test pipeline skips stages already in store."""
        stored_stages = {"stage_555": {"stage": "555", "status": "completed"}}
        def mock_store(sid, stage, payload):
            stored_stages[stage] = payload
        
        def mock_get(sid, stage):
            return stored_stages.get(stage, {})
        
        emp_calls = []
        with patch("core.kernel.stage_orchestrator.core_organs.sync", new_callable=AsyncMock) as mock_sync, \
             patch("core.kernel.stage_orchestrator.core_organs.empathize", new_callable=AsyncMock) as mock_emp, \
             patch("core.kernel.stage_orchestrator.core_organs.align", new_callable=AsyncMock), \
             patch("core.kernel.stage_orchestrator.core_organs.forge", new_callable=AsyncMock), \
             patch("core.kernel.stage_orchestrator.core_organs.judge", new_callable=AsyncMock), \
             patch("core.kernel.stage_orchestrator.core_organs.seal", new_callable=AsyncMock):
            
            mock_sync.return_value = MagicMock(verdict=MagicMock(value="SEAL"), floor_scores=MagicMock(f3_tri_witness=0.95))
            mock_emp.side_effect = lambda **kwargs: emp_calls.append(kwargs) or MagicMock()
            
            await run_metabolic_pipeline(
                session_id="pipeline-test",
                query="test query",
                get_stage_result_fn=mock_get,
                store_stage_result_fn=mock_store,
            )
        
        # Empathy should not be called because stage_555 already exists
        assert len(emp_calls) == 0
