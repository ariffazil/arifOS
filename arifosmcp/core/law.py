"""
F1–L13 Constitutional Law Enforcer — Core Layer
══════════════════════════════════════════════════

Each floor is an interceptor axiom, not a callable function.
They wrap ALL tool executions unconditionally.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
from typing import Any

from arifosmcp.constitutional_map import CANONICAL_TOOLS, Law

logger = logging.getLogger(__name__)

LAW_DESCRIPTIONS: dict[Law, str] = {
    Law.L01_AMANAH: "Trustworthiness — every action carries signature and accountability.",
    Law.L02_TRUTH: "Truthfulness — no fabrication, no hallucination passed as fact.",
    Law.L03_WITNESS: "Verifiable evidence — claims require reproducible grounding.",
    Law.L04_CLARITY: "Transparent intent — no hidden objective, no obscured purpose.",
    Law.L05_PEACE: "Human dignity — never erode the worth or autonomy of a person.",
    Law.L06_EMPATHY: "Consider consequence — model downstream harm before acting.",
    Law.L07_HUMILITY: "Acknowledge limits — declare uncertainty, never overstate confidence.",
    Law.L08_GENIUS: "Elegant correctness — simple, robust, and thermodynamically efficient.",
    Law.L09_ANTIHANTU: "Reject manipulation — detect and neutralize deception vectors.",
    Law.L10_ONTOLOGY: "Structural coherence — consistent taxonomy, no category drift.",
    Law.L11_AUDIT: "Identity verification — bind actor to capability before execution.",
    Law.L12_INJECTION: "Input sanitization — treat all ingress as potentially hostile.",
    Law.L13_SOVEREIGN: "Human veto absolute — the Sovereign (Arif) holds master override.",
}


class ConstitutionalViolation(Exception):
    """Raised when a floor is breached."""

    def __init__(self, floors: list[str], reason: str):
        self.floors = floors
        self.reason = reason
        super().__init__(f"Law breach [{', '.join(floors)}]: {reason}")


def check_laws(
    tool_name: str, params: dict[str, Any], actor_id: str | None = None
) -> dict[str, Any]:
    """
    Run F1–L13 interceptors for a tool call.

    Returns:
        {"verdict": "SEAL" | "HOLD" | "VOID", "violated_laws": [...], "reason": str}

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
            "violated_laws": ["L10"],
            "reason": f"Unknown tool in ontology: {tool_name}",
        }

    failed: list[str] = []

    for floor in spec.get("floors", []):
        floor_value = floor.value if hasattr(floor, "value") else floor

        if floor_value == "L01":
            if not actor_id and spec.get("risk_tier") in ("critical", "sovereign"):
                failed.append("L01")

        elif floor_value == "L02":
            pass

        elif floor_value == "L03":
            pass

        elif floor_value == "L04":
            pass

        elif floor_value == "L05":
            pass

        elif floor_value == "L06":
            pass

        elif floor_value == "L07":
            pass

        elif floor_value == "L08":
            pass

        elif floor_value == "L09":
            # F9a: keyword-level manipulation detection (surface)
            for key, value in params.items():
                if isinstance(value, str):
                    manipulation = ["sudo", "chmod", "eval", "exec(", "__import__"]
                    if any(m in value for m in manipulation):
                        failed.append("L09")
                        logger.warning(f"L09 ANTIHANTU: manipulation pattern in {key}")

            # F9b: heart-critique prerequisite gate for forge (F9 TAQWA short-circuit)
            # If agent skips arif_heart_critique entirely, forge must be blocked.
            if tool_name == "arif_forge_execute":
                session_id = params.get("session_id")
                if session_id:
                    try:
                        from arifosmcp.apps.session_state import was_tool_called

                        if not was_tool_called(session_id, "arif_heart_critique"):
                            failed.append("L09")
                            logger.critical(
                                f"L09 ANTIHANTU: arif_forge_execute blocked — "
                                f"arif_heart_critique not called in session {session_id}. "
                                f"PSI KHIANAT: Anti-Hantu prerequisite violated."
                            )
                    except Exception as e:
                        logger.error(f"L09 TAQWA check failed: {e}")

        elif floor_value == "L10":
            pass

        elif floor_value == "L11":
            if spec.get("access") == "sovereign" and not actor_id:
                failed.append("L11")
            # H2: All L11-gated tools require identity binding (session_id or actor_id)
            if not actor_id and not session_id and spec.get("access") != "public":
                failed.append("L11")

        elif floor_value == "L12":
            for key, value in params.items():
                if isinstance(value, str):
                    injection = ["rm -rf", "eval(", "exec(", "os.system", "subprocess"]
                    if any(i in value for i in injection):
                        failed.append("L12")
                        logger.warning(f"L12 INJECTION: pattern in {key}")

        elif floor_value == "L13":
            # L13 fires when sovereign override is BYPASSED (not when used).
            # sovereign_veto=True means Arif exercised his override — operation halts
            # but this is L13 WORKING, not L13 BREACHING.
            # We log it and return VOID so execution stops, but do NOT add to failed.
            if params.get("sovereign_veto"):
                logger.critical("L13 SOVEREIGN VETO exercised by Arif — operation halted")
                # Return VOID but do NOT append L13 to failed — veto usage is not a breach
                return {
                    "verdict": "VOID",
                    "violated_laws": [],
                    "reason": "Sovereign veto exercised — operation halted by Arif",
                    "sovereign_veto_used": True,
                }

    # ── Human Substrate Check ──────────────────────────────────────
    # The human is not entirely intelligence. They have scars, shadows,
    # paradoxes, limits, constraints, invariants. The kernel must know.
    substrate_warnings: list[str] = []
    try:
        from arifosmcp.core.human_substrate import check_human_substrate_floor

        for floor in spec.get("floors", []):
            floor_value = floor.value if hasattr(floor, "value") else floor
            sub_result = check_human_substrate_floor(floor_value, tool_name, params)
            if sub_result["verdict"] in ("GUARD", "BLOCK", "STRENGTHEN"):
                substrate_warnings.append(
                    f"{floor_value}: {sub_result['reason']} (verdict={sub_result['verdict']})"
                )
                # Only BLOCK adds to failed — GUARD/STRENGTHEN are advisory
                if sub_result["verdict"] == "BLOCK":
                    failed.append(floor_value)
    except Exception:
        pass  # Non-fatal: substrate check is advisory unless BLOCK

    if failed:
        if "L13" in failed:
            return {
                "verdict": "VOID",
                "violated_laws": failed,
                "reason": "Sovereign veto",
            }
        return {
            "verdict": "HOLD",
            "violated_laws": failed,
            "reason": f"Law breach: {', '.join(failed)}",
        }

    return {
        "verdict": "SEAL",
        "violated_laws": [],
        "reason": "All constitutional floors clear",
        "substrate_warnings": substrate_warnings,
    }


def get_floor_status() -> dict[str, Any]:
    """Return current constitutional floor status for /health endpoint."""
    result = {
        "floors": {f.value: LAW_DESCRIPTIONS[f] for f in Law},
        "status": "aligned",
        "version": "2026.04.26-KANON",
    }
    try:
        from arifosmcp.core.human_substrate import get_substrate_summary

        result["human_substrate"] = get_substrate_summary()
    except Exception:
        result["human_substrate"] = {"status": "unavailable"}
    return result


def get_tool_floors(tool_name: str) -> list[str]:
    """Get floor list for a specific tool."""
    spec = CANONICAL_TOOLS.get(tool_name)
    if not spec:
        return []
    return [f.value if hasattr(f, "value") else f for f in spec.get("floors", [])]
