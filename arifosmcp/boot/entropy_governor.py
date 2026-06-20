"""
Human Entropy Governor — ARIF_INIT_HUMAN_ENTROPY_GOVERNOR_v1

DITEMPA BUKAN DIBERI — Forged, Not Given.

Every governed agentic session must lower human entropy.
Intelligence is not the freedom to act — it is the discipline to reduce chaos.

Entropy dimensions (E1–E10):
  E1: uncertainty           — unknown state, missing facts
  E2: open_loops            — unresolved tasks, pending decisions
  E3: decision_burden       — choices forwarded to human unnecessarily
  E4: missing_provenance    — unsealed work, unverifiable claims
  E5: operational_risk      — exposed blast radius, ungoverned mutation
  E6: duplicated_work       — wasted effort, agent collision
  E7: memory_fragmentation  — scattered context, stale state
  E8: federation_drift      — tool/capability/constitution mismatch
  E9: cognitive_load        — complexity forwarded to human
  E10: irreversible_exposure— ungoverned atomic surface

Goal: minimize total E without violating constitution.

Prime rule:
  A governed agent is successful if, after it leaves, Arif has fewer
  decisions, fewer unknowns, fewer risks, fewer scattered contexts,
  fewer hidden loops, and a clearer next move.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# ── Entropy dimension definitions ─────────────────────────────────

ENTROPY_DIMENSIONS = {
    "E1_uncertainty": {
        "label": "Uncertainty",
        "max": 3,
        "description": "Unknown state, missing facts, unverified claims",
    },
    "E2_open_loops": {
        "label": "Open Loops",
        "max": 3,
        "description": "Unresolved tasks, pending decisions, dangling work",
    },
    "E3_decision_burden": {
        "label": "Decision Burden",
        "max": 3,
        "description": "Choices forwarded to human unnecessarily",
    },
    "E4_missing_provenance": {
        "label": "Missing Provenance",
        "max": 3,
        "description": "Unsealed work, unverifiable claims, no audit trail",
    },
    "E5_operational_risk": {
        "label": "Operational Risk",
        "max": 3,
        "description": "Exposed blast radius, ungoverned mutation surface",
    },
    "E6_duplicated_work": {
        "label": "Duplicated Work",
        "max": 3,
        "description": "Agent collision, wasted effort, redundant computation",
    },
    "E7_memory_fragmentation": {
        "label": "Memory Fragmentation",
        "max": 3,
        "description": "Scattered context, stale state, forgotten handoffs",
    },
    "E8_federation_drift": {
        "label": "Federation Drift",
        "max": 3,
        "description": "Tool/capability/constitution mismatch across organs",
    },
    "E9_cognitive_load": {
        "label": "Cognitive Load",
        "max": 3,
        "description": "Complexity forwarded to human without compression",
    },
    "E10_irreversible_exposure": {
        "label": "Irreversible Exposure",
        "max": 3,
        "description": "Ungoverned atomic surface, no rollback path",
    },
}


@dataclass
class EntropyScore:
    """Lightweight entropy scoring across all 10 dimensions."""

    uncertainty: int = 0
    open_loops: int = 0
    decision_burden: int = 0
    missing_provenance: int = 0
    operational_risk: int = 0
    duplicated_work: int = 0
    memory_fragmentation: int = 0
    federation_drift: int = 0
    cognitive_load: int = 0
    irreversible_exposure: int = 0

    def total(self) -> int:
        return sum(
            [
                self.uncertainty,
                self.open_loops,
                self.decision_burden,
                self.missing_provenance,
                self.operational_risk,
                self.duplicated_work,
                self.memory_fragmentation,
                self.federation_drift,
                self.cognitive_load,
                self.irreversible_exposure,
            ]
        )

    def max_possible(self) -> int:
        return 30  # 10 dimensions × max 3 each

    def ratio(self) -> float:
        m = self.max_possible()
        return self.total() / m if m > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "E1_uncertainty": self.uncertainty,
            "E2_open_loops": self.open_loops,
            "E3_decision_burden": self.decision_burden,
            "E4_missing_provenance": self.missing_provenance,
            "E5_operational_risk": self.operational_risk,
            "E6_duplicated_work": self.duplicated_work,
            "E7_memory_fragmentation": self.memory_fragmentation,
            "E8_federation_drift": self.federation_drift,
            "E9_cognitive_load": self.cognitive_load,
            "E10_irreversible_exposure": self.irreversible_exposure,
            "total": self.total(),
            "max": self.max_possible(),
            "ratio": round(self.ratio(), 3),
        }


@dataclass
class OpenLoop:
    """One unresolved item in the federation."""

    loop_id: str
    type: str  # TASK_OPEN, DECISION_PENDING, etc.
    owner: str = "unknown"
    status: str = "open"
    next_action: str = ""
    risk: str = "medium"
    vault_pointer: str | None = None


# ── Entropy Governor ──────────────────────────────────────────────


class EntropyGovernor:
    """
    Measures and governs human entropy across all 10 dimensions.

    Purpose: every session must leave Arif with less chaos, clearer
    truth, tighter risk, fewer open loops, and a sealed path forward.

    This is NOT an autonomous agent. It is a measurement and advisory
    instrument. It scores, recommends, but never acts.
    """

    def measure(self, state: dict[str, Any]) -> EntropyScore:
        """
        Score human entropy from current federation state.

        Reads the swarm manifest, vault state, capabilities, leases,
        tasks, and risk leash to compute E1–E10.
        """
        return EntropyScore(
            uncertainty=self._score_uncertainty(state),
            open_loops=self._score_open_loops(state),
            decision_burden=self._score_decision_burden(state),
            missing_provenance=self._score_missing_provenance(state),
            operational_risk=self._score_operational_risk(state),
            duplicated_work=self._score_duplicated_work(state),
            memory_fragmentation=self._score_memory_fragmentation(state),
            federation_drift=self._score_federation_drift(state),
            cognitive_load=self._score_cognitive_load(state),
            irreversible_exposure=self._score_irreversible_exposure(state),
        )

    def choose_next_action(self, state: dict[str, Any], score: EntropyScore) -> dict[str, Any]:
        """
        Choose the smallest safe entropy-reducing action.

        Priority order:
          1. Prevent irreversible harm
          2. Clarify current state
          3. Close stale loops
          4. Reconcile contradictions
          5. Seal important state
          6. Produce smallest useful next action
        """
        # Find the highest-entropy dimension
        dims = score.to_dict()
        ranked = sorted(
            [(k, v) for k, v in dims.items() if k.startswith("E")],
            key=lambda x: -x[1],
        )

        if not ranked:
            return {"action": "OBSERVE_ONLY", "reason": "No entropy data"}

        top_dim, top_score = ranked[0]

        if top_score <= 1:
            return {
                "action": "PROCEED_WITH_LEASE_RULES",
                "reason": f"Entropy low ({top_dim}={top_score})",
                "entropy_ratio": score.ratio(),
            }

        # Map high-entropy dimensions to recommended actions
        recommendations = {
            "E1_uncertainty": ("SENSE_AND_CLARIFY", "High uncertainty — observe and classify"),
            "E2_open_loops": ("CLOSE_STALE_LOOPS", "Open loops detected — resolve or escalate"),
            "E3_decision_burden": (
                "CLASSIFY_DECISIONS",
                "Decision burden high — classify what agent can decide vs human gate",
            ),
            "E4_missing_provenance": (
                "SEAL_IMPORTANT_STATE",
                "Unsealed work — propose VAULT999 seal",
            ),
            "E5_operational_risk": ("TIGHTEN_RISK_LEASH", "Operational risk — reduce action class"),
            "E6_duplicated_work": (
                "COORDINATE_AGENTS",
                "Duplication detected — check active leases",
            ),
            "E7_memory_fragmentation": (
                "COMPRESS_CONTEXT",
                "Fragmented memory — produce context packet",
            ),
            "E8_federation_drift": ("REATTEST_CAPABILITIES", "Drift detected — re-attest organs"),
            "E9_cognitive_load": ("SUMMARIZE_FOR_HUMAN", "High cognitive load — compress for Arif"),
            "E10_irreversible_exposure": ("888_HOLD", "Irreversible exposure — escalate to human"),
        }

        action, reason = recommendations.get(top_dim, ("OBSERVE_ONLY", "Unknown entropy dimension"))

        return {
            "action": action,
            "reason": reason,
            "top_dimension": top_dim,
            "top_score": top_score,
            "entropy_ratio": score.ratio(),
            "entropy_total": score.total(),
        }

    def close_session(self, before: EntropyScore, after: EntropyScore) -> dict[str, Any]:
        """
        Compute entropy delta at session close.

        Returns verdict:
          CHAOS_REDUCED    — entropy decreased
          STATE_PRESERVED  — entropy unchanged
          CHAOS_INCREASED  — entropy increased (must explain why)
        """
        delta = after.total() - before.total()

        if delta < 0:
            verdict = "CHAOS_REDUCED"
        elif delta == 0:
            verdict = "STATE_PRESERVED"
        else:
            verdict = "CHAOS_INCREASED_EXPLAIN"

        return {
            "entropy_before": before.to_dict(),
            "entropy_after": after.to_dict(),
            "delta": delta,
            "delta_ratio": round(delta / before.max_possible(), 3)
            if before.max_possible() > 0
            else 0.0,
            "verdict": verdict,
            "note": (
                "Chaos reduced — session improved federation state."
                if verdict == "CHAOS_REDUCED"
                else "Chaos increased — session must explain why and seal receipt."
                if verdict == "CHAOS_INCREASED_EXPLAIN"
                else "State preserved — no change in human entropy."
            ),
        }

    def open_loop_register(self, state: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Build the OpenLoopRegister from current state.

        Detects: stale tasks, pending decisions, unattested capabilities,
        expired leases, unsealed vault entries, detected drift.
        """
        loops: list[dict[str, Any]] = []

        # TASK_OPEN: check unresolved tasks
        swarm = state.get("swarm", {})
        tasks = swarm.get("unresolved_tasks", [])
        for task in tasks:
            loops.append(
                {
                    "loop_id": task.get("task_id", "unknown"),
                    "type": "TASK_OPEN",
                    "owner": task.get("holder", "unknown"),
                    "status": task.get("status", "open"),
                    "risk": "medium",
                }
            )

        # CAPABILITY_UNATTESTED: check degraded organs
        caps = state.get("capabilities", {}).get("attested", {})
        for organ, info in caps.items():
            if info.get("status", "").startswith("DEGRADED"):
                loops.append(
                    {
                        "loop_id": f"CAP-{organ}",
                        "type": "CAPABILITY_UNATTESTED",
                        "owner": organ,
                        "status": "open",
                        "next_action": f"Request live attestation from {organ}",
                        "risk": "medium",
                    }
                )

        # VAULT999_UNSEALED: check if boot seal is dry-run only
        boot_seal = state.get("vault999_boot_seal", {})
        if boot_seal.get("status") == "DRY_RUN_SEAL":
            loops.append(
                {
                    "loop_id": "VAULT-BOOT-SEAL",
                    "type": "VAULT999_UNSEALED",
                    "owner": "arifOS",
                    "status": "open",
                    "next_action": "Real VAULT999 seal requires F01/F13 gates",
                    "risk": "low",
                }
            )

        # LEASE_EXPIRED: check active leases
        leases = swarm.get("active_leases", [])
        for lease in leases:
            if lease.get("status") == "EXPIRED":
                loops.append(
                    {
                        "loop_id": lease.get("lease_id", "unknown"),
                        "type": "LEASE_EXPIRED",
                        "owner": lease.get("holder", "unknown"),
                        "status": "open",
                        "next_action": "Release or renew lease",
                        "risk": "low",
                    }
                )

        # DRIFT_DETECTED: check capability degradation
        degraded = state.get("recursive_init", {}).get("degraded_organs", [])
        if degraded:
            loops.append(
                {
                    "loop_id": "DRIFT-CAPABILITY",
                    "type": "DRIFT_DETECTED",
                    "owner": "arifOS",
                    "status": "open",
                    "next_action": f"Re-attest {len(degraded)} degraded organs",
                    "risk": "medium",
                }
            )

        return loops

    # ── Private scoring functions ──────────────────────────────────

    def _score_uncertainty(self, state: dict[str, Any]) -> int:
        score = 0
        actor = state.get("actor_receipt", {})
        if not actor.get("identity_verified", False):
            score += 1  # actor unverified
        caps = state.get("capabilities", {}).get("attested", {})
        degraded_count = sum(
            1 for info in caps.values() if info.get("status", "").startswith("DEGRADED")
        )
        if degraded_count >= len(caps) and len(caps) > 0:
            score += 1  # all organs degraded
        if state.get("recursive_init", {}).get("gaps"):
            score += 1  # known gaps exist
        return min(score, 3)

    def _score_open_loops(self, state: dict[str, Any]) -> int:
        loops = self.open_loop_register(state)
        count = len(loops)
        if count == 0:
            return 0
        if count <= 3:
            return 1
        if count <= 7:
            return 2
        return 3

    def _score_decision_burden(self, state: dict[str, Any]) -> int:
        # Arif decisions needed: all DEGRADED_CLAIM organs need attestation decision
        caps = state.get("capabilities", {}).get("attested", {})
        degraded = sum(1 for info in caps.values() if info.get("status", "").startswith("DEGRADED"))
        if degraded == 0:
            return 0
        if degraded <= 2:
            return 1
        if degraded <= 5:
            return 2
        return 3

    def _score_missing_provenance(self, state: dict[str, Any]) -> int:
        score = 0
        boot_seal = state.get("vault999_boot_seal", {})
        if boot_seal.get("status") == "DRY_RUN_SEAL":
            score += 1
        vault = state.get("vault999", {})
        if not vault.get("reconstructable"):
            score += 2
        return min(score, 3)

    def _score_operational_risk(self, state: dict[str, Any]) -> int:
        risk = state.get("risk_leash", {})
        max_class = risk.get("max_action_class", "OBSERVE")
        if max_class == "OBSERVE":
            return 0
        if max_class in ("DRAFT", "REASON"):
            return 1
        if max_class == "DRY_RUN":
            return 2
        return 3  # MUTATE or higher

    def _score_duplicated_work(self, state: dict[str, Any]) -> int:
        swarm = state.get("swarm", {})
        agents = swarm.get("active_agents", [])
        if len(agents) <= 1:
            return 0
        if len(agents) <= 2:
            return 1
        return 2  # potential for collision

    def _score_memory_fragmentation(self, state: dict[str, Any]) -> int:
        vault = state.get("vault999", {})
        if not vault.get("reconstructable"):
            return 3  # no memory continuity
        if not vault.get("handoff_pointer"):
            return 2  # no clear handoff
        if not state.get("manifest_hash"):
            return 1  # unsealed
        return 0

    def _score_federation_drift(self, state: dict[str, Any]) -> int:
        degraded = state.get("recursive_init", {}).get("degraded_organs", [])
        if not degraded:
            return 0
        if len(degraded) <= 2:
            return 1
        if len(degraded) <= 5:
            return 2
        return 3

    def _score_cognitive_load(self, state: dict[str, Any]) -> int:
        gaps = state.get("recursive_init", {}).get("gaps", [])
        loops = self.open_loop_register(state)
        total = len(gaps) + len(loops)
        if total == 0:
            return 0
        if total <= 3:
            return 1
        if total <= 7:
            return 2
        return 3

    def _score_irreversible_exposure(self, state: dict[str, Any]) -> int:
        rules = state.get("rules", {})
        if rules.get("self_authority", True):
            return 3  # self-authorizing = maximal exposure
        risk = state.get("risk_leash", {})
        if risk.get("irreversible_allowed") or risk.get("external_side_effect_allowed"):
            return 3
        return 0  # self_authority false + no irreversible allowed = safe


# ── Singleton ─────────────────────────────────────────────────────

_entropy_governor: EntropyGovernor | None = None


def get_entropy_governor() -> EntropyGovernor:
    global _entropy_governor
    if _entropy_governor is None:
        _entropy_governor = EntropyGovernor()
    return _entropy_governor
