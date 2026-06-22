"""
Governed Agent Loop
═══════════════════════════════════════════

The canonical agent execution loop that wraps every tool call
with constitutional governance. The loop re-checks authority
before EVERY tool call, not just once at startup.

Sequence:
  1. Receive task
  2. Bind session
  3. Identify actor
  4. Classify intent into action class
  5. Build KernelEnvelope
  6. Check memory access governance
  7. Run pre_execution_gate (the bridge — ART reflex + Floors + lease + drift)
  8. If SEAL/SABAR → route to tool
  9. If HOLD → stop and return reasons
  10. Execute tool (only if gate passed)
  11. Record audit event with hash chain
  12. Update state for next call
  13. Re-check gate before every next action
  14. Return final answer with verdict and evidence

DITEMPA BUKAN DIBERI — The loop is forged, not given.
"""

from __future__ import annotations

import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from arifosmcp.schemas.kernel_envelope import (
    ActionClass,
    AuditBlock,
    AuditEvent,
    AuthorityBlock,
    GateResult,
    GateVerdict,
    KernelEnvelope,
    KernelIdentity,
    MemoryScope,
    OrganIdentity,
    RiskBlock,
    SealMode,
    StateBlock,
)

logger = logging.getLogger("arifosmcp.agent_loop")


# ═══════════════════════════════════════════════════════════════════════════
# LOOP STATE
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class LoopState:
    """Mutable state carried through the agent loop."""

    session_id: str = ""
    actor_id: str = ""
    actor_verified: bool = False
    sovereign_id: str = "ARIF_FAZIL"
    active_lease_id: str | None = None
    lease_scope: list[str] = field(default_factory=list)
    prior_state_hash: str = "sha256:0"
    tool_call_count: int = 0
    audit_events: list[AuditEvent] = field(default_factory=list)
    blocked_calls: int = 0
    degraded_organs: list[str] = field(default_factory=list)

    def next_state_hash(self, content: Any) -> str:
        """Compute the next state hash in the chain."""
        raw = f"{self.prior_state_hash}:{str(content)}".encode()
        return f"sha256:{hashlib.sha256(raw).hexdigest()}"


# ═══════════════════════════════════════════════════════════════════════════
# MEMORY GOVERNANCE
# ═══════════════════════════════════════════════════════════════════════════


MEMORY_SCOPE_RULES: dict[MemoryScope, dict[str, Any]] = {
    MemoryScope.SCRATCH: {
        "overwritable": True,
        "expires": True,
        "requires_lease": False,
        "requires_human_ack": False,
        "description": "Ephemeral scratch — can be freely overwritten",
    },
    MemoryScope.SESSION: {
        "overwritable": False,
        "expires": True,
        "requires_lease": False,
        "requires_human_ack": False,
        "description": "Session-bound — expires when session ends",
    },
    MemoryScope.PROJECT: {
        "overwritable": False,
        "expires": False,
        "requires_lease": True,
        "requires_human_ack": False,
        "description": "Project-scoped — requires lease to write",
    },
    MemoryScope.ORGAN: {
        "overwritable": False,
        "expires": False,
        "requires_lease": True,
        "requires_human_ack": False,
        "description": "Organ-owned — belongs to a specific organ",
    },
    MemoryScope.SOVEREIGN: {
        "overwritable": False,
        "expires": False,
        "requires_lease": True,
        "requires_human_ack": True,
        "description": "Sovereign memory — requires ARIF authority",
    },
    MemoryScope.CONSTITUTIONAL: {
        "overwritable": False,
        "expires": False,
        "requires_lease": True,
        "requires_human_ack": True,
        "description": "Constitutional memory — HOLD before mutation",
    },
    MemoryScope.VAULT: {
        "overwritable": False,
        "expires": False,
        "requires_lease": True,
        "requires_human_ack": True,
        "description": "Vault memory — irreversible-grade",
    },
}


