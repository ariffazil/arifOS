"""
art_compat.py — Legacy 6-check order compat shim
═══════════════════════════════════════════════════════════════════════════════
For the 18-test legacy battery that targets the 6-check order.
This is v1 over-engineering preserved as compat-only. Not used in production.

The canonical reflex is in art.py (v3 light, ≤ 500 lines). This module exists
ONLY to make the 18 legacy tests pass. New code should use art.py.

Heritage: v1 ART (12 cmd × 7 fasa × 5 files) → rolled back 2026-06-21
See /root/.agents/skills/ART/SKILL.md §"Hard Lesson (2026-06-21, Arif correction)"

DITEMPA BUKAN DIBERI — compat exists for tests, not for the reflex.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# §ENUMS
# ═══════════════════════════════════════════════════════════════════════


class DecisionClass(str, Enum):
    """C0-C5 decision classes (the 6 levels of consequence)."""

    C0 = "C0"  # pure observation, no side effect
    C1 = "C1"  # analysis, read-only reasoning
    C2 = "C2"  # draft, proposal only
    C3 = "C3"  # mutate with rollback
    C4 = "C4"  # execute, irreversible
    C5 = "C5"  # void, no recovery


class GatewayVerdict(str, Enum):
    """The 5 verdicts the legacy 6-check order can emit."""

    PROCEED = "PROCEED"
    SABAR = "SABAR"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    DEFAULT_OBSERVE = "DEFAULT_OBSERVE"


class ReversibilityTier(str, Enum):
    """4-tier reversibility (REVERSIBLE → COMPENSABLE → IRREVERSIBLE → VOID)."""

    REVERSIBLE = "reversible"
    COMPENSABLE = "compensable"
    IRREVERSIBLE = "irreversible"
    VOID = "void"


# ═══════════════════════════════════════════════════════════════════════
# §DATACLASSES
# ═══════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class EntropySnapshot:
    """A snapshot of system entropy at a point in time."""

    omega: float
    psi_vitality: float
    timestamp: float
    source: str

    @property
    def is_overload(self) -> bool:
        return self.omega >= 0.85

    @property
    def is_warm(self) -> bool:
        return self.omega >= 0.65

    @property
    def is_healthy(self) -> bool:
        return self.omega < 0.65

    def to_dict(self) -> dict[str, Any]:
        return {
            "omega": self.omega,
            "psi_vitality": self.psi_vitality,
            "timestamp": self.timestamp,
            "source": self.source,
            "is_overload": self.is_overload,
            "is_warm": self.is_warm,
            "is_healthy": self.is_healthy,
        }


@dataclass(frozen=True)
class ReversibilityAssessment:
    """The output of a 4-tier reversibility check."""

    tier: ReversibilityTier
    rationale: str
    can_rollback: bool
    blast_radius: str
    estimated_undo_steps: int


@dataclass(frozen=True)
class GatewayDecision:
    """The full decision record of a 6-check order gateway pass."""

    verdict: GatewayVerdict
    decision_class: DecisionClass
    reversibility: ReversibilityAssessment
    entropy: EntropySnapshot
    actor_id: str
    tool_name: str
    rationale: str
    next_action: str
    witness: dict[str, float] = field(
        default_factory=lambda: {
            "human": 0.42,
            "ai": 0.32,
            "earth": 0.26,
        }
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "decision_class": self.decision_class.value,
            "reversibility": {
                "tier": self.reversibility.tier.value,
                "rationale": self.reversibility.rationale,
                "can_rollback": self.reversibility.can_rollback,
                "blast_radius": self.reversibility.blast_radius,
            },
            "entropy": self.entropy.to_dict(),
            "actor_id": self.actor_id,
            "tool_name": self.tool_name,
            "rationale": self.rationale,
            "next_action": self.next_action,
            "witness": self.witness,
        }


# ═══════════════════════════════════════════════════════════════════════
# §AUTHORITY
# ═══════════════════════════════════════════════════════════════════════


AUTHORITY_ORDER: list[str] = ["readonly", "contributor", "operator", "sovereign", "f13"]

DEFAULT_AUTHORITY: dict[str, str] = {
    "arif": "f13",
    "sovereign": "f13",
    "openclaw": "operator",
    "forge": "operator",
    "hermes": "readonly",
}

DEFAULT_TOOL_AUTHORITY: dict[str, str] = {
    "arif_judge": "f13",
    "arif_seal": "f13",
    "arif_forge": "operator",
    "arif_kernel_route": "operator",
    "arif_think": "readonly",
    "arif_critique": "readonly",
    "arif_memory_recall": "readonly",
    "arif_observe": "readonly",
    "arif_fetch": "readonly",
    "arif_kernel_status": "readonly",
    "arif_kernel_attest": "readonly",
    "arif_init": "readonly",
}


def _classify_decision(action_class: str) -> DecisionClass:
    mapping = {
        "OBSERVE": DecisionClass.C0,
        "ANALYZE": DecisionClass.C1,
        "DRAFT": DecisionClass.C2,
        "MUTATE": DecisionClass.C3,
        "EXECUTE": DecisionClass.C4,
        "EXTERNAL_SIDE_EFFECT": DecisionClass.C4,
        "IRREVERSIBLE": DecisionClass.C5,
    }
    return mapping.get(action_class.upper(), DecisionClass.C3)


def _check_authority(actor_id: str, tool_name: str) -> tuple[bool, str]:
    actor_tier = DEFAULT_AUTHORITY.get(actor_id.lower())
    if actor_tier is None:
        return False, f"Unknown actor '{actor_id}'; cannot authorize."
    required_tier = DEFAULT_TOOL_AUTHORITY.get(tool_name, "operator")
    if required_tier not in AUTHORITY_ORDER or actor_tier not in AUTHORITY_ORDER:
        return False, f"Invalid authority tier: actor={actor_tier}, required={required_tier}"
    actor_idx = AUTHORITY_ORDER.index(actor_tier)
    required_idx = AUTHORITY_ORDER.index(required_tier)
    if actor_idx >= required_idx:
        return True, f"actor tier '{actor_tier}' >= required '{required_tier}'"
    return False, f"actor tier '{actor_tier}' < required '{required_tier}'"


# ═══════════════════════════════════════════════════════════════════════
# §ENTROPY WATCHER
# ═══════════════════════════════════════════════════════════════════════


class EntropyWatcher:
    """Monitors system entropy and signals overload (legacy 6-check order)."""

    THRESHOLD_HEALTHY = 0.65
    THRESHOLD_OVERLOAD = 0.85

    def __init__(self, warm_threshold: float = 0.65, overload_threshold: float = 0.85):
        self.warm_threshold = warm_threshold
        self.overload_threshold = overload_threshold
        self._last_snapshot: EntropySnapshot | None = None

    def snapshot(self) -> EntropySnapshot:
        try:
            with open("/proc/loadavg") as f:
                parts = f.read().split()
            load_1m = float(parts[0])
            if load_1m <= 4.0:
                omega = 0.0
            else:
                omega = min(1.0, (load_1m - 4.0) / 12.0)
            psi = max(0.0, 1.0 - omega)
            source = "simulated"
        except Exception:
            omega, psi = 0.0, 1.0
            source = "fallback"
        snap = EntropySnapshot(omega=omega, psi_vitality=psi, timestamp=time.time(), source=source)
        self._last_snapshot = snap
        return snap

    def should_pause(self) -> bool:
        if self._last_snapshot is None:
            self.snapshot()
        return self._last_snapshot is not None and self._last_snapshot.is_overload


# ═══════════════════════════════════════════════════════════════════════
# §REVERSIBILITY (4-tier classifier)
# ═══════════════════════════════════════════════════════════════════════


DEFAULT_BY_ACTION_CLASS: dict[str, ReversibilityTier] = {
    "OBSERVE": ReversibilityTier.REVERSIBLE,
    "ANALYZE": ReversibilityTier.REVERSIBLE,
    "DRAFT": ReversibilityTier.REVERSIBLE,
    "MUTATE": ReversibilityTier.COMPENSABLE,
    "EXECUTE": ReversibilityTier.IRREVERSIBLE,
    "EXTERNAL_SIDE_EFFECT": ReversibilityTier.IRREVERSIBLE,
    "IRREVERSIBLE": ReversibilityTier.VOID,
}


def classify_reversibility(
    *,
    action_class: str,
    tool_name: str,
    params: dict[str, Any] | None = None,
    declared_reversible: bool | None = None,
    blast_radius: str = "low",
) -> ReversibilityAssessment:
    """Classify a tool call's reversibility tier (4-tier)."""
    params = params or {}
    base_tier = DEFAULT_BY_ACTION_CLASS.get(action_class.upper(), ReversibilityTier.COMPENSABLE)
    if declared_reversible is True and base_tier in (
        ReversibilityTier.IRREVERSIBLE,
        ReversibilityTier.VOID,
    ):
        base_tier = ReversibilityTier.COMPENSABLE
    elif declared_reversible is False and base_tier == ReversibilityTier.REVERSIBLE:
        base_tier = ReversibilityTier.COMPENSABLE
    if blast_radius == "high" and base_tier == ReversibilityTier.COMPENSABLE:
        base_tier = ReversibilityTier.IRREVERSIBLE
    elif blast_radius == "high" and base_tier == ReversibilityTier.REVERSIBLE:
        base_tier = ReversibilityTier.COMPENSABLE
    if action_class.upper() == "VOID":
        base_tier = ReversibilityTier.VOID
    if base_tier == ReversibilityTier.REVERSIBLE:
        can_rollback, undo_steps, rationale = (
            True,
            1,
            f"{action_class} is reversible; one-step undo",
        )
    elif base_tier == ReversibilityTier.COMPENSABLE:
        can_rollback, undo_steps, rationale = (
            True,
            2,
            f"{action_class} is compensable; refund/rollback path",
        )
    elif base_tier == ReversibilityTier.IRREVERSIBLE:
        can_rollback, undo_steps, rationale = (
            False,
            -1,
            f"{action_class} is irreversible; 888_HOLD required",
        )
    else:
        can_rollback, undo_steps, rationale = False, -1, f"{action_class} is void; no recovery"
    return ReversibilityAssessment(
        tier=base_tier,
        rationale=rationale,
        can_rollback=can_rollback,
        blast_radius=blast_radius,
        estimated_undo_steps=undo_steps,
    )


