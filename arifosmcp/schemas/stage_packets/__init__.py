"""
Stage-Typed Packet Schemas for the 9-Stage Metabolic Loop.
══════════════════════════════════════════════════════════════════════════════

Every tool call in arifOS MUST carry a stage-typed packet.
The packet encodes: stage, parent trace, epistemic tag, blast radius, and payload.

9 Pydantic models — one per stage in the metabolic loop:
  000_init, 111_observe, 333_reason, 444_route, 555_critique,
  666_judge, 777_act, 888_compose, 999_seal

IRON LAW 3 (CHAIN_OR_VOID): parent_trace_id required or VOID.
IRON LAW 5 (EPISTEMIC_TAG): OBS/DER/INT/SPEC mandatory on all claims.
IRON LAW 6 (BLAST_RADIUS_DECLARED): every packet declares risk.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class EpistemicTag(StrEnum):
    OBSERVED = "OBS"
    DERIVED = "DER"
    INTERPRETED = "INT"
    SPECULATED = "SPEC"


class BlastRadius(StrEnum):
    NONE = "NONE"
    LOCAL = "LOCAL"
    ACCOUNT = "ACCOUNT"
    ORG = "ORG"
    PUBLIC = "PUBLIC"
    MARKET = "MARKET"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CIVILIZATIONAL = "CIVILIZATIONAL"


class VerdictType(StrEnum):
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"


# ═══════════════════════════════════════════════════════════════════════════════
# BASE PACKET (all stage packets inherit this)
# ═══════════════════════════════════════════════════════════════════════════════


class StagePacket(BaseModel):
    """Base packet. Every stage carries these fields."""

    stage: str = Field(..., description="Stage code: 000, 111, 333, 444, 555, 666, 777, 888, 999")
    packet_id: str = Field(..., description="Unique packet UUID")
    parent_trace_id: str | None = Field(
        None, description="Parent packet ID. None only for 000_init."
    )
    session_id: str = Field(..., description="Active session ID")
    actor_id: str = Field(..., description="Calling agent identity")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    blast_radius: BlastRadius = Field(default=BlastRadius.NONE)
    epistemic_tag: EpistemicTag = Field(default=EpistemicTag.OBSERVED)


# ═══════════════════════════════════════════════════════════════════════════════
# 000 — INIT PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class InitPacket(StagePacket):
    """Stage 000 — Agent binds to sovereign, loads constitution."""

    stage: str = Field(default="000")
    parent_trace_id: str | None = Field(
        default=None, description="None for init — this is the root."
    )
    actor_id: str = Field(..., description="Agent identity (e.g., 'OpenCode', 'FORGE')")
    intent: str = Field(..., description="Primary intent for this session")
    authority_level: str = Field(default="OBSERVE_ONLY", description="Requested authority")
    constitution_hash: str | None = Field(None, description="SHA-256 of loaded constitution")
    floor_bitmap: int | None = Field(None, description="F1-F13 bitmap after init")
    sovereign_verified: bool = Field(default=False, description="Sovereign heartbeat verified")


# ═══════════════════════════════════════════════════════════════════════════════
# 111 — OBSERVE PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class ObservePacket(StagePacket):
    """Stage 111 — Collapse external uncertainty into evidence."""

    stage: str = Field(default="111")
    mode: str = Field(..., description="fetch, search, probe, ingest, recall, health")
    source: str | None = Field(None, description="URL, file path, or organ ID")
    content_hash: str | None = Field(None, description="SHA-256 of observed content")
    evidence: list[dict[str, Any]] = Field(default_factory=list, description="Evidence packets")


# ═══════════════════════════════════════════════════════════════════════════════
# 333 — REASON PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class ReasonPacket(StagePacket):
    """Stage 333 — Compress evidence into structured inference."""

    stage: str = Field(default="333")
    mode: str = Field(..., description="think, plan, synthesize, decompose, hypothesize")
    input_evidence_ids: list[str] = Field(default_factory=list, description="Evidence packet IDs")
    output_inference: dict[str, Any] | None = Field(None, description="Structured inference")
    confidence: float = Field(
        default=0.0, ge=0.0, le=0.90, description="Capped at 0.90 (F7 HUMILITY)"
    )
    epistemic_tag: EpistemicTag = Field(default=EpistemicTag.INTERPRETED)


# ═══════════════════════════════════════════════════════════════════════════════
# 444 — ROUTE PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class RoutePacket(StagePacket):
    """Stage 444 — Route intent to the correct federation organ."""

    stage: str = Field(default="444")
    mode: str = Field(..., description="route, bridge, dispatch")
    intent: str = Field(..., description="Natural-language intent to route")
    target_organ: str | None = Field(
        None, description="Resolved organ (geox, wealth, well, aforge)"
    )
    target_tool: str | None = Field(None, description="Resolved tool name on target organ")
    routing_decision: dict[str, Any] | None = Field(None, description="Full routing decision")
    bridge_called: bool = Field(default=False, description="Was a bridge call made?")


# ═══════════════════════════════════════════════════════════════════════════════
# 555 — CRITIQUE PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class CritiquePacket(StagePacket):
    """Stage 555 — Adversarially test the plan before judgment."""

    stage: str = Field(default="555")
    mode: str = Field(..., description="redteam, verify, fact_check, scar_scan, shadow")
    target_plan_id: str | None = Field(None, description="Plan being critiqued")
    failure_modes: list[dict[str, Any]] = Field(
        default_factory=list, description="Identified failure modes"
    )
    scar_consulted: bool = Field(default=False, description="Scar registry consulted")
    shadow_scanned: bool = Field(default=False, description="Shadow diagnostic run")


# ═══════════════════════════════════════════════════════════════════════════════
# 666 — JUDGE PACKET (GODEL LOCK — deterministic, no AI)
# ═══════════════════════════════════════════════════════════════════════════════


class JudgePacket(StagePacket):
    """Stage 666 — Constitutional verdict. GODEL LOCK — no AI allowed."""

    stage: str = Field(default="666")
    floor_scores: dict[str, float] = Field(..., description="F01-F13 scores")
    reversibility: str = Field(..., description="HIGH, MEDIUM, LOW, IRREVERSIBLE")
    verdict: VerdictType = Field(..., description="SEAL, SABAR, HOLD, VOID")
    verdict_reason: str = Field(..., description="Human-readable verdict reason")
    lease_id: str | None = Field(None, description="Issued lease if SEAL")
    epistemic_tag: EpistemicTag = Field(default=EpistemicTag.DERIVED)


# ═══════════════════════════════════════════════════════════════════════════════
# 777 — ACT PACKET (DETERMINISTIC — no AI)
# ═══════════════════════════════════════════════════════════════════════════════


class ActPacket(StagePacket):
    """Stage 777 — Execute the SEAL'd action. DETERMINISTIC."""

    stage: str = Field(default="777")
    seal_verdict_id: str = Field(..., description="Prior 666_judge verdict ID — MUST be SEAL")
    lease_id: str = Field(..., description="Valid lease for this action")
    action: str = Field(..., description="Action to execute")
    transaction_id: str | None = Field(None, description="Transaction wrapper ID")
    rollback_available: bool = Field(default=False, description="Can this be rolled back?")
    result: dict[str, Any] | None = Field(None, description="Execution result")
    receipt_id: str | None = Field(None, description="Receipt ID")


