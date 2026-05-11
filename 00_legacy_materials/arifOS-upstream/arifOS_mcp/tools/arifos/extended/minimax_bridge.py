"""
MiniMax MCP Bridge — Extended Capability Surface
DITEMPA BUKAN DIBERI

Spawns minimax-coding-plan-mcp as a managed stdio subprocess
and exposes web_search + understand_image to the arifOS runtime.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import subprocess
from typing import Any

logger = logging.getLogger("arifOS.minimax_bridge")


class MinimaxMCPBridge:
    """Managed stdio bridge to MiniMax Token Plan MCP."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._lock = asyncio.Lock()
        self._request_id = 0

    def _ensure_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.setdefault("MINIMAX_API_KEY", os.getenv("MINIMAX_API_KEY", ""))
        env.setdefault("MINIMAX_API_HOST", "https://api.minimax.io")
        return env

    async def _spawn(self) -> subprocess.Popen:
        uvx = shutil.which("uvx") or "/usr/local/bin/uvx"
        env = self._ensure_env()
        if not env.get("MINIMAX_API_KEY"):
            raise RuntimeError("MINIMAX_API_KEY not set")

        proc = subprocess.Popen(
            [uvx, "minimax-coding-plan-mcp", "--transport", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        # Wait for initialization handshake
        init_req = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "arifOS", "version": "2026.04.20"},
            },
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()

        # Read initialize response
        line = proc.stdout.readline()
        if not line:
            raise RuntimeError("MiniMax MCP closed stdout during init")

        # Send initialized notification
        proc.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                }
            )
            + "\n"
        )
        proc.stdin.flush()
        return proc

    async def _call(self, method: str, params: dict[str, Any]) -> Any:
        async with self._lock:
            if self._proc is None or self._proc.poll() is not None:
                self._proc = await self._spawn()

            self._request_id += 1
            req = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": method,
                "params": params,
            }

            self._proc.stdin.write(json.dumps(req) + "\n")
            self._proc.stdin.flush()

            line = self._proc.stdout.readline()
            if not line:
                raise RuntimeError("MiniMax MCP closed stdout")

            resp = json.loads(line)
            if "error" in resp:
                raise RuntimeError(f"MiniMax MCP error: {resp['error']}")
            return resp.get("result")

    async def web_search(self, query: str) -> dict[str, Any]:
        """Execute web search via MiniMax MCP."""
        result = await self._call(
            "tools/call",
            {"name": "web_search", "arguments": {"query": query}},
        )
        # Parse content blocks
        content = result.get("content", [])
        for block in content:
            if block.get("type") == "text":
                text = block["text"]
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    if text.startswith("Failed") or text.startswith("Error"):
                        return {
                            "error": text,
                            "base_resp": {"status_code": 400, "status_msg": text},
                        }
                    return {
                        "result": text,
                        "base_resp": {"status_code": 200, "status_msg": "ok"},
                    }
        return {
            "organic": [],
            "base_resp": {"status_code": -1, "status_msg": "no text content"},
        }

    async def understand_image(self, image_url: str, prompt: str = "") -> dict[str, Any]:
        """Analyze image via MiniMax MCP."""
        args: dict[str, Any] = {"image_source": image_url}
        if prompt:
            args["prompt"] = prompt
        result = await self._call(
            "tools/call",
            {"name": "understand_image", "arguments": args},
        )
        content = result.get("content", [])
        for block in content:
            if block.get("type") == "text":
                text = block["text"]
                # Handle both JSON results and plain text errors
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # Plain text error or non-JSON response
                    if text.startswith("Failed") or text.startswith("Error"):
                        return {
                            "error": text,
                            "base_resp": {"status_code": 400, "status_msg": text},
                        }
                    return {
                        "result": text,
                        "base_resp": {"status_code": 200, "status_msg": "ok"},
                    }
        return {
            "result": "",
            "base_resp": {"status_code": -1, "status_msg": "no text content"},
        }


# Singleton bridge instance
_bridge: MinimaxMCPBridge | None = None


def get_bridge() -> MinimaxMCPBridge:
    global _bridge
    if _bridge is None:
        _bridge = MinimaxMCPBridge()
    return _bridge
