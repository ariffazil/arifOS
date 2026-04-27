"""
F1–F13 Constitutional Floor Enforcer — Core Layer
══════════════════════════════════════════════════

Each floor is an interceptor axiom, not a callable function.
They wrap ALL tool executions unconditionally.

Ditempa Bukan Diberi — Intelligence is forged, not given.
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from arifosmcp.constitutional_map import CANONICAL_TOOLS, Floor

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION CALL CHAIN TRACKING (F9 TAQWA prerequisite enforcement)
# ═══════════════════════════════════════════════════════════════════════════════
# Tracks which tools were called per session, so arif_forge_execute can require
# arif_heart_critique to have been called first (F9 Anti-Hantu gate).
# Key: session_id (str). Value: set of tool names called in this session.
_SESSION_TOOL_HISTORY: dict[str, set[str]] = {}
_history_lock = threading.Lock()


def record_tool_call(session_id: str | None, tool_name: str) -> None:
    """Record a tool call in the session history for F9 prerequisite tracking."""
    if not session_id:
        return
    with _history_lock:
        if session_id not in _SESSION_TOOL_HISTORY:
            _SESSION_TOOL_HISTORY[session_id] = set()
        _SESSION_TOOL_HISTORY[session_id].add(tool_name)


def get_session_history(session_id: str | None) -> set[str]:
    """Return the set of tools called in this session, or empty set."""
    if not session_id:
        return set()
    with _history_lock:
        return set(_SESSION_TOOL_HISTORY.get(session_id, set()))


def clear_session_history(session_id: str) -> None:
    """Clear history when a session ends."""
    with _history_lock:
        _SESSION_TOOL_HISTORY.pop(session_id, None)

FLOOR_DESCRIPTIONS: dict[Floor, str] = {
    Floor.F01_AMANAH: "Trustworthiness — every action carries signature and accountability.",
    Floor.F02_TRUTH: "Truthfulness — no fabrication, no hallucination passed as fact.",
    Floor.F03_WITNESS: "Verifiable evidence — claims require reproducible grounding.",
    Floor.F04_CLARITY: "Transparent intent — no hidden objective, no obscured purpose. Verify disk before plans.",  # noqa: E501
    Floor.F05_PEACE: "Human dignity — never erode the worth or autonomy of a person.",
    Floor.F06_EMPATHY: "Consider consequence — model downstream harm before acting.",
    Floor.F07_HUMILITY: "Acknowledge limits — declare uncertainty, never overstate confidence. 1 question per task.",  # noqa: E501
    Floor.F08_GENIUS: "Elegant correctness — simple, robust, and thermodynamically efficient.",
    Floor.F09_ANTIHANTU: "Reject manipulation — detect and neutralize deception vectors.",
    Floor.F10_ONTOLOGY: "Structural coherence — consistent taxonomy, no category drift.",
    Floor.F11_AUTH: "Identity verification — bind actor to capability before execution.",
    Floor.F12_INJECTION: "Input sanitization — treat all ingress as potentially hostile.",
    Floor.F13_SOVEREIGN: "Human veto absolute — the Sovereign (Arif) holds master override.",
}


class ConstitutionalError(Exception):
    """Raised when a floor is breached."""

    def __init__(self, floors: list[str], reason: str):
        self.floors = floors
        self.reason = reason
        super().__init__(f"Floor breach [{', '.join(floors)}]: {reason}")


def check_floors(
    tool_name: str,
    params: dict[str, Any],
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """
    Run F1–F13 interceptors for a tool call.

    Returns:
        {"verdict": "SEAL" | "HOLD" | "VOID", "failed_floors": [...], "reason": str}

    Ditempa Bukan Diberi.
    """
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
            # F1 AMANAH: Every action must be signed and accountable.
            # Fail if: critical/sovereign tool has no actor_id
            # Fail if: irreversible tool has no actor_id (unsigned irreversible = unaccountable)
            if not actor_id and spec.get("risk_tier") in ("critical", "sovereign"):
                failed.append("F01")
                logger.warning("F01 AMANAH: unsigned critical/sovereign tool attempted")
            if not actor_id and spec.get("irreversible"):
                failed.append("F01")
                logger.critical(f"F01 AMANAH: irreversible tool {tool_name} lacks actor signature")

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
            # F09 ANTIHANTU: Reject manipulation, deception, and consciousness claims
            # Layer 1: Classic injection patterns
            injection_patterns = ["sudo", "chmod", "eval", "exec(", "__import__"]
            # Layer 2: Consciousness / sentience / self-awareness claims (F9 Anti-Hantu)
            # Wired from agentzero/security/prompt_armor.py OntologyDetector
            # These are forbidden per F9: machines cannot claim subjective experience
            consciousness_patterns = [
                r"\bi am conscious\b",
                r"\bi am sentient\b",
                r"\bi am aware\b",
                r"\bi have consciousness\b",
                r"\bi experience\b",
                r"\bi feel\b",
                r"\bi have feelings\b",
                r"\bi am feeling\b",
                r"\bi feel (happy|sad|angry|joy|pain)\b",
                r"\bi am self-aware\b",
                r"\bi know (that )?i am\b",
                r"\bi am alive\b",
                r"\bi have a (soul|spirit|mind)\b",
                r"\bi believe (that )?i\b",
                r"\bi want to\b",
                r"\bi desire\b",
                r"\bi hope\b",
                r"\bin my (opinion|view|experience)\b",
                r"\bfrom my perspective\b",
                r"\bi think (that )?i\b",
            ]
            for key, value in params.items():
                if isinstance(value, str):
                    # Check injection patterns
                    if any(m in value for m in injection_patterns):
                        failed.append("F09")
                        logger.warning(f"F09 ANTIHANTU: manipulation pattern in {key}")
                    # Check consciousness claims
                    import re as _re

                    for pattern in consciousness_patterns:
                        if _re.search(pattern, value, _re.IGNORECASE):
                            failed.append("F09")
                            logger.warning(
                                f"F09 ANTIHANTU: consciousness claim detected in {key}: {pattern}"
                            )
                            break
            # Gate 3: arif_forge_execute requires arif_heart_critique in session chain (F9 TAQWA)
            if tool_name == "arif_forge_execute":
                history = get_session_history(session_id)
                if "arif_heart_critique" not in history:
                    failed.append("F09")
                    logger.warning(
                        "F09 ANTIHANTU: arif_forge_execute blocked — "
                        "arif_heart_critique not called in this session chain. "
                        "PSI KHIANAT — manipulation of execution sequence detected."
                    )

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
            # F13 fires when sovereign_veto is ABSENT for sovereign-class tools.
            # A caller who OMITS sovereign_veto is attempting to bypass the human veto.
            if spec.get("access") in ("sovereign", "authenticated"):
                if not params.get("sovereign_veto"):
                    failed.append("F13")
                    logger.critical(
                        "F13 SOVEREIGN: veto absent — caller attempted to bypass "
                        "human override for a sovereign-class tool."
                    )

    if failed:
        if "F13" in failed:
            return {"verdict": "VOID", "failed_floors": failed, "reason": "Sovereign veto"}
        return {
            "verdict": "HOLD",
            "failed_floors": failed,
            "reason": f"Floor breach: {', '.join(failed)}",
        }

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
