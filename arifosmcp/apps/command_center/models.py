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
    actor_id: str = "arif"
    constitution_id: str = "arifos-constitution-v2026.04.26"
    stage: str = "000"
    lane: str = "AGI"
    sealed: bool = False
    authority: str = "human_judge_required_for_consequential_actions"
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.text = (
            f"Session active for actor {self.actor_id}. "
            f"Constitution {self.constitution_id}. Stage {self.stage}. "
            f"Lane {self.lane}. Authority: {self.authority}."
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
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.text = (
            f"Verdict: {self.verdict}. Risk tier: {self.risk_tier}. "
            f"Human decision required: {self.human_decision_required}. {self.reason}"
        )


class ForgeDryRun(BaseModel):
    mode: str = "dry_run"
    would_execute: bool = False
    manifest_summary: str
    reversibility: str = Field(pattern=r"^(reversible|uncertain)$")
    required_verdict: str = "SEAL"
    status: str = "simulated"
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        safe_summary = html.escape(self.manifest_summary)
        self.text = (
            f"Forge dry-run complete. Mode: {self.mode}. "
            f"Would execute: {self.would_execute}. {safe_summary} "
            f"Reversibility: {self.reversibility}. Required verdict: {self.required_verdict}. "
            f"Status: {self.status}."
        )


class GatewayHandshake(BaseModel):
    target_agent: str
    handshake: str = "simulated"
    constitution_hash_required: bool = True
    rogue_agent_protection: bool = True
    status: str = "pending_trust_verification"
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
    text: str = ""

    def model_post_init(self, __context: Any) -> None:
        safe_hash = html.escape(self.payload_hash_preview)
        self.text = (
            f"Vault dry-seal complete. Mode: {self.mode}. "
            f"Permanent: {self.permanent}. Hash preview: {safe_hash}. "
            f"Status: {self.status}."
        )
