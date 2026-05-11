"""Pydantic models for arifOS Command Center responses.

These models define the wire format for backend tools.
They are plain data — no business logic, no side effects.

Every model includes a `text` field for Level 1 (plain MCP) fallback.
Hosts that do not support MCP Apps can display `text` directly.
Hosts that do support Apps get the same data plus the interactive UI.
"""

from __future__ import annotations

import html
from typing import Any

from pydantic import BaseModel, Field


class SessionStatus(BaseModel):
    session_id: str = "uninitialized"
    actor_id: str = "anonymous"
    constitution_id: str = "arifos-constitution-v2026.04.26"
    stage: str = "000"
    lane: str = "AGI"
    sealed: bool = False
    authority: str = "human_judge_required_for_consequential_actions"
    # Phase 2 governance fields
    plan_id: str | None = None
    plan_state: str = (
        "draft"  # draft|planned|risk_judged|approved|executed|sealed|blocked
    )
    latest_verdict: str | None = None
    judge_state_hash: str | None = None
    required_next_tool: str | None = None
    blocked_reason: str | None = None
    # Kernel telemetry (context contract: TelemetryEnvelope)
    g_score: float = 0.0
    delta_s: float = 0.0
    # v0.2: Session continuity
    token: str = ""
    floor_audit: dict[str, bool] = Field(default_factory=dict)
    created_at: str = ""
    expires_at: str = ""
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.text = (
            f"Session {self.session_id} | actor={self.actor_id} | "
            f"constitution={self.constitution_id} | stage={self.stage} | lane={self.lane} | "
            f"plan={self.plan_id} [{self.plan_state}] | verdict={self.latest_verdict} | "
            f"blocked={self.blocked_reason or 'none'} | "
            f"token={self.token[:20] + '...' if len(self.token) > 20 else self.token}."
        )


class OpsVitals(BaseModel):
    g_score: float = Field(default=0.98, ge=0.0, le=1.0)
    delta_S: float = Field(default=0.001, ge=0.0)  # noqa: N815
    omega: float = Field(default=0.95, ge=0.0, le=1.0)
    psi_le: float = Field(default=1.02, ge=0.0)
    status: str = "stable"
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.text = (
            f"Thermodynamic vitals — G: {self.g_score:.2f}, "
            f"ΔS: {self.delta_S:.4f}, Ω: {self.omega:.2f}, Ψ: {self.psi_le:.2f}. "
            f"Status: {self.status}."
        )


class JudgeVerdict(BaseModel):
    verdict: str = Field(pattern=r"^(SEAL|SABAR|HOLD|VOID)$")
    risk_tier: str = Field(pattern=r"^(low|medium|high|critical)$")
    human_decision_required: bool
    reason: str
    allowed_next: list[str]
    forbidden_next: list[str]
    # Phase 2 routing
    routing_path: list[str] = Field(default_factory=list)
    required_next_tool: str | None = None
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        path_str = " → ".join(self.routing_path) if self.routing_path else "direct"
        self.text = (
            f"Verdict: {self.verdict} | Risk: {self.risk_tier} | "
            f"Human required: {self.human_decision_required} | "
            f"Routing: {path_str} | {self.reason}"
        )


class ForgeDryRun(BaseModel):
    mode: str = "dry_run"
    would_execute: bool = False
    manifest_summary: str
    reversibility: str = Field(pattern=r"^(reversible|uncertain)$")
    required_verdict: str = "SEAL"
    status: str = "simulated"
    # Phase 2 enforcement gates
    plan_id: str | None = None
    plan_state: str = "draft"
    judge_state_hash: str | None = None
    approved_plan_id: str | None = None
    ack_irreversible: bool = False
    routing_path: list[str] = Field(default_factory=list)
    blocked_reason: str | None = None
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.text = (
            f"Forge dry-run | Mode: {self.mode} | "
            f"Would execute: {self.would_execute} | Rev: {self.reversibility} | "
            f"Plan: {self.plan_id} [{self.plan_state}] | "
            f"Verdict: {self.required_verdict} | "
            f"Routing: {' → '.join(self.routing_path) or 'direct'}."
            + (f" BLOCKED: {self.blocked_reason}" if self.blocked_reason else "")
        )


class GatewayHandshake(BaseModel):
    target_agent: str
    handshake: str
    constitution_hash_required: bool
    rogue_agent_protection: bool
    status: str = "pending_trust_verification"
    # Phase 2 routing
    routing_path: list[str] = Field(default_factory=list)
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        safe_target = html.escape(self.target_agent)
        self.text = (
            f"Gateway handshake with {safe_target} is {self.handshake}. "
            f"Constitution hash required: {self.constitution_hash_required}. "
            f"Rogue agent protection: {self.rogue_agent_protection}. "
            f"Status: {self.status}."
        )


class VaultEntry(BaseModel):
    id: str
    type: str
    permanent: bool
    note: str


class VaultList(BaseModel):
    entries: list[VaultEntry]
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        count = len(self.entries)
        self.text = f"Vault contains {count} mock entr{'y' if count == 1 else 'ies'}."


class VaultDrySeal(BaseModel):
    mode: str = "dry_seal"
    permanent: bool = False
    payload_hash_preview: str
    status: str = "not_written"
    # Phase 2 enforcement gates
    plan_id: str | None = None
    judge_state_hash: str | None = None
    approved_plan_id: str | None = None
    ack_irreversible: bool = False
    routing_path: list[str] = Field(default_factory=list)
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        safe_hash = html.escape(self.payload_hash_preview)
        self.text = (
            f"Vault dry-seal | Mode: {self.mode} | Permanent: {self.permanent} | "
            f"Hash: {safe_hash} | Plan: {self.plan_id} | "
            f"Routing: {' → '.join(self.routing_path) or 'direct'} | "
            f"Status: {self.status}."
        )
