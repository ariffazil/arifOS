"""
arifOS Embodied arif_mind_reason — 333_MIND with full pipeline
═══════════════════════════════════════════════════════════════

Migration of arif_mind_reason through EmbodiedTool.run():

    RECEIVE → SENSE BOUND → CLASSIFY → CHECK AUTHORITY
    → CHECK REVERSIBILITY → SIMULATE → ACT OR HOLD
    → WITNESS → REVIEW

The embodied execution path:
1. preflight()  → run_preflight()  → EmbodiedDecision (SEAL/HOLD/VOID)
2. execute()    → _arif_mind_reason kernel (deterministic constitutional reasoning)
3. postflight() → run_postflight()  → EmbodiedToolEnvelope + witness record

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.embodied import EmbodiedTool
from arifosmcp.tools.reason import arif_mind_reason as _mind_reason_kernel


class ArifMindReasonEmbodied(EmbodiedTool):
    """
    Embodied arif_mind_reason — constitutional reasoning with full pipeline.

    Modes (from tools/mind_reason.py):
      reason       General constitutional reasoning with axiom trace.
      reflect      Introspective replay of prior reasoning steps.
      socratic     Socratic questioning mode.
      forge        Forge artifact generation.
      debate       Counterfactual position evaluation.

    Risk: T1 (low irreversible risk, reversible output)
    Domain: AOS
    """

    tool_id = "arif_mind_reason"
    tool_name = "arif_mind_reason"
    domain = "AOS"
    description = (
        "Structured reasoning with constitutional awareness — axiom trace, synthesis, verification"
    )
    risk_tier = "T1"
    reversibility = "reversible"
    blast_radius = "low"
    required_permissions = []
    required_floors = ["F02", "F07", "F08", "F10"]
    safe_compose_with = [
        "arif_sense_observe",
        "arif_evidence_fetch",
        "arif_heart_critique",
        "arif_kernel_route",
        "arif_memory_recall",
    ]
    dangerous_compose_with = [
        "arif_vault_seal",
        "arif_judge_deliberate",
        "arif_forge_execute",
    ]

    async def execute(self, params: dict, ctx: Any) -> dict:
        """
        Execute constitutional reasoning kernel.

        Args:
            params: {
                "mode": str,       # reason | reflect | socratic | forge | debate
                "query": str | None,
                "session_id": str | None,
                "actor_id": str | None,
                "context": dict | None,  # Optional session context
            }

        Returns:
            Synthesis dict with delta_bundle fields:
            - verdict, synthesis, confidence, omega_0
            - scars, floor_scores, entropy
            - facts, axioms_used, reasoning_trace
        """
        mode = params.get("mode", "reason")
        query = params.get("query")
        session_id = params.get("session_id")
        actor_id = params.get("actor_id")
        context = params.get("context")

        if context is None:
            context = {}
        if session_id:
            context["session_id"] = session_id

        result = _mind_reason_kernel(
            mode=mode,
            query=query,
            actor_id=actor_id,
            context=context,
        )

        if hasattr(result, "model_dump"):
            return result.model_dump()
        elif hasattr(result, "dict"):
            return result.dict()
        else:
            return dict(result) if result else {}
