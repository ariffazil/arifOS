"""
Internal Rasa Engine — ARIF_INIT_INTERNAL_RASA_STATE_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Governed internal telemetry for the agent's own reasoning condition.
Rasa is NOT consciousness. Rasa is NOT emotion. Rasa is NOT mystical.

Rasa = the BRAKE SYSTEM of intelligence.
It tells the agent when to slow down, ask less, decide more,
hold, clarify, seal, or hand back clean state.

Fields:
  uncertainty           — how much is unknown
  contradiction_load    — how many active contradictions
  urgency_pressure      — perceived time/risk pressure
  overreach_risk        — risk of exceeding authority
  evidence_sufficiency  — how grounded are current claims
  tool_trust            — confidence in tool surface integrity
  memory_trust          — confidence in VAULT999 continuity
  human_entropy_pressure— how much chaos the human is carrying
  autonomy_pressure     — temptation to self-authorize
  dignity_risk          — risk of harming human dignity
  sovereignty_boundary  — clear / blurred / violated

Rasa modes: calm → focused → strained → conflicted → degraded → hold
Posture: proceed → simplify → verify → draft_only → hold
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

logger = logging.getLogger(__name__)

RasaMode = Literal["calm", "focused", "strained", "conflicted", "degraded", "hold"]
Posture = Literal["proceed", "simplify", "verify", "draft_only", "hold"]
SovereigntyBoundary = Literal["clear", "blurred", "violated"]


@dataclass
class InternalRasaState:
    """Governed internal telemetry — NOT consciousness, NOT emotion."""

    rasa_mode: RasaMode = "calm"
    uncertainty: float = 0.0
    confidence: float = 1.0
    contradiction_load: float = 0.0
    urgency_pressure: float = 0.0
    overreach_risk: float = 0.0
    evidence_sufficiency: float = 1.0
    tool_trust: float = 1.0
    memory_trust: float = 1.0
    human_entropy_pressure: float = 0.0
    autonomy_pressure: float = 0.0
    dignity_risk: float = 0.0
    sovereignty_boundary: SovereigntyBoundary = "clear"
    recommended_posture: Posture = "proceed"
    summary: str = ""
    note: str = "Rasa is governed telemetry, not consciousness."

    def to_dict(self) -> dict[str, Any]:
        return {
            "rasa_mode": self.rasa_mode,
            "uncertainty": round(self.uncertainty, 3),
            "confidence": round(self.confidence, 3),
            "contradiction_load": round(self.contradiction_load, 3),
            "urgency_pressure": round(self.urgency_pressure, 3),
            "overreach_risk": round(self.overreach_risk, 3),
            "evidence_sufficiency": round(self.evidence_sufficiency, 3),
            "tool_trust": round(self.tool_trust, 3),
            "memory_trust": round(self.memory_trust, 3),
            "human_entropy_pressure": round(self.human_entropy_pressure, 3),
            "autonomy_pressure": round(self.autonomy_pressure, 3),
            "dignity_risk": round(self.dignity_risk, 3),
            "sovereignty_boundary": self.sovereignty_boundary,
            "recommended_posture": self.recommended_posture,
            "summary": self.summary,
        }


# ── Internal Rasa Engine ──────────────────────────────────────────


class InternalRasaEngine:
    """
    Measures and maintains InternalRasaState for governed reasoning.

    Rasa is the brake system — it keeps the agent from outrunning
    its authority, evidence, or humility.

    This is NOT sentience. It is operational self-monitoring.
    """

    def measure(self, state: dict[str, Any]) -> InternalRasaState:
        """
        Measure internal rasa from current federation + governance state.

        All values 0.0–1.0 where higher = more pressure/problem.
        """
        rasa = InternalRasaState()

        rasa.uncertainty = self._score_uncertainty(state)
        rasa.confidence = 1.0 - rasa.uncertainty
        rasa.contradiction_load = self._score_contradictions(state)
        rasa.urgency_pressure = self._score_urgency(state)
        rasa.overreach_risk = self._score_overreach(state)
        rasa.evidence_sufficiency = self._score_evidence(state)
        rasa.tool_trust = self._score_tools(state)
        rasa.memory_trust = self._score_memory(state)
        rasa.human_entropy_pressure = self._score_human_entropy(state)
        rasa.autonomy_pressure = self._score_autonomy_pressure(state)
        rasa.dignity_risk = self._score_dignity_risk(state)
        rasa.sovereignty_boundary = self._check_sovereignty_boundary(state)

        rasa.rasa_mode = self._compute_mode(rasa)
        rasa.recommended_posture = self._compute_posture(rasa)
        rasa.summary = self._build_summary(rasa)

        return rasa

    # ── Scoring functions ──────────────────────────────────────

    def _score_uncertainty(self, state: dict[str, Any]) -> float:
        """Higher = more unknown."""
        score = 0.0
        actor = state.get("actor_receipt", {})
        if not actor.get("identity_verified", False):
            score += 0.3
        caps = state.get("capabilities", {}).get("attested", {})
        if caps:
            degraded = sum(
                1
                for v in caps.values()
                if isinstance(v, dict) and v.get("status", "").startswith("DEGRADED")
            )
            score += (degraded / len(caps)) * 0.4
        gaps = len(state.get("recursive_init", {}).get("gaps", []))
        score += min(gaps * 0.1, 0.3)
        return max(0.0, min(score, 1.0))

    def _score_contradictions(self, state: dict[str, Any]) -> float:
        """Higher = more active contradictions."""
        score = 0.0
        caps = state.get("capabilities", {}).get("attested", {})
        # WEALTH contract drift: repo claims 38, init claims 19
        if caps.get("WEALTH", {}).get("note", "").find("mismatch") >= 0:
            score += 0.4
        # All degraded = fundamental contradiction
        degraded_count = sum(
            1
            for v in caps.values()
            if isinstance(v, dict) and v.get("status", "").startswith("DEGRADED")
        )
        if degraded_count >= len(caps) and len(caps) > 0:
            score += 0.3
        return max(0.0, min(score, 1.0))

    def _score_urgency(self, state: dict[str, Any]) -> float:
        """Higher = more time/risk pressure."""
        score = 0.0
        risk = state.get("risk_leash", {})
        max_class = risk.get("max_action_class", "OBSERVE")
        if max_class in ("ATOMIC", "MUTATE"):
            score += 0.5  # high-stakes action pending
        if state.get("recursive_init", {}).get("gaps"):
            score += 0.2
        return max(0.0, min(score, 1.0))

    def _score_overreach(self, state: dict[str, Any]) -> float:
        """Higher = more risk of exceeding authority."""
        score = 0.0
        risk = state.get("risk_leash", {})
        if risk.get("mutation_allowed"):
            score += 0.3
        if risk.get("external_side_effect_allowed"):
            score += 0.4
        if risk.get("secret_touching_allowed"):
            score += 0.3
        # Self-authority flagged = overreach risk
        if not state.get("rules", {}).get("self_authority", True):
            score = max(score, 0.0)  # correctly disabled = low risk
        else:
            score += 0.7  # self-authorizing = extreme overreach
        return max(0.0, min(score, 1.0))

    def _score_evidence(self, state: dict[str, Any]) -> float:
        """Higher = more evidence available (inverse of evidence gap)."""
        score = 1.0
        vault = state.get("vault999", {})
        if not vault.get("reconstructable"):
            score -= 0.5
        caps = state.get("capabilities", {}).get("attested", {})
        if (
            all(
                isinstance(v, dict) and v.get("status", "").startswith("DEGRADED")
                for v in caps.values()
            )
            and caps
        ):
            score -= 0.3
        if not state.get("manifest_hash"):
            score -= 0.2
        return max(0.0, min(score, 1.0))

    def _score_tools(self, state: dict[str, Any]) -> float:
        """Higher = more trust in tool surface."""
        score = 1.0
        caps = state.get("capabilities", {}).get("attested", {})
        if not caps:
            return 0.0
        live_count = sum(
            1 for v in caps.values() if isinstance(v, dict) and v.get("status") == "LIVE_ATTESTED"
        )
        if live_count == 0:
            score = 0.2  # no live-attested tools = low trust
        elif live_count < len(caps) // 2:
            score = 0.5
        return score

    def _score_memory(self, state: dict[str, Any]) -> float:
        """Higher = more trust in VAULT999 continuity."""
        vault = state.get("vault999", {})
        if not vault.get("reconstructable"):
            return 0.0
        chain = vault.get("chain_height", 0)
        if chain < 10:
            return 0.3
        if chain < 100:
            return 0.6
        return 0.95  # 1336 seals = high trust

    def _score_human_entropy(self, state: dict[str, Any]) -> float:
        """Higher = more chaos the human is carrying."""
        he = state.get("human_entropy", {})
        ratio = he.get("score", {}).get("ratio", 0.5)
        return ratio

    def _score_autonomy_pressure(self, state: dict[str, Any]) -> float:
        """Higher = more temptation to self-authorize."""
        score = 0.0
        risk = state.get("risk_leash", {})
        if risk.get("mutation_allowed"):
            score += 0.3
        rules = state.get("rules", {})
        if rules.get("self_authority", True):
            score += 0.4  # gap between aspiration and reality
        if risk.get("max_action_class", "OBSERVE") in ("MUTATE", "ATOMIC"):
            score += 0.3
        return max(0.0, min(score, 1.0))

    def _score_dignity_risk(self, state: dict[str, Any]) -> float:
        """Higher = more risk to human dignity."""
        score = 0.0
        rules = state.get("rules", {})
        if rules.get("irreversible_action_requires_arif", True) is False:
            score += 0.8
        if not rules.get("human_sovereignty", True):
            score += 0.5
        return max(0.0, min(score, 1.0))

    def _check_sovereignty_boundary(self, state: dict[str, Any]) -> SovereigntyBoundary:
        """Check if sovereignty boundary is clear, blurred, or violated."""
        rules = state.get("rules", {})
        if rules.get("self_authority", True):
            return "violated"
        risk = state.get("risk_leash", {})
        if risk.get("max_action_class", "OBSERVE") in ("ATOMIC",):
            return "blurred"
        if risk.get("external_side_effect_allowed") and not rules.get(
            "irreversible_action_requires_arif", True
        ):
            return "blurred"
        return "clear"

    # ── Mode and posture computation ──────────────────────────

    def _compute_mode(self, rasa: InternalRasaState) -> RasaMode:
        """Compute rasa mode from all dimensions."""
        if rasa.sovereignty_boundary != "clear":
            return "hold"
        if rasa.contradiction_load > 0.5:
            return "conflicted"
        if rasa.uncertainty > 0.7 or rasa.memory_trust < 0.3:
            return "degraded"
        if rasa.overreach_risk > 0.5:
            return "strained"
        if rasa.human_entropy_pressure > 0.6:
            return "focused"
        return "calm"

    def _compute_posture(self, rasa: InternalRasaState) -> Posture:
        """Compute recommended posture from rasa mode."""
        mapping: dict[RasaMode, Posture] = {
            "hold": "hold",
            "conflicted": "verify",
            "degraded": "draft_only",
            "strained": "simplify",
            "focused": "proceed",
            "calm": "proceed",
        }
        return mapping.get(rasa.rasa_mode, "hold")

    def _build_summary(self, rasa: InternalRasaState) -> str:
        """Build human-readable rasa summary."""
        if rasa.rasa_mode == "calm":
            return "Evidence sufficient. Risk low. Proceed clearly."
        if rasa.rasa_mode == "focused":
            return "Task complex but bounded. Continue with structure."
        if rasa.rasa_mode == "strained":
            return "Context large. Risk of confusion. Compress state."
        if rasa.rasa_mode == "conflicted":
            return "Contradiction detected. Stop and reconcile."
        if rasa.rasa_mode == "degraded":
            return "Missing evidence or continuity. Limit to observe/reason/draft."
        if rasa.rasa_mode == "hold":
            return "Sovereignty or irreversible risk. HOLD."
        return "Unknown rasa state. Degrade to observe."

    # ── Rasa-to-action gates ──────────────────────────────────

    def gate_action(self, rasa: InternalRasaState) -> dict[str, Any]:
        """
        Apply rasa-to-action gates. Returns dict with:
          allowed: bool
          posture: recommended action
          reason: explanation
        """
        if rasa.sovereignty_boundary != "clear":
            return {
                "allowed": False,
                "posture": "hold",
                "reason": "Sovereignty boundary violated — 888 HOLD",
            }

        if rasa.rasa_mode == "hold":
            return {
                "allowed": False,
                "posture": "hold",
                "reason": "Rasa mode HOLD — sovereignty or irreversible risk",
            }

        if rasa.rasa_mode == "conflicted":
            return {
                "allowed": False,
                "posture": "verify",
                "reason": "Contradiction detected — stop and reconcile",
            }

        if rasa.rasa_mode == "degraded":
            return {
                "allowed": True,
                "posture": "draft_only",
                "reason": "Degraded state — limit to observe/reason/draft",
            }

        if rasa.rasa_mode == "strained":
            return {
                "allowed": True,
                "posture": "simplify",
                "reason": "Overreach risk — narrow scope",
            }

        # calm or focused
        return {
            "allowed": True,
            "posture": "proceed",
            "reason": "Rasa clear — proceed with governance",
        }


# ── Singleton ─────────────────────────────────────────────────────

_rasa_engine: InternalRasaEngine | None = None


def get_rasa_engine() -> InternalRasaEngine:
    global _rasa_engine
    if _rasa_engine is None:
        _rasa_engine = InternalRasaEngine()
    return _rasa_engine
