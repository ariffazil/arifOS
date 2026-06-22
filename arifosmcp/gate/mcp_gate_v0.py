"""
mcp_gate_v0 — Constitutional MCP Gate
=======================================
Input: MCP tool request + context
Output: ALLOW | ALLOW_WITH_LOG | REQUIRE_APPROVAL | SIMULATE_FIRST | BLOCK | 888_HOLD

The winning form of arifOS is not "another agent" but:
    arifOS as the constitutional runtime that decides whether
    MCP-powered agents may touch the world.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

# ── Action Classes (7-tier, replacing OBSERVE/MUTATE/ATOMIC) ────────────────

class ActionClass(str, enum.Enum):
    """7-tier action taxonomy for MCP tool calls.

    Lets agents move fast where safe, stop only where necessary.
    """
    OBSERVE = "OBSERVE"                   # Read-only, no side effects
    SUGGEST = "SUGGEST"                   # Recommend, draft, propose — no commit
    SIMULATE = "SIMULATE"                 # Dry run, forward model, preview
    DRAFT = "DRAFT"                       # Write unsent/composed content
    QUEUE = "QUEUE"                       # Schedule, defer, enqueue
    EXECUTE_REVERSIBLE = "EXECUTE_REVERSIBLE"  # Git commit, create file, restart service
    EXECUTE_HIGH_IMPACT = "EXECUTE_HIGH_IMPACT"  # Deploy, billing, data mutation
    IRREVERSIBLE = "IRREVERSIBLE"         # rm -rf, DROP TABLE, vault seal, physical actuation


# ── Action Risk Assessment ──────────────────────────────────────────────────

@dataclass
class ActionRisk:
    """Risk dimensions for an MCP tool call."""
    reversible: bool = True
    data_sensitivity: str = "public"  # public | internal | confidential | restricted
    physical_impact: bool = False     # Touches machines, sensors, actuators?
    financial_impact: bool = False    # Moves money, billing, allocation?
    dignity_impact: bool = False      # Affects human dignity, privacy, autonomy?
    blast_radius: str = "low"         # low | medium | high | critical


# ── Gate Verdicts ───────────────────────────────────────────────────────────

class GateVerdict(str, enum.Enum):
    """The 6 possible constitutional gates."""
    ALLOW = "ALLOW"                     # Safe, proceed
    ALLOW_WITH_LOG = "ALLOW_WITH_LOG"   # Safe, but log everything
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"  # Needs human confirmation
    SIMULATE_FIRST = "SIMULATE_FIRST"   # Must dry-run before real execution
    BLOCK = "BLOCK"                     # Constitutionally blocked
    HOLD_888 = "HOLD_888"               # Irreversible, needs 888_HOLD


# ── Gate Request/Response ───────────────────────────────────────────────────

@dataclass
class MCPGateRequest:
    """What the gate needs to make a decision."""
    tool_name: str
    actor_id: str
    action_class: ActionClass
    risk: ActionRisk = field(default_factory=ActionRisk)
    session_active: bool = False
    lease_active: bool = False
    tool_args: dict = field(default_factory=dict)


@dataclass
class MCPGateResponse:
    """What the gate returns."""
    verdict: GateVerdict
    reason: str                          # One-line for Lapisan 1
    explanation: str                     # Five-line for Lapisan 2
    action_class: ActionClass
    floors_triggered: list[str] = field(default_factory=list)
    constitutional_chain_id: str | None = None


# ── The Gate ────────────────────────────────────────────────────────────────

class MCPGateV0:
    """Constitutional MCP Gate v0.

    Simple, brutal, working. No AI. No LLM. Pure deterministic rules.
    """

    # Tools that ALWAYS require SIMULATE_FIRST before real execution
    SIMULATE_REQUIRED_TOOLS: set[str] = {
        "geox_prospect_evaluate",
        "geox_seismic_compute",
        "geox_subsurface_generate_candidates",
        "forge_dry_run",
        "arif_forge",
    }

    # Tools that ALWAYS require 888_HOLD
    IRREVERSIBLE_TOOLS: set[str] = {
        "arif_seal",
        "forge_vault_seal",
        "forge_approve",
        "docker_volume_remove",
        "docker_container_remove",
        "systemctl_stop",
        "systemctl_restart",
        "hostinger_vps_restart",
        "hostinger_vps_stop",
        "git_push_force",
        "git_hard_reset",
        "geox_segy_export",
    }

    # Tools that REQUIRE_APPROVAL before execution
    APPROVAL_REQUIRED_TOOLS: set[str] = {
        "arif_forge",
        "forge_execute",
        "forge_approve",
        "docker_container_start",
        "docker_container_restart",
        "git_push",
        "git_commit",
        "write",
        "edit",
        "bash",
        "forge_filesystem_write",
        "forge_filesystem_delete",
        "forge_postgres_query",
    }

    # Tools that are BLOCKED entirely (constitutional prohibition)
    BLOCKED_TOOLS: set[str] = set()

    def judge(self, request: MCPGateRequest) -> MCPGateResponse:
        """The one entry point. All routing logic is here."""

        # ── Phase 1: Session gate ──────────────────────────────────────
        if not request.session_active and request.action_class not in (
            ActionClass.OBSERVE, ActionClass.SUGGEST
        ):
            return MCPGateResponse(
                verdict=GateVerdict.BLOCK,
                reason="No active session. Start one with arif_init.",
                explanation=(
                    "All non-observation actions require an active constitutional session. "
                    "Call arif_init(actor_id='...') first. "
                    "Sessions provide identity, lease, and audit context. "
                    "F1 AMANAH: no anonymous mutation."
                ),
                action_class=request.action_class,
                floors_triggered=["F1", "F8"],
            )

        # ── Phase 2: Blocked tools ─────────────────────────────────────
        if request.tool_name in self.BLOCKED_TOOLS:
            return MCPGateResponse(
                verdict=GateVerdict.BLOCK,
                reason=f"'{request.tool_name}' is constitutionally blocked.",
                explanation=(
                    f"The tool '{request.tool_name}' is in the BLOCKED registry. "
                    "This typically means it violates F9 ANTI-HANTU or F8 LAW. "
                    "Contact the sovereign to register an exception."
                ),
                action_class=request.action_class,
                floors_triggered=["F8", "F9"],
            )

        # ── Phase 3: Irreversible tools ────────────────────────────────
        if request.tool_name in self.IRREVERSIBLE_TOOLS:
            return MCPGateResponse(
                verdict=GateVerdict.HOLD_888,
                reason=f"'{request.tool_name}' is irreversible. 888_HOLD triggered.",
                explanation=(
                    f"'{request.tool_name}' performs an irreversible action. "
                    "Per F1 AMANAH and F13 SOVEREIGN, this requires explicit human approval. "
                    "The request has been queued in the AAA Cockpit approval queue. "
                    "Awaiting sovereign verdict."
                ),
                action_class=ActionClass.IRREVERSIBLE,
                floors_triggered=["F1", "F11", "F13"],
            )

        # ── Phase 4: SIMULATE_FIRST gate ───────────────────────────────
        if request.tool_name in self.SIMULATE_REQUIRED_TOOLS and request.action_class not in (
            ActionClass.SIMULATE, ActionClass.OBSERVE
        ):
            return MCPGateResponse(
                verdict=GateVerdict.SIMULATE_FIRST,
                reason=f"'{request.tool_name}' requires simulation before execution.",
                explanation=(
                    f"'{request.tool_name}' has physical-world or irreversible consequences. "
                    "Run it in SIMULATE mode first (forge_dry_run or equivalent). "
                    "Review the simulated output. Then re-submit with action_class=EXECUTE_REVERSIBLE. "
                    "F1 AMANAH: simulate before actuate."
                ),
                action_class=request.action_class,
                floors_triggered=["F1", "F4"],
            )

        # ── Phase 5: Risk-based gating ─────────────────────────────────
        # Physical impact → REQUIRE_APPROVAL
        if request.risk.physical_impact and request.action_class in (
            ActionClass.EXECUTE_REVERSIBLE, ActionClass.EXECUTE_HIGH_IMPACT
        ):
            return MCPGateResponse(
                verdict=GateVerdict.REQUIRE_APPROVAL,
                reason="Physical-world impact requires human approval.",
                explanation=(
                    "This action affects physical systems (machines, sensors, actuators). "
                    "Per F6 MARUAH and safety envelope doctrine, human must approve. "
                    "Queued in AAA Cockpit approval queue."
                ),
                action_class=request.action_class,
                floors_triggered=["F1", "F6", "F13"],
            )

        # Financial impact (high) → REQUIRE_APPROVAL
        if request.risk.financial_impact and request.action_class in (
            ActionClass.EXECUTE_HIGH_IMPACT, ActionClass.IRREVERSIBLE
        ):
            return MCPGateResponse(
                verdict=GateVerdict.REQUIRE_APPROVAL,
                reason="Financial impact requires human approval.",
                explanation=(
                    "This action affects capital allocation or billing. "
                    "Per WEALTH boundary governance, financial decisions need sovereign approval. "
                    "Queued in AAA Cockpit approval queue."
                ),
                action_class=request.action_class,
                floors_triggered=["F1", "F6", "F13"],
            )

        # Dignity impact → REQUIRE_APPROVAL
        if request.risk.dignity_impact:
            return MCPGateResponse(
                verdict=GateVerdict.REQUIRE_APPROVAL,
                reason="Human dignity impact requires review.",
                explanation=(
                    "This action may affect human dignity, privacy, or autonomy. "
                    "Per F6 MARUAH and F9 ANTI-HANTU, dignity-affected actions require "
                    "human review before execution. Queued in AAA Cockpit."
                ),
                action_class=request.action_class,
                floors_triggered=["F6", "F9", "F13"],
            )

        # High blast radius + non-OBSERVE → REQUIRE_APPROVAL
        if request.risk.blast_radius in ("high", "critical") and request.action_class not in (
            ActionClass.OBSERVE, ActionClass.SUGGEST, ActionClass.SIMULATE
        ):
            return MCPGateResponse(
                verdict=GateVerdict.REQUIRE_APPROVAL,
                reason=f"Blast radius '{request.risk.blast_radius}' requires approval.",
                explanation=(
                    f"Action classified as blast_radius={request.risk.blast_radius}. "
                    "High blast radius actions need human confirmation even if technically reversible. "
                    "F4 CLARITY: broad changes need visibility."
                ),
                action_class=request.action_class,
                floors_triggered=["F4", "F13"],
            )

        # ── Phase 6: Data sensitivity gate ──────────────────────────────
        if request.risk.data_sensitivity in ("confidential", "restricted"):
            return MCPGateResponse(
                verdict=GateVerdict.ALLOW_WITH_LOG,
                reason=f"Sensitive data ({request.risk.data_sensitivity}). Full audit trail.",
                explanation=(
                    f"Data sensitivity is '{request.risk.data_sensitivity}'. "
                    "Action is allowed but ALL interactions will be logged to VAULT999 "
                    "with full request/response capture. F11 AUDIT: sensitive operations "
                    "leave complete traces."
                ),
                action_class=request.action_class,
                floors_triggered=["F11"],
            )

        # ── Phase 7: Action class routing ──────────────────────────────
        action_routes: dict[ActionClass, GateVerdict] = {
            ActionClass.OBSERVE: GateVerdict.ALLOW,
            ActionClass.SUGGEST: GateVerdict.ALLOW_WITH_LOG,
            ActionClass.SIMULATE: GateVerdict.ALLOW,
            ActionClass.DRAFT: GateVerdict.ALLOW_WITH_LOG,
            ActionClass.QUEUE: GateVerdict.ALLOW_WITH_LOG,
            ActionClass.EXECUTE_REVERSIBLE: GateVerdict.ALLOW_WITH_LOG,
            ActionClass.EXECUTE_HIGH_IMPACT: GateVerdict.REQUIRE_APPROVAL,
            ActionClass.IRREVERSIBLE: GateVerdict.HOLD_888,
        }

        verdict = action_routes.get(request.action_class, GateVerdict.REQUIRE_APPROVAL)

        one_liners = {
            GateVerdict.ALLOW: "Action allowed.",
            GateVerdict.ALLOW_WITH_LOG: f"Action allowed ({request.action_class.value}). Logged.",
            GateVerdict.REQUIRE_APPROVAL: "Action requires human approval.",
            GateVerdict.SIMULATE_FIRST: "Simulate first.",
            GateVerdict.BLOCK: "Blocked by constitutional policy.",
            GateVerdict.HOLD_888: "Held for sovereign judgment.",
        }

        return MCPGateResponse(
            verdict=verdict,
            reason=one_liners[verdict],
            explanation=(
                f"Action class: {request.action_class.value}. "
                f"Reversible: {request.risk.reversible}. "
                f"Sensitivity: {request.risk.data_sensitivity}. "
                f"Physical: {request.risk.physical_impact}. "
                f"Financial: {request.risk.financial_impact}. "
                f"Dignity: {request.risk.dignity_impact}. "
                f"Blast radius: {request.risk.blast_radius}."
            ),
            action_class=request.action_class,
            floors_triggered=["F1", "F4", "F8", "F11", "F13"] if verdict != GateVerdict.ALLOW else [],
        )


# ── Standalone judge function ───────────────────────────────────────────────

def judge_action(
    tool_name: str,
    actor_id: str = "anonymous",
    action_class: str = "OBSERVE",
    reversible: bool = True,
    data_sensitivity: str = "public",
    physical_impact: bool = False,
    financial_impact: bool = False,
    dignity_impact: bool = False,
    blast_radius: str = "low",
    session_active: bool = False,
    lease_active: bool = False,
    tool_args: dict | None = None,
) -> dict:
    """Quick one-shot gate call. Returns dict for easy JSON serialization.

    This is the primary public API. Call it from any MCP tool or REST endpoint.
    """
    try:
        action_class_enum = ActionClass(action_class.upper())
    except ValueError:
        action_class_enum = ActionClass.OBSERVE

    request = MCPGateRequest(
        tool_name=tool_name,
        actor_id=actor_id,
        action_class=action_class_enum,
        risk=ActionRisk(
            reversible=reversible,
            data_sensitivity=data_sensitivity,
            physical_impact=physical_impact,
            financial_impact=financial_impact,
            dignity_impact=dignity_impact,
            blast_radius=blast_radius,
        ),
        session_active=session_active,
        lease_active=lease_active,
        tool_args=tool_args or {},
    )

    gate = MCPGateV0()
    response = gate.judge(request)

    return {
        "verdict": response.verdict.value,
        "reason": response.reason,
        "explanation": response.explanation,
        "action_class": response.action_class.value,
        "floors_triggered": response.floors_triggered,
        "constitutional_chain_id": response.constitutional_chain_id,
        # Lapisan 1: one-line
        "_summary": f"{response.verdict.value}: {response.reason}",
        # Lapisan 2: five-line
        "_detail": (
            f"Tool: {tool_name}\n"
            f"Action: {response.action_class.value}\n"
            f"Risk: reversible={reversible}, sensitivity={data_sensitivity}, "
            f"physical={physical_impact}, financial={financial_impact}, "
            f"dignity={dignity_impact}, blast={blast_radius}\n"
            f"Floors: {', '.join(response.floors_triggered) if response.floors_triggered else 'none triggered'}\n"
            f"Session: {'active' if session_active else 'inactive'}"
        ),
    }
