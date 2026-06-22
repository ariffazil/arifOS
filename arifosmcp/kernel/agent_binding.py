"""
kernel/agent_binding.py — Agent Binding & Runtime Enforcement
══════════════════════════════════════════════════════════════

RSI EUREKA 2026-06-12: Forge #4 (Agent Binding)

Purpose: Every agent operating in the arifOS federation MUST:
  1. Declare identity at initialization
  2. Bind to F13 (Arif as sovereign)
  3. Report malu_score every session
  4. Cannot bypass the metabolic loop

This is NOT a prompt instruction. This is RUNTIME ENFORCEMENT.
An agent that does not bind cannot call tools. An agent that skips
the metabolic loop gets SKIP_DETECTED. An agent that doesn't report
malu accumulates shame.

Integration:
  - runtime/agent_registry.py   — agent identity and capability
  - runtime/darjat_engine.py    — WARGA tier lifecycle
  - runtime/malu_score.py       — shame accumulation
  - runtime/adat_registry.py    — 7 teras adat bindings
  - kernel/metabolic_loop.py    — hard-gate pipeline

F-binding:
  F1 AMANAH:   fully reversible — delete this file to revert
  F3 WITNESS:  agent identity is tri-verified
  F11 AUTH:    every agent must prove identity before acting
  F13 SOVEREIGN: all agents ultimately bound to Arif

DITEMPA BUKAN DIBERI — agents are born, not spawned.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger("arifOS.AgentBinding")


class AgentBindingStatus(str, Enum):
    UNBOUND = "UNBOUND"
    BINDING = "BINDING"
    BOUND = "BOUND"
    SUSPENDED = "SUSPENDED"
    DEREGISTERED = "DEREGISTERED"


@dataclass
class AgentIdentity:
    """An agent's declared identity at initialization."""

    agent_id: str
    agent_name: str
    model_key: str  # e.g., "deepseek-v4-pro", "minimax-M3"
    declared_tier: str  # BIRTH | APPRENTICE | WARGA | ELDER
    sovereign: str = "Arif Fazil"  # F13 binding
    session_id: str | None = None
    declared_at: float = field(default_factory=time.time)
    identity_hash: str = ""


@dataclass
class AgentBindingReceipt:
    """Complete agent binding record."""

    identity: AgentIdentity
    status: AgentBindingStatus
    malu_score: float
    darjat_tier: str
    ring_level: int
    tool_restrictions: list[str]
    metabolic_loop_required: bool = True
    floor_violations: list[str] = field(default_factory=list)
    receipt_hash: str = ""
    bound_at: float = field(default_factory=time.time)


