"""
arifOS MCP Recall Tool - Recall memories from L7 (Mem0 + Qdrant).

This tool performs semantic search to find relevant prior interactions.
All recalled memories are capped at 0.85 confidence (INV-4).
"""

from __future__ import annotations

from ..models import RecallRequest, RecallResponse, RecallMemory


def arifos_recall(request: RecallRequest) -> RecallResponse:
    """
    Recall memories from L7 memory layer.

    Performs semantic search to find relevant prior interactions
    for the given user and prompt.

    IMPORTANT: Recalled memories are suggestions, NOT facts (INV-4).

    Args:
        request: RecallRequest with user_id and prompt

    Returns:
        RecallResponse with memories and confidence ceiling
    """
    try:
        from arifos_core.memory import Memory, recall_at_stage_111

        memory = Memory()

        if not memory.is_enabled():
            return RecallResponse(
                memories=[],
                confidence_ceiling=0.85,
                l7_available=False,
                caveat="L7 memory is disabled. No memories recalled.",
            )

        # Use pipeline integration function for recall
        recall_result = recall_at_stage_111(
            query=request.prompt,
            user_id=request.user_id,
            top_k=request.max_results,
        )

        # Convert to response format
        memories = []
        if recall_result and hasattr(recall_result, "memories"):
            for mem in recall_result.memories:
                memories.append(
                    RecallMemory(
                        memory_id=getattr(mem, "memory_id", None),
                        content=getattr(mem, "content", ""),
                        score=min(getattr(mem, "score", 0.0), 0.85),  # Cap at ceiling
                        timestamp=getattr(mem, "timestamp", None),
                    )
                )

        return RecallResponse(
            memories=memories,
            confidence_ceiling=0.85,
            l7_available=True,
            caveat="Recalled memories are suggestions, not facts. (INV-4)",
        )

    except ImportError:
        return RecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat="L7 memory module not available.",
        )
    except Exception as e:
        # Fail-open: return empty results on error
        return RecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat=f"L7 memory unavailable: {str(e)}",
        )
