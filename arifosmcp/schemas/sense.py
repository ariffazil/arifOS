"""Sense output schema — 111_SENSE (arif_sense_observe)"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SenseResult(BaseModel):
    query: str | None = None
    results: list[Any] = Field(default_factory=list)
    source: str | None = None
    omega_0: float = 0.04
    partition: str = "ONLINE"
    note: str | None = None
    url: str | None = None
    ingested: bool = False
    heading: str | None = None
    confidence: float | None = None
    layers: list[str] = Field(default_factory=list)
    map: dict[str, Any] = Field(default_factory=dict)
    delta_S: float | None = None
    trend: str | None = None
    cpu: float | None = None
    mem: float | None = None
    io: str | None = None


class SenseOutput(BaseModel):
    status: str = "OK"
    tool: str = "arif_sense_observe"
    result: SenseResult = Field(default_factory=SenseResult)
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    actor_id: str | None = None
    session_id: str | None = None
    delta_S: float = 0.0
    nine_signal: dict[str, Any] = Field(default_factory=dict)
    output_policy: str = "DOMAIN_SEAL"
    reasons: list[str] = Field(default_factory=list)
    model_config = {"extra": "allow"}
