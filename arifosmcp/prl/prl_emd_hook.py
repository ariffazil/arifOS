"""
prl_emd_hook.py — PRL → EMD Stack Integration Hook
═══════════════════════════════════════════════════

Lightweight, non-invasive hook that injects PRL precedent constraints
into the arif_think reasoning pipeline.

Usage (inside arif_think mode=reason):
    from arifosmcp.prl.prl_emd_hook import prl_pre_reason_check

    constraints = await prl_pre_reason_check(query=query, actor_id=actor_id)
    if constraints:
        # Inject into reasoning prompt as structural constraints
        prompt = constraints + "\\n\\n" + prompt

Design principles:
  - Non-fatal: PRL failure never blocks reasoning
  - Async: Qdrant call is non-blocking in the pipeline
  - F9-compliant: Constraints are structural, not "memories"
  - Low blast radius: Import-time only, no monkey-patching

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────
PRL_EMD_CHECK_ENABLED = True  # Master kill-switch for PRL in EMD pipeline


async def prl_pre_reason_check(
    query: str,
    blast_radius: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Run PRL precedent check before arif_think reasoning.

    Call this from arif_think(mode=reason) BEFORE the LLM reasoning step.

    Args:
        query: The user's query / intent text
        blast_radius: Optional override.  Auto-classified if None.
        actor_id: Calling actor for audit
        session_id: Governing session

    Returns:
        {
            "verdict": "PRL_MATCH" | "PRL_NONE" | "PRL_OMEGA0_HOLD" | "PRL_ERROR",
            "constraint_block": str | None,       # Formatted for prompt injection
            "constraints": list[PrlConstraint],   # Raw constraint objects
            "query_blast_radius": str,
            "search_ms": float,
            "omega0_triggered": bool,
        }
    """
    result: dict[str, Any] = {
        "verdict": "PRL_NONE",
        "constraint_block": None,
        "constraints": [],
        "query_blast_radius": blast_radius or "L2_SYSTEM",
        "search_ms": 0.0,
        "omega0_triggered": False,
        "omega0_reason": "",
        "error": "",
    }

    if not PRL_EMD_CHECK_ENABLED:
        return result

    try:
        from arifosmcp.prl import PrlGate

        gate = PrlGate()
        gate_result = await gate.interrogate(
            query_text=query,
            blast_radius=blast_radius,
        )

        result["verdict"] = gate_result.verdict
        result["query_blast_radius"] = gate_result.query_blast_radius
        result["search_ms"] = gate_result.search_ms
        result["omega0_triggered"] = gate_result.omega0_triggered
        result["omega0_reason"] = gate_result.omega0_reason
        result["error"] = gate_result.error

        if gate_result.constraints:
            # Build F9-compliant constraint block for prompt injection
            blocks = []
            for c in gate_result.constraints:
                blocks.append(c.to_prompt_block())
            result["constraint_block"] = "\n".join(blocks)
            result["constraints"] = [
                {
                    "seal_id": c.seal_id,
                    "blast_radius": c.blast_radius,
                    "cosine_score": c.cosine_score,
                    "constraint_text": c.constraint_text[:256],
                }
                for c in gate_result.constraints
            ]

            logger.info(
                "PRL matched %d precedent(s) for query (τ≥0.95, blast_radius=%s)",
                len(gate_result.constraints),
                result["query_blast_radius"],
            )

        elif gate_result.omega0_triggered:
            logger.warning(
                "PRL Ω₀ triggered — geometric match but contextual ambiguity: %s",
                gate_result.omega0_reason,
            )

    except ImportError:
        logger.debug("PRL not available — skipping pre-reason check")
        result["verdict"] = "PRL_NONE"
        result["error"] = "PRL not imported"
    except Exception as exc:
        logger.error("PRL pre-reason check failed: %s", exc)
        result["verdict"] = "PRL_ERROR"
        result["error"] = str(exc)[:200]

    return result


def prl_pre_reason_check_sync(
    query: str,
    blast_radius: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Synchronous wrapper for prl_pre_reason_check.

    Use when the caller is not async (e.g., CLI tools, test harnesses).
    """
    import asyncio

    return asyncio.run(
        prl_pre_reason_check(
            query=query,
            blast_radius=blast_radius,
            actor_id=actor_id,
            session_id=session_id,
        )
    )
