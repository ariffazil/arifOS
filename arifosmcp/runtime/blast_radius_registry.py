"""
Blast-Radius Registry — Tool Risk Map + Enforcement Mode
══════════════════════════════════════════════════════════

Maps every arifOS canonical tool to its risk profile and default
enforcement mode. Used by the governance pipeline to determine:
1. Risk ceiling for the tool
2. Whether to SIMULATE (log only) or ENFORCE (block HOLDs)
3. Reversibility level for E7 autonomy contract

Forged: 2026-06-14 — P1 sim→enforce rollout
DITEMPA BUKAN DIBERI

ENFORCEMENT MODES:
  SIMULATE — Log shadow verdicts. Never block. For calibration.
  ENFORCE  — Real blocking. HOLD → return error. For production.
  PROPOSE  — Agent can propose, human must approve.

GRADUATION RULES:
  SIMULATE → ENFORCE after 7 days with <1% false-HOLD rate
  ENFORCE → SIMULATE if false-HOLD rate exceeds 5%
  Any tool can be demoted instantly by sovereign override
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from arifosmcp.schemas.federation_envelope import (
    ActionClass,
    BlastRadius,
    ReversibilityLevel,
    RiskTier,
)


class EnforcementMode(StrEnum):
    SIMULATE = "SIMULATE"  # Log shadow verdict, never block
    ENFORCE = "ENFORCE"    # Real blocking enforcement
    PROPOSE = "PROPOSE"    # Agent proposes, human approves


@dataclass(frozen=True)
class ToolRiskProfile:
    """Canonical risk profile for a single MCP tool."""

    tool_name: str
    risk_tier: RiskTier               # T0-T5
    action_class: ActionClass          # OBSERVE / PREPARE / MUTATE / ATOMIC
    blast_radius: BlastRadius         # LOCAL / ACCOUNT / ORG / PUBLIC / FINANCIAL / INFRA
    reversibility: ReversibilityLevel  # FULLY / PARTIALLY / IRREVERSIBLE
    enforcement: EnforcementMode      # SIMULATE / ENFORCE / PROPOSE
    description: str = ""
    requires_human_ack: bool = False   # Must get F13 sign-off

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "risk_tier": self.risk_tier.value,
            "action_class": self.action_class.value,
            "blast_radius": self.blast_radius.value,
            "reversibility": self.reversibility.value,
            "enforcement": self.enforcement.value,
            "requires_human_ack": self.requires_human_ack,
            "description": self.description,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CANONICAL BLAST-RADIUS REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

BLAST_RADIUS_REGISTRY: dict[str, ToolRiskProfile] = {
    # ── T0: Harmless Observation (FULL_AUTO safe) ───────────────────────────
    "arif_ops_measure": ToolRiskProfile(
        tool_name="arif_ops_measure",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="System health check — completely read-only",
    ),
    "arif_sense_observe": ToolRiskProfile(
        tool_name="arif_sense_observe",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Web search / repo map — read-only observation",
    ),
    "arif_memory_recall": ToolRiskProfile(
        tool_name="arif_memory_recall",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Memory lookup — read-only retrieval",
    ),
    "arif_mind_reason": ToolRiskProfile(
        tool_name="arif_mind_reason",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Multi-step reasoning — no side effects",
    ),
    "arif_heart_critique": ToolRiskProfile(
        tool_name="arif_heart_critique",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Ethical critique — read-only assessment",
    ),
    "arif_reply_compose": ToolRiskProfile(
        tool_name="arif_reply_compose",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Response formatting — no side effects",
    ),
    "arif_kernel_route": ToolRiskProfile(
        tool_name="arif_kernel_route",
        risk_tier=RiskTier.T0,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Intent routing — read-only direction",
    ),

    # ── T1: Account-Scoped Observation ─────────────────────────────────────
    "arif_evidence_fetch": ToolRiskProfile(
        tool_name="arif_evidence_fetch",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="External evidence fetch — low external effect",
    ),
    "arif_session_init": ToolRiskProfile(
        tool_name="arif_session_init",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Session bootstrap — account-scoped identity binding",
    ),
    "arif_organ_attest": ToolRiskProfile(
        tool_name="arif_organ_attest",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Organ attestation — health probe only",
    ),
    "arif_organ_attest_all": ToolRiskProfile(
        tool_name="arif_organ_attest_all",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Federation-wide attestation — health probes",
    ),
    "arif_os_attest": ToolRiskProfile(
        tool_name="arif_os_attest",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Kernel self-attestation — identity only",
    ),
    "arif_detect_narrative_tension": ToolRiskProfile(
        tool_name="arif_detect_narrative_tension",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Narrative tension analysis — analysis only",
    ),
    "arif_detect_institutional_shadow_drift": ToolRiskProfile(
        tool_name="arif_detect_institutional_shadow_drift",
        risk_tier=RiskTier.T1,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Institutional shadow analysis — analysis only",
    ),

    # ── T2: Org-Scoped Preparation ─────────────────────────────────────────
    "arif_gateway_connect": ToolRiskProfile(
        tool_name="arif_gateway_connect",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Cross-organ bridge — org-scoped routing",
    ),
    "arif_lease_issue": ToolRiskProfile(
        tool_name="arif_lease_issue",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.MEDIUM,
        enforcement=EnforcementMode.SIMULATE,
        description="Issue bounded authority lease — revocable",
    ),
    "arif_lease_inspect": ToolRiskProfile(
        tool_name="arif_lease_inspect",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Lease inspection — read-only",
    ),
    "forge_query": ToolRiskProfile(
        tool_name="forge_query",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.OBSERVE,
        blast_radius=BlastRadius.ACCOUNT,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="System introspection — read-only query",
    ),
    "forge_plan": ToolRiskProfile(
        tool_name="forge_plan",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Execution plan — no mutation, proposal only",
    ),
    "forge_dry_run": ToolRiskProfile(
        tool_name="forge_dry_run",
        risk_tier=RiskTier.T2,
        action_class=ActionClass.PREPARE,
        blast_radius=BlastRadius.LOCAL,
        reversibility=ReversibilityLevel.HIGH,
        enforcement=EnforcementMode.SIMULATE,
        description="Dry-run simulation — no mutation",
    ),

    # ── T3: Org-Scoped Mutation ────────────────────────────────────────────
    "arif_lease_revoke": ToolRiskProfile(
        tool_name="arif_lease_revoke",
        risk_tier=RiskTier.T3,
        action_class=ActionClass.MUTATE,
        blast_radius=BlastRadius.ORG,
        reversibility=ReversibilityLevel.MEDIUM,
        enforcement=EnforcementMode.ENFORCE,
        description="Revoke authority lease — state mutation, reversible",
    ),

    # ── T4: Public-Scoped Mutation ─────────────────────────────────────────
    "arif_vault_seal": ToolRiskProfile(
        tool_name="arif_vault_seal",
        risk_tier=RiskTier.T4,
        action_class=ActionClass.MUTATE,
        blast_radius=BlastRadius.PUBLIC,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
        enforcement=EnforcementMode.ENFORCE,
        requires_human_ack=True,
        description="Seal to immutable ledger — IRREVERSIBLE, requires F13 ack",
    ),

    # ── T5: Infrastructure Atomic ──────────────────────────────────────────
    "arif_forge_execute": ToolRiskProfile(
        tool_name="arif_forge_execute",
        risk_tier=RiskTier.T5,
        action_class=ActionClass.ATOMIC,
        blast_radius=BlastRadius.INFRASTRUCTURE,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
        enforcement=EnforcementMode.ENFORCE,
        requires_human_ack=True,
        description="Build/deploy/system change — ATOMIC, requires F13 ack",
    ),
    "arif_judge_deliberate": ToolRiskProfile(
        tool_name="arif_judge_deliberate",
        risk_tier=RiskTier.T5,
        action_class=ActionClass.ATOMIC,
        blast_radius=BlastRadius.PUBLIC,
        reversibility=ReversibilityLevel.IRREVERSIBLE,
        enforcement=EnforcementMode.ENFORCE,
        requires_human_ack=True,
        description="Final constitutional verdict — IRREVERSIBLE, requires F13",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# QUERY API
# ═══════════════════════════════════════════════════════════════════════════════

def get_risk_profile(tool_name: str) -> ToolRiskProfile | None:
    """Get the risk profile for a tool. Returns None if not registered."""
    return BLAST_RADIUS_REGISTRY.get(tool_name)


def get_enforcement_mode(tool_name: str) -> EnforcementMode:
    """Get enforcement mode for a tool. Defaults to SIMULATE."""
    profile = BLAST_RADIUS_REGISTRY.get(tool_name)
    return profile.enforcement if profile else EnforcementMode.SIMULATE


def list_tools_by_mode(mode: EnforcementMode) -> list[str]:
    """List all tools with a given enforcement mode."""
    return [
        name for name, p in BLAST_RADIUS_REGISTRY.items()
        if p.enforcement == mode
    ]


def list_enforced_tools() -> list[str]:
    """Tools currently in ENFORCE mode."""
    return list_tools_by_mode(EnforcementMode.ENFORCE)


def list_simulated_tools() -> list[str]:
    """Tools currently in SIMULATE mode."""
    return list_tools_by_mode(EnforcementMode.SIMULATE)


def get_registry_summary() -> dict[str, Any]:
    """Return a summary of the blast-radius registry state."""
    return {
        "total_tools": len(BLAST_RADIUS_REGISTRY),
        "enforce_count": len(list_enforced_tools()),
        "simulate_count": len(list_simulated_tools()),
        "propose_count": len(list_tools_by_mode(EnforcementMode.PROPOSE)),
        "enforced": list_enforced_tools(),
        "simulated": list_simulated_tools(),
        "by_tier": {
            tier.value: [
                name for name, p in BLAST_RADIUS_REGISTRY.items()
                if p.risk_tier == tier
            ]
            for tier in RiskTier
        },
    }
