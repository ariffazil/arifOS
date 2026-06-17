"""
client.py — arifOS MCP client.

Talks to the live arifOS MCP server (the kernel) over HTTP/SSE.
Used by the 4 guards to issue kernel calls.

Default base URL is the public production endpoint. Override for
local dev or testing.

Uses streamable HTTP transport per MCP spec 2025-11-25.
"""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from arifos.actor import Actor
from arifos.envelope import CallEnvelope
from arifos.intent import Intent


class ArifOSMCPClient:
    """
    Thin client for the arifOS MCP server.

    Default base URL points at the public production endpoint
    `https://arifos.arif-fazil.com`. Override for local dev:

        client = ArifOSMCPClient(base_url="http://localhost:8088")

    The kernel is the source of truth. This client is just transport.
    """

    def __init__(
        self,
        base_url: str = "https://arifos.arif-fazil.com",
        actor: Actor | None = None,
        timeout: float = 30.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.mcp_url = f"{self.base_url}/mcp"
        self.actor = actor or Actor(actor_id="arif", actor_type="sovereign")
        self.timeout = timeout
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def _call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Call an arifOS MCP tool. Returns the result envelope."""
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
                "_meta": {
                    "actor_id": self.actor.actor_id,
                    "session_id": self.actor.session_id or f"sess_{os.urandom(8).hex()}",
                },
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.mcp_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
            )
            response.raise_for_status()

            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                result = None
                for line in response.text.splitlines():
                    if line.startswith("data: "):
                        result = json.loads(line[6:])
                if result is None:
                    raise RuntimeError("Empty SSE response from arifOS MCP")
                return result
            return response.json()

    async def kernel_check_call(
        self,
        intent: Intent,
        parent_lease_id: str | None = None,
    ) -> dict[str, Any]:
        """Issue a kernel.check_call (Band 1 cognition firewall endpoint)."""
        return await self._call(
            "arif_kernel_route",
            {
                "mode": "check_call",
                "intent": intent.model_dump(mode="json"),
                "parent_lease_id": parent_lease_id,
            },
        )

    async def kernel_seal(
        self,
        decision: dict[str, Any],
        output: dict[str, Any],
    ) -> dict[str, Any]:
        """Seal a decision + output to VAULT999."""
        return await self._call(
            "arif_vault_seal",
            {
                "decision": decision,
                "output": output,
            },
        )
