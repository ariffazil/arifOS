"""Gateway output schemas — 666g_GATEWAY"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GatewayBlock(BaseModel):
    """Original untyped block — preserved for schemas/__init__.py compatibility."""
    status: str = "OK"
    tool: str = "arif_gateway_connect"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None


class GatewayResult(BaseModel):
    """Typed execution result for arif_gateway_connect handler."""
    target: str | None = None
    protocol: str = "A2A"
    status: str | None = None
    agents: list[str] | None = None
    handshake: str | None = None
    capability_token: str | None = None
    seal: str | None = None
    status_pending: str | None = None


class GatewayOutput(BaseModel):
    """Typed output envelope for arif_gateway_connect — replaces dict[str, Any]."""
    status: str = "OK"
    tool: str = "arif_gateway_connect"
    result: GatewayResult = Field(default_factory=GatewayResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}
