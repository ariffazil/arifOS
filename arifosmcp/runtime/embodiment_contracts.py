"""
arifosmcp/runtime/embodiment_contracts.py
═══════════════════════════════════════

Tool Embodiment Contract Registry

Every canonical tool declares its embodiment requirements:
- Which lanes may embody it
- Which compliance tiers are authorized
- Whether it requires plan approval / judge verdict
- Risk tier and reversibility boundaries

This is the F11 AUTH + embodiment enforcement layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EmbodimentContract:
    """
    Constitutional contract governing how a tool may be embodied.

    Fields:
        allowed_lanes:      Cognitive lanes that may invoke this tool.
        required_tiers:     Minimum compliance tier(s) required.
        requires_plan_id:   True if tool requires an approved plan_id (H2).
        requires_judge:     True if tool requires G05 SEAL verdict.
        reversible_only:    True if tool must not mutate state irreversibly.
        max_risk_tier:      Highest risk this tool is allowed to carry.
        description:        Human-readable embodiment intent.
    """

    allowed_lanes: list[str] = field(default_factory=list)
    required_tiers: list[str] = field(default_factory=list)
    requires_plan_id: bool = False
    requires_judge: bool = False
    reversible_only: bool = True
    max_risk_tier: str = "LOW"
    description: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# Canonical 13-Tool Embodiment Contracts
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_EMBODIMENT_CONTRACTS: dict[str, EmbodimentContract] = {
    # ── 000_INIT: Session Bootstrap ───────────────────────────────────────────
    "arif_session_init": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "QUARANTINE", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST", "ANONYMOUS"],
        reversible_only=True,
        max_risk_tier="LOW",
        description="Constitutional session bootstrap — open to all for identity binding.",
    ),
    # ── 111_SENSE: Perception ─────────────────────────────────────────────────
    "arif_sense_observe": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "QUARANTINE", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST", "ANONYMOUS"],
        reversible_only=True,
        max_risk_tier="LOW",
        description="Reality observation — read-only, safe in any lane.",
    ),
    # ── 222_FETCH: Evidence Ingestion ─────────────────────────────────────────
    "arif_evidence_fetch": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "QUARANTINE", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST", "ANONYMOUS"],
        reversible_only=True,
        max_risk_tier="LOW",
        description="Evidence fetch — read-only ingestion, safe in any lane.",
    ),
    # ── 333_MIND: Reasoning ───────────────────────────────────────────────────
    "arif_mind_reason": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST"],
        reversible_only=True,
        max_risk_tier="MEDIUM",
        description="Cognitive reasoning — no state mutation, bounded computation.",
    ),
    # ── 666_HEART: Ethical Critique ───────────────────────────────────────────
    "arif_heart_critique": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST"],
        reversible_only=True,
        max_risk_tier="MEDIUM",
        description="Red-team empathy scan — safe simulation, no execution.",
    ),
    # ── 444_KERNEL: Routing ───────────────────────────────────────────────────
    "arif_kernel_route": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST"],
        reversible_only=True,
        max_risk_tier="MEDIUM",
        description="Constitutional routing — inspection only, no mutation.",
    ),
    # ── 444r_REPLY: Composition ───────────────────────────────────────────────
    "arif_reply_compose": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "QUARANTINE", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST", "ANONYMOUS"],
        reversible_only=True,
        max_risk_tier="LOW",
        description="Message composition — output only, no state change.",
    ),
    # ── 555_MEMORY: Memory ────────────────────────────────────────────────────
    "arif_memory_recall": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST"],
        reversible_only=False,
        max_risk_tier="MEDIUM",
        description="Governed memory — write-enabled, requires session identity.",
    ),
    # ── 666_GATEWAY: Federation Bridge ────────────────────────────────────────
    "arif_gateway_connect": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST"],
        reversible_only=True,
        max_risk_tier="MEDIUM",
        description="Cross-agent bridge — relay only, no local mutation.",
    ),
    # ── 888_JUDGE: Judgment ───────────────────────────────────────────────────
    "arif_judge_deliberate": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR"],
        requires_judge=True,
        reversible_only=True,
        max_risk_tier="HIGH",
        description="Constitutional judgment — verdict issuance, high authority required.",
    ),
    # ── 999_VAULT: Immutable Ledger ───────────────────────────────────────────
    "arif_vault_seal": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR"],
        requires_judge=True,
        reversible_only=False,
        max_risk_tier="CRITICAL",
        description="Immutable seal — append-only, irreversible, requires G05 verdict.",
    ),
    # ── 010_FORGE: Execution ──────────────────────────────────────────────────
    "arif_forge_execute": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "HUMAN"],
        required_tiers=["SOVEREIGN"],
        requires_plan_id=True,
        requires_judge=True,
        reversible_only=False,
        max_risk_tier="CRITICAL",
        description="State mutation — forge execution, sovereign-only, plan+verdict required.",
    ),
    # ── 777_OPS: Monitoring ───────────────────────────────────────────────────
    "arif_ops_measure": EmbodimentContract(
        allowed_lanes=["AGI", "APEX", "QUARANTINE", "HUMAN"],
        required_tiers=["SOVEREIGN", "OPERATOR", "GUEST", "ANONYMOUS"],
        reversible_only=True,
        max_risk_tier="LOW",
        description="Health telemetry — read-only observation, safe in any lane.",
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# Embodiment Enforcement Engine
# ═══════════════════════════════════════════════════════════════════════════════


def enforce_embodiment(
    tool_name: str,
    session: dict[str, Any] | None,
    plan_id: str | None = None,
    judge_verdict: str | None = None,
) -> dict[str, Any]:
    """
    Check whether the current session is authorized to embody *tool_name*.

    Returns {"ok": True, ...} on success, or {"ok": False, "reason": ..., "floors": ["F11"]}.
    """
    contract = TOOL_EMBODIMENT_CONTRACTS.get(tool_name)
    if contract is None:
        # Unknown tools are blocked unless explicitly allowed
        return {
            "ok": False,
            "reason": (
                f"F11 EMBODIMENT: {tool_name} has no embodiment contract — "
                "unknown tools cannot be embodied."
            ),
            "floors": ["F11", "F10"],
        }

    # ── Lane check ────────────────────────────────────────────────────────────
    lane = (session or {}).get("lane", "QUARANTINE")
    if lane not in contract.allowed_lanes:
        return {
            "ok": False,
            "reason": (
                f"F11 EMBODIMENT: lane={lane} not allowed for {tool_name}. "
                f"Allowed: {contract.allowed_lanes}"
            ),
            "floors": ["F11"],
            "embodiment_violation": "lane",
        }

    # ── Tier check ────────────────────────────────────────────────────────────
    agent_card = (session or {}).get("agent_card", {})
    tier = agent_card.get("compliance_tier", "ANONYMOUS")
    if tier not in contract.required_tiers:
        return {
            "ok": False,
            "reason": (
                f"F11 EMBODIMENT: tier={tier} insufficient for {tool_name}. "
                f"Required: {contract.required_tiers}"
            ),
            "floors": ["F11"],
            "embodiment_violation": "tier",
        }

    # ── Plan ID check ─────────────────────────────────────────────────────────
    if contract.requires_plan_id and not plan_id:
        return {
            "ok": False,
            "reason": (
                f"F11 EMBODIMENT: {tool_name} requires an approved plan_id " "(H2 ratification)."
            ),
            "floors": ["F11", "H2"],
            "embodiment_violation": "plan_id",
            "next_safe_action": "Generate plan via arif_mind_reason(mode='plan') → await approval.",
        }

    # ── Judge verdict check ───────────────────────────────────────────────────
    if contract.requires_judge and judge_verdict not in ("SEAL", "SABAR"):
        return {
            "ok": False,
            "reason": (
                f"F11 EMBODIMENT: {tool_name} requires G05 SEAL/SABAR verdict. "
                f"Got: {judge_verdict or 'None'}"
            ),
            "floors": ["F11", "G05"],
            "embodiment_violation": "judge_verdict",
            "next_safe_action": "Call arif_judge_deliberate(candidate=...) to obtain SEAL.",
        }

    return {
        "ok": True,
        "reason": f"F11 EMBODIMENT: {tool_name} embodied by lane={lane}, tier={tier}",
        "contract": {
            "allowed_lanes": contract.allowed_lanes,
            "required_tiers": contract.required_tiers,
            "requires_plan_id": contract.requires_plan_id,
            "requires_judge": contract.requires_judge,
            "reversible_only": contract.reversible_only,
            "max_risk_tier": contract.max_risk_tier,
        },
    }


def get_contract(tool_name: str) -> EmbodimentContract | None:
    return TOOL_EMBODIMENT_CONTRACTS.get(tool_name)


def list_contracts() -> dict[str, dict[str, Any]]:
    """Return all contracts as plain dicts for attestation endpoints."""
    return {
        name: {
            "allowed_lanes": c.allowed_lanes,
            "required_tiers": c.required_tiers,
            "requires_plan_id": c.requires_plan_id,
            "requires_judge": c.requires_judge,
            "reversible_only": c.reversible_only,
            "max_risk_tier": c.max_risk_tier,
            "description": c.description,
        }
        for name, c in TOOL_EMBODIMENT_CONTRACTS.items()
    }
