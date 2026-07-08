"""
kernel.py — Kernel: the main entry point for the arifOS SDK.

The Kernel class is what most agents use. It holds a single MCP
client and provides convenient async methods for the 4 guards.
"""

from __future__ import annotations

from typing import Any

from arifos.actor import Actor
from arifos.client import ArifOSMCPClient
from arifos.decision import Decision
from arifos.guards import posttool, prethink, pretool
from arifos.intent import Intent
from arifos.seal import seal as _seal


class Kernel:
    """
    The arifOS SDK Kernel — main entry point.

    Holds a single MCP client and a decision history. Use the
    high-level methods to drive the 4-guard cognition firewall.

    Usage:
        kernel = Kernel(actor=Actor(actor_id="arif"))

        decision = await kernel.prethink(
            intent=Intent(
                action="edit_file",
                action_class="MUTATE_LOCAL",
                lane="MUTATE",
                blast_radius=BlastRadius.LOCAL,
                actor=kernel.actor,
            )
        )

        if decision.is_holding():
            raise RuntimeError("888 HOLD")

        tool_decision = await kernel.pretool(
            "edit_file",
            {"path": "/tmp/test"},
            prior_decision=decision,
        )
    """

    def __init__(
        self,
        base_url: str = "https://arifos.arif-fazil.com",
        actor: Actor | None = None,
        fail_closed_on_kernel_unavailable: bool = True,
    ):
        self.actor = actor or Actor(actor_id="arif", actor_type="sovereign")
        self.client = ArifOSMCPClient(base_url=base_url, actor=self.actor)
        self.fail_closed = fail_closed_on_kernel_unavailable
        self.history: list[Decision] = []

    async def prethink(self, intent: Intent) -> Decision:
        """Run prethink. Appends to history."""
        decision = await prethink(intent=intent, client=self.client)
        self.history.append(decision)
        return decision

    async def pretool(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        prior_decision: Decision,
    ) -> Decision:
        """Run pretool. Appends to history."""
        decision = await pretool(
            tool_name=tool_name,
            tool_args=tool_args,
            prior_decision=prior_decision,
            client=self.client,
        )
        self.history.append(decision)
        return decision

    async def posttool(
        self,
        tool_name: str,
        tool_result: Any,
        prior_decision: Decision,
        confidence: float | None = None,
        source: str | None = None,
    ) -> Decision:
        """Run posttool. Appends to history."""
        decision = await posttool(
            tool_name=tool_name,
            tool_result=tool_result,
            prior_decision=prior_decision,
            confidence=confidence,
            source=source,
            client=self.client,
        )
        self.history.append(decision)
        return decision

    async def seal(self, final_output: Any) -> Decision:
        """Seal the run. Returns the sealed Decision."""
        return await _seal(
            final_output=final_output,
            decision_history=self.history,
            client=self.client,
        )
