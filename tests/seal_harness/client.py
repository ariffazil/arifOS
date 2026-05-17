"""
MCP Streamable HTTP Client with SSE parsing.
"""

import json
import uuid
from typing import Dict, Any, Optional
import httpx


class MCPClient:
    """Minimal MCP Streamable HTTP client."""

    def __init__(self, endpoint: str, headers: Optional[Dict[str, str]] = None):
        self.endpoint = endpoint
        self.mcp_session_id: Optional[str] = None
        self.client = httpx.AsyncClient()
        self.custom_headers = headers or {}

    def _parse_sse(self, content: str) -> Optional[Dict]:
        """Parse SSE response to extract JSON data."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("data:"):
                data = line[5:].strip()
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    continue
        # Try direct JSON parse as fallback
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None

    async def initialize(self) -> bool:
        """Initialize MCP session."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "arifos-seal-harness", "version": "2026.3.1"},
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            **self.custom_headers,
        }

        resp = await self.client.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

        # Extract session ID from response header
        self.mcp_session_id = resp.headers.get("mcp-session-id") or str(uuid.uuid4())

        result = self._parse_sse(resp.text)
        return result is not None and "result" in result

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool."""
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.mcp_session_id,
            **self.custom_headers,
        }

        resp = await self.client.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

        result = self._parse_sse(resp.text)

        if result and "result" in result and "content" in result["result"]:
            text = result["result"]["content"][0].get("text", "{}")
            if result["result"].get("isError"):
                return {"_error": text}
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"_text": text, "_raw": text}
        elif result and "error" in result:
            return {"_error": result["error"]}

        return {"_error": "Unknown response format", "_raw": resp.text[:500]}

    async def list_tools(self) -> list:
        """List available tools."""
        payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.mcp_session_id,
            **self.custom_headers,
        }

        resp = await self.client.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

        result = self._parse_sse(resp.text)

        if result and "result" in result:
            return result["result"].get("tools", [])
        return []

    async def list_resources(self) -> list:
        """List available resources."""
        payload = {"jsonrpc": "2.0", "id": 1, "method": "resources/list"}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.mcp_session_id,
            **self.custom_headers,
        }

        resp = await self.client.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

        result = self._parse_sse(resp.text)

        if result and "result" in result:
            return result["result"].get("resources", [])
        return []

    async def list_prompts(self) -> list:
        """List available prompts."""
        payload = {"jsonrpc": "2.0", "id": 1, "method": "prompts/list"}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "mcp-session-id": self.mcp_session_id,
            **self.custom_headers,
        }

        resp = await self.client.post(self.endpoint, json=payload, headers=headers, timeout=30.0)

        result = self._parse_sse(resp.text)

        if result and "result" in result:
            return result["result"].get("prompts", [])
        return []

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
