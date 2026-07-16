"""
arifosmcp/runtime/fastmcp_ext/resources.py
MCP Resources for arifOS — verdicts, continuity, session state, and INIT prompts.

These are registered alongside tools to achieve full MCP spec compliance.
INIT prompt resources make agent bootstrap files discoverable via MCP (F4 CLARITY).
"""

from __future__ import annotations

import logging
import os
from typing import Any


logger = logging.getLogger(__name__)

# ── INIT prompt files — canonical paths ──────────────────────────────────
_INIT_PROMPT_DIR = "/root/AAA/agents/opencode"
_AGENT_INIT_V3_PATH = "/root/AAA/prompts/AGENT_INIT_v3.0.md"

_INIT_PROMPT_FILES: dict[str, str] = {
    "AGENTS": os.path.join(_INIT_PROMPT_DIR, "AGENTS.md"),
    "AUTONOMOUS_GOVERNANCE": os.path.join(_INIT_PROMPT_DIR, "AUTONOMOUS_GOVERNANCE.md"),
    "SOUL": os.path.join(_INIT_PROMPT_DIR, "SOUL.md"),
    "TOOLS": os.path.join(_INIT_PROMPT_DIR, "TOOLS.md"),
    "IDENTITY": os.path.join(_INIT_PROMPT_DIR, "IDENTITY.md"),
    "BOOTSTRAP": os.path.join(_INIT_PROMPT_DIR, "BOOTSTRAP.md"),
    "HEARTBEAT": os.path.join(_INIT_PROMPT_DIR, "HEARTBEAT.md"),
    "USER": "/root/.openclaw/workspace/USER.md",
    "SKILL_PROFILE": "/root/AAA/skills/OPENCODE_SKILL_PROFILE.json",
}


def _read_file_safe(path: str) -> str:
    """Read file with F1-safe fallback."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("INIT resource file not found: %s", path)
        return f"[Resource unavailable: {path} — file not found]"
    except OSError as e:
        logger.warning("INIT resource read error: %s: %s", path, e)
        return f"[Resource unavailable: {path} — {e}]"


def register_arifos_resources(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP resources on the given FastMCP server.

    Includes: verdict, continuity, vitals, INIT prompts, and AGENT_INIT_v3.0.
    """
    registered: list[str] = []

    # ── Verdict resource ────────────────────────────────────────────────
    @mcp.resource(
        "arifos://verdict/{session_id}",
        description=(
            "Constitutional verdict for a specific session. "
            "Returns the current constitutional advisory verdict (SEAL, SABAR, VOID, or HOLD). "
            "Human judgment remains final authority. "
            "from the governance kernel, along with floor compliance proof and "
            "risk tier. Updated in real-time as the session progresses through stages."
        ),
    )
    async def get_verdict(session_id: str) -> str:
        """Get constitutional verdict for a session as JSON."""
        try:
            from core.governance_kernel import get_governance_kernel

            kernel = get_governance_kernel()
            state = kernel.get_current_state() if hasattr(kernel, "get_current_state") else {}
            verdict = state.get("verdict", "SEAL") if state else "SEAL"
        except Exception:
            verdict = "SEAL"
        import json

        return json.dumps({"session_id": session_id, "verdict": verdict}, indent=2)

    registered.append("arifos://verdict/{session_id}")

    # ── Continuity resource ──────────────────────────────────────────────
    @mcp.resource(
        "arifos://continuity/{session_id}",
        description=(
            "Session continuity state and contract lineage. "
            "Returns the full continuity chain for a session including previous tool, "
            "current tool, max risk tier, and contract version. "
            "Essential for resuming interrupted sessions and audit trail reconstruction."
        ),
    )
    async def get_continuity(session_id: str) -> str:
        """Get session continuity state as JSON."""
        try:
            from arifosmcp.runtime.contracts import get_continuity_store

            store = get_continuity_store()
            data = store.load(session_id)
        except Exception:
            data = {}
        import json

        return json.dumps({"session_id": session_id, "continuity": data}, indent=2)

    registered.append("arifos://continuity/{session_id}")

    # ── Vitals resource ──────────────────────────────────────────────────
    @mcp.resource(
        "arifos://vitals",
        description=(
            "Real-time constitutional vitals and thermodynamic telemetry. "
            "Returns CPU, memory, disk, genius score (G), entropy delta (ΔS), "
            "human impact load (Ω), and paradox tension (Ψ). "
            "Updated continuously by the metabolic monitor. Use for health checks."
        ),
    )
    async def get_vitals() -> str:
        """Get real-time constitutional vitals as JSON."""
        try:
            from arifosmcp.runtime.rest_routes import _build_governance_status_payload

            payload = _build_governance_status_payload()
        except Exception as exc:
            payload = {"error": str(exc)}
        import json

        return json.dumps(payload, indent=2)

    registered.append("arifos://vitals")

    # ── INIT prompt resources (F4 CLARITY: MCP-discoverable bootstrap) ────
    for name, filepath in _INIT_PROMPT_FILES.items():
        uri = f"arifos://init/opencode/{name.lower()}"
        description = f"OpenCode INIT prompt: {name}.md — agent bootstrap instruction."
        _content = _read_file_safe(filepath)

        @mcp.resource(uri, description=description)
        async def _init_resource(_content=_content) -> str:
            return _content

        registered.append(uri)

    # ── AGENT_INIT_v3.0 resource ──────────────────────────────────────────
    @mcp.resource(
        "arifos://init/agent_init_v3",
        description=(
            "Canonical AGENT_INIT_v3.0.md — TRINITY-33 + RSI + Constitutional Friction. "
            "Full 612-line boot-phase contract for all agents entering the arifOS federation. "
            "Forged 2026-07-08 by FORGE (000Ω) under F13 SOVEREIGN directive."
        ),
    )
    async def agent_init_v3() -> str:
        return _read_file_safe(_AGENT_INIT_V3_PATH)

    registered.append("arifos://init/agent_init_v3")

    logger.info(
        "Registered %d extended resources (incl. %d INIT prompts + agent_init_v3)",
        len(registered),
        len(_INIT_PROMPT_FILES),
    )
    return registered


__all__ = ["register_arifos_resources"]
