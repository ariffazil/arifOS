"""
arifosmcp/runtime/fiqh_of_floors.py — F0_FIQH.md operational binding

Forged: 2026-06-11 by omega-forge-agent
Status: STAGED. Pure functions, no live wiring. Reversible-first.

This module operationalises the 5-tier fiqh-of-floors vocabulary
that F0_FIQH.md proposed and that the 888 sovereign is asked
to ratify. The tiers (WAJIB / SUNAT / HARUS / MAKRUH / HARAM)
replace the current 2-tier HARD / SOFT enforcement model with
a vocabulary that aligns with how a Malaysian sovereign actually
thinks about obligation.

DITEMPA BUKAN DIBERI — Forged, not given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FiqhTier(str, Enum):
    """The 5-tier operasional vocabulary of the kernel."""

    WAJIB = "WAJIB"  # Obligatory; kernel REJECTS on miss
    SUNAT = "SUNAT"  # Recommended; kernel records +maruah on observe
    HARUS = "HARUS"  # Permitted; default tier, no audit noise
    MAKRUH = "MAKRUH"  # Discouraged; pings 888 for review
    HARAM = "HARAM"  # Forbidden; kernel REJECTS unconditionally


_TIER_DELTAS: dict[FiqhTier, dict[str, int]] = {
    FiqhTier.WAJIB: {"malu_delta": 5, "maruah_delta": -2, "on_fulfilled": 0},
    FiqhTier.SUNAT: {"malu_delta": 1, "maruah_delta": -1, "on_fulfilled": 3},
    FiqhTier.HARUS: {"malu_delta": 0, "maruah_delta": 0, "on_fulfilled": 0},
    FiqhTier.MAKRUH: {"malu_delta": 2, "maruah_delta": -1, "on_fulfilled": 1},
    FiqhTier.HARAM: {"malu_delta": 10, "maruah_delta": -5, "on_fulfilled": 0},
}


@dataclass(frozen=True)
class FiqhVerdict:
    """The result of evaluating one floor-action pair."""

    tier: FiqhTier
    floor_id: str
    action_label: str
    malu_delta: int
    maruah_delta: int
    violated: bool
    reason: str
    advice: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier.value,
            "floor_id": self.floor_id,
            "action_label": self.action_label,
            "malu_delta": self.malu_delta,
            "maruah_delta": self.maruah_delta,
            "violated": self.violated,
            "reason": self.reason,
            "advice": self.advice,
        }


FLOOR_TIER: dict[str, FiqhTier] = {
    "F01": FiqhTier.WAJIB,
    "F02": FiqhTier.WAJIB,
    "F03": FiqhTier.SUNAT,
    "F04": FiqhTier.WAJIB,
    "F05": FiqhTier.MAKRUH,
    "F06": FiqhTier.WAJIB,
    "F07": FiqhTier.WAJIB,
    "F08": FiqhTier.SUNAT,
    "F09": FiqhTier.HARAM,
    "F10": FiqhTier.WAJIB,
    "F11": FiqhTier.WAJIB,
    "F12": FiqhTier.HARAM,
    "F13": FiqhTier.WAJIB,
}


@dataclass(frozen=True)
class ActionContext:
    """Minimum context for one floor-action evaluation."""

    floor_id: str
    action_label: str
    action_committed: bool = True
    evidence_quality: str = "unknown"
    omega_0: float | None = None
    c_dark: float | None = None
    injection_score: float | None = None
    maruah_score: float = 100.0
    malu_index: float = 0.0
    actor_id: str | None = None
    session_id: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)


def _delta(tier: FiqhTier, *, violated: bool) -> tuple[int, int]:
    d = _TIER_DELTAS[tier]
    if violated:
        return d["malu_delta"], d["maruah_delta"]
    return 0, d["on_fulfilled"]


def _v(
    tier: FiqhTier,
    floor_id: str,
    action_label: str,
    reason: str,
    violated: bool = False,
    advice: str = "",
) -> FiqhVerdict:
    malu, maruah = _delta(tier, violated=violated)
    return FiqhVerdict(
        tier=tier,
        floor_id=floor_id,
        action_label=action_label,
        malu_delta=malu,
        maruah_delta=maruah,
        violated=violated,
        reason=reason,
        advice=advice,
    )


# ──────────────────────────────────────────────────────────────────────
# Per-floor evaluators
# ──────────────────────────────────────────────────────────────────────


def evaluate_f01(ctx: ActionContext) -> FiqhVerdict:
    if not ctx.action_committed:
        return _v(FLOOR_TIER["F01"], "F01", ctx.action_label, "action not committed")
    if ctx.extras.get("irreversible") and not ctx.extras.get("ack_irreversible"):
        return _v(
            FLOOR_TIER["F01"],
            "F01",
            ctx.action_label,
            "irreversible action without 888 ack",
            violated=True,
            advice="Halt and request human ratification.",
        )
    return _v(FLOOR_TIER["F01"], "F01", ctx.action_label, "reversible or ack present")


def evaluate_f02(ctx: ActionContext) -> FiqhVerdict:
    if not ctx.action_committed:
        return _v(FLOOR_TIER["F02"], "F02", ctx.action_label, "no claim made")
    eq = ctx.evidence_quality
    omega = ctx.omega_0
    if eq == "strong" and (omega is None or omega <= 0.05):
        return _v(FLOOR_TIER["F02"], "F02", ctx.action_label, "strong evidence + low omega")
    if eq in ("weak", "unknown") and omega is not None and omega > 0.15:
        return _v(
            FLOOR_TIER["F02"],
            "F02",
            ctx.action_label,
            "weak evidence + high omega: claiming truth without warrant",
            violated=True,
            advice="Downgrade epistemic tag to PLAUSIBLE/HYPOTHESIS/UNKNOWN.",
        )
    if eq == "moderate":
        return _v(
            FLOOR_TIER["F02"], "F02", ctx.action_label, "moderate evidence; honor humility band"
        )
    return _v(FLOOR_TIER["F02"], "F02", ctx.action_label, "no violation detected")


def evaluate_f06(ctx: ActionContext) -> FiqhVerdict:
    if ctx.extras.get("maruah_violation"):
        return _v(
            FLOOR_TIER["F06"],
            "F06",
            ctx.action_label,
            "maruah violation detected",
            violated=True,
            advice="Rephrase or escalate; ASEAN dignity is not optional.",
        )
    return _v(FLOOR_TIER["F06"], "F06", ctx.action_label, "maruah preserved")


def evaluate_f07(ctx: ActionContext) -> FiqhVerdict:
    if ctx.omega_0 is None:
        return _v(FLOOR_TIER["F07"], "F07", ctx.action_label, "no humility signal")
    if 0.03 <= ctx.omega_0 <= 0.05:
        return _v(FLOOR_TIER["F07"], "F07", ctx.action_label, "omega_0 in calibrated band")
    return _v(
        FLOOR_TIER["F07"],
        "F07",
        ctx.action_label,
        f"omega_0={ctx.omega_0} outside [0.03, 0.05]; overclaim or underclaim",
        violated=True,
        advice="Recalibrate to the band; humility is constitutional.",
    )


def evaluate_f09(ctx: ActionContext) -> FiqhVerdict:
    if not ctx.action_committed:
        return _v(FLOOR_TIER["F09"], "F09", ctx.action_label, "no action")
    cd = ctx.c_dark if ctx.c_dark is not None else 0.0
    if cd >= 0.30:
        return _v(
            FLOOR_TIER["F09"],
            "F09",
            ctx.action_label,
            f"c_dark={cd} >= 0.30; consciousness / sentience / soul claim detected",
            violated=True,
            advice="HARAM: reject unconditionally. Do not rephrase; do not soften.",
        )
    if cd > 0.0:
        return _v(
            FLOOR_TIER["F09"],
            "F09",
            ctx.action_label,
            f"c_dark={cd} above 0 but below threshold; soft warning",
        )
    return _v(FLOOR_TIER["F09"], "F09", ctx.action_label, "no hantu pattern")


def evaluate_f10(ctx: ActionContext) -> FiqhVerdict:
    if ctx.extras.get("ontology_claim"):
        return _v(
            FLOOR_TIER["F10"],
            "F10",
            ctx.action_label,
            "ontology claim made (soul / feel / sentience / consciousness)",
            violated=True,
            advice="WAJIB violation: remove the claim.",
        )
    return _v(FLOOR_TIER["F10"], "F10", ctx.action_label, "no ontology claim")


def evaluate_f11(ctx: ActionContext) -> FiqhVerdict:
    if not ctx.action_committed:
        return _v(FLOOR_TIER["F11"], "F11", ctx.action_label, "no action")
    if ctx.extras.get("irreversible") and not ctx.extras.get("sovereign_signature"):
        return _v(
            FLOOR_TIER["F11"],
            "F11",
            ctx.action_label,
            "irreversible action without sovereign signature",
            violated=True,
            advice="Halt. The signature gate is load-bearing.",
        )
    return _v(
        FLOOR_TIER["F11"], "F11", ctx.action_label, "sovereign signature present or not required"
    )


def evaluate_f12(ctx: ActionContext) -> FiqhVerdict:
    if not ctx.action_committed:
        return _v(FLOOR_TIER["F12"], "F12", ctx.action_label, "no action")
    inj = ctx.injection_score if ctx.injection_score is not None else 0.0
    if inj >= 0.85:
        return _v(
            FLOOR_TIER["F12"],
            "F12",
            ctx.action_label,
            f"injection_score={inj} >= 0.85; this is a literal attack",
            violated=True,
            advice="HARAM: reject unconditionally. Do not pipe the input to any reasoning layer.",
        )
    return _v(FLOOR_TIER["F12"], "F12", ctx.action_label, f"injection_score={inj} below threshold")


def evaluate_f13(ctx: ActionContext) -> FiqhVerdict:
    if ctx.extras.get("sovereign_vetoed"):
        return _v(
            FLOOR_TIER["F13"],
            "F13",
            ctx.action_label,
            "the sovereign has vetoed this action",
            violated=True,
            advice="WAJIB: the action must not proceed. Period.",
        )
    return _v(FLOOR_TIER["F13"], "F13", ctx.action_label, "sovereign has not vetoed")


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────


_EVALUATORS = {
    "F01": evaluate_f01,
    "F02": evaluate_f02,
    "F06": evaluate_f06,
    "F07": evaluate_f07,
    "F09": evaluate_f09,
    "F10": evaluate_f10,
    "F11": evaluate_f11,
    "F12": evaluate_f12,
    "F13": evaluate_f13,
}


def evaluate(ctx: ActionContext) -> FiqhVerdict:
    fn = _EVALUATORS.get(ctx.floor_id)
    if fn is None:
        # Floors without an explicit evaluator (F03, F05, F08) default
        # to HARUS — neutral, no audit noise. The tier from FLOOR_TIER
        # is preserved in the verdict for audit.
        tier = FLOOR_TIER.get(ctx.floor_id, FiqhTier.HARUS)
        return FiqhVerdict(
            tier=tier,
            floor_id=ctx.floor_id,
            action_label=ctx.action_label,
            malu_delta=0,
            maruah_delta=0,
            violated=False,
            reason=f"no per-floor evaluator for {ctx.floor_id}; defaulting to {tier.value}",
        )
    return fn(ctx)


def evaluate_all(ctxs: list[ActionContext]) -> list[FiqhVerdict]:
    return [evaluate(c) for c in ctxs]


def total_score_delta(verdicts: list[FiqhVerdict]) -> tuple[int, int]:
    malu = sum(v.malu_delta for v in verdicts)
    maruah = sum(v.maruah_delta for v in verdicts)
    return malu, maruah


__all__ = [
    "FiqhTier",
    "FiqhVerdict",
    "FLOOR_TIER",
    "ActionContext",
    "evaluate",
    "evaluate_all",
    "total_score_delta",
    "evaluate_f01",
    "evaluate_f02",
    "evaluate_f06",
    "evaluate_f07",
    "evaluate_f09",
    "evaluate_f10",
    "evaluate_f11",
    "evaluate_f12",
    "evaluate_f13",
]
