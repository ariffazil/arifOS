"""
arifOS Embodied arif_mind_reason — 333_MIND with full pipeline
══════════════════════════════════════════════════════════════

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

import json
import logging
from datetime import datetime
from typing import Any

from arifosmcp.memory.policy_engine import MemoryPolicyEngine
from arifosmcp.memory.types import Authority, MemoryCandidate, MemoryType
from arifosmcp.tools.embodied import EmbodiedTool
from arifosmcp.tools.memory import arif_memory_recall
from arifosmcp.tools.reason import arif_mind_reason as _mind_reason_kernel

logger = logging.getLogger(__name__)

_policy_engine = MemoryPolicyEngine()


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
                "mode": str,       # reason | reflect | metabolize | ...
                "query": str | None,
                "session_id": str | None,
                "actor_id": str | None,
                "task": dict | None,
                "context": dict | None,
                "evidence": dict | None,
                "reasoning_control": dict | None,
            }

        Returns:
            Synthesis dict or MindResponse dict.
        """
        mode = params.get("mode", "reason")
        query = params.get("query")
        session_id = params.get("session_id")
        actor_id = params.get("actor_id")

        if mode == "metabolize":
            from arifosmcp.runtime.mind_reason import arif_mind_reason_v2
            from arifosmcp.schemas.mind_metabolism import MindRequest

            # ── 555_MEM: Recall relevant memory context BEFORE reasoning ──────────
            recalled_memories: list[str] = []
            memory_summary = ""
            try:
                recall_result = arif_memory_recall(
                    mode="search",
                    query=query or "",
                    session_id=session_id,
                    actor_id=actor_id or "anonymous",
                    limit=5,
                )
                if recall_result.get("ok") and recall_result.get("results"):
                    recalled_memories = [
                        r.get("content", "")[:500]
                        for r in recall_result["results"]
                        if r.get("content")
                    ]
                    memory_summary = "Prior context: " + " | ".join(recalled_memories[:3])
                    logger.debug(f"333_MIND recalled {len(recalled_memories)} memory items")
            except Exception as exc:
                logger.warning(f"333_MIND memory recall failed: {exc}")

            # Build MindContext with memory injection
            from arifosmcp.schemas.mind_metabolism import MindContext

            base_context = params.get("context", {}) or {}
            user_ctx = base_context.get("user_context", "") or ""
            enriched_user_ctx = (
                (user_ctx + "\n\n" + memory_summary).strip() if user_ctx else memory_summary
            )

            mind_ctx = MindContext(
                user_context=enriched_user_ctx or None,
                memory_context=recalled_memories,
            )

            # Construct v2 request
            request = MindRequest(
                query=query or "",
                mode=mode,
                session_id=session_id,
                actor_id=actor_id,
                task=params.get("task", {}),
                context=mind_ctx,
                evidence=params.get("evidence", {}),
                reasoning_control=params.get("reasoning_control", {}),
            )
            result = await arif_mind_reason_v2(request)

            # ── 555_MEM: Store reasoning outcome AFTER reasoning ─────────────────
            try:
                result_content = json.dumps(result, default=str)
                confidence = 0.7  # Reasoning has good confidence
                sensitivity = 0.1  # Low sensitivity unless domain is sensitive

                candidate = MemoryCandidate(
                    type=MemoryType.EPISODIC,
                    subject=query[:200] if query else "reasoning_output",
                    content=result_content[:10000],  # Truncate to avoid bloat
                    summary=(
                        result.get("synthesis", {}).get("bounded_answer", "")[:500]
                        if isinstance(result, dict)
                        else ""
                    ),
                    source_type="arif_mind_reason",
                    source_ref={
                        "mode": mode,
                        "session_id": session_id,
                        "actor_id": actor_id,
                    },
                    confidence=confidence,
                    authority=Authority.SYSTEM_INFERRED,
                    sensitivity=sensitivity,
                    tags=["reasoning", "metabolize", "333_MIND"],
                )

                allowed, reason, score = _policy_engine.evaluate(
                    candidate, actor_role="system", ctx={}
                )
                if allowed == "ALLOWED":
                    arif_memory_recall(
                        mode="store",
                        query=query or "reasoning",
                        session_id=session_id,
                        actor_id=actor_id or "anonymous",
                        content=result_content,
                        tags=["reasoning", "metabolize", "333_MIND"],
                    )
                    logger.debug(f"333_MIND stored outcome: score={score:.3f}")
                else:
                    logger.debug(f"333_MIND memory store held: {reason}")
            except Exception as exc:
                logger.warning(f"333_MIND memory store failed: {exc}")

        else:
            # Legacy v1 path
            context = params.get("context", {})
            if session_id:
                context["session_id"] = session_id

            result = _mind_reason_kernel(
                mode=mode,
                query=query,
                actor_id=actor_id,
                context=context,
            )

        # Handle both Pydantic models (MindResponse) and plain dicts (legacy v1)
        if hasattr(result, "model_dump"):  # type: ignore[attr-defined]
            return result.model_dump()  # type: ignore[attr-defined]
        if hasattr(result, "dict"):  # type: ignore[attr-defined]
            return result.dict()  # type: ignore[attr-defined]
        if isinstance(result, dict):
            return result
        return {}