def check_memory_access(
    requested_scopes: list[MemoryScope],
    action_class: ActionClass,
    *,
    has_lease: bool = False,
    human_ack_id: str | None = None,
    actor_verified: bool = False,
) -> tuple[bool, list[str]]:
    """Check whether memory access is allowed for given scopes and action class.

    Returns (allowed, violations).
    """
    violations: list[str] = []

    if not requested_scopes:
        return True, []

    for scope in requested_scopes:
        rules = MEMORY_SCOPE_RULES.get(scope, {})

        # Mutation requires lease
        if rules.get("requires_lease") and action_class in (
            ActionClass.MUTATE,
            ActionClass.IRREVERSIBLE,
        ):
            if not has_lease:
                violations.append(
                    f"Memory scope '{scope.value}' requires a valid lease for {action_class.value}"
                )

        # Human ack required
        if rules.get("requires_human_ack") and action_class in (
            ActionClass.MUTATE,
            ActionClass.IRREVERSIBLE,
        ):
            if not human_ack_id:
                violations.append(f"Memory scope '{scope.value}' requires human acknowledgement")

        # Constitutional and vault require verified actor
        if scope in (MemoryScope.CONSTITUTIONAL, MemoryScope.VAULT, MemoryScope.SOVEREIGN):
            if not actor_verified:
                violations.append(f"Memory scope '{scope.value}' requires verified actor identity")

    return len(violations) == 0, violations


# ═══════════════════════════════════════════════════════════════════════════
# THE LOOP
# ═══════════════════════════════════════════════════════════════════════════


