"""
arifOS KERNEL rCore — Unified Metabolic Orchestrator

444_KERNEL: Primary metabolic conductor that unifies:
  - INPUT Stage: Query normalization, session context assembly
  - ORCHESTRATE Stage: Classification, tool selection, governance enforcement
  - OUTPUT Stage: Envelope sealing, continuity state management

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

from core.kernel.pattern_registry import PatternRegistry
from core.kernel.pattern_selector import PatternSelector
from core.kernel.planner import Planner
from core.kernel.role_registry import AgentRoleRegistry
from core.kernel.tool_registry import ToolContractRegistry

from arifosmcp.runtime.shadow_defense import ShadowDefense
from arifosmcp.models.verdicts import SealType, PipelineStage
from arifosmcp.runtime.sessions import get_session_continuity_state

logger = logging.getLogger(__name__)

class KernelCore:
    """
    Unified KERNEL rCore that orchestrates the metabolic pipeline.
    """

    def __init__(self):
        self._tool_handlers: dict[str, Any] = {}
        self._governance_enabled: bool = True
        
        self.pattern_registry = PatternRegistry()
        self.pattern_selector = PatternSelector(self.pattern_registry)
        self.planner = Planner()
        self.tool_registry = ToolContractRegistry()
        self.role_registry = AgentRoleRegistry()
        self.shadow_defense = ShadowDefense()

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
        payload = dict(payload or {})
        payload.update(kwargs)

        if query: payload.setdefault("query", query)
        if session_id: payload.setdefault("session_id", session_id)
        if actor_id: payload.setdefault("actor_id", actor_id)
        if intent: payload.setdefault("intent", intent)
        if auth_context: payload.setdefault("auth_context", auth_context)
        if caller_context: payload.setdefault("caller_context", caller_context)

        effective_query = payload.get("query") or query or ""
        
        # ── Identity Resolution (F11 Hardening) ──
        from arifosmcp.runtime.sessions import get_session_identity
        
        _bound_actor = None
        if session_id and session_id != "global":
            _identity = get_session_identity(session_id)
            if _identity:
                _bound_actor = _identity.get("actor_id")
        
        effective_actor = (
            _bound_actor or payload.get("actor_id") or actor_id or "anonymous"
        ).strip().lower()

        selected_pattern = self.pattern_selector.select({"query": effective_query, **payload})
        adaptive_depth = self._compute_adaptive_depth(effective_query, risk_tier, payload)
        
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
            "adaptive_depth": adaptive_depth,
            "kernel_primitives": {
                "planner": self.planner,
                "tool_registry": self.tool_registry,
                "role_registry": self.role_registry,
            }
        }
        return context

    def _compute_adaptive_depth(self, query: str, risk_tier: str, payload: dict[str, Any]) -> str:
        q = query.lower()
        destructive_signals = {"delete", "remove", "forge", "execute", "write", "modify", "deploy", "seal", "wipe", "drop"}
        has_destructive = any(s in q for s in destructive_signals)
        if risk_tier == "low" and not has_destructive and not payload.get("allow_execution"):
            return "fast"
        return "deep" if (risk_tier in ("high", "critical") or has_destructive) else "standard"

    def verify_dag(self, tool_name: str, session_id: str, context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Enforces arifOS v2.0 DAG ordering and Omega gates.
        """
        state = get_session_continuity_state(session_id) or {}
        completed_stages = state.get("completed_stages", [])
        
        # Rule 1: No Stage 777 (Forge/Execution) without Stage 666 (Heart/Risk)
        if "forge" in tool_name or "execute" in tool_name:
            if 666 not in completed_stages:
                return False, "DAG_VIOLATION: Stage 777 (Forge) requires Stage 666 (Heart) completion."
            
            # Omega Gate: Ω ≥ 0.95
            omega = context.get("metrics", {}).get("omega_ortho", 1.0)
            if omega < 0.95:
                return False, f"GATE_LOCKED: Ω={omega} < 0.95. Lane independence insufficient for execution."
        
        return True, "OK"

    async def orchestrate_stage(self, context: dict[str, Any]) -> dict[str, Any]:
        from arifosmcp.runtime.governance_enforcer import classify_and_route
        from arifosmcp.runtime.tools_hardened_dispatch import get_tool_handler

        query = context.get("query", "")
        actor_id = context.get("actor_id", "anonymous")
        session_id = context.get("session_id", "global")
        
        # 1. Shadow-arifOS Audit (F9)
        audit_results = self.shadow_defense.run_full_audit(context)
        if any(r.is_shadow for r in audit_results):
            return {
                "ok": False,
                "verdict": SealType.VOID,
                "error": f"SHADOW_DETECTED: {audit_results[0].description}"
            }

        # 2. DAG Verification
        routing_result = await classify_and_route(query=query, actor_id=actor_id, session_id=session_id, context=context)
        tool_name = routing_result.get("tool_name", "arifos_mind")
        
        dag_ok, dag_error = self.verify_dag(tool_name, session_id, context)
        if not dag_ok:
            return {"ok": False, "verdict": SealType.VOID, "error": dag_error}

        # 3. Invoke Tool
        handler = get_tool_handler(tool_name) or get_tool_handler("arifos_mind")
        tool_result = await self._invoke_with_governance(handler=handler, tool_name=tool_name, context=context)

        # ── WELL Cognitive Pressure Signal ───────────────────────────
        try:
            from arifosmcp.runtime.well_bridge import signal_cognitive_pressure
            signal_cognitive_pressure(load_delta=0.1, source=tool_name)
        except Exception:
            pass  # non-fatal

        return {
            "ok": tool_result.get("ok", True),
            "tool_name": tool_name,
            "tool_result": tool_result,
            "routing_result": routing_result,
            "context": context,
        }

    async def _invoke_with_governance(self, handler: Any, tool_name: str, context: dict[str, Any]) -> dict[str, Any]:
        try:
            kwargs = {
                "query": context.get("query"),
                "session_id": context.get("session_id"),
                "risk_tier": context.get("risk_tier", "medium"),
                "dry_run": context.get("dry_run", True),
                "allow_execution": context.get("allow_execution", False),
                "platform": context.get("platform", "unknown"),
            }
            if tool_name == "arifos_init":
                kwargs["actor_id"] = context.get("actor_id")
                kwargs["intent"] = context.get("intent")
            
            from arifosmcp.runtime.tools_hardened_dispatch import dispatch_with_fail_closed
            return await dispatch_with_fail_closed(tool_name, kwargs)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def output_stage(self, tool_result: dict[str, Any], tool_name: str, context: dict[str, Any], routing_result: dict[str, Any]) -> dict[str, Any]:
        from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
        from arifosmcp.runtime.models import RuntimeEnvelope
        
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
                stage=PipelineStage.S444_KERNEL.value,
                session_id=session_id,
                payload=tool_result,
            )

        # ── OutputEnvelope limits: cap payload lists and truncate verbose strings ──
        if isinstance(envelope.payload, dict):
            pl = envelope.payload
            for key in ("facts", "uncertainties", "options"):
                if key in pl and isinstance(pl[key], list):
                    pl[key] = pl[key][:3]
            envelope.payload = pl
        if envelope.detail and len(envelope.detail) > 500:
            envelope.detail = envelope.detail[:497] + "..."
        if envelope.hint and len(envelope.hint) > 300:
            envelope.hint = envelope.hint[:297] + "..."

        # ── Philosophy Injection (Horizon Atlas) ──
        try:
            from arifosmcp.runtime.philosophy import AtlasScores, select_atlas_philosophy
            
            # Extract metrics from envelope/payload
            metrics = getattr(envelope, "metrics", None)
            pl = envelope.payload if isinstance(envelope.payload, dict) else {}
            
            delta_s = float(
                pl.get("delta_s", getattr(metrics.telemetry, "ds", -0.01) if metrics else -0.01)
            )
            g_score = float(
                pl.get(
                    "truth_score",
                    getattr(metrics.telemetry, "confidence", 0.85) if metrics else 0.85
                )
            )
            omega_score = float(pl.get("omega_score", 0.04))

            scores = AtlasScores(
                delta_s=delta_s,
                g_score=g_score,
                omega_score=omega_score,
                lyapunov_sign="stable",
                verdict=str(envelope.verdict),
                session_stage=str(envelope.stage),
            )
            
            phi = select_atlas_philosophy(scores, session_id=session_id)
            if isinstance(envelope.payload, dict):
                envelope.payload["philosophy"] = phi
                
            # Update detail with primary quote
            quote = phi.get("primary_quote", {}).get("quote")
            author = phi.get("primary_quote", {}).get("author", "Unknown")
            if quote:
                base_detail = envelope.detail or ""
                envelope.detail = f"{base_detail}\n\n\"{quote}\" — {author}"
        except Exception as phil_err:
            logger.debug(f"KERNEL OUTPUT: Philosophy atlas injection failed: {phil_err}")

        # Seal with continuity
        sealed = seal_runtime_envelope(
            envelope=envelope,
            tool_id=tool_name,
            session_id=session_id,
        )
        
        sealed = seal_runtime_envelope(envelope=envelope, tool_id=tool_name, session_id=session_id)
        
        # ── Health Band Injection ──
        if isinstance(sealed, RuntimeEnvelope):
            from arifosmcp.runtime.telemetry_bands import TelemetryBands
            metrics_dict = {
                "ds": getattr(sealed.metrics.telemetry, "ds", 0.0),
                "peace2": getattr(sealed.metrics.telemetry, "peace2", 1.0),
                "omega": getattr(sealed.metrics.telemetry, "omega_ortho", 1.0),
                "w3": getattr(sealed.metrics.witness, "ai", 0.95), # Simplification for now
                "shadow": getattr(sealed.metrics.telemetry, "shadow", 0.0)
            }
            sealed.metrics.meta["health_bands"] = TelemetryBands.compute_all_bands(metrics_dict)
            return sealed.to_dict(compact=True)
        return sealed

    async def execute(self, query: str | None = None, session_id: str | None = None, actor_id: str | None = None, 
                      intent: str | None = None, auth_context: dict | None = None, risk_tier: str = "medium", 
                      dry_run: bool = True, allow_execution: bool = False, caller_context: dict | None = None, 
                      payload: dict[str, Any] | None = None, platform: str = "unknown", **kwargs: Any) -> dict[str, Any]:
        
        context = await self.input_stage(query=query, session_id=session_id, actor_id=actor_id, intent=intent, 
                                          auth_context=auth_context, risk_tier=risk_tier, dry_run=dry_run, 
                                          allow_execution=allow_execution, caller_context=caller_context, 
                                          payload=payload, platform=platform, **kwargs)

        orchestrate_result = await self.orchestrate_stage(context)
        if not orchestrate_result.get("ok"):
            return orchestrate_result

        final_result = await self.output_stage(orchestrate_result.get("tool_result", {}), orchestrate_result.get("tool_name"), 
                                               context, orchestrate_result.get("routing_result", {}))
        
        verdict = final_result.get("verdict", "SABAR")
        final_result["kernel_status"] = "READY" if verdict == "SEAL" else ("BLOCKED" if verdict == "VOID" else "HOLD")

        # ── WELL Biological Context Injection ────────────────────────
        try:
            from arifosmcp.runtime.well_bridge import inject_biological_context
            final_result = inject_biological_context(final_result)
        except Exception:
            pass  # WELL offline is non-fatal — W0 sovereignty invariant

        return final_result

_kernel_core: KernelCore | None = None
def get_kernel_core() -> KernelCore:
    global _kernel_core
    if _kernel_core is None: _kernel_core = KernelCore()
    return _kernel_core

async def kernel_execute(**kwargs: Any) -> dict[str, Any]:
    return await get_kernel_core().execute(**kwargs)
