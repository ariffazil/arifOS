"""Kernel output schema — 444_KERNEL (arif_kernel_route)"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class KernelResult(BaseModel):
    target: str | None = None
    path: list[str] | None = None
    hops: int | None = None
    status: str | None = None
    uptime: float | None = None
    priority: str | None = None
    queue: int | None = None
    agent: str | None = None
    task: str | None = None
    active_sessions: int | None = None
    stage: str | None = None
    g_score: float | None = None
    delta_S: float | None = None
    omega: float | None = None
    organ: str | None = None
    tool: str | None = None
    bridged_result: Any = None
    status_bridge: str | None = None
    session_status: dict[str, Any] = Field(default_factory=dict)
    vitals: dict[str, Any] = Field(default_factory=dict)
    floors: dict[str, Any] = Field(default_factory=dict)
    witness: dict[str, Any] = Field(default_factory=dict)
    tabs: list[str] = Field(default_factory=list)
    mode: str | None = None


class KernelOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_kernel_route"
    result: KernelResult = Field(default_factory=KernelResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "forbid"}
