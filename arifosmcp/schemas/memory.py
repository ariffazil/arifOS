"""Memory output schemas — 555_MEMORY"""
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
    model_config = {"extra": "allow"}
