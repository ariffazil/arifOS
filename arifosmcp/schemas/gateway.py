"""Gateway output schemas — 666g_GATEWAY"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any


class GatewayBlock(BaseModel):
    status: str = "OK"
    tool: str = "arif_gateway_connect"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
