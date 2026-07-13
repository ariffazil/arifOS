"""
action_profile.py — Action Classification Profile (D1)

═══════════════════════════════════════════════════════════
FORGED: 2026-07-13 — Arif's D1 directive
PURPOSE: Compute immutable action_profile once, before any
         gate evaluates. All gates read from this profile;
         no gate silently sets facts another gate needs.
═══════════════════════════════════════════════════════════

The current serial chain is wrong because later gates generate
facts needed by earlier gates. Gate 3.5 asks "is this dangerous?"
but Gate 7 (sovereign authority check) never runs because 3.5
already blocked.

Fix: Classification phase produces the complete action_profile
BEFORE any gate enforces. Gates then read from this immutable
profile — they do NOT compute facts that other gates need.

DITEMPA BUKAN DIBERI — The profile is forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION CLASSIFICATION ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class MutationClass(StrEnum):
    """Class of mutation the action performs."""

    NONE = "NONE"  # read-only, observe
    APPEND_ONLY = "APPEND_ONLY"  # VAULT seal, log write
    MUTATE = "MUTATE"  # state change (reversible)
    DESTROY = "DESTROY"  # delete/remove
    CREATE = "CREATE"  # new resource
    OVERRIDE = "OVERRIDE"  # force override existing state
    UNKNOWN = "UNKNOWN"


class Reversibility(StrEnum):
    """How reversible is this action?"""

    REVERSIBLE = "REVERSIBLE"  # git revert, config rollback
    PARTIALLY_REVERSIBLE = "PARTIALLY_REVERSIBLE"  # data lost but system ok
    IRREVERSIBLE = "IRREVERSIBLE"  # VAULT seal, prod deploy, DROP TABLE
    UNKNOWN = "UNKNOWN"


class BlastRadius(StrEnum):
    """Scope of impact if this action goes wrong."""

    NONE = "NONE"  # no external impact
    LOCAL = "LOCAL"  # single file, single session
    TOOL = "TOOL"  # one MCP tool
    ORGAN = "ORGAN"  # one federation organ
    DATASET = "DATASET"  # multiple organs / data surface
    FEDERATION = "FEDERATION"  # all organs
    SOVEREIGN = "SOVEREIGN"  # constitutional floor, human identity
    UNKNOWN = "UNKNOWN"


class InfrastructureImpact(StrEnum):
    """Does this affect infrastructure (VPS, Docker, ports, Caddy)?"""

    NONE = "NONE"
    CONTAINER = "CONTAINER"  # docker restart, service restart
    PORT = "PORT"  # port mapping, proxy config
    NETWORK = "NETWORK"  # routing, DNS, firewall
    HARDWARE = "HARDWARE"  # VPS, disk, memory
    UNKNOWN = "UNKNOWN"


class GovernanceImpact(StrEnum):
    """Does this affect constitutional governance?"""

    NONE = "NONE"
    ROUTINE = "ROUTINE"  # session accounting, standard receipts
    CONSTITUTIONAL = "CONSTITUTIONAL"  # floor enforcement, seal chain
    SOVEREIGN = "SOVEREIGN"  # F13 decision, irreversible binding
    UNKNOWN = "UNKNOWN"


class ReceiptClass(StrEnum):
    """What kind of receipt does this action produce?"""

    NONE = "NONE"  # no receipt (OBSERVE)
    ROUTINE = "ROUTINE"  # standard session receipt (service-signed)
    SESSION_CLOSURE = "SESSION_CLOSURE"  # session end receipt
    SOVEREIGN_DECISION = "SOVEREIGN_DECISION"  # F13-ratified decision
    CONSTITUTIONAL = "CONSTITUTIONAL"  # floor violation/adherence record
    UNKNOWN = "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════════════════
# REQUIRED CAPABILITY — what capability grant is needed
# ═══════════════════════════════════════════════════════════════════════════════


class RequiredCapability(StrEnum):
    """Capability string that must be in actor's grant."""

    # Session
    SESSION_INIT = "session.init"
    SESSION_RESUME = "session.resume"
    SESSION_CLOSE = "session.close"
    SESSION_OBSERVE = "session.observe"

    # Observe
    OBSERVE_SEARCH = "observe.search"
    OBSERVE_FETCH = "observe.fetch"

    # Think / Reason
    THINK_REASON = "think.reason"
    THINK_PLAN = "think.plan"

    # Route
    ROUTE_INTENT = "route.intent"

    # Judge
    JUDGE_DELIBERATE = "judge.deliberate"
    JUDGE_ADJUDICATE = "judge.adjudicate"
    JUDGE_OVERRIDE = "judge.override"

    # Forge
    FORGE_READ = "forge.read"
    FORGE_WRITE = "forge.write"
    FORGE_EXECUTE = "forge.execute"
    FORGE_DEPLOY = "forge.deploy"

    # Vault
    VAULT_APPEND_ROUTINE = "vault.append.routine"
    VAULT_APPEND_SESSION_CLOSURE = "vault.append.session_closure"
    VAULT_APPEND_SOVEREIGN = "vault.append.sovereign"
    VAULT_READ = "vault.read"
    VAULT_VERIFY = "vault.verify"

    # Infrastructure
    INFRA_CONTAINER = "infra.container"
    INFRA_PORT = "infra.port"
    INFRA_NETWORK = "infra.network"
    INFRA_HARDWARE = "infra.hardware"

    # Constitutional
    CONSTITUTIONAL_FLOOR_CHECK = "constitutional.floor_check"
    CONSTITUTIONAL_AMEND = "constitutional.amend"

    UNKNOWN = "unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# ACTION PROFILE — immutable per-request classification
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ActionProfile:
    """
    Immutable classification of an action, computed once at the start
    of the gate pipeline. Every gate reads from this profile; no gate
    silently sets facts needed by another gate.

    Once computed, this profile is frozen for the lifetime of the request.
    """

    # ── Tool identity ──
    tool: str  # e.g. "arif_seal", "arif_forge", "arif_observe"
    verb: str  # e.g. "seal", "engineer", "search"

    # ── Core classification ──
    mutation_class: MutationClass
    reversibility: Reversibility
    blast_radius: BlastRadius

    # ── Impact classification ──
    infrastructure_impact: InfrastructureImpact
    governance_impact: GovernanceImpact

    # ── Receipt and capability ──
    receipt_class: ReceiptClass
    required_capability: RequiredCapability

    # ── Sovereign gating ──
    sovereign_required: bool  # True = F13 cryptographic key required
    requires_human_ack: bool  # True = human must acknowledge first

    # ── Classification provenance ──
    classified_by: str  # which classifier rule or mapping produced this
    profile_hash: str = ""  # SHA-256 of all above fields (immutable binding)

    def __post_init__(self) -> None:
        """Auto-compute profile_hash from canonical field order."""
        if not self.profile_hash:
            import hashlib
            import json

            canonical = {
                "tool": self.tool,
                "verb": self.verb,
                "mutation_class": self.mutation_class.value,
                "reversibility": self.reversibility.value,
                "blast_radius": self.blast_radius.value,
                "infrastructure_impact": self.infrastructure_impact.value,
                "governance_impact": self.governance_impact.value,
                "receipt_class": self.receipt_class.value,
                "required_capability": self.required_capability.value,
                "sovereign_required": self.sovereign_required,
                "requires_human_ack": self.requires_human_ack,
                "classified_by": self.classified_by,
            }
            h = hashlib.sha256(
                json.dumps(canonical, sort_keys=True).encode()
            ).hexdigest()
            object.__setattr__(self, "profile_hash", h[:16])


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL-CLASSIFICATION MAP — canonical mapping from tool+verb to ActionProfile
# ═══════════════════════════════════════════════════════════════════════════════
# This is the single source of truth for action classification.
# If a tool+verb is not in this map, classification fails with UNKNOWN.
# Add new tools here — never in ad-hoc gate logic.
# ═══════════════════════════════════════════════════════════════════════════════

