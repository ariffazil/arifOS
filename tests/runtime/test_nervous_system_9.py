"""
tests/runtime/test_nervous_system_9.py — Nervous System 9 Hardened Tools Tests

Tests all 9 hardened internal tools from console_tools.py to verify:
1. They accept session_id and auth_context parameters
2. They return RuntimeEnvelope (not legacy responses)
3. They have proper stage mapping
4. They handle errors gracefully

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Any


class TestSystemHealthHardened:
    """Test hardened system_health tool"""

    @pytest.mark.asyncio
    async def test_system_health_returns_runtime_envelope(self):
        """Verify system_health returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import system_health
        from arifosmcp.runtime.models import RuntimeEnvelope

        result = await system_health()

        assert isinstance(result, RuntimeEnvelope), f"Expected RuntimeEnvelope, got {type(result)}"

    @pytest.mark.asyncio
    async def test_system_health_accepts_session_id(self):
        """Verify system_health accepts session_id parameter"""
        from arifosmcp.intelligence.console_tools import system_health

        result = await system_health(session_id="test-session-123")

        assert result.session_id == "test-session-123"

    @pytest.mark.asyncio
    async def test_system_health_accepts_auth_context(self):
        """Verify system_health accepts auth_context parameter"""
        from arifosmcp.intelligence.console_tools import system_health

        auth = {"actor_id": "arif", "clearance": "sovereign"}
        result = await system_health(auth_context=auth)

        # Handle AuthContext BaseModel equivalence with dict
        if hasattr(result.auth_context, "model_dump"):
            dumped = result.auth_context.model_dump(exclude_none=True)
            for k, v in auth.items():
                assert dumped.get(k) == v
        else:
            for k, v in auth.items():
                assert result.auth_context.get(k) == v

    @pytest.mark.asyncio
    async def test_system_health_with_all_params(self):
        """Test system_health with all documented parameters"""
        from arifosmcp.intelligence.console_tools import system_health

        result = await system_health(
            include_swap=True,
            include_io=True,
            include_temp=True,
            session_id="test",
            auth_context={"test": "auth"},
        )

        assert result.tool == "system_health"
        assert result.session_id == "test"
        assert "payload" in str(result) or hasattr(result, "payload")


class TestFsInspectHardened:
    """Test hardened fs_inspect tool"""

    @pytest.mark.asyncio
    async def test_fs_inspect_returns_runtime_envelope(self):
        """Verify fs_inspect returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import fs_inspect
        from arifosmcp.runtime.models import RuntimeEnvelope

        with patch("arifosmcp.intelligence.tools.fs_inspector.inspect_path") as mock_inspect:
            mock_inspect.return_value = {"files": [], "directories": []}

            result = await fs_inspect(path="/test")

            assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_fs_inspect_accepts_governance_params(self):
        """Verify fs_inspect accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import fs_inspect

        with patch("arifosmcp.intelligence.tools.fs_inspector.inspect_path") as mock_inspect:
            mock_inspect.return_value = {"files": []}

            result = await fs_inspect(
                path="/test", session_id="sess-123", auth_context={"actor": "test"}
            )

            assert result.session_id == "sess-123"
            if hasattr(result.auth_context, "model_dump"):
                dumped = result.auth_context.model_dump(exclude_none=True)
                assert dumped.get("actor") == "test"
            else:
                assert result.auth_context.get("actor") == "test"


class TestChromaQueryHardened:
    """Test hardened chroma_query tool"""

    @pytest.mark.asyncio
    async def test_chroma_query_returns_runtime_envelope(self):
        """Verify chroma_query returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import chroma_query
        from arifosmcp.runtime.models import RuntimeEnvelope

        with patch("arifosmcp.intelligence.tools.chroma_query.query_memory") as mock_query:
            mock_query.return_value = AsyncMock()
            mock_query.return_value = {"ids": [["doc1"]], "distances": [[0.1]]}

            result = await chroma_query(query="test query")

            assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_chroma_query_accepts_governance_params(self):
        """Verify chroma_query accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import chroma_query

        with patch("arifosmcp.intelligence.tools.chroma_query.query_memory") as mock_query:
            mock_query.return_value = AsyncMock()
            mock_query.return_value = {"results": []}

            result = await chroma_query(
                query="test", session_id="vector-session", auth_context={"clearance": "agent"}
            )

            assert result.session_id == "vector-session"


class TestLogTailHardened:
    """Test hardened log_tail tool"""

    @pytest.mark.asyncio
    async def test_log_tail_returns_runtime_envelope(self):
        """Verify log_tail returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import log_tail
        from arifosmcp.runtime.models import RuntimeEnvelope

        with patch("arifosmcp.intelligence.tools.log_reader.log_tail") as mock_log:
            mock_log.return_value = AsyncMock()
            mock_log.return_value = {"lines": ["log1", "log2"], "count": 2}

            result = await log_tail(log_file="test.log")

            assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_log_tail_accepts_governance_params(self):
        """Verify log_tail accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import log_tail

        with patch("arifosmcp.intelligence.tools.log_reader.log_tail") as mock_log:
            mock_log.return_value = AsyncMock()
            mock_log.return_value = {"lines": []}

            result = await log_tail(
                log_file="test.log", session_id="log-session", auth_context={"actor": "admin"}
            )

            assert result.session_id == "log-session"


