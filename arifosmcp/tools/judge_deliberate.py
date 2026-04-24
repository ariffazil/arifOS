"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE
═══════════════════════════════════════════════

Constitutional verdict engine.
"""
from __future__ import annotations

from arifosmcp.runtime.tools import _arif_judge_deliberate
from arifosmcp.schemas.verdict import VerdictOutput


def arif_judge_deliberate(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
) -> VerdictOutput:
    return VerdictOutput(
        **_arif_judge_deliberate(
            mode=mode,
            candidate=candidate,
            session_id=session_id,
            actor_id=actor_id,
            constitutional_chain_id=constitutional_chain_id,
        )
    )