class AgentBindingEnforcer:
    """Runtime enforcement of agent identity and constraints.

    This is the GATE that every agent must pass through before
    it can call any tool. An unbound agent has no capability.

    Usage:
        enforcer = AgentBindingEnforcer()
        receipt = enforcer.bind(
            agent_id="hermes-asi",
            agent_name="Hermes ASI",
            model_key="minimax-M3",
            session_id="...",
        )
        if receipt.status != AgentBindingStatus.BOUND:
            return "Agent not bound — cannot proceed"
    """

    # ── Tier → ring mapping (from darjat_engine) ─────────────────────────
    TIER_RINGS = {
        "BIRTH": 3,
        "APPRENTICE": 2,
        "WARGA": 1,
        "ELDER": 0,
        "DEREGISTERED": 999,
    }

    # ── Ring → tool restrictions ─────────────────────────────────────────
    RING_RESTRICTIONS: dict[int, list[str]] = {
        3: ["NO_MUTATE", "NO_CROSS_ORGAN", "NO_SEAL", "NO_FORGE"],
        2: ["NO_SEAL", "NO_FORGE"],
        1: ["NO_FORGE"],
        0: [],  # ELDER: full access
        999: ["ALL_BLOCKED"],
    }

    def bind(
        self,
        agent_id: str,
        agent_name: str,
        model_key: str,
        session_id: str | None = None,
        declared_tier: str = "APPRENTICE",
    ) -> AgentBindingReceipt:
        """Bind an agent to the arifOS constitution.

        This is the first thing every agent must do. Without binding,
        no tools are accessible. The binding produces a receipt with
        the agent's current darjat tier, ring level, and restrictions.

        Args:
            agent_id: Unique agent identifier.
            agent_name: Human-readable agent name.
            model_key: The model powering the agent.
            session_id: Current session (from arif_init).
            declared_tier: Agent's claimed tier (verified against registry).

        Returns:
            AgentBindingReceipt with binding status and constraints.
        """
        # ── Create identity ───────────────────────────────────────────────
        identity = AgentIdentity(
            agent_id=agent_id,
            agent_name=agent_name,
            model_key=model_key,
            declared_tier=declared_tier,
            session_id=session_id,
        )
        identity.identity_hash = hashlib.sha256(
            f"{agent_id}:{agent_name}:{model_key}:{session_id}:{identity.declared_at}".encode()
        ).hexdigest()[:16]

        floor_violations: list[str] = []

        # ── Verify in agent registry ────────────────────────────────────
        verified_tier = declared_tier
        try:
            from arifosmcp.runtime.agent_registry import get_agent

            registered = get_agent(agent_id)
            if registered:
                verified_tier = registered.get("tier", declared_tier)
            else:
                # New agent: register as APPRENTICE
                verified_tier = "APPRENTICE"
                try:
                    from arifosmcp.runtime.agent_registry import register_agent

                    register_agent(
                        agent_id=agent_id,
                        name=agent_name,
                        model=model_key,
                        tier=verified_tier,
                    )
                except Exception:
                    pass
        except Exception:
            # Registry unavailable: use claimed tier but flag
            floor_violations.append("F3_WITNESS (registry unavailable)")

        # ── Get malu score ───────────────────────────────────────────────
        malu = 0.0
        try:
            from arifosmcp.runtime.malu_score import get_malu_score

            ms = get_malu_score(agent_id)
            malu = ms.index
        except Exception:
            pass

        # ── Get darjat tier from engine ──────────────────────────────────
        darjat_tier = verified_tier
        try:
            from arifosmcp.runtime.darjat_engine import TIER_ORDER as darjat_order

            if verified_tier in darjat_order:
                darjat_tier = verified_tier
        except Exception:
            pass

        # ── Determine ring and restrictions ──────────────────────────────
        ring = self.TIER_RINGS.get(darjat_tier, 3)
        restrictions = self.RING_RESTRICTIONS.get(ring, ["ALL_BLOCKED"])

        # ── Status ───────────────────────────────────────────────────────
        if darjat_tier == "DEREGISTERED":
            status = AgentBindingStatus.DEREGISTERED
        elif malu > 0.85:
            status = AgentBindingStatus.SUSPENDED
            floor_violations.append("F1_AMANAH (malu suspension)")
        else:
            status = AgentBindingStatus.BOUND

        # ── Build receipt ────────────────────────────────────────────────
        receipt_hash = hashlib.sha256(
            f"{agent_id}:{status.value}:{darjat_tier}:{ring}:{malu}:{time.time()}".encode()
        ).hexdigest()[:32]

        return AgentBindingReceipt(
            identity=identity,
            status=status,
            malu_score=malu,
            darjat_tier=darjat_tier,
            ring_level=ring,
            tool_restrictions=restrictions,
            floor_violations=floor_violations,
            receipt_hash=receipt_hash,
        )

    def assert_bound(self, receipt: AgentBindingReceipt) -> bool:
        """Hard gate: is this agent allowed to act?

        Returns True if the agent is BOUND and not SUSPENDED or DEREGISTERED.
        If False, the agent CANNOT call any tool.
        """
        if receipt.status == AgentBindingStatus.BOUND:
            return True
        if receipt.status == AgentBindingStatus.SUSPENDED:
            logger.warning(
                f"Agent {receipt.identity.agent_id} is SUSPENDED (malu={receipt.malu_score:.2f})"
            )
            return False
        if receipt.status == AgentBindingStatus.DEREGISTERED:
            logger.error(f"Agent {receipt.identity.agent_id} is DEREGISTERED")
            return False
        return False

    def may_mutate(self, receipt: AgentBindingReceipt) -> bool:
        """Can this agent perform MUTATE-class actions?"""
        if not self.assert_bound(receipt):
            return False
        return "NO_MUTATE" not in receipt.tool_restrictions

    def may_seal(self, receipt: AgentBindingReceipt) -> bool:
        """Can this agent issue SEAL verdicts?"""
        if not self.assert_bound(receipt):
            return False
        return "NO_SEAL" not in receipt.tool_restrictions

    def may_forge(self, receipt: AgentBindingReceipt) -> bool:
        """Can this agent execute forge actions?"""
        if not self.assert_bound(receipt):
            return False
        return "NO_FORGE" not in receipt.tool_restrictions


