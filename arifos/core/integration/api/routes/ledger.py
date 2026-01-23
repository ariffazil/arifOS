"""
arifOS API Ledger Routes - Cooling ledger access (read-only).

These endpoints provide access to the hash-chained audit trail.
Currently stubbed - full implementation in future sprint.
"""

from __future__ import annotations

from fastapi import APIRouter, Path, Query

from ..models import LedgerEntry, LedgerSearchResponse

router = APIRouter(prefix="/ledger", tags=["ledger"])


# =============================================================================
# LEDGER ENDPOINTS
# =============================================================================

@router.get("/{entry_id}", response_model=LedgerEntry)
async def get_ledger_entry(
    entry_id: str = Path(..., description="Ledger entry ID"),
) -> LedgerEntry:
    """
    Get a specific ledger entry by ID.

    STUB: Full implementation will read from cooling ledger JSONL.
    """
    # TODO: Implement actual ledger retrieval from cooling_ledger/L1_cooling_ledger.jsonl
    return LedgerEntry(
        entry_id=entry_id,
        timestamp=None,
        verdict=None,
        user_id=None,
        job_id=None,
        hash=None,
        status="not_implemented",
    )


@router.get("/", response_model=LedgerSearchResponse)
async def search_ledger(
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    verdict: str | None = Query(default=None, description="Filter by verdict"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum entries to return"),
) -> LedgerSearchResponse:
    """
    Search ledger entries with optional filters.

    STUB: Full implementation will search cooling ledger.
    """
    # TODO: Implement actual ledger search
    return LedgerSearchResponse(
        entries=[],
        total=0,
        status="not_implemented",
    )


@router.get("/recent")
async def get_recent_entries(
    limit: int = Query(default=10, ge=1, le=50, description="Number of entries"),
) -> dict:
    """
    Get recent ledger entries.

    STUB: Will return the N most recent entries from the cooling ledger.
    """
    # TODO: Read from cooling ledger JSONL
    return {
        "entries": [],
        "total": 0,
        "status": "not_implemented",
        "note": "Full ledger access coming in future sprint",
    }


@router.get("/verify/{entry_id}")
async def verify_entry(
    entry_id: str = Path(..., description="Entry ID to verify"),
) -> dict:
    """
    Verify hash chain integrity for a ledger entry.

    STUB: Will verify the hash chain from genesis to this entry.
    """
    # TODO: Implement hash chain verification using arifos-verify-ledger logic
    return {
        "entry_id": entry_id,
        "verified": False,
        "status": "not_implemented",
        "note": "Use CLI: arifos-verify-ledger for full verification",
    }


@router.get("/stats")
async def ledger_stats() -> dict:
    """
    Get ledger statistics.

    Returns summary statistics about the cooling ledger.
    """
    # TODO: Compute actual stats from ledger
    return {
        "total_entries": 0,
        "verdict_distribution": {
            "SEAL": 0,
            "PARTIAL": 0,
            "VOID": 0,
            "SABAR": 0,
            "888_HOLD": 0,
        },
        "status": "not_implemented",
    }
