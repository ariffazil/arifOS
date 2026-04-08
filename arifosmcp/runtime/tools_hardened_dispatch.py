"""
Hardened Tool Dispatch Layer for arifOS MCP

This module provides the canonical tool dispatch map for all 10 arifOS tools.
Each tool is backed by a hardened wrapper that enforces ToM validation,
philosophy injection, and proper envelope sealing.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable


def _build_dispatch_map() -> dict[str, Callable[..., Awaitable[Any]]]:
    """Build the dispatch map. Called lazily so megaTools is fully initialized."""
    try:
        from fastmcp.dependencies import CurrentContext
    except ImportError:  # pragma: no cover - FastMCP 2 fallback
        CurrentContext = None

    from arifosmcp.runtime.megaTools import architect_registry
    from arifosmcp.runtime.tools import (
        arifos_heart,
        arifos_init,
        arifos_judge,
        arifos_memory,
        arifos_mind,
        arifos_ops,
        arifos_route,
        arifos_sense,
        arifos_vault,
    )
    from arifosmcp.runtime.tools_forge import arifos_forge
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

    def _ctx(provided: Any = None) -> Any:
        return provided or (CurrentContext() if CurrentContext else None)

    def _pop_payload(kwargs: dict[str, Any]) -> dict[str, Any]:
        return dict(kwargs.pop("payload", None) or {})

    async def _dispatch_init(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_init(
            actor_id=kwargs.pop("actor_id", None) or payload.get("actor_id") or "anonymous",
            intent=kwargs.pop("intent", None) or payload.get("intent") or payload.get("declared_intent") or "",
            declared_name=kwargs.pop("declared_name", None) or payload.get("declared_name"),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            allow_execution=kwargs.pop("allow_execution", payload.get("allow_execution", False)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_sense(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_sense(
            query=kwargs.pop("query", None) or payload.get("query") or kwargs.get("raw_input") or "",
            mode=kwargs.pop("mode", payload.get("mode", "governed")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_mind(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_mind(
            query=kwargs.pop("query", None) or payload.get("query") or kwargs.get("raw_input") or "",
            context=kwargs.pop("context", None) or payload.get("context"),
            mode=kwargs.pop("mode", payload.get("mode", "reason")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_route(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_route(
            request=kwargs.pop("request", None) or payload.get("request") or payload.get("query") or kwargs.get("raw_input") or "",
            mode=kwargs.pop("mode", payload.get("mode", "kernel")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            allow_execution=kwargs.pop("allow_execution", payload.get("allow_execution", False)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_memory(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_memory(
            query=kwargs.pop("query", None) or payload.get("query") or kwargs.get("raw_input") or "",
            mode=kwargs.pop("mode", payload.get("mode", "vector_query")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_heart(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_heart(
            content=kwargs.pop("content", None) or payload.get("content") or payload.get("query") or kwargs.get("raw_input") or "",
            mode=kwargs.pop("mode", payload.get("mode", "critique")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_ops(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_ops(
            action=kwargs.pop("action", None) or payload.get("action") or payload.get("query") or kwargs.get("raw_input") or "",
            mode=kwargs.pop("mode", payload.get("mode", "cost")),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_judge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_judge(
            candidate_action=kwargs.pop("candidate_action", None) or payload.get("candidate_action") or payload.get("query") or kwargs.get("raw_input") or "",
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            telemetry=kwargs.pop("telemetry", None) or payload.get("telemetry"),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_vault(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_vault(
            verdict=kwargs.pop("verdict", None) or payload.get("verdict") or "HOLD",
            evidence=kwargs.pop("evidence", None) or payload.get("evidence"),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            debug=kwargs.pop("debug", payload.get("debug", False)),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _dispatch_forge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await arifos_forge(
            action=kwargs.pop("action", None) or payload.get("action") or kwargs.pop("mode", None) or "compute",
            payload=payload.get("payload", payload),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id") or "global",
            judge_verdict=kwargs.pop("judge_verdict", None) or payload.get("judge_verdict") or "VOID",
            judge_g_star=float(kwargs.pop("judge_g_star", payload.get("judge_g_star", 0.0)) or 0.0),
            constraints=kwargs.pop("constraints", None) or payload.get("constraints"),
            ttl_seconds=int(kwargs.pop("ttl_seconds", payload.get("ttl_seconds", 300)) or 300),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            af_forge_endpoint=kwargs.pop("af_forge_endpoint", None) or payload.get("af_forge_endpoint"),
            platform=kwargs.pop("platform", payload.get("platform", "unknown")),
        )

    async def _legacy_init(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await init_anchor_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "init")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_sense(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("input", payload.get("query") or kwargs.get("query") or kwargs.get("raw_input") or "")
        return await physics_reality_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "search")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_mind(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("query", payload.get("query") or kwargs.get("query") or kwargs.get("raw_input") or "")
        return await agi_mind_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "reason")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_route(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        query = payload.get("query") or kwargs.get("query") or kwargs.get("raw_input") or ""
        return await arifos_kernel_impl(
            query=query,
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            allow_execution=kwargs.pop("allow_execution", payload.get("allow_execution", False)),
            session_id=kwargs.pop("session_id", None) or payload.get("session_id"),
            ctx=_ctx(kwargs.pop("ctx", None)),
            intent=payload.get("intent"),
        )

    async def _legacy_heart(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("content", payload.get("content") or kwargs.get("content") or payload.get("query") or kwargs.get("raw_input") or "")
        return await asi_heart_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "critique")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_memory(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("query", payload.get("query") or kwargs.get("query") or kwargs.get("raw_input") or "")
        return await engineering_memory_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "vector_query")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_ops(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("action", payload.get("action") or kwargs.get("action") or payload.get("query") or kwargs.get("raw_input") or "")
        return await math_estimator_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "cost")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_judge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        payload.setdefault("candidate", payload.get("candidate") or payload.get("candidate_action") or payload.get("query") or kwargs.get("raw_input") or "")
        return await apex_judge_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "judge")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_vault(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await vault_ledger_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "seal")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_forge(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await code_engine_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "execute")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    async def _legacy_architect(**kwargs: Any) -> Any:
        payload = _pop_payload(kwargs)
        return await architect_registry_dispatch_impl(
            mode=kwargs.pop("mode", payload.get("mode", "list")),
            payload=payload,
            auth_context=kwargs.pop("auth_context", payload.get("auth_context")),
            risk_tier=kwargs.pop("risk_tier", payload.get("risk_tier", "medium")),
            dry_run=kwargs.pop("dry_run", payload.get("dry_run", True)),
            ctx=_ctx(kwargs.pop("ctx", None)),
        )

    return {
        "arifos_init": _dispatch_init,
        "arifos_route": _dispatch_route,
        "arifos_judge": _dispatch_judge,
        "arifos_forge": _dispatch_forge,
        "arifos_sense": _dispatch_sense,
        "arifos_mind": _dispatch_mind,
        "arifos_memory": _dispatch_memory,
        "arifos_heart": _dispatch_heart,
        "arifos_ops": _dispatch_ops,
        "arifos_vault": _dispatch_vault,
        "init_anchor": _legacy_init,
        "arifOS_kernel": _legacy_route,
        "engineering_memory": _legacy_memory,
        "asi_heart": _legacy_heart,
        "math_estimator": _legacy_ops,
        "apex_soul": _legacy_judge,
        "vault_ledger": _legacy_vault,
        "code_engine": _legacy_forge,
        "architect_registry": _legacy_architect,
    }


class _LazyDispatchMap(dict):  # type: ignore[type-arg]
    """Dict that populates itself on first access, avoiding circular-import issues."""

    _loaded: bool = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            try:
                self.update(_build_dispatch_map())
            except ImportError as e:
                print(f"Warning: Could not load tool handlers: {e}")
            self._loaded = True

    def __getitem__(self, key: str) -> Any:
        self._ensure_loaded()
        return super().__getitem__(key)

    def __contains__(self, key: object) -> bool:
        self._ensure_loaded()
        return super().__contains__(key)

    def get(self, key: str, default: Any = None) -> Any:  # type: ignore[override]
        self._ensure_loaded()
        return super().get(key, default)

    def items(self) -> Any:
        self._ensure_loaded()
        return super().items()

    def keys(self) -> Any:
        self._ensure_loaded()
        return super().keys()

    def values(self) -> Any:
        self._ensure_loaded()
        return super().values()


HARDENED_DISPATCH_MAP: dict[str, Callable[..., Awaitable[Any]]] = _LazyDispatchMap()


def get_tool_handler(tool_name: str) -> Callable[..., Awaitable[Any]] | None:
    """Get the hardened handler for a canonical tool name."""
    return HARDENED_DISPATCH_MAP.get(tool_name)


def is_canonical_tool(tool_name: str) -> bool:
    """Check if a tool name is a canonical arifOS tool."""
    return tool_name in HARDENED_DISPATCH_MAP


def list_canonical_tools() -> list[str]:
    """Return list of all canonical tool names."""
    return [
        "arifos_init",
        "arifos_sense",
        "arifos_mind",
        "arifos_route",
        "arifos_memory",
        "arifos_heart",
        "arifos_ops",
        "arifos_judge",
        "arifos_vault",
        "arifos_forge",
    ]
