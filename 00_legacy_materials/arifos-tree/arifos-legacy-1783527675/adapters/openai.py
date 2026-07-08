"""
arifos.adapters.openai — OpenAI Agents SDK adapter.

Wraps an OpenAI Agent with the arifOS cognition firewall. The 4
guards (prethink, pretool, posttool, seal) are wired into the
agent's tool execution and run lifecycle.

Imports are lazy to avoid hard dependency on openai-agents unless
the adapter is used.

Install:
    pip install "arifos[openai]"

Usage:
    from agents import Agent, Runner, function_tool
    from arifos.adapters.openai import ArifKernel, ARIFOS_PRETHINK_TOOL

    @function_tool
    def read_file(path: str) -> str:
        return open(path).read()

    agent = Agent(
        name="CodexCoder",
        instructions="You are a code review assistant.",
        tools=[read_file],
    )

    kernel = ArifKernel()
    wrapped = kernel.wrap(agent)
    result = await Runner.run(wrapped, "Read /etc/hostname")
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Awaitable, Callable

from arifos.actor import Actor
from arifos.client import ArifOSMCPClient
from arifos.decision import CognitionLane, Decision
from arifos.exceptions import (
    ArifHold,
    ArifSealMissing,
)
from arifos.guards import (
    posttool,
    pretool,
    seal as arifos_seal,
)

logger = logging.getLogger(__name__)


# The prethink tool schema — model MUST call this before any other tool.
ARIFOS_PRETHINK_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "_arifos_prethink",
        "description": (
            "MANDATORY cognition-time gate. MUST be called before any "
            "other tool. Declares the agent's intent and proposed action. "
            "Returns the kernel's verdict (ALLOW/DENY/HOLD/DEGRADED). "
            "The agent must not proceed without verdict=ALLOW or DEGRADED."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action the agent is about to perform (e.g. 'edit_file', 'publish').",
                },
                "action_class": {
                    "type": "string",
                    "enum": [
                        "OBSERVE",
                        "COMPUTE",
                        "PROPOSE",
                        "MUTATE_LOCAL",
                        "MUTATE_EXTERNAL",
                        "DEPLOY",
                        "SPEND",
                        "PUBLISH",
                        "DELETE",
                        "SIGN",
                        "GRANT_ACCESS",
                        "CREDENTIAL_CHANGE",
                        "CONSTITUTION_CHANGE",
                    ],
                    "description": "Action class for F1-F13 floor checks.",
                },
                "lane": {
                    "type": "string",
                    "enum": ["OBSERVE", "PLAN", "MUTATE", "EXECUTE"],
                    "description": "Cognition lane (read-only / reasoning / local mutation / cross-system).",
                },
                "blast_radius": {
                    "type": "string",
                    "enum": ["NONE", "LOCAL", "SESSION", "FEDERATION", "EXTERNAL"],
                },
                "proposed_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "reason": {"type": "string", "description": "Human-readable explanation."},
            },
            "required": ["action", "action_class", "lane", "blast_radius", "reason"],
            "additionalProperties": False,
        },
        "strict": True,
    },
}


class _DecisionHistory:
    """Tracks decisions across an agent run."""

    def __init__(self) -> None:
        self.decisions: list[Decision] = []

    def add(self, decision: Decision) -> None:
        self.decisions.append(decision)

    def last(self) -> Decision | None:
        return self.decisions[-1] if self.decisions else None

    def all(self) -> list[Decision]:
        return list(self.decisions)


class ArifKernel:
    """
    Wraps an OpenAI Agent with the arifOS cognition firewall.

    Injects:
    1. The _arifos_prethink tool (forced call before any other tool)
    2. pretool + posttool guards (every tool call)
    3. seal at run end
    """

    def __init__(
        self,
        base_url: str = "https://arifos.arif-fazil.com",
        actor: Actor | None = None,
    ):
        self.actor = actor or Actor(actor_id="arif", actor_type="sovereign")
        self.client = ArifOSMCPClient(base_url=base_url, actor=self.actor)

    def wrap(self, agent: Any) -> Any:
        """
        Wrap an OpenAI Agent with the 4 guards.

        Returns the wrapped agent (original is not mutated).
        """
        history = _DecisionHistory()

        # 1. Inject the prethink tool
        original_tools = list(getattr(agent, "tools", []))
        agent.tools = [ARIFOS_PRETHINK_TOOL] + original_tools

        # 2. Wrap tool execution
        original_execute = getattr(agent, "_execute_tool_call", None) or getattr(
            agent, "execute_tool_call", None
        )
        if original_execute is not None:
            agent._execute_tool_call = self._wrap_execute(original_execute, history)

        # 3. Wrap the run for the seal
        original_run = getattr(agent, "run", None) or getattr(agent, "__call__", None)
        if original_run is not None:
            agent.run = self._wrap_run(original_run, history)

        return agent

    def _wrap_execute(
        self,
        original: Callable[..., Awaitable[Any]],
        history: _DecisionHistory,
    ) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(original)
        async def wrapper(*args, **kwargs):
            tool_name = kwargs.get("tool_name") or (args[0] if args else "unknown")
            tool_args = kwargs.get("tool_args") or kwargs.get("arguments") or {}

            last = history.last()
            if last is None and tool_name != "_arifos_prethink":
                # No prethink yet — refuse
                raise ArifHold(
                    Decision(
                        verdict="HOLD",
                        cognition_lane=CognitionLane.OBSERVE,
                        reasons=[
                            f"F8 LAW: tool {tool_name!r} called before _arifos_prethink. "
                            "No agent may form an executable plan until prethink returns ALLOW."
                        ],
                        required_human_ack=True,
                    )
                )

            # PRETOOL guard
            if tool_name != "_arifos_prethink" and last is not None:
                decision = await pretool(
                    tool_name=tool_name,
                    tool_args=tool_args,
                    prior_decision=last,
                    client=self.client,
                )
                history.add(decision)

            # Execute
            result = await original(*args, **kwargs)

            # POSTTOOL guard
            if tool_name != "_arifos_prethink":
                confidence = None
                source = None
                if isinstance(result, dict):
                    confidence = result.get("confidence")
                    source = result.get("source") or result.get("url")

                post_decision = await posttool(
                    tool_name=tool_name,
                    tool_result=result,
                    prior_decision=last
                    if last
                    else Decision(verdict="ALLOW", cognition_lane=CognitionLane.OBSERVE),
                    confidence=confidence,
                    source=source,
                    client=self.client,
                )
                history.add(post_decision)
            else:
                # Record the prethink result
                if isinstance(result, dict):
                    try:
                        decision = Decision(**result)
                        history.add(decision)
                    except Exception:
                        logger.warning("Could not parse prethink result")

            return result

        return wrapper

    def _wrap_run(
        self,
        original: Callable[..., Awaitable[Any]],
        history: _DecisionHistory,
    ) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(original)
        async def wrapper(*args, **kwargs):
            result = await original(*args, **kwargs)
            try:
                seal = await arifos_seal(
                    final_output=result,
                    decision_history=history.all(),
                    client=self.client,
                )
                if isinstance(result, dict):
                    result["_arifos_seal"] = seal.to_envelope()
                else:
                    setattr(result, "_arifos_seal", seal)
            except ArifSealMissing as exc:
                logger.error(f"arifOS seal missing: {exc}")
                raise
            return result

        return wrapper


__all__ = ["ArifKernel", "ARIFOS_PRETHINK_TOOL"]