# ═══════════════════════════════════════════════════════════════════════
# §THE 6-CHECK ORDER (legacy compat)
# ═══════════════════════════════════════════════════════════════════════


def guarded_tool_call(
    *,
    intent: str,
    tool_name: str,
    params: dict[str, Any] | None = None,
    actor_id: str,
    action_class: str = "MUTATE",
    declared_reversible: bool | None = None,
    blast_radius: str = "low",
    ack_irreversible: bool = False,
    drift_count: int = 0,
    failure_rate: float = 0.0,
    entropy_watcher: EntropyWatcher | None = None,
    use_art_v2: bool = True,
) -> GatewayDecision:
    """The legacy 6-check order gateway (compat-only, not for production use)."""
    params = params or {}
    watcher = entropy_watcher or EntropyWatcher()
    entropy_snap = watcher.snapshot()
    reversibility = classify_reversibility(
        action_class=action_class,
        tool_name=tool_name,
        params=params,
        declared_reversible=declared_reversible,
        blast_radius=blast_radius,
    )

    # 1. Entropy
    if entropy_snap.is_overload:
        return GatewayDecision(
            verdict=GatewayVerdict.HOLD,
            decision_class=_classify_decision(action_class),
            reversibility=reversibility,
            entropy=entropy_snap,
            actor_id=actor_id,
            tool_name=tool_name,
            rationale=f"AGENT_PAUSE: entropy Ω={entropy_snap.omega:.2f} >= 0.85",
            next_action="halt",
        )

    # 2. Authority
    authorized, auth_rationale = _check_authority(actor_id, tool_name)
    if not authorized:
        return GatewayDecision(
            verdict=GatewayVerdict.BLOCK,
            decision_class=_classify_decision(action_class),
            reversibility=reversibility,
            entropy=entropy_snap,
            actor_id=actor_id,
            tool_name=tool_name,
            rationale=f"AUTHORITY: {auth_rationale}",
            next_action="halt",
        )

    # 3+4. Reversibility / Irreversibility
    if reversibility.tier == ReversibilityTier.VOID:
        return GatewayDecision(
            verdict=GatewayVerdict.BLOCK,
            decision_class=DecisionClass.C5,
            reversibility=reversibility,
            entropy=entropy_snap,
            actor_id=actor_id,
            tool_name=tool_name,
            rationale=f"VOID: action is irrecoverable: {reversibility.rationale}",
            next_action="halt",
        )
    if reversibility.tier == ReversibilityTier.IRREVERSIBLE and not ack_irreversible:
        return GatewayDecision(
            verdict=GatewayVerdict.HOLD,
            decision_class=DecisionClass.C4,
            reversibility=reversibility,
            entropy=entropy_snap,
            actor_id=actor_id,
            tool_name=tool_name,
            rationale=f"888_HOLD: irreversible without ack: {reversibility.rationale}",
            next_action="escalate",
        )

    # 5. Drift / failure
    if drift_count >= 3 or failure_rate > 0.3:
        return GatewayDecision(
            verdict=GatewayVerdict.SABAR,
            decision_class=_classify_decision(action_class),
            reversibility=reversibility,
            entropy=entropy_snap,
            actor_id=actor_id,
            tool_name=tool_name,
            rationale=f"DEGRADED_TOOL: drift={drift_count}, failure_rate={failure_rate:.2f} — FALLBACK",
            next_action="downgrade",
        )

    # 6. All passed
    return GatewayDecision(
        verdict=GatewayVerdict.PROCEED,
        decision_class=_classify_decision(action_class),
        reversibility=reversibility,
        entropy=entropy_snap,
        actor_id=actor_id,
        tool_name=tool_name,
        rationale=f"All 6 checks passed. Reversibility={reversibility.tier.value}, entropy={entropy_snap.omega:.2f}, authority=OK.",
        next_action="execute",
    )


__all__ = [
    "DecisionClass",
    "GatewayVerdict",
    "ReversibilityTier",
    "EntropySnapshot",
    "ReversibilityAssessment",
    "GatewayDecision",
    "AUTHORITY_ORDER",
    "DEFAULT_AUTHORITY",
    "DEFAULT_TOOL_AUTHORITY",
    "EntropyWatcher",
    "classify_reversibility",
    "guarded_tool_call",
]
