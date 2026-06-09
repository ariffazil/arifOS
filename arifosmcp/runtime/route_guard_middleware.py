"""
arifOS Route Guard Middleware — Enforce arifos_route_query as pre-retrieval gate.

Blocks search/discovery tool calls unless arifos_route_query was called first
in the current session. F1 AMANAH: fail-closed. F11 AUDITABILITY: every block logged.

Architecture:
  1. Agent calls arifos_route_query → session marked as "routed"
  2. Agent calls search tool (arif_sense_observe, arif_memory_recall, etc.)
  3. Middleware checks: has this session been routed?
     - YES → allow
     - NO → HOLD with instruction to call arifos_route_query first

DITEMPA BUKAN DIBERI — Routing is mandatory, not optional.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ── Session Tracking ───────────────────────────────────────────────────────

# Tools that REQUIRE prior routing
GATED_TOOLS: frozenset[str] = frozenset({
    "arif_sense_observe",
    "arif_evidence_fetch",
    "arif_memory_recall",
    "arif_kernel_route",
    "arif_gateway_connect",
    # GEOX tools (via bridge)
    "geox_data_ingest_bundle",
    "geox_evidence_discover",
    "geox_evidence_reason",
    "geox_basin_profile",
    "geox_query_intake",
    # WEALTH tools (via bridge)
    "wealth_field_macro",
    "wealth_market_data",
    "wealth_agent_path",
    # WELL tools (via bridge)
    "well_trace_lineage",
    "well_system_registry_status",
})

# Tools that do NOT require routing (always allowed)
PASSTHROUGH_TOOLS: frozenset[str] = frozenset({
    "arif_session_init",
    "arifos_route_query",
    "arif_ops_measure",
    "arif_heart_critique",
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_forge_execute",
    "arif_reply_compose",
    "arif_mind_reason",
})


class RouteGuardState:
    """Per-session routing state. Thread-safe."""
    def __init__(self):
        self._routed_sessions: dict[str, float] = {}  # session_id → timestamp
        self._lock = threading.Lock()
        self._route_ttl_seconds: float = 3600.0  # 1 hour
        self._blocked_count: int = 0

    def mark_routed(self, session_id: str) -> None:
        with self._lock:
            self._routed_sessions[session_id] = time.monotonic()

    def is_routed(self, session_id: str) -> bool:
        with self._lock:
            ts = self._routed_sessions.get(session_id)
            if ts is None:
                return False
            # Check TTL
            if time.monotonic() - ts > self._route_ttl_seconds:
                del self._routed_sessions[session_id]
                return False
            return True

    def clear_session(self, session_id: str) -> None:
        with self._lock:
            self._routed_sessions.pop(session_id, None)

    def record_block(self) -> None:
        with self._lock:
            self._blocked_count += 1

    @property
    def blocked_count(self) -> int:
        with self._lock:
            return self._blocked_count


# ── Singleton ──────────────────────────────────────────────────────────────

_guard_state = RouteGuardState()


def get_route_guard_state() -> RouteGuardState:
    return _guard_state


# ── Middleware ──────────────────────────────────────────────────────────────


def create_route_guard_middleware(
    get_session_id: Callable[[], str | None],
) -> Callable[[str, dict[str, Any]], dict[str, Any] | None]:
    """
    Create a middleware function that enforces route_query pre-check.

    Args:
        get_session_id: A callable that returns the current session ID from context.

    Returns:
        A middleware function: (tool_name, tool_args) → HOLD response or None (allow)
    """
    guard = get_route_guard_state()

    def route_guard(tool_name: str, tool_args: dict[str, Any]) -> dict[str, Any] | None:
        # Passthrough tools — always allowed
        if tool_name in PASSTHROUGH_TOOLS:
            return None  # Allow

        # Not a gated tool — allow
        if tool_name not in GATED_TOOLS:
            return None  # Allow

        # Gated tool — check if session has been routed
        session_id = tool_args.get("session_id") or get_session_id()

        if not session_id:
            # No session — block (F1: fail-closed)
            guard.record_block()
            logger.warning(
                "ROUTE_GUARD: Blocked %s — no session_id. "
                "Call arif_session_init first, then arifos_route_query.",
                tool_name,
            )
            return {
                "verdict": "HOLD",
                "reason": "NO_SESSION",
                "tool": tool_name,
                "instruction": "Call arif_session_init first, then arifos_route_query before any search/discovery tool.",
                "governance": {
                    "floor": "F1",
                    "rule": "Pre-retrieval routing gate",
                    "reversible": True,
                },
            }

        if guard.is_routed(session_id):
            return None  # Allow — session has been routed

        # Block — session not routed
        guard.record_block()
        logger.warning(
            "ROUTE_GUARD: Blocked %s in session %s — "
            "arifos_route_query not called yet.",
            tool_name, session_id[:20],
        )
        return {
            "verdict": "HOLD",
            "reason": "ROUTE_NOT_PERFORMED",
            "tool": tool_name,
            "session_id": session_id,
            "instruction": (
                f"Call arifos_route_query(query='<your query>', session_id='{session_id}') "
                f"before calling {tool_name}. This ensures deterministic routing "
                f"with exploit/explore lane selection, budget enforcement, and "
                f"contradiction quota compliance."
            ),
            "governance": {
                "floor": "F1",
                "rule": "Pre-retrieval routing gate — arifos_route_query is mandatory",
                "reversible": True,
                "delta_S": 0.0,
            },
            "next_action": "call_arifos_route_query_first",
        }

    return route_guard


# ── Integration hooks ──────────────────────────────────────────────────────


def mark_session_routed(session_id: str) -> None:
    """Call this after arifos_route_query returns successfully."""
    get_route_guard_state().mark_routed(session_id)


def on_arifos_route_query_complete(result: dict[str, Any]) -> None:
    """
    Hook to call after arifos_route_query execution.
    Marks the session as routed so subsequent gated tools are allowed.
    """
    session_id = result.get("audit", {}).get("session_id") or result.get("session_id")
    if session_id:
        mark_session_routed(session_id)
        logger.debug("Route guard: session %s marked as routed", session_id[:20])
