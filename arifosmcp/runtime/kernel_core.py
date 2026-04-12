"""
arifOS KERNEL rCore — Unified Metabolic Orchestrator

444_KERNEL: Primary metabolic conductor that unifies:
  - INPUT Stage: Query normalization, session context assembly
  - ORCHESTRATE Stage: Classification, tool selection, governance enforcement
  - OUTPUT Stage: Envelope sealing, continuity state management

DITEMPA BUKAN DIBERI — Forged, Not Given

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │  KERNEL rCore (Unified)                                     │
    │                                                             │
    │  INPUT ─────► ORCHESTRATE ─────► OUTPUT                    │
    │     │              │               │                        │
    │  Normalize    Classify +      Seal +                     │
    │  Query        Route +          Continuity                  │
    │  Assemble     Invoke +         Update                     │
    │  Context      Govern                                   │
    └─────────────────────────────────────────────────────────────┘
"""

from __future__ import annotations

import logging
import time
from typing import Any

from core.kernel.pattern_registry import PatternRegistry
from core.kernel.pattern_selector import PatternSelector
from core.kernel.planner import Planner
from core.kernel.tool_registry import ToolContractRegistry
from core.kernel.role_registry import AgentRoleRegistry

logger = logging.getLogger(__name__)

# =============================================================================
# KERNEL rCore — Unified Metabolic Orchestrator
# =============================================================================