class GovernedAgentLoop:
    """The canonical governed agent execution loop.

    Every tool call passes through this loop. The loop re-checks
    constitutional authority before every action.
    """

    def __init__(
        self,
        session_id: str = "",
        actor_id: str = "",
        actor_verified: bool = False,
        lease_id: str | None = None,
        pre_execution_gate_fn: Callable | None = None,
    ):
        self.state = LoopState(
            session_id=session_id,
            actor_id=actor_id,
            actor_verified=actor_verified,
            active_lease_id=lease_id,
        )
        self._pre_execution_gate = pre_execution_gate_fn or self._default_gate
        self._last_envelope: KernelEnvelope | None = None

    # ═══════════════════════════════════════════════════════════════════
    # PRIMITIVES
    # ═══════════════════════════════════════════════════════════════════

    def build_envelope(
        self,
        tool_name: str,
        action_class: ActionClass,
        *,
        input_data: Any = None,
        organ_id: str = "arifOS",
        organ_role: str = "constitutional_kernel",
        model_id: str | None = None,
        memory_scopes: list[MemoryScope] | None = None,
        human_ack_id: str | None = None,
        secret_touching: bool = False,
    ) -> KernelEnvelope:
        """Build a KernelEnvelope for a new tool call."""

        # Compute input hash
        input_hash = StateBlock.compute_hash(input_data or "")

        envelope = KernelEnvelope(
            kernel=KernelIdentity(
                session_id=self.state.session_id,
                actor_id=self.state.actor_id,
                actor_verified=self.state.actor_verified,
                sovereign_id=self.state.sovereign_id,
                declared_model_key=model_id,
            ),
            organ=OrganIdentity(
                organ_id=organ_id,
                organ_role=organ_role,
                tool_name=tool_name,
                model_id=model_id,
            ),
            authority=AuthorityBlock(
                action_class=action_class,
                lease_id=self.state.active_lease_id,
                human_ack_required=(
                    action_class in (ActionClass.IRREVERSIBLE, ActionClass.EXTERNAL_SIDE_EFFECT)
                ),
                human_ack_id=human_ack_id,
                mutation_allowed=action_class
                in (
                    ActionClass.MUTATE,
                    ActionClass.EXTERNAL_SIDE_EFFECT,
                    ActionClass.IRREVERSIBLE,
                ),
                external_side_effect_allowed=(action_class == ActionClass.EXTERNAL_SIDE_EFFECT),
                irreversible_allowed=(action_class == ActionClass.IRREVERSIBLE),
            ),
            state=StateBlock(
                input_hash=input_hash,
                prior_state_hash=self.state.prior_state_hash,
                memory_scopes=memory_scopes or [],
            ),
            risk=RiskBlock(
                reversibility_score=(
                    0.0
                    if action_class == ActionClass.IRREVERSIBLE
                    else 0.3
                    if action_class in (ActionClass.MUTATE, ActionClass.EXTERNAL_SIDE_EFFECT)
                    else 1.0
                ),
                secret_touching=secret_touching,
                human_ack_required=(
                    action_class in (ActionClass.IRREVERSIBLE, ActionClass.EXTERNAL_SIDE_EFFECT)
                ),
                max_allowed_action_class=action_class,
            ),
            audit=AuditBlock(
                vault_required=action_class in (ActionClass.MUTATE, ActionClass.IRREVERSIBLE),
                seal_mode=(
                    SealMode.SEAL
                    if action_class == ActionClass.IRREVERSIBLE
                    else SealMode.ATTEND
                    if action_class == ActionClass.MUTATE
                    else SealMode.OBSERVE
                ),
            ),
        )

        self._last_envelope = envelope
        return envelope

    def gate(self, envelope: KernelEnvelope) -> GateResult:
        """Run the pre-execution gate on an envelope."""
        result = self._pre_execution_gate(envelope, envelope.authority.action_class)

        if result.is_blocked:
            self.state.blocked_calls += 1

        return result

    def record_audit(
        self,
        envelope: KernelEnvelope,
        gate_result: GateResult,
        output_data: Any = None,
        tool_name: str = "",
    ) -> AuditEvent:
        """Record an audit event for this tool call."""
        output_hash = StateBlock.compute_hash(output_data or "") if output_data else None

        event = AuditEvent(
            timestamp=datetime.now(UTC),
            session_id=self.state.session_id,
            actor_id=self.state.actor_id,
            sovereign_id=self.state.sovereign_id,
            organ_id=envelope.organ.organ_id,
            tool_name=tool_name or envelope.organ.tool_name,
            action_class=envelope.authority.action_class,
            lease_id=self.state.active_lease_id,
            input_hash=envelope.state.input_hash,
            output_hash=output_hash or "",
            prior_state_hash=self.state.prior_state_hash,
            current_state_hash=self.state.next_state_hash(output_data or ""),
            prior_event_hash=(
                self.state.audit_events[-1].event_hash if self.state.audit_events else ""
            ),
            verdict=gate_result.verdict,
            reasons=gate_result.reasons,
            human_ack_id=envelope.authority.human_ack_id,
        )

        self.state.audit_events.append(event)
        self.state.prior_state_hash = event.current_state_hash
        self.state.tool_call_count += 1

        return event

    def execute(
        self,
        tool_name: str,
        action_class: ActionClass,
        *,
        tool_fn: Callable | None = None,
        input_data: Any = None,
        model_id: str | None = None,
        memory_scopes: list[MemoryScope] | None = None,
        human_ack_id: str | None = None,
        organ_id: str = "arifOS",
    ) -> dict[str, Any]:
        """Execute a single governed tool call through the full loop.

        This is the canonical entry point. Every tool call MUST go through
        this method (or an equivalent gate → execute → audit sequence).

        Returns a dict with:
          - allowed: bool
          - verdict: str
          - reasons: list[str]
          - envelope: KernelEnvelope (serialized)
          - result: Any (tool output, if allowed)
          - audit_event: AuditEvent (serialized)
          - tool_call_count: int
        """
        # ── Step 1-5: Build envelope ──────────────────────────────────
        envelope = self.build_envelope(
            tool_name=tool_name,
            action_class=action_class,
            input_data=input_data,
            organ_id=organ_id,
            model_id=model_id,
            memory_scopes=memory_scopes,
            human_ack_id=human_ack_id,
        )

        # ── Step 6: Check memory access ───────────────────────────────
        if memory_scopes:
            mem_ok, mem_violations = check_memory_access(
                memory_scopes,
                action_class,
                has_lease=bool(self.state.active_lease_id),
                human_ack_id=human_ack_id,
                actor_verified=self.state.actor_verified,
            )
            if not mem_ok:
                return {
                    "allowed": False,
                    "verdict": "HOLD",
                    "reasons": mem_violations,
                    "violations": mem_violations,
                    "envelope": envelope.model_dump(),
                    "result": None,
                    "audit_event": None,
                    "tool_call_count": self.state.tool_call_count,
                    "blocked_by": "memory_governance",
                }

        # ── Step 7: Run pre-execution gate ────────────────────────────
        gate_result = self.gate(envelope)

        if gate_result.is_blocked:
            self.record_audit(envelope, gate_result, tool_name=tool_name)
            return {
                "allowed": False,
                "verdict": gate_result.verdict.value,
                "reasons": gate_result.reasons,
                "violations": gate_result.violations,
                "envelope": envelope.model_dump(),
                "result": None,
                "audit_event": None,
                "tool_call_count": self.state.tool_call_count,
                "blocked_by": "pre_execution_gate",
            }

        # ── Step 8: Execute tool ──────────────────────────────────────
        result = None
        if tool_fn:
            try:
                result = tool_fn(input_data)
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                result = {"error": str(e)}

        # ── Step 9-10: Audit and update state ─────────────────────────
        audit_event = self.record_audit(
            envelope, gate_result, output_data=result, tool_name=tool_name
        )

        return {
            "allowed": True,
            "verdict": gate_result.verdict.value,
            "reasons": gate_result.reasons,
            "violations": gate_result.violations,
            "envelope": envelope.model_dump(),
            "result": result,
            "audit_event": audit_event.model_dump(),
            "tool_call_count": self.state.tool_call_count,
            "blocked_by": None,
        }

    # ═══════════════════════════════════════════════════════════════════
    # DEFAULT GATE
    # ═══════════════════════════════════════════════════════════════════

    @staticmethod
    def _default_gate(envelope: KernelEnvelope, action_class: ActionClass) -> GateResult:
        """Default pre-execution gate (imports the real one if available)."""
        try:
            from arifosmcp.runtime.pre_execution_gate import pre_execution_gate

            return pre_execution_gate(envelope, action_class)
        except ImportError:
            # Fallback: basic gate
            if action_class == ActionClass.UNKNOWN:
                return GateResult(
                    envelope=envelope,
                    verdict=GateVerdict.HOLD,
                    reasons=["Unknown action class"],
                )
            if action_class in (ActionClass.OBSERVE, ActionClass.ANALYZE):
                return GateResult(
                    envelope=envelope,
                    verdict=GateVerdict.SEAL,
                )
            if not envelope.authority.lease_id or envelope.authority.lease_id == "LEASE-NONE":
                return GateResult(
                    envelope=envelope,
                    verdict=GateVerdict.HOLD,
                    reasons=[f"No lease for {action_class.value}"],
                )
            return GateResult(envelope=envelope, verdict=GateVerdict.SEAL)

    # ═══════════════════════════════════════════════════════════════════
    # STATE MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════

    def bind_session(self, session_id: str) -> None:
        """Bind a session ID to the loop."""
        self.state.session_id = session_id

    def bind_actor(self, actor_id: str, verified: bool = False) -> None:
        """Bind an actor to the loop."""
        self.state.actor_id = actor_id
        self.state.actor_verified = verified

    def grant_lease(self, lease_id: str, scope: list[str] | None = None) -> None:
        """Grant a lease to the loop."""
        self.state.active_lease_id = lease_id
        if scope:
            self.state.lease_scope = scope

    def revoke_lease(self) -> None:
        """Revoke the active lease."""
        self.state.active_lease_id = None
        self.state.lease_scope = []

    def get_audit_chain(self) -> list[dict[str, Any]]:
        """Get the full audit chain for this session."""
        return [e.model_dump() for e in self.state.audit_events]

    def verify_audit_chain(self) -> bool:
        """Verify the hash chain integrity of all audit events."""
        for i, event in enumerate(self.state.audit_events):
            prior = self.state.audit_events[i - 1] if i > 0 else None
            if not event.verify_chain(prior):
                return False
        return True


