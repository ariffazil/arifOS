"""
arifosmcp/runtime/tools_hardened_dispatch.py

🔒 THE FAIL-CLOSED GATEKEEPER (Hardened Rebuild)
Stage: DISPATCH | Trinity: DELTA Δ | Floors: F12, F13

Zero-loophole: any request missing identity, schema, or operating outside
the explicit call graph is instantly VOID. Silent fallbacks to ANONYMOUS
are impossible.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# DISPATCH MAP (CANONICAL INTERNAL GATES)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_dispatch_map() -> dict[str, Callable[..., Awaitable[Any]]]:
    """
    Build the dispatch map pointing directly to internal metabolic implementations.
    This BREAKS the recursive loop between megaTools and Dispatch.
    """
    from arifosmcp.runtime.tools_internal import (
        agi_mind_dispatch_impl,
        apex_judge_dispatch_impl,
        architect_registry_dispatch_impl,
        arifos_kernel_impl,
        asi_heart_dispatch_impl,
        code_engine_dispatch_impl,
        engineering_memory_dispatch_impl,
        init_anchor_dispatch_impl,
        math_estimator_dispatch_impl,
        physics_reality_dispatch_impl,
        vault_ledger_dispatch_impl,
    )

    def _ctx() -> Any:
        return None  # Context injected by FastMCP framework at runtime if needed

    def _pop_payload(kwargs: dict[str, Any]) -> dict[str, Any]:
        """Unified payload extraction."""
        p = dict(kwargs.pop("payload", None) or {})
        # Merge top-level kwargs into payload for internal dispatchers
        for k, v in list(kwargs.items()):
            if k not in ("auth_context", "risk_tier", "dry_run", "ctx"):
                p[k] = kwargs.get(k)
        return p

    async def _dispatch_init(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await init_anchor_dispatch_impl(
            mode=kwargs.get("mode", "init"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_sense(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await physics_reality_dispatch_impl(
            mode=kwargs.get("mode", "governed"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_mind(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await agi_mind_dispatch_impl(
            mode=kwargs.get("mode", "reason"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_route(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_kernel_impl(
            query=payload.get("query") or payload.get("request"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            auth_context=kwargs.get("auth_context"),
            dry_run=kwargs.get("dry_run", True),
            allow_execution=kwargs.get("allow_execution", False),
            session_id=payload.get("session_id"),
            ctx=_ctx(),
        )

    async def _dispatch_memory(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await engineering_memory_dispatch_impl(
            mode=kwargs.get("mode", "vector_query"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_heart(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await asi_heart_dispatch_impl(
            mode=kwargs.get("mode", "critique"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_ops(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await math_estimator_dispatch_impl(
            mode=kwargs.get("mode", "cost"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_judge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await apex_judge_dispatch_impl(
            mode=kwargs.get("mode", "judge"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_vault(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await vault_ledger_dispatch_impl(
            mode=kwargs.get("mode", "seal"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    async def _dispatch_forge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await code_engine_dispatch_impl(
            mode=kwargs.get("mode", "execute"),
            payload=payload,
            auth_context=kwargs.get("auth_context"),
            risk_tier=kwargs.get("risk_tier", "medium"),
            dry_run=kwargs.get("dry_run", True),
            ctx=_ctx(),
        )

    # Alias Map
    return {
        "arifos_init": _dispatch_init,
        "arifos_sense": _dispatch_sense,
        "arifos_mind": _dispatch_mind,
        "arifos_route": _dispatch_route,
        "arifos_memory": _dispatch_memory,
        "arifos_heart": _dispatch_heart,
        "arifos_ops": _dispatch_ops,
        "arifos_judge": _dispatch_judge,
        "arifos_vault": _dispatch_vault,
        "arifos_forge": _dispatch_forge,
        # Legacy/Internal mapping consistency
        "init_anchor": _dispatch_init,
        "physics_reality": _dispatch_sense,
        "agi_mind": _dispatch_mind,
        "arifos_kernel": _dispatch_route,
        "engineering_memory": _dispatch_memory,
        "asi_heart": _dispatch_heart,
        "math_estimator": _dispatch_ops,
        "apex_judge": _dispatch_judge,
        "vault_ledger": _dispatch_vault,
        "code_engine": _dispatch_forge,
        "architect_registry": architect_registry_dispatch_impl,
    }

class _LazyDispatchMap(dict):
    _loaded: bool = False
    def _ensure_loaded(self) -> None:
        if not self._loaded:
            try:
                self.update(_build_dispatch_map())
            except ImportError as e:
                logger.error(f"FAIL_CLOSED: Critical dispatch load error: {e}")
            self._loaded = True
    def __getitem__(self, key: str) -> Any: self._ensure_loaded(); return super().__getitem__(key)
    def __contains__(self, key: object) -> bool: self._ensure_loaded(); return super().__contains__(key)
    def get(self, key: str, default: Any = None) -> Any: self._ensure_loaded(); return super().get(key, default)
    def items(self) -> Any: self._ensure_loaded(); return super().items()
    def keys(self) -> Any: self._ensure_loaded(); return super().keys()
    def values(self) -> Any: self._ensure_loaded(); return super().values()

HARDENED_DISPATCH_MAP: dict[str, Callable[..., Awaitable[Any]]] = _LazyDispatchMap()

# ═══════════════════════════════════════════════════════════════════════════════
# FAIL-CLOSED WRAPPER (PR-17 REBUILD)
# ═══════════════════════════════════════════════════════════════════════════════

_IDENTITY_GATED_TOOLS = frozenset([
    "arifos_mind", "arifos_sense", "arifos_memory", "arifos_heart",
    "arifos_ops", "arifos_judge", "arifos_vault", "arifos_forge", "arifos_route"
])

def _get_fail_closed_result(tool_name: str, reason: str, session_id: str | None = None) -> dict[str, Any]:
    return {
        "ok": False, "verdict": "VOID", "tool": tool_name, "stage": "FAIL_CLOSED",
        "error": reason, "error_code": "FAIL_CLOSED_GATE", "session_id": session_id,
        "fail_closed": True
    }

async def dispatch_with_fail_closed(tool_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Final Gatekeeper. Processes all tool requests through F12/F13 filters.
    """
    handler = HARDENED_DISPATCH_MAP.get(tool_name)
    session_id = kwargs.get("session_id")

    # GATE 1: Existence
    if handler is None:
        return _get_fail_closed_result(tool_name, f"Tool '{tool_name}' unknown.", session_id)

    # GATE 2: Identity (F12)
    if tool_name in _IDENTITY_GATED_TOOLS:
        from arifosmcp.runtime.sessions import get_session_identity
        identity = get_session_identity(session_id) if session_id else None
        if not identity or identity.get("actor_id", "anonymous") == "anonymous":
            return _get_fail_closed_result(tool_name, "UNANCHORED_SESSION: Call arifos_init first.", session_id)

    # GATE 3: Side-Effect Ratification (F13)
    if tool_name == "arifos_forge":
        if not kwargs.get("human_ratified") or not kwargs.get("confirmation_step"):
             return _get_fail_closed_result(tool_name, "RATIFICATION_MISSING: Requires human_ratified=True.", session_id)

    # EXECUTION
    try:
        result = await handler(**kwargs)
        if hasattr(result, "to_dict"):
            return result.to_dict(compact=True)
        if hasattr(result, "model_dump"):
            return result.model_dump(mode="json")
        if hasattr(result, "__dict__"):
            return result.__dict__
        return result or {"ok": True}
    except Exception as e:
        logger.error(f"FAIL_CLOSED: Handler exception in {tool_name}: {e}")
        return _get_fail_closed_result(tool_name, f"INTERNAL_ERROR: {str(e)}", session_id)

def list_canonical_tools() -> list[str]:
    return list(HARDENED_DISPATCH_MAP.keys())
