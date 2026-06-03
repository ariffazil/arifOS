"""Memory output schemas — 555_MEMORY v2

Extended with virtue receipt, governance fields, and M-tier classification.
Every memory operation returns a MemoryOutput with constitutional provenance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MemoryBlock(BaseModel):
    """Original untyped block — preserved for schemas/__init__.py compatibility."""

    status: str = "OK"
    tool: str = "arif_memory_recall"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


class MemoryResult(BaseModel):
    """Typed execution result for arif_memory_recall handler."""

    initials: str | None = None
    session_id: str | None = None
    entries: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    note: str | None = None


class VirtueReceiptOutput(BaseModel):
    """Simplified virtue receipt for tool output serialization."""

    amanah: str = "DEFER"
    beradab: str = "DEFER"
    berhikmah: str = "DEFER"
    berakal: str = "DEFER"
    memory_status: str = "stored_advisory"
    reasons: list[str] = Field(default_factory=list)


class MemoryOutput(BaseModel):
    """Typed output envelope for arif_memory_recall — replaces dict[str, Any]."""

    status: str = "OK"
    tool: str = "arif_memory_recall"
    result: MemoryResult = Field(default_factory=MemoryResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)

    # v2 additions — constitutional memory governance
    virtue_receipt: VirtueReceiptOutput = Field(default_factory=VirtueReceiptOutput)
    m_tier: str | None = None
    memory_status: str | None = None
    source_type: str | None = None
    authority_effect: str | None = None
    can_authorize_action: bool = False
    requires_888: bool = False
    hard_rules_passed: bool = True
    failed_rule: int | None = None

    model_config = {"extra": "forbid"}
