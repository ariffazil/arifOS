"""
VersionGate — Phased Rollout Filter
════════════════════════════════════

Enables gradual rollout of new tool versions by percentage or actor list.
"""
from __future__ import annotations

import hashlib
import logging
from collections.abc import Sequence
from typing import Any

from fastmcp.server.transforms import Transform
from fastmcp.tools.tool import Tool

logger = logging.getLogger(__name__)


class VersionGate(Transform):
    """
    Filters tools based on a phased rollout gate.

    - percentage: 0–100 roll-out (stable per actor_id hash)
    - actors: explicit allow-list
    - default_enabled: whether untagged tools pass through
    """

    def __init__(
        self,
        actor_id: str | None = None,
        percentage: float = 100.0,
        actors: list[str] | None = None,
        default_enabled: bool = True,
    ) -> None:
        self.actor_id = actor_id or "anonymous"
        self.percentage = max(0.0, min(100.0, percentage))
        self.actors = set(actors or [])
        self.default_enabled = default_enabled

    def __repr__(self) -> str:
        return (
            f"VersionGate(actor={self.actor_id!r}, pct={self.percentage}, "
            f"actors={len(self.actors)})"
        )

    def _actor_in_rollout(self, tool_name: str) -> bool:
        if self.actor_id in self.actors:
            return True
        digest = hashlib.sha256(f"{tool_name}:{self.actor_id}".encode()).hexdigest()
        bucket = int(digest[:8], 16) % 100
        return bucket < self.percentage

    def _allowed(self, tool: Tool) -> bool:
        meta = tool.meta or {}
        arifos_meta = meta.get("arifos") if isinstance(meta.get("arifos"), dict) else {}
        gate = arifos_meta.get("version_gate")
        if gate is None:
            return self.default_enabled
        if gate == "all":
            return True
        if gate == "none":
            return False
        if isinstance(gate, (int, float)):
            return self._actor_in_rollout(tool.name)
        return self.default_enabled

    async def list_tools(self, tools: Sequence[Tool]) -> Sequence[Tool]:
        filtered = [t for t in tools if self._allowed(t)]
        logger.debug(
            f"[VersionGate] {self.actor_id}: {len(filtered)}/{len(tools)} tools in gate"
        )
        return filtered

    async def get_tool(
        self, name: str, call_next: Any, *, version: Any = None
    ) -> Tool | None:
        tool = await call_next(name, version=version)
        if tool is None:
            return None
        if not self._allowed(tool):
            logger.debug(f"[VersionGate] Blocked '{name}' for actor '{self.actor_id}'")
            return None
        return tool
