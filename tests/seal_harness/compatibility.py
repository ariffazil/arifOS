"""
Compatibility Probe — Multi-Client Verification for arifOS MCP

This module implements compatibility testing across different MCP client
configurations and transport modes.

Test Coverage:
- HTTP Streamable transport (production default)
- Protocol version negotiation
- Session header handling
- Response format consistency

Constitutional Note (F8 Integrity):
    Behavior must be deterministic across all supported configurations.
    No hidden client-specific logic paths.

Version: 2026.3.1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from tests.seal_harness.client import (
    DEFAULT_ENDPOINT,
    MCPStreamableClient,
    parse_tool_result_json,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class CompatibilityResult:
    """Result of a compatibility probe."""

    test_name: str
    status: str  # PASS, FAIL, SKIP, INFO
    transport: str
    protocol_version: str
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_name": self.test_name,
            "status": self.status,
            "transport": self.transport,
            "protocol_version": self.protocol_version,
            "details": self.details,
            "error": self.error,
            "duration_ms": round(self.duration_ms, 2),
        }


@dataclass
class BehaviorComparison:
    """Comparison of behavior across multiple clients."""

    tool_name: str
    results_match: bool
    differences: list[dict[str, Any]] = field(default_factory=list)
    client_results: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "results_match": self.results_match,
            "differences": self.differences,
            "client_results": self.client_results,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Compatibility Probe
# ═══════════════════════════════════════════════════════════════════════════════


class CompatibilityProbe:
    """
        Multi-client compatibility verification for arifOS MCP.

        Tests various client configurations against the same endpoint
    to ensure consistent behavior.
    """

    def __init__(
        self,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: float = 30.0,
    ):
        """
        Initialize the compatibility probe.

        Args:
            endpoint: MCP server endpoint URL
            timeout: Request timeout in seconds
        """
        self.endpoint = endpoint
        self.timeout = timeout
        self.results: list[CompatibilityResult] = []

    async def run_all_tests(self) -> list[CompatibilityResult]:
        """
        Run all compatibility tests.

        Returns:
            List of all test results
        """
        self.results = []

        # HTTP Streamable tests
        self.results.append(await self.test_http_streamable())
        self.results.append(await self.test_protocol_negotiation())
        self.results.append(await self.test_session_management())
        self.results.append(await self.test_tool_call_flow())

        # Documentation notes for other transports
        self.results.append(await self.test_stdio_compatibility())
        self.results.append(await self.test_sse_mode_notes())

        return self.results

    async def test_http_streamable(self) -> CompatibilityResult:
        """
        Test HTTP Streamable transport with httpx.

        Verifies:
        - Connection establishment
        - JSON-RPC request/response
        - Proper header handling
        """
        import time

        start = time.perf_counter()
        result = CompatibilityResult(
            test_name="http_streamable_basic",
            transport="http",
            protocol_version="2024-11-05",
        )

        try:
            async with MCPStreamableClient(
                endpoint=self.endpoint,
                timeout=self.timeout,
            ) as client:
                init_data = await client.initialize()

                result.details = {
                    "server_name": init_data.get("serverInfo", {}).get("name"),
                    "server_version": init_data.get("serverInfo", {}).get("version"),
                    "negotiated_protocol": init_data.get("protocolVersion"),
                    "capabilities": init_data.get("capabilities"),
                    "session_id": client.session_id,
                }
                result.status = "PASS"

        except Exception as e:
            result.status = "FAIL"
            result.error = f"{type(e).__name__}: {e}"

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    async def test_protocol_negotiation(self) -> CompatibilityResult:
        """
        Test MCP protocol version negotiation.

        Verifies that server correctly handles different protocol versions
        and negotiates appropriately.
        """
        import time

        start = time.perf_counter()
        result = CompatibilityResult(
            test_name="protocol_negotiation",
            transport="http",
            protocol_version="various",
        )

        negotiation_results = []

        # Test various protocol versions
        test_versions = ["2024-11-05", "2025-11-25"]

        for version in test_versions:
            try:
                async with MCPStreamableClient(
                    endpoint=self.endpoint,
                    protocol_version=version,
                    timeout=self.timeout,
                ) as client:
                    init_data = await client.initialize()
                    negotiated = init_data.get("protocolVersion", "unknown")

                    negotiation_results.append(
                        {
                            "requested": version,
                            "negotiated": negotiated,
                            "success": True,
                        }
                    )
            except Exception as e:
                negotiation_results.append(
                    {
                        "requested": version,
                        "error": str(e),
                        "success": False,
                    }
                )

        result.details = {"negotiations": negotiation_results}

        # PASS if at least one version negotiates successfully
        if any(r["success"] for r in negotiation_results):
            result.status = "PASS"
        else:
            result.status = "FAIL"

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    async def test_session_management(self) -> CompatibilityResult:
        """
        Test session header management.

        Verifies:
        - Session ID is generated on initialize
        - Session ID is consistent across requests
        - Session header is properly transmitted
        """
        import time

        start = time.perf_counter()
        result = CompatibilityResult(
            test_name="session_management",
            transport="http",
            protocol_version="2024-11-05",
        )

        try:
            async with MCPStreamableClient(
                endpoint=self.endpoint,
                timeout=self.timeout,
            ) as client:
                # Initialize
                await client.initialize()
                session_id_1 = client.session_id

                # Make another request - should maintain same session
                tools = await client.list_tools()

                # The client maintains the session ID
                session_id_2 = client.session_id

                result.details = {
                    "session_id_generated": bool(session_id_1),
                    "session_id_consistent": session_id_1 == session_id_2,
                    "session_id": session_id_1[:16] + "..." if session_id_1 else None,
                    "tool_count": len(tools),
                }

                if session_id_1 and session_id_1 == session_id_2:
                    result.status = "PASS"
                else:
                    result.status = "FAIL"
                    result.error = "Session ID not consistent across requests"

        except Exception as e:
            result.status = "FAIL"
            result.error = f"{type(e).__name__}: {e}"

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    async def test_tool_call_flow(self) -> CompatibilityResult:
        """
        Test complete tool call flow.

        Verifies anchor_session → reason_mind chain works correctly.
        """
        import time

        start = time.perf_counter()
        result = CompatibilityResult(
            test_name="tool_call_flow",
            transport="http",
            protocol_version="2024-11-05",
        )

        try:
            async with MCPStreamableClient(
                endpoint=self.endpoint,
                timeout=self.timeout,
            ) as client:
                # Initialize
                await client.initialize()

                # Call anchor_session
                anchor_result = await client.call_tool(
                    "anchor_session",
                    {"query": "Compatibility probe test", "actor_id": "probe"},
                )

                if anchor_result.is_error:
                    result.status = "FAIL"
                    result.error = f"anchor_session failed: {anchor_result.raw_response}"
                    result.duration_ms = (time.perf_counter() - start) * 1000
                    return result

                anchor_data = parse_tool_result_json(anchor_result) or {}
                session_id = anchor_data.get("session_id")

                if not session_id:
                    result.status = "FAIL"
                    result.error = "No session_id in anchor response"
                    result.duration_ms = (time.perf_counter() - start) * 1000
                    return result

                # Call reason_mind with the session
                reason_result = await client.call_tool(
                    "reason_mind",
                    {
                        "query": "Test query",
                        "session_id": session_id,
                        "actor_id": "probe",
                    },
                )

                reason_data = parse_tool_result_json(reason_result) or {}

                result.details = {
                    "anchor_verdict": anchor_data.get("verdict"),
                    "reason_verdict": reason_data.get("verdict"),
                    "session_id": session_id[:16] + "..." if session_id else None,
                    "chain_complete": bool(reason_data.get("verdict")),
                }

                if reason_data.get("verdict"):
                    result.status = "PASS"
                else:
                    result.status = "FAIL"
                    result.error = "Tool call chain incomplete"

        except Exception as e:
            result.status = "FAIL"
            result.error = f"{type(e).__name__}: {e}"

        result.duration_ms = (time.perf_counter() - start) * 1000
        return result

    async def test_stdio_compatibility(self) -> CompatibilityResult:
        """
        Document stdio transport compatibility.

        Note: stdio mode requires different setup (subprocess spawn).
        This test documents the requirements but does not execute stdio tests.
        """
        result = CompatibilityResult(
            test_name="stdio_compatibility_notes",
            transport="stdio",
            protocol_version="n/a",
            status="INFO",
        )

        result.details = {
            "supported": True,
            "requirements": [
                "Python 3.12+",
                "Direct subprocess spawn of arifOS MCP server",
                "stdin/stdout communication (no HTTP)",
                "Requires 'python -m arifosmcp.runtime stdio'",
            ],
            "test_coverage": "Not automated - requires subprocess orchestration",
            "notes": [
                "stdio mode is primarily for Claude Desktop / Cursor IDE",
                "Same JSON-RPC protocol over stdio instead of HTTP",
                "Session management differs - no HTTP headers",
            ],
        }

        return result

    async def test_sse_mode_notes(self) -> CompatibilityResult:
        """
        Document SSE transport mode compatibility.

        Note: SSE mode is used for server-to-client streaming.
        """
        result = CompatibilityResult(
            test_name="sse_mode_notes",
            transport="sse",
            protocol_version="2024-11-05",
            status="INFO",
        )

        result.details = {
            "supported": True,
            "endpoint": f"{self.endpoint}/sse",
            "requirements": [
                "Accept: text/event-stream header support",
                "Event/data format parsing",
                "Reconnection handling",
            ],
            "test_coverage": "Partial - SSE events parsed but streaming not fully tested",
            "notes": [
                "SSE primarily used for real-time notifications",
                "Most tool calls use standard HTTP POST + JSON response",
                "arifOS server may return SSE for long-running operations",
            ],
        }

        return result

    async def compare_client_behaviors(
        self,
        tool_name: str = "anchor_session",
        tool_args: dict[str, Any] | None = None,
    ) -> BehaviorComparison:
        """
        Compare behavior of the same tool call across different client configs.

        Args:
            tool_name: Tool to test
            tool_args: Arguments for the tool

        Returns:
            BehaviorComparison showing differences
        """
        if tool_args is None:
            tool_args = {"query": "Behavior comparison test", "actor_id": "probe"}

        comparison = BehaviorComparison(tool_name=tool_name)

        # Test with different protocol versions
        configs = [
            ("2024-11-05", "http-2024-11-05"),
            ("2025-11-25", "http-2025-11-25"),
        ]

        for protocol, label in configs:
            try:
                async with MCPStreamableClient(
                    endpoint=self.endpoint,
                    protocol_version=protocol,
                    timeout=self.timeout,
                ) as client:
                    await client.initialize()
                    result = await client.call_tool(tool_name, tool_args)
                    data = parse_tool_result_json(result) or {}

                    comparison.client_results[label] = {
                        "verdict": data.get("verdict"),
                        "stage": data.get("stage"),
                        "success": not result.is_error,
                    }
            except Exception as e:
                comparison.client_results[label] = {
                    "error": str(e),
                    "success": False,
                }

        # Check for differences
        successful_results = [
            r for r in comparison.client_results.values() if r.get("success") and "verdict" in r
        ]

        if len(successful_results) > 1:
            verdicts = {r["verdict"] for r in successful_results}
            if len(verdicts) > 1:
                comparison.results_match = False
                comparison.differences.append(
                    {
                        "field": "verdict",
                        "values": list(verdicts),
                        "severity": "WARNING",
                    }
                )
            else:
                comparison.results_match = True
        else:
            comparison.results_match = len(successful_results) <= 1

        return comparison

    def get_summary(self) -> dict[str, Any]:
        """Get summary of all compatibility test results."""
        if not self.results:
            return {"status": "NOT_RUN", "total": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        info = sum(1 for r in self.results if r.status == "INFO")

        return {
            "status": "PASS" if failed == 0 else "FAIL",
            "total": len(self.results),
            "passed": passed,
            "failed": failed,
            "info": info,
        }
