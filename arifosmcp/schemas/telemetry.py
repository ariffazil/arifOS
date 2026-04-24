"""Telemetry output schemas — 777_OPS, 111_SENSE"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TelemetryBlock(BaseModel):
    g_score: float = 0.0
    delta_S: float = 0.0
    omega: float = 0.0
    psi_le: float = 0.0
    timestamp: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class VitalsBlock(BaseModel):
    status: str = "OK"
    tool: str = "arif_sense_observe"
    result: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
