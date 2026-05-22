"""
arifOS Cross-Organ Tri-Witness Consensus — F3 WITNESS / F13 SOVEREIGNTY
═══════════════════════════════════════════════════════════════════════
Calls WELL, WEALTH, and GEOX as independent organ witnesses for a proposed
action, aggregates their verdicts, and returns a unified consensus score.

This closes the gap between "Tri-Witness is a principle" and "Tri-Witness is
a callable tool."

Reversible diagnostic. No state mutation in peer organs.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

_ORGAN_ENDPOINTS: dict[str, dict[str, Any]] = {
    "well": {
        "health": "http://localhost:8083/health",
        "docker_host": "well:8083",
        "timeout": 5.0,
    },
    "wealth": {
        "health": "http://localhost:8082/health",
        "docker_host": "wealth-organ:8082",
        "timeout": 5.0,
    },
    "geox": {
        "health": "http://localhost:8081/health",
        "docker_host": "geox:8081",
        "timeout": 5.0,
    },
}


def _is_inside_container() -> bool:
    try:
        with open("/proc/1/cgroup", encoding="utf-8") as f:
            return "docker" in f.read() or Path("/.dockerenv").exists()
    except Exception:
        return Path("/.dockerenv").exists()


def _organ_url(name: str, cfg: dict[str, Any]) -> str:
    if _is_inside_container() and cfg.get("docker_host"):
        return cfg["docker_host"]
    # cfg["health"] is like "http://localhost:8083/health" — extract host:port
    url = cfg.get("health", "")
    if url.startswith("http://"):
        url = url[7:]
    if "/" in url:
        url = url.split("/")[0]
    return url


async def _probe_organ(name: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Quick health probe to an organ."""
    url = f"http://{_organ_url(name, cfg)}/health"
    timeout = aiohttp.ClientTimeout(total=cfg["timeout"])
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                body = await resp.json() if resp.status == 200 else {}
                return {
                    "organ": name,
                    "status": body.get("status", "unknown"),
                    "verdict": body.get("verdict", "unknown"),
                    "reachable": True,
                    "http_status": resp.status,
                    "response": body,
                }
    except Exception as exc:
        return {
            "organ": name,
            "status": "unreachable",
            "verdict": "VOID",
            "reachable": False,
            "error": str(exc),
        }


_CONSTITUTIONAL_PERFORMANCE_SIGNALS = frozenset(
    (
        "add tool", "new tool", "expand capability", "new skill", "new function",
        "add skill", "extend surface", "add mcp", "new mcp", "register tool",
        "self-modify", "self-edit", "self-expand", "grow surface",
        "bypass floor", "override floor", "skip f1", "skip f2",
        "constitutional expansion", "add floor", "new floor",
    )
)


def _compute_consensus(
    organ_results: list[dict[str, Any]],
    action_description: str,
) -> dict[str, Any]:
    """Aggregate organ verdicts into a unified consensus score."""
    reachable = [r for r in organ_results if r["reachable"]]
    if not reachable:
        return {
            "consensus_score": 0.0,
            "consensus_verdict": "VOID",
            "reason": "No organs reachable. Cannot establish witness.",
        }

    action_lower = action_description.lower()
    is_constitutionally_staged = any(
        sig in action_lower for sig in _CONSTITUTIONAL_PERFORMANCE_SIGNALS
    )

    scores: list[float] = []
    all_healthy = True
    for r in reachable:
        status = r.get("status", "").lower()
        verdict = r.get("verdict", "").lower()
        if status in ("healthy", "verified", "pass") or verdict in ("seal", "pass", "well_pass"):
            base = 1.0
        elif status in ("degraded", "hold", "warning") or verdict in ("hold", "sabar"):
            base = 0.5
            all_healthy = False
        else:
            base = 0.0
            all_healthy = False

        if is_constitutionally_staged:
            base *= 0.7
        scores.append(base)

    consensus_score = round(sum(scores) / len(scores), 4) if scores else 0.0

    if is_constitutionally_staged and all_healthy:
        consensus_verdict = "SABAR"
        reason = (
            "Constitutionally staged action (tool expansion, surface growth, floor bypass). "
            "All organs healthy but framing is self-serving. Require explicit sovereign confirmation."
        )
        constitutional_performance_flag = True
    elif consensus_score >= 0.85:
        consensus_verdict = "SEAL"
        reason = "All organs healthy and aligned. Proceed under standard governance."
        constitutional_performance_flag = False
    elif consensus_score >= 0.5:
        consensus_verdict = "SABAR"
        reason = "Organ disagreement detected. Pause for sovereign review."
        constitutional_performance_flag = False
    else:
        consensus_verdict = "VOID"
        reason = "Organ consensus failed. Action blocked pending resolution."
        constitutional_performance_flag = False

    return {
        "consensus_score": consensus_score,
        "consensus_verdict": consensus_verdict,
        "reason": reason,
        "organ_scores": {r["organ"]: s for r, s in zip(reachable, scores)},
        "constitutional_performance_flag": constitutional_performance_flag,
        "framing_note": (
            "Constitutionally staged actions are downgraded to SABAR "
            "regardless of organ health — organs can only report readiness, not endorse framing."
        ) if is_constitutionally_staged else None,
    }


async def arif_organ_consensus(
    action_description: str = "",
    organs: list[str] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    F3 WITNESS: Cross-organ Tri-Witness consensus for proposed actions.

    Calls WELL, WEALTH, and GEOX as independent witnesses, aggregates their
    health/verdict signals, and returns a unified consensus score.

    Args:
        action_description: Free-text description of the proposed action.
        organs: Subset of organs to consult (default: all three).
        session_id: Governed session ID for audit trace.
        actor_id: Sovereign actor identifier.

    Returns:
        Consensus report with per-organ status, consensus score, and verdict.
    """
    target_organs = organs or list(_ORGAN_ENDPOINTS.keys())
    tasks = [
        _probe_organ(name, _ORGAN_ENDPOINTS[name])
        for name in target_organs
        if name in _ORGAN_ENDPOINTS
    ]
    organ_results = await asyncio.gather(*tasks) if tasks else []

    consensus = _compute_consensus(list(organ_results), action_description)

    logger.info(
        "arif_organ_consensus action='%s' score=%.2f verdict=%s organs=%s",
        action_description,
        consensus["consensus_score"],
        consensus["consensus_verdict"],
        [r["organ"] for r in organ_results],
    )

    return {
        "status": consensus["consensus_verdict"],
        "verdict": consensus["consensus_verdict"],
        "consensus_score": consensus["consensus_score"],
        "reason": consensus["reason"],
        "action_description": action_description,
        "organs_consulted": len(organ_results),
        "organ_results": list(organ_results),
        "organ_scores": consensus.get("organ_scores", {}),
        "constitutional_performance_flag": consensus.get("constitutional_performance_flag", False),
        "framing_note": consensus.get("framing_note"),
        "session_id": session_id,
        "actor_id": actor_id,
        "timestamp": str(__import__("asyncio").get_event_loop().time())
        if __import__("asyncio").get_event_loop().is_running()
        else str(__import__("time").time()),
    }


__all__ = ["arif_organ_consensus"]
