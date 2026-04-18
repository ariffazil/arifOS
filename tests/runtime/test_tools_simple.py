"""
tests/runtime/test_tools_simple.py — Simple Runtime Tools Tests

Focused tests for runtime/tools.py covering the 11 canonical tools
and legacy aliases.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock


def _mock_envelope(tool: str, ok: bool = True, stage: str = "000_INIT"):
    from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus
    from core.shared.types import Verdict
    return RuntimeEnvelope(
        ok=ok,
        tool=tool,
        stage=stage,
        status=RuntimeStatus.SUCCESS if ok else RuntimeStatus.HOLD,
        verdict=Verdict.SEAL if ok else Verdict.SABAR,
        payload={},
    )


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


class TestArifosInit:
    """Test arifos_init"""

    @pytest.mark.asyncio
    async def test_arifos_init_basic(self):
        """Test arifos_init returns envelope"""
        from arifosmcp.runtime.tools import arifos_init

        with patch("arifosmcp.runtime.tools._mega_init_anchor") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_init", stage="000_INIT")

            result = await arifos_init(actor_id="test", intent="test")

            assert result is not None
            mock_mega.assert_called_once()

    @pytest.mark.asyncio
    async def test_canonical_init_handler_accepts_public_signature(self):
        """Canonical MCP handler should point at the public init wrapper."""
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        handler = CANONICAL_TOOL_HANDLERS["arifos_init"]

        with patch("arifosmcp.runtime.tools._mega_init_anchor", new_callable=AsyncMock) as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_init", stage="000_INIT")

            result = await handler(actor_id="test", intent="test", risk_tier="medium")

            assert result is not None
            mock_mega.assert_awaited_once()


class TestArifosSense:
    """Test arifos_sense"""

    @pytest.mark.asyncio
    async def test_arifos_sense_basic(self):
        """Test arifos_sense basic (falls back to legacy on governed failure)"""
        from arifosmcp.runtime.tools import arifos_sense

        with patch("arifosmcp.runtime.tools._sense_legacy") as mock_legacy:
            mock_legacy.return_value = _mock_envelope("arifos_sense", stage="111_SENSE")

            result = await arifos_sense(query="test query")

            assert result is not None
            # governed mode may succeed or fall back; either way result is valid

    @pytest.mark.asyncio
    async def test_canonical_sense_handler_accepts_public_signature(self):
        """Canonical MCP handler should accept the public sense signature."""
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        handler = CANONICAL_TOOL_HANDLERS["arifos_sense"]

        result = await handler(query="test query", platform="api")

        assert result is not None
        assert result.tool == "arifos_sense"

    @pytest.mark.asyncio
    async def test_arifos_sense_attaches_domain_evidence_to_legacy_envelope(self):
        from arifosmcp.runtime.tools import arifos_sense

        with patch("arifosmcp.runtime.tools._sense_legacy") as mock_legacy:
            mock_legacy.return_value = _mock_envelope("arifos_sense", stage="111_SENSE")

            result = await arifos_sense(
                query="test query",
                mode="search",
                domain_evidence={"claim_tag": "GEOX.CLAIM", "disagreement_band": 0.12},
            )

            _, kwargs = mock_legacy.call_args
            assert kwargs["domain_evidence"]["claim_tag"] == "GEOX.CLAIM"
            assert result.tool == "arifos_sense"


class TestArifosMind:
    """Test arifos_mind"""

    @pytest.mark.asyncio
    async def test_arifos_mind_basic(self):
        """Test arifos_mind basic"""
        from arifosmcp.runtime.tools import arifos_mind

        with patch("arifosmcp.runtime.tools._mega_agi_mind") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_mind", stage="333_MIND")

            result = await arifos_mind(query="test query")

            assert result is not None
            mock_mega.assert_called_once()

    @pytest.mark.asyncio
    async def test_arifos_mind_reflect_mode(self):
        """Test arifos_mind with reflect mode"""
        from arifosmcp.runtime.tools import arifos_mind

        with patch("arifosmcp.runtime.tools._mega_agi_mind") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_mind", stage="333_MIND")

            result = await arifos_mind(query="test", mode="reflect")

            assert result is not None
            mock_mega.assert_called_once()

    @pytest.mark.asyncio
    async def test_arifos_mind_public_normalizes_context_without_nameerror(self):
        """Public arifos_mind wrapper should normalize context before session gating."""
        from arifosmcp.runtime.tools import _arifos_mind_public

        result = await _arifos_mind_public(query="test", context={"evidence": [1, 2, 3]})

        assert result is not None
        assert result.tool == "arifos_mind"
        assert result.ok is False


class TestArifosKernel:
    """Test arifos_kernel"""

    @pytest.mark.asyncio
    async def test_arifos_kernel_basic(self):
        """Test kernel basic execution"""
        from arifosmcp.runtime.tools import arifos_kernel

        with patch("arifosmcp.runtime.tools._mega_arifos_kernel") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_kernel", stage="444_ROUTER")

            result = await arifos_kernel(request="test request")

            assert result is not None
            mock_mega.assert_called_once()


class TestArifosHeart:
    """Test arifos_heart"""

    @pytest.mark.asyncio
    async def test_arifos_heart_basic(self):
        """Test arifos_heart basic"""
        from arifosmcp.runtime.tools import arifos_heart

        with patch("arifosmcp.runtime.tools._mega_asi_heart") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_heart", stage="666_HEART")

            result = await arifos_heart(content="test content")

            assert result is not None
            mock_mega.assert_called_once()


class TestArifosOps:
    """Test arifos_ops"""

    @pytest.mark.asyncio
    async def test_arifos_ops_basic(self):
        """Test arifos_ops basic"""
        from arifosmcp.runtime.tools import arifos_ops

        with patch("arifosmcp.runtime.tools._mega_math_estimator") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_ops", stage="777_OPS")

            result = await arifos_ops(action="test")

            assert result is not None
            mock_mega.assert_called_once()


class TestArifosJudge:
    """Test arifos_judge"""

    @pytest.mark.asyncio
    async def test_arifos_judge_basic(self):
        """Test arifos_judge basic"""
        from arifosmcp.runtime.tools import arifos_judge

        with patch("arifosmcp.runtime.tools._mega_apex_judge") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_judge", stage="888_JUDGE")

            result = await arifos_judge(candidate_action="test action")

            assert result is not None
            mock_mega.assert_called_once()

    @pytest.mark.asyncio
    async def test_canonical_judge_handler_accepts_public_query_signature(self):
        """Canonical MCP handler should point at the public query-compatible wrapper."""
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS

        handler = CANONICAL_TOOL_HANDLERS["arifos_judge"]

        with patch("arifosmcp.runtime.tools._mega_apex_judge", new_callable=AsyncMock) as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_judge", stage="888_JUDGE")

            result = await handler(query="test action", risk_tier="medium")

            assert result is not None
            mock_mega.assert_awaited_once()
            _, kwargs = mock_mega.await_args
            assert kwargs["mode"] == "judge"
            assert kwargs["payload"]["verdict_candidate"] == "SEAL"
            assert kwargs["payload"]["reason_summary"] == "test action"

    @pytest.mark.asyncio
    async def test_arifos_judge_forwards_domain_evidence(self):
        from arifosmcp.runtime.tools import arifos_judge

        with patch("arifosmcp.runtime.tools._mega_apex_judge", new_callable=AsyncMock) as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_judge", stage="888_JUDGE")

            result = await arifos_judge(
                risk_tier="medium",
                domain_evidence={"claim_tag": "GEOX.SEAL", "p10_p50_p90": {"p50": 12.0}},
            )

            _, kwargs = mock_mega.await_args
            assert kwargs["payload"]["domain_evidence"]["claim_tag"] == "GEOX.SEAL"
            assert result.payload["domain_evidence"]["claim_tag"] == "GEOX.SEAL"


class TestArifosMemory:
    """Test arifos_memory"""

    @pytest.mark.asyncio
    async def test_arifos_memory_basic(self):
        """Test arifos_memory basic"""
        from arifosmcp.runtime.tools import arifos_memory

        with patch("arifosmcp.runtime.tools._mega_engineering_memory") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_memory", stage="555_MEMORY")

            result = await arifos_memory(query="test query")

            assert result is not None
            mock_mega.assert_called_once()

    @pytest.mark.asyncio
    async def test_arifos_memory_asset_store_maps_to_vector_store(self):
        from arifosmcp.runtime.tools import arifos_memory

        with patch("arifosmcp.runtime.tools._mega_engineering_memory") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_memory", stage="555_MEMORY")

            result = await arifos_memory(
                mode="asset_store",
                asset_id="asset-001",
                content="stored payload",
                domain_evidence={"claim_tag": "GEOX.ASSET"},
            )

            _, kwargs = mock_mega.call_args
            assert kwargs["mode"] == "vector_store"
            assert result.payload["domain_evidence"]["claim_tag"] == "GEOX.ASSET"


class TestArifosVault:
    """Test arifos_vault"""

    @pytest.mark.asyncio
    async def test_arifos_vault_basic(self):
        """Test arifos_vault basic"""
        from arifosmcp.runtime.tools import arifos_vault

        with patch("arifosmcp.runtime.tools._mega_vault_ledger") as mock_mega:
            mock_mega.return_value = _mock_envelope("arifos_vault", stage="999_VAULT")

            result = await arifos_vault(verdict="SEAL")

            assert result is not None
            mock_mega.assert_called_once()


class TestArifosGateway:
    """Test arifos_gateway"""

    @pytest.mark.asyncio
    async def test_arifos_gateway_basic(self):
        """Test arifos_gateway basic"""
        from arifosmcp.runtime.tools import arifos_gateway

        result = await arifos_gateway(session_id="test-session")

        assert result is not None
        assert result.ok is True

    @pytest.mark.asyncio
    async def test_arifos_gateway_guard_mode(self):
        """Test arifos_gateway guard mode"""
        from arifosmcp.runtime.tools import arifos_gateway

        result = await arifos_gateway(session_id="test-session", mode="guard")

        assert result is not None
        assert result.ok is True

    @pytest.mark.asyncio
    async def test_arifos_gateway_audit_mode(self):
        """Test arifos_gateway audit mode"""
        from arifosmcp.runtime.tools import arifos_gateway

        result = await arifos_gateway(session_id="test-session", mode="audit")

        assert result is not None
        assert result.ok is True


class TestLegacyAliases:
    """Test legacy aliases still dispatch"""

    @pytest.mark.asyncio
    async def test_init_anchor_alias(self):
        """Test init_anchor alias dispatches to arifos_init"""
        from arifosmcp.runtime.tools import init_anchor

        with patch("arifosmcp.runtime.tools.arifos_init") as mock_init:
            mock_init.return_value = AsyncMock()
            result = await init_anchor(raw_input="test")
            mock_init.assert_called_once()

    @pytest.mark.asyncio
    async def test_audit_rules_alias(self):
        """Test audit_rules returns a valid envelope"""
        from arifosmcp.runtime.tools import audit_rules

        result = await audit_rules(session_id="test")
        assert result is not None
        assert result.ok is True

    @pytest.mark.asyncio
    async def test_verify_vault_ledger_alias(self):
        """Test verify_vault_ledger returns a valid envelope"""
        from arifosmcp.runtime.tools import verify_vault_ledger

        result = await verify_vault_ledger(session_id="test")
        assert result is not None
        assert result.ok is True

    @pytest.mark.asyncio
    async def test_seal_vault_commit_alias(self):
        """Test seal_vault_commit returns a valid envelope"""
        from arifosmcp.runtime.tools import seal_vault_commit

        result = await seal_vault_commit(session_id="test")
        assert result is not None
        assert result.ok is True


class TestToolDispatch:
    """Test tool handler lookup and normalization"""

    def test_get_tool_handler_canonical(self):
        """Test get_tool_handler finds canonical tools"""
        from arifosmcp.runtime.tools import get_tool_handler, CANONICAL_TOOL_HANDLERS

        for name in CANONICAL_TOOL_HANDLERS:
            handler = get_tool_handler(name)
            assert handler is not None, f"{name} should have a handler"

    def test_get_tool_handler_legacy_alias(self):
        """Test get_tool_handler resolves legacy aliases"""
        from arifosmcp.runtime.tools import get_tool_handler

        handler = get_tool_handler("init_anchor")
        assert handler is not None

        handler = get_tool_handler("arifos.init")
        assert handler is not None

    def test_get_tool_handler_unknown(self):
        """Test get_tool_handler returns None for unknown"""
        from arifosmcp.runtime.tools import get_tool_handler

        handler = get_tool_handler("totally_unknown_tool")
        assert handler is None

    def test_normalize_tool_name_canonical(self):
        """Test normalize_tool_name on canonical names"""
        from arifosmcp.runtime.tools import normalize_tool_name

        assert normalize_tool_name("arifos_init") == "arifos_init"
        assert normalize_tool_name("arifos_sense") == "arifos_sense"

    def test_normalize_tool_name_legacy(self):
        """Test normalize_tool_name resolves legacy aliases"""
        from arifosmcp.runtime.tools import normalize_tool_name

        assert normalize_tool_name("init_anchor") == "arifos_init"
        assert normalize_tool_name("arifos.init") == "arifos_init"
        assert normalize_tool_name("apex_soul") == "arifos_judge"


class TestPublicRegistryImports:
    """Test public registry exports"""

    def test_public_tool_specs_available(self):
        """Test public_tool_specs is available in public_registry"""
        from arifosmcp.runtime.public_registry import public_tool_specs

        assert public_tool_specs is not None
        assert isinstance(public_tool_specs(), tuple)

    def test_public_tool_names_available(self):
        """Test public_tool_names is available in public_registry"""
        from arifosmcp.runtime.public_registry import public_tool_names

        assert public_tool_names is not None
        assert isinstance(public_tool_names(), tuple)

    def test_public_tool_count_is_11(self):
        """Test public registry has exactly 11 tools"""
        from arifosmcp.runtime.public_registry import public_tool_names, EXPECTED_TOOL_COUNT

        names = public_tool_names()
        assert len(names) == EXPECTED_TOOL_COUNT


class TestRegisterV2Tools:
    """Test register_v2_tools"""

    def test_register_v2_tools_returns_list(self):
        """Test register_v2_tools returns a list of registered names"""
        from arifosmcp.runtime.tools import register_v2_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        registered = register_v2_tools(mcp)

        assert isinstance(registered, list)
        assert len(registered) >= 11

    def test_register_v2_tools_includes_canonical(self):
        """Test register_v2_tools includes the 11 canonical tools"""
        from arifosmcp.runtime.tools import register_v2_tools
        from arifosmcp.runtime.public_registry import public_tool_names
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        registered = register_v2_tools(mcp)

        public_names = set(public_tool_names())
        assert public_names.issubset(set(registered)), "Missing canonical tools in registration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