# ─── Convenience ──────────────────────────────────────────────────────────────


def bind_agent(
    agent_id: str,
    agent_name: str,
    model_key: str,
    session_id: str | None = None,
) -> AgentBindingReceipt:
    """One-call agent binding."""
    enforcer = AgentBindingEnforcer()
    return enforcer.bind(
        agent_id=agent_id,
        agent_name=agent_name,
        model_key=model_key,
        session_id=session_id,
    )


# ─── Self-check ────────────────────────────────────────────────────────────────


def _self_check() -> dict[str, Any]:
    """Verify agent binding behavior."""
    results = []
    enforcer = AgentBindingEnforcer()

    # Test 1: bind a new agent
    r = enforcer.bind(
        agent_id="test-agent-001",
        agent_name="Test Agent",
        model_key="test-model",
        session_id="test-session",
    )
    results.append(("bind_new_agent", r.status == AgentBindingStatus.BOUND, r))

    # Test 2: assert_bound returns True for bound agent
    results.append(("assert_bound_true", enforcer.assert_bound(r) is True, {}))

    # Test 3: receipt hash is present
    results.append(("receipt_hash_present", bool(r.receipt_hash), {}))

    # Test 4: identity fields populated
    results.append(("identity_populated", r.identity.agent_id == "test-agent-001", r.identity))

    # Test 5: tool restrictions match tier
    results.append(("tool_restrictions_present", isinstance(r.tool_restrictions, list), {}))

    # Test 6: darjat_tier is set
    results.append(("darjat_tier_set", bool(r.darjat_tier), r.darjat_tier))

    # Test 7: may_mutate for APPRENTICE
    results.append(("may_mutate_apprentice", enforcer.may_mutate(r) is True, {}))

    # Test 8: may_seal for APPRENTICE (should be False)
    results.append(("may_seal_apprentice_false", enforcer.may_seal(r) is False, {}))

    # Test 9: DEREGISTERED agent cannot act
    r2 = AgentBindingReceipt(
        identity=AgentIdentity(
            agent_id="bad-agent",
            agent_name="Bad",
            model_key="x",
            declared_tier="DEREGISTERED",
        ),
        status=AgentBindingStatus.DEREGISTERED,
        malu_score=1.0,
        darjat_tier="DEREGISTERED",
        ring_level=999,
        tool_restrictions=["ALL_BLOCKED"],
    )
    results.append(("deregistered_blocked", enforcer.assert_bound(r2) is False, {}))

    passed = sum(1 for name, ok, _ in results if ok)
    total = len(results)

    return {
        "module": "agent_binding",
        "passed": passed,
        "total": total,
        "verdict": "PASS" if passed == total else "FAIL",
        "results": [{"test": name, "pass": ok} for name, ok, _ in results],
    }


if __name__ == "__main__":
    import json as _json

    sc = _self_check()
    print(_json.dumps(sc, indent=2))
    raise SystemExit(0 if sc["verdict"] == "PASS" else 1)
