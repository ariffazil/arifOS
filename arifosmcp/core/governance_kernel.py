"""
arifosmcp.core.governance_kernel — Constitutional Governance Kernel
════════════════════════════════════════════════════════════════════

Wraps ALL tool executions with F1–F13 interceptors.
This is the sovereign boundary layer — no tool executes without passing through here.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from arifosmcp.core.floors import check_floors, get_floor_status
from arifosmcp.constitutional_map import TrinityLane

logger = logging.getLogger(__name__)


VERDICT_SEAL = "SEAL"
VERDICT_HOLD = "HOLD"
VERDICT_VOID = "VOID"


class GovernanceKernel:
    """
    Constitutional governance wrapper for all tool executions.

    Usage:
        kernel = GovernanceKernel()
        result = kernel.execute_tool("arif_session_init", params, actor_id)
    """

    def __init__(self):
        self.invocation_count = 0
        self.hold_count = 0
        self.void_count = 0

    def execute_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
        actor_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a tool through constitutional governance.

        Returns dict with:
            - verdict: SEAL | HOLD | VOID
            - result: tool output (empty if HOLD/VOID)
            - meta: governance metadata
        """
        self.invocation_count += 1

        floor_check = check_floors(tool_name, params, actor_id)
        verdict = floor_check["verdict"]

        if verdict == VERDICT_VOID:
            self.void_count += 1
            logger.critical(f"VOID: {tool_name} — {floor_check['reason']}")
            return {
                "verdict": VERDICT_VOID,
                "tool": tool_name,
                "result": {},
                "meta": {
                    "reason": floor_check["reason"],
                    "failed_floors": floor_check["failed_floors"],
                    "actor_id": actor_id,
                },
            }

        if verdict == VERDICT_HOLD:
            self.hold_count += 1
            logger.warning(f"HOLD: {tool_name} — {floor_check['reason']}")
            return {
                "verdict": VERDICT_HOLD,
                "tool": tool_name,
                "result": {},
                "meta": {
                    "reason": floor_check["reason"],
                    "failed_floors": floor_check["failed_floors"],
                    "actor_id": actor_id,
                },
            }

        return {
            "verdict": VERDICT_SEAL,
            "tool": tool_name,
            "result": {},
            "meta": {
                "reason": "All constitutional floors clear",
                "failed_floors": [],
                "actor_id": actor_id,
            },
        }

    def get_metrics(self) -> dict[str, Any]:
        """Return governance kernel metrics."""
        total = self.invocation_count
        return {
            "total_invocations": total,
            "seal_count": total - self.hold_count - self.void_count,
            "hold_count": self.hold_count,
            "void_count": self.void_count,
            "hold_rate": self.hold_count / total if total > 0 else 0,
            "void_rate": self.void_count / total if total > 0 else 0,
        }


_kernel = GovernanceKernel()


def get_kernel() -> GovernanceKernel:
    """Get the singleton kernel instance."""
    return _kernel


def execute_through_kernel(
    tool_name: str,
    params: dict[str, Any],
    actor_id: str | None = None,
) -> dict[str, Any]:
    """Convenience wrapper around the singleton kernel."""
    return _kernel.execute_tool(tool_name, params, actor_id)
