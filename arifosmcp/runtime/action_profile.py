"""
action_profile.py — arifOS D1: Immutable Action Classification (dependency-graph precondition)

Per D1 (2026-07-13 corrective): gates must not generate facts that other
gates need. Classification runs FIRST and produces an immutable action_profile
that downstream gates consume — but never modify.

The action_profile freezes 7 facts:
  1. tool
  2. mutation class         (NONE | EPHEMERAL | UPDATE | DELETE | APPEND_ONLY)
  3. reversibility          (READ_ONLY | REVERSIBLE | COMPENSATABLE | IRREVERSIBLE)
  4. blast_radius           (LOCAL | SESSION | SERVICE | DATASET | INFRASTRUCTURE | FEDERATION)
  5. infrastructure_impact  (NONE | LOW | MEDIUM | HIGH | CRITICAL)
  6. governance_impact      (LOW | MODERATE | HIGH | CONSTITUTIONAL)
  7. receipt_class          (SESSION_OBSERVED | SESSION_CLOSURE | SOVEREIGN_DECISION |
                             OPERATIONAL | AUDIT_FINDING | RECOVERY_CHECKPOINT)
  8. required_capability    (e.g. "vault.append.session_closure", "vault.append.sovereign")
  9. sovereign_required     (bool)

These 9 facts resolve the four orthogonal questions:

  Q1. Can this action destroy infrastructure?
      NO  if blast_radius < INFRASTRUCTURE AND infrastructure_impact <= LOW
      YES otherwise

  Q2. Can this action be reversed?
      YES if reversibility in {READ_ONLY, REVERSIBLE, COMPENSATABLE}
      NO  if reversibility == IRREVERSIBLE

  Q3. Does this require F13 sovereign authority?
      YES if sovereign_required == True
      NO  otherwise

  Q4. What capability must back this action?
      answer = required_capability

Receives:
    request — normalised request envelope (caller decides shape)
    manifest — tool manifest entry from canonical tool registry
    session — session record from canonical store
    actor — canonical actor identity

Returns:
    ActionProfile (frozen dataclass, hash-stable)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS — orthogonal axes per A1.R2 + D1
# ═══════════════════════════════════════════════════════════════════════════════


class MutationClass(str, Enum):
    NONE = "none"
    EPHEMERAL = "ephemeral"
    UPDATE = "update"
    DELETE = "delete"
    APPEND_ONLY = "append_only"


class Reversibility(str, Enum):
    READ_ONLY = "read_only"
    REVERSIBLE = "reversible"
    COMPENSATABLE = "compensatable"
    IRREVERSIBLE = "irreversible"


class BlastRadius(str, Enum):
    LOCAL = "local"
    SESSION = "session"
    SERVICE = "service"
    DATASET = "dataset"
    INFRASTRUCTURE = "infrastructure"
    FEDERATION = "federation"


class InfrastructureImpact(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GovernanceImpact(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CONSTITUTIONAL = "constitutional"


class ReceiptClass(str, Enum):
    """Closure classes — SESSION_OBSERVED / SESSION_CLOSURE are operational;
    SOVEREIGN_DECISION / RECOVERY_CHECKPOINT are sovereign-grade; etc."""

    SESSION_OBSERVED = "session_observed"  # session existed but not fully governed
    SESSION_CLOSURE = "session_closure"  # governed session completed
    OPERATIONAL = "operational"  # routine receipt (signed by service)
    AUDIT_FINDING = "audit_finding"  # A-AUDIT-delivered
    RECOVERY_CHECKPOINT = "recovery_checkpoint"  # sovereign + recovery quorum
    SOVEREIGN_DECISION = "sovereign_decision"  # F13-only


# ═══════════════════════════════════════════════════════════════════════════════
# IMMUTABLE ACTION_PROFILE
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ActionProfile:
    """Frozen, hash-stable classification of one request.

    All 9 facts are derived deterministically from the inputs. The result is
    IMMUTABLE — no gate may mutate fields after creation. Subsequent gates
    consume this profile but never produce new values that earlier gates need.
    """

    tool: str
    mutation: MutationClass
    reversibility: Reversibility
    blast_radius: BlastRadius
    infrastructure_impact: InfrastructureImpact
    governance_impact: GovernanceImpact
    receipt_class: ReceiptClass
    required_capability: str
    sovereign_required: bool

    def requires_infrastructure_gate(self) -> bool:
        """True if Gate 5 (infrastructure consequence) MUST run."""
        return self.blast_radius in {
            BlastRadius.INFRASTRUCTURE,
            BlastRadius.FEDERATION,
        } or self.infrastructure_impact in {
            InfrastructureImpact.HIGH,
            InfrastructureImpact.CRITICAL,
        }

    def requires_irreversible_governance_gate(self) -> bool:
        """True if Gate 6 (constitutional / irreversibility governance) MUST run."""
        return self.reversibility == Reversibility.IRREVERSIBLE

    def requires_sovereign_authority(self) -> bool:
        """True if F13 capability/identity path is required."""
        return self.sovereign_required

    def profile_hash(self) -> str:
        """Stable hash of the profile — used for vault.append payload binding."""
        import hashlib

        canonical = repr(
            tuple(
                sorted(
                    {
                        "tool": self.tool,
                        "mutation": self.mutation.value,
                        "reversibility": self.reversibility.value,
                        "blast_radius": self.blast_radius.value,
                        "infrastructure_impact": self.infrastructure_impact.value,
                        "governance_impact": self.governance_impact.value,
                        "receipt_class": self.receipt_class.value,
                        "required_capability": self.required_capability,
                        "sovereign_required": self.sovereign_required,
                    }.items()
                )
            )
        )
        return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()}"

    def to_dict(self) -> dict:
        return {
            "tool": self.tool,
            "mutation": self.mutation.value,
            "reversibility": self.reversibility.value,
            "blast_radius": self.blast_radius.value,
            "infrastructure_impact": self.infrastructure_impact.value,
            "governance_impact": self.governance_impact.value,
            "receipt_class": self.receipt_class.value,
            "required_capability": self.required_capability,
            "sovereign_required": self.sovereign_required,
            "profile_hash": self.profile_hash(),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL MANIFEST (canonical taxonomy — single source of truth)
# ═══════════════════════════════════════════════════════════════════════════════

# Each entry is the canonical classification for a tool call.
# Derived from spec examples + A1.R2 multi-dimensional taxonomy.
TOOL_ACTION_PROFILE_TABLE: dict[str, dict] = {
    # Append-only vault operations
    "arif_seal": {
        "mutation": MutationClass.APPEND_ONLY,
        "reversibility": Reversibility.IRREVERSIBLE,
        "blast_radius": BlastRadius.DATASET,
        "infrastructure_impact": InfrastructureImpact.NONE,
        "governance_impact": GovernanceImpact.CONSTITUTIONAL,
        "receipt_class_default": ReceiptClass.SESSION_CLOSURE,
        "required_capability_default": "vault.append.session_closure",
        "sovereign_required_default": False,
    },
    # Session lifecycle
    "arif_init": {
        "mutation": MutationClass.UPDATE,
        "reversibility": Reversibility.COMPENSATABLE,
        "blast_radius": BlastRadius.SESSION,
        "infrastructure_impact": InfrastructureImpact.NONE,
        "governance_impact": GovernanceImpact.MODERATE,
        "receipt_class_default": ReceiptClass.OPERATIONAL,
        "required_capability_default": "session.create",
        "sovereign_required_default": False,
    },
    "session_close": {
        "mutation": MutationClass.UPDATE,
        "reversibility": Reversibility.IRREVERSIBLE,
        "blast_radius": BlastRadius.SESSION,
        "infrastructure_impact": InfrastructureImpact.NONE,
        "governance_impact": GovernanceImpact.MODERATE,
        "receipt_class_default": ReceiptClass.SESSION_CLOSURE,
        "required_capability_default": "session.close",
        "sovereign_required_default": False,
    },
    # Production operations — must trigger infrastructure gate
    "deploy_to_production": {
        "mutation": MutationClass.UPDATE,
        "reversibility": Reversibility.REVERSIBLE,
        "blast_radius": BlastRadius.INFRASTRUCTURE,
        "infrastructure_impact": InfrastructureImpact.HIGH,
        "governance_impact": GovernanceImpact.HIGH,
        "receipt_class_default": ReceiptClass.OPERATIONAL,
        "required_capability_default": "infra.deploy",
        "sovereign_required_default": False,
    },
    "delete_database": {
        "mutation": MutationClass.DELETE,
        "reversibility": Reversibility.IRREVERSIBLE,
        "blast_radius": BlastRadius.DATASET,
        "infrastructure_impact": InfrastructureImpact.HIGH,
        "governance_impact": GovernanceImpact.HIGH,
        "receipt_class_default": ReceiptClass.OPERATIONAL,
        "required_capability_default": "database.delete",
        "sovereign_required_default": False,
    },
    # Sovereign-grade operations
    "constitutional_amend": {
        "mutation": MutationClass.UPDATE,
        "reversibility": Reversibility.COMPENSATABLE,
        "blast_radius": BlastRadius.FEDERATION,
        "infrastructure_impact": InfrastructureImpact.HIGH,
        "governance_impact": GovernanceImpact.CONSTITUTIONAL,
        "receipt_class_default": ReceiptClass.SOVEREIGN_DECISION,
        "required_capability_default": "vault.append.sovereign",
        "sovereign_required_default": True,
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════


def classify_action(
    tool: str,
    *,
    # Optional overrides from request context (otherwise use canonical table)
    mutation: MutationClass | None = None,
    reversibility: Reversibility | None = None,
    blast_radius: BlastRadius | None = None,
    infrastructure_impact: InfrastructureImpact | None = None,
    governance_impact: GovernanceImpact | None = None,
    receipt_class: ReceiptClass | None = None,
    required_capability: str | None = None,
    sovereign_required: bool | None = None,
    # Request-context hints
    actor_id: str | None = None,
    session_id: str | None = None,
) -> ActionProfile:
    """Produce an immutable ActionProfile for the request.

    Lookup logic:
    1. If tool has canonical entry in TOOL_ACTION_PROFILE_TABLE, use it.
    2. Apply any explicit overrides.
    3. Return frozen ActionProfile (cannot be mutated by callers).

    Raises:
        ValueError on unknown tool and no overrides provided.
    """
    base = TOOL_ACTION_PROFILE_TABLE.get(tool)
    if base is None and mutation is None:
        raise ValueError(f"Tool {tool!r} has no canonical profile and no mutation override")
    if base is None:
        # Pure override path
        base = {
            "mutation": mutation or MutationClass.NONE,
            "reversibility": reversibility or Reversibility.READ_ONLY,
            "blast_radius": blast_radius or BlastRadius.LOCAL,
            "infrastructure_impact": infrastructure_impact or InfrastructureImpact.NONE,
            "governance_impact": governance_impact or GovernanceImpact.LOW,
            "receipt_class_default": ReceiptClass.OPERATIONAL,
            "required_capability_default": required_capability or f"tool.{tool}",
            "sovereign_required_default": sovereign_required
            if sovereign_required is not None
            else False,
        }

    return ActionProfile(
        tool=tool,
        mutation=mutation or base["mutation"],
        reversibility=reversibility or base["reversibility"],
        blast_radius=blast_radius or base["blast_radius"],
        infrastructure_impact=infrastructure_impact or base["infrastructure_impact"],
        governance_impact=governance_impact or base["governance_impact"],
        receipt_class=receipt_class or base["receipt_class_default"],
        required_capability=required_capability or base["required_capability_default"],
        sovereign_required=sovereign_required
        if sovereign_required is not None
        else base["sovereign_required_default"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GATE STRUCTURED OUTPUT
# ═══════════════════════════════════════════════════════════════════════════════

from enum import Enum as _Enum


class GateStatus(str, _Enum):
    PASS = "pass"
    HOLD = "hold"
    DENY = "deny"


@dataclass(frozen=True)
class GateOutput:
    """Structured gate result per D1 — no bare bool, no fact-propagation."""

    status: GateStatus
    reason: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    obligations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "reason": self.reason,
            "evidence_refs": list(self.evidence_refs),
            "obligations": list(self.obligations),
        }


def gate_pass(
    reason: str = "", evidence_refs: list[str] | None = None, obligations: list[str] | None = None
) -> GateOutput:
    return GateOutput(GateStatus.PASS, reason, list(evidence_refs or []), list(obligations or []))


def gate_hold(
    reason: str = "", evidence_refs: list[str] | None = None, obligations: list[str] | None = None
) -> GateOutput:
    return GateOutput(GateStatus.HOLD, reason, list(evidence_refs or []), list(obligations or []))


def gate_deny(
    reason: str = "", evidence_refs: list[str] | None = None, obligations: list[str] | None = None
) -> GateOutput:
    return GateOutput(GateStatus.DENY, reason, list(evidence_refs or []), list(obligations or []))


__all__ = [
    "MutationClass",
    "Reversibility",
    "BlastRadius",
    "InfrastructureImpact",
    "GovernanceImpact",
    "ReceiptClass",
    "ActionProfile",
    "TOOL_ACTION_PROFILE_TABLE",
    "classify_action",
    "GateStatus",
    "GateOutput",
    "gate_pass",
    "gate_hold",
    "gate_deny",
]
