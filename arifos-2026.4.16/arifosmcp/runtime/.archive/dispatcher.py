"""
arifOS Tool Dispatcher
=====================

SINGLE dispatch point for all tool calls.

Replaces:
- arifosmcp/runtime/tools.py (dispatch logic)
- arifosmcp/runtime/tools_hardened_dispatch.py (hardened dispatch map)

Status: PHASE 2 - Single dispatcher
Branch: refactor/v2.0-abi
"""

from __future__ import annotations

import logging
import time
from typing import Any

from core.shared.types import (
    Verdict,
    RuntimeStatus,
    RuntimeEnvelope,
)
from arifosmcp.tools.base import ToolRegistry

logger = logging.getLogger(__name__)


class DispatchResult:
    """Result of a tool dispatch."""

    def __init__(
        self,
        envelope: RuntimeEnvelope,
        cached: bool = False,
        from_cache: bool = False,
    ):
        self.envelope = envelope
        self.cached = cached
        self.from_cache = from_cache


class ToolDispatcher:
    """
    Single dispatch point for all arifOS tool calls.

    Responsibilities:
    1. Look up tool in registry
    2. Validate request against ABI schema
    3. Check constitutional floors
    4. Execute tool
    5. Return RuntimeEnvelope

    Usage:
        dispatcher = ToolDispatcher()
        result = await dispatcher.dispatch(
            tool_name="init_anchor",
            payload={"actor_id": "my_agent"},
            session_id="..."
        )
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._dispatch_count = 0

    async def dispatch(
        self,
        tool_name: str,
        payload: dict[str, Any],
        session_id: str | None = None,
        auth_context: dict[str, Any] | None = None,
        dry_run: bool | None = None,
    ) -> RuntimeEnvelope:
        """
        Dispatch a tool call.

        Args:
            tool_name: Name of the tool to call
            payload: Request payload
            session_id: Optional session ID
            auth_context: Optional authentication context
            dry_run: Override dry_run from payload

        Returns:
            RuntimeEnvelope with result
        """
        start_time = time.time()
        self._dispatch_count += 1

        # 1. Lookup tool
        tool = ToolRegistry.get(tool_name)
        if not tool:
            return self._error_envelope(
                tool_name=tool_name,
                message=f"Unknown tool: {tool_name}",
                session_id=session_id,
                start_time=start_time,
            )

        self.logger.info(
            f"[DISPATCH] {tool_name} (stage: {tool.stage}, floors: {tool.floors})"
        )

        # 2. Run tool with full governance
        try:
            # Override dry_run if specified
            dispatch_payload = dict(payload)
            if dry_run is not None:
                dispatch_payload["dry_run"] = dry_run

            result = await tool.run(
                payload=dispatch_payload,
                session_id=session_id,
                auth_context=auth_context,
            )

            # Add latency if not already set
            if result.latency_ms == 0:
                result.latency_ms = (time.time() - start_time) * 1000

            self.logger.info(
                f"[DISPATCH] {tool_name} → verdict={result.verdict}, "
                f"status={result.status}, latency={result.latency_ms:.1f}ms"
            )

            return result

        except Exception as e:
            self.logger.exception(f"[DISPATCH] Error dispatching {tool_name}")
            return self._error_envelope(
                tool_name=tool_name,
                message=f"Execution error: {str(e)}",
                session_id=session_id,
                start_time=start_time,
            )

    async def dispatch_batch(
        self,
        calls: list[dict[str, Any]],
        session_id: str | None = None,
        auth_context: dict[str, Any] | None = None,
    ) -> list[RuntimeEnvelope]:
        """
        Dispatch multiple tool calls.

        Args:
            calls: List of {tool_name, payload} dicts
            session_id: Session ID for all calls
            auth_context: Auth context for all calls

        Returns:
            List of RuntimeEnvelopes in same order as calls
        """
        results = []
        for call in calls:
            result = await self.dispatch(
                tool_name=call.get("tool_name", call.get("tool")),
                payload=call.get("payload", call.get("arguments", {})),
                session_id=session_id,
                auth_context=auth_context,
                dry_run=call.get("dry_run"),
            )
            results.append(result)
        return results

    def _error_envelope(
        self,
        tool_name: str,
        message: str,
        session_id: str | None,
        start_time: float,
    ) -> RuntimeEnvelope:
        """Create an error envelope."""
        return RuntimeEnvelope(
            tool=tool_name,
            stage="ERROR",
            status=RuntimeStatus.ERROR,
            verdict=Verdict.VOID,
            payload={"error": message},
            session_id=session_id,
            errors=[{"code": "DISPATCH_ERROR", "message": message}],
            latency_ms=(time.time() - start_time) * 1000,
        )

    @property
    def dispatch_count(self) -> int:
        """Total number of dispatches."""
        return self._dispatch_count

    def stats(self) -> dict[str, Any]:
        """Return dispatcher statistics."""
        return {
            "dispatch_count": self._dispatch_count,
            "registered_tools": len(ToolRegistry.list_tools()),
            "version": "1.0.0",
        }


# Global dispatcher instance
dispatcher = ToolDispatcher()


async def dispatch_tool(
    tool_name: str,
    payload: dict[str, Any],
    session_id: str | None = None,
    auth_context: dict[str, Any] | None = None,
    dry_run: bool | None = None,
) -> RuntimeEnvelope:
    """
    Convenience function to dispatch a tool call.

    This is the main entry point for tool execution.
    """
    return await dispatcher.dispatch(
        tool_name=tool_name,
        payload=payload,
        session_id=session_id,
        auth_context=auth_context,
        dry_run=dry_run,
    )


__all__ = [
    "DispatchResult",
    "ToolDispatcher",
    "dispatcher",
    "dispatch_tool",
]
