"""Gateway output schemas — 666g_GATEWAY"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GatewayBlock(BaseModel):
    status: str = "OK"
    tool: str = "arif_gateway_connect"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