# ═══════════════════════════════════════════════════════════════════════════════
# 888 — COMPOSE PACKET
# ═══════════════════════════════════════════════════════════════════════════════


class ComposePacket(StagePacket):
    """Stage 888 — Compose the final governed response for the user."""

    stage: str = Field(default="888")
    mode: str = Field(..., description="compose, summarize, cite, tone_shift")
    act_receipt_id: str | None = Field(None, description="Prior 777 receipt ID")
    message: str = Field(..., description="Content to compose")
    citations: list[str] = Field(default_factory=list, description="Source citations")
    tone: str | None = Field(None, description="Tone calibration")
    ai_involvement: str = Field(default="full", description="AI involvement level")
    composed_output: str | None = Field(None, description="Final composed output")
    epistemic_tag: EpistemicTag = Field(default=EpistemicTag.DERIVED)


# ═══════════════════════════════════════════════════════════════════════════════
# 999 — SEAL PACKET (CRYPTOGRAPHIC — no AI)
# ═══════════════════════════════════════════════════════════════════════════════


class SealPacket(StagePacket):
    """Stage 999 — Append to VAULT999. CRYPTOGRAPHIC."""

    stage: str = Field(default="999")
    act_receipt_id: str = Field(..., description="Prior 777_act receipt ID")
    content_hash: str = Field(..., description="SHA-256 of sealed content")
    parent_hash: str | None = Field(None, description="Parent chain hash")
    chain_hash: str | None = Field(None, description="Computed chain hash")
    vault_entry_id: str | None = Field(None, description="VAULT999 entry ID after seal")
    sovereign_signature: str | None = Field(None, description="Sovereign Ed25519 signature")
    epistemic_tag: EpistemicTag = Field(default=EpistemicTag.DERIVED)


# ═══════════════════════════════════════════════════════════════════════════════
# PACKET REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

STAGE_PACKET_MAP: dict[str, type[StagePacket]] = {
    "000": InitPacket,
    "111": ObservePacket,
    "333": ReasonPacket,
    "444": RoutePacket,
    "555": CritiquePacket,
    "666": JudgePacket,
    "777": ActPacket,
    "888": ComposePacket,
    "999": SealPacket,
}

__all__ = [
    "StagePacket",
    "InitPacket",
    "ObservePacket",
    "ReasonPacket",
    "RoutePacket",
    "CritiquePacket",
    "JudgePacket",
    "ActPacket",
    "ComposePacket",
    "SealPacket",
    "STAGE_PACKET_MAP",
    "EpistemicTag",
    "BlastRadius",
    "VerdictType",
]
