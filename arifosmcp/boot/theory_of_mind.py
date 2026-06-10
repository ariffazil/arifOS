"""
Theory of Mind Engine — ARIF_INIT_THEORY_OF_MIND_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

A bounded model of Arif, other agents, stakeholders, and federation context.
Purpose: reduce human burden, not manipulate.

ToM is the STEERING SYSTEM of service — it aims the agent toward the human.

Rules:
  - Never treat inference as truth.
  - Always tag claims: OBSERVED / DERIVED / SPECULATIVE.
  - Mind-reading is FORBIDDEN.
  - Say "Likely intent: X", never "Arif wants X" unless observed.
  - Do not over-explain known context.
  - Do not ask questions already answerable.
  - Do not give ten options when one decision is obvious.
  - Do not hide risk.
  - Do not flatter.
  - Do not make Arif carry agent confusion.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

ClaimState = Literal["OBSERVED", "DERIVED", "SPECULATIVE", "FORBIDDEN"]
DecisionBurden = Literal["low", "medium", "high"]
ContextFamiliarity = Literal["novice", "familiar", "expert"]


@dataclass
class HumanModel:
    """Bounded model of Arif — the sovereign architect."""

    name: str = "Arif"
    role: str = "sovereign_architect"
    decision_style: str = "fast_direct"
    preferred_response: str = "plain_decisive_structured"
    current_goal: str = "reduce chaos and improve governed runtime intelligence"
    likely_hidden_goal: str = "federation autonomy without sovereignty loss"
    decision_burden: DecisionBurden = "medium"
    context_familiarity: ContextFamiliarity = "expert"
    needs: list[str] = field(
        default_factory=lambda: [
            "clarity",
            "execution_path",
            "risk_boundary",
            "copy_paste_spec",
            "architecture_synthesis",
        ]
    )
    avoid: list[str] = field(
        default_factory=lambda: [
            "generic advice",
            "too many choices",
            "re-explaining arifOS basics",
            "false certainty",
            "unnecessary questions",
        ]
    )
    claim_state: ClaimState = "DERIVED"


@dataclass
class AgentBelief:
    """What we believe about another agent in the swarm."""

    agent_id: str
    role: str = "unknown"
    status: str = "ACTIVE"
    lease_held: str | None = None
    task_held: str | None = None
    possible_misalignment: str | None = None
    claim_state: ClaimState = "DERIVED"


@dataclass
class TheoryOfMindState:
    """Complete Theory of Mind for a governed session."""

    human: HumanModel = field(default_factory=HumanModel)
    agents: dict[str, AgentBelief] = field(default_factory=dict)
    stakeholders: dict[str, list[str]] = field(
        default_factory=lambda: {
            "direct": ["Arif"],
            "indirect": ["future agents", "federation users", "operators", "affected humans"],
            "weakest": ["human_who_inherits_agent_output"],
        }
    )
    session: dict[str, Any] = field(
        default_factory=lambda: {
            "human_entropy_estimate": 0,
            "open_loops": [],
            "likely_next_best_action": "",
        }
    )
    sovereignty_required: bool = False
    summary: str = ""
    claim_state: ClaimState = "DERIVED"


# ── Theory of Mind Engine ────────────────────────────────────────


class TheoryOfMindEngine:
    """
    Builds and maintains TheoryOfMindState for a governed session.

    This is NOT mind-reading. It is operational modeling to reduce
    human burden, avoid unnecessary questions, and aim the agent
    toward entropy-reducing action.
    """

    def build(
        self,
        *,
        input_context: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
    ) -> TheoryOfMindState:
        """
        Build TheoryOfMindState from session input and federation state.

        All claims are DERIVED unless explicitly OBSERVED in input.
        """
        tom = TheoryOfMindState()

        # ── Human model ────────────────────────────────────
        tom.human.current_goal = self._infer_current_goal(input_context, state)
        tom.human.decision_burden = self._estimate_decision_burden(state)
        tom.human.context_familiarity = self._estimate_context_familiarity(input_context)
        tom.human.claim_state = "DERIVED"

        # ── Agent models ───────────────────────────────────
        if state:
            swarm = state.get("swarm", {})
            for agent_info in swarm.get("active_agents", []):
                if isinstance(agent_info, dict):
                    aid = agent_info.get("agent_id", "unknown")
                    tom.agents[aid] = AgentBelief(
                        agent_id=aid,
                        status="ACTIVE",
                        lease_held=agent_info.get("lease_id"),
                        claim_state="DERIVED",
                    )

        # ── Session context ────────────────────────────────
        tom.sovereignty_required = self._requires_human_judgment(state)

        # ── Summary ────────────────────────────────────────
        tom.summary = (
            f"Arif: {tom.human.decision_burden} burden, "
            f"{len(tom.agents)} known agents, "
            f"sovereignty {'REQUIRED' if tom.sovereignty_required else 'not required'}. "
            f"Goal: reduce chaos through governed execution."
        )
        tom.claim_state = "DERIVED"

        return tom

    def _infer_current_goal(
        self,
        input_context: dict[str, Any] | None,
        state: dict[str, Any] | None,
    ) -> str:
        """Infer Arif's likely current goal from context. DERIVED only."""
        if input_context and input_context.get("mode") == "forge":
            return "execute governed forge cycle"
        if input_context and input_context.get("mode") == "audit":
            return "audit federation state and reduce drift"
        return "reduce chaos and improve governed runtime intelligence"

    def _estimate_decision_burden(self, state: dict[str, Any] | None) -> DecisionBurden:
        """Estimate Arif's decision burden from federation state."""
        if not state:
            return "medium"

        caps = state.get("capabilities", {}).get("attested", {})
        degraded_count = sum(
            1
            for info in caps.values()
            if isinstance(info, dict) and info.get("status", "").startswith("DEGRADED")
        )
        total = len(caps)

        if total == 0:
            return "medium"
        if degraded_count >= total:
            return "high"  # all organs need attestation decisions
        if degraded_count >= total // 2:
            return "medium"
        return "low"

    def _estimate_context_familiarity(
        self, input_context: dict[str, Any] | None
    ) -> ContextFamiliarity:
        """Estimate Arif's familiarity with current context."""
        if input_context and input_context.get("mode") in ("forge", "init", "audit"):
            return "expert"
        return "familiar"

    def _requires_human_judgment(self, state: dict[str, Any] | None) -> bool:
        """Determine if human sovereignty judgment is required."""
        if not state:
            return False

        risk = state.get("risk_leash", {})
        max_class = risk.get("max_action_class", "OBSERVE")

        # Arif required for: ATOMIC, EXTERNAL, SECRET, ROOT, DEPLOY, PUBLISH, MONEY
        if max_class in ("ATOMIC", "MUTATE"):
            return True
        if risk.get("external_side_effect_allowed"):
            return True
        if risk.get("secret_touching_allowed"):
            return True

        return False

    def entropy_sources(self, tom: TheoryOfMindState, state: dict[str, Any] | None) -> list[str]:
        """Identify human entropy sources from ToM perspective."""
        sources: list[str] = []

        if tom.human.decision_burden == "high":
            sources.append("Arif's decision burden is high — classify and decide what is safe")

        if tom.sovereignty_required:
            sources.append("Sovereignty gate active — prepare clear escalation")

        if state:
            caps = state.get("capabilities", {}).get("attested", {})
            degraded = sum(
                1
                for info in caps.values()
                if isinstance(info, dict) and info.get("status", "").startswith("DEGRADED")
            )
            if degraded > 0:
                sources.append(f"{degraded} organs need capability attestation")

        return sources


# ── Singleton ─────────────────────────────────────────────────────

_tom_engine: TheoryOfMindEngine | None = None


def get_tom_engine() -> TheoryOfMindEngine:
    global _tom_engine
    if _tom_engine is None:
        _tom_engine = TheoryOfMindEngine()
    return _tom_engine
