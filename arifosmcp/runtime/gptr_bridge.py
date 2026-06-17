"""
arifosmcp/runtime/gptr_bridge.py — gptr-mcp organ bridge for arifOS

Wraps the gptr-mcp organ (running on 127.0.0.1:18084, added 2026-06-16)
as a set of async methods. Exposes the 5 gptr-mcp tools:

  - deep_research       — multi-step research, 30-60s, ~$0.40
  - quick_search        — fast web search w/ snippets
  - write_report        — report generation from research
  - get_research_sources — pull source list
  - get_research_context — pull full research context

F2 epistemic tag: every successful envelope carries `epistemic_tag`
(INTERPRETATION for AI-curated content, OBSERVED for raw data).

This is an in-process MCP client. The gptr organ must be running on
127.0.0.1:18084 (started by gptr-organ.service). The bridge will:
  1. Open SSE stream
  2. Get session_id
  3. POST initialize, tools/call
  4. Read response from SSE
  5. Return parsed result

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_GPTR_URL = os.getenv("GPTR_ORGAN_URL", "http://127.0.0.1:18084")
_GPTR_TIMEOUT = float(os.getenv("GPTR_ORGAN_TIMEOUT", "180.0"))


class GPTROrganBridge:
    """Async MCP client for the gptr-mcp organ (port 18084)."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None
        self._session_id: str | None = None
        self._lock = asyncio.Lock()
        self._request_id = 0

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=_GPTR_TIMEOUT)
        return self._client

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    async def health(self) -> dict[str, Any]:
        """Lightweight health check via /health endpoint."""
        client = self._get_client()
        try:
            resp = await client.get(f"{_GPTR_URL}/health")
            resp.raise_for_status()
            return {
                "status": "healthy",
                "gptr_response": resp.json(),
            }
        except Exception as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "gptr_url": _GPTR_URL,
                "bridge": "gptr_organ_health",
            }

    async def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        bridge_name: str = "gptr_organ",
        timeout: float = 180.0,
    ) -> dict[str, Any]:
        """
        Open MCP session to gptr, call a tool, return the parsed content.

        Pattern (proven by test_gptr_mcp_client.py):
          1. Open a long-lived background task that reads /sse into a queue
          2. Wait for the session_id event from the queue
          3. POST initialize, wait for the init response from the queue
          4. POST tools/call, wait for the call response from the queue

        Uses a single httpx client for everything (SSE + POSTs). The client's
        connection pool routes SSE and POSTs over separate TCP connections
        since the gptr server uses HTTP/1.1 keepalive.
        """
        client = self._get_client()
        sse_events: asyncio.Queue = asyncio.Queue()

        async def sse_reader() -> None:
            try:
                async with client.stream("GET", f"{_GPTR_URL}/sse") as resp:
                    async for line in resp.aiter_lines():
                        if line.startswith("data:"):
                            data = line[5:].strip()
                            if data:
                                await sse_events.put(data)
            except (asyncio.CancelledError, Exception) as exc:
                logger.debug("sse_reader ended: %s", exc)

        try:
            # Step 1: Start SSE reader
            reader_task = asyncio.create_task(sse_reader())

            # Step 2: Wait for session_id
            try:
                session_id = None
                while True:
                    data = await asyncio.wait_for(sse_events.get(), timeout=10.0)
                    if "session_id=" in data:
                        session_id = data.split("session_id=", 1)[1].strip()
                        break
            except asyncio.TimeoutError:
                reader_task.cancel()
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": "gptr SSE timeout (no session_id in 10s)",
                    "bridge": bridge_name,
                }

            # Step 3: Send initialize
            await client.post(
                f"{_GPTR_URL}/messages/?session_id={session_id}",
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-25",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "arifOS-gptr-bridge",
                            "version": "1.0",
                        },
                    },
                },
            )

            # Read init response (consume it from the queue)
            try:
                await asyncio.wait_for(sse_events.get(), timeout=15.0)
            except asyncio.TimeoutError:
                reader_task.cancel()
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": "gptr initialize response timeout",
                    "bridge": bridge_name,
                }

            # Step 4: Send the tool call
            await client.post(
                f"{_GPTR_URL}/messages/?session_id={session_id}",
                json={
                    "jsonrpc": "2.0",
                    "id": self._next_id(),
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments,
                    },
                },
            )

            # Read tool call response
            try:
                raw_response = await asyncio.wait_for(
                    sse_events.get(), timeout=timeout
                )
            except asyncio.TimeoutError:
                reader_task.cancel()
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": f"gptr tool {tool_name} timeout after {timeout}s",
                    "bridge": bridge_name,
                }

            reader_task.cancel()
            try:
                await reader_task
            except (asyncio.CancelledError, Exception):
                pass

            # Step 5: Parse the JSON-RPC response
            try:
                parsed = json.loads(raw_response)
            except json.JSONDecodeError as exc:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": f"invalid JSON from gptr: {exc}",
                    "raw": raw_response[:200],
                    "bridge": bridge_name,
                }

            if "error" in parsed:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": parsed["error"].get("message", str(parsed["error"])),
                    "error_code": parsed["error"].get("code"),
                    "bridge": bridge_name,
                }

            result = parsed.get("result", {})
            content = result.get("content", [])

            text_payloads: list[str] = []
            for item in content:
                if item.get("type") == "text":
                    text_payloads.append(item.get("text", ""))
                else:
                    text_payloads.append(json.dumps(item))

            if not text_payloads:
                return {
                    "status": "error",
                    "verdict": "SABAR",
                    "error": "gptr returned empty content",
                    "bridge": bridge_name,
                }

            try:
                inner = json.loads(text_payloads[0])
            except (json.JSONDecodeError, IndexError):
                inner = {"raw_text": text_payloads[0] if text_payloads else ""}

            return {
                "status": "success",
                "verdict": "SEAL",
                "bridge": bridge_name,
                "tool": tool_name,
                "result": inner,
                "raw_text": text_payloads[0] if text_payloads else "",
            }

        except Exception as exc:
            logger.error("gptr_bridge._call_mcp_tool failed: %s", exc)
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "bridge": bridge_name,
            }

    # ── High-level tool wrappers ──────────────────────────────────────

    async def deep_research(
        self,
        query: str,
    ) -> dict[str, Any]:
        """
        Multi-step research via gptr-mcp's deep_research + write_report.
        Chains two organ calls:
          1. deep_research  — research + scrape (returns research_id + context)
          2. write_report   — synthesizes a long-form report from the research
        30-90s, ~$0.40 Tavily credits, returns full report + sources.
        F2 epistemic tag: INTERPRETATION.

        Note: gptr-mcp's deep_research tool only accepts `query` as a
        parameter. MAX_ITERATIONS is controlled via the gptr-organ's
        .env file (default 2), not per-call.
        """
        # Step 1: Conduct the research (returns research_id + context + sources)
        result = await self._call_mcp_tool(
            "deep_research", {"query": query}, bridge_name="gptr_deep_research", timeout=300.0
        )
        if result.get("status") != "success":
            return result

        inner = result.get("result", {})
        research_id = inner.get("research_id")
        if not research_id:
            result["status"] = "error"
            result["verdict"] = "SABAR"
            result["error"] = "deep_research returned no research_id"
            return result

        # Step 2: Write the report from the research
        # Note: write_report only accepts `research_id`. `report_format` is
        # a parameter of the deep_research tool, not write_report.
        report_result = await self._call_mcp_tool(
            "write_report",
            {"research_id": research_id},
            bridge_name="gptr_write_report",
            timeout=120.0,
        )

        # Combine: enrich the deep_research result with the report
        result["epistemic_tag"] = "INTERPRETATION"  # F2
        result["query"] = query
        result["research_id"] = research_id
        result["context"] = inner.get("context")
        result["context_length_chars"] = len(inner.get("context", ""))
        result["sources"] = inner.get("sources", [])
        result["source_count"] = inner.get("source_count", len(inner.get("sources", [])))

        if report_result.get("status") == "success":
            report_inner = report_result.get("result", {})
            # write_report returns {"report": "..."} or similar
            report_text = (
                report_inner.get("report")
                or report_inner.get("content")
                or report_inner.get("text")
                or ""
            )
            result["report"] = report_text
            result["report_length_chars"] = len(report_text)
        else:
            # Research succeeded but report generation failed — still return context
            result["report"] = ""
            result["report_error"] = report_result.get("error", "unknown")
        return result

    async def quick_search(self, query: str) -> dict[str, Any]:
        """
        Fast web search w/ snippets via gptr-mcp's quick_search tool.
        5-10s, returns search results only.
        F2 epistemic tag: INTERPRETATION.
        """
        result = await self._call_mcp_tool(
            "quick_search", {"query": query}, bridge_name="gptr_quick_search", timeout=60.0
        )
        if result.get("status") == "success":
            inner = result.get("result", {})
            result["epistemic_tag"] = "INTERPRETATION"
            result["query"] = query
            result["search_results"] = inner.get("search_results", [])
            result["search_id"] = inner.get("search_id")
        return result

    async def write_report(
        self,
        research_id: str,
        report_format: str = "markdown",
    ) -> dict[str, Any]:
        """Generate report from previously-conducted research."""
        result = await self._call_mcp_tool(
            "write_report",
            {"research_id": research_id, "report_format": report_format},
            bridge_name="gptr_write_report",
            timeout=120.0,
        )
        if result.get("status") == "success":
            inner = result.get("result", {})
            result["epistemic_tag"] = "INTERPRETATION"
            result["report"] = inner.get("report")
        return result

    async def get_research_sources(self, research_id: str) -> dict[str, Any]:
        """Get the source URLs used in a research."""
        result = await self._call_mcp_tool(
            "get_research_sources",
            {"research_id": research_id},
            bridge_name="gptr_get_sources",
            timeout=30.0,
        )
        if result.get("status") == "success":
            inner = result.get("result", {})
            result["epistemic_tag"] = "OBSERVED"  # URL list, no LLM
            result["sources"] = inner.get("sources", [])
        return result

    async def get_research_context(self, research_id: str) -> dict[str, Any]:
        """Get the full research context (raw scraped content)."""
        result = await self._call_mcp_tool(
            "get_research_context",
            {"research_id": research_id},
            bridge_name="gptr_get_context",
            timeout=30.0,
        )
        if result.get("status") == "success":
            inner = result.get("result", {})
            result["epistemic_tag"] = "INTERPRETATION"  # AI-curated context
            result["context"] = inner.get("context")
        return result


async def _read_sse_response(sse_resp, timeout: float) -> str | None:
    """Read SSE stream until we get a JSON-RPC response (event with data: {...jsonrpc...})."""
    async for line in sse_resp.aiter_lines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data.startswith("{"):
                return data
        # Skip event:, id:, retry: lines and empty lines
    return None


gptr_bridge = GPTROrganBridge()
