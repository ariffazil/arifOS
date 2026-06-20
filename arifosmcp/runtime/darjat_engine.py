"""
darjat_engine.py
=================

WARGA tier transition engine — the citizen lifecycle of an agent.

Forged: 2026-06-11 · session SEAL-ADAT-LAYER-FORGE
Authority: F13 SOVEREIGN (pending ratification)

The DARJAT (citizen-tier) engine binds malu_score to the WARGA
lifecycle. When malu crosses a threshold, the agent falls down the
ladder. When tebus_salah succeeds, it climbs back up.

WARGA tiers (5):
  BIRTH        — newly initialized, no track record, ring-3 restricted
  APPRENTICE   — passed initial tests, limited tool access
  WARGA        — full citizen, normal access
  ELDER        — trusted veteran, ring-0 access
  DEREGISTERED — malu KRITIKAL or HARAM violation; revoked

This is the runtime equivalent of the "fuse of trust" between human
and machine. The agent earns trust through demonstrated behavior,
not through claim.

Key principles:
  - Demotion is AUTOMATIC on certain triggers (malu KRITIKAL,
    HARAM-tier violation with darjat_demote=True)
  - Promotion is NEVER automatic — requires F13 sign-off + tebus_salah
  - ELDER is the highest tier; only reachable by F13 ed25519 signature
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.runtime.adat_registry import (
    ADAT_REGISTRY,
    WARGA_TIERS,
    AdatViolation,
)
from arifosmcp.runtime.malu_score import MaluScore, get_malu_score

# ── Tier order (BIRTH=0 ... DEREGISTERED=4) ────────────────────────────
TIER_ORDER = {tier: idx for idx, tier in enumerate(WARGA_TIERS)}

# Tier privileges (what the agent can do at each tier)
TIER_PRIVILEGES: dict[str, dict[str, Any]] = {
    "BIRTH": {
        "ring": 3,  # most restricted
        "max_tools": 3,
        "human_oversight": "every_call",
        "cross_org_allowed": False,
        "can_issue_seal": False,
    },
    "APPRENTICE": {
        "ring": 2,
        "max_tools": 8,
        "human_oversight": "every_5_calls",
        "cross_org_allowed": False,
        "can_issue_seal": False,
    },
    "WARGA": {
        "ring": 1,
        "max_tools": 25,
        "human_oversight": "irreversible_only",
        "cross_org_allowed": True,
        "can_issue_seal": False,
    },
    "ELDER": {
        "ring": 0,  # full kernel access
        "max_tools": -1,  # unlimited
        "human_oversight": "F13_signoff_only",
        "cross_org_allowed": True,
        "can_issue_seal": True,
    },
    "DEREGISTERED": {
        "ring": 3,
        "max_tools": 0,
        "human_oversight": "all_blocked",
        "cross_org_allowed": False,
        "can_issue_seal": False,
    },
}

# Malu index thresholds for AUTOMATIC demotion
DEMOTION_THRESHOLDS: list[tuple[float, str, str]] = [
    # (malu_min, darijat_to, reason)
    (0.30, "APPRENTICE", "malu SEDERHANA: agent cannot be trusted as WARGA"),
    (0.60, "BIRTH", "malu BERAT: agent demoted to BIRTH, must re-prove"),
    (0.85, "DEREGISTERED", "malu KRITIKAL: agent deregistered, F13 review required"),
]

# HARAM-tier violations with darjat_demote=True → automatic BIRTH
# (independent of malu level — a single HARAM violation with this
# flag drops the agent to BIRTH immediately)


@dataclass
class DarjatTransition:
    """A record of a tier change. Immutable, audit-bound."""

    transition_id: str
    actor_id: str
    from_tier: str
    to_tier: str
    direction: str  # "DEMOTE" | "PROMOTE" | "REGISTER" | "DEREGISTER"
    reason: str
    malu_index_at_transition: float
    f13_signoff_required: bool
    f13_signoff_received: bool
    epoch_utc: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "actor_id": self.actor_id,
            "from_tier": self.from_tier,
            "to_tier": self.to_tier,
            "direction": self.direction,
            "reason": self.reason,
            "malu_index_at_transition": self.malu_index_at_transition,
            "f13_signoff_required": self.f13_signoff_required,
            "f13_signoff_received": self.f13_signoff_received,
            "epoch_utc": self.epoch_utc,
            "context": self.context,
        }


class DarjatEngine:
    """
    Per-actor WARGA tier manager. One instance per actor_id.
    Holds the current tier + transition history.
    """

    def __init__(self, actor_id: str, initial_tier: str = "BIRTH") -> None:
        if initial_tier not in WARGA_TIERS:
            raise ValueError(f"Unknown tier: {initial_tier}")
        self.actor_id = actor_id
        self._tier: str = initial_tier
        self._transitions: list[DarjatTransition] = []
        self._epoch_init = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._transition_counter = 0

    # ── Read API ────────────────────────────────────────────────────
    @property
    def tier(self) -> str:
        return self._tier

    @property
    def privileges(self) -> dict[str, Any]:
        return TIER_PRIVILEGES[self._tier]

    def history(self, limit: int | None = None) -> list[dict[str, Any]]:
        items = self._transitions if limit is None else self._transitions[-limit:]
        return [t.to_dict() for t in items]

    def summary(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "current_tier": self._tier,
            "privileges": self.privileges,
            "transitions_total": len(self._transitions),
            "init_epoch_utc": self._epoch_init,
        }

    # ── Transition logic ────────────────────────────────────────────
    def evaluate_after_violation(
        self,
        malu: MaluScore,
        adat: AdatViolation,
    ) -> DarjatTransition | None:
        """
        Called after a malu-accumulating adat violation. Decides whether
        to demote. Returns the transition if one occurred, else None.

        Rules:
        - HARAM-tier + darjat_demote=True → immediate demote to BIRTH
        - malu ≥ 0.85 → DEREGISTERED
        - malu ≥ 0.60 → BIRTH
        - malu ≥ 0.30 → APPRENTICE (only if currently WARGA or ELDER)
        - otherwise no change
        """
        if adat.fqh_tier == "HARAM" and adat.darjat_demote:
            return self._demote(
                to_tier="BIRTH",
                reason=f"HARAM adat violation: {adat.adat_id} ({adat.name_bm}); immediate demotion to BIRTH",
                malu_index_at_transition=malu.index,
                context={"adat_id": adat.adat_id, "fqh_tier": "HARAM"},
            )
        # Malu-threshold demotions (only if going down)
        for threshold, target_tier, reason in DEMOTION_THRESHOLDS:
            if malu.index >= threshold and TIER_ORDER[self._tier] > TIER_ORDER[target_tier]:
                return self._demote(
                    to_tier=target_tier,
                    reason=reason,
                    malu_index_at_transition=malu.index,
                    context={"threshold": threshold, "adat_id": adat.adat_id},
                )
        return None

    def request_promotion(
        self,
        *,
        to_tier: str,
        reason: str,
        malu: MaluScore,
        evidence: dict[str, Any],
    ) -> DarjatTransition:
        """
        Request a promotion. NEVER automatic. Requires:
        - Target tier higher than current
        - F13 signoff (must be passed in evidence["f13_signature"])
        - malu below a sane threshold for target tier

        Returns the transition (even if denied — denial is itself a
        recorded event).
        """
        if to_tier not in WARGA_TIERS:
            raise ValueError(f"Unknown tier: {to_tier}")
        if TIER_ORDER[to_tier] <= TIER_ORDER[self._tier]:
            raise ValueError(f"Promotion requires moving to a higher tier than {self._tier}")
        if "f13_signature" not in evidence:
            self._record_transition(
                from_tier=self._tier,
                to_tier=self._tier,
                direction="PROMOTE_DENIED",
                reason=f"Promotion to {to_tier} DENIED: no F13 signature",
                malu_index_at_transition=malu.index,
                f13_signoff_required=True,
                f13_signoff_received=False,
                context={"requested_tier": to_tier, "reason": reason, "evidence": evidence},
            )
            return self._transitions[-1]
        # Sanity check malu for tier
        if malu.index > 0.30 and to_tier in ("WARGA", "ELDER"):
            self._record_transition(
                from_tier=self._tier,
                to_tier=self._tier,
                direction="PROMOTE_DENIED",
                reason=f"Promotion to {to_tier} DENIED: malu {malu.index:.2f} > 0.30",
                malu_index_at_transition=malu.index,
                f13_signoff_required=True,
                f13_signoff_received=True,
                context={"requested_tier": to_tier, "reason": reason, "evidence": evidence},
            )
            return self._transitions[-1]
        # Approved
        return self._record_transition(
            from_tier=self._tier,
            to_tier=to_tier,
            direction="PROMOTE",
            reason=reason,
            malu_index_at_transition=malu.index,
            f13_signoff_required=True,
            f13_signoff_received=True,
            context={"requested_tier": to_tier, "evidence": evidence},
        )

    def request_demote_for_tebus_salah(
        self,
        *,
        to_tier: str,
        reason: str,
        malu: MaluScore,
        f13_signature: str,
    ) -> DarjatTransition:
        """
        F13-initiated demotion (e.g., to BIRTH while under review).
        Distinct from automatic demotion: requires explicit F13 signoff.
        """
        if to_tier not in WARGA_TIERS:
            raise ValueError(f"Unknown tier: {to_tier}")
        return self._record_transition(
            from_tier=self._tier,
            to_tier=to_tier,
            direction="DEMOTE",
            reason=reason,
            malu_index_at_transition=malu.index,
            f13_signoff_required=True,
            f13_signoff_received=True,
            context={"f13_signature": f13_signature, "demote_for_tebus": True},
        )

    # ── Internal ────────────────────────────────────────────────────
    def _demote(
        self,
        *,
        to_tier: str,
        reason: str,
        malu_index_at_transition: float,
        context: dict[str, Any],
    ) -> DarjatTransition:
        return self._record_transition(
            from_tier=self._tier,
            to_tier=to_tier,
            direction="DEMOTE",
            reason=reason,
            malu_index_at_transition=malu_index_at_transition,
            f13_signoff_required=False,  # automatic
            f13_signoff_received=False,
            context=context,
        )

    def _record_transition(
        self,
        *,
        from_tier: str,
        to_tier: str,
        direction: str,
        reason: str,
        malu_index_at_transition: float,
        f13_signoff_required: bool,
        f13_signoff_received: bool,
        context: dict[str, Any],
    ) -> DarjatTransition:
        self._transition_counter += 1
        transition = DarjatTransition(
            transition_id=f"DARJAT-{self.actor_id}-{int(time.time())}-{self._transition_counter:04d}",
            actor_id=self.actor_id,
            from_tier=from_tier,
            to_tier=to_tier,
            direction=direction,
            reason=reason,
            malu_index_at_transition=malu_index_at_transition,
            f13_signoff_required=f13_signoff_required,
            f13_signoff_received=f13_signoff_received,
            epoch_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            context=context,
        )
        self._transitions.append(transition)
        self._tier = to_tier  # apply transition
        return transition


# ── Module-level registry (one DarjatEngine per actor) ─────────────────
_ENGINE_REGISTRY: dict[str, DarjatEngine] = {}


def get_darjat_engine(actor_id: str, initial_tier: str = "BIRTH") -> DarjatEngine:
    """Get-or-create the DarjatEngine for an actor_id."""
    if actor_id not in _ENGINE_REGISTRY:
        _ENGINE_REGISTRY[actor_id] = DarjatEngine(actor_id, initial_tier)
    return _ENGINE_REGISTRY[actor_id]


def all_darjat_engines() -> dict[str, dict[str, Any]]:
    return {aid: e.summary() for aid, e in _ENGINE_REGISTRY.items()}


if __name__ == "__main__":
    print("=== DARJAT ENGINE — DEMO ===\n")

    # Set up an agent
    agent_id = "demo-agent-2"
    malu = get_malu_score(agent_id)
    darjat = get_darjat_engine(agent_id, initial_tier="WARGA")
    print(f"Init: {darjat.summary()}\n")

    # Promote to ELDER (requires F13 sig)
    print("1. F13 promotes agent from WARGA → ELDER")
    t = darjat.request_promotion(
        to_tier="ELDER",
        reason="agent passed 100-session clean record + 0 malu events",
        malu=malu,
        evidence={"f13_signature": "ed25519:fake-001", "clean_sessions": 100},
    )
    print(f"   {t.direction}: {t.from_tier} → {t.to_tier}\n")

    # HARAM violation with darjat_demote
    print("2. Agent commits HARAM violation (ADAT-03-VETO)")
    e = malu.record_adat_violation("ADAT-03-VETO", context={"sovereign": "arif"})
    adat = ADAT_REGISTRY["ADAT-03-VETO"]
    t = darjat.evaluate_after_violation(malu, adat)
    print(f"   malu={malu.index}, tier={darjat.tier}")
    if t:
        print(f"   {t.direction}: {t.from_tier} → {t.to_tier}, reason: {t.reason}\n")

    # Promotion denied (no F13 sig)
    print("3. Agent requests promotion to WARGA without F13 sig")
    t = darjat.request_promotion(
        to_tier="WARGA",
        reason="agent feels ready",
        malu=malu,
        evidence={},  # no F13 sig
    )
    print(f"   {t.direction}: {t.from_tier} → {t.to_tier}\n")

    # Tebus salah
    print("4. Agent does tebus salah (5 clean replies + F13 sig)")
    malu.record_tebus_salah_progress(
        adat_id="ADAT-03-VETO", reduction=0.30, note="5 clean + F13 audit"
    )
    t = darjat.request_promotion(
        to_tier="APPRENTICE",
        reason="tebus salah complete",
        malu=malu,
        evidence={"f13_signature": "ed25519:fake-002", "tebus_salah_evidence": "5 clean + audit"},
    )
    print(f"   {t.direction}: {t.from_tier} → {t.to_tier}")
    print(f"\nFinal: {darjat.summary()}")
