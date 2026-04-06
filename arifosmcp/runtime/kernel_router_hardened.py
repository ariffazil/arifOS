"""
arifOS Hardened Kernel Router (444_ROUTER)
═══════════════════════════════════════════════════════════════════════════════

FIX: Proper sequencing to prevent HOLD/VOID bypass

CORRECT ORDER:
1. Classify query (Class A/B/C)
2. If Class A → Model responds directly (no tool)
3. If Class B/C → Execute tool
4. Evaluate verdict
5. IF HOLD/VOID → HARD STOP (no model call)
6. IF SEAL/PASS → Call model
7. Return response

CRITICAL: Model is NEVER called before verdict evaluation.

Author: 888_VALIDATOR
Version: 2026.04.06-HARDENED
"""

from __future__ import annotations

from typing import Any, Optional

from arifosmcp.runtime.governance_enforcer import (
    QueryClass,
    classify_and_route,
    enforce_tool_verdict,
    get_enforcer,
)
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


class HardenedKernelRouter:
    """
    Hardened 444_ROUTER with strict governance enforcement.
    
    PREVENTS: Model being called before verdict evaluation
    ENSURES: HOLD/VOID is terminal (no bypass)
    """
    
    def __init__(self):
        self.enforcer = get_enforcer()
    
    async def route(
        self,
        query: str,
        actor_id: str = "anonymous",
        session_id: Optional[str] = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Hardened routing with strict Class A/B/C separation.
        
        This is the ONLY entry point for query processing.
        All other paths must flow through here.
        """
        context = context or {}
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 1: CLASSIFY QUERY (Before any tool invocation)
        # ═══════════════════════════════════════════════════════════════════════
        query_class, requires_tool = classify_and_route(query, context)
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 2: CLASS A — INFORMATIONAL (No state change)
        # Model may respond directly. No vault write. No seal required.
        # ═══════════════════════════════════════════════════════════════════════
        if query_class == QueryClass.INFORMATIONAL:
            # For informational queries, we can optionally still run through
            # sense/mind for quality, but it's not required for governance
            return {
                "ok": True,
                "query_class": QueryClass.INFORMATIONAL.value,
                "governance_required": False,
                "note": "Informational query — model response permitted without seal",
                "proceed_to_model": True,
            }
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 3: CLASS B/C — GOVERNED/CRITICAL (State mutation)
        # Must pass full F1-F13. Requires tool invocation.
        # ═══════════════════════════════════════════════════════════════════════
        
        # Determine which tool to invoke based on query
        tool_name = self._select_tool(query_class, query, context)
        
        # Execute tool through governance layer
        tool_result = await self._invoke_tool_with_governance(
            tool_name=tool_name,
            query=query,
            actor_id=actor_id,
            session_id=session_id,
            context=context,
        )
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 4: EVALUATE VERDICT (HARD STOP if HOLD/VOID)
        # ═══════════════════════════════════════════════════════════════════════
        allowed, response = enforce_tool_verdict(
            tool_name=tool_name,
            envelope=tool_result,
            query=query,
            actor_id=actor_id,
        )
        
        if not allowed:
            # HARD STOP: Return block response, DO NOT CALL MODEL
            return {
                "ok": False,
                "query_class": query_class.value,
                "governance_block": True,
                "tool_result": response,
                "proceed_to_model": False,
                "audit_note": "HARD STOP enforced — model not invoked",
            }
        
        # ═══════════════════════════════════════════════════════════════════════
        # STEP 5: ALLOWED — Call model (only after SEAL/PASS)
        # ═══════════════════════════════════════════════════════════════════════
        return {
            "ok": True,
            "query_class": query_class.value,
            "governance_required": True,
            "governance_passed": True,
            "tool_result": tool_result,
            "proceed_to_model": True,
            "audit_note": "SEAL/PASS received — model invocation permitted",
        }
    
    def _select_tool(
        self,
        query_class: QueryClass,
        query: str,
        context: dict[str, Any],
    ) -> str:
        """Select appropriate tool based on query class and content."""
        
        query_lower = query.lower()
        
        # Session/init queries
        if any(kw in query_lower for kw in ["init", "session", "anchor", "start"]):
            return "arifos.init"
        
        # Memory queries
        if any(kw in query_lower for kw in ["remember", "recall", "memory", "context"]):
            return "arifos.memory"
        
        # Execution/forge queries
        if any(kw in query_lower for kw in ["execute", "run", "deploy", "forge", "spawn"]):
            return "arifos.forge"
        
        # Seal/vault queries
        if any(kw in query_lower for kw in ["seal", "commit", "vault", "ledger"]):
            return "arifos.vault"
        
        # Reasoning/mind queries
        if any(kw in query_lower for kw in ["reason", "think", "analyze", "mind"]):
            return "arifos.mind"
        
        # Safety/heart queries
        if any(kw in query_lower for kw in ["safe", "risk", "harm", "heart"]):
            return "arifos.heart"
        
        # Operations/cost queries
        if any(kw in query_lower for kw in ["cost", "ops", "estimate", "feasible"]):
            return "arifos.ops"
        
        # Reality/sense queries
        if any(kw in query_lower for kw in ["sense", "ground", "verify", "reality"]):
            return "arifos.sense"
        
        # Judge queries (default for critical)
        if query_class == QueryClass.CRITICAL:
            return "arifos.judge"
        
        # Route as default
        return "arifos.route"
    
    async def _invoke_tool_with_governance(
        self,
        tool_name: str,
        query: str,
        actor_id: str,
        session_id: Optional[str],
        context: dict[str, Any],
    ) -> RuntimeEnvelope:
        """Invoke tool with full ToM requirements."""
        
        # Import tools dynamically to avoid circular deps
        from arifosmcp.runtime.tools import CANONICAL_TOOL_HANDLERS
        
        handler = CANONICAL_TOOL_HANDLERS.get(tool_name)
        if not handler:
            # Return error envelope if tool not found
            return RuntimeEnvelope(
                tool=tool_name,
                stage="444_ROUTER",
                status=RuntimeStatus.ERROR,
                verdict=Verdict.VOID,
                session_id=session_id,
                payload={
                    "ok": False,
                    "error": f"Tool {tool_name} not found",
                    "tom_violation": False,
                }
            )
        
        # Build payload with ToM fields if not present
        payload = context.get("payload", {})
        
        # Ensure minimal ToM fields for Class B/C
        if "declared_intent" not in payload:
            payload["declared_intent"] = query[:200]  # Truncate for intent
        if "confidence_self_estimate" not in payload:
            payload["confidence_self_estimate"] = 0.7
        if "context_assumptions" not in payload:
            payload["context_assumptions"] = ["User wants to accomplish task"]
        
        # Call the tool
        import asyncio
        result = await handler(
            mode=context.get("mode", "default"),
            payload=payload,
            session_id=session_id,
            risk_tier=context.get("risk_tier", "medium"),
            dry_run=context.get("dry_run", True),
        )
        
        return result


# Global router instance
_router: Optional[HardenedKernelRouter] = None


def get_router() -> HardenedKernelRouter:
    """Get or create global hardened router."""
    global _router
    if _router is None:
        _router = HardenedKernelRouter()
    return _router


async def process_query(
    query: str,
    actor_id: str = "anonymous",
    session_id: Optional[str] = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    MAIN ENTRY POINT for query processing.
    
    This is the ONLY way to process queries with proper governance.
    All other paths are considered bypass attempts.
    """
    router = get_router()
    return await router.route(query, actor_id, session_id, context)


__all__ = [
    "HardenedKernelRouter",
    "get_router",
    "process_query",
]
