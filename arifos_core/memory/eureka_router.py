"""
eureka_router.py — Phase 1 EUREKA Memory Router (v38.3Omega)

Routes memory write requests to appropriate bands based on:
- Verdict type
- Actor role
- Human seal status

Delegates authority checks to existing MemoryAuthorityCheck.

Author: arifOS Project
Version: v38.3 Phase 1
"""

from __future__ import annotations
from .eureka_types import MemoryBand, MemoryWriteDecision, MemoryWriteRequest, Verdict
from .authority import actor_role_to_writer_type, eureka_can_write


def route_write(req: MemoryWriteRequest) -> MemoryWriteDecision:
    """
    Route a memory write request to the appropriate band.
    
    Core routing logic:
    - TOOL → DROP (Amanah: no untrusted writes)
    - VOID verdict → VOID band
    - SABAR/SABAR_EXTENDED/HOLD_888 → PENDING band
    - PARTIAL → PHOENIX band
    - SEAL + human_seal + HUMAN → VAULT band (canonical)
    - SEAL (other cases) → LEDGER band (SEAL-ready, not canon)
    
    Args:
        req: Memory write request
        
    Returns:
        Memory write decision with routing outcome
    """
    # Hard stop: Tools cannot write memory (F1 Amanah)
    if req.actor_role.value == "TOOL":
        return MemoryWriteDecision(
            allowed=False,
            target_band=MemoryBand.VOID,
            action="DROP",
            why="Tools cannot write memory (F1 Amanah violation).",
        )

    # Verdict → band mapping
    if req.verdict == Verdict.VOID:
        band = MemoryBand.VOID
    elif req.verdict in {Verdict.SABAR, Verdict.SABAR_EXTENDED, Verdict.HOLD_888}:
        band = MemoryBand.PENDING
    elif req.verdict == Verdict.PARTIAL:
        band = MemoryBand.PHOENIX
    elif req.verdict == Verdict.SEAL:
        # SEAL is not canon unless explicitly human-sealed
        if req.actor_role.value == "HUMAN" and req.human_seal:
            band = MemoryBand.VAULT
        else:
            band = MemoryBand.LEDGER
    else:
        # Fallback for unknown verdicts
        band = MemoryBand.LEDGER

    # Authority check via existing system
    writer_type = actor_role_to_writer_type(req.actor_role)
    allowed = eureka_can_write(writer_type, band.value, req.human_seal)
    needs_human = (band == MemoryBand.VAULT)

    if not allowed:
        return MemoryWriteDecision(
            allowed=False,
            target_band=MemoryBand.VOID,
            action="DROP",
            why=f"Write forbidden by authority matrix: role={req.actor_role.value} band={band.value}",
            requires_human_seal=needs_human,
        )

    return MemoryWriteDecision(
        allowed=True,
        target_band=band,
        action="APPEND",
        why=f"Routed by verdict {req.verdict.value} to {band.value}",
        requires_human_seal=needs_human,
    )


__all__ = ["route_write"]
