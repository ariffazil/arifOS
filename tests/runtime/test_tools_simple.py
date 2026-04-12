"""
tests/runtime/test_tools_simple.py — Simple Runtime Tools Tests

Focused tests for runtime/tools.py to cover the gaps
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock


class TestPublicKernelToolName:
    """Test public constants"""

    def test_public_kernel_tool_name_constant(self):
        """Test the public kernel tool name constant"""
        from arifosmcp.runtime.tools import PUBLIC_KERNEL_TOOL_NAME

        assert PUBLIC_KERNEL_TOOL_NAME == "arifos_kernel"

    def test_legacy_kernel_tool_name_constant(self):
        """Test the legacy kernel tool name constant"""
        from arifosmcp.runtime.tools import LEGACY_KERNEL_TOOL_NAME

        assert LEGACY_KERNEL_TOOL_NAME == "metabolic_loop_router"


class TestStageEnum:
    """Test Stage enum values"""

    def test_stage_values(self):
        """Test stage enum has correct values"""
        from arifosmcp.runtime.tools import Stage

        assert Stage.INIT_000.value == "000_INIT"
        assert Stage.SENSE_111.value == "111_SENSE"
        assert Stage.REALITY_222.value == "222_REALITY"
        assert Stage.MIND_333.value == "333_MIND"
        assert Stage.ROUTER_444.value == "444_ROUTER"
        assert Stage.MEMORY_555.value == "555_MEMORY"
        assert Stage.HEART_666.value == "666_HEART"
        assert Stage.FORGE_777.value == "777_FORGE"
        assert Stage.JUDGE_888.value == "888_JUDGE"
        assert Stage.VAULT_999.value == "999_VAULT"


class TestNormalizeSessionId:
    """Test _normalize_session_id function"""

    def test_normalize_none_generates_uuid(self):
        """Test None generates UUID"""
        from arifosmcp.runtime.tools import _normalize_session_id

        result = _normalize_session_id(None)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_normalize_existing_session(self):
        """Test existing session ID returned"""
        from arifosmcp.runtime.tools import _normalize_session_id

        existing = "test-session-123"
        result = _normalize_session_id(existing)
        assert result == existing


class TestSearchRealityAlias:
    """Test search_reality alias"""

    @pytest.mark.asyncio
    async def test_search_reality_is_alias(self):
        """Test search_reality calls reality_compass with search mode"""
        from arifosmcp.runtime.tools import search_reality

        with patch("arifosmcp.runtime.tools.reality_compass") as mock_compass:
            mock_result = AsyncMock()
            mock_result.tool = "reality_compass"
            mock_compass.return_value = mock_result

            result = await search_reality("test query")

            mock_compass.assert_called_once()
            call_kwargs = mock_compass.call_args.kwargs
            assert call_kwargs.get("mode") == "search"


class TestIngestEvidenceAlias:
    """Test ingest_evidence alias"""

    @pytest.mark.asyncio
    async def test_ingest_evidence_is_alias(self):
        """Test ingest_evidence calls reality_compass with fetch mode"""
        from arifosmcp.runtime.tools import ingest_evidence

        with patch("arifosmcp.runtime.tools.reality_compass") as mock_compass:
            mock_result = AsyncMock()
            mock_result.tool = "reality_compass"
            mock_compass.return_value = mock_result

            result = await ingest_evidence("https://example.com")

            mock_compass.assert_called_once()
            call_kwargs = mock_compass.call_args.kwargs
            assert call_kwargs.get("mode") == "fetch"


class TestCheckVital:
    """Test check_vital tool"""

    @pytest.mark.asyncio
    async def test_check_vital_basic(self):
        """Test check_vital returns envelope"""
        from arifosmcp.runtime.tools import check_vital

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_result.payload = {}
            mock_wrap.return_value = mock_result

            result = await check_vital(session_id="test")

            assert result is not None
            mock_wrap.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_vital_with_thermodynamics(self):
        """Test check_vital includes thermodynamics"""
        from arifosmcp.runtime.tools import check_vital

        with patch("arifosmcp.runtime.tools.get_thermodynamic_report") as mock_thermo:
            mock_thermo.return_value = {"dS": 0.5, "peace2": 0.8}

            with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
                mock_result = AsyncMock()
                mock_result.ok = True
                mock_result.payload = {}
                mock_wrap.return_value = mock_result

                result = await check_vital(session_id="test")

                assert result is not None

    @pytest.mark.asyncio
    async def test_check_vital_thermo_error(self):
        """Test check_vital handles thermodynamics errors"""
        from arifosmcp.runtime.tools import check_vital

        with patch("arifosmcp.runtime.tools.get_thermodynamic_report") as mock_thermo:
            mock_thermo.side_effect = Exception("Thermo error")

            with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
                mock_result = AsyncMock()
                mock_result.ok = True
                mock_result.payload = {}
                mock_wrap.return_value = mock_result

                result = await check_vital(session_id="test")

                # Should handle error gracefully
                assert result is not None


class TestProbeIntelligenceServices:
    """Test _probe_intelligence_services"""

    @pytest.mark.asyncio
    async def test_probe_services_basic(self):
        """Test probing intelligence services"""
        from arifosmcp.runtime.tools import _probe_intelligence_services

        result = await _probe_intelligence_services()

        assert isinstance(result, dict)


class TestAdaptationStatus:
    """Test adaptation functions"""

    def test_check_adaptation_status(self):
        """Test adaptation status returns data"""
        from arifosmcp.runtime.tools import check_adaptation_status

        result = check_adaptation_status()

        assert isinstance(result, dict)

    def test_get_current_hysteresis(self):
        """Test hysteresis calculation"""
        from arifosmcp.runtime.tools import get_current_hysteresis

        result = get_current_hysteresis()

        assert isinstance(result, (dict, float, int))


class TestArifosKernel:
    """Test arifos_kernel"""

    @pytest.mark.asyncio
    async def test_arifos_kernel_basic(self):
        """Test kernel basic execution"""
        from arifosmcp.runtime.tools import arifos_kernel

        with patch("arifosmcp.runtime.tools.metabolic_loop_router") as mock_loop:
            mock_loop.return_value = AsyncMock()
            mock_loop.return_value = {
                "ok": True,
                "tool": "arifos_kernel",
                "session_id": "test",
                "stage": "000_INIT",
                "verdict": "SEAL",
                "status": "SUCCESS",
            }

            result = await arifos_kernel(query="test query")

            assert result is not None

    @pytest.mark.asyncio
    async def test_arifos_kernel_with_dry_run(self):
        """Test kernel with dry_run flag"""
        from arifosmcp.runtime.tools import arifos_kernel

        with patch("arifosmcp.runtime.tools.metabolic_loop_router") as mock_loop:
            mock_loop.return_value = AsyncMock()
            mock_loop.return_value = {
                "ok": True,
                "tool": "arifos_kernel",
                "session_id": "test",
                "stage": "000_INIT",
                "verdict": "SEAL",
                "status": "DRY_RUN",
                "meta": {},
            }

            result = await arifos_kernel(query="test query", dry_run=True)

            assert result is not None

    @pytest.mark.asyncio
    async def test_arifos_kernel_with_debug(self):
        """Test kernel with debug flag"""
        from arifosmcp.runtime.tools import arifos_kernel

        with patch("arifosmcp.runtime.tools.metabolic_loop_router") as mock_loop:
            mock_loop.return_value = AsyncMock()
            mock_loop.return_value = {
                "ok": True,
                "tool": "arifos_kernel",
                "session_id": "test",
                "stage": "000_INIT",
                "verdict": "SEAL",
                "status": "SUCCESS",
                "meta": {},
            }

            result = await arifos_kernel(query="test query", debug=True)

            assert result is not None


class TestForge:
    """Test forge tool"""

    @pytest.mark.asyncio
    async def test_forge_basic(self):
        """Test forge basic execution"""
        from arifosmcp.runtime.tools import forge

        with patch("arifosmcp.runtime.tools.metabolic_loop_router") as mock_loop:
            mock_loop.return_value = AsyncMock()
            mock_loop.return_value = {
                "ok": True,
                "tool": "forge",
                "verdict": "SEAL",
                "status": "SUCCESS",
            }

            result = await forge(spec="test spec")

            assert result is not None

    @pytest.mark.asyncio
    async def test_forge_with_risk_tiers(self):
        """Test forge with different risk tiers"""
        from arifosmcp.runtime.tools import forge

        for risk_tier in ["low", "medium", "high"]:
            with patch("arifosmcp.runtime.tools.metabolic_loop_router") as mock_loop:
                mock_loop.return_value = AsyncMock()
                mock_loop.return_value = {
                    "ok": True,
                    "tool": "forge",
                    "verdict": "SEAL",
                    "status": "SUCCESS",
                }

                result = await forge(spec="test spec", risk_tier=risk_tier)

                assert result is not None


class TestRealityCompass:
    """Test reality_compass"""

    @pytest.mark.asyncio
    async def test_reality_compass_basic(self):
        """Test reality_compass basic"""
        from arifosmcp.runtime.tools import reality_compass

        with patch("arifosmcp.runtime.tools.reality_handler.handle_compass") as mock_handle:
            mock_result = AsyncMock()
            mock_result.status.state = "SUCCESS"
            mock_result.status.verdict = "SEAL"
            mock_result.model_dump.return_value = {"status": {"state": "SUCCESS"}}
            mock_handle.return_value = mock_result

            result = await reality_compass(input="test query", session_id="test")

            assert result is not None

    @pytest.mark.asyncio
    async def test_reality_compass_with_policy(self):
        """Test reality_compass with policy"""
        from arifosmcp.runtime.tools import reality_compass

        with patch("arifosmcp.runtime.tools.reality_handler.handle_compass") as mock_handle:
            mock_result = AsyncMock()
            mock_result.status.state = "SUCCESS"
            mock_result.status.verdict = "SEAL"
            mock_result.model_dump.return_value = {"status": {"state": "SUCCESS"}}
            mock_handle.return_value = mock_result

            result = await reality_compass(
                input="test query", session_id="test", policy={"allow_search": True}
            )

            assert result is not None


class TestInitAnchor:
    """Test init_anchor"""

    @pytest.mark.asyncio
    async def test_init_anchor_basic(self):
        """Test init_anchor basic"""
        from arifosmcp.runtime.tools import init_anchor

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await init_anchor(raw_input="test input", session_id="test")

            assert result is not None


class TestAuditRules:
    """Test audit_rules"""

    @pytest.mark.asyncio
    async def test_audit_rules_basic(self):
        """Test audit_rules returns envelope"""
        from arifosmcp.runtime.tools import audit_rules

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_result.payload = {}
            mock_wrap.return_value = mock_result

            result = await audit_rules(session_id="test")

            assert result is not None


class TestSealVaultCommit:
    """Test seal_vault_commit"""

    @pytest.mark.asyncio
    async def test_seal_vault_basic(self):
        """Test seal_vault_commit basic"""
        from arifosmcp.runtime.tools import seal_vault_commit

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await seal_vault_commit(
                verdict="SEAL", evidence={"test": "data"}, session_id="test"
            )

            assert result is not None


class TestAGIReason:
    """Test agi_reason"""

    @pytest.mark.asyncio
    async def test_agi_reason_basic(self):
        """Test agi_reason basic"""
        from arifosmcp.runtime.tools import agi_reason

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agi_reason(query="test query", session_id="test")

            assert result is not None


class TestAGIReflect:
    """Test agi_reflect"""

    @pytest.mark.asyncio
    async def test_agi_reflect_basic(self):
        """Test agi_reflect basic"""
        from arifosmcp.runtime.tools import agi_reflect

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agi_reflect(topic="test topic", session_id="test")

            assert result is not None


class TestASISimulate:
    """Test asi_simulate"""

    @pytest.mark.asyncio
    async def test_asi_simulate_basic(self):
        """Test asi_simulate basic"""
        from arifosmcp.runtime.tools import asi_simulate

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await asi_simulate(scenario="test scenario", session_id="test")

            assert result is not None


class TestASICritique:
    """Test asi_critique"""

    @pytest.mark.asyncio
    async def test_asi_critique_basic(self):
        """Test asi_critique basic"""
        from arifosmcp.runtime.tools import asi_critique

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await asi_critique(draft_output="test output", session_id="test")

            assert result is not None


class TestApexJudge:
    """Test apex_judge"""

    @pytest.mark.asyncio
    async def test_apex_judge_basic(self):
        """Test apex_judge basic"""
        from arifosmcp.runtime.tools import apex_judge

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await apex_judge(candidate_output="test output", session_id="test")

            assert result is not None


class TestRealityAtlas:
    """Test reality_atlas"""

    @pytest.mark.asyncio
    async def test_reality_atlas_basic(self):
        """Test reality_atlas basic"""
        from arifosmcp.runtime.tools import reality_atlas

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await reality_atlas(operation="merge", session_id="test", bundles=[], query={})

            assert result is not None


class TestVaultSeal:
    """Test vault_seal"""

    @pytest.mark.asyncio
    async def test_vault_seal_basic(self):
        """Test vault_seal basic"""
        from arifosmcp.runtime.tools import vault_seal

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await vault_seal(summary="test summary", session_id="test")

            assert result is not None


class TestVerifyVaultLedger:
    """Test verify_vault_ledger"""

    @pytest.mark.asyncio
    async def test_verify_vault_ledger_basic(self):
        """Test verify_vault_ledger basic"""
        from arifosmcp.runtime.tools import verify_vault_ledger

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await verify_vault_ledger(session_id="test")

            assert result is not None


class TestAgentzeroTools:
    """Test agentzero tool wrappers"""

    @pytest.mark.asyncio
    async def test_agentzero_validate_basic(self):
        """Test agentzero_validate basic"""
        from arifosmcp.runtime.tools import agentzero_validate

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agentzero_validate(
                input_to_validate="test input", validation_type="plan", session_id="test"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_agentzero_armor_scan_basic(self):
        """Test agentzero_armor_scan basic"""
        from arifosmcp.runtime.tools import agentzero_armor_scan

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agentzero_armor_scan(content="test content", session_id="test")

            assert result is not None

    @pytest.mark.asyncio
    async def test_agentzero_hold_check_basic(self):
        """Test agentzero_hold_check basic"""
        from arifosmcp.runtime.tools import agentzero_hold_check

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agentzero_hold_check(session_id="test")

            assert result is not None

    @pytest.mark.asyncio
    async def test_agentzero_engineer_basic(self):
        """Test agentzero_engineer basic"""
        from arifosmcp.runtime.tools import agentzero_engineer

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agentzero_engineer(
                task="test task", action_type="execute_code", session_id="test"
            )

            assert result is not None

    @pytest.mark.asyncio
    async def test_agentzero_memory_query_basic(self):
        """Test agentzero_memory_query basic"""
        from arifosmcp.runtime.tools import agentzero_memory_query

        with patch("arifosmcp.runtime.tools._wrap_call") as mock_wrap:
            mock_result = AsyncMock()
            mock_result.ok = True
            mock_wrap.return_value = mock_result

            result = await agentzero_memory_query(query="test query", session_id="test")

            assert result is not None


class TestPublicToolSpecs:
    """Test public tool specs"""

    def test_public_tool_specs_available(self):
        """Test public_tool_specs is available"""
        from arifosmcp.runtime.tools import public_tool_specs

        assert public_tool_specs is not None
        assert isinstance(public_tool_specs, list)

    def test_public_tool_names_available(self):
        """Test public_tool_names is available"""
        from arifosmcp.runtime.tools import public_tool_names

        assert public_tool_names is not None
        assert isinstance(public_tool_names, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
