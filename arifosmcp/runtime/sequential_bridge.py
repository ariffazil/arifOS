"""
arifosmcp/runtime/sequential_bridge.py — Sequential Thinking MCP Bridge
═══════════════════════════════════════════════════════════════════════

MCP client bridge to the A-FORGE Sequential Thinking MCP server.
Follows the same pattern as integrations/playwright_bridge.py.

Two backends:
  1. NATIVE:  arifOS runtime/thinking/ module (always available, constitutionally governed)
  2. EXTERNAL: A-FORGE FastMCP HTTP server (port 51001, full MCP protocol)

The bridge prefers NATIVE (constitutional governance) and falls back to
EXTERNAL if explicitly configured via MIND_SEQUENTIAL_BACKEND=external.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx
import mcp.types as types
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client

logger = logging.getLogger(__name__)

# ── Backend Selection ────────────────────────────────────────────────────────
# "native" = arifOS constitutional thinking module (default)
# "external" = A-FORGE FastMCP HTTP server
# "auto" = try external first, fall back to native
MIND_SEQUENTIAL_BACKEND = os.getenv("MIND_SEQUENTIAL_BACKEND", "native")

# A-FORGE sequential thinking server URL
SEQUENTIAL_MCP_URL = os.getenv(
    "SEQUENTIAL_MCP_URL",
    "http://127.0.0.1:51001/mcp",
)
SEQUENTIAL_MCP_TIMEOUT = float(os.getenv("SEQUENTIAL_MCP_TIMEOUT", "90.0"))

# Client info for MCP handshake
BRIDGE_CLIENT_INFO = types.Implementation(
    name="arifOS-sequential-bridge",
    version="1.0.0",
)


# ═══════════════════════════════════════════════════════════════════════════════
# EXTERNAL BACKEND — MCP Client (pattern from playwright_bridge.py)
# ═══════════════════════════════════════════════════════════════════════════════


def _create_sequential_http_client() -> httpx.AsyncClient:
    """Create an httpx client configured for the A-FORGE sequential thinking server."""
    return httpx.AsyncClient(
        timeout=httpx.Timeout(SEQUENTIAL_MCP_TIMEOUT),
        headers={
            "Accept": "application/json, text/event-stream",
        },
        follow_redirects=True,
    )


@asynccontextmanager
async def sequential_mcp_session(
    url: str = SEQUENTIAL_MCP_URL,
) -> AsyncGenerator[ClientSession, None]:
    """
    Open an MCP client session to the Sequential Thinking server.

    Usage:
        async with sequential_mcp_session() as session:
            result = await session.call_tool("sequentialthinking", {...})
    """
    async with _create_sequential_http_client() as client:
        async with streamable_http_client(url, client, client_info=BRIDGE_CLIENT_INFO) as transport:
            async with ClientSession(transport[0], transport[1]) as session:
                await session.initialize()
                yield session


async def call_external_sequential_thinking(
    thought: str,
    thought_number: int = 1,
    total_thoughts: int = 3,
    next_thought_needed: bool = True,
    is_revision: bool = False,
    revises_thought: int | None = None,
    branch_from_thought: int | None = None,
    branch_id: str | None = None,
    needs_more_thoughts: bool = False,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Call the external A-FORGE Sequential Thinking MCP server.

    Maps to the standard MCP sequentialthinking tool signature.
    Returns the thought result from the external server.
    """
    arguments: dict[str, Any] = {
        "thought": thought,
        "thoughtNumber": thought_number,
        "totalThoughts": total_thoughts,
        "nextThoughtNeeded": next_thought_needed,
    }

    if is_revision:
        arguments["isRevision"] = True
        if revises_thought:
            arguments["revisesThought"] = revises_thought

    if branch_from_thought is not None:
        arguments["branchFromThought"] = branch_from_thought
    if branch_id:
        arguments["branchId"] = branch_id
    if needs_more_thoughts:
        arguments["needsMoreThoughts"] = True

    try:
        async with sequential_mcp_session() as session:
            result = await session.call_tool("sequentialthinking", arguments)
            return {
                "status": "ok",
                "backend": "external",
                "server_url": SEQUENTIAL_MCP_URL,
                "thought_number": thought_number,
                "total_thoughts": total_thoughts,
                "next_thought_needed": next_thought_needed,
                "result": result.content if hasattr(result, "content") else str(result),
            }
    except Exception as exc:
        logger.warning(f"External sequential thinking unavailable: {exc}")
        return {
            "status": "external_unavailable",
            "backend": "external",
            "error": str(exc),
            "thought_number": thought_number,
            "total_thoughts": total_thoughts,
            "next_thought_needed": next_thought_needed,
            "recommendation": "Fall back to native constitutional thinking.",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NATIVE BACKEND — arifOS Constitutional Thinking
# ═══════════════════════════════════════════════════════════════════════════════


def call_native_sequential_thinking(
    thought: str,
    thought_number: int = 1,
    total_thoughts: int = 3,
    next_thought_needed: bool = True,
    is_revision: bool = False,
    revises_thought: int | None = None,
    branch_from_thought: int | None = None,
    branch_id: str | None = None,
    needs_more_thoughts: bool = False,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Use arifOS native constitutional thinking module.

    Wraps runtime/thinking/session.py with the standard sequentialthinking
    tool signature for compatibility.
    """
    from arifosmcp.runtime.thinking.session import (
        ThinkingSessionManager,
        StepType,
    )

    manager = ThinkingSessionManager()
    sid = session_id or f"mind-{thought_number}"

    # Get or create session
    session = manager.get_session(sid)
    if session is None:
        session = manager.start_session(
            problem=thought[:200],
            arifos_session_id=sid,
            tags=["sequential", "native", "constitutional"],
        )
        # Use the generated session_id
        sid = session.session_id

    # Determine step type
    if is_revision:
        step_type = StepType.REVISION.value
    elif branch_id:
        step_type = StepType.BRANCH.value
    elif thought_number >= total_thoughts:
        step_type = StepType.CONCLUSION.value
    elif "hypothesis" in thought.lower() or "maybe" in thought.lower():
        step_type = StepType.HYPOTHESIS.value
    elif "verify" in thought.lower() or "check" in thought.lower():
        step_type = StepType.VERIFICATION.value
    else:
        step_type = StepType.ANALYSIS.value

    # Add step via manager (includes full constitutional validation)
    step = manager.add_step(
        session_id=sid,
        step_type=step_type,
        content=thought,
        branch_id=branch_id,
        parent_step=revises_thought if is_revision else None,
    )

    # Get updated session for stats
    session = manager.get_session(sid)

    return {
        "status": "ok",
        "backend": "native",
        "session_id": sid,
        "thought_number": step.step_number,
        "total_thoughts": total_thoughts,
        "next_thought_needed": next_thought_needed,
        "step_type": step.step_type,
        "constitutional_verdict": step.constitutional_verdict,
        "f2_truth_score": step.f2_truth_score,
        "f7_uncertainty": step.f7_uncertainty,
        "total_steps_in_session": len(session.steps) if session else 0,
        "branches": list(session.branches.keys()) if (session and session.branches) else [],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# UNIFIED CALL — backend-agnostic
# ═══════════════════════════════════════════════════════════════════════════════


async def sequential_think(
    thought: str,
    thought_number: int = 1,
    total_thoughts: int = 3,
    next_thought_needed: bool = True,
    is_revision: bool = False,
    revises_thought: int | None = None,
    branch_from_thought: int | None = None,
    branch_id: str | None = None,
    needs_more_thoughts: bool = False,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Unified sequential thinking call — backend selected by MIND_SEQUENTIAL_BACKEND.

    Backends:
      - "native": arifOS constitutional thinking (default, always available)
      - "external": A-FORGE FastMCP HTTP server
      - "auto": try external, fall back to native
    """
    backend = MIND_SEQUENTIAL_BACKEND

    if backend == "external":
        result = await call_external_sequential_thinking(
            thought=thought,
            thought_number=thought_number,
            total_thoughts=total_thoughts,
            next_thought_needed=next_thought_needed,
            is_revision=is_revision,
            revises_thought=revises_thought,
            branch_from_thought=branch_from_thought,
            branch_id=branch_id,
            needs_more_thoughts=needs_more_thoughts,
            session_id=session_id,
        )
        if result.get("status") == "external_unavailable":
            logger.info("External backend unavailable, falling back to native.")
            backend = "native"
        else:
            return result

    if backend in ("native", "auto"):
        return call_native_sequential_thinking(
            thought=thought,
            thought_number=thought_number,
            total_thoughts=total_thoughts,
            next_thought_needed=next_thought_needed,
            is_revision=is_revision,
            revises_thought=revises_thought,
            branch_from_thought=branch_from_thought,
            branch_id=branch_id,
            needs_more_thoughts=needs_more_thoughts,
            session_id=session_id,
            actor_id=actor_id,
        )

    # Unknown backend
    return {
        "status": "error",
        "backend": backend,
        "error": f"Unknown backend: {backend}. Valid: native, external, auto.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════


def get_thinking_session(session_id: str) -> dict[str, Any] | None:
    """Retrieve a thinking session by ID (native backend only)."""
    from arifosmcp.runtime.thinking.session import ThinkingSessionManager

    manager = ThinkingSessionManager()
    try:
        session = manager.get_session(session_id)
        return {
            "session_id": session.session_id,
            "problem": session.problem,
            "status": session.status.value,
            "step_count": len(session.steps),
            "steps": [
                {
                    "step_number": s.step_number,
                    "content": s.content[:200],
                    "step_type": s.step_type,
                    "constitutional_verdict": s.constitutional_verdict,
                }
                for s in session.steps
            ],
            "branches": list(session.branches.keys()),
            "final_verdict": session.final_verdict,
            "created_at": str(session.created_at),
        }
    except Exception:
        return None


def list_thinking_sessions() -> list[dict[str, Any]]:
    """List all active thinking sessions (native backend only)."""
    from arifosmcp.runtime.thinking.session import ThinkingSessionManager

    manager = ThinkingSessionManager()
    sessions = manager.list_sessions()
    return [
        {
            "session_id": s.session_id,
            "problem": s.problem[:100],
            "status": s.status.value,
            "step_count": len(s.steps),
            "created_at": str(s.created_at),
        }
        for s in sessions
    ]
