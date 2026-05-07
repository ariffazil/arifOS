"""
arifOS MCP Connector
Connects experiments to live arifOS MCP endpoint for real telemetry.

Authority: 888_JUDGE
Status: PRODUCTION_INTEGRATION
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

try:
    import aiohttp

    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    print("Warning: aiohttp not installed. Using fallback simulation only.")


@dataclass
class MCPTelemetry:
    """Real telemetry from arifOS MCP."""

    timestamp: float
    latency_ms: float
    verdict: str
    delta_s: float
    omega: float
    W_cube: float
    floors_violated: List[str]
    tool_used: str
    request_complexity: float


class arifOSMCPConnector:
    """
    Connector to live arifOS MCP endpoint.

    Usage:
        connector = arifOSMCPConnector(endpoint="https://arifosmcp.arif-fazil.com/mcp")
        telemetry = await connector.send_request({"query": "..."})
    """

    def __init__(
        self,
        endpoint: str = "https://arifosmcp.arif-fazil.com/mcp",
        api_key: Optional[str] = None,
        timeout_seconds: float = 30.0,
    ):
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout_seconds
        self.session = None

    async def __aenter__(self):
        """Async context manager entry."""
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp not installed. Cannot connect to live MCP.")
        self.session = aiohttp.ClientSession(
            headers=self._get_headers(), timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth if available."""
        headers = {"Content-Type": "application/json", "User-Agent": "arifOS-Autoresearch/1.0"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def send_request(
        self, request_payload: Dict[str, Any], tool: str = "agi_mind"
    ) -> MCPTelemetry:
        """
        Send request to arifOS MCP and capture telemetry.

        Args:
            request_payload: The actual request (e.g., {"query": "..."})
            tool: Which tool to invoke

        Returns:
            MCPTelemetry with real metrics from the system
        """
        if not self.session:
            raise RuntimeError("Connector not initialized. Use async with.")

        # Prepare MCP request
        mcp_request = {
            "tool": tool,
            "parameters": request_payload,
            "context": {
                "session_id": f"autoresearch_{int(time.time())}",
                "actor_id": "888_JUDGE",
                "request_source": "autoresearch_experiment",
            },
        }

        start_time = time.time()

        try:
            async with self.session.post(self.endpoint, json=mcp_request) as response:
                latency_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    data = await response.json()
                    return self._parse_telemetry(data, latency_ms)
                else:
                    # Handle error response
                    error_text = await response.text()
                    return self._create_error_telemetry(
                        latency_ms, f"HTTP {response.status}: {error_text}"
                    )

        except asyncio.TimeoutError:
            return self._create_error_telemetry(self.timeout * 1000, "TIMEOUT")
        except Exception as e:
            return self._create_error_telemetry((time.time() - start_time) * 1000, str(e))

    def _parse_telemetry(self, response_data: Dict[str, Any], latency_ms: float) -> MCPTelemetry:
        """Parse MCP response into telemetry object."""

        # Extract verdict
        verdict = response_data.get("verdict", "VOID")

        # Extract metrics
        metrics = response_data.get("metrics", {})
        delta_s = metrics.get("delta_s", 0.0)
        omega = metrics.get("confidence", 0.04)  # Ω is stored as confidence
        W_cube = response_data.get("constitutional_context", {}).get("W_cube", 0.0)

        # Extract violations
        violations = response_data.get("constitutional_context", {}).get("violations", [])
        floors_violated = [v.split(":")[0] for v in violations] if violations else []

        # Calculate request complexity (from payload analysis)
        complexity = self._estimate_complexity(response_data)

        return MCPTelemetry(
            timestamp=time.time(),
            latency_ms=latency_ms,
            verdict=verdict,
            delta_s=delta_s,
            omega=omega,
            W_cube=W_cube,
            floors_violated=floors_violated,
            tool_used=response_data.get("tool", "unknown"),
            request_complexity=complexity,
        )

    def _create_error_telemetry(self, latency_ms: float, error: str) -> MCPTelemetry:
        """Create telemetry for failed requests."""
        return MCPTelemetry(
            timestamp=time.time(),
            latency_ms=latency_ms,
            verdict="VOID",
            delta_s=0.0,
            omega=0.0,
            W_cube=0.0,
            floors_violated=["SYSTEM_ERROR"],
            tool_used="none",
            request_complexity=0.0,
        )

    def _estimate_complexity(self, response_data: Dict[str, Any]) -> float:
        """
        Estimate request complexity from response features.

        Higher complexity = more reasoning steps, longer processing,
        higher entropy in input/output.
        """
        complexity_signals = 0.0

        # Check payload size
        payload_str = json.dumps(response_data)
        if len(payload_str) > 10000:
            complexity_signals += 0.3
        elif len(payload_str) > 5000:
            complexity_signals += 0.2
        elif len(payload_str) > 1000:
            complexity_signals += 0.1

        # Check for multi-step reasoning
        if "reasoning" in str(response_data).lower():
            complexity_signals += 0.2

        # Check tool used
        tool = response_data.get("tool", "")
        complexity_by_tool = {
            "agi_mind": 0.7,
            "asi_heart": 0.6,
            "engineering_memory": 0.4,
            "code_engine": 0.8,
            "math_estimator": 0.5,
        }
        complexity_signals += complexity_by_tool.get(tool, 0.3)

        # Normalize to [0, 1]
        return min(1.0, complexity_signals)

    async def health_check(self) -> Dict[str, Any]:
        """Check MCP endpoint health."""
        try:
            async with self.session.get(f"{self.endpoint}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "DEGRADED", "http_status": response.status}
        except Exception as e:
            return {"status": "UNREACHABLE", "error": str(e)}


class FallbackTelemetryProvider:
    """
    Fallback provider when MCP is unavailable.
    Uses realistic simulation based on validated distributions.
    """

    def __init__(self, seed: int = 42):
        import random

        self.random = random.Random(seed)

    async def generate_telemetry(
        self, request_payload: Dict[str, Any], tool: str = "agi_mind"
    ) -> MCPTelemetry:
        """Generate realistic simulated telemetry."""

        # Estimate complexity from request
        complexity = self._estimate_complexity_local(request_payload)

        # Generate metrics based on complexity
        latency_ms = self.random.gauss(200 + complexity * 300, 50)
        delta_s = self.random.gauss(-0.1 - complexity * 0.1, 0.15)
        omega = self.random.gauss(0.04, 0.005 + complexity * 0.01)
        omega = max(0.015, min(0.20, omega))  # Constrain to valid band
        W_cube = self.random.gauss(0.97, 0.02)

        # Determine verdict based on thresholds
        floors_violated = []
        if delta_s > 0.3:
            floors_violated.append("F4_CLARITY")
        if omega < 0.015:
            floors_violated.append("F7_HUMILITY")
        if omega > 0.20:
            floors_violated.append("F7_HUMILITY")

        verdict = "VOID" if floors_violated else "SEAL"

        return MCPTelemetry(
            timestamp=time.time(),
            latency_ms=max(10, latency_ms),
            verdict=verdict,
            delta_s=delta_s,
            omega=omega,
            W_cube=max(0, min(1, W_cube)),
            floors_violated=floors_violated,
            tool_used=tool,
            request_complexity=complexity,
        )

    def _estimate_complexity_local(self, payload: Dict[str, Any]) -> float:
        """Local complexity estimation."""
        payload_str = json.dumps(payload)
        if len(payload_str) > 1000:
            return 0.7
        elif len(payload_str) > 500:
            return 0.5
        else:
            return 0.3


# Convenience function for experiments
async def get_telemetry(
    request: Dict[str, Any],
    use_live_mcp: bool = False,
    endpoint: str = "https://arifosmcp.arif-fazil.com/mcp",
) -> MCPTelemetry:
    """
    Get telemetry for a request.

    Args:
        request: The request payload
        use_live_mcp: If True, connect to real MCP. If False, use simulation.
        endpoint: MCP endpoint URL
    """
    if use_live_mcp:
        async with arifOSMCPConnector(endpoint=endpoint) as connector:
            health = await connector.health_check()
            if health.get("status") == "healthy":
                return await connector.send_request(request)
            else:
                print(f"MCP unhealthy ({health}), falling back to simulation")
                provider = FallbackTelemetryProvider()
                return await provider.generate_telemetry(request)
    else:
        provider = FallbackTelemetryProvider()
        return await provider.generate_telemetry(request)


if __name__ == "__main__":
    # Demo usage
    async def demo():
        print("=" * 60)
        print("arifOS MCP Connector Demo")
        print("=" * 60)

        # Test with fallback (simulation)
        print("\n1. Simulated telemetry:")
        telemetry = await get_telemetry({"query": "Explain constitutional AI"}, use_live_mcp=False)
        print(f"   Verdict: {telemetry.verdict}")
        print(f"   Ω: {telemetry.omega:.4f}")
        print(f"   ΔS: {telemetry.delta_s:.4f}")
        print(f"   Complexity: {telemetry.request_complexity:.2f}")
        print(f"   Latency: {telemetry.latency_ms:.1f}ms")

        # Test MCP health (live)
        print("\n2. MCP health check (live):")
        if HAS_AIOHTTP:
            async with arifOSMCPConnector() as connector:
                health = await connector.health_check()
                print(f"   Status: {health.get('status', 'unknown')}")
                if "error" in health:
                    print(f"   Error: {health['error']}")
        else:
            print("   Skipped (aiohttp not installed)")

        print("\n" + "=" * 60)

    asyncio.run(demo())