TOOL_CLASSIFICATION_MAP: dict[str, dict[str, dict[str, Any]]] = {
    # ── arif_init ──
    "arif_init": {
        "init": {
            "mutation_class": "CREATE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "ROUTINE",
            "receipt_class": "NONE",
            "required_capability": "session.init",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "light": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "session.init",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "resume": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "ROUTINE",
            "receipt_class": "NONE",
            "required_capability": "session.resume",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
    },
    # ── arif_observe ──
    "arif_observe": {
        "search": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "observe.search",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "fetch": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "observe.fetch",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "vitals": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "observe.search",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
    },
    # ── arif_think ──
    "arif_think": {
        "reason": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "think.reason",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "plan": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "think.plan",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
    },
    # ── arif_judge ──
    "arif_judge": {
        "*": {
            "mutation_class": "APPEND_ONLY",
            "reversibility": "IRREVERSIBLE" if False else "PARTIALLY_REVERSIBLE",
            "blast_radius": "TOOL",
            "infrastructure_impact": "NONE",
            "governance_impact": "CONSTITUTIONAL",
            "receipt_class": "CONSTITUTIONAL",
            "required_capability": "judge.deliberate",
            "sovereign_required": False,
            "requires_human_ack": True,
        },
    },
    # ── arif_seal ──
    "arif_seal": {
        "seal": {
            "mutation_class": "APPEND_ONLY",
            "reversibility": "IRREVERSIBLE",
            "blast_radius": "DATASET",
            "infrastructure_impact": "NONE",
            "governance_impact": "CONSTITUTIONAL",
            "receipt_class": "SESSION_CLOSURE",  # default; classification phase can upgrade to SOVEREIGN_DECISION
            "required_capability": "vault.append.session_closure",
            "sovereign_required": False,  # classification phase sets True only with F13 key
            "requires_human_ack": True,
        },
        "verify": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "vault.verify",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
    },
    # ── arif_forge ──
    "arif_forge": {
        "query": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "forge.read",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "engineer": {
            "mutation_class": "MUTATE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "ROUTINE",
            "required_capability": "forge.write",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "write": {
            "mutation_class": "MUTATE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "ROUTINE",
            "required_capability": "forge.write",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "generate": {
            "mutation_class": "CREATE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "LOCAL",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "ROUTINE",
            "required_capability": "forge.write",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
        "commit": {
            "mutation_class": "APPEND_ONLY",
            "reversibility": "REVERSIBLE",
            "blast_radius": "TOOL",
            "infrastructure_impact": "NONE",
            "governance_impact": "ROUTINE",
            "receipt_class": "ROUTINE",
            "required_capability": "forge.write",
            "sovereign_required": False,
            "requires_human_ack": True,
        },
    },
    # ── arif_route ──
    "arif_route": {
        "*": {
            "mutation_class": "NONE",
            "reversibility": "REVERSIBLE",
            "blast_radius": "NONE",
            "infrastructure_impact": "NONE",
            "governance_impact": "NONE",
            "receipt_class": "NONE",
            "required_capability": "route.intent",
            "sovereign_required": False,
            "requires_human_ack": False,
        },
    },
    # ── Infrastructure tools ──
    "infra": {
        "*": {
            "mutation_class": "MUTATE",
            "reversibility": "PARTIALLY_REVERSIBLE",
            "blast_radius": "FEDERATION",
            "infrastructure_impact": "HARDWARE",
            "governance_impact": "NONE",
            "receipt_class": "ROUTINE",
            "required_capability": "infra.hardware",
            "sovereign_required": True,
            "requires_human_ack": True,
        },
    },
}

# ── Wildcard catch-all for tools not in the map ──
UNKNOWN_CLASSIFICATION: dict[str, Any] = {
    "mutation_class": "UNKNOWN",
    "reversibility": "UNKNOWN",
    "blast_radius": "UNKNOWN",
    "infrastructure_impact": "UNKNOWN",
    "governance_impact": "UNKNOWN",
    "receipt_class": "UNKNOWN",
    "required_capability": "unknown",
    "sovereign_required": False,
    "requires_human_ack": False,
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════


def classify_action(
    tool: str,
    verb: str,
    *,
    upgrade_receipt_class: ReceiptClass | None = None,
    force_sovereign: bool = False,
) -> ActionProfile:
    """
    Classify an action into its immutable ActionProfile.

    This is the ONLY function that computes action profiles.
    No gate, no enforcer, no tool handler may modify the profile
    after this function returns.

    Args:
        tool: MCP tool name (e.g. "arif_seal")
        verb: Mode or sub-verb (e.g. "seal", "engineer")
        upgrade_receipt_class: Optional override to upgrade the receipt class
            (e.g. seal with sovereign key → SOVEREIGN_DECISION)
        force_sovereign: Set True if F13 cryptographic key is present

    Returns:
        Immutable ActionProfile
    """
    import hashlib
    import json

    # Look up tool
    tool_map = TOOL_CLASSIFICATION_MAP.get(tool, {})
    if not tool_map:
        # Unknown tool — use UNKNOWN classification
        return ActionProfile(
            tool=tool,
            verb=verb,
            mutation_class=MutationClass.UNKNOWN,
            reversibility=Reversibility.UNKNOWN,
            blast_radius=BlastRadius.UNKNOWN,
            infrastructure_impact=InfrastructureImpact.UNKNOWN,
            governance_impact=GovernanceImpact.UNKNOWN,
            receipt_class=ReceiptClass.UNKNOWN,
            required_capability=RequiredCapability.UNKNOWN,
            sovereign_required=False,
            requires_human_ack=False,
            classified_by="fallback_unknown",
        )

    # Look up verb — try exact match first, then wildcard
    fields = tool_map.get(verb) or tool_map.get("*")
    if not fields:
        # Unknown verb — use UNKNOWN
        return ActionProfile(
            tool=tool,
            verb=verb,
            mutation_class=MutationClass.UNKNOWN,
            reversibility=Reversibility.UNKNOWN,
            blast_radius=BlastRadius.UNKNOWN,
            infrastructure_impact=InfrastructureImpact.UNKNOWN,
            governance_impact=GovernanceImpact.UNKNOWN,
            receipt_class=ReceiptClass.UNKNOWN,
            required_capability=RequiredCapability.UNKNOWN,
            sovereign_required=False,
            requires_human_ack=False,
            classified_by="fallback_unknown_verb",
        )

    # Build profile from classification map
    receipt_class = upgrade_receipt_class or ReceiptClass(fields["receipt_class"])

    profile = ActionProfile(
        tool=tool,
        verb=verb,
        mutation_class=MutationClass(fields["mutation_class"]),
        reversibility=Reversibility(fields["reversibility"]),
        blast_radius=BlastRadius(fields["blast_radius"]),
        infrastructure_impact=InfrastructureImpact(fields["infrastructure_impact"]),
        governance_impact=GovernanceImpact(fields["governance_impact"]),
        receipt_class=receipt_class,
        required_capability=RequiredCapability(fields["required_capability"]),
        sovereign_required=force_sovereign or fields["sovereign_required"],
        requires_human_ack=fields["requires_human_ack"],
        classified_by=f"canonical_map:{tool}/{verb}",
    )
    return profile


# ═══════════════════════════════════════════════════════════════════════════════
# UPGRADE RULES — classification-phase upgrades based on context
# ═══════════════════════════════════════════════════════════════════════════════
# These are applied AFTER classify_action() when additional context is available
# (e.g. identity resolution found an F13 key, or the payload contains a sovereign
# directive). They return an upgraded ActionProfile — the original is never mutated.
# ═══════════════════════════════════════════════════════════════════════════════


def upgrade_to_sovereign(profile: ActionProfile) -> ActionProfile:
    """
    Upgrade a profile to sovereign decision class.
    Called when identity resolution confirms F13 key binding.

    This is the only allowed mutation path for an ActionProfile —
    and it produces a new frozen profile, never mutates the original.
    """
    return ActionProfile(
        tool=profile.tool,
        verb=profile.verb,
        mutation_class=profile.mutation_class,
        reversibility=profile.reversibility,
        blast_radius=profile.blast_radius,
        infrastructure_impact=profile.infrastructure_impact,
        governance_impact=GovernanceImpact.SOVEREIGN,
        receipt_class=ReceiptClass.SOVEREIGN_DECISION,
        required_capability=RequiredCapability.VAULT_APPEND_SOVEREIGN,
        sovereign_required=True,
        requires_human_ack=profile.requires_human_ack,
        classified_by=f"{profile.classified_by}|upgrade_sovereign",
    )


def upgrade_to_session_closure(profile: ActionProfile) -> ActionProfile:
    """
    Upgrade a profile to session-closure receipt class.
    Called when session is ending and this is the final seal.
    """
    return ActionProfile(
        tool=profile.tool,
        verb=profile.verb,
        mutation_class=profile.mutation_class,
        reversibility=profile.reversibility,
        blast_radius=profile.blast_radius,
        infrastructure_impact=profile.infrastructure_impact,
        governance_impact=profile.governance_impact,
        receipt_class=ReceiptClass.SESSION_CLOSURE,
        required_capability=RequiredCapability.VAULT_APPEND_SESSION_CLOSURE,
        sovereign_required=profile.sovereign_required,
        requires_human_ack=profile.requires_human_ack,
        classified_by=f"{profile.classified_by}|upgrade_session_closure",
    )
