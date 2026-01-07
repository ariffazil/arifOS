"""
arifOS API Memory Routes - L7 memory recall and search.

All memory operations are fail-open - if L7 is unavailable,
endpoints return empty results with l7_available=False.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..models import (
    MemoryRecallRequest,
    MemoryRecallResponse,
    MemorySearchRequest,
    MemoryHit,
)

router = APIRouter(prefix="/memory", tags=["memory"])


# =============================================================================
# MEMORY ENDPOINTS
# =============================================================================

@router.get("/recall", response_model=MemoryRecallResponse)
async def recall_memories(
    user_id: str = Query(..., min_length=1, description="User ID for memory isolation"),
    prompt: str = Query(..., min_length=1, description="Query prompt for semantic search"),
    max_results: int = Query(default=5, ge=1, le=20, description="Maximum memories to return"),
) -> MemoryRecallResponse:
    """
    Recall relevant memories from L7 (Mem0 + Qdrant).

    This endpoint performs semantic search to find relevant prior interactions.
    All recalled memories are capped at 0.85 confidence (INV-4).

    IMPORTANT: Recalled memories are suggestions, NOT facts.
    """
    try:
        from arifos_core.memory import Memory, recall_at_stage_111

        memory = Memory()

        if not memory.is_enabled():
            return MemoryRecallResponse(
                memories=[],
                confidence_ceiling=0.85,
                l7_available=False,
                caveat="L7 memory is disabled. No memories recalled.",
            )

        # Use the pipeline integration function for recall
        recall_result = recall_at_stage_111(
            query=prompt,
            user_id=user_id,
            top_k=max_results,
        )

        # Convert to API response format
        memories = []
        if recall_result and hasattr(recall_result, "memories"):
            for mem in recall_result.memories:
                memories.append(
                    MemoryHit(
                        memory_id=getattr(mem, "memory_id", None),
                        content=getattr(mem, "content", ""),
                        score=min(getattr(mem, "score", 0.0), 0.85),  # Cap at ceiling
                        user_id=getattr(mem, "user_id", user_id),
                        metadata=getattr(mem, "metadata", {}),
                        timestamp=getattr(mem, "timestamp", None),
                    )
                )

        return MemoryRecallResponse(
            memories=memories,
            confidence_ceiling=0.85,
            l7_available=True,
            caveat="Recalled memories are suggestions, not facts. (INV-4)",
        )

    except ImportError:
        return MemoryRecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat="L7 memory module not available.",
        )
    except Exception as e:
        # Fail-open: return empty results on error
        return MemoryRecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat=f"L7 memory unavailable: {str(e)}",
        )


@router.post("/search", response_model=MemoryRecallResponse)
async def search_memories(request: MemorySearchRequest) -> MemoryRecallResponse:
    """
    Search L7 memories with custom parameters.

    Similar to recall but with more control over search parameters.
    """
    try:
        from arifos_core.memory import Memory

        memory = Memory()

        if not memory.is_enabled():
            return MemoryRecallResponse(
                memories=[],
                confidence_ceiling=0.85,
                l7_available=False,
                caveat="L7 memory is disabled.",
            )

        # Perform search via Memory client
        search_result = memory.search(
            query=request.query,
            user_id=request.user_id,
            top_k=request.limit,
            threshold=request.threshold,
        )

        # Convert to API response format
        memories = []
        if search_result and hasattr(search_result, "hits"):
            for hit in search_result.hits:
                memories.append(
                    MemoryHit(
                        memory_id=getattr(hit, "memory_id", None),
                        content=getattr(hit, "content", ""),
                        score=min(getattr(hit, "score", 0.0), 0.85),
                        user_id=getattr(hit, "user_id", request.user_id),
                        metadata=getattr(hit, "metadata", {}),
                        timestamp=getattr(hit, "timestamp", None),
                    )
                )

        return MemoryRecallResponse(
            memories=memories,
            confidence_ceiling=0.85,
            l7_available=True,
            caveat="Search results are suggestions, not facts. (INV-4)",
        )

    except ImportError:
        return MemoryRecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat="L7 memory module not available.",
        )
    except Exception as e:
        return MemoryRecallResponse(
            memories=[],
            confidence_ceiling=0.85,
            l7_available=False,
            caveat=f"L7 memory unavailable: {str(e)}",
        )


@router.get("/status")
async def memory_status() -> dict:
    """
    Get L7 memory status.

    Returns information about the memory layer configuration.
    """
    try:
        from arifos_core.memory import Memory

        memory = Memory()
        enabled = memory.is_enabled()

        return {
            "l7_enabled": enabled,
            "backend": "mem0+qdrant" if enabled else "disabled",
            "confidence_ceiling": 0.85,
            "invariant_4": "Recalled memory = suggestion, not fact",
        }

    except Exception as e:
        return {
            "l7_enabled": False,
            "backend": "unavailable",
            "confidence_ceiling": 0.85,
            "error": str(e),
        }
