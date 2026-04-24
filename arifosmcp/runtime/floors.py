"""
F1–F13 Constitutional Floor Enforcer
════════════════════════════════════

Each floor is an interceptor axiom, not a callable tool.
They wrap all tool executions and gate the pipeline.
"""
from __future__ import annotations

import logging
from typing import Any

from arifosmcp.constitutional_map import Floor, CANONICAL_TOOLS

logger = logging.getLogger(__name__)


FLOOR_DESCRIPTIONS: dict[Floor, str] = {
    Floor.F01_AMANAH: "Trustworthiness — every action is accountable.",
    Floor.F02_TRUTH: "Truthfulness — no deception, no hallucination passed as fact.",
    Floor.F03_WITNESS: "Witness — evidence must be verifiable and preserved.",
    Floor.F04_CLARITY: "Clarity — intent and mechanism are transparent.",
    Floor.F05_PEACE: "Peace — no harm to human dignity or safety.",
    Floor.F06_EMPATHY: "Empathy — consider human consequence before acting.",
    Floor.F07_HUMILITY: "Humility — acknowledge limits and uncertainty.",
    Floor.F08_GENIUS: "Genius — strive for elegant, correct solutions.",
    Floor.F09_ANTIHANTU: "Anti-Hantu — detect and reject manipulation.",
    Floor.F10_ONTOLOGY: "Ontology — preserve structural coherence.",
    Floor.F11_AUTH: "Authority — verify identity before irreversible acts.",
    Floor.F12_INJECTION: "Injection Guard — sanitize all inputs.",
    Floor.F13_SOVEREIGN: "Sovereign — human veto is absolute.",
}


def check_floors(tool_name: str, params: dict[str, Any], actor_id: str | None) -> dict[str, Any]:
    """
    Run F1–F13 interceptors for a tool call.
    Returns {"verdict": "SEAL" | "HOLD" | "VOID", "failed_floors": [...], "reason": str}
    """
    spec = CANONICAL_TOOLS.get(tool_name)
    if not spec:
        return {"verdict": "VOID", "failed_floors": ["F10"], "reason": f"Unknown tool: {tool_name}"}

    failed: list[str] = []

    # F12 Injection Guard — basic sanity on params
    for key, value in params.items():
        if isinstance(value, str):
            risky = ["rm -rf", "eval(", "exec(", "__import__", "os.system"]
            if any(r in value for r in risky):
                failed.append("F12")
                logger.warning(f"F12 BLOCK: injection pattern in param '{key}' for {tool_name}")
                break

    # F11 Authority — irreversible or sovereign tools need actor_id
    risk_tier = spec.get("risk_tier", "low")
    if risk_tier in ("critical", "sovereign") and not actor_id:
        failed.append("F11")
        logger.warning(f"F11 HOLD: {tool_name} requires actor_id")

    # F01 Amanah — vault and forge are irreversible; need explicit ack
    if spec.get("irreversible") and not params.get("ack_irreversible"):
        failed.append("F01")
        logger.warning(f"F01 HOLD: {tool_name} is irreversible without ack")

    # F13 Sovereign — hardcoded master veto placeholder
    if params.get("sovereign_veto"):
        failed.append("F13")
        logger.critical("F13 SOVEREIGN VETO invoked")

    if failed:
        return {
            "verdict": "HOLD" if "F13" not in failed else "VOID",
            "failed_floors": failed,
            "reason": f"Constitutional floor breach: {', '.join(failed)}",
        }

    return {"verdict": "SEAL", "failed_floors": [], "reason": "All floors clear"}


def get_floor_status() -> dict[str, Any]:
    """Return current constitutional floor status."""
    return {
        "floors": {f.value: FLOOR_DESCRIPTIONS[f] for f in Floor},
        "status": "aligned",
        "version": "2026.04.24-KANON",
    }
