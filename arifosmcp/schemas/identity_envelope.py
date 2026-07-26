"""
arifosmcp/schemas/identity_envelope.py — IDENTITY ENVELOPE + AGENT LIFECYCLE + INSTITUTIONAL STATE (P5)
══════════════════════════════════════════════════════════════════════════════════

Three-layer identity per Arif's SEAL architecture:
  1. AgentCard        = declared static identity (agent-card.json)
  2. IdentityEnvelope = runtime-bound identity (this file)
  3. AuthorityState   = live permission (AuthorityContext in authority_context.py)

Plus: AgentLifecycle (UNBORN→SEALED→DEAD state machine)
Plus: InstitutionalState (what AAA displays, arifOS judges, A-FORGE consumes)

North-star: AAA identifies. arifOS judges. A-FORGE executes. VAULT999 records.
            ARIF vetoes. No agent self-authorizes.

Forged: 2026-07-26 under Arif's P5 SEAL directive.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from arifosmcp.schemas.authority_context import AuthorityContext

# ═══════════════════════════════════════════════════════════════════════════════
# AGENT LIFECYCLE STATE MACHINE
# ═══════════════════════════════════════════════════════════════════════════════


class AgentLifecycle(StrEnum):
    """Institutional state machine for every agent. Gate rules enforced."""

    UNBORN = "UNBORN"  # Does not exist yet
    CLAIMED = "CLAIMED"  # Identity claimed, not yet registered
    REGISTERED = "REGISTERED"  # Registered, not yet attested
    MANIFESTED = "MANIFESTED"  # Capabilities declared
    ATTESTED = "ATTESTED"  # Identity cryptographically attested
    CONTEXT_BOUND = "CONTEXT_BOUND"  # Bound to institutional context
    LEASED = "LEASED"  # Capability lease granted
    ACTIVE = "ACTIVE"  # Fully operational
    DEGRADED = "DEGRADED"  # Operating with reduced capabilities
    SUSPENDED = "SUSPENDED"  # Temporarily halted
    COMPLETED = "COMPLETED"  # Task complete, terminating
    REVOKED = "REVOKED"  # Authority revoked — no resurrection
    SEALED = "SEALED"  # Immutable history in VAULT999
    DEAD = "DEAD"  # Permanently terminated


# Gate rules: which states allow which actions
LIFECYCLE_GATES: dict[AgentLifecycle, dict[str, bool]] = {
    AgentLifecycle.UNBORN: {"register": False, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.CLAIMED: {"register": True, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.REGISTERED: {
        "register": False,
        "observe": False,
        "mutate": False,
        "seal": False,
    },
    AgentLifecycle.MANIFESTED: {
        "register": False,
        "observe": False,
        "mutate": False,
        "seal": False,
    },
    AgentLifecycle.ATTESTED: {"register": False, "observe": True, "mutate": False, "seal": False},
    AgentLifecycle.CONTEXT_BOUND: {
        "register": False,
        "observe": True,
        "mutate": False,
        "seal": False,
    },
    AgentLifecycle.LEASED: {"register": False, "observe": True, "mutate": True, "seal": False},
    AgentLifecycle.ACTIVE: {"register": False, "observe": True, "mutate": True, "seal": False},
    AgentLifecycle.DEGRADED: {"register": False, "observe": True, "mutate": False, "seal": False},
    AgentLifecycle.SUSPENDED: {"register": False, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.COMPLETED: {"register": False, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.REVOKED: {"register": False, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.SEALED: {"register": False, "observe": False, "mutate": False, "seal": False},
    AgentLifecycle.DEAD: {"register": False, "observe": False, "mutate": False, "seal": False},
}

LEGAL_TRANSITIONS: dict[AgentLifecycle, list[AgentLifecycle]] = {
    AgentLifecycle.UNBORN: [AgentLifecycle.CLAIMED],
    AgentLifecycle.CLAIMED: [AgentLifecycle.REGISTERED],
    AgentLifecycle.REGISTERED: [AgentLifecycle.MANIFESTED, AgentLifecycle.REVOKED],
    AgentLifecycle.MANIFESTED: [AgentLifecycle.ATTESTED, AgentLifecycle.REVOKED],
    AgentLifecycle.ATTESTED: [AgentLifecycle.CONTEXT_BOUND, AgentLifecycle.REVOKED],
    AgentLifecycle.CONTEXT_BOUND: [AgentLifecycle.LEASED, AgentLifecycle.REVOKED],
    AgentLifecycle.LEASED: [
        AgentLifecycle.ACTIVE,
        AgentLifecycle.DEGRADED,
        AgentLifecycle.SUSPENDED,
        AgentLifecycle.REVOKED,
    ],
    AgentLifecycle.ACTIVE: [
        AgentLifecycle.DEGRADED,
        AgentLifecycle.SUSPENDED,
        AgentLifecycle.COMPLETED,
        AgentLifecycle.REVOKED,
    ],
    AgentLifecycle.DEGRADED: [
        AgentLifecycle.ACTIVE,
        AgentLifecycle.SUSPENDED,
        AgentLifecycle.COMPLETED,
        AgentLifecycle.REVOKED,
    ],
    AgentLifecycle.SUSPENDED: [
        AgentLifecycle.ACTIVE,
        AgentLifecycle.DEGRADED,
        AgentLifecycle.COMPLETED,
        AgentLifecycle.REVOKED,
    ],
    AgentLifecycle.COMPLETED: [AgentLifecycle.SEALED, AgentLifecycle.REVOKED],
    AgentLifecycle.REVOKED: [AgentLifecycle.SEALED, AgentLifecycle.DEAD],
    AgentLifecycle.SEALED: [AgentLifecycle.DEAD],
    AgentLifecycle.DEAD: [],  # terminal
}


def can_transition(from_state: AgentLifecycle, to_state: AgentLifecycle) -> bool:
    return to_state in LEGAL_TRANSITIONS.get(from_state, [])


def may_register(state: AgentLifecycle) -> bool:
    return LIFECYCLE_GATES.get(state, {}).get("register", False)


def may_observe(state: AgentLifecycle) -> bool:
    return LIFECYCLE_GATES.get(state, {}).get("observe", False)


def may_mutate(state: AgentLifecycle) -> bool:
    return LIFECYCLE_GATES.get(state, {}).get("mutate", False)


def may_seal(state: AgentLifecycle) -> bool:
    return LIFECYCLE_GATES.get(state, {}).get("seal", False)


# ═══════════════════════════════════════════════════════════════════════════════
# IDENTITY ENVELOPE (LAYER 2 — runtime-bound identity)
# ═══════════════════════════════════════════════════════════════════════════════

PrincipalType = Literal[
    "human",
    "architect",
    "agent",
    "llm",
    "model",
    "institution",
    "earth",
    "void",
    "liar",
    "unknown",
]

DelegationMode = Literal["direct", "scoped", "chain", "none"]


@dataclass
class IdentityEnvelope:
    """Runtime-bound identity — carried by every task, tool call, A2A message.

    AgentCard declares. IdentityEnvelope binds. AuthorityState permits.
    """

    actor_id: str
    agent_id: str
    sovereign_id: str = "ARIF_FAZIL"
    caller_actor_id: str | None = None
    executor_actor_id: str | None = None
    session_id: str = ""
    session_token_hash: str = ""
    trace_id: str = ""
    delegation_mode: DelegationMode = "none"
    principal_agent_type: PrincipalType = "unknown"
    host_organ: str = "AAA"
    lifecycle: AgentLifecycle = AgentLifecycle.REGISTERED
    proof_method: str = "session"
    verified: bool = False
    bound_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "agent_id": self.agent_id,
            "sovereign_id": self.sovereign_id,
            "caller_actor_id": self.caller_actor_id,
            "executor_actor_id": self.executor_actor_id,
            "session_id": self.session_id,
            "session_token_hash": self.session_token_hash,
            "trace_id": self.trace_id,
            "delegation_mode": self.delegation_mode,
            "principal_agent_type": self.principal_agent_type,
            "host_organ": self.host_organ,
            "lifecycle": self.lifecycle.value,
            "proof_method": self.proof_method,
            "verified": self.verified,
            "bound_at": self.bound_at,
        }

    def may_act(self) -> bool:
        """Can this identity take actions right now?"""
        return (
            self.verified
            and may_mutate(self.lifecycle)
            and self.lifecycle in (AgentLifecycle.LEASED, AgentLifecycle.ACTIVE)
        )

    def may_observe(self) -> bool:
        """Can this identity observe/reason?"""
        return self.verified and may_observe(self.lifecycle) if self.verified else False

    def can_advance_to(self, next_state: AgentLifecycle) -> bool:
        return can_transition(self.lifecycle, next_state)


# ═══════════════════════════════════════════════════════════════════════════════
# INSTITUTIONAL STATE (what AAA displays, arifOS judges, A-FORGE consumes)
# ═══════════════════════════════════════════════════════════════════════════════

OrganHealth = Literal["green", "yellow", "red", "unknown"]


@dataclass
class InstitutionalState:
    """Transient runtime configuration — health-bound, lease-controlled, lock-aware.

    AAA displays. arifOS judges. A-FORGE consumes. VAULT999 records receipts.
    """

    state_id: str = ""
    session_id: str = ""

    # Actor
    identity: IdentityEnvelope | None = None
    authority: AuthorityContext | None = None

    # Organ health
    organ_health: dict[str, OrganHealth] = field(default_factory=dict)

    # Runtime state
    active_leases: list[str] = field(default_factory=list)
    active_locks: list[str] = field(default_factory=list)
    pending_holds: list[str] = field(default_factory=list)
    current_tasks: list[dict[str, Any]] = field(default_factory=list)

    # Governance
    verdicts: list[dict[str, Any]] = field(default_factory=list)
    receipts: list[dict[str, Any]] = field(default_factory=list)
    vault_refs: list[str] = field(default_factory=list)

    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "state_id": self.state_id,
            "session_id": self.session_id,
            "identity": self.identity.to_dict() if self.identity else None,
            "authority": self.authority.to_dict() if self.authority else None,
            "organ_health": self.organ_health,
            "active_leases": self.active_leases,
            "active_locks": self.active_locks,
            "pending_holds": self.pending_holds,
            "current_tasks": self.current_tasks,
            "verdicts": self.verdicts,
            "receipts": self.receipts,
            "vault_refs": self.vault_refs,
            "updated_at": self.updated_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# PRINCIPAL AGENT TYPE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

PRINCIPAL_CAPABILITIES: dict[PrincipalType, dict[str, Any]] = {
    "human": {
        "may_judge": True,
        "may_seal": True,
        "may_veto": True,
        "may_execute_irreversible": True,
        "description": "Sovereign human — F13 authority, absolute veto",
    },
    "architect": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "System architect — designs, configures, never executes",
    },
    "agent": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Autonomous agent — scoped execution, bounded authority",
    },
    "llm": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "LLM model — reasoning only, no authority of its own",
    },
    "model": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Computational model — stateless inference, no agency",
    },
    "institution": {
        "may_judge": True,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Institutional entity — organizational scope, delegated authority",
    },
    "earth": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Earth/physical evidence — observational truth only",
    },
    "void": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Null/void principal — no authority, placeholder only",
    },
    "liar": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Deceptive principal — explicitly untrusted, all claims void",
    },
    "unknown": {
        "may_judge": False,
        "may_seal": False,
        "may_veto": False,
        "may_execute_irreversible": False,
        "description": "Unknown principal — fail-closed, assumed untrusted",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# NORTH-STAR INVARIANT CHECKER
# ═══════════════════════════════════════════════════════════════════════════════


def north_star_check(identity: IdentityEnvelope, action: str) -> dict[str, Any]:
    """The constitutional compression check:
    AAA identifies. arifOS judges. A-FORGE executes. VAULT999 records.
    ARIF vetoes. No agent self-authorizes.
    """
    principal = PRINCIPAL_CAPABILITIES.get(
        identity.principal_agent_type, PRINCIPAL_CAPABILITIES["unknown"]
    )

    if action == "self_authorize":
        return {"allowed": False, "reason": "No agent self-authorizes — north-star invariant"}
    if action in ("seal", "self_seal") and not principal.get("may_seal", False):
        return {"allowed": False, "reason": f"{identity.principal_agent_type} may not seal"}
    if action in ("irreversible",) and not principal.get("may_execute_irreversible", False):
        return {
            "allowed": False,
            "reason": f"{identity.principal_agent_type} may not execute irreversible actions",
        }
    if action == "veto" and not principal.get("may_veto", False):
        return {"allowed": False, "reason": "Only human (ARIF) may veto"}

    return {
        "allowed": True,
        "reason": f"Action '{action}' permitted for {identity.principal_agent_type}",
    }


# ─── P5 self-test ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test lifecycle state machine
    assert can_transition(AgentLifecycle.UNBORN, AgentLifecycle.CLAIMED)
    assert not can_transition(AgentLifecycle.UNBORN, AgentLifecycle.ACTIVE)
    assert can_transition(AgentLifecycle.ACTIVE, AgentLifecycle.COMPLETED)
    assert can_transition(AgentLifecycle.COMPLETED, AgentLifecycle.SEALED)
    assert can_transition(AgentLifecycle.SEALED, AgentLifecycle.DEAD)
    assert not can_transition(AgentLifecycle.DEAD, AgentLifecycle.ACTIVE)
    assert may_observe(AgentLifecycle.ACTIVE) and not may_observe(AgentLifecycle.UNBORN)
    assert may_mutate(AgentLifecycle.ACTIVE) and not may_mutate(AgentLifecycle.ATTESTED)
    print("✅ Lifecycle state machine: ALL transitions valid")

    # Test IdentityEnvelope
    env = IdentityEnvelope(
        actor_id="opencode",
        agent_id="opencode",
        session_id="s1",
        principal_agent_type="llm",
        lifecycle=AgentLifecycle.ACTIVE,
        verified=True,
    )
    # LLM: cannot seal, cannot veto, cannot execute irreversible
    for action in ["seal", "veto", "irreversible", "self_authorize"]:
        r = north_star_check(env, action)
        assert not r["allowed"], f"LLM should not {action}: {r['reason']}"
        print(f"  ✅ LLM {action} → BLOCKED: {r['reason']}")

    human_env = IdentityEnvelope(
        actor_id="arif",
        agent_id="arif",
        principal_agent_type="human",
        lifecycle=AgentLifecycle.ACTIVE,
        verified=True,
    )
    for action in ["seal", "veto", "irreversible"]:
        r = north_star_check(human_env, action)
        assert r["allowed"], f"Human should {action}: {r['reason']}"
        print(f"  ✅ Human {action} → ALLOWED: {r['reason']}")

    # Test InstitutionalState
    state = InstitutionalState(
        state_id="state-1",
        session_id="s1",
        identity=env,
        organ_health={"arifOS": "green", "A-FORGE": "green", "GEOX": "unknown"},
    )
    d = state.to_dict()
    assert d["organ_health"]["arifOS"] == "green"
    print(f"  ✅ InstitutionalState: {len(d['organ_health'])} organs tracked")

    print(f"\n✅ P5b+P5c: Lifecycle + IdentityEnvelope + InstitutionalState ALL PASS")
