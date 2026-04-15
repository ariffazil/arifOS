"""
arifosmcp/integrations/substrate_bridge.py — Substrate Integration Layer

This module manages the connection to the 6 primary substrate services:
1. Time (mcp_time)
2. Filesystem (mcp_filesystem)
3. Git (mcp_git)
4. Memory (mcp_memory)
5. Fetch (mcp_fetch)
6. Everything (mcp_everything) - conformance harness

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# Configuration from environment
MCP_SUBSTRATES_ENABLED = os.getenv("MCP_SUBSTRATES_ENABLED", "true").lower() == "true"
MCP_SUBSTRATE_TIMEOUT = float(os.getenv("MCP_SUBSTRATE_TIMEOUT", "30.0"))


class SubstrateClient:
    """Base client for MCP substrate services."""
    
    def __init__(self, service_name: str, base_url: str, timeout: float = 30.0):
        self.service_name = service_name
        self.base_url = base_url
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy initialization of HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                follow_redirects=True
            )
        return self._client
    
    async def health_check(self) -> dict[str, Any]:
        """Verify service connectivity."""
        if not MCP_SUBSTRATES_ENABLED:
            return {"status": "DISABLED", "service": self.service_name}
        
        try:
            # Try multiple health endpoints
            endpoints = ["/health", "/mcp/health", "/api/health", "/"]
            for endpoint in endpoints:
                try:
                    response = await self.client.get(endpoint, timeout=5.0)
                    if response.status_code in [200, 204]:
                        return {
                            "status": "OK",
                            "service": self.service_name,
                            "endpoint": endpoint,
                            "response_time_ms": response.elapsed.total_seconds() * 1000
                        }
                except Exception:
                    continue
            
            return {
                "status": "DEGRADED",
                "service": self.service_name,
                "error": "No health endpoint responded"
            }
        except Exception as e:
            logger.warning(f"Health check failed for {self.service_name}: {e}")
            return {"status": "DOWN", "service": self.service_name, "error": str(e)}
    
    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a tool on the substrate server via MCP-over-HTTP/SSE."""
        if not MCP_SUBSTRATES_ENABLED:
            raise RuntimeError(f"MCP substrates disabled. Cannot call {tool_name}")
        
        # Try multiple endpoint patterns
        endpoints = [
            f"/tools/{tool_name}/call",
            f"/mcp/tools/{tool_name}/call",
            f"/api/tools/{tool_name}/call",
            f"/{tool_name}",
        ]
        
        last_error = None
        for endpoint in endpoints:
            try:
                response = await self.client.post(
                    endpoint,
                    json={"arguments": arguments, "params": arguments},
                    timeout=self.timeout
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 404:
                    continue  # Try next endpoint
                else:
                    response.raise_for_status()
                    
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}: {e.response.text}"
                if e.response.status_code != 404:
                    break
            except Exception as e:
                last_error = str(e)
                continue
        
        error_msg = f"Substrate call failed [{self.service_name}:{tool_name}]: {last_error}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools on the substrate."""
        if not MCP_SUBSTRATES_ENABLED:
            return []
        
        endpoints = ["/tools", "/mcp/tools", "/api/tools"]
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        return data.get("tools", data.get("result", []))
                    return data if isinstance(data, list) else []
            except Exception:
                continue
        return []
    
    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources on the substrate."""
        if not MCP_SUBSTRATES_ENABLED:
            return []
        
        endpoints = ["/resources", "/mcp/resources", "/api/resources"]
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        return data.get("resources", data.get("result", []))
                    return data if isinstance(data, list) else []
            except Exception:
                continue
        return []
    
    async def list_prompts(self) -> list[dict[str, Any]]:
        """List available prompts on the substrate."""
        if not MCP_SUBSTRATES_ENABLED:
            return []
        
        endpoints = ["/prompts", "/mcp/prompts", "/api/prompts"]
        for endpoint in endpoints:
            try:
                response = await self.client.get(endpoint, timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict):
                        return data.get("prompts", data.get("result", []))
                    return data if isinstance(data, list) else []
            except Exception:
                continue
        return []
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


class SubstrateBridge:
    """Unified bridge for all arifOS substrate services."""
    
    def __init__(self):
        # Service URLs - use environment variables for flexibility
        # Each substrate runs on its own port (8001-8006)
        self.time = SubstrateClient(
            "mcp_time",
            os.getenv("MCP_TIME_URL", "http://mcp_time:8001"),
            MCP_SUBSTRATE_TIMEOUT
        )
        self.filesystem = SubstrateClient(
            "mcp_filesystem",
            os.getenv("MCP_FILESYSTEM_URL", "http://mcp_filesystem:8002"),
            MCP_SUBSTRATE_TIMEOUT
        )
        self.git = SubstrateClient(
            "mcp_git",
            os.getenv("MCP_GIT_URL", "http://mcp_git:8003"),
            MCP_SUBSTRATE_TIMEOUT
        )
        self.memory = SubstrateClient(
            "mcp_memory",
            os.getenv("MCP_MEMORY_URL", "http://mcp_memory:8004"),
            MCP_SUBSTRATE_TIMEOUT
        )
        self.fetch = SubstrateClient(
            "mcp_fetch",
            os.getenv("MCP_FETCH_URL", "http://mcp_fetch:8005"),
            MCP_SUBSTRATE_TIMEOUT
        )
        self.everything = SubstrateClient(
            "mcp_everything",
            os.getenv("MCP_EVERYTHING_URL", "http://mcp_everything:8006"),
            MCP_SUBSTRATE_TIMEOUT
        )
        
        self.clients = [self.time, self.filesystem, self.git, self.memory, self.fetch, self.everything]
    
    async def get_global_health(self) -> dict[str, Any]:
        """Rollup health status for all substrate components."""
        if not MCP_SUBSTRATES_ENABLED:
            return {
                "status": "DISABLED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "substrate": {},
                "note": "MCP substrates disabled via environment"
            }
        
        results = {}
        for client in self.clients:
            results[client.service_name] = await client.health_check()
        
        healthy_count = sum(1 for r in results.values() if r["status"] == "OK")
        total_count = len(results)
        
        status = "HEALTHY" if healthy_count == total_count else \
                 "DEGRADED" if healthy_count > 0 else "DOWN"
        
        return {
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "substrate": results,
            "summary": {
                "healthy": healthy_count,
                "total": total_count,
                "availability": f"{healthy_count}/{total_count}"
            }
        }
    
    async def close_all(self):
        """Close all substrate client connections."""
        for client in self.clients:
            await client.close()


# Global bridge instance
bridge = SubstrateBridge()


# Cleanup helper
async def cleanup_substrate_connections():
    """Cleanup all substrate connections - call on shutdown."""
    await bridge.close_all()
