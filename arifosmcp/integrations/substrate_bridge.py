"""
arifosmcp/integrations/substrate_bridge.py — Substrate Integration Layer

This module manages the connection to the 5 primary substrate services:
1. Time (mcp_time)
2. Filesystem (mcp_filesystem)
4. Git (mcp_git)
5. Memory (mcp_memory)
6. Fetch (mcp_fetch)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import httpx

logger = logging.getLogger(__name__)

class SubstrateClient:
    """Base client for MCP substrate services."""
    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def health_check(self) -> dict[str, Any]:
        """Verify service connectivity."""
        try:
            # Most MCP SSE servers expose /health or /tools
            response = await self.client.get("/health")
            if response.status_code == 200:
                return {"status": "OK", "service": self.service_name}
            return {"status": "DEGRADED", "service": self.service_name, "code": response.status_code}
        except Exception as e:
            return {"status": "DOWN", "service": self.service_name, "error": str(e)}

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Invoke a tool on the substrate server via MCP-over-HTTP/SSE."""
        # This is a simplified placeholder for the actual MCP SSE/HTTP protocol
        # In a real implementation, this would handle the SSE session management
        try:
            response = await self.client.post(f"/tools/{tool_name}/call", json={"arguments": arguments})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Substrate call failed [{self.service_name}:{tool_name}]: {e}")
            raise

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools on the substrate."""
        try:
            response = await self.client.get("/tools")
            response.raise_for_status()
            return response.json().get("tools", [])
        except Exception:
            return []

    async def list_resources(self) -> list[dict[str, Any]]:
        """List available resources on the substrate."""
        try:
            response = await self.client.get("/resources")
            response.raise_for_status()
            return response.json().get("resources", [])
        except Exception:
            return []

    async def list_prompts(self) -> list[dict[str, Any]]:
        """List available prompts on the substrate."""
        try:
            response = await self.client.get("/prompts")
            response.raise_for_status()
            return response.json().get("prompts", [])
        except Exception:
            return []

class SubstrateBridge:
    """Unified bridge for all arifOS substrate services."""
    
    def __init__(self):
        # Service URLs reflect the docker-compose container names on the core network
        self.time = SubstrateClient("mcp_time", "http://mcp_time:8000")
        self.filesystem = SubstrateClient("mcp_filesystem", "http://mcp_filesystem:8000")
        self.git = SubstrateClient("mcp_git", "http://mcp_git:8000")
        self.memory = SubstrateClient("mcp_memory", "http://mcp_memory:8000")
        self.fetch = SubstrateClient("mcp_fetch", "http://mcp_fetch:8000")
        self.everything = SubstrateClient("mcp_everything", "http://mcp_everything:8000")
        
        self.clients = [self.time, self.filesystem, self.git, self.memory, self.fetch, self.everything]

    async def get_global_health(self) -> dict[str, Any]:
        """Rollup health status for all substrate components."""
        results = {}
        for client in self.clients:
            results[client.service_name] = await client.health_check()
            
        return {
            "status": "HEALTHY" if all(r["status"] == "OK" for r in results.values()) else "DEGRADED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "substrate": results
        }

# Global bridge instance
bridge = SubstrateBridge()
