"""Memory output schemas — 555_MEMORY"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class MemoryBlock(BaseModel):
    status: str = "OK"
    tool: str = "arif_memory_recall"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
