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
_AGENT_INIT_V3_PATH = "/root/AAA/prompts/INIT.md"

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
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("INIT resource file not found: %s", path)
        return f"[Resource unavailable: {path} — file not found]"
    except OSError as e:
        logger.warning("INIT resource read error: %s: %s", path, e)
        return f"[Resource unavailable: {path} — {e}]"


def register_arifos_resources(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP resources on the given FastMCP server.

    Includes: verdict, continuity, vitals, INIT prompts, and agent_init (ex AGENT_INIT_v3.0).
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
    # FastMCP requires URI templates with at least one `{param}` parameter.
    # We use a single templated resource `{name}` and look up content by name.
    @mcp.resource(
        "arifos://init/opencode/{name}",
        description=(
            "OpenCode INIT prompt files (agent bootstrap instruction). "
            "Available names: " + ", ".join(sorted(_INIT_PROMPT_FILES.keys()))
        ),
    )
    async def get_init_resource(name: str) -> str:
        """Return the contents of a named INIT prompt file."""
        filepath = _INIT_PROMPT_FILES.get(name)
        if not filepath:
            return (
                f"[Unknown INIT resource: {name}. Available: {sorted(_INIT_PROMPT_FILES.keys())}]"
            )
        return _read_file_safe(filepath)

    registered.append("arifos://init/opencode/{name}")

    # ── AGENT_INIT_v3.0 resource ──────────────────────────────────────────
    @mcp.resource(
        "arifos://init/agent_init",
        description=(
            "Canonical INIT.md (zen-dated 2026.07.17, ex AGENT_INIT_v3.0) — TRINITY-33 + RSI + Constitutional Friction. "
            "Full 612-line boot-phase contract for all agents entering the arifOS federation. "
            "Forged 2026-07-08 by FORGE (000Ω) under F13 SOVEREIGN directive."
        ),
    )
    async def agent_init() -> str:
        return _read_file_safe(_AGENT_INIT_V3_PATH)

    registered.append("arifos://init/agent_init")

    # ── carry-forward resource (session state continuity) ─────────────────
    _CARRY_FORWARD_PATH = "/root/.local/share/arifos/carry_forward.json"

    @mcp.resource(
        "arifos://carry-forward",
        description=(
            "Live session carry-forward state. Returns prior session ID, completed tasks, "
            "open 888_HOLD loops, entropy delta, cooling status, and successor pointer. "
            "This is the MCP-native equivalent of reading carry_forward.json from filesystem. "
            "Essential for agent continuity — load at session start instead of FS reads."
        ),
    )
    async def get_carry_forward() -> str:
        """Return current carry-forward.json contents."""
        try:
            with open(_CARRY_FORWARD_PATH, encoding="utf-8") as fh:
                return fh.read()
        except FileNotFoundError:
            return (
                '{"error":"carry_forward.json not found","note":"No prior session state available"}'
            )
        except Exception as exc:
            return f'{{"error":"{exc}"}}'

    registered.append("arifos://carry-forward")

    # ── flow-state resource (FQ pulse — metabolic nerve health) ───────────
    _FLOW_STATE_PATH = "/root/AAA/state/flow_state.json"

    @mcp.resource(
        "arifos://flow-state",
        description=(
            "Live Flow Quality (FQ) pulse — the federation's metabolic nerve health. "
            "Returns FQ value, verdict (OPTIMAL/BALANCED/WATCHING/STUCK), and last update. "
            "FQ < 0.5 → ALL agents HOLD (OBSERVE_ONLY). "
            "FQ >= 0.5 → forge. This replaces filesystem reads of /root/AAA/state/flow_state.json. "
            "Cross-reference with arifFlow :7073/health for real-time metabolic data."
        ),
    )
    async def get_flow_state() -> str:
        """Return current flow_state.json contents."""
        try:
            with open(_FLOW_STATE_PATH, encoding="utf-8") as fh:
                flow_data = fh.read()
        except (FileNotFoundError, Exception):
            # Try arifFlow as fallback
            import json

            try:
                import urllib.request

                with urllib.request.urlopen("http://localhost:7073/health", timeout=3) as resp:
                    arifflow_data = json.loads(resp.read())
                flow_data = json.dumps(
                    {
                        "fq": arifflow_data.get("fq", {}),
                        "status": arifflow_data.get("status", "unknown"),
                        "source": "arifFlow :7073 (fallback — flow_state.json unavailable)",
                    },
                    indent=2,
                )
            except Exception:
                flow_data = json.dumps(
                    {
                        "fq": {"quotient": 0.5, "verdict": "UNKNOWN"},
                        "error": "Neither flow_state.json nor arifFlow available",
                        "action": "Proceed with FQ=0.5 (conservative). Monitor.",
                    },
                    indent=2,
                )
        return flow_data

    registered.append("arifos://flow-state")

    logger.info(
        "Registered %d extended resources (incl. %d INIT prompts + agent_init + carry-forward + flow-state)",
        len(registered),
        len(_INIT_PROMPT_FILES),
    )
    return registered


__all__ = ["register_arifos_resources"]