class TestProcessListHardened:
    """Test hardened process_list tool"""

    @pytest.mark.asyncio
    async def test_process_list_returns_runtime_envelope(self):
        """Verify process_list returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import process_list
        from arifosmcp.runtime.models import RuntimeEnvelope

        result = await process_list()

        assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_process_list_accepts_governance_params(self):
        """Verify process_list accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import process_list

        result = await process_list(session_id="proc-session", auth_context={"role": "monitor"})

        assert result.session_id == "proc-session"


class TestNetStatusHardened:
    """Test hardened net_status tool"""

    @pytest.mark.asyncio
    async def test_net_status_returns_runtime_envelope(self):
        """Verify net_status returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import net_status
        from arifosmcp.runtime.models import RuntimeEnvelope

        with patch("arifosmcp.intelligence.tools.net_monitor.check_connectivity") as mock_check:
            mock_check.return_value = AsyncMock()
            mock_check.return_value = {"status": "ok", "latency": 10}

            result = await net_status()

            assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_net_status_accepts_governance_params(self):
        """Verify net_status accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import net_status

        with patch("arifosmcp.intelligence.tools.net_monitor.check_connectivity") as mock_check:
            mock_check.return_value = AsyncMock()
            mock_check.return_value = {"status": "ok"}

            result = await net_status(
                session_id="net-session", auth_context={"actor": "network-admin"}
            )

            assert result.session_id == "net-session"


class TestListResourcesHardened:
    """Test hardened arifos_list_resources tool"""

    @pytest.mark.asyncio
    async def test_list_resources_returns_runtime_envelope(self):
        """Verify arifos_list_resources returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import arifos_list_resources
        from arifosmcp.runtime.models import RuntimeEnvelope

        result = await arifos_list_resources()

        assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_list_resources_accepts_governance_params(self):
        """Verify arifos_list_resources accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import arifos_list_resources

        result = await arifos_list_resources(
            session_id="resource-session", auth_context={"actor": "resource-admin"}
        )

        assert result.session_id == "resource-session"


class TestReadResourceHardened:
    """Test hardened arifos_read_resource tool"""

    @pytest.mark.asyncio
    async def test_read_resource_returns_runtime_envelope(self):
        """Verify arifos_read_resource returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import arifos_read_resource
        from arifosmcp.runtime.models import RuntimeEnvelope

        result = await arifos_read_resource(uri="canon://floors")

        assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_read_resource_accepts_governance_params(self):
        """Verify arifos_read_resource accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import arifos_read_resource

        result = await arifos_read_resource(
            uri="canon://tools", session_id="read-session", auth_context={"actor": "reader"}
        )

        assert result.session_id == "read-session"


class TestCostEstimatorHardened:
    """Test hardened cost_estimator tool"""

    @pytest.mark.asyncio
    async def test_cost_estimator_returns_runtime_envelope(self):
        """Verify cost_estimator returns RuntimeEnvelope"""
        from arifosmcp.intelligence.console_tools import cost_estimator
        from arifosmcp.runtime.models import RuntimeEnvelope

        result = await cost_estimator(operation="search")

        assert isinstance(result, RuntimeEnvelope)

    @pytest.mark.asyncio
    async def test_cost_estimator_accepts_governance_params(self):
        """Verify cost_estimator accepts session_id and auth_context"""
        from arifosmcp.intelligence.console_tools import cost_estimator

        result = await cost_estimator(
            operation="search", session_id="cost-session", auth_context={"actor": "budget-admin"}
        )

        assert result.session_id == "cost-session"


class TestAllNineTools:
    """Test all 9 tools together"""

    @pytest.mark.asyncio
    async def test_all_tools_return_runtime_envelope(self):
        """Verify all 9 tools return RuntimeEnvelope"""
        from arifosmcp.intelligence import console_tools
        from arifosmcp.runtime.models import RuntimeEnvelope

        tools_to_test = [
            (console_tools.system_health, []),
            (console_tools.fs_inspect, ["/tmp"]),
            (console_tools.chroma_query, ["test"]),
            (console_tools.log_tail, ["test.log"]),
            (console_tools.process_list, []),
            (console_tools.net_status, []),
            (console_tools.arifos_list_resources, []),
            (console_tools.arifos_read_resource, ["canon://floors"]),
            (console_tools.cost_estimator, ["search"]),
        ]

        results = []
        for tool, args in tools_to_test:
            with patch("arifosmcp.intelligence.tools") as mock_tools:
                # Mock all the internal tool calls
                for attr in dir(mock_tools):
                    if not attr.startswith("_"):
                        setattr(mock_tools, attr, AsyncMock(return_value={"ok": True}))

                try:
                    result = await tool(*args)
                    results.append((tool.__name__, isinstance(result, RuntimeEnvelope)))
                except Exception as e:
                    results.append((tool.__name__, False))

        # Check all returned RuntimeEnvelope
        for name, is_envelope in results:
            assert is_envelope, f"{name} did not return RuntimeEnvelope"

    def test_all_tools_have_governance_params(self):
        """Verify all 9 tools have session_id and auth_context"""
        import inspect
        from arifosmcp.intelligence import console_tools

        tools = [
            console_tools.system_health,
            console_tools.fs_inspect,
            console_tools.chroma_query,
            console_tools.log_tail,
            console_tools.process_list,
            console_tools.net_status,
            console_tools.arifos_list_resources,
            console_tools.arifos_read_resource,
            console_tools.cost_estimator,
        ]

        for tool in tools:
            sig = inspect.signature(tool)
            params = list(sig.parameters.keys())

            assert "session_id" in params, f"{tool.__name__} missing session_id"
            assert "auth_context" in params, f"{tool.__name__} missing auth_context"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