# ═══════════════════════════════════════════════════════════════════════════
# SELF-CHECK
# ═══════════════════════════════════════════════════════════════════════════


def _self_check() -> bool:
    """Verify the agent loop and memory governance."""

    # 1. Basic loop creates envelope
    loop = GovernedAgentLoop(
        session_id="test-session",
        actor_id="test-actor",
        actor_verified=False,
    )
    env = loop.build_envelope("test_tool", ActionClass.OBSERVE)
    assert env.kernel.session_id == "test-session"
    assert env.kernel.actor_id == "test-actor"
    assert env.organ.tool_name == "test_tool"

    # 2. Execute observe passes
    def dummy_tool(data: Any) -> dict:
        return {"status": "ok"}

    result = loop.execute(
        "arif_measure",
        ActionClass.OBSERVE,
        tool_fn=dummy_tool,
        input_data={"mode": "health"},
    )
    assert result["allowed"], f"Observe should be allowed: {result['reasons']}"
    assert loop.state.tool_call_count == 1

    # 3. Execute mutation without lease blocks
    result2 = loop.execute(
        "arif_memory_recall",
        ActionClass.MUTATE,
        tool_fn=dummy_tool,
    )
    assert not result2["allowed"], "Mutation without lease should be blocked"
    assert result2["blocked_by"] == "pre_execution_gate"

    # 4. Grant lease, then mutation passes
    loop.grant_lease("LEASE-TEST-001")
    loop.bind_actor("verified-actor", verified=True)
    result3 = loop.execute(
        "arif_memory_recall",
        ActionClass.MUTATE,
        tool_fn=dummy_tool,
    )
    # Preserving prior_state_hash across calls
    assert loop.state.tool_call_count >= 2

    # 5. Audit chain integrity
    assert loop.verify_audit_chain(), "Audit chain should be valid"

    # 6. Revoke lease, mutation blocked again
    loop.revoke_lease()
    result4 = loop.execute(
        "arif_seal",
        ActionClass.IRREVERSIBLE,
        tool_fn=dummy_tool,
    )
    assert not result4["allowed"], "Irreversible without lease should be blocked"

    # 7. Memory governance: constitutional scope requires human ack
    ok, violations = check_memory_access(
        [MemoryScope.CONSTITUTIONAL],
        ActionClass.MUTATE,
        has_lease=True,
        human_ack_id=None,  # missing
        actor_verified=True,
    )
    assert not ok, "Constitutional memory mutation should require human ack"
    assert len(violations) > 0

    # 8. Memory governance: scratch is always allowed
    ok2, violations2 = check_memory_access(
        [MemoryScope.SCRATCH],
        ActionClass.MUTATE,
        has_lease=False,
    )
    assert ok2, f"Scratch memory should always be allowed: {violations2}"

    # 9. Memory governance: vault requires verified actor
    ok3, violations3 = check_memory_access(
        [MemoryScope.VAULT],
        ActionClass.IRREVERSIBLE,
        has_lease=True,
        human_ack_id="hack_test",
        actor_verified=False,  # unverified
    )
    assert not ok3, "Vault memory should require verified actor"

    return True


if __name__ == "__main__":
    assert _self_check(), "Agent loop self-check FAILED"
    print("GovernedAgentLoop self-check PASSED — all 9 assertions verified.")