class KernelCore:
    """
    Unified KERNEL rCore that orchestrates the metabolic pipeline.

    Three stages:
    1. INPUT: Normalize query, assemble session context
    2. ORCHESTRATE: Classify, select tool, invoke with governance
    3. OUTPUT: Seal envelope, update continuity state
    """

    def __init__(self):
        self._tool_handlers: dict[str, Any] = {}
        self._governance_enabled: bool = True
        
        # New Kernel Primitives (30-day Roadmap)
        self.pattern_registry = PatternRegistry()
        self.pattern_selector = PatternSelector(self.pattern_registry)
        self.planner = Planner()
        self.tool_registry = ToolContractRegistry()
        self.role_registry = AgentRoleRegistry()

    # =============================================================================
    # INPUT Stage — Query Normalization & Context Assembly
    # =============================================================================

    async def input_stage(
        self,
        query: str | None = None,
        session_id: str | None = None,
        actor_id: str | None = None,
        intent: str | None = None,
        auth_context: dict | None = None,
        risk_tier: str = "medium",
        dry_run: bool = True,
        allow_execution: bool = False,
        caller_context: dict | None = None,
        payload: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        INPUT Stage: Normalize and assemble context.

        From arifos_kernel query normalization + session assembly.
        """
        payload = dict(payload or {})
        payload.update(kwargs)

        # Normalize query
        if query:
            payload.setdefault("query", query)
        if session_id:
            payload.setdefault("session_id", session_id)
        if actor_id:
            payload.setdefault("actor_id", actor_id)
        if intent:
            payload.setdefault("intent", intent)
        if auth_context:
            payload.setdefault("auth_context", auth_context)
        if caller_context:
            payload.setdefault("caller_context", caller_context)

        effective_query = payload.get("query") or query or ""
        effective_actor = str(payload.get("actor_id") or actor_id or "anonymous").strip().lower()

        # Pattern selection
        selected_pattern = self.pattern_selector.select({"query": effective_query, **payload})

        context = {
            "payload": payload,
            "query": effective_query,
            "actor_id": effective_actor,
            "session_id": session_id,
            "risk_tier": risk_tier,
            "dry_run": dry_run,
            "allow_execution": allow_execution,
            "intent": intent,
            "auth_context": auth_context or {},
            "selected_pattern": selected_pattern,
            "kernel_primitives": {
                "planner": self.planner,
                "tool_registry": self.tool_registry,
                "role_registry": self.role_registry,
            }
        }

        logger.info(
            f"KERNEL INPUT: query='{effective_query[:50]}...' actor={effective_actor} session={session_id} pattern={selected_pattern}"
        )

        return context

    # ═══════════════════════════════════════════════════════════════════════════
    # ORCHESTRATE Stage — Classification, Routing, Governance
    # ═══════════════════════════════════════════════════════════════════════════

    async def orchestrate_stage(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        ORCHESTRATE Stage: Classify query, select tool, invoke with governance.

        From kernel_router.process_query + classify_and_route.
        """
        from arifosmcp.runtime.governance_enforcer import classify_and_route
        from arifosmcp.runtime.tools_hardened_dispatch import get_tool_handler

        query = context.get("query", "")
        actor_id = context.get("actor_id", "anonymous")
        session_id = context.get("session_id")

        # Classify query
        routing_result = await classify_and_route(
            query=query,
            actor_id=actor_id,
            session_id=session_id,
            context=context,
        )

        # Extract tool to invoke
        tool_name = routing_result.get("tool_name", "arifos_mind")

        # Get handler
        handler = get_tool_handler(tool_name)
        if not handler:
            logger.warning(
                f"KERNEL ORCHESTRATE: No handler for tool '{tool_name}', defaulting to arifos_mind"
            )
            handler = get_tool_handler("arifos_mind")

        # Invoke tool
        if handler:
            tool_result = await self._invoke_with_governance(
                handler=handler,
                tool_name=tool_name,
                context=context,
            )
        else:
            tool_result = {"ok": False, "error": f"No handler for tool: {tool_name}"}

        logger.info(f"KERNEL ORCHESTRATE: tool={tool_name} ok={tool_result.get('ok', False)}")

        return {
            "ok": routing_result.get("ok", True),
            "tool_name": tool_name,
            "tool_result": tool_result,
            "routing_result": routing_result,
            "context": context,
        }

    async def _invoke_with_governance(
        self,
        handler: Any,
        tool_name: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Invoke tool handler with governance context."""
        try:
            # Build invoke kwargs from context
            kwargs = {
                "query": context.get("query"),
                "session_id": context.get("session_id"),
                "risk_tier": context.get("risk_tier", "medium"),
                "dry_run": context.get("dry_run", True),
                "allow_execution": context.get("allow_execution", False),
                "platform": context.get("platform", "unknown"),
            }

            # Add tool-specific params
            if tool_name == "arifos_init":
                kwargs["actor_id"] = context.get("actor_id")
                kwargs["intent"] = context.get("intent")
            elif tool_name == "arifos_sense":
                kwargs["mode"] = context.get("payload", {}).get("mode", "governed")
            elif tool_name == "arifos_mind":
                kwargs["context"] = context.get("payload", {}).get("context")

            # Invoke
            result = await handler(**kwargs)

            if hasattr(result, "__dict__"):
                return result.__dict__
            return result or {"ok": True}

        except Exception as e:
            logger.error(f"KERNEL ORCHESTRATE: Tool invocation failed: {e}")
            return {"ok": False, "error": str(e)}

    # ═══════════════════════════════════════════════════════════════════════════
    # OUTPUT Stage — Envelope Sealing & Continuity Update
    # ═══════════════════════════════════════════════════════════════════════════

    async def output_stage(
        self,
        tool_result: dict[str, Any],
        tool_name: str,
        context: dict[str, Any],
        routing_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        OUTPUT Stage: Seal envelope and update continuity state.

        From continuity_contract.seal_runtime_envelope.
        """
        from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
        from arifosmcp.runtime.models import RuntimeEnvelope, Stage

        session_id = context.get("session_id")

        # Build envelope from tool result
        if isinstance(tool_result, RuntimeEnvelope):
            envelope = tool_result
        else:
            # Wrap raw result in envelope
            envelope = RuntimeEnvelope(
                ok=tool_result.get("ok", True),
                tool=tool_name,
                canonical_tool_name=tool_name,
                stage=Stage.ROUTER_444.value,
                session_id=session_id,
                payload=tool_result,
            )

        # Seal with continuity
        sealed = seal_runtime_envelope(
            envelope=envelope,
            tool_id=tool_name,
            session_id=session_id,
        )

        logger.info(f"KERNEL OUTPUT: sealed={getattr(sealed, 'ok', False)} session={session_id}")

        if isinstance(sealed, RuntimeEnvelope):
            return sealed.__dict__
        return sealed

    # ═══════════════════════════════════════════════════════════════════════════
    # UNIFIED execute — Full INPUT → ORCHESTRATE → OUTPUT pipeline
    # ═══════════════════════════════════════════════════════════════════════════

    async def execute(
        self,
        query: str | None = None,
        session_id: str | None = None,
        actor_id: str | None = None,
        intent: str | None = None,
        auth_context: dict | None = None,
        risk_tier: str = "medium",
        dry_run: bool = True,
        allow_execution: bool = False,
        caller_context: dict | None = None,
        payload: dict[str, Any] | None = None,
        platform: str = "unknown",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Execute full KERNEL pipeline: INPUT → ORCHESTRATE → OUTPUT.
        Unified entry point: INPUT → ORCHESTRATE → OUTPUT
        
        Hardened Fix 3: Returns READY | HOLD | BLOCKED contract.
        """
        # INPUT: Normalize and assemble
        context = await self.input_stage(
            query=query,
            session_id=session_id,
            actor_id=actor_id,
            intent=intent,
            auth_context=auth_context,
            risk_tier=risk_tier,
            dry_run=dry_run,
            allow_execution=allow_execution,
            caller_context=caller_context,
            payload=payload,
            platform=platform,
            **kwargs,
        )

        # ORCHESTRATE: Classify, route, invoke
        orchestrate_result = await self.orchestrate_stage(context)

        tool_name = orchestrate_result.get("tool_name", "arifos_mind")
        tool_result = orchestrate_result.get("tool_result", {})
        routing_result = orchestrate_result.get("routing_result", {})

        # OUTPUT: Seal and update continuity
        final_result = await self.output_stage(
            tool_result=tool_result,
            tool_name=tool_name,
            context=context,
            routing_result=routing_result,
        )
        
        # ── V2 Kernel Contract Hardening (Fix 3) ───────────────────────────
        # Ensure top-level contract is binary/trinary: READY | HOLD | BLOCKED
        verdict = final_result.get("verdict", "SABAR")
        status = "READY"
        if verdict == "VOID":
            status = "BLOCKED"
        elif verdict in ("HOLD", "SABAR", "PARTIAL"):
            status = "HOLD"
            
        final_result["kernel_status"] = status
        final_result["handoff_spec"] = {
            "next_stage": routing_result.get("next_stage", "333_MIND"),
            "required_inputs": routing_result.get("required_inputs", []),
            "release_condition": routing_result.get("release_condition", "governance_seal")
        }
        # ───────────────────────────────────────────────────────────────────

        return final_result


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton instance for convenience
# ═══════════════════════════════════════════════════════════════════════════════

_kernel_core: KernelCore | None = None


def get_kernel_core() -> KernelCore:
    """Get singleton KERNEL rCore instance."""
    global _kernel_core
    if _kernel_core is None:
        _kernel_core = KernelCore()
    return _kernel_core


async def kernel_execute(
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    intent: str | None = None,
    auth_context: dict | None = None,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    payload: dict[str, Any] | None = None,
    platform: str = "unknown",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Convenience function for KERNEL rCore execution.

    Unified entry point: INPUT → ORCHESTRATE → OUTPUT
    """
    core = get_kernel_core()
    return await core.execute(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        auth_context=auth_context,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        payload=payload,
        platform=platform,
        **kwargs,
    )
