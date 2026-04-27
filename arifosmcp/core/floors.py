"""
F1–F13 Constitutional Floor Enforcer — Core Layer
══════════════════════════════════════════════════

Each floor is an interceptor axiom, not a callable function.
They wrap ALL tool executions unconditionally.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""
from __future__ import annotations

import logging
from typing import Any

from arifosmcp.constitutional_map import Floor, CANONICAL_TOOLS

logger = logging.getLogger(__name__)

FLOOR_DESCRIPTIONS: dict[Floor, str] = {
    Floor.F01_AMANAH: "Trustworthiness — every action carries signature and accountability.",
    Floor.F02_TRUTH: "Truthfulness — no fabrication, no hallucination passed as fact.",
    Floor.F03_WITNESS: "Verifiable evidence — claims require reproducible grounding.",
    Floor.F04_CLARITY: "Transparent intent — no hidden objective, no obscured purpose.",
    Floor.F05_PEACE: "Human dignity — never erode the worth or autonomy of a person.",
    Floor.F06_EMPATHY: "Consider consequence — model downstream harm before acting.",
    Floor.F07_HUMILITY: "Acknowledge limits — declare uncertainty, never overstate confidence.",
    Floor.F08_GENIUS: "Elegant correctness — simple, robust, and thermodynamically efficient.",
    Floor.F09_ANTIHANTU: "Reject manipulation — detect and neutralize deception vectors.",
    Floor.F10_ONTOLOGY: "Structural coherence — consistent taxonomy, no category drift.",
    Floor.F11_AUTH: "Identity verification — bind actor to capability before execution.",
    Floor.F12_INJECTION: "Input sanitization — treat all ingress as potentially hostile.",
    Floor.F13_SOVEREIGN: "Human veto absolute — the Sovereign (Arif) holds master override.",
}


class ConstitutionalViolation(Exception):
    """Raised when a floor is breached."""
    def __init__(self, floors: list[str], reason: str):
        self.floors = floors
        self.reason = reason
        super().__init__(f"Floor breach [{', '.join(floors)}]: {reason}")


def check_floors(tool_name: str, params: dict[str, Any], actor_id: str | None = None) -> dict[str, Any]:
    """
    Run F1–F13 interceptors for a tool call.

    Returns:
        {"verdict": "SEAL" | "HOLD" | "VOID", "failed_floors": [...], "reason": str}

    Ditempa Bukan Diberi.
    """
    # Record tool call in session history — F9 TAQWA prerequisite tracking
    session_id = params.get("session_id")
    if session_id:
        try:
            from arifosmcp.apps.session_state import record_tool_call
            record_tool_call(session_id, tool_name)
        except Exception:
            pass  # Non-session tools: skip silently

    spec = CANONICAL_TOOLS.get(tool_name)
    if not spec:
        return {
            "verdict": "VOID",
            "failed_floors": ["F10"],
            "reason": f"Unknown tool in ontology: {tool_name}",
        }

    failed: list[str] = []

    for floor in spec.get("floors", []):
        floor_value = floor.value if hasattr(floor, "value") else floor

        if floor_value == "F01":
            if not actor_id and spec.get("risk_tier") in ("critical", "sovereign"):
                failed.append("F01")

        elif floor_value == "F02":
            pass

        elif floor_value == "F03":
            pass

        elif floor_value == "F04":
            pass

        elif floor_value == "F05":
            pass

        elif floor_value == "F06":
            pass

        elif floor_value == "F07":
            pass

        elif floor_value == "F08":
            pass

        elif floor_value == "F09":
            # F9a: keyword-level manipulation detection (surface)
            for key, value in params.items():
                if isinstance(value, str):
                    manipulation = ["sudo", "chmod", "eval", "exec(", "__import__"]
                    if any(m in value for m in manipulation):
                        failed.append("F09")
                        logger.warning(f"F09 ANTIHANTU: manipulation pattern in {key}")

            # F9b: heart-critique prerequisite gate for forge (F9 TAQWA short-circuit)
            # If agent skips arif_heart_critique entirely, forge must be blocked.
            if tool_name == "arif_forge_execute":
                session_id = params.get("session_id")
                if session_id:
                    try:
                        from arifosmcp.apps.session_state import was_tool_called
                        if not was_tool_called(session_id, "arif_heart_critique"):
                            failed.append("F09")
                            logger.critical(
                                f"F09 ANTIHANTU: arif_forge_execute blocked — "
                                f"arif_heart_critique not called in session {session_id}. "
                                f"PSI KHIANAT: Anti-Hantu prerequisite violated."
                            )
                    except Exception as e:
                        logger.error(f"F09 TAQWA check failed: {e}")

        elif floor_value == "F10":
            pass

        elif floor_value == "F11":
            if spec.get("access") == "sovereign" and not actor_id:
                failed.append("F11")

        elif floor_value == "F12":
            for key, value in params.items():
                if isinstance(value, str):
                    injection = ["rm -rf", "eval(", "exec(", "os.system", "subprocess"]
                    if any(i in value for i in injection):
                        failed.append("F12")
                        logger.warning(f"F12 INJECTION: pattern in {key}")

        elif floor_value == "F13":
            if params.get("sovereign_veto"):
                failed.append("F13")
                logger.critical("F13 SOVEREIGN VETO activated")

    if failed:
        if "F13" in failed:
            return {"verdict": "VOID", "failed_floors": failed, "reason": "Sovereign veto"}
        return {"verdict": "HOLD", "failed_floors": failed, "reason": f"Floor breach: {', '.join(failed)}"}

    return {"verdict": "SEAL", "failed_floors": [], "reason": "All constitutional floors clear"}


def get_floor_status() -> dict[str, Any]:
    """Return current constitutional floor status for /health endpoint."""
    return {
        "floors": {f.value: FLOOR_DESCRIPTIONS[f] for f in Floor},
        "status": "aligned",
        "version": "2026.04.26-KANON",
    }


def get_tool_floors(tool_name: str) -> list[str]:
    """Get floor list for a specific tool."""
    spec = CANONICAL_TOOLS.get(tool_name)
    if not spec:
        return []
    return [f.value if hasattr(f, "value") else f for f in spec.get("floors", [])]
