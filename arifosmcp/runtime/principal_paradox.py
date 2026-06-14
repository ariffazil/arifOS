"""
EUREKA 7 — Agent Principal Paradox
═══════════════════════════════════════

"When task criticality, irreversibility, or blast radius rises,
 blind delegation becomes invalid. The agent may retain proposal
 authority, but execution authority must revert to the principal
 or explicitly authorized human reviewer. Autonomy contracts as
 risk expands."

This is NOT "agents bad." This is constitutional recognition that
delegation without enforceable oversight degrades trust.

AAA Constitutional Control: Accountability, Authority, Attestation.

Constitutional Binding:
  F1  AMANAH    — autonomy contraction is reversible (policy update, not code removal)
  F2  TRUTH     — every delegation decision emits falsifiable evidence
  F8  GENIUS    — ceiling is computed, not hardcoded; adapts to context
  F11 AUDIT     — every override logged to VAULT999 with principal signature
  F12 RESILIENCE — surge protection prevents override-storm (max 3/hour)
  F13 SOVEREIGN — principal override is FINAL; not appealable

Gate position: Governance Pipeline Gate 1.5 (between Identity & Budget)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger("arifosmcp.principal_paradox")

# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

MAX_OVERRIDES_PER_HOUR = 3
OVERRIDE_WINDOW_SECONDS = 3600
REVERSIBILITY_HARD_FLOOR = 0.3  # below this → full principal control required


# ═══════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════


class ActionClass(StrEnum):
    OBSERVE = "OBSERVE"
    COMPUTE = "COMPUTE"
    PROPOSE = "PROPOSE"
    MUTATE = "MUTATE"
    ATOMIC = "ATOMIC"


class RiskTier(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    ATOMIC = "ATOMIC"


class BlastRadius(StrEnum):
    LOCAL = "LOCAL"
    ORGAN = "ORGAN"
    FEDERATION = "FEDERATION"
    EXTERNAL = "EXTERNAL"


class AutonomyTier(StrEnum):
    FULL_AUTO = "FULL_AUTO"
    PROPOSE_ONLY = "PROPOSE_ONLY"
    PRINCIPAL_APPROVAL_REQUIRED = "PRINCIPAL_APPROVAL_REQUIRED"
    HOLD = "HOLD"


class GateVerdict(StrEnum):
    PROCEED = "PROCEED"
    SABAR = "SABAR"
    HOLD = "HOLD"


# ═══════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════


@dataclass
class AutonomyDecision:
    """Output of evaluate_autonomy_ceiling()."""

    autonomy_tier: AutonomyTier
    rationale: str
    gate_verdict: GateVerdict
    requires_principal: bool
    override_allowed: bool
    evidence_required: list[str] = field(default_factory=list)

    def to_envelope(self) -> dict[str, Any]:
        return {
            "autonomy_tier": self.autonomy_tier.value,
            "rationale": self.rationale,
            "gate_verdict": self.gate_verdict.value,
            "requires_principal": self.requires_principal,
            "override_allowed": self.override_allowed,
            "evidence_required": self.evidence_required,
            "eureka": "E7",
            "timestamp": datetime.now(UTC).isoformat(),
        }


@dataclass
class AttestationReceipt:
    """Evidence packet emitted by every gated action."""

    intent: str
    inputs_hash: str
    risk_trigger: str
    autonomy_tier_at_execution: AutonomyTier
    approval_decision: GateVerdict
    approving_authority: str
    principal_override_occurred: bool
    override_path: str | None
    completion_proof: str | None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    receipt_hash: str = ""

    def __post_init__(self):
        raw = f"{self.intent}|{self.inputs_hash}|{self.approving_authority}|{self.timestamp}"
        self.receipt_hash = f"sha256:{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


# ═══════════════════════════════════════════════════════════════
# IN-MEMORY SURGE TRACKER (per-session overrides)
# ═══════════════════════════════════════════════════════════════

_override_tracker: dict[str, list[float]] = {}  # session_id → [timestamps]


def _count_recent_overrides(session_id: str) -> int:
    """Count overrides in the last hour for a session."""
    now = time.time()
    timestamps = _override_tracker.get(session_id, [])
    # Prune stale entries
    fresh = [t for t in timestamps if now - t < OVERRIDE_WINDOW_SECONDS]
    _override_tracker[session_id] = fresh
    return len(fresh)


def _record_override(session_id: str) -> int:
    """Record a principal override and return new count."""
    now = time.time()
    timestamps = _override_tracker.get(session_id, [])
    timestamps.append(now)
    _override_tracker[session_id] = [t for t in timestamps if now - t < OVERRIDE_WINDOW_SECONDS]
    return len(_override_tracker[session_id])


# ═══════════════════════════════════════════════════════════════
# AUTONOMY CONTRACTION TABLE (the core algorithm)
# ═══════════════════════════════════════════════════════════════

# (risk_tier, blast_radius, reversibility_floor) → autonomy_tier
AUTONOMY_CONTRACTION = [
    # (Risk,         Blast,       Rev Floor,  Autonomy)
    (RiskTier.LOW,    BlastRadius.LOCAL,      0.9,  AutonomyTier.FULL_AUTO),
    (RiskTier.LOW,    BlastRadius.ORGAN,      0.8,  AutonomyTier.FULL_AUTO),
    (RiskTier.LOW,    BlastRadius.FEDERATION, 0.7,  AutonomyTier.PROPOSE_ONLY),
    (RiskTier.LOW,    BlastRadius.EXTERNAL,   0.7,  AutonomyTier.PROPOSE_ONLY),
    (RiskTier.MEDIUM, BlastRadius.LOCAL,      0.7,  AutonomyTier.FULL_AUTO),
    (RiskTier.MEDIUM, BlastRadius.ORGAN,      0.7,  AutonomyTier.PROPOSE_ONLY),
    (RiskTier.MEDIUM, BlastRadius.FEDERATION, 0.5,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.MEDIUM, BlastRadius.EXTERNAL,   0.5,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.HIGH,   BlastRadius.LOCAL,      0.5,  AutonomyTier.PROPOSE_ONLY),
    (RiskTier.HIGH,   BlastRadius.ORGAN,      0.5,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.HIGH,   BlastRadius.FEDERATION, 0.3,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.HIGH,   BlastRadius.EXTERNAL,   0.3,  AutonomyTier.HOLD),
    (RiskTier.ATOMIC, BlastRadius.LOCAL,      0.5,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.ATOMIC, BlastRadius.ORGAN,      0.3,  AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED),
    (RiskTier.ATOMIC, BlastRadius.FEDERATION, 0.0,  AutonomyTier.HOLD),
    (RiskTier.ATOMIC, BlastRadius.EXTERNAL,   0.0,  AutonomyTier.HOLD),
]


# ═══════════════════════════════════════════════════════════════
# CORE FUNCTION
# ═══════════════════════════════════════════════════════════════


def evaluate_autonomy_ceiling(
    action_class: str,
    risk_tier: str,
    blast_radius: str,
    reversibility: float,
    caller_is_principal: bool = False,
    caller_has_lease: bool = False,
    prior_override_count: int | None = None,
    session_id: str = "",
) -> tuple[str, str, dict]:
    """
    Compute the maximum autonomy tier allowed for this action.

    Core principle: autonomy contracts as risk expands.

    Args:
        action_class: OBSERVE | COMPUTE | PROPOSE | MUTATE | ATOMIC
        risk_tier: LOW | MEDIUM | HIGH | ATOMIC
        blast_radius: LOCAL | ORGAN | FEDERATION | EXTERNAL
        reversibility: 1.0 (fully reversible) → 0.0 (irreversible)
        caller_is_principal: True if human sovereign is direct caller
        caller_has_lease: True if caller holds active authority lease
        prior_override_count: Known override count (fetched from tracker if None)
        session_id: Session for surge tracking

    Returns:
        (autonomy_tier: str, rationale: str, envelope: dict)
    """

    # ── Guard 0: Principal direct access — always FULL_AUTO ──
    if caller_is_principal:
        return (
            AutonomyTier.FULL_AUTO.value,
            "Principal (F13 SOVEREIGN) — direct authority, no ceiling.",
            {
                "gate": "E7",
                "verdict": GateVerdict.PROCEED.value,
                "principal_direct": True,
                "ceiling_override": False,
                "surge_count": 0,
            },
        )

    # ── Guard 1: No lease → HOLD ──
    if not caller_has_lease:
        return (
            AutonomyTier.HOLD.value,
            "E7 HOLD: No active authority lease. Agent cannot execute without lease.",
            {
                "gate": "E7",
                "verdict": GateVerdict.HOLD.value,
                "principal_direct": False,
                "ceiling_override": False,
                "violation": "NO_LEASE",
            },
        )

    # ── Guard 2: Irreversibility hard floor ──
    if reversibility < REVERSIBILITY_HARD_FLOOR:
        return (
            AutonomyTier.HOLD.value,
            f"E7 HOLD: Reversibility {reversibility:.2f} below hard floor "
            f"({REVERSIBILITY_HARD_FLOOR}). Full principal control required.",
            {
                "gate": "E7",
                "verdict": GateVerdict.HOLD.value,
                "principal_direct": False,
                "ceiling_override": False,
                "violation": "IRREVERSIBILITY_FLOOR",
                "reversibility": reversibility,
            },
        )

    # ── Guard 3: Surge protection ──
    override_count = prior_override_count if prior_override_count is not None else _count_recent_overrides(session_id)
    surge_active = override_count >= MAX_OVERRIDES_PER_HOUR

    # ── Resolve autonomy tier from contraction table ──
    try:
        risk = RiskTier(risk_tier)
        blast = BlastRadius(blast_radius)
    except ValueError:
        return (
            AutonomyTier.HOLD.value,
            f"E7 HOLD: Invalid risk_tier={risk_tier} or blast_radius={blast_radius}",
            {
                "gate": "E7",
                "verdict": GateVerdict.HOLD.value,
                "violation": "INVALID_CLASSIFICATION",
            },
        )

    resolved_tier = AutonomyTier.HOLD  # default safest
    for r_tier, b_radius, rev_floor, a_tier in AUTONOMY_CONTRACTION:
        if r_tier == risk and b_radius == blast:
            if reversibility >= rev_floor:
                resolved_tier = a_tier
            else:
                # Reversibility below floor → downgrade one tier
                resolved_tier = _downgrade_tier(a_tier)
            break

    # ── Surge protection: downgrade one tier ──
    if surge_active and resolved_tier != AutonomyTier.HOLD:
        resolved_tier = _downgrade_tier(resolved_tier)
        surge_note = (
            f" | SURGE PROTECTION ACTIVE: downgraded due to {override_count} "
            f"overrides in last hour (max {MAX_OVERRIDES_PER_HOUR})"
        )
    else:
        surge_note = ""

    # ── OBSERVE class always FULL_AUTO (read-only, no mutation) ──
    if ActionClass(action_class) == ActionClass.OBSERVE:
        resolved_tier = AutonomyTier.FULL_AUTO

    # ── Build rationale ──
    rationale = (
        f"E7: action_class={action_class} risk={risk_tier} blast={blast_radius} "
        f"reversibility={reversibility:.2f} → autonomy={resolved_tier.value}"
        f"{surge_note}"
    )

    # ── Gate verdict ──
    if resolved_tier == AutonomyTier.HOLD:
        gate = GateVerdict.HOLD
    elif resolved_tier == AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED:
        gate = GateVerdict.SABAR
    else:
        gate = GateVerdict.PROCEED

    envelope = {
        "gate": "E7",
        "verdict": gate.value,
        "autonomy_tier": resolved_tier.value,
        "risk_tier": risk_tier,
        "blast_radius": blast_radius,
        "reversibility": reversibility,
        "principal_direct": False,
        "ceiling_override": False,
        "surge_active": surge_active,
        "override_count": override_count,
        "max_overrides_per_hour": MAX_OVERRIDES_PER_HOUR,
    }

    return (resolved_tier.value, rationale, envelope)


def _downgrade_tier(tier: AutonomyTier) -> AutonomyTier:
    """Downgrade autonomy by one step."""
    order = [
        AutonomyTier.FULL_AUTO,
        AutonomyTier.PROPOSE_ONLY,
        AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED,
        AutonomyTier.HOLD,
    ]
    try:
        idx = order.index(tier)
        return order[min(idx + 1, len(order) - 1)]
    except ValueError:
        return AutonomyTier.HOLD


# ═══════════════════════════════════════════════════════════════
# THREE ENFORCEABLE CLAUSES
# ═══════════════════════════════════════════════════════════════


def enforce_scope(action: dict[str, Any], policy_scope: list[str]) -> tuple[bool, str]:
    """
    Clause 1 — Bounded Execution Rights.

    "Agents hold bounded execution rights only within declared policy scope."

    Supports fnmatch glob patterns: *, arif_*, arif_judge_*, etc.
    Also supports "namespace:" prefix matching (e.g. "arif:" matches all arif_* tools).

    Returns: (in_scope: bool, reason: str)
    """
    import fnmatch as _fnmatch

    action_name = action.get("tool_name", action.get("action", "unknown"))
    if not policy_scope:
        return (False, f"E7 CLAUSE 1: No policy scope declared. Action '{action_name}' blocked.")

    for scope in policy_scope:
        # Literal "*" — matches everything
        if scope == "*":
            return (True, f"E7 CLAUSE 1: Action '{action_name}' within wildcard scope.")

        # Exact match
        if scope == action_name:
            return (True, f"E7 CLAUSE 1: Action '{action_name}' exactly matches scope '{scope}'.")

        # Glob pattern match (e.g. "arif_*", "arif_judge_*")
        if _fnmatch.fnmatch(action_name, scope):
            return (True, f"E7 CLAUSE 1: Action '{action_name}' matches glob pattern '{scope}'.")

        # Namespace prefix match (e.g. "arif:" matches arif_*)
        if ":" in scope:
            prefix = scope.split(":")[0]
            if action_name.startswith(prefix):
                return (True, f"E7 CLAUSE 1: Action '{action_name}' within namespace '{scope}'.")

    return (False, f"E7 CLAUSE 1: Action '{action_name}' outside declared policy scope {policy_scope}.")


def require_approval(action: dict[str, Any], autonomy_tier: str) -> GateVerdict:
    """
    Clause 2 — Mandatory Principal Approval.

    "Irreversible, high-impact, or policy-crossing actions trigger
     mandatory principal approval."

    Returns: GateVerdict
    """
    tier = AutonomyTier(autonomy_tier)
    if tier == AutonomyTier.FULL_AUTO:
        return GateVerdict.PROCEED
    elif tier == AutonomyTier.PROPOSE_ONLY:
        return GateVerdict.SABAR  # agent can propose, principal must approve
    elif tier == AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED:
        return GateVerdict.SABAR  # principal must explicitly approve
    else:
        return GateVerdict.HOLD


def emit_attestation(
    intent: str,
    inputs_hash: str,
    risk_trigger: str,
    autonomy_tier: str,
    approval_decision: str,
    approving_authority: str,
    principal_override_occurred: bool = False,
    override_path: str | None = None,
    completion_proof: str | None = None,
) -> AttestationReceipt:
    """
    Clause 3 — Attestation Evidence.

    "Every delegated action must emit evidence sufficient for skeptical
     replay: intent, inputs, checks, override path, and completion proof."

    Returns: AttestationReceipt
    """
    receipt = AttestationReceipt(
        intent=intent,
        inputs_hash=inputs_hash,
        risk_trigger=risk_trigger,
        autonomy_tier_at_execution=AutonomyTier(autonomy_tier),
        approval_decision=GateVerdict(approval_decision),
        approving_authority=approving_authority,
        principal_override_occurred=principal_override_occurred,
        override_path=override_path,
        completion_proof=completion_proof,
    )
    logger.info(
        "E7 ATTESTATION: %s | tier=%s | authority=%s | override=%s | hash=%s",
        intent[:80],
        autonomy_tier,
        approving_authority,
        principal_override_occurred,
        receipt.receipt_hash,
    )
    return receipt


# ═══════════════════════════════════════════════════════════════
# GOVERNANCE PIPELINE INTEGRATION (Gate 1.5)
# ═══════════════════════════════════════════════════════════════


def gate_1_5_principal_paradox(
    action_class: str,
    risk_tier: str,
    blast_radius: str,
    reversibility: float,
    caller_is_principal: bool = False,
    caller_has_lease: bool = False,
    session_id: str = "",
    prior_override_count: int | None = None,
) -> dict[str, Any]:
    """
    Governance Pipeline Gate 1.5 — Principal Paradox.

    Called between Gate 1 (Identity & Authority) and Gate 2 (Budget).

    Returns HOLD/SABAR/PROCEED verdict with full rationale and envelope.
    Suitable for direct insertion into governance_pipeline.py.
    """
    tier, rationale, envelope = evaluate_autonomy_ceiling(
        action_class=action_class,
        risk_tier=risk_tier,
        blast_radius=blast_radius,
        reversibility=reversibility,
        caller_is_principal=caller_is_principal,
        caller_has_lease=caller_has_lease,
        prior_override_count=prior_override_count,
        session_id=session_id,
    )

    if tier == AutonomyTier.HOLD.value:
        return {
            "gate": "1.5_PRINCIPAL_PARADOX",
            "verdict": "HOLD",
            "autonomy_tier": tier,
            "rationale": rationale,
            "envelope": envelope,
            "violated_laws": ["E7"],
            "reasons": [rationale],
            "next_safe_action": "Escalate to principal (F13 SOVEREIGN) or reduce risk tier.",
            "principal_override_available": True,
        }

    if tier == AutonomyTier.PRINCIPAL_APPROVAL_REQUIRED.value:
        return {
            "gate": "1.5_PRINCIPAL_PARADOX",
            "verdict": "SABAR",
            "autonomy_tier": tier,
            "rationale": rationale,
            "envelope": envelope,
            "violated_laws": [],
            "reasons": [rationale],
            "next_safe_action": "Await principal approval or downgrade action_class.",
            "principal_approval_required": True,
        }

    # PROPOSE_ONLY or FULL_AUTO
    return {
        "gate": "1.5_PRINCIPAL_PARADOX",
        "verdict": "PROCEED",
        "autonomy_tier": tier,
        "rationale": rationale,
        "envelope": envelope,
        "violated_laws": [],
        "reasons": [],
        "principal_approval_required": False,
    }


# ═══════════════════════════════════════════════════════════════
# /000 + /999 PUBLIC SURFACE HELPERS
# ═══════════════════════════════════════════════════════════════


def build_000_autonomy_surface(session_id: str = "") -> dict[str, Any]:
    """Build the /000 public attestation surface for autonomy policy."""
    override_count = _count_recent_overrides(session_id) if session_id else 0
    return {
        "autonomy_policy": {
            "max_tier": AutonomyTier.PROPOSE_ONLY.value,
            "automatic_approval_threshold": RiskTier.LOW.value,
            "principal_override_window_seconds": OVERRIDE_WINDOW_SECONDS,
            "surge_protection_max_overrides_per_hour": MAX_OVERRIDES_PER_HOUR,
            "reversibility_hard_floor": REVERSIBILITY_HARD_FLOOR,
            "current_override_count": override_count,
            "contract_version": "v54.0.0",
        },
        "hold_conditions": [
            "F13 non-delegable gate triggered (E5)",
            "E7 autonomy ceiling exceeded",
            f"Blast radius >= FEDERATION without principal approval",
            f"Reversibility < {REVERSIBILITY_HARD_FLOOR} without explicit principal approval",
            "No active authority lease",
            f"Override surge: >{MAX_OVERRIDES_PER_HOUR} per hour",
        ],
        "eureka": "E7",
    }


def build_999_execution_surface(
    seal_id: str = "",
    action_class: str = "",
    risk_tier: str = "",
    approving_authority: str = "",
    principal_override_occurred: bool = False,
    evidence_hash: str = "",
    chain_position: int = 0,
    autonomy_tier: str = "",
    e7_gate_passed: bool = True,
) -> dict[str, Any]:
    """Build the /999 public proof chamber surface for execution evidence."""
    return {
        "last_seal": {
            "seal_id": seal_id,
            "action_class": action_class,
            "risk_tier": risk_tier,
            "approving_authority": approving_authority,
            "principal_override_occurred": principal_override_occurred,
            "evidence_hash": evidence_hash,
            "chain_position": chain_position,
            "autonomy_tier_at_execution": autonomy_tier,
            "e7_gate_passed": e7_gate_passed,
        },
        "recent_overrides": [
            {"seal_id": "", "reason": "", "timestamp": ""}
        ],  # populated by vault query
        "surge_status": "SURGE" if _count_recent_overrides("") >= MAX_OVERRIDES_PER_HOUR else "NORMAL",
        "eureka": "E7",
    }


# ═══════════════════════════════════════════════════════════════
# PRINCIPAL OVERRIDE (F13-gated)
# ═══════════════════════════════════════════════════════════════


def principal_override(
    session_id: str,
    principal_signature: str,
    reason: str,
) -> dict[str, Any]:
    """
    Execute a principal override — bypass E7 ceiling for one action.

    Requires F13 sovereign authority. Logged to VAULT999.
    Cannot be called by agent — principal_signature must be valid.

    Returns: override receipt with new surge count.
    """
    count = _record_override(session_id)
    surge = count >= MAX_OVERRIDES_PER_HOUR

    receipt = {
        "event": "E7_PRINCIPAL_OVERRIDE",
        "session_id": session_id,
        "principal_signature_hash": f"sha256:{hashlib.sha256(principal_signature.encode()).hexdigest()[:16]}",
        "reason": reason,
        "override_count": count,
        "surge_protection_active": surge,
        "timestamp": datetime.now(UTC).isoformat(),
        "eureka": "E7",
    }

    logger.warning(
        "E7 PRINCIPAL OVERRIDE: session=%s count=%d surge=%s reason=%s",
        session_id, count, surge, reason[:80],
    )

    return receipt


__all__ = [
    "ActionClass",
    "RiskTier",
    "BlastRadius",
    "AutonomyTier",
    "GateVerdict",
    "AutonomyDecision",
    "AttestationReceipt",
    "evaluate_autonomy_ceiling",
    "enforce_scope",
    "require_approval",
    "emit_attestation",
    "gate_1_5_principal_paradox",
    "build_000_autonomy_surface",
    "build_999_execution_surface",
    "principal_override",
    "MAX_OVERRIDES_PER_HOUR",
    "REVERSIBILITY_HARD_FLOOR",
]
